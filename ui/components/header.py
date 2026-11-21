"""
ATTACHORA Header Component
Displays top brand bar, breadcrumb title, verified connection status, storage indicator,
and a functional Scan Now trigger.
"""

from pathlib import Path
import streamlit as st
from src.config import CONFIG
from src.database.db_manager import DB
from src.email_engine.reader import READER


def render_header(current_page: str):
    """Renders the top workstation header with real connection state and functional Scan Now."""
    accounts = DB.get_accounts()
    active_account = accounts[0] if accounts else None

    # Verified Connection State
    if active_account:
        conn_status = active_account.get("connection_status", "configured")
        if conn_status == "connected":
            status_text = "Connected"
            status_color = "#32815A"
        elif conn_status == "error":
            status_text = "Sync Error"
            status_color = "#BC4B4B"
        else:
            status_text = "Configured (Idle)"
            status_color = "#B78032"
        account_label = active_account.get("account_email", "")
    else:
        status_text = "No IMAP Account"
        status_color = "#737C78"
        account_label = "Local Mode"

    # Layout Header Bar
    head_c1, head_c2 = st.columns([5, 5])

    with head_c1:
        st.markdown(
            f"""
            <div style="display:flex; align-items:center; gap:8px; padding-top:4px;">
                <span class="brand-title">ATTACHORA</span>
                <span style="color:#D5DBD7; font-weight:300;">|</span>
                <span style="font-size:14px; font-weight:600; color:#252B29;">{current_page}</span>
                <span style="font-size:12px; color:#737C78;">(Local Operations Workstation)</span>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with head_c2:
        r1, r2, r3 = st.columns([2.5, 2.5, 2])
        with r1:
            st.markdown(
                f"""
                <div style="font-size:11px; color:#737C78; text-align:right; padding-top:6px;">
                    Storage: <code class="hash-pill">{CONFIG.STORAGE_ROOT.name}</code>
                </div>
                """,
                unsafe_allow_html=True,
            )
        with r2:
            st.markdown(
                f"""
                <div style="font-size:12px; text-align:right; padding-top:6px;">
                    <span style="color:{status_color}; font-weight:600;">● {status_text}</span>
                </div>
                """,
                unsafe_allow_html=True,
            )
        with r3:
            if st.button("Scan Now", key="btn_header_scan_now", use_container_width=True):
                if active_account:
                    with st.spinner(f"Connecting to {active_account['imap_host']}..."):
                        res = READER.sync_imap_account(account_id=active_account["id"])
                        if res["success"]:
                            st.success(f"Scanned {res['messages_scanned']} msgs ({res['attachments_detected']} attachments).")
                            st.rerun()
                        else:
                            st.error(f"IMAP sync failed: {res.get('error')}")
                else:
                    # No IMAP configured - check if sample directory has files to ingest
                    sample_dir = CONFIG.SAMPLE_EMAILS_DIR
                    if sample_dir.exists():
                        emls = list(sample_dir.glob("*.eml"))
                        if emls:
                            with st.spinner("No IMAP account configured. Scanning local sample .eml files..."):
                                count = 0
                                for eml in emls:
                                    staged = READER.import_eml_file(eml)
                                    count += len(staged)
                                st.success(f"Scanned {len(emls)} sample emails ({count} attachments detected).")
                                st.rerun()
                        else:
                            st.warning("No IMAP account configured and no local .eml files found in data/sample_emails. Configure an account in Connections.")
                    else:
                        st.warning("No IMAP account configured. Please configure an account in the Connections tab.")

    st.markdown("<div style='border-bottom: 1px solid #E1E5E2; margin-bottom: 12px;'></div>", unsafe_allow_html=True)
