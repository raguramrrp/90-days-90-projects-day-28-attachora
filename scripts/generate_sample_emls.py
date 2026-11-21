"""
ATTACHORA Realistic Sample .EML Generator
Creates realistic synthetic RFC 822 email files containing genuine binary and text
attachments across all standard business categories, duplicate scenarios, and conflict test cases.
"""

from email.message import EmailMessage
from email.utils import formatdate
import io
from pathlib import Path
import zipfile

SAMPLE_DIR = Path(__file__).resolve().parent.parent / "data" / "sample_emails"
SAMPLE_DIR.mkdir(parents=True, exist_ok=True)


def build_minimal_pdf(title: str, body: str) -> bytes:
    """Builds a valid, minimal PDF structure in pure Python."""
    content = f"""%PDF-1.4
1 0 obj << /Type /Catalog /Pages 2 0 R >> endobj
2 0 obj << /Type /Pages /Kids [3 0 R] /Count 1 >> endobj
3 0 obj << /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Contents 4 0 R /Resources << /Font << /F1 5 0 R >> >> >> endobj
4 0 obj << /Length 120 >> stream
BT
/F1 18 Tf
50 720 Td
({title}) Tj
/F1 12 Tf
0 -30 Td
({body}) Tj
ET
endstream endobj
5 0 obj << /Type /Font /Subtype /Type1 /BaseFont /Helvetica >> endobj
xref
0 6
0000000000 65535 f
0000000009 00000 n
0000000058 00000 n
0000000115 00000 n
0000000244 00000 n
0000000414 00000 n
trailer << /Size 6 /Root 1 0 R >>
startxref
493
%%EOF"""
    return content.encode("latin-1")


