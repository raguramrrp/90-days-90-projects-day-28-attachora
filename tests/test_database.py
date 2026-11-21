"""
Unit tests for SQLite Database Manager, CRUD operations, and Schema integrity.
"""

from src.database.db_manager import DatabaseManager


def test_database_init_and_default_rules(tmp_path):
    db_file = tmp_path / "test_init.db"
    db = DatabaseManager(db_path=db_file)

    rules = db.get_rules()
    assert len(rules) >= 5
    assert any(r["rule_name"] == "Invoices to Finance" for r in rules)


def test_database_account_crud(tmp_path):
    db_file = tmp_path / "test_accounts.db"
    db = DatabaseManager(db_path=db_file)

    acc_id = db.add_account("user@example.com", "imap.example.com", 993, "INBOX", "password")
    assert acc_id > 0

    acc = db.get_account_by_id(acc_id)
    assert acc["account_email"] == "user@example.com"
    assert acc["connection_status"] == "configured"

    db.update_account_status(acc_id, "connected", last_sync="2026-11-21T12:00:00")
    acc_updated = db.get_account_by_id(acc_id)
    assert acc_updated["connection_status"] == "connected"

    db.delete_account(acc_id)
    assert db.get_account_by_id(acc_id) is None


def test_database_email_and_attachment_persistence(tmp_path):
    db_file = tmp_path / "test_email_att.db"
    db = DatabaseManager(db_path=db_file)

    eid = db.insert_email(None, "uid-100", "msg-100", "Sender", "sender@test.com", "Subject", "2026-11-21")
    assert eid > 0

    aid = db.insert_attachment(
        email_id=eid,
        original_filename="sample.pdf",
        stored_filename="sample_organized.pdf",
        mime_type="application/pdf",
        extension="pdf",
        file_size=1024,
        sha256="abc123sha256",
        category="Documents",
        classification_method="rules",
        classification_reason="reason",
        confidence=1.0,
        original_path="/tmp/sample.pdf",
        current_path="/library/sample.pdf",
        status="Detected",
    )
    assert aid > 0

    att = db.get_attachment_by_id(aid)
    assert att["original_filename"] == "sample.pdf"
    assert att["status"] == "Detected"

    # Test operation logging
    op_id = db.log_operation(aid, "Classify", "/tmp/sample.pdf", "/library/sample.pdf", "sample.pdf", "sample_organized.pdf", "Organized")
    assert op_id > 0

    ops = db.get_operations()
    assert len(ops) == 1
    assert ops[0]["operation_type"] == "Classify"
