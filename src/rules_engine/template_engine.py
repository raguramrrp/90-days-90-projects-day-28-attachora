"""
ATTACHORA Filename Template Engine
Renders dynamic, sanitized filenames from organizational templates and context variables.
"""

from datetime import datetime
import os
from pathlib import Path
import re
from typing import Any, Dict, Optional
from src.security.sanitizer import sanitize_filename


def extract_sender_domain(email_address: str) -> str:
    """Extracts domain from email string, e.g. 'accounts@stripe.com' -> 'stripe.com'."""
    if not email_address or "@" not in email_address:
        return "external"
    parts = email_address.strip().split("@")
    return parts[-1].split(">")[0].strip().lower()


def extract_sender_handle(email_address: str) -> str:
    """Extracts username or clean handle from sender, e.g. 'John Doe <john@acme.com>' -> 'John_Doe'."""
    if not email_address:
        return "sender"
    if "<" in email_address:
        name = email_address.split("<")[0].strip()
        if name:
            return sanitize_filename(name).replace(" ", "_")
    return sanitize_filename(email_address.split("@")[0]).replace(" ", "_")


def render_filename_template(
    template: str,
    attachment: Dict[str, Any],
    email: Optional[Dict[str, Any]] = None,
) -> str:
    """Renders a filename template with context variables and sanitizes the output."""
    email_data = email or {}

    # Extract date string
    received_at = email_data.get("received_at")
    date_str = datetime.now().strftime("%Y%m%d")
    if received_at:
        try:
            # Parse ISO or standard string
            dt = datetime.fromisoformat(str(received_at).replace("Z", "+00:00"))
            date_str = dt.strftime("%Y%m%d")
        except Exception:
            pass

    orig_fn = attachment.get("original_filename", "attachment.dat")
    stem, ext = os.path.splitext(orig_fn)

    category = attachment.get("category", "Document").replace(" ", "_").replace("/", "-")
    sender_email = email_data.get("sender_email", "") or email_data.get("sender", "")
    sender_domain = extract_sender_domain(sender_email)
    sender_handle = extract_sender_handle(email_data.get("sender", "") or sender_email)
    subject = sanitize_filename(email_data.get("subject", "email") or "email")[:40]

    template_str = template or "{original_filename}"

    # Replace template tokens
    rendered = template_str.replace("{date}", date_str)
    rendered = rendered.replace("{category}", category)
    rendered = rendered.replace("{original_filename}", orig_fn)
    rendered = rendered.replace("{filename_stem}", stem)
    rendered = rendered.replace("{sender}", sender_handle)
    rendered = rendered.replace("{sender_domain}", sender_domain)
    rendered = rendered.replace("{subject}", subject)

    # Ensure extension is retained if missing from template
    if not rendered.lower().endswith(ext.lower()):
        rendered = f"{rendered}{ext}"

    return sanitize_filename(rendered)


def generate_unique_conflict_filename(destination_dir: Path, target_filename: str) -> str:
    """If target_filename already exists in destination_dir, appends _001, _002 without overwriting."""
    stem, ext = os.path.splitext(target_filename)
    candidate = target_filename
    counter = 1

    while (destination_dir / candidate).exists():
        candidate = f"{stem}_{counter:03d}{ext}"
        counter += 1
        if counter > 999:
            # Safety circuit breaker
            import uuid

            candidate = f"{stem}_{uuid.uuid4().hex[:6]}{ext}"
            break

    return candidate
