"""
ATTACHORA Horizontal Top Navigation Bar
Provides the exact header matching the reference image:
- ATTACHORA wordmark and workspace breadcrumb
- Center navigation links: Queue, Rules, Library, History, Analytics, Settings
- Right mailbox connection status and 'Import files' button
"""

from pathlib import Path
import streamlit as st
from src.config import CONFIG
from src.database.db_manager import DB

NAV_LINKS = [
    ("Queue", "Queue"),
    ("Rules", "Rules"),
    ("Library", "Library"),
    ("History", "History"),
    ("Analytics", "Analytics"),
    ("Settings", "Settings"),
]


def render_header(current_page: str):
    """Renders the horizontal topbar with centered navigation and connection state."""
    # Check if a topbar link was clicked via query param
    if "page" in st.query_params and st.query_params["page"]:
        current_page = st.query_params["page"]
        st.session_state["active_page"] = current_page

    accounts = DB.get_accounts()
    active_account = accounts[0] if accounts else None

    # Real connection state
    if active_account:
        conn_status = active_account.get("connection_status", "configured")
        if conn_status == "connected":
            status_text = f"Connected ({active_account['account_email']})"
            dot_color = "#278253"
        elif conn_status == "error":
            status_text = "Sync error"
            dot_color = "#BD4545"
        else:
            status_text = f"{active_account['account_email']}"
            dot_color = "#278253"
    else:
        status_text = "Local mailbox"
        dot_color = "#278253"

    # Render HTML topbar
    st.markdown(
        f"""
        <div class="attachora-topbar">
            <div class="topbar-brand">
                <span class="topbar-title">ATTACHORA</span>
                <span class="topbar-separator">|</span>
                <span class="topbar-breadcrumb">Workspace / {current_page}</span>
            </div>
            <div class="topbar-actions">
                <div class="mailbox-pill">
                    <span class="status-dot" style="background-color:{dot_color};"></span>
                    <span>{status_text}</span>
                    <span style="font-size:10px; color:#66716B; margin-left:3px;">▾</span>
                </div>
                <a href="?page=Mailbox" target="_self" style="text-decoration:none;">
                    <div style="background-color:#286B50; color:#FFFFFF; font-size:12px; font-weight:600; padding:6px 12px; border-radius:6px; display:flex; align-items:center; gap:5px; cursor:pointer;">
                        <span>↓</span>
                        <span>Import files</span>
                    </div>
                </a>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
