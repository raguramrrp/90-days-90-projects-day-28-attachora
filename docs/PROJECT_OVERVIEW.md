# ATTACHORA — Project Overview

## 1. Executive Summary
**ATTACHORA** (Intelligent Email Attachment Classification & Filing System) is an autonomous, desktop-oriented workstation designed to detect, classify, deduplicate, and organize incoming email attachments into clean, structured folder hierarchies.

The core tagline: *"Every attachment, automatically in its place."*

## 2. Problem Statement
Knowledge workers and enterprise departments spend hours every week downloading email attachments from disparate threads, manually deciphering unhelpful filenames (e.g., `inv_final_v2(1).pdf`), renaming documents, and moving them into appropriate project folders. Common issues include:
- Severe storage bloat from identical attachments received across multiple email threads.
- Accidental file overwrites caused by filename collisions.
- Vulnerability to malicious payloads (ZIP bombs, path traversal sequences).
- Lack of an audit log or rollback mechanism when an automated script files documents into wrong locations.

## 3. Solution & Scope
ATTACHORA provides an enterprise file operations workstation with:
- **Strict Read-Only Email Ingestion:** TLS-protected IMAP client that never deletes, alters, or sends emails, combined with an offline `.eml` archive importer.
- **Explainable Classification:** Deterministic rule engine parsing MIME types, extensions, and keyword patterns across 12 standard business categories, backed by a lightweight local TF-IDF Naive Bayes classifier for ambiguous tokens.
- **Cryptographic Deduplication:** SHA-256 fingerprinting that differentiates exact duplicates, existing filename conflicts, and similar names.
- **Smart Rule & Template Engine:** Prioritized filing rules supporting AND/OR condition logic and customizable naming templates (`{date}_{category}_{original_filename}`).
- **Two Operating Modes:** Review Mode (manual operator approval) and Automatic Mode (autonomous filing for high-confidence matches).
- **Safe Recovery:** Atomic operations with single-click Undo and complete audit history.
