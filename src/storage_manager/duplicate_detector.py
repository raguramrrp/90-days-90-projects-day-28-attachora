"""
ATTACHORA Duplicate Detector
Classifies attachments using SHA-256 cryptographic hashes and filename collision analysis.
"""

from pathlib import Path
from typing import Any, Dict, List, Optional
from src.database.db_manager import DatabaseManager


class DuplicateDetector:
    def __init__(self, db: DatabaseManager):
        self.db = db

    def inspect_duplicate(
        self,
        sha256: str,
        filename: str,
        target_destination_dir: Optional[Path] = None,
        exclude_attachment_id: Optional[int] = None,
    ) -> Dict[str, Any]:
        """Classifies attachment duplication status.

        Possible results:
        - Exact Duplicate (Confirmed SHA-256 match in database)
        - Existing Filename Conflict (Different SHA-256, but file with exact name exists at target)
        - Potentially Similar Name (Different SHA-256, but normalized name matches existing record)
        - New File (Unique content and unique name)
        """
        # 1. Exact SHA-256 match
        existing_by_hash = self.db.get_attachments_by_hash(sha256)
        if exclude_attachment_id:
            existing_by_hash = [a for a in existing_by_hash if a["id"] != exclude_attachment_id]

        # Check if any existing record is organized on disk
        for existing in existing_by_hash:
            if existing.get("status") in ("Organized", "Detected", "Pending Approval"):
                return {
                    "status": "Exact Duplicate",
                    "reason": f"Identical file content (SHA-256: {sha256[:12]}...) already registered in system",
                    "existing_attachment_id": existing["id"],
                    "existing_file_path": existing.get("current_path") or existing.get("original_path"),
                    "can_skip": True,
                }

        # 2. Existing filename conflict at physical target directory
        if target_destination_dir and target_destination_dir.exists():
            target_file = target_destination_dir / filename
            if target_file.exists():
                return {
                    "status": "Existing Filename Conflict",
                    "reason": f"A different file named '{filename}' already exists in target folder",
                    "existing_attachment_id": None,
                    "existing_file_path": str(target_file),
                    "can_skip": False,
                }

        # 3. Potentially similar filename in database
        clean_name = filename.lower().replace("_", "").replace("-", "").replace(" ", "")
        similar_records = self.db.get_attachments_workspace(search_query=Path(filename).stem[:6])
        if exclude_attachment_id:
            similar_records = [r for r in similar_records if r["id"] != exclude_attachment_id]

        for sim in similar_records:
            sim_name = (sim.get("original_filename") or "").lower().replace("_", "").replace("-", "").replace(" ", "")
            if sim_name == clean_name and sim.get("sha256") != sha256:
                return {
                    "status": "Potentially Similar Name",
                    "reason": f"Filename similar to previously received '{sim.get('original_filename')}', but contents differ",
                    "existing_attachment_id": sim["id"],
                    "existing_file_path": sim.get("current_path"),
                    "can_skip": False,
                }

        # 4. New unique file
        return {
            "status": "New File",
            "reason": "Unique content and unique filename. Ready for organization.",
            "existing_attachment_id": None,
            "existing_file_path": None,
            "can_skip": False,
        }
