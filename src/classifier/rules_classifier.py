"""
ATTACHORA Deterministic Rules Classifier
Classifies attachments using file extensions, MIME types, filename patterns,
and keyword heuristics. Provides 100% explainable, deterministic classification reasons.
"""

from pathlib import Path
import re
from typing import Any, Dict, Optional, Tuple

# Mapping of file extensions to initial category candidates
EXTENSION_MAP = {
    # Spreadsheets
    "xlsx": "Spreadsheets",
    "xls": "Spreadsheets",
    "csv": "Spreadsheets",
    "tsv": "Spreadsheets",
    "ods": "Spreadsheets",
    "xlsm": "Spreadsheets",
    # Presentations
    "pptx": "Presentations",
    "ppt": "Presentations",
    "key": "Presentations",
    "odp": "Presentations",
    # Documents
    "docx": "Documents",
    "doc": "Documents",
    "odt": "Documents",
    "rtf": "Documents",
    "txt": "Documents",
    "pages": "Documents",
    # Images
    "png": "Images",
    "jpg": "Images",
    "jpeg": "Images",
    "gif": "Images",
    "webp": "Images",
    "svg": "Images",
    "bmp": "Images",
    "tiff": "Images",
    "ico": "Images",
    # Audio
    "mp3": "Audio",
    "wav": "Audio",
    "ogg": "Audio",
    "m4a": "Audio",
    "flac": "Audio",
    "aac": "Audio",
    # Videos
    "mp4": "Videos",
    "mkv": "Videos",
    "mov": "Videos",
    "avi": "Videos",
    "wmv": "Videos",
    "webm": "Videos",
    # Archives
    "zip": "Archives",
    "tar": "Archives",
    "gz": "Archives",
    "7z": "Archives",
    "rar": "Archives",
    "bz2": "Archives",
    # Code / Technical Files
    "py": "Code / Technical Files",
    "js": "Code / Technical Files",
    "ts": "Code / Technical Files",
    "html": "Code / Technical Files",
    "css": "Code / Technical Files",
    "json": "Code / Technical Files",
    "xml": "Code / Technical Files",
    "yaml": "Code / Technical Files",
    "yml": "Code / Technical Files",
    "sql": "Code / Technical Files",
    "sh": "Code / Technical Files",
    "bat": "Code / Technical Files",
    "java": "Code / Technical Files",
    "c": "Code / Technical Files",
    "cpp": "Code / Technical Files",
    "go": "Code / Technical Files",
    "rs": "Code / Technical Files",
}

# Regex patterns for high-priority semantic document classifications
INVOICE_PATTERNS = re.compile(
    r"\b(invoice|inv|bill|billing|tax_invoice|proforma|rechnung|factura|charge)\b",
    re.IGNORECASE,
)
RECEIPT_PATTERNS = re.compile(
    r"\b(receipt|quittung|recibo|rebu|payment_proof|transaction_receipt|uber_trip|order_confirm)\b",
    re.IGNORECASE,
)
RESUME_PATTERNS = re.compile(
    r"\b(resume|cv|curriculum_vitae|lebenslauf|biodata|profile_cv|job_application)\b",
    re.IGNORECASE,
)
REPORT_PATTERNS = re.compile(
    r"\b(report|quarterly|annual_report|audit|summary|analysis|findings|review_q[1-4]|whitepaper|metrics)\b",
    re.IGNORECASE,
)


def classify_by_rules(
    filename: str,
    mime_type: Optional[str] = None,
    subject: Optional[str] = None,
    email_body_excerpt: Optional[str] = None,
) -> Tuple[Optional[str], Optional[str], float]:
    """Applies deterministic pattern matching to classify an attachment.

    Returns: (category, reason, confidence)
    """
    clean_name = filename.lower()
    ext = Path(filename).suffix.lower().lstrip(".")
    subj = (subject or "").lower()

    # Normalize underscores and hyphens to spaces so word boundaries \b match properly
    normalized_name = re.sub(r"[_\-\.]+", " ", clean_name)
    normalized_subj = re.sub(r"[_\-\.]+", " ", subj)
    search_space = f"{normalized_name} {normalized_subj}"

    # 1. High-priority semantic checks for PDF / Word / Image documents
    if ext in ("pdf", "docx", "doc", "jpg", "jpeg", "png", ""):
        # Check Invoices
        if INVOICE_PATTERNS.search(search_space):
            match = INVOICE_PATTERNS.search(search_space).group(0)
            return (
                "Invoices",
                f"Matched invoice keyword '{match}' in filename/subject ({ext.upper() if ext else 'file'})",
                1.0,
            )

        # Check Receipts
        if RECEIPT_PATTERNS.search(search_space):
            match = RECEIPT_PATTERNS.search(search_space).group(0)
            return (
                "Receipts",
                f"Matched receipt keyword '{match}' in filename/subject ({ext.upper() if ext else 'file'})",
                1.0,
            )

        # Check Resumes / CVs
        if RESUME_PATTERNS.search(search_space):
            match = RESUME_PATTERNS.search(search_space).group(0)
            return (
                "Resumes / CVs",
                f"Matched resume keyword '{match}' in filename/subject ({ext.upper() if ext else 'file'})",
                1.0,
            )

        # Check Reports
        if REPORT_PATTERNS.search(search_space):
            match = REPORT_PATTERNS.search(search_space).group(0)
            return (
                "Reports",
                f"Matched report keyword '{match}' in filename/subject ({ext.upper() if ext else 'file'})",
                1.0,
            )

    # 2. PDF without specific keywords defaults to general Documents
    if ext == "pdf":
        return ("Documents", "PDF document without specific invoice/resume/report keywords", 0.95)

    # 3. Direct extension mapping
    if ext in EXTENSION_MAP:
        category = EXTENSION_MAP[ext]
        return (category, f"Standard file extension '.{ext}' mapped to {category}", 1.0)

    # 4. MIME type fallback
    if mime_type:
        m = mime_type.lower()
        if m.startswith("image/"):
            return ("Images", f"MIME type '{mime_type}' indicates image format", 0.95)
        if m.startswith("audio/"):
            return ("Audio", f"MIME type '{mime_type}' indicates audio stream", 0.95)
        if m.startswith("video/"):
            return ("Videos", f"MIME type '{mime_type}' indicates video format", 0.95)
        if "spreadsheet" in m or "excel" in m or "csv" in m:
            return ("Spreadsheets", f"MIME type '{mime_type}' indicates tabular data", 0.95)
        if "zip" in m or "compressed" in m or "tar" in m:
            return ("Archives", f"MIME type '{mime_type}' indicates compressed archive", 0.95)
        if "text/" in m:
            return ("Documents", f"Plain text MIME type '{mime_type}'", 0.90)

    # 5. Unclassified fallback
    return (
        "Other / Unclassified",
        f"Unrecognized file format or pattern for '.{ext}'",
        0.50,
    )
