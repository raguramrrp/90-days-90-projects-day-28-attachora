"""
ATTACHORA Configuration Module
Handles environment variables, default directory paths, security constraints,
and system-wide constants.
"""

from dataclasses import dataclass
import os
from pathlib import Path


@dataclass(frozen=True)
class AppConfig:
    # Base application paths
    BASE_DIR: Path = Path(__file__).resolve().parent.parent
    STORAGE_ROOT: Path = Path(os.getenv("ATTACHORA_STORAGE_ROOT", str(BASE_DIR / "ATTACHORA_LIBRARY")))
    STAGING_DIR: Path = Path(os.getenv("ATTACHORA_STAGING_DIR", str(BASE_DIR / ".attachora_staging")))
    DB_PATH: Path = Path(os.getenv("ATTACHORA_DB_PATH", str(BASE_DIR / "attachora.db")))
    VAULT_KEY_PATH: Path = Path(os.getenv("ATTACHORA_VAULT_KEY_PATH", str(BASE_DIR / ".vault.key")))
    SAMPLE_EMAILS_DIR: Path = BASE_DIR / "data" / "sample_emails"

    # Security Limits
    MAX_FILE_SIZE_BYTES: int = int(os.getenv("ATTACHORA_MAX_FILE_SIZE_MB", "25")) * 1024 * 1024
    MAX_ARCHIVE_SIZE_BYTES: int = int(os.getenv("ATTACHORA_MAX_ARCHIVE_SIZE_MB", "100")) * 1024 * 1024
    MAX_ARCHIVE_ENTRIES: int = int(os.getenv("ATTACHORA_MAX_ARCHIVE_ENTRIES", "500"))
    MAX_DECOMPRESSION_RATIO: float = 100.0  # Archive bomb defense

    # Operational settings
    AUTO_MODE: bool = os.getenv("ATTACHORA_AUTO_MODE", "False").lower() in ("true", "1", "yes")
    AUTO_CONFIDENCE_THRESHOLD: float = float(os.getenv("ATTACHORA_AUTO_CONFIDENCE_THRESHOLD", "0.90"))

    # UI Theme Palette (Specified in system guidelines)
    COLOR_BG: str = "#F4F5F4"
    COLOR_NAV: str = "#F8F9F8"
    COLOR_SURFACE: str = "#FFFFFF"
    COLOR_TEXT_PRIMARY: str = "#252B29"
    COLOR_TEXT_SECONDARY: str = "#737C78"
    COLOR_ACCENT: str = "#356B59"
    COLOR_NAV_ACTIVE: str = "#E7EFEB"
    COLOR_BORDER: str = "#E1E5E2"
    COLOR_ROW_HOVER: str = "#F1F4F2"
    COLOR_SUCCESS: str = "#32815A"
    COLOR_WARNING: str = "#B78032"
    COLOR_ERROR: str = "#BC4B4B"

    # Supported Categories
    CATEGORIES = (
        "Invoices",
        "Receipts",
        "Resumes / CVs",
        "Reports",
        "Spreadsheets",
        "Presentations",
        "Documents",
        "Images",
        "Audio",
        "Videos",
        "Archives",
        "Code / Technical Files",
        "Other / Unclassified",
    )


# Active runtime configuration instance
CONFIG = AppConfig()
CONFIG.STORAGE_ROOT.mkdir(parents=True, exist_ok=True)
CONFIG.STAGING_DIR.mkdir(parents=True, exist_ok=True)
