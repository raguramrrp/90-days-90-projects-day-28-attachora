# ATTACHORA — Intelligent Email Attachment Classification & Filing System

> **"Every attachment, automatically in its place."**

ATTACHORA is a desktop-oriented email attachment organization workstation built with Python, Streamlit, and SQLite. It automatically detects email attachments, classifies document types, calculates cryptographic SHA-256 hashes to eliminate duplicates, evaluates custom prioritized filing rules, organizes files into structured folders, and maintains an immutable audit log with full rollback capabilities.

---

## 1. Problem Statement & Motivation
In modern corporate environments, professionals receive dozens of critical attachments every day across scattered email threads. Manually identifying, renaming, categorizing, and sorting these files into local folder structures is tedious, inconsistent, and error-prone. Typical challenges include:
- **Duplicate Document Bloat:** Identical PDFs and spreadsheets downloaded repeatedly waste disk space and create confusion.
- **Vague Naming Conventions:** Files named `Scan_001.pdf` or `Invoice_v2.pdf` lack context regarding who sent them or when they arrived.
- **Security Risks:** Malicious email attachments (ZIP bombs, path traversal sequences) can compromise local systems.
- **Lack of Operational History:** Automated scripts often move files without an audit trail, making accidental misplacements impossible to track or undo.

ATTACHORA solves these challenges by combining explainable rule-based routing, cryptographic deduplication, in-app file previews, and a table-first approval workspace.

---

## 2. Objectives & Intended Users
- **Primary Objective:** Build a reliable, privacy-preserving, local-first attachment management system that operates without paid cloud APIs or complex infrastructure.
- **Intended Users:**
  - **Accountants & Finance Teams:** Automatically route invoices, vendor bills, and tax receipts into structured expense folders.
  - **HR & Recruitment Specialists:** File incoming resumes and CVs into categorized candidate pipelines.
  - **Engineers & Researchers:** Organize datasets, technical documentation, code snippets, and benchmark archives.
  - **Knowledge Workers:** Clean up chaotic downloads and email clutter automatically.

---

## 3. Key Features

- **Read-Only IMAP & Offline EML Ingestion:** Connect to Gmail, Outlook, Yahoo, or private IMAP servers over TLS with strict read-only guarantees (emails are never deleted or modified). Also includes an offline `.eml` parser for local message archives.
- **12-Category Explainable Classification:** Categorizes attachments into *Invoices, Receipts, Resumes / CVs, Reports, Spreadsheets, Presentations, Documents, Images, Audio, Videos, Archives,* and *Code / Technical Files*.
- **Local Machine Learning Fallback:** Incorporates a lightweight on-device TF-IDF Naive Bayes model that assists with ambiguous filenames and retrains from user feedback.
- **SHA-256 Deduplication & Collision Defense:** Flags exact duplicates, existing filename conflicts, and similar names before file operations occur.
- **Smart Filing Rules & Template Engine:** Prioritized rules supporting AND/OR logic conditions and naming templates (`{date}_{category}_{original_filename}`).
- **Two Operating Modes:**
  - *Review Mode:* Full operator oversight with batch approvals and manual category overrides.
  - *Automatic Mode:* Hands-free autonomous filing for high-confidence matches.
- **In-App Previews & Archive Bomb Defense:** Preview PDFs, images, spreadsheets, and code directly in the workstation. Inspects ZIP archives safely without extracting files to disk.
- **Atomic Undo & Rollback:** Reverse any organized file move with a single click, restoring files to staging while recording the event in the audit log.
- **Database-Backed Analytics:** Real calculated operational metrics (total volume, storage organized, storage saved through deduplication).

---

## 4. Workstation Visuals & Screenshots

