"""
ATTACHORA Search & Filter Toolbar Component
Provides a full-width search bar, compact multi-attribute filters,
date/duplicate filters, and filter reset controls with active count feedback.
"""

from datetime import date
from typing import Any, Dict
import streamlit as st
from src.config import CONFIG


def render_search_toolbar(total_results: int = 0) -> Dict[str, Any]:
    """Renders the search bar and compact filter toolbar."""
    # 1. Full-width search input with clear action
    sc1, sc2 = st.columns([8.5, 1.5])
    with sc1:
        search_query = st.text_input(
            label="Search Query",
            placeholder="Search attachments, senders, filenames, subjects or SHA-256...",
            key="search_query_input",
            label_visibility="collapsed",
        )
    with sc2:
        if st.button("Clear Search", key="btn_clear_search", use_container_width=True):
            st.session_state["search_query_input"] = ""
            st.rerun()

    # 2. Compact filter toolbar
    fc1, fc2, fc3, fc4, fc5, fc6 = st.columns([1.8, 1.8, 1.5, 1.8, 1.8, 1.3])

    with fc1:
        category_options = ["All"] + list(CONFIG.CATEGORIES)
        selected_category = st.selectbox(
            "Category",
            options=category_options,
            key="ws_filter_cat",
        )

    with fc2:
        status_options = ["All", "Pending Approval", "Organized", "Duplicate", "Skipped", "Restored", "Failed"]
        selected_status = st.selectbox(
            "Processing Status",
            options=status_options,
            key="ws_filter_status",
        )

    with fc3:
        ext_options = ["All", "PDF", "CSV", "XLSX", "PNG", "JPG", "DOCX", "PPTX", "ZIP", "PY", "TXT"]
        selected_ext = st.selectbox(
            "File Type",
            options=ext_options,
            key="ws_filter_ext",
        )

    with fc4:
        dup_options = ["All", "Duplicates Only", "Non-Duplicates Only"]
        selected_dup = st.selectbox(
            "Duplicate Status",
            options=dup_options,
            key="ws_filter_dup",
        )

    with fc5:
        sort_options = {
            "newest": "Newest First",
            "oldest": "Oldest First",
            "size_desc": "Size (Largest)",
            "size_asc": "Size (Smallest)",
            "name_asc": "Name (A-Z)",
        }
        selected_sort = st.selectbox(
            "Sort Order",
            options=list(sort_options.keys()),
            format_func=lambda k: sort_options[k],
            key="ws_filter_sort",
        )

    with fc6:
        st.markdown("<div style='height: 24px;'></div>", unsafe_allow_html=True)
        if st.button("Reset Filters", key="btn_reset_filters", use_container_width=True):
            st.session_state["search_query_input"] = ""
            st.session_state["ws_filter_cat"] = "All"
            st.session_state["ws_filter_status"] = "All"
            st.session_state["ws_filter_ext"] = "All"
            st.session_state["ws_filter_dup"] = "All"
            st.session_state["ws_filter_sort"] = "newest"
            st.rerun()

    return {
        "search_query": search_query.strip(),
        "category": selected_category,
        "status": selected_status,
        "extension": selected_ext,
        "duplicate_filter": selected_dup,
        "sort_by": selected_sort,
        "sender": "All",
    }
