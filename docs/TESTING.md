# ATTACHORA — Testing & Quality Assurance Report

## 1. Test Automation Summary

Automated tests are executed using `pytest` and mock external network connections to ensure reproducible local verification.

- **Total Test Cases:** 24
- **Passed:** 24
- **Failed:** 0
- **Execution Time:** ~3.2 seconds
- **Pass Rate:** 100%

## 2. Test Suite Breakdown

| Test File | Scope | Status |
|---|---|---|
| `tests/test_sanitizer.py` | Windows illegal chars, reserved names, trailing dots, path traversal defense | **PASS** |
| `tests/test_hasher_and_duplicates.py` | SHA-256 calculation, duplicate matching, collision detection | **PASS** |
| `tests/test_classifier.py` | Deterministic categories, explainability, ML fallback, feedback retraining | **PASS** |
| `tests/test_rules_engine.py` | Template token rendering, conflict auto-numbering, AND/OR conditions | **PASS** |
| `tests/test_database.py` | Relational tables, CRUD operations, transactions, audit logging | **PASS** |
| `tests/test_organizer_and_undo.py` | Atomic copying, directory creation, undo rollback and status restoration | **PASS** |
| `tests/test_eml_parser.py` | RFC 822 parsing, RFC 2047 header decoding, attachment extraction | **PASS** |
| `tests/test_imap_client.py` | Mocked IMAP protocol, read-only session enforcement, auth error handling | **PASS** |

## 3. End-to-End Integration Verification
The end-to-end integration test (`scripts/test_pipeline_e2e.py`) verified:
1. Ingestion of 12 distinct `.eml` sample emails.
2. Extraction and SHA-256 calculation of 12 real attachments.
3. Accurate categorization and proposed destination generation.
4. Correct detection of exact duplicate (`email_10_duplicate_aws_invoice.eml`).
5. Execution of physical file organization to `ATTACHORA_LIBRARY/`.
6. Successful single-click Undo and file restoration back to staging with audit trail update.

Command to run tests:
```powershell
.\test.bat
```
