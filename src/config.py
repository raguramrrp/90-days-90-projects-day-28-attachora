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

    # UI Theme Palette (Matching Reference Image)
    COLOR_BG: str = "#F4F6F4"
    COLOR_NAV: str = "#FFFFFF"
    COLOR_SURFACE: str = "#FFFFFF"
    COLOR_TEXT_PRIMARY: str = "#202824"
    COLOR_TEXT_SECONDARY: str = "#66716B"
    COLOR_TEXT_MUTED: str = "#8A948E"
    COLOR_ACCENT: str = "#286B50"
    COLOR_ACCENT_HOVER: str = "#20553F"
    COLOR_SOFT_GREEN: str = "#E9F2EC"
    COLOR_BORDER: str = "#DCE3DE"
    COLOR_TABLE_HEADER: str = "#F7F9F7"
    COLOR_ROW_HOVER: str = "#F1F6F2"
    COLOR_SUCCESS: str = "#278253"
    COLOR_WARNING: str = "#B77925"
    COLOR_ERROR: str = "#BD4545"
    COLOR_NEUTRAL: str = "#64716A"

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
