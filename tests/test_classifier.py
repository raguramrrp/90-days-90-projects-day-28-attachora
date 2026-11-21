"""
Unit tests for Deterministic and Machine Learning Attachment Classification.
"""

from src.classifier.engine import CLASSIFIER
from src.classifier.ml_classifier import LocalMLClassifier
from src.classifier.rules_classifier import classify_by_rules


def test_deterministic_rules_invoices_and_receipts():
    cat1, reason1, conf1 = classify_by_rules("Tax_Invoice_Nov2026.pdf")
    assert cat1 == "Invoices"
    assert "invoice" in reason1.lower()
    assert conf1 == 1.0

    cat2, reason2, conf2 = classify_by_rules("uber_trip_receipt.pdf")
    assert cat2 == "Receipts"
    assert "receipt" in reason2.lower()
    assert conf2 == 1.0


def test_deterministic_rules_resumes_and_spreadsheets():
    cat3, reason3, conf3 = classify_by_rules("ragu_ram_ai_engineer_resume.pdf")
    assert cat3 == "Resumes / CVs"
    assert conf3 == 1.0

    cat4, reason4, conf4 = classify_by_rules("q4_financials.csv")
    assert cat4 == "Spreadsheets"
    assert conf4 == 1.0


def test_deterministic_rules_code_and_archives():
    cat5, reason5, conf5 = classify_by_rules("api_service.py")
    assert cat5 == "Code / Technical Files"
    assert conf5 == 1.0

    cat6, reason6, conf6 = classify_by_rules("archive_bundle.zip")
    assert cat6 == "Archives"
    assert conf6 == 1.0


def test_unified_classifier_returns_complete_structure():
    res = CLASSIFIER.classify_attachment(
        filename="billing_invoice.pdf",
        mime_type="application/pdf",
        subject="Monthly Cloud Bill",
    )
    assert res["category"] == "Invoices"
    assert res["classification_method"] == "Deterministic Rules"
    assert "confidence" in res
    assert res["file_type"] == "PDF"


def test_ml_classifier_retraining_with_feedback():
    ml = LocalMLClassifier()
    # Test initial prediction
    pred, conf = ml.predict("unknown_dataset_tokens.parquet", "application/octet-stream")
    assert isinstance(pred, str)
    assert 0.0 <= conf <= 1.0

    # Add feedback records
    feedback = [
        {"original_filename": "custom_parquet_file.parquet", "mime_type": "application/octet-stream", "corrected_category": "Spreadsheets"},
        {"original_filename": "another_dataset.parquet", "mime_type": "application/octet-stream", "corrected_category": "Spreadsheets"},
    ]
    added = ml.retrain_with_feedback(feedback)
    assert added == 2
    # Verify model remains trained
    assert ml.is_trained is True
