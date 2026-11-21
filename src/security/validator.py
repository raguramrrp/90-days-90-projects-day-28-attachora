"""
ATTACHORA File & Archive Validator
Performs pre-processing validation, MIME type inspection, file size checks,
and safe archive inspection without arbitrary file decompression.
"""

from io import BytesIO
import mimetypes
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
import zipfile
from src.config import CONFIG


def guess_mime_and_extension(filename: str, header_bytes: Optional[bytes] = None) -> Tuple[str, str]:
    """Determines the MIME type and normalized file extension from filename and magic bytes."""
    ext = Path(filename).suffix.lower().lstrip(".")
    mime, _ = mimetypes.guess_type(filename)
    if not mime:
        mime = "application/octet-stream"

    # Magic byte hints for common formats if available
    if header_bytes:
        if header_bytes.startswith(b"%PDF"):
            return "application/pdf", ext or "pdf"
        elif header_bytes.startswith(b"\x89PNG\r\n\x1a\n"):
            return "image/png", ext or "png"
        elif header_bytes.startswith(b"\xff\xd8\xff"):
            return "image/jpeg", ext or "jpg"
        elif header_bytes.startswith(b"PK\x03\x04") or header_bytes.startswith(b"PK\x05\x06"):
            if ext in ("docx", "xlsx", "pptx", "zip"):
                return mime, ext
            return "application/zip", ext or "zip"
        elif header_bytes.startswith(b"GIF87a") or header_bytes.startswith(b"GIF89a"):
            return "image/gif", ext or "gif"

    return mime, ext


def validate_file_size(size_bytes: int) -> Tuple[bool, Optional[str]]:
    """Checks whether the file size complies with max attachment limits."""
    if size_bytes <= 0:
        return False, "File is empty (0 bytes)"
    if size_bytes > CONFIG.MAX_FILE_SIZE_BYTES:
        mb = CONFIG.MAX_FILE_SIZE_BYTES / (1024 * 1024)
        return False, f"File size exceeds maximum permitted limit ({size_bytes / (1024*1024):.2f} MB > {mb:.1f} MB)"
    return True, None


def inspect_zip_archive_safely(file_data_or_path: Any) -> Dict[str, Any]:
    """Safely inspects a ZIP archive's table of contents without extracting files to disk.

    Defends against ZIP bombs (excessive file counts, extreme compression ratios).
    """
    total_uncompressed = 0
    total_compressed = 0
    entries: List[Dict[str, Any]] = []
    is_safe = True
    warning_reason = None

    try:
        with zipfile.ZipFile(file_data_or_path, "r") as zf:
            infolist = zf.infolist()

            if len(infolist) > CONFIG.MAX_ARCHIVE_ENTRIES:
                return {
                    "is_safe": False,
                    "warning": f"Archive contains {len(infolist)} files (limit: {CONFIG.MAX_ARCHIVE_ENTRIES}). Risk of archive bomb.",
                    "entry_count": len(infolist),
                    "total_uncompressed_bytes": 0,
                    "entries": [],
                }

            for info in infolist:
                # Check for path traversal within archive entry names
                if ".." in info.filename or info.filename.startswith("/") or info.filename.startswith("\\"):
                    is_safe = False
                    warning_reason = f"Suspicious file path detected inside archive: {info.filename}"
                    break

                total_uncompressed += info.file_size
                total_compressed += info.compress_size
                entries.append(
                    {
                        "filename": info.filename,
                        "uncompressed_size": info.file_size,
                        "compressed_size": info.compress_size,
                        "is_dir": info.is_dir(),
                    }
                )

                if total_uncompressed > CONFIG.MAX_ARCHIVE_SIZE_BYTES:
                    is_safe = False
                    warning_reason = (
                        f"Uncompressed archive size exceeds limit ({total_uncompressed / (1024*1024):.1f} MB > "
                        f"{CONFIG.MAX_ARCHIVE_SIZE_BYTES / (1024*1024):.1f} MB)."
                    )
                    break

            if total_compressed > 0:
                ratio = total_uncompressed / total_compressed
                if ratio > CONFIG.MAX_DECOMPRESSION_RATIO:
                    is_safe = False
                    warning_reason = f"Anomalous compression ratio ({ratio:.1f}:1). Potential archive bomb detected."

        return {
            "is_safe": is_safe,
            "warning": warning_reason,
            "entry_count": len(entries),
            "total_uncompressed_bytes": total_uncompressed,
            "total_compressed_bytes": total_compressed,
            "entries": entries[:100],  # Return up to 100 entries for preview
        }
    except zipfile.BadZipFile:
        return {
            "is_safe": False,
            "warning": "Corrupted or invalid ZIP archive file.",
            "entry_count": 0,
            "total_uncompressed_bytes": 0,
            "entries": [],
        }
    except Exception as e:
        return {
            "is_safe": False,
            "warning": f"Unable to safely inspect archive: {str(e)}",
            "entry_count": 0,
            "total_uncompressed_bytes": 0,
            "entries": [],
        }
