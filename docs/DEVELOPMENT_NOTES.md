# ATTACHORA — Development Notes & Engineering Decisions

## 1. Key Engineering Decisions

### Why Deterministic Rules First?
In production document management systems, users require 100% explainable file routing. Showing "Matched invoice keyword 'invoice' in filename/subject" gives users total confidence that their files are being routed intentionally. Fake ML probabilities (e.g. inventing 99.4% on an `.xlsx` file) degrade user trust.

### Why Local Scikit-learn Fallback?
When filenames lack obvious keywords, an on-device TF-IDF Naive Bayes model provides useful category suggestions without sending sensitive user data to external cloud APIs or requiring expensive LLM tokens. Furthermore, user corrections are stored in `classification_feedback` and can retrain the model locally with one click.

### Windows Filesystem Hardening
Windows imposes specific filesystem rules that can crash generic file organizers:
- **Reserved Device Names:** Filenames like `CON.pdf`, `PRN.csv`, or `NUL.txt` crash Windows shell APIs. ATTACHORA detects and sanitizes these into `CON_file.pdf`.
- **Trailing Dots and Spaces:** Windows strips trailing periods and spaces, which can lead to unexpected collision errors. ATTACHORA normalizes these upfront.
- **Path Traversal Defense:** ATTACHORA strictly checks `is_relative_to(storage_root)` and rejects any attempt to inject `..` sequences or absolute paths.

### Collision Resolution Strategy
Rather than silently overwriting files or throwing unhandled exceptions, ATTACHORA implements sequential non-destructive auto-numbering (`_001.pdf`, `_002.pdf`) up to `_999.pdf` before employing UUID fallbacks.

## 2. Trade-offs & Assumptions
- **SQLite Database:** Chosen for self-contained, zero-configuration local installation without external database services. WAL (Write-Ahead Logging) mode is enabled for responsive concurrent reads.
- **Read-Only IMAP Mode:** To ensure user data safety, the IMAP client strictly calls `select(mailbox, readonly=True)`. This guarantees that ATTACHORA never marks, modifies, deletes, or sends emails.
