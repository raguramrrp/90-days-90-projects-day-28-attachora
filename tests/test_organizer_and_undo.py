"""
Unit tests for Atomic File Organization and Undo / Rollback Operations.
"""

from pathlib import Path
from src.database.db_manager import DatabaseManager
from src.storage_manager.organizer import FileOrganizer
from src.storage_manager.undo_manager import UndoManager


def test_organize_and_undo_lifecycle(tmp_path):
    db_file = tmp_path / "test_org.db"
    db = DatabaseManager(db_path=db_file)

    storage_root = tmp_path / "ATTACHORA_LIBRARY"
    storage_root.mkdir()
    staging_dir = tmp_path / "staging"
    staging_dir.mkdir()

    organizer = FileOrganizer(db=db, storage_root=storage_root)
    undo_mgr = UndoManager(db=db)

    # Create dummy staging file
    staging_file = staging_dir / "invoice_test.pdf"
    staging_file.write_bytes(b"PDF_SAMPLE_DATA_12345")

    # Insert into DB
    eid = db.insert_email(None, "uid-1", "msg-1", "AWS", "aws@amazon.com", "Invoice", "2026-11-21")
    aid = db.insert_attachment(
        email_id=eid,
        original_filename="invoice_test.pdf",
        stored_filename=None,
        mime_type="application/pdf",
        extension="pdf",
        file_size=len(b"PDF_SAMPLE_DATA_12345"),
        sha256="fake_sha256_hash",
        category="Invoices",
        classification_method="rules",
        classification_reason="test",
        confidence=1.0,
        original_path=str(staging_file),
        current_path=str(staging_file),
        status="Pending Approval",
    )

    # 1. Execute Organize
    res = organizer.organize_attachment(
        attachment_id=aid,
        destination_folder="Finance/Invoices",
        proposed_filename="20261121_invoice_test.pdf",
        duplicate_action="keep_copy",
    )
    assert res["success"] is True
    assert res["status"] == "Organized"

    organized_file = Path(res["final_path"])
    assert organized_file.exists()
    assert organized_file.read_bytes() == b"PDF_SAMPLE_DATA_12345"

    # Verify DB status updated
    att_updated = db.get_attachment_by_id(aid)
    assert att_updated["status"] == "Organized"
    assert att_updated["current_path"] == str(organized_file)

    # 2. Execute Undo / Rollback
    undo_res = undo_mgr.undo_operation(attachment_id=aid)
    assert undo_res["success"] is True
    assert undo_res["status"] == "Restored"

    # Verify organized file removed from library and moved to restored location
    assert not organized_file.exists()
    restored_file = Path(undo_res["restored_path"])
    assert restored_file.exists()

    # Verify DB status updated to Restored
    att_restored = db.get_attachment_by_id(aid)
    assert att_restored["status"] == "Restored"
