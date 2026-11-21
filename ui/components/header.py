"""
ATTACHORA Header Component
Displays top brand bar, active page indicator, connection status, and Scan Now action.
"""

from pathlib import Path
import streamlit as st
from src.config import CONFIG
from src.database.db_manager import DB


def render_header(current_page: str, on_scan_callback=None):
    """Renders the compact enterprise header bar."""
    # Check connection status from database
    accounts = DB.get_accounts()
    active_account = accounts[0] if accounts else None

    if active_account:
        status_label = active_account.get("connection_status", "configured").capitalize()
        status_color = "#32815A" if status_label == "Connected" else "#B78032"
        account_email = active_account.get("account_email", "")
    else:
        status_label = "Local EML Ready"
        status_color = "#356B59"
        account_email = "No IMAP connected"

    st.markdown(
        f"""
        <div class="attachora-header">
            <div style="display: flex; align-items: baseline;">
                <span class="brand-title">ATTACHORA</span>
                <span class="brand-subtitle">/ {current_page}</span>
            </div>
            <div style="display: flex; align-items: center; gap: 15px; font-size: 0.85rem;">
                <span style="color: {CONFIG.COLOR_TEXT_SECONDARY};">Storage: <code class="hash-pill">{CONFIG.STORAGE_ROOT.name}</code></span>
                <span style="color: {status_color}; font-weight: 600;">● {status_label}</span>
                <span style="color: {CONFIG.COLOR_TEXT_SECONDARY};">({account_email})</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
