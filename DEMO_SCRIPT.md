# ATTACHORA — 90-Second Demonstration Script

Follow this sequence to showcase the entire automated workflow of ATTACHORA during presentations, interviews, or video demonstrations.

---

### Step 1: Launch the Workstation (0:00 - 0:15)
1. Run `run.bat` or execute in PowerShell:
   ```powershell
   streamlit run app.py
   ```
2. The browser opens to `http://localhost:8501`.
3. Point out the enterprise light theme (`#F4F5F4` background, `#356B59` brand accent) and slim left-hand navigation rail.

---

### Step 2: Ingest Sample Email Attachments (0:15 - 0:35)
1. Click the **Connections** tab on the navigation rail.
2. Select the **EML File Importer & Test Suite** tab.
3. Click the primary button: **Import All 12 Sample Test Emails**.
4. Observe the immediate processing feedback: 12 RFC 822 emails parsed, 12 binary/text attachments extracted, validated, hashed with SHA-256, and staged.

---

### Step 3: Inspect & Review Queue in Workspace (0:35 - 0:55)
1. Navigate back to the **Workspace** tab.
2. Highlight the table-first operations queue:
   - Point out **Categorization**: Invoices, Receipts, Resumes / CVs, Spreadsheets, Presentations, Code, Archives.
   - Point out **Proposed Destination**: Automatically computed from priority filing rules (e.g. `Finance/Invoices`, `HR/Resumes`).
   - Point out **Deduplication Tag**: Locate the exact duplicate file (`invoice_aws_nov_2026_copy.pdf` flagged as `Exact Duplicate`).
3. Click on any row (e.g., `invoice_aws_nov_2026.pdf`) to inspect the live PDF preview drawer on the right side.

---

### Step 4: Batch Approval & Organization (0:55 - 1:15)
1. Click **Select All** or select individual rows.
2. Click **Approve Selected**.
3. Watch the system perform atomic file moves to `ATTACHORA_LIBRARY/`, avoiding filename conflicts automatically (`_001.pdf`).
4. Toggle **Automatic Filing Mode** in the top right to explain how high-confidence items can be filed autonomously in enterprise setups.

---

### Step 5: Explore Library & Demonstrate Rollback / Undo (1:15 - 1:30)
1. Click the **Organized Files** tab to view the live library directory structure.
2. Click **Undo / Restore** next to any organized file:
   - The file is instantly moved back to staging.
   - Its status in the audit log updates to `Restored`.
3. Switch to **History & Audit** to view the tamper-evident audit trail, and download the full report via **Export History (CSV)**.
4. Open **Analytics & Reports** to review real calculated storage savings from deduplication.
