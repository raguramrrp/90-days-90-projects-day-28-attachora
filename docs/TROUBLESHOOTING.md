# ATTACHORA — Troubleshooting Guide

Common issues, error codes, and operational fixes for Windows environments.

---

### 1. `ModuleNotFoundError: No module named 'streamlit'`
- **Cause:** Running Python commands outside the activated virtual environment.
- **Fix:** Run `.\.venv\Scripts\activate.bat` before executing commands, or launch via `run.bat`.

### 2. IMAP Connection Error: "Invalid credentials"
- **Cause:** Many modern email providers (e.g. Gmail, Yahoo, Microsoft) do not accept your regular login password over IMAP.
- **Fix:** Generate an **App Password** in your provider's security settings (e.g., Google Account -> Security -> 2-Step Verification -> App Passwords). Use the 16-character App Password in ATTACHORA.

### 3. IMAP Connection Timed Out
- **Cause:** Network firewall or incorrect port configuration.
- **Fix:** Ensure port is set to `993` for SSL/TLS connections. If behind an enterprise VPN or proxy, verify outbound port 993 is permitted. Alternatively, use the offline `.eml` importer.

### 4. File Not Allowed / Size Exceeded
- **Cause:** Attachment size exceeds configured maximum limit (default: 25 MB).
- **Fix:** Go to **Settings** -> increase **Max Allowed Attachment Size (MB)** to accommodate larger files.

### 5. Suspicious Archive / ZIP Bomb Warning
- **Cause:** ATTACHORA detects an archive containing over 500 files, an uncompressed size over 100 MB, or compression ratios exceeding 100:1.
- **Fix:** This is an intentional security safeguard. If you need to inspect larger archives, adjust the threshold in **Settings** -> **Max Archive Uncompressed Size**.
