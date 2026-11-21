# ATTACHORA — Quick Start Guide

Get ATTACHORA running locally on Windows in less than 2 minutes.

---

## Method 1: Automated Windows Setup (Recommended)

1. Double-click or run `setup.bat`:
   ```powershell
   .\setup.bat
   ```
   This will:
   - Create a project-specific Python virtual environment (`.venv`).
   - Install required dependencies from `requirements.txt`.
   - Generate all 12 realistic sample `.eml` test emails.
   - Initialize the SQLite database with default enterprise filing rules.

2. Launch the application:
   ```powershell
   .\run.bat
   ```

3. Run automated verification tests:
   ```powershell
   .\test.bat
   ```

---

## Method 2: Manual PowerShell Setup

If you prefer executing commands manually:

```powershell
# 1. Navigate to project root
cd "d:\90 days\90-days-90-projects-day-28-attachora"

# 2. Create virtual environment
python -m venv --system-site-packages .venv

# 3. Activate virtual environment
.\.venv\Scripts\Activate.ps1

# 4. Install dependencies
pip install -r requirements.txt

# 5. Generate sample email dataset
python scripts\generate_sample_emls.py

# 6. Run automated test suite
python -m pytest tests -v

# 7. Start the workstation
streamlit run app.py
```

---

## First-Time Walkthrough

1. Open your browser to `http://localhost:8501`.
2. Go to the **Connections** tab -> click **Import All 12 Sample Test Emails**.
3. Return to the **Workspace** tab -> inspect attachments in the queue.
4. Click **Select All** -> click **Approve Selected** to organize them into `ATTACHORA_LIBRARY/`.
5. Visit **Organized Files** to explore the sorted folders and test the single-click **Undo / Restore** button.