def create_sample_emails():
    # 1. AWS Cloud Invoice PDF
    aws_invoice_pdf = build_minimal_pdf("AWS Cloud Monthly Invoice", "Invoice #INV-2026-9482 | Total: $412.50 USD")
    msg1 = EmailMessage()
    msg1["From"] = "AWS Billing Department <no-reply@amazon.com>"
    msg1["To"] = "engineering-lead@startup.io"
    msg1["Subject"] = "Your Monthly AWS Cloud Invoice for November 2026 (INV-2026-9482)"
    msg1["Date"] = formatdate(localtime=True)
    msg1["Message-ID"] = "<aws-inv-2026-9482@amazon.com>"
    msg1.set_content("Please find attached your monthly cloud infrastructure invoice.")
    msg1.add_attachment(aws_invoice_pdf, maintype="application", subtype="pdf", filename="invoice_aws_nov_2026.pdf")
    (SAMPLE_DIR / "email_01_aws_invoice.eml").write_bytes(msg1.as_bytes())

    # 2. Uber Trip Receipt PDF
    uber_receipt_pdf = build_minimal_pdf("Uber Trip Receipt", "Trip on Nov 20, 2026 | Amount: $28.40 USD")
    msg2 = EmailMessage()
    msg2["From"] = "Uber Receipts <receipts@uber.com>"
    msg2["To"] = "employee@startup.io"
    msg2["Subject"] = "Your Thursday evening trip with Uber [Receipt]"
    msg2["Date"] = formatdate(localtime=True)
    msg2["Message-ID"] = "<uber-receipt-77491@uber.com>"
    msg2.set_content("Here is your receipt for your recent trip.")
    msg2.add_attachment(uber_receipt_pdf, maintype="application", subtype="pdf", filename="uber_trip_receipt_nov20.pdf")
    (SAMPLE_DIR / "email_02_uber_receipt.eml").write_bytes(msg2.as_bytes())

    # 3. AI Candidate Resume PDF
    resume_pdf = build_minimal_pdf("Curriculum Vitae: Ragu Ram P", "AI & Data Science Engineer | Python, ML, NLP, Systems")
    msg3 = EmailMessage()
    msg3["From"] = "Ragu Ram P <raguramrrp@gmail.com>"
    msg3["To"] = "careers@deepmind.com"
    msg3["Subject"] = "Application for AI Software Engineer Role - Ragu Ram P"
    msg3["Date"] = formatdate(localtime=True)
    msg3["Message-ID"] = "<ragu-job-app-2026@gmail.com>"
    msg3.set_content("Dear Hiring Team, please review my enclosed resume for the AI Engineer role.")
    msg3.add_attachment(resume_pdf, maintype="application", subtype="pdf", filename="ragu_ram_ai_engineer_resume.pdf")
    (SAMPLE_DIR / "email_03_ai_candidate_resume.eml").write_bytes(msg3.as_bytes())

    # 4. Q4 Financial Spreadsheet CSV
    csv_content = "quarter,revenue,cogs,operating_expense,ebitda\nQ1,120000,40000,35000,45000\nQ2,145000,48000,38000,59000\nQ3,180000,56000,42000,82000\nQ4,230000,69000,48000,113000\n".encode(
        "utf-8"
    )
    msg4 = EmailMessage()
    msg4["From"] = "Finance Controller <finance@company.com>"
    msg4["To"] = "leadership@company.com"
    msg4["Subject"] = "Updated Q4 Financial Projections Model"
    msg4["Date"] = formatdate(localtime=True)
    msg4["Message-ID"] = "<fin-q4-model@company.com>"
    msg4.set_content("Attached are the finalized Q4 revenue and EBITDA sheets.")
    msg4.add_attachment(csv_content, maintype="text", subtype="csv", filename="q4_financial_model_projection.csv")
    (SAMPLE_DIR / "email_04_q4_financials.eml").write_bytes(msg4.as_bytes())

    # 5. Product Launch Deck (Presentation placeholder)
    deck_content = b"PK\x03\x04\x14\x00\x06\x00Presentation_Deck_Data_2026"
    msg5 = EmailMessage()
    msg5["From"] = "Product Management <pm@company.com>"
    msg5["To"] = "all-hands@company.com"
    msg5["Subject"] = "ATTACHORA Product Launch Keynote Presentation"
    msg5["Date"] = formatdate(localtime=True)
    msg5["Message-ID"] = "<pm-deck-8831@company.com>"
    msg5.set_content("Enclosed is the keynote deck for tomorrow's demo.")
    msg5.add_attachment(deck_content, maintype="application", subtype="vnd.ms-powerpoint", filename="product_launch_roadmap.pptx")
    (SAMPLE_DIR / "email_05_investor_deck.eml").write_bytes(msg5.as_bytes())

    # 6. Cybersecurity Audit Report PDF
    audit_pdf = build_minimal_pdf("Annual Cybersecurity Audit Report", "Findings: Zero critical vulnerabilities detected.")
    msg6 = EmailMessage()
    msg6["From"] = "InfoSec Compliance <security@auditpartners.org>"
    msg6["To"] = "compliance@company.com"
    msg6["Subject"] = "Final Audit Report: Information Security & Data Governance 2026"
    msg6["Date"] = formatdate(localtime=True)
    msg6["Message-ID"] = "<audit-rep-991@auditpartners.org>"
    msg6.set_content("Please find attached the final audit review documentation.")
    msg6.add_attachment(audit_pdf, maintype="application", subtype="pdf", filename="annual_infosec_audit_report_2026.pdf")
    (SAMPLE_DIR / "email_06_cybersecurity_audit.eml").write_bytes(msg6.as_bytes())

    # 7. Code File: api_service.py
    code_content = b"""# ATTACHORA Email Ingestion Microservice
import os
import sqlite3

def init_service():
    print("Email processing daemon active")
"""
    msg7 = EmailMessage()
    msg7["From"] = "DevOps Lead <devops@cloudtech.io>"
    msg7["To"] = "backend-team@cloudtech.io"
    msg7["Subject"] = "Patch for Attachment Webhook Handler"
    msg7["Date"] = formatdate(localtime=True)
    msg7["Message-ID"] = "<code-patch-124@cloudtech.io>"
    msg7.set_content("Here is the updated ingestion script.")
    msg7.add_attachment(code_content, maintype="text", subtype="x-python", filename="api_service.py")
    (SAMPLE_DIR / "email_07_api_backend.eml").write_bytes(msg7.as_bytes())

    # 8. Architecture Diagram Image (PNG)
    # Minimal 1x1 valid PNG
    png_bytes = (
        b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15c4\x00\x00\x00\rIDATx\x9cc`"
        b"\x00\x00\x00\x02\x00\x01H\xaf\xa4q\x00\x00\x00\x00IEND\xaeB`\x82"
    )
    msg8 = EmailMessage()
    msg8["From"] = "System Architect <arch@cloudtech.io>"
    msg8["To"] = "engineering@cloudtech.io"
    msg8["Subject"] = "System Architecture Schematic v2"
    msg8["Date"] = formatdate(localtime=True)
    msg8["Message-ID"] = "<arch-diagram-345@cloudtech.io>"
    msg8.set_content("Attached diagram depicts the proposed modular boundary.")
    msg8.add_attachment(png_bytes, maintype="image", subtype="png", filename="system_architecture_diagram.png")
    (SAMPLE_DIR / "email_08_architecture_diagram.eml").write_bytes(msg8.as_bytes())

    # 9. Safe ZIP Archive
    zip_buf = io.BytesIO()
    with zipfile.ZipFile(zip_buf, "w") as zf:
        zf.writestr("dataset_notes.txt", "Sample dataset descriptors and feature dictionaries.")
        zf.writestr("schema_definition.json", '{"version": 1, "fields": ["id", "val"]}')
    zip_bytes = zip_buf.getvalue()

    msg9 = EmailMessage()
    msg9["From"] = "Research Labs <research@datafoundry.org>"
    msg9["To"] = "analytics@company.com"
    msg9["Subject"] = "Bundle: Benchmark Dataset Metadata"
    msg9["Date"] = formatdate(localtime=True)
    msg9["Message-ID"] = "<bundle-zip-119@datafoundry.org>"
    msg9.set_content("Attached archive contains dataset specifications.")
    msg9.add_attachment(zip_bytes, maintype="application", subtype="zip", filename="dataset_bundle_2026.zip")
    (SAMPLE_DIR / "email_09_dataset_archive.eml").write_bytes(msg9.as_bytes())

    # 10. EXACT DUPLICATE TEST CASE: Same AWS invoice PDF sent by accounting follow-up
    msg10 = EmailMessage()
    msg10["From"] = "Accounting Follow-up <ap-inquiries@amazon.com>"
    msg10["To"] = "finance@startup.io"
    msg10["Subject"] = "FWD: Past Due Notice for Invoice INV-2026-9482"
    msg10["Date"] = formatdate(localtime=True)
    msg10["Message-ID"] = "<aws-inv-followup-9921@amazon.com>"
    msg10.set_content("Forwarding another copy of your invoice INV-2026-9482.")
    msg10.add_attachment(aws_invoice_pdf, maintype="application", subtype="pdf", filename="invoice_aws_nov_2026_copy.pdf")
    (SAMPLE_DIR / "email_10_duplicate_aws_invoice.eml").write_bytes(msg10.as_bytes())

    # 11. FILENAME CONFLICT TEST CASE: Different content, but named 'receipt.pdf'
    different_receipt_pdf = build_minimal_pdf("Hardware Store Receipt", "Purchase: Ethernet Cables & Server Racks | Total: $184.20")
    msg11 = EmailMessage()
    msg11["From"] = "Hardware Supplier <sales@techhardware.com>"
    msg11["To"] = "procurement@startup.io"
    msg11["Subject"] = "Your Order Receipt #99312"
    msg11["Date"] = formatdate(localtime=True)
    msg11["Message-ID"] = "<hardware-rcpt-882@techhardware.com>"
    msg11.set_content("Receipt for server supplies.")
    # Notice this is named generic 'receipt.pdf'
    msg11.add_attachment(different_receipt_pdf, maintype="application", subtype="pdf", filename="receipt.pdf")
    (SAMPLE_DIR / "email_11_filename_conflict_receipt.eml").write_bytes(msg11.as_bytes())

    # 12. Generic Meeting Notes
    msg12 = EmailMessage()
    msg12["From"] = "Scrum Master <scrum@agileteam.org>"
    msg12["To"] = "sprint-team@agileteam.org"
    msg12["Subject"] = "Sprint 28 Retrospective Action Items"
    msg12["Date"] = formatdate(localtime=True)
    msg12["Message-ID"] = "<scrum-notes-3829@agileteam.org>"
    msg12.set_content("Notes attached.")
    msg12.add_attachment(b"Sprint 28 Retrospective Summary\n1. Excellent velocity\n2. Automate attachment handling with ATTACHORA", maintype="text", subtype="plain", filename="sprint_28_notes.txt")
    (SAMPLE_DIR / "email_12_generic_notes.eml").write_bytes(msg12.as_bytes())

    print(f"Successfully generated 12 sample .EML files in {SAMPLE_DIR}")


if __name__ == "__main__":
    create_sample_emails()
