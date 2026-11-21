"""
ATTACHORA Email Reader Pipeline
Coordinates email retrieval from IMAP accounts and .eml file imports,
executing the full extraction, validation, classification, and staging workflow.
"""

from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional
from src.classifier.engine import CLASSIFIER
from src.config import CONFIG
from src.database.db_manager import DatabaseManager
from src.email_engine.eml_parser import parse_eml_bytes, parse_eml_file
from src.email_engine.imap_client import IMAPClient, IMAPConnectionError
from src.rules_engine.rule_evaluator import match_filing_rules
from src.security.credential_vault import VAULT
from src.security.sanitizer import sanitize_filename
from src.security.validator import validate_file_size
from src.storage_manager.duplicate_detector import DuplicateDetector


class EmailReaderPipeline:
    def __init__(self, db: DatabaseManager):
        self.db = db
        self.duplicate_detector = DuplicateDetector(db)
        self.staging_dir = CONFIG.STAGING_DIR
        self.staging_dir.mkdir(parents=True, exist_ok=True)

    def process_email_data(
        self,
        email_data: Dict[str, Any],
        account_id: Optional[int] = None,
        message_uid: Optional[str] = None,
        mailbox_name: str = "INBOX",
    ) -> List[Dict[str, Any]]:
        """Processes an extracted email dictionary and stages any attachments."""
        processed_attachments: List[Dict[str, Any]] = []

        # 1. Insert or get Email record
        email_id = self.db.insert_email(
            account_id=account_id,
            message_uid=message_uid or email_data.get("message_id"),
            message_id=email_data.get("message_id"),
            sender=email_data.get("sender", "Unknown"),
            sender_email=email_data.get("sender_email", ""),
            subject=email_data.get("subject", "(No Subject)"),
            received_at=email_data.get("received_at"),
            mailbox_name=mailbox_name,
        )

        email_row = self.db.get_email_by_id(email_id) or email_data

        # Load active filing rules for evaluation
        rules = self.db.get_rules(enabled_only=True)

        # 2. Process each attachment
        for att in email_data.get("attachments", []):
            orig_fn = sanitize_filename(att.get("original_filename", "attachment.dat"))
            file_bytes = att.get("content_bytes", b"")
            sha256 = att.get("sha256")
            file_size = att.get("file_size", len(file_bytes))
            initial_mime = att.get("mime_type")

            # Validate file size
            is_valid_size, size_err = validate_file_size(file_size)
            if not is_valid_size:
                # Log failed extraction
                continue

            # Stage file to local temporary staging directory
            staging_filename = f"{sha256[:12]}_{orig_fn}"
            staging_path = self.staging_dir / staging_filename
            with open(staging_path, "wb") as f:
                f.write(file_bytes)

            # Classify attachment
            classification = CLASSIFIER.classify_attachment(
                filename=orig_fn,
                mime_type=initial_mime,
                subject=email_data.get("subject"),
                header_bytes=file_bytes[:64],
            )

            # Build temporary attachment object for rule evaluation
            att_temp = {
                "original_filename": orig_fn,
                "mime_type": classification["mime_type"],
                "extension": classification["extension"],
                "file_size": file_size,
                "category": classification["category"],
            }

            # Evaluate filing rules
            rule_match = match_filing_rules(rules, att_temp, email_row)

            # Check duplicate status
            dup_info = self.duplicate_detector.inspect_duplicate(
                sha256=sha256,
                filename=orig_fn,
            )

            # Determine initial status:
            # If auto mode is enabled and confidence meets threshold and not duplicate, mark pending or auto-organize
            initial_status = "Pending Approval"
            if dup_info["status"] == "Exact Duplicate":
                initial_status = "Duplicate"

            # Insert into database
            att_id = self.db.insert_attachment(
                email_id=email_id,
                original_filename=orig_fn,
                stored_filename=rule_match["proposed_filename"],
                mime_type=classification["mime_type"],
                extension=classification["extension"],
                file_size=file_size,
                sha256=sha256,
                category=classification["category"],
                classification_method=classification["classification_method"],
                classification_reason=classification["classification_reason"],
                confidence=classification["confidence"],
                original_path=str(staging_path),
                current_path=str(staging_path),
                status=initial_status,
            )

            # Log operation event
            self.db.log_operation(
                attachment_id=att_id,
                operation_type="Classify",
                source_path=str(staging_path),
                destination_path=rule_match["destination"],
                previous_filename=orig_fn,
                final_filename=rule_match["proposed_filename"],
                status=initial_status,
                error_message=rule_match["reason"],
            )

            processed_attachments.append(
                {
                    "attachment_id": att_id,
                    "filename": orig_fn,
                    "category": classification["category"],
                    "rule": rule_match["rule_name"],
                    "proposed_destination": rule_match["destination"],
                    "proposed_filename": rule_match["proposed_filename"],
                    "duplicate_status": dup_info["status"],
                    "status": initial_status,
                }
            )

        return processed_attachments

    def import_eml_file(self, eml_path: Path) -> List[Dict[str, Any]]:
        """Imports a single .eml file from disk."""
        data = parse_eml_file(eml_path)
        return self.process_email_data(data, account_id=None, mailbox_name="Imported EML")

    def import_eml_bytes(self, raw_bytes: bytes, filename: str) -> List[Dict[str, Any]]:
        """Imports an .eml file from uploaded byte buffer."""
        data = parse_eml_bytes(raw_bytes, source_identifier=filename)
        return self.process_email_data(data, account_id=None, mailbox_name="Uploaded EML")

    def sync_imap_account(
        self,
        account_id: int,
        password_override: Optional[str] = None,
        max_messages: int = 25,
    ) -> Dict[str, Any]:
        """Synchronizes an IMAP mailbox incrementally, extracting unread/unprocessed attachments."""
        account = self.db.get_account_by_id(account_id)
        if not account:
            return {"success": False, "error": f"Account ID {account_id} not found"}

        # Resolve password: from memory vault, override, or decrypted token
        password = password_override or VAULT.get_memory_credential(account["account_email"])
        if not password:
            return {
                "success": False,
                "error": "Password / App Password is required to access mailbox. Please provide credentials in the Connections tab.",
            }

        sync_id = self.db.start_sync(account_id)
        self.db.update_account_status(account_id, "syncing")

        client = IMAPClient(
            host=account["imap_host"],
            port=account.get("imap_port", 993),
            username=account["account_email"],
            password=password,
            use_ssl=True,
        )

        try:
            raw_messages = client.fetch_messages_raw(
                mailbox=account.get("mailbox", "INBOX"),
                max_messages=max_messages,
            )

            total_messages = len(raw_messages)
            detected_attachments = 0

            for uid, msg_bytes in raw_messages:
                email_data = parse_eml_bytes(msg_bytes, source_identifier=f"imap_{uid}")
                if email_data["attachments"]:
                    staged = self.process_email_data(
                        email_data=email_data,
                        account_id=account_id,
                        message_uid=uid,
                        mailbox_name=account.get("mailbox", "INBOX"),
                    )
                    detected_attachments += len(staged)

            now_str = datetime.now().isoformat()
            self.db.update_account_status(account_id, "connected", last_sync=now_str)
            self.db.complete_sync(
                sync_id=sync_id,
                messages_scanned=total_messages,
                attachments_detected=detected_attachments,
                status="Completed",
            )

            return {
                "success": True,
                "messages_scanned": total_messages,
                "attachments_detected": detected_attachments,
            }

        except IMAPConnectionError as ice:
            err = str(ice)
            self.db.update_account_status(account_id, "error")
            self.db.complete_sync(sync_id=sync_id, messages_scanned=0, attachments_detected=0, status="Failed", error_message=err)
            return {"success": False, "error": err}
        except Exception as e:
            err = f"Unexpected sync error: {str(e)}"
            self.db.update_account_status(account_id, "error")
            self.db.complete_sync(sync_id=sync_id, messages_scanned=0, attachments_detected=0, status="Failed", error_message=err)
            return {"success": False, "error": err}


# Singleton reader pipeline
READER = EmailReaderPipeline(db=DatabaseManager())
