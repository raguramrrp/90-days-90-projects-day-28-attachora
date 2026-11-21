"""
ATTACHORA File Organizer
Safely transfers and organizes validated attachments into structured local directories
with conflict resolution, path traversal defense, and comprehensive audit logging.
"""

from pathlib import Path
import shutil
from typing import Any, Dict, Optional, Tuple
from src.config import CONFIG
from src.database.db_manager import DatabaseManager
from src.rules_engine.template_engine import generate_unique_conflict_filename
from src.security.sanitizer import resolve_safe_destination


class FileOrganizer:
    def __init__(self, db: DatabaseManager, storage_root: Optional[Path] = None):
        self.db = db
        self.storage_root = Path(storage_root or CONFIG.STORAGE_ROOT)
        self.storage_root.mkdir(parents=True, exist_ok=True)

    def organize_attachment(
        self,
        attachment_id: int,
        destination_folder: str,
        proposed_filename: str,
        duplicate_action: str = "keep_copy",  # "skip", "keep_copy", "keep_reference"
        reference_path: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Organizes a single attachment to the structured library."""
        att = self.db.get_attachment_by_id(attachment_id)
        if not att:
            return {"success": False, "error": f"Attachment ID {attachment_id} not found."}

        source_path_str = att.get("current_path") or att.get("original_path")
        if not source_path_str:
            return {"success": False, "error": "Source path missing for attachment."}

        source_path = Path(source_path_str)
        if not source_path.exists():
            return {"success": False, "error": f"Staging source file does not exist: {source_path}"}

        # Handle duplicate strategy: SKIP
        if duplicate_action == "skip":
            self.db.update_attachment_status(attachment_id, status="Skipped")
            self.db.log_operation(
                attachment_id=attachment_id,
                operation_type="Skip",
                source_path=str(source_path),
                destination_path=None,
                previous_filename=att.get("original_filename"),
                final_filename=None,
                status="Skipped",
                error_message="Skipped per duplicate handling policy",
            )
            return {
                "success": True,
                "status": "Skipped",
                "final_path": None,
                "message": "Duplicate attachment skipped successfully.",
            }

        # Handle duplicate strategy: KEEP REFERENCE
        if duplicate_action == "keep_reference" and reference_path:
            self.db.update_attachment_status(
                attachment_id=attachment_id,
                status="Duplicate",
                current_path=reference_path,
                stored_filename=Path(reference_path).name,
            )
            self.db.log_operation(
                attachment_id=attachment_id,
                operation_type="Duplicate-Ref",
                source_path=str(source_path),
                destination_path=reference_path,
                previous_filename=att.get("original_filename"),
                final_filename=Path(reference_path).name,
                status="Duplicate",
                error_message="Linked as reference to existing stored file",
            )
            return {
                "success": True,
                "status": "Duplicate",
                "final_path": reference_path,
                "message": "Referenced existing file without duplicating storage.",
            }

        # Resolve destination path safely (defense against path traversal)
        try:
            target_file, clean_filename = resolve_safe_destination(
                storage_root=self.storage_root,
                relative_dir=destination_folder,
                filename=proposed_filename,
            )
        except ValueError as pe:
            self.db.log_operation(
                attachment_id=attachment_id,
                operation_type="Organize",
                source_path=str(source_path),
                destination_path=None,
                previous_filename=att.get("original_filename"),
                final_filename=None,
                status="Failed",
                error_message=str(pe),
            )
            return {"success": False, "error": str(pe)}

        # Conflict resolution: if destination file exists, append _001
        target_dir = target_file.parent
        target_dir.mkdir(parents=True, exist_ok=True)
        final_filename = generate_unique_conflict_filename(target_dir, clean_filename)
        final_dest_file = target_dir / final_filename

        try:
            # Perform atomic file copy
            shutil.copy2(source_path, final_dest_file)

            # Update DB record
            self.db.update_attachment_status(
                attachment_id=attachment_id,
                status="Organized",
                current_path=str(final_dest_file),
                stored_filename=final_filename,
            )

            # Log operation
            self.db.log_operation(
                attachment_id=attachment_id,
                operation_type="Organize",
                source_path=str(source_path),
                destination_path=str(final_dest_file),
                previous_filename=att.get("original_filename"),
                final_filename=final_filename,
                status="Organized",
                error_message=None,
            )

            return {
                "success": True,
                "status": "Organized",
                "final_path": str(final_dest_file),
                "final_filename": final_filename,
                "message": f"Organized to {destination_folder}/{final_filename}",
            }
        except Exception as e:
            error_msg = f"Failed to organize file: {str(e)}"
            self.db.update_attachment_status(attachment_id, status="Failed")
            self.db.log_operation(
                attachment_id=attachment_id,
                operation_type="Organize",
                source_path=str(source_path),
                destination_path=str(final_dest_file),
                previous_filename=att.get("original_filename"),
                final_filename=final_filename,
                status="Failed",
                error_message=error_msg,
            )
            return {"success": False, "error": error_msg}


# Singleton organizer instance
ORGANIZER = FileOrganizer(db=DatabaseManager())