```
+-----------------------------------------------------------------------------------------------+
| ATTACHORA  / Workspace                      Storage: [ATTACHORA_LIBRARY]  ● Connected (Local) |
+-----------------------------------------------------------------------------------------------+
| [Search attachments, senders, filenames, subjects, categories, or SHA-256...        ] [Clear]  |
| Category: [All v]  Status: [All v]  File Type: [All v]  Sender: [Filter by email...          ] |
+-----------------------------------------------------------------------------------------------+
| [Select All] [Deselect All] [Approve Selected (4)] [Skip Selected]      Mode: [Automatic (Off)]|
+-------------------------------------------------------------+---------------------------------+
| Queue Volume: 12 attachments                                | ATTACHMENT INSPECTOR & PREVIEW  |
|                                                             |                                 |
| [X] invoice_aws_nov_2026.pdf (1.2 KB)            [PENDING]  | invoice_aws_nov_2026.pdf        |
|     Sender: no-reply@amazon.com                             | Category: Invoices | Size: 1.2KB|
|     Proposed: Finance/Invoices/20261121_Invoices_inv.pdf    | Reason: Matched 'invoice' kw    |
|     [Select] [Inspect & Edit] [Approve]                     | SHA: d83e4661e9e4e016...        |
|                                                             | +-----------------------------+ |
| [ ] uber_trip_receipt_nov20.pdf (1.1 KB)         [PENDING]  | | [Rendered PDF Preview Image]| |
|     Sender: receipts@uber.com                               | | Page 1 of 1                 | |
|     Proposed: Finance/Receipts/20261121_receipt.pdf         | +-----------------------------+ |
|     [Select] [Inspect & Edit] [Approve]                     |                                 |
|                                                             | [Modify Destination / Category] |
| [ ] invoice_aws_nov_2026_copy.pdf (1.2 KB)      [DUPLICATE]| [Duplicate Handling Strategy v] |
|     Sender: ap-inquiries@amazon.com                         |                                 |
+-------------------------------------------------------------+---------------------------------+
```

*Note: Screenshots can be captured by running the application locally via `run.bat` and saving interface views to `screenshots/workspace.png` and `screenshots/analytics.png`.*

---

## 5. Architecture & Technology Stack

### Technology Stack
- **Runtime:** Python 3.11 / 3.12
- **User Interface:** Streamlit (Custom Enterprise Station CSS)
- **Database:** SQLite 3 (WAL mode, Foreign Key constraints)
- **Email Protocol:** `imaplib` (TLS SSL), `email` (RFC 822 / MIME parser)
- **Machine Learning:** `scikit-learn` (TF-IDF Vectorizer + Multinomial Naive Bayes)
- **File & PDF Processing:** `pymupdf` (PyMuPDF), `pillow`, `pandas`, `openpyxl`
- **Security & Integrity:** `hashlib` (SHA-256), `hmac`, `secrets`, `pathlib`
- **Testing:** `pytest` (24 automated test cases)

---

## 6. Project Directory Structure

