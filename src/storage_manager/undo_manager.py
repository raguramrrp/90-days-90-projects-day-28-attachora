"""
ATTACHORA Undo & Restoration Manager
Provides rollback of organized file operations, restoring files to staging paths
safely without overwriting existing data.
"""

import os
from pathlib import Path
import shutil
from typing import Any, Dict, Optional
from src.database.db_manager import DatabaseManager


class UndoManager:
    def __init__(self, db: DatabaseManager):
        self.db = db

    def undo_operation(self, attachment_id: int) -> Dict[str, Any]:
        """Rolls back an organized attachment, moving it back to staging and updating history."""
        # Find the last organize operation for this attachment
        op = self.db.get_last_successful_organize_operation(attachment_id)
        if not op:
            return {"success": False, "error": f"No successful organize operation found for attachment ID {attachment_id}."}

        dest_path_str = op.get("destination_path")
        source_path_str = op.get("source_path")

        if not dest_path_str:
            return {"success": False, "error": "Destination path missing from operation record."}

        dest_file = Path(dest_path_str)
        if not dest_file.exists():
            return {
                "success": False,
                "error": f"Target organized file no longer exists on disk: {dest_path_str}",
            }

        # Check source/staging restoration destination
        source_path = Path(source_path_str) if source_path_str else None
        if not source_path:
            # Fall back to staging folder
            staging_dir = Path("./.attachora_staging")
            staging_dir.mkdir(parents=True, exist_ok=True)
            source_path = staging_dir / op.get("previous_filename", dest_file.name)

        # Ensure parent directory of restoration target exists
        source_path.parent.mkdir(parents=True, exist_ok=True)

        # Do not overwrite if source path somehow exists already
        restore_target = source_path
        if restore_target.exists():
            stem = restore_target.stem
            ext = restore_target.suffix
            counter = 1
            while restore_target.exists():
                restore_target = source_path.parent / f"{stem}_restored_{counter}{ext}"
                counter += 1

        try:
            # Move the file from organized library back to staging/source
            shutil.move(str(dest_file), str(restore_target))

            # Update attachment status
            self.db.update_attachment_status(
                attachment_id=attachment_id,
                status="Restored",
                current_path=str(restore_target),
                stored_filename=restore_target.name,
            )

            # Log undo operation in audit table
            self.db.log_operation(
                attachment_id=attachment_id,
                operation_type="Undo",
                source_path=str(dest_file),
                destination_path=str(restore_target),
                previous_filename=dest_file.name,
                final_filename=restore_target.name,
                status="Restored",
                error_message=None,
            )

            return {
                "success": True,
                "status": "Restored",
                "restored_path": str(restore_target),
                "message": f"Successfully restored to {restore_target.name}",
            }
        except Exception as e:
            err = f"Failed to undo file operation: {str(e)}"
            self.db.log_operation(
                attachment_id=attachment_id,
                operation_type="Undo",
                source_path=str(dest_file),
                destination_path=str(restore_target),
                previous_filename=dest_file.name,
                final_filename=None,
                status="Failed",
                error_message=err,
            )
            return {"success": False, "error": err}


# Singleton undo manager instance
UNDO_MANAGER = UndoManager(db=DatabaseManager())
