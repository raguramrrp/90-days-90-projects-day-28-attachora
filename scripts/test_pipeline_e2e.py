"""
End-to-end integration test script for ATTACHORA.
Imports all 12 sample .EML files, simulates approval and organization,
tests duplicate handling and undo operations.
"""

from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from src.analytics.reporter import REPORTER
from src.config import CONFIG
from src.database.db_manager import DB
from src.email_engine.reader import READER
from src.rules_engine.rule_evaluator import match_filing_rules
from src.storage_manager.organizer import ORGANIZER
from src.storage_manager.undo_manager import UNDO_MANAGER


def main():
    print("--- 1. Ingesting Sample EML Files ---")
    eml_files = sorted(list(CONFIG.SAMPLE_EMAILS_DIR.glob("*.eml")))
    print(f"Found {len(eml_files)} sample files.")

    total_staged = 0
    for eml in eml_files:
        staged = READER.import_eml_file(eml)
        total_staged += len(staged)
        print(f"  Processed {eml.name}: {len(staged)} attachments detected.")

    print(f"\nTotal attachments staged: {total_staged}")

    # Inspect DB attachments
    attachments = DB.get_attachments_workspace()
    print(f"Database active attachments: {len(attachments)}")

    # Check for Duplicate detection
    duplicates = [a for a in attachments if a["status"] == "Duplicate"]
    print(f"Identified duplicate attachments: {len(duplicates)}")
    assert len(duplicates) >= 1, "Expected at least 1 duplicate attachment detected from email_10"

    print("\n--- 2. Simulating Approval & Organization of First 3 Attachments ---")
    rules = DB.get_rules(enabled_only=True)
    organized_ids = []
    for att in attachments[:3]:
        rule_match = match_filing_rules(rules, att, {"sender": att.get("sender"), "received_at": att.get("received_at")})
        res = ORGANIZER.organize_attachment(
            attachment_id=att["id"],
            destination_folder=rule_match["destination"],
            proposed_filename=rule_match["proposed_filename"],
            duplicate_action="keep_copy",
        )
        print(f"  Organized #{att['id']} ({att['original_filename']}) -> {res.get('final_path')}")
        assert res["success"] is True
        organized_ids.append(att["id"])

    # Verify metrics
    metrics = REPORTER.get_summary_metrics()
    print(f"\n--- 3. Database Operational Metrics ---")
    print(f"  Total Detected: {metrics['total_detected']}")
    print(f"  Total Organized: {metrics['total_organized']}")
    print(f"  Awaiting Approval: {metrics['awaiting_approval']}")
    print(f"  Duplicates Detected: {metrics['duplicates_count']}")
    print(f"  Storage Organized: {metrics['total_storage_organized_mb']} MB")

    print("\n--- 4. Testing Undo Operation on First Organized File ---")
    undo_id = organized_ids[0]
    undo_res = UNDO_MANAGER.undo_operation(undo_id)
    print(f"  Undo result for #{undo_id}: {undo_res['message']}")
    assert undo_res["success"] is True

    # Verify updated metrics
    updated_metrics = REPORTER.get_summary_metrics()
    print(f"  Organized count after undo: {updated_metrics['total_organized']}")
    assert updated_metrics["total_organized"] == metrics["total_organized"] - 1

    print("\n[SUCCESS] End-to-end integration workflow verified 100% operational!")


if __name__ == "__main__":
    main()
