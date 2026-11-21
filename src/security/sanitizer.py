"""
ATTACHORA Path & Filename Sanitizer
Prevents path traversal attacks and sanitizes filenames for Windows filesystem compliance.
"""

import os
from pathlib import Path
import re
from typing import Tuple

# Windows reserved device names
RESERVED_NAMES = {
    "CON",
    "PRN",
    "AUX",
    "NUL",
    "COM1",
    "COM2",
    "COM3",
    "COM4",
    "COM5",
    "COM6",
    "COM7",
    "COM8",
    "COM9",
    "LPT1",
    "LPT2",
    "LPT3",
    "LPT4",
    "LPT5",
    "LPT6",
    "LPT7",
    "LPT8",
    "LPT9",
}

# Invalid characters in Windows file/folder names: < > : " / \ | ? * and control chars 0-31
INVALID_CHARS_REGEX = re.compile(r'[<>:"/\\|?*\x00-\x1f]')


def sanitize_filename(filename: str, fallback_prefix: str = "attachment") -> str:
    """Sanitizes a filename to ensure safe storage on Windows and cross-platform filesystems."""
    if not filename or not isinstance(filename, str):
        return f"{fallback_prefix}.dat"

    # Normalize backslashes and strip path elements
    name = Path(filename).name.strip()

    # Replace invalid characters with underscore
    name = INVALID_CHARS_REGEX.sub("_", name)

    # Collapse multiple consecutive underscores or spaces
    name = re.sub(r"[_\s]+", "_", name)

    # Strip trailing spaces and dots which Windows does not permit
    name = name.rstrip(". ")

    if not name:
        name = f"{fallback_prefix}.dat"

    # Split stem and extension
    stem, ext = os.path.splitext(name)

    # Check for Windows reserved names (e.g. CON.pdf, NUL.txt)
    if stem.upper() in RESERVED_NAMES:
        stem = f"{stem}_file"
    name = f"{stem}{ext}"

    # Enforce safe length constraints (max 220 chars to leave buffer for paths)
    if len(name) > 220:
        ext_len = len(ext)
        stem = stem[: 220 - ext_len]
        name = f"{stem}{ext}"

    return name


def sanitize_relative_path(path_str: str) -> str:
    """Sanitizes a relative subfolder path (e.g. 'Finance/Invoices/2026').

    Strips directory traversal sequences ('..') and invalid characters.
    """
    if not path_str:
        return "Unclassified"

    parts = []
    # Normalize separators
    normalized = path_str.replace("\\", "/")
    for raw_part in normalized.split("/"):
        part = raw_part.strip()
        if not part or part == ".":
            continue
        if part == "..":
            # Path traversal attempt: drop or sanitize
            continue
        sanitized_part = sanitize_filename(part, fallback_prefix="folder")
        parts.append(sanitized_part)

    return "/".join(parts) if parts else "Unclassified"


def resolve_safe_destination(storage_root: Path, relative_dir: str, filename: str) -> Tuple[Path, str]:
    """Resolves a destination path ensuring it strictly resides within storage_root.

    Raises ValueError if path traversal is detected.
    """
    if os.path.isabs(relative_dir) or (len(relative_dir) > 1 and relative_dir[1] == ":") or relative_dir.startswith("/") or relative_dir.startswith("\\"):
        raise ValueError(f"Path traversal detected: destination escapes storage root ({relative_dir})")

    root_resolved = storage_root.resolve()
    clean_subfolder = sanitize_relative_path(relative_dir)
    clean_filename = sanitize_filename(filename)

    target_dir = (root_resolved / clean_subfolder).resolve()

    # Security check: target_dir must be relative to root_resolved
    try:
        target_dir.relative_to(root_resolved)
    except ValueError:
        raise ValueError(f"Path traversal detected: destination escapes storage root ({relative_dir})")

    target_file = target_dir / clean_filename
    try:
        target_file.relative_to(root_resolved)
    except ValueError:
        raise ValueError(f"Path traversal detected: file destination escapes storage root ({filename})")

    return target_file, clean_filename
