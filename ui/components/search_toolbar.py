"""
ATTACHORA Search & Filter Toolbar Component
Provides unified global search input and compact filter controls.
"""

from typing import Any, Dict
import streamlit as st
from src.config import CONFIG
from src.database.db_manager import DB


def render_search_toolbar() -> Dict[str, Any]:
    """Renders the top wide search bar and compact dropdown filters.

    Returns a dict of active search and filter arguments.
    """
    # 1. Wide search bar
    search_col, clear_col = st.columns([6, 1])
    with search_col:
        search_query = st.text_input(
            label="Search Attachments",
            placeholder="Search attachments, senders, filenames, subjects, categories, or SHA-256...",
            key="global_search_input",
            label_visibility="collapsed",
        )
    with clear_col:
        if st.button("Clear Search", use_container_width=True):
            st.session_state["global_search_input"] = ""
            st.rerun()

    # 2. Compact filter toolbar
    f1, f2, f3, f4 = st.columns(4)

    # Categories list
    category_options = ["All"] + list(CONFIG.CATEGORIES)
    with f1:
        selected_category = st.selectbox(
            "Category",
            options=category_options,
            index=0,
            key="filter_category",
        )

    # Statuses list
    status_options = ["All", "Pending Approval", "Organized", "Duplicate", "Skipped", "Restored", "Failed"]
    with f2:
        selected_status = st.selectbox(
            "Processing Status",
            options=status_options,
            index=0,
            key="filter_status",
        )

    # File extensions list
    ext_options = ["All", "PDF", "CSV", "XLSX", "PNG", "JPG", "DOCX", "PPTX", "ZIP", "PY", "TXT"]
    with f3:
        selected_ext = st.selectbox(
            "File Type / Extension",
            options=ext_options,
            index=0,
            key="filter_extension",
        )

    # Sender filter
    with f4:
        sender_query = st.text_input(
            "Sender Filter",
            placeholder="Filter by sender email...",
            key="filter_sender",
        )

    return {
        "search_query": search_query.strip(),
        "category": selected_category,
        "status": selected_status,
        "extension": selected_ext,
        "sender": sender_query.strip(),
    }
