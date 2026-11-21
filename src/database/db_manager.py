"""
ATTACHORA Database Manager
Provides thread-safe access, queries, transactions, and seeding for SQLite.
"""

from contextlib import contextmanager
import json
from pathlib import Path
import sqlite3
from typing import Any, Dict, Generator, List, Optional
from src.config import CONFIG
from src.database.schema import CREATE_TABLES_SQL, DEFAULT_RULES, SCHEMA_VERSION


class DatabaseManager:
    def __init__(self, db_path: Optional[Path] = None):
        self.db_path = Path(db_path or CONFIG.DB_PATH)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.init_database()

    @contextmanager
    def get_connection(self) -> Generator[sqlite3.Connection, None, None]:
        """Provides a managed sqlite connection with WAL mode enabled."""
        conn = sqlite3.connect(
            str(self.db_path),
            timeout=30.0,
        )
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON;")
        conn.execute("PRAGMA journal_mode = WAL;")
        try:
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    def init_database(self) -> None:
        """Initializes tables and seeds default filing rules."""
        with self.get_connection() as conn:
            conn.executescript(CREATE_TABLES_SQL)
            cursor = conn.cursor()
            cursor.execute("SELECT value FROM schema_meta WHERE key = 'version'")
            row = cursor.fetchone()
            if not row:
                cursor.execute(
                    "INSERT INTO schema_meta (key, value) VALUES ('version', ?)",
                    (str(SCHEMA_VERSION),),
                )
                # Seed default rules
                for rule in DEFAULT_RULES:
                    cursor.execute(
                        """
                        INSERT INTO filing_rules (rule_name, conditions_json, destination, filename_template, priority, enabled)
                        VALUES (:rule_name, :conditions_json, :destination, :filename_template, :priority, :enabled)
                    """,
                        rule,
                    )

    # ------------------ EMAIL ACCOUNTS ------------------
    def get_accounts(self) -> List[Dict[str, Any]]:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM email_accounts ORDER BY id ASC")
            return [dict(row) for row in cursor.fetchall()]

    def get_account_by_id(self, account_id: int) -> Optional[Dict[str, Any]]:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM email_accounts WHERE id = ?", (account_id,))
            row = cursor.fetchone()
            return dict(row) if row else None

    def add_account(
        self,
        account_email: str,
        imap_host: str,
        imap_port: int = 993,
        mailbox: str = "INBOX",
        auth_type: str = "password",
    ) -> int:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO email_accounts (account_email, imap_host, imap_port, mailbox, authentication_type, connection_status)
                VALUES (?, ?, ?, ?, ?, 'configured')
                ON CONFLICT(account_email) DO UPDATE SET
                    imap_host = excluded.imap_host,
                    imap_port = excluded.imap_port,
                    mailbox = excluded.mailbox,
                    authentication_type = excluded.authentication_type
            """,
                (account_email, imap_host, imap_port, mailbox, auth_type),
            )
            return cursor.lastrowid

    def update_account_status(self, account_id: int, status: str, last_sync: Optional[str] = None) -> None:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            if last_sync:
                cursor.execute(
                    "UPDATE email_accounts SET connection_status = ?, last_sync_at = ? WHERE id = ?",
                    (status, last_sync, account_id),
                )
            else:
                cursor.execute(
                    "UPDATE email_accounts SET connection_status = ? WHERE id = ?",
                    (status, account_id),
                )

    def delete_account(self, account_id: int) -> None:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM email_accounts WHERE id = ?", (account_id,))

    # ------------------ EMAILS ------------------
    def insert_email(
        self,
        account_id: Optional[int],
        message_uid: Optional[str],
        message_id: Optional[str],
        sender: str,
        sender_email: str,
        subject: str,
        received_at: Optional[str],
        mailbox_name: str = "INBOX",
    ) -> int:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO emails (account_id, message_uid, message_id, sender, sender_email, subject, received_at, mailbox_name)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(account_id, message_uid, message_id) DO UPDATE SET
                    sender = excluded.sender,
                    sender_email = excluded.sender_email,
                    subject = excluded.subject,
                    received_at = excluded.received_at
            """,
                (account_id, message_uid, message_id, sender, sender_email, subject, received_at, mailbox_name),
            )
            if cursor.lastrowid and cursor.lastrowid > 0:
                return cursor.lastrowid
            # Retrieve existing row id if conflict updated
            cursor.execute(
                "SELECT id FROM emails WHERE account_id IS ? AND message_uid IS ? AND message_id IS ?",
                (account_id, message_uid, message_id),
            )
            row = cursor.fetchone()
            return row["id"] if row else 1

    def get_email_by_id(self, email_id: int) -> Optional[Dict[str, Any]]:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM emails WHERE id = ?", (email_id,))
            row = cursor.fetchone()
            return dict(row) if row else None

    # ------------------ ATTACHMENTS ------------------
    def insert_attachment(
        self,
        email_id: int,
        original_filename: str,
        stored_filename: Optional[str],
        mime_type: str,
        extension: str,
        file_size: int,
        sha256: str,
        category: str,
        classification_method: str,
        classification_reason: str,
        confidence: float,
        original_path: str,
        current_path: str,
        status: str = "Detected",
    ) -> int:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO attachments (
                    email_id, original_filename, stored_filename, mime_type, extension,
                    file_size, sha256, category, classification_method, classification_reason,
                    confidence, original_path, current_path, status
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    email_id,
                    original_filename,
                    stored_filename,
                    mime_type,
                    extension,
                    file_size,
                    sha256,
                    category,
                    classification_method,
                    classification_reason,
                    confidence,
                    original_path,
                    current_path,
                    status,
                ),
            )
            return cursor.lastrowid

    def get_attachment_by_id(self, attachment_id: int) -> Optional[Dict[str, Any]]:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT a.*, e.sender, e.sender_email, e.subject, e.received_at, e.mailbox_name
                FROM attachments a
                JOIN emails e ON a.email_id = e.id
                WHERE a.id = ?
            """,
                (attachment_id,),
            )
            row = cursor.fetchone()
            return dict(row) if row else None

    def get_attachments_by_hash(self, sha256: str) -> List[Dict[str, Any]]:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT a.*, e.sender, e.sender_email, e.subject, e.received_at
                FROM attachments a
                JOIN emails e ON a.email_id = e.id
                WHERE a.sha256 = ?
            """,
                (sha256,),
            )
            return [dict(row) for row in cursor.fetchall()]

    def get_attachments_workspace(
        self,
        search_query: str = "",
        category: str = "All",
        status: str = "All",
        extension: str = "All",
        sender: str = "All",
    ) -> List[Dict[str, Any]]:
        query = """
            SELECT a.*, e.sender, e.sender_email, e.subject, e.received_at, e.mailbox_name
            FROM attachments a
            JOIN emails e ON a.email_id = e.id
            WHERE 1=1
        """
        params: List[Any] = []

        if category and category != "All":
            query += " AND a.category = ?"
            params.append(category)

        if status and status != "All":
            query += " AND a.status = ?"
            params.append(status)

        if extension and extension != "All":
            query += " AND LOWER(a.extension) = ?"
            params.append(extension.lower().lstrip("."))

        if sender and sender != "All":
            query += " AND (e.sender_email LIKE ? OR e.sender LIKE ?)"
            params.extend([f"%{sender}%", f"%{sender}%"])

        if search_query.strip():
            sq = f"%{search_query.strip()}%"
            query += """ AND (
                a.original_filename LIKE ? OR
                e.sender LIKE ? OR
                e.sender_email LIKE ? OR
                e.subject LIKE ? OR
                a.category LIKE ? OR
                a.sha256 LIKE ? OR
                a.current_path LIKE ?
            )"""
            params.extend([sq, sq, sq, sq, sq, sq, sq])

        query += " ORDER BY a.id DESC"

        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            return [dict(row) for row in cursor.fetchall()]

    def update_attachment_status(
        self,
        attachment_id: int,
        status: str,
        current_path: Optional[str] = None,
        stored_filename: Optional[str] = None,
    ) -> None:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            if current_path and stored_filename:
                cursor.execute(
                    "UPDATE attachments SET status = ?, current_path = ?, stored_filename = ? WHERE id = ?",
                    (status, current_path, stored_filename, attachment_id),
                )
            elif current_path:
                cursor.execute(
                    "UPDATE attachments SET status = ?, current_path = ? WHERE id = ?",
                    (status, current_path, attachment_id),
                )
            else:
                cursor.execute(
                    "UPDATE attachments SET status = ? WHERE id = ?",
                    (status, attachment_id),
                )

    def update_attachment_category(
        self,
        attachment_id: int,
        category: str,
        reason: str = "User manual override",
        confidence: float = 1.0,
    ) -> None:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                UPDATE attachments
                SET category = ?, classification_method = 'manual_correction', classification_reason = ?, confidence = ?
                WHERE id = ?
            """,
                (category, reason, confidence, attachment_id),
            )

    # ------------------ FILING RULES ------------------
    def get_rules(self, enabled_only: bool = False) -> List[Dict[str, Any]]:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            if enabled_only:
                cursor.execute("SELECT * FROM filing_rules WHERE enabled = 1 ORDER BY priority ASC, id ASC")
            else:
                cursor.execute("SELECT * FROM filing_rules ORDER BY priority ASC, id ASC")
            rules = []
            for row in cursor.fetchall():
                r = dict(row)
                if isinstance(r.get("conditions_json"), str):
                    try:
                        r["conditions"] = json.loads(r["conditions_json"])
                    except Exception:
                        r["conditions"] = {}
                rules.append(r)
            return rules

    def add_rule(
        self,
        rule_name: str,
        conditions_json: str,
        destination: str,
        filename_template: str = "{original_filename}",
        priority: int = 10,
        enabled: int = 1,
    ) -> int:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO filing_rules (rule_name, conditions_json, destination, filename_template, priority, enabled)
                VALUES (?, ?, ?, ?, ?, ?)
            """,
                (rule_name, conditions_json, destination, filename_template, priority, enabled),
            )
            return cursor.lastrowid

    def update_rule(
        self,
        rule_id: int,
        rule_name: str,
        conditions_json: str,
        destination: str,
        filename_template: str,
        priority: int,
        enabled: int,
    ) -> None:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                UPDATE filing_rules
                SET rule_name = ?, conditions_json = ?, destination = ?, filename_template = ?, priority = ?, enabled = ?
                WHERE id = ?
            """,
                (rule_name, conditions_json, destination, filename_template, priority, enabled, rule_id),
            )

    def delete_rule(self, rule_id: int) -> None:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM filing_rules WHERE id = ?", (rule_id,))

    def reorder_rules(self, rule_ids_in_order: List[int]) -> None:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            for priority, rule_id in enumerate(rule_ids_in_order, start=1):
                cursor.execute("UPDATE filing_rules SET priority = ? WHERE id = ?", (priority, rule_id))

    # ------------------ OPERATIONS & AUDIT LOG ------------------
    def log_operation(
        self,
        attachment_id: int,
        operation_type: str,
        source_path: Optional[str],
        destination_path: Optional[str],
        previous_filename: Optional[str],
        final_filename: Optional[str],
        status: str,
        error_message: Optional[str] = None,
    ) -> int:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO operations (
                    attachment_id, operation_type, source_path, destination_path,
                    previous_filename, final_filename, status, error_message
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    attachment_id,
                    operation_type,
                    source_path,
                    destination_path,
                    previous_filename,
                    final_filename,
                    status,
                    error_message,
                ),
            )
            return cursor.lastrowid

    def get_operations(
        self,
        status: str = "All",
        operation_type: str = "All",
        search_query: str = "",
        limit: int = 500,
    ) -> List[Dict[str, Any]]:
        query = """
            SELECT o.*, a.original_filename, a.sha256, a.category, a.file_size,
                   e.sender, e.sender_email, e.subject
            FROM operations o
            JOIN attachments a ON o.attachment_id = a.id
            JOIN emails e ON a.email_id = e.id
            WHERE 1=1
        """
        params: List[Any] = []

        if status and status != "All":
            query += " AND o.status = ?"
            params.append(status)

        if operation_type and operation_type != "All":
            query += " AND o.operation_type = ?"
            params.append(operation_type)

        if search_query.strip():
            sq = f"%{search_query.strip()}%"
            query += """ AND (
                a.original_filename LIKE ? OR
                o.final_filename LIKE ? OR
                e.sender LIKE ? OR
                e.sender_email LIKE ? OR
                a.sha256 LIKE ? OR
                o.destination_path LIKE ?
            )"""
            params.extend([sq, sq, sq, sq, sq, sq])

        query += " ORDER BY o.id DESC LIMIT ?"
        params.append(limit)

        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            return [dict(row) for row in cursor.fetchall()]

    def get_last_successful_organize_operation(self, attachment_id: int) -> Optional[Dict[str, Any]]:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT * FROM operations
                WHERE attachment_id = ? AND operation_type = 'Organize' AND status = 'Organized'
                ORDER BY id DESC LIMIT 1
            """,
                (attachment_id,),
            )
            row = cursor.fetchone()
            return dict(row) if row else None

    # ------------------ CLASSIFICATION FEEDBACK ------------------
    def log_feedback(self, attachment_id: int, predicted: str, corrected: str) -> None:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO classification_feedback (attachment_id, predicted_category, corrected_category)
                VALUES (?, ?, ?)
            """,
                (attachment_id, predicted, corrected),
            )

    def get_feedback_records(self) -> List[Dict[str, Any]]:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT f.*, a.original_filename, a.mime_type, a.extension
                FROM classification_feedback f
                JOIN attachments a ON f.attachment_id = a.id
                ORDER BY f.id DESC
            """
            )
            return [dict(row) for row in cursor.fetchall()]

    # ------------------ SYNC HISTORY ------------------
    def start_sync(self, account_id: Optional[int]) -> int:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO sync_history (account_id, status) VALUES (?, 'Running')",
                (account_id,),
            )
            return cursor.lastrowid

    def complete_sync(
        self,
        sync_id: int,
        messages_scanned: int,
        attachments_detected: int,
        status: str = "Completed",
        error_message: Optional[str] = None,
    ) -> None:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                UPDATE sync_history
                SET completed_at = CURRENT_TIMESTAMP,
                    messages_scanned = ?,
                    attachments_detected = ?,
                    status = ?,
                    error_message = ?
                WHERE id = ?
            """,
                (messages_scanned, attachments_detected, status, error_message, sync_id),
            )

    def get_sync_history(self, limit: int = 50) -> List[Dict[str, Any]]:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT s.*, a.account_email, a.imap_host
                FROM sync_history s
                LEFT JOIN email_accounts a ON s.account_id = a.id
                ORDER BY s.id DESC LIMIT ?
            """,
                (limit,),
            )
            return [dict(row) for row in cursor.fetchall()]


# Singleton default database instance
DB = DatabaseManager()
