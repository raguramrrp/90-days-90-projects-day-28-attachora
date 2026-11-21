"""
Unit tests for RFC 822 / MIME Email Parsing and Attachment Extraction.
"""

from email.message import EmailMessage
from email.utils import formatdate
from src.email_engine.eml_parser import decode_mime_header, parse_eml_bytes


def test_decode_mime_header():
    # Plain ascii
    assert decode_mime_header("Monthly Statement") == "Monthly Statement"
    # RFC 2047 utf-8
    rfc_utf8 = "=?utf-8?B?QXR0YWNobWVudCBJbnZvaWNl?="
    assert decode_mime_header(rfc_utf8) == "Attachment Invoice"


def test_parse_eml_bytes_extracts_attachments():
    msg = EmailMessage()
    msg["From"] = "Billing Team <billing@acme.com>"
    msg["To"] = "client@acme.com"
    msg["Subject"] = "Your Invoice INV-99"
    msg["Date"] = formatdate(localtime=True)
    msg["Message-ID"] = "<inv-99@acme.com>"
    msg.set_content("Please find attached.")

    payload = b"%PDF-1.4 sample pdf binary data"
    msg.add_attachment(payload, maintype="application", subtype="pdf", filename="invoice_nov.pdf")

    raw_bytes = msg.as_bytes()
    data = parse_eml_bytes(raw_bytes, source_identifier="test_message")

    assert data["sender_email"] == "billing@acme.com"
    assert data["subject"] == "Your Invoice INV-99"
    assert data["attachment_count"] == 1

    att = data["attachments"][0]
    assert att["original_filename"] == "invoice_nov.pdf"
    assert att["mime_type"] == "application/pdf"
    assert att["file_size"] == len(payload)
    assert len(att["sha256"]) == 64
