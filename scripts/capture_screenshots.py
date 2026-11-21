"""
ATTACHORA Automated Feature Screenshot Capture
Starts the local server and captures high-resolution screenshots of all 8 core views
using Chromium/Edge headless mode, saving them away from git tracking.
"""

import os
import shutil
import subprocess
import sys
import threading
import time
from pathlib import Path

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

import uvicorn
from server import app

PORT = 8555
BASE_URL = f"http://127.0.0.1:{PORT}"

# Target directories (completely away from git repo)
OUT_DIR_EXTERNAL = Path(r"d:\90 days\ATTACHORA_SCREENSHOTS")
OUT_DIR_ARTIFACT = Path(r"C:\Users\ragur\.gemini\antigravity\brain\b92c6aa7-2988-4351-9c8c-afa610453623\screenshots")

OUT_DIR_EXTERNAL.mkdir(parents=True, exist_ok=True)
OUT_DIR_ARTIFACT.mkdir(parents=True, exist_ok=True)

# Locate Edge or Chrome binary
edge_paths = [
    Path(r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"),
    Path(r"C:\Program Files\Microsoft\Edge\Application\msedge.exe"),
    Path(r"C:\Program Files\Google\Chrome\Application\chrome.exe"),
    Path(r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe"),
]

browser_exe = None
for p in edge_paths:
    if p.exists():
        browser_exe = str(p)
        break

if not browser_exe:
    raise RuntimeError("No Chromium/Edge executable found on system.")

print(f"Using browser executable: {browser_exe}")

# Start Uvicorn server in a background thread
config = uvicorn.Config(app=app, host="127.0.0.1", port=PORT, log_level="error")
server = uvicorn.Server(config)
thread = threading.Thread(target=server.run, daemon=True)
thread.start()

print("Waiting for server initialization...")
time.sleep(2.0)

PAGES = [
    ("01_Attachment_Queue", f"{BASE_URL}/?page=Queue"),
    ("02_Smart_Filing_Rules", f"{BASE_URL}/?page=Rules"),
    ("03_Organized_Library", f"{BASE_URL}/?page=Library"),
    ("04_Email_Connections_Ingestion", f"{BASE_URL}/?page=Mailbox"),
    ("05_Integrity_Security_Center", f"{BASE_URL}/?page=Integrity"),
    ("06_Operation_History_Audit", f"{BASE_URL}/?page=History"),
    ("07_Operational_Analytics", f"{BASE_URL}/?page=Analytics"),
    ("08_System_Settings_Preferences", f"{BASE_URL}/?page=Settings"),
]

captured = []

for filename_prefix, url in PAGES:
    filename = f"{filename_prefix}.png"
    target_path = OUT_DIR_EXTERNAL / filename
    print(f"Capturing: {filename} from {url}...")
    
    cmd = [
        browser_exe,
        "--headless=new",
        "--hide-scrollbars",
        "--disable-gpu",
        "--no-sandbox",
        "--window-size=1440,900",
        f"--screenshot={str(target_path)}",
        "--virtual-time-budget=3500",
        url,
    ]
    
    try:
        proc = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=20)
        if target_path.exists() and target_path.stat().st_size > 1000:
            # Also copy to brain artifact directory
            artifact_copy = OUT_DIR_ARTIFACT / filename
            shutil.copy2(target_path, artifact_copy)
            file_size_kb = target_path.stat().st_size // 1024
            print(f"  [OK] Saved {filename} ({file_size_kb} KB)")
            captured.append(target_path)
        else:
            print(f"  [WARNING] Screenshot {filename} not created or empty.")
    except Exception as e:
        print(f"  [ERROR] Failed to capture {filename}: {e}")

server.should_exit = True
print(f"\nAll {len(captured)} feature screenshots successfully captured and saved!")
print(f"Primary external directory: {OUT_DIR_EXTERNAL}")
print(f"Artifact directory: {OUT_DIR_ARTIFACT}")
