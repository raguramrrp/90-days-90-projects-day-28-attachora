"""
Unit tests for SHA-256 Hashes and Duplicate Detection Logic.
"""

from pathlib import Path
import pytest
from src.database.db_manager import DatabaseManager
from src.security.hasher import calculate_sha256
from src.storage_manager.duplicate_detector import DuplicateDetector


def test_calculate_sha256_bytes_and_file(tmp_path):
    sample_bytes = b"ATTACHORA_TEST_FILE_CONTENT_2026"
    expected_hash = "d83e4661e9e4e0164aa4e3d3aebe95d2263a8f55ee9a4000a1fc6d632ee15263"

    assert calculate_sha256(sample_bytes) == expected_hash

    # Test file path
    f = tmp_path / "test.bin"
    f.write_bytes(sample_bytes)
    assert calculate_sha256(f) == expected_hash


def test_duplicate_detector_exact_and_conflict(tmp_path):
    db_file = tmp_path / "test_dup.db"
    db = DatabaseManager(db_path=db_file)
    detector = DuplicateDetector(db)

    hash_val = "1111222233334444555566667777888899990000aaaabbbbccccddddeeeeffff"

    # Initially New File
    res1 = detector.inspect_duplicate(sha256=hash_val, filename="contract.pdf")
    assert res1["status"] == "New File"

    # Insert an email and attachment into DB
    eid = db.insert_email(None, "uid1", "msg1", "Sender", "sender@test.com", "Subject", "2026-11-21")
    db.insert_attachment(
        email_id=eid,
        original_filename="contract.pdf",
        stored_filename="contract.pdf",
        mime_type="application/pdf",
        extension="pdf",
        file_size=5000,
        sha256=hash_val,
        category="Documents",
        classification_method="rules",
        classification_reason="reason",
        confidence=1.0,
        original_path="/tmp/contract.pdf",
        current_path="/library/contract.pdf",
        status="Organized",
    )

    # Now same hash should detect Exact Duplicate
    res2 = detector.inspect_duplicate(sha256=hash_val, filename="contract_copy.pdf")
    assert res2["status"] == "Exact Duplicate"
    assert res2["can_skip"] is True

    # Test physical target filename conflict with different hash
    target_dir = tmp_path / "target_folder"
    target_dir.mkdir()
    (target_dir / "statement.pdf").write_bytes(b"existing content")

    res3 = detector.inspect_duplicate(
        sha256="different_hash_9999",
        filename="statement.pdf",
        target_destination_dir=target_dir,
    )
    assert res3["status"] == "Existing Filename Conflict"
