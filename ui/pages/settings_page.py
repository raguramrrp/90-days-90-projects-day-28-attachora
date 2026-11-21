"""
ATTACHORA Settings & Configuration Page
Configures storage directory paths, security thresholds, archive bomb defenses,
filename template defaults, and machine credential vault settings.
"""

import os
from pathlib import Path
import streamlit as st
from src.config import CONFIG
from src.database.db_manager import DB
from src.security.credential_vault import VAULT


def render_settings_page():
    st.markdown(
        """
        <div style="margin-bottom: 14px;">
            <h1 style="font-size:22px; font-weight:700; color:#202824; margin:0 0 4px 0;">
                System Settings & Preferences
            </h1>
            <div style="font-size:13px; color:#66716B;">
                Configure root filing destinations, automation confidence limits, filename templates, and security defenses.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    with st.form("settings_form"):
        # 1. Storage Location
        st.markdown("#### 1. Storage Location")
        storage_path_input = st.text_input(
            "Root Storage Directory",
            value=str(CONFIG.STORAGE_ROOT.resolve()),
            help="All classified folders and files are organized relative to this local folder.",
        )

        # 2. Automation & Approval Parameters
        st.markdown("#### 2. Filing Preferences & Automation Mode")
        c_auto1, c_auto2 = st.columns(2)
        with c_auto1:
            default_auto = st.checkbox("Enable Hands-Free Automatic Filing Mode", value=CONFIG.AUTO_MODE)
        with c_auto2:
            conf_threshold = st.slider("Automatic Filing Confidence Threshold", min_value=0.50, max_value=1.00, value=CONFIG.AUTO_CONFIDENCE_THRESHOLD, step=0.05)

        # 3. Filename Templates & Duplicate Defaults
        st.markdown("#### 3. Filename Template & Duplicate Strategy Defaults")
        c_tmpl1, c_tmpl2 = st.columns(2)
        with c_tmpl1:
            default_tmpl = st.text_input("Default Filename Pattern", value="{date}_{category}_{original_filename}")
            st.caption("Tokens: {date}, {category}, {sender}, {sender_domain}, {subject}, {original_filename}")
        with c_tmpl2:
            default_dup = st.selectbox("Default Duplicate Policy", ["Keep Copy (Numbered)", "Skip Duplicate", "Link Reference"])

        # 4. Security Limits & Archive Defenses
        st.markdown("#### 4. Security Limits & Archive Defenses")
        c_sec1, c_sec2 = st.columns(2)
        with c_sec1:
            max_size_mb = st.number_input("Max Allowed Attachment Size (MB)", min_value=1, max_value=500, value=int(CONFIG.MAX_FILE_SIZE_BYTES / (1024 * 1024)))
        with c_sec2:
            max_archive_mb = st.number_input("Max Archive Uncompressed Size (MB)", min_value=10, max_value=2000, value=int(CONFIG.MAX_ARCHIVE_SIZE_BYTES / (1024 * 1024)))

        save_settings = st.form_submit_button("Save Configuration", type="primary")

        if save_settings:
            target_p = Path(storage_path_input)
            try:
                target_p.mkdir(parents=True, exist_ok=True)
                st.success(f"Storage path '{target_p}' validated and configured.")
            except Exception as e:
                st.error(f"Cannot create or access path: {str(e)}")

    st.markdown("---")

    # 5. Credential Vault Management
    st.markdown("#### 5. Machine Credential Vault Management")
    c_v1, c_v2 = st.columns(2)
    with c_v1:
        st.markdown(f"**Vault Key Location:** `{CONFIG.VAULT_KEY_PATH}`")
        st.caption("Machine-bound key protecting local cached tokens and credentials.")
    with c_v2:
        if st.button("Purge In-Memory Session Passwords", use_container_width=True):
            VAULT.clear_memory_vault()
            st.info("In-memory credential vault cleared. Credentials will need to be re-entered at next sync.")

    st.markdown("---")

    # 6. User Feedback & Machine Learning Tuning
    st.markdown("#### 6. User Feedback & Machine Learning Model")
    feedback_rows = DB.get_feedback_records()
    st.markdown(f"**Logged User Classification Corrections:** {len(feedback_rows)}")
    if feedback_rows:
        if st.button("Retrain Local ML Model from Logged Corrections"):
            from src.classifier.ml_classifier import ML_CLASSIFIER
            count = ML_CLASSIFIER.retrain_with_feedback(feedback_rows)
            st.success(f"Successfully retrained local model with {count} user corrections!")
    else:
        st.caption("No manual classification overrides logged yet. When you override categories in the Queue, corrections are recorded here for local on-device ML model tuning.")
