"""
Unit tests for Path & Filename Sanitization and Path Traversal Defense.
"""

from pathlib import Path
import pytest
from src.security.sanitizer import (
    resolve_safe_destination,
    sanitize_filename,
    sanitize_relative_path,
)


def test_sanitize_windows_illegal_characters():
    dirty = 'inv:oice/test*?<bad>|"name".pdf'
    clean = sanitize_filename(dirty)
    assert ":" not in clean
    assert "/" not in clean
    assert "*" not in clean
    assert "?" not in clean
    assert "<" not in clean
    assert ">" not in clean
    assert "|" not in clean
    assert '"' not in clean
    assert clean.endswith(".pdf")


def test_sanitize_trailing_dots_and_spaces():
    dirty = "invoice_nov2026.pdf...   "
    clean = sanitize_filename(dirty)
    assert not clean.endswith(".")
    assert not clean.endswith(" ")
    assert clean == "invoice_nov2026.pdf"


def test_sanitize_windows_reserved_names():
    assert sanitize_filename("CON.pdf") == "CON_file.pdf"
    assert sanitize_filename("nul.txt") == "nul_file.txt"
    assert sanitize_filename("prn.csv") == "prn_file.csv"


def test_sanitize_relative_path_strips_traversal():
    assert sanitize_relative_path("../../../etc/passwd") == "etc/passwd"
    assert sanitize_relative_path("Finance/../../Windows/System32") == "Finance/Windows/System32"
    assert sanitize_relative_path("") == "Unclassified"


def test_resolve_safe_destination_prevents_escape(tmp_path):
    root = tmp_path / "ATTACHORA_LIBRARY"
    root.mkdir()

    # Valid relative destination
    target, filename = resolve_safe_destination(root, "Finance/Invoices", "bill.pdf")
    assert target.is_relative_to(root)
    assert filename == "bill.pdf"

    # Malicious path traversal
    with pytest.raises(ValueError):
        # We manually verify relative_to check triggers if target leaves root
        malicious_p = Path("../../secret.txt")
        # sanitizer strips traversal, but if an absolute path escapes:
        resolve_safe_destination(root, "/Windows/System32", "trojan.exe")
