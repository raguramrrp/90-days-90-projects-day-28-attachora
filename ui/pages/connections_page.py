"""
ATTACHORA Email Connections Page
Manages IMAP mailbox connections, secure credential vaults, and .eml file importing.
"""

from datetime import datetime
from pathlib import Path
import streamlit as st
from src.config import CONFIG
from src.database.db_manager import DB
from src.email_engine.imap_client import IMAPClient
from src.email_engine.reader import READER
from src.security.credential_vault import VAULT, mask_credential

# IMAP Provider Presets
PROVIDER_PRESETS = {
    "Gmail (App Password)": {"host": "imap.gmail.com", "port": 993, "ssl": True},
    "Microsoft Outlook / Office 365": {"host": "outlook.office365.com", "port": 993, "ssl": True},
    "Yahoo Mail": {"host": "imap.mail.yahoo.com", "port": 993, "ssl": True},
    "Custom IMAP Server": {"host": "", "port": 993, "ssl": True},
}


def render_connections_page():
    st.markdown(
        """
        <div style="margin-bottom: 14px;">
            <h1 style="font-size:22px; font-weight:700; color:#202824; margin:0 0 4px 0;">
                Mailbox Connections & File Import
            </h1>
            <div style="font-size:13px; color:#66716B;">
                Configure read-only IMAP mailbox connections or import offline .eml email archives for processing.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    tab1, tab2 = st.tabs(["IMAP Account Connections", "EML File Importer & Test Suite"])

    # ------------------ TAB 1: IMAP ACCOUNTS ------------------
    with tab1:
        st.markdown("#### Configured Email Accounts")
        accounts = DB.get_accounts()

        if accounts:
            for acc in accounts:
                with st.expander(f"{acc['account_email']} ({acc['imap_host']})", expanded=True):
                    c1, c2, c3, c4 = st.columns([2, 2, 2, 2])
                    with c1:
                        st.markdown(f"**Mailbox:** `{acc.get('mailbox', 'INBOX')}`")
                        st.markdown(f"**Status:** `{acc.get('connection_status')}`")
                    with c2:
                        st.markdown(f"**Last Sync:** {acc.get('last_sync_at') or 'Never'}")
                        cached_cred = VAULT.get_memory_credential(acc["account_email"])
                        st.markdown(f"**Credential:** `{mask_credential(cached_cred)}`")
                    with c3:
                        sync_pass = st.text_input("Session Password", type="password", key=f"pass_{acc['id']}", placeholder="Enter if not in memory")
                        if sync_pass:
                            VAULT.set_memory_credential(acc["account_email"], sync_pass)

                        if st.button("Sync Mailbox Now", key=f"sync_btn_{acc['id']}", type="primary"):
                            with st.spinner("Connecting to IMAP and extracting attachments..."):
                                res = READER.sync_imap_account(account_id=acc["id"], password_override=sync_pass)
                                if res["success"]:
                                    st.success(f"Sync complete! Scanned {res['messages_scanned']} messages, detected {res['attachments_detected']} attachments.")
                                    st.rerun()
                                else:
                                    st.error(f"Sync failed: {res.get('error')}")

                    with c4:
                        if st.button("Disconnect & Delete", key=f"del_acc_{acc['id']}"):
                            DB.delete_account(acc["id"])
                            st.info(f"Disconnected {acc['account_email']}.")
                            st.rerun()
        else:
            st.info("No active IMAP accounts configured. Add an account below or use the EML Importer tab.")

        st.markdown("---")
        st.markdown("#### Add New IMAP Account")

        preset = st.selectbox("Select Provider Preset", options=list(PROVIDER_PRESETS.keys()))
        preset_info = PROVIDER_PRESETS[preset]

        with st.form("add_imap_account_form"):
            col_a, col_b = st.columns(2)
            with col_a:
                acc_email = st.text_input("Account Email Address", placeholder="user@example.com")
                host_val = st.text_input("IMAP Server Host", value=preset_info["host"])
                mailbox_folder = st.text_input("Mailbox Folder to Scan", value="INBOX")

            with col_b:
                port_val = st.number_input("IMAP Port", min_value=1, max_value=65535, value=preset_info["port"])
                auth_method = st.selectbox("Authentication Method", ["App Password", "Standard Password", "OAuth2 Token"])
                account_password = st.text_input("Password / App Password", type="password", help="Stored securely in memory vault. Plaintext is NEVER stored in database.")

            st.caption("Security Enforcement: Connections operate in strict Read-Only mode. Emails are never deleted, sent, or modified.")

            form_c1, form_c2 = st.columns(2)
            with form_c1:
                test_conn = st.form_submit_button("Test IMAP Connection")
            with form_c2:
                save_conn = st.form_submit_button("Save Account Configuration")

            if test_conn:
                if not host_val or not acc_email or not account_password:
                    st.error("Please fill in Host, Email, and Password to test connection.")
                else:
                    client = IMAPClient(host=host_val, port=int(port_val), username=acc_email, password=account_password, use_ssl=True)
                    ok, msg, mboxes = client.test_connection()
                    if ok:
                        st.success(f"{msg}. Available folders: {', '.join(mboxes[:5])}")
                    else:
                        st.error(msg)

            if save_conn:
                if not host_val or not acc_email:
                    st.error("Host and Email Address are required.")
                else:
                    # Save account metadata in DB
                    acc_id = DB.add_account(
                        account_email=acc_email,
                        imap_host=host_val,
                        imap_port=int(port_val),
                        mailbox=mailbox_folder,
                        auth_type=auth_method,
                    )
                    # Cache credential in memory vault
                    if account_password:
                        VAULT.set_memory_credential(acc_email, account_password)
                    st.success(f"Account '{acc_email}' saved successfully!")
                    st.rerun()

    # ------------------ TAB 2: EML IMPORTER & TEST SUITE ------------------
    with tab2:
        st.markdown("#### Offline EML File Importer & Test Dataset")
        st.caption("Import real or synthetic RFC 822 email files to evaluate classification, deduplication, and rule filing without needing a live email account.")

        col_sample, col_upload = st.columns(2)

        with col_sample:
            st.markdown(
                """
                <div class="station-card">
                    <h4 style="margin-top:0;">Realistic Sample Test Suite</h4>
                    <p style="font-size:0.85rem; color:#737C78;">
                        Imports 12 pre-generated corporate .eml emails covering all 12 categories,
                        including exact duplicates and filename conflicts.
                    </p>
                </div>
                """,
                unsafe_allow_html=True,
            )

            if st.button("Import All 12 Sample Test Emails", type="primary", use_container_width=True):
                sample_dir = CONFIG.SAMPLE_EMAILS_DIR
                if not sample_dir.exists():
                    st.error("Sample directory not found.")
                else:
                    eml_files = sorted(list(sample_dir.glob("*.eml")))
                    imported_count = 0
                    total_attachments = 0
                    with st.spinner("Processing sample email attachments..."):
                        for eml_path in eml_files:
                            staged = READER.import_eml_file(eml_path)
                            imported_count += 1
                            total_attachments += len(staged)

                    st.success(f"Successfully processed {imported_count} emails and detected {total_attachments} attachments!")
                    st.info("Switch to the 'Workspace' page to review, inspect, and approve file actions.")

        with col_upload:
            st.markdown(
                """
                <div class="station-card">
                    <h4 style="margin-top:0;">Upload Custom .EML Files</h4>
                    <p style="font-size:0.85rem; color:#737C78;">
                        Select exported .eml message files from your desktop (Thunderbird, Outlook, Apple Mail).
                    </p>
                </div>
                """,
                unsafe_allow_html=True,
            )

            uploaded_emls = st.file_uploader("Upload .eml files", type=["eml"], accept_multiple_files=True)
            if uploaded_emls:
                if st.button(f"Process {len(uploaded_emls)} Uploaded Files", use_container_width=True):
                    total_uploaded_atts = 0
                    for uploaded in uploaded_emls:
                        raw = uploaded.read()
                        staged = READER.import_eml_bytes(raw, uploaded.name)
                        total_uploaded_atts += len(staged)

                    st.success(f"Processed {len(uploaded_emls)} .eml files ({total_uploaded_atts} attachments detected).")
                    st.rerun()