```
90-days-90-projects-day-28-attachora/
├── .env.example              # Environment configuration defaults
├── .gitignore                # Production git ignore definitions
├── app.py                    # Main Streamlit workstation entrypoint
├── DEMO_SCRIPT.md            # 90-second portfolio demonstration guide
├── QUICKSTART.md             # Fast setup commands for developers
├── README.md                 # Complete system documentation
├── requirements.txt          # Python dependency manifest
├── setup.bat                 # Windows automated environment setup
├── run.bat                   # Windows one-click workstation launch
├── test.bat                  # Windows automated test execution
├── reset_demo_data.bat       # Demo database and library reset script
├── data/
│   ├── README.md             # Dataset documentation
│   └── sample_emails/        # 12 pre-generated RFC 822 .eml test emails
├── docs/
│   ├── PROJECT_OVERVIEW.md   # Problem statement, scope, and objectives
│   ├── ARCHITECTURE.md       # Architectural diagram and component design
│   ├── USER_GUIDE.md         # Step-by-step user instructions
│   ├── DEVELOPMENT_NOTES.md  # Engineering trade-offs and decisions
│   ├── TESTING.md            # Test cases, commands, and results
│   └── TROUBLESHOOTING.md    # Common errors and resolutions
├── scripts/
│   ├── generate_sample_emls.py # Generator for realistic synthetic .eml files
│   └── test_pipeline_e2e.py    # End-to-end integration test runner
├── src/
│   ├── config.py             # System paths, color tokens, and safety limits
│   ├── analytics/
│   │   └── reporter.py       # Operational KPI aggregator and CSV export
│   ├── classifier/
│   │   ├── engine.py         # Unified classification engine
│   │   ├── ml_classifier.py  # Local retrainable TF-IDF Naive Bayes model
│   │   └── rules_classifier.py # Deterministic pattern matching rules
│   ├── database/
│   │   ├── db_manager.py     # SQLite thread-safe connection and CRUD
│   │   └── schema.py         # Relational schema DDL and default rules
│   ├── email_engine/
│   │   ├── eml_parser.py     # RFC 822 and MIME attachment decoder
│   │   ├── imap_client.py    # TLS IMAP client with read-only enforcement
│   │   └── reader.py         # Ingestion pipeline and staging coordinator
│   ├── rules_engine/
│   │   ├── rule_evaluator.py # Priority evaluator for AND/OR condition groups
│   │   └── template_engine.py# Filename template renderer and conflict resolver
│   ├── security/
│   │   ├── credential_vault.py # Encrypted machine vault for passwords
│   │   ├── hasher.py         # Cryptographic SHA-256 calculator
│   │   ├── sanitizer.py      # Path traversal and Windows filename sanitizer
│   │   └── validator.py      # File size and archive bomb protector
│   └── storage_manager/
│       ├── duplicate_detector.py # Cryptographic hash deduplication
│       ├── organizer.py      # Atomic file copy and library organizer
│       └── undo_manager.py   # Reversible file moves and rollback manager
├── tests/
│   ├── conftest.py           # Pytest path configuration
│   ├── test_classifier.py    # Unit tests for classification engines
│   ├── test_database.py      # Unit tests for database CRUD and schema
│   ├── test_eml_parser.py    # Unit tests for MIME parsing and decoding
│   ├── test_hasher_and_duplicates.py # Tests for SHA-256 and collisions
│   ├── test_imap_client.py   # Mocked tests for IMAP read-only sessions
│   ├── test_organizer_and_undo.py    # Tests for file moves and rollback
│   ├── test_rules_engine.py  # Tests for templates and condition logic
│   └── test_sanitizer.py     # Tests for Windows legal names and traversal
└── ui/
    ├── theme.py              # Enterprise CSS tokens and status badges
    ├── components/
    │   ├── header.py         # Top branding and status header
    │   ├── nav_rail.py       # Compact vertical navigation rail
    │   ├── preview_panel.py  # Safe in-app PDF, image, and code previewer
    │   └── search_toolbar.py # Search field and dropdown filter toolbar
    └── pages/
        ├── analytics_page.py # Operational charts and KPI summary
        ├── connections_page.py # IMAP account manager and EML importer
        ├── history_page.py   # Complete audit trail and CSV download
        ├── organized_page.py # Library explorer and single-click Undo
        ├── rules_page.py     # Smart filing rule builder and simulator
        ├── settings_page.py  # Storage roots and safety threshold controls
        └── workspace_page.py # Primary operations queue and approval table
```

---

## 7. Prerequisites
- **Operating System:** Windows 10 / Windows 11 (or Linux / macOS)
- **Python Version:** Python 3.11 or Python 3.12 (Tested on Python 3.12.6)
- **No external paid API keys or cloud services required.**

---

## 8. Step-by-Step Windows Installation

### Option A: Automatic Setup
Run `setup.bat` from File Explorer or PowerShell:
```powershell
.\setup.bat
```

### Option B: Manual Setup
```powershell
# 1. Create project virtual environment
python -m venv --system-site-packages .venv

# 2. Activate virtual environment
.\.venv\Scripts\Activate.ps1

# 3. Install dependencies
pip install -r requirements.txt

# 4. Generate test email dataset
python scripts\generate_sample_emls.py

# 5. Initialize SQLite database
python -c "from src.database.db_manager import DB; print('Initialized.')"
```

---

## 9. Quick Start Commands

- **Launch Application:**
  ```powershell
  .\run.bat
  ```
- **Execute Automated Tests:**
  ```powershell
  .\test.bat
  ```
- **Run End-to-End Integration Verification:**
  ```powershell
  .\.venv\Scripts\python.exe scripts\test_pipeline_e2e.py
  ```

---

## 10. Environment Variables (`.env.example`)

