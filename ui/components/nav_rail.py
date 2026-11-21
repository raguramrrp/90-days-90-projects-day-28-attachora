"""
ATTACHORA Navigation Rail Component
Provides a minimalist, professional navigation sidebar without emoji icons,
displaying clean labels, active state indicator, and application metadata.
"""

import streamlit as st

NAV_ITEMS = [
    ("Workspace", "Workspace", "Attachment operations queue and approvals"),
    ("Connections", "Connections", "IMAP accounts and offline .EML file importer"),
    ("Filing Rules", "Filing Rules", "Smart routing rules and priority rankings"),
    ("Organized Files", "Organized Files", "Structured library directory explorer and Undo"),
    ("Operation History", "Operation History", "Immutable operation audit trail and CSV export"),
    ("Analytics", "Analytics", "Operational metrics, storage savings, and sender charts"),
    ("Settings", "Settings", "Storage paths, archive limits, and automation modes"),
]


def render_nav_rail() -> str:
    """Renders the navigation rail in the sidebar and returns active page name."""
    with st.sidebar:
        st.markdown(
            """
            <div style="padding: 6px 0 12px 0; border-bottom: 1px solid #E1E5E2; margin-bottom: 12px;">
                <div style="font-weight: 700; font-size: 16px; color: #356B59; letter-spacing: 0.04em;">ATTACHORA</div>
                <div style="font-size: 11px; color: #737C78; font-weight: 500;">Email Attachment Workstation</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        current = st.session_state.get("active_page", "Workspace")
        labels = [item[0] for item in NAV_ITEMS]
        default_idx = labels.index(current) if current in labels else 0

        # Compact radio navigation without emoji icons
        selected_page = st.radio(
            label="Navigation",
            options=labels,
            index=default_idx,
            label_visibility="collapsed",
        )

        st.session_state["active_page"] = selected_page

        st.markdown("<div style='margin-top: 40px; border-top: 1px solid #E1E5E2; padding-top: 12px;'></div>", unsafe_allow_html=True)
        st.markdown(
            """
            <div style="font-size: 11px; color: #737C78;">
                <div>Environment: <b>Local Desktop</b></div>
                <div>Storage Engine: <b>SQLite 3</b></div>
                <div>Version: <b>1.0.0-PRO</b></div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    return selected_page
