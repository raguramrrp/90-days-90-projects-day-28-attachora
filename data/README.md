# ATTACHORA Sample Dataset & Test Corpus

This directory contains realistic synthetic RFC 822 email files (`.eml`) generated to demonstrate and validate the complete ATTACHORA attachment processing pipeline without requiring live third-party mailbox credentials.

## Sample Email Inventory

| File | Sender | Subject | Attachment | True Category | Special Scenario |
|---|---|---|---|---|---|
| `email_01_aws_invoice.eml` | AWS Billing `<no-reply@amazon.com>` | Your Monthly AWS Cloud Invoice | `invoice_aws_nov_2026.pdf` | Invoices | Standard business invoice |
| `email_02_uber_receipt.eml` | Uber Receipts `<receipts@uber.com>` | Your Thursday evening trip with Uber | `uber_trip_receipt_nov20.pdf` | Receipts | Expense voucher |
| `email_03_ai_candidate_resume.eml` | Ragu Ram P `<raguramrrp@gmail.com>` | Application for AI Software Engineer Role | `ragu_ram_ai_engineer_resume.pdf` | Resumes / CVs | HR recruitment candidate CV |
| `email_04_q4_financials.eml` | Finance Controller `<finance@company.com>` | Updated Q4 Financial Projections Model | `q4_financial_model_projection.csv` | Spreadsheets | Tabular financial dataset |
| `email_05_investor_deck.eml` | Product Management `<pm@company.com>` | ATTACHORA Product Launch Keynote | `product_launch_roadmap.pptx` | Presentations | Keynote slide deck |
| `email_06_cybersecurity_audit.eml` | InfoSec Compliance `<security@auditpartners.org>` | Final Audit Report: InfoSec 2026 | `annual_infosec_audit_report_2026.pdf` | Reports | Formal compliance report |
| `email_07_api_backend.eml` | DevOps Lead `<devops@cloudtech.io>` | Patch for Attachment Webhook Handler | `api_service.py` | Code / Technical Files | Python source code |
| `email_08_architecture_diagram.eml` | System Architect `<arch@cloudtech.io>` | System Architecture Schematic v2 | `system_architecture_diagram.png` | Images | High-resolution bitmap diagram |
| `email_09_dataset_archive.eml` | Research Labs `<research@datafoundry.org>` | Bundle: Benchmark Dataset Metadata | `dataset_bundle_2026.zip` | Archives | Safe compressed ZIP bundle |
| `email_10_duplicate_aws_invoice.eml` | Accounting Follow-up `<ap-inquiries@amazon.com>` | FWD: Past Due Notice for Invoice | `invoice_aws_nov_2026_copy.pdf` | Invoices | **Exact Duplicate Test** (identical SHA-256 to `email_01`) |
| `email_11_filename_conflict_receipt.eml` | Hardware Supplier `<sales@techhardware.com>` | Your Order Receipt #99312 | `receipt.pdf` | Receipts | **Filename Conflict Test** (different content, triggers `_001.pdf`) |
| `email_12_generic_notes.eml` | Scrum Master `<scrum@agileteam.org>` | Sprint 28 Retrospective Action Items | `sprint_28_notes.txt` | Documents | Unformatted plain text document |

## Data Generation
All sample `.eml` files can be deterministically regenerated at any time using:
```powershell
python scripts/generate_sample_emls.py
```
All files are synthetically generated and contain zero personal, proprietary, or private data.