| Variable | Default Value | Description |
|---|---|---|
| `ATTACHORA_STORAGE_ROOT` | `./ATTACHORA_LIBRARY` | Destination directory for organized attachments |
| `ATTACHORA_DB_PATH` | `./attachora.db` | Local SQLite database file location |
| `ATTACHORA_MAX_FILE_SIZE_MB` | `25` | Maximum allowed attachment size in megabytes |
| `ATTACHORA_MAX_ARCHIVE_SIZE_MB` | `100` | Maximum uncompressed archive size limit |
| `ATTACHORA_MAX_ARCHIVE_ENTRIES` | `500` | Maximum files allowed inside a ZIP archive |
| `ATTACHORA_AUTO_MODE` | `False` | Enables autonomous filing without manual approval |
| `ATTACHORA_AUTO_CONFIDENCE_THRESHOLD` | `0.90` | Minimum confidence required for auto-filing |

---

## 11. Example Usage & Workflow

1. **Import Test Emails:** In **Connections** -> **EML File Importer**, click **Import All 12 Sample Test Emails**.
2. **Review in Workspace:**
   - `invoice_aws_nov_2026.pdf` -> Categorized as **Invoices** -> Proposed: `Finance/Invoices/20261121_Invoices_invoice_aws_nov_2026.pdf`.
   - `uber_trip_receipt_nov20.pdf` -> Categorized as **Receipts** -> Proposed: `Finance/Receipts/20261121_uber_trip_receipt_nov20.pdf`.
   - `invoice_aws_nov_2026_copy.pdf` -> Flagged as **Exact Duplicate** (SHA-256 match).
3. **Approve Operations:** Select rows and click **Approve Selected**. Files are safely organized into `ATTACHORA_LIBRARY/`.
4. **Inspect & Rollback:** Go to **Organized Files** -> click **Undo / Restore** on any item to revert the move.
5. **Audit Trail:** Check **History & Audit** to review the immutable operation record or export to CSV.

---

## 12. Testing & Quality Assurance Status

All tests run locally without external network dependencies:
- **Test Command:** `python -m pytest tests -v`
- **Result:** **24 passed in 3.23s (100% PASS)**
- **Test Coverage:**
  - Filename sanitization, reserved Windows devices, and path traversal prevention.
  - SHA-256 calculation, duplicate detection, and filename conflict handling.
  - Deterministic classification for all 12 business categories and ML retraining.
  - Filing rules evaluation with AND/OR logic and dynamic filename templates.
  - SQLite schema creation, foreign key constraints, and CRUD transactions.
  - Atomic file organization, conflict auto-numbering, and single-click Undo.
  - RFC 822 MIME parsing, RFC 2047 header decoding, and attachment extraction.
  - IMAP protocol handling and strict read-only session enforcement.

---

## 13. Known Limitations
- **IMAP Read-Only Limitation:** By design, ATTACHORA never deletes emails from your mailbox. To remove emails after filing, use your email client directly.
- **Large Archive Extraction:** Files inside ZIP archives are inspected for safety but are not extracted automatically into the library.
- **App Password Requirement:** Modern email providers (Gmail, Microsoft) require generating an App Password rather than using standard account passwords.

---

## 14. Security & Privacy Considerations
- **Untrusted Input Defense:** Email attachments are treated as untrusted inputs. Files are staged in an isolated staging folder before user approval.
- **Archive Bomb Protection:** Checks ZIP decompression ratios, uncompressed byte sizes, and file counts before inspection.
- **Zero Plaintext Credentials:** Passwords are encrypted using machine-derived keys or stored only in volatile memory during active sessions.
- **No Remote Telemetry:** No user data, filenames, or email contents leave your local workstation.

---

## 15. Learning Outcomes & Resume Keywords
- **Core Competencies:** Enterprise Software Architecture, Local Automation, Cryptographic Deduplication, MIME Email Engineering, Document Management.
- **Technical Skills:** Python 3.12, Streamlit, SQLite 3, Scikit-learn (TF-IDF, Naive Bayes), IMAP4, Cryptography, PyMuPDF, Pytest, Windows Shell Engineering.
- **Keywords:** Autonomous Agent, Email Ingestion Pipeline, Deterministic Classifier, SHA-256 Deduplication, Path Traversal Defense, Enterprise Workstation.

---

## 16. License & Attribution
Developed as part of the **90 Days – 90 Projects Challenge** by Ragu Ram P (Final-Year B.Tech AI & Data Science). Permissive open license for educational and portfolio demonstration.
