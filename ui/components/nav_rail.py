"""
ATTACHORA Navigation Rail Component
Renders a slim, compact navigation rail with icon labels and tooltips.
"""

from typing import Tuple
import streamlit as st

PAGES = [
    ("Workspace", "📁", "Attachment review queue and operation approvals"),
    ("Connections", "🔌", "IMAP email accounts and .EML file importer"),
    ("Filing Rules", "⚙️", "Smart organizational rules and priority ordering"),
    ("Organized Files", "🗄️", "Structured library explorer and file rollback"),
    ("History & Audit", "📜", "Immutable operation history and audit trails"),
    ("Analytics & Reports", "📊", "Operational metrics and CSV data exports"),
    ("Settings", "🛠️", "Storage path configuration and safety limits"),
]


def render_nav_rail() -> str:
    """Renders the navigation rail in the sidebar and returns selected page name."""
    with st.sidebar:
        st.markdown(
            """
            <div style="padding: 10px 0 15px 0; border-bottom: 1px solid #E1E5E2; margin-bottom: 10px;">
                <div style="font-weight: 700; font-size: 1.1rem; color: #356B59; letter-spacing: 0.05em;">ATTACHORA</div>
                <div style="font-size: 0.72rem; color: #737C78;">Intelligent Attachment System</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        current = st.session_state.get("active_page", "Workspace")
        page_names = [p[0] for p in PAGES]
        icons = {p[0]: f"{p[1]}  {p[0]}" for p in PAGES}

        default_idx = page_names.index(current) if current in page_names else 0

        selected_page = st.radio(
            label="Navigation",
            options=page_names,
            index=default_idx,
            format_func=lambda x: icons.get(x, x),
            label_visibility="collapsed",
        )

        st.session_state["active_page"] = selected_page

        st.markdown("<div style='margin-top: 30px;'></div>", unsafe_allow_html=True)
        st.caption("Mode: Enterprise Local")
        st.caption("v1.0.0 · SQLite")

    return selected_page
