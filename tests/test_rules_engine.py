"""
Unit tests for Filing Rules, Condition Groups (AND/OR), and Filename Templates.
"""

from pathlib import Path
from src.rules_engine.rule_evaluator import match_filing_rules
from src.rules_engine.template_engine import (
    generate_unique_conflict_filename,
    render_filename_template,
)


def test_filename_template_rendering():
    att = {
        "original_filename": "invoice_1042.pdf",
        "category": "Invoices",
    }
    email = {
        "sender": "Stripe Payments <billing@stripe.com>",
        "sender_email": "billing@stripe.com",
        "subject": "Monthly Payout Statement",
        "received_at": "2026-11-21T10:00:00",
    }

    # Template with {date}, {category}, {sender}
    rendered = render_filename_template("{date}_{category}_{sender}_{original_filename}", att, email)
    assert "20261121" in rendered
    assert "Invoices" in rendered
    assert "invoice_1042.pdf" in rendered


def test_generate_unique_conflict_filename(tmp_path):
    target_dir = tmp_path / "Finance"
    target_dir.mkdir()

    # Create existing file
    (target_dir / "invoice.pdf").write_bytes(b"content")

    # Should generate _001
    new_fn = generate_unique_conflict_filename(target_dir, "invoice.pdf")
    assert new_fn == "invoice_001.pdf"

    # Create invoice_001.pdf
    (target_dir / "invoice_001.pdf").write_bytes(b"content 2")
    new_fn2 = generate_unique_conflict_filename(target_dir, "invoice.pdf")
    assert new_fn2 == "invoice_002.pdf"


def test_rule_matching_priority_and_and_or():
    rules = [
        {
            "id": 1,
            "rule_name": "Invoice High Priority",
            "conditions": {
                "logic": "AND",
                "rules": [{"field": "category", "operator": "equals", "value": "Invoices"}],
            },
            "destination": "Finance/Invoices",
            "filename_template": "{date}_{original_filename}",
            "priority": 1,
            "enabled": 1,
        },
        {
            "id": 2,
            "rule_name": "Company Domain Fallback",
            "conditions": {
                "logic": "AND",
                "rules": [{"field": "sender_domain", "operator": "equals", "value": "acme.com"}],
            },
            "destination": "Company/Internal",
            "filename_template": "{original_filename}",
            "priority": 2,
            "enabled": 1,
        },
    ]

    att = {"original_filename": "bill.pdf", "category": "Invoices"}
    email = {"sender_email": "billing@acme.com", "sender": "Acme Billing"}

    # Priority 1 should match first
    res = match_filing_rules(rules, att, email)
    assert res["matched"] is True
    assert res["rule_name"] == "Invoice High Priority"
    assert res["destination"] == "Finance/Invoices"
