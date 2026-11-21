# ATTACHORA — User Guide

A step-by-step operational manual for managing email attachments with ATTACHORA.

---

## 1. Connecting an Email Account (IMAP)
1. Open the **Connections** screen from the sidebar.
2. Select your provider preset (e.g. *Gmail*, *Microsoft 365*, *Yahoo*, or *Custom IMAP*).
3. Enter your account email address, IMAP host, port (default: 993), and password/app password.
4. Click **Test IMAP Connection** to verify access without saving.
5. Click **Save Account Configuration** to store settings in the database.
6. Note: Password credentials are never stored in plaintext SQLite; they reside in an encrypted local vault.

## 2. Importing Offline .EML Files
If you do not have live IMAP credentials or wish to test offline:
1. Navigate to the **Connections** -> **EML File Importer** tab.
2. Click **Import All 12 Sample Test Emails** for immediate demonstration data.
3. Alternatively, upload `.eml` files from your desktop using the file drop zone.

## 3. Working in the Approval Workspace
The **Workspace** is your operational command center:
- **Table-First Review:** Each row displays original filename, file size, sender, subject, proposed destination, and duplicate status.
- **Preview & Inspection:** Click **Inspect & Edit** on any row to open the preview drawer on the right side.
- **In-App Previews:** Safely inspect PDFs, images, spreadsheets, and source code directly in the workstation.
- **Approval Actions:**
  - Click **Approve** on a row to file the document immediately.
  - Select multiple rows using checkboxes and click **Approve Selected**.
  - Click **Skip Selected** to bypass unwanted items without deleting.

## 4. Customizing Smart Filing Rules
1. Navigate to **Filing Rules**.
2. Review active rules and their priority rankings (Priority 1 executes before Priority 2).
3. To add a rule:
   - Provide a descriptive name (e.g. *AWS Invoices to Cloud Finance*).
   - Define condition groups with AND/OR logic.
   - Choose destination subfolder (e.g. `Finance/AWS`).
   - Define a naming template: `{date}_{category}_{original_filename}`.
4. Test rules in the **Rule Tester** tab against any active attachment in your queue.

## 5. Rollback & Restoring Files (Undo)
If a file was organized into the wrong folder:
1. Navigate to the **Organized Files** page.
2. Locate the file in the library directory tree.
3. Click the **Undo / Restore** button.
4. ATTACHORA will safely move the file back to the staging area and update the audit log status to `Restored`.
