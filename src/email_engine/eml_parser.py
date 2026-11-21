"""
ATTACHORA EML Parser
Parses RFC 822 / MIME .eml files and byte streams, extracting headers, metadata,
and attachments while decoding RFC 2047 / RFC 2231 encoded filenames.
"""

from datetime import datetime
from email import policy
from email.header import decode_header
from email.message import EmailMessage
from email.parser import BytesParser
from email.utils import parseaddr, parsedate_to_datetime
from io import BytesIO
import os
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
from src.security.hasher import calculate_sha256
from src.security.sanitizer import sanitize_filename
from src.security.validator import guess_mime_and_extension


def decode_mime_header(header_value: Optional[str]) -> str:
    """Decodes MIME encoded header strings (RFC 2047) into clean Unicode."""
    if not header_value:
        return ""
    try:
        decoded_slices = decode_header(header_value)
        pieces = []
        for text, encoding in decoded_slices:
            if isinstance(text, bytes):
                enc = encoding or "utf-8"
                try:
                    pieces.append(text.decode(enc, errors="replace"))
                except Exception:
                    pieces.append(text.decode("latin-1", errors="replace"))
            else:
                pieces.append(str(text))
        return " ".join(pieces).strip()
    except Exception:
        return str(header_value).strip()


def parse_eml_bytes(raw_bytes: bytes, source_identifier: str = "direct_upload") -> Dict[str, Any]:
    """Parses raw EML bytes into structured email metadata and extracted attachment streams."""
    parser = BytesParser(policy=policy.default)
    msg: EmailMessage = parser.parsebytes(raw_bytes)

    # Extract headers
    raw_from = msg.get("From", "")
    sender_name, sender_email = parseaddr(raw_from)
    sender_name = decode_mime_header(sender_name) or sender_email

    subject = decode_mime_header(msg.get("Subject", "(No Subject)"))
    message_id = msg.get("Message-ID", f"local-{calculate_sha256(raw_bytes)[:16]}")

    # Received timestamp
    date_header = msg.get("Date")
    received_at_iso = None
    if date_header:
        try:
            dt = parsedate_to_datetime(date_header)
            received_at_iso = dt.isoformat()
        except Exception:
            received_at_iso = datetime.now().isoformat()
    else:
        received_at_iso = datetime.now().isoformat()

    extracted_attachments: List[Dict[str, Any]] = []

    # Iterate MIME parts to locate attachments
    for part in msg.walk():
        # Check if part is an attachment
        content_disposition = part.get_content_disposition()
        filename = part.get_filename()

        # Some mail clients don't set disposition='attachment', but set filename
        is_attachment = content_disposition in ("attachment", "inline") and bool(filename)

        if not is_attachment:
            continue

        decoded_fn = decode_mime_header(filename)
        clean_fn = sanitize_filename(decoded_fn)

        payload_bytes = part.get_payload(decode=True)
        if not payload_bytes:
            continue

        part_mime = part.get_content_type()
        guessed_mime, ext = guess_mime_and_extension(clean_fn, payload_bytes[:32])
        effective_mime = part_mime if (part_mime and part_mime != "application/octet-stream") else guessed_mime

        sha256 = calculate_sha256(payload_bytes)

        extracted_attachments.append(
            {
                "original_filename": clean_fn,
                "mime_type": effective_mime,
                "extension": ext,
                "file_size": len(payload_bytes),
                "sha256": sha256,
                "content_bytes": payload_bytes,
            }
        )

    return {
        "message_id": message_id,
        "sender": sender_name,
        "sender_email": sender_email.lower(),
        "subject": subject,
        "received_at": received_at_iso,
        "source": source_identifier,
        "attachment_count": len(extracted_attachments),
        "attachments": extracted_attachments,
    }


def parse_eml_file(file_path: Path) -> Dict[str, Any]:
    """Reads and parses an .eml file from disk."""
    with open(file_path, "rb") as f:
        raw_bytes = f.read()
    return parse_eml_bytes(raw_bytes, source_identifier=file_path.name)
