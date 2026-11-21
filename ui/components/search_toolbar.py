"""
ATTACHORA Search & Filter Toolbar Component
Implements the exact search field, compact dropdown filters, and bulk action toolbar matching the reference image.
"""

from typing import Any, Dict, List
import streamlit as st
from src.config import CONFIG


def render_search_and_filters(senders_list: List[str] = None) -> Dict[str, Any]:
    """Renders the full search bar and compact filter toolbar."""
    # 1. Search Bar with Clear action
    sc1, sc2 = st.columns([9.2, 0.8])
    with sc1:
        search_query = st.text_input(
            label="Search Query",
            placeholder="Search filename, sender, subject or SHA-256",
            key="search_query_input",
            label_visibility="collapsed",
        )
    with sc2:
        if st.button("Clear", key="btn_clear_search", use_container_width=True):
            st.session_state["search_query_input"] = ""
            st.rerun()

    # 2. Compact Filter Toolbar
    fc1, fc2, fc3, fc4, fc5, fc6 = st.columns([1.8, 1.6, 1.6, 1.8, 1.8, 1.4])

    with fc1:
        category_options = ["All Categories"] + list(CONFIG.CATEGORIES)
        selected_category = st.selectbox(
            "Category",
            options=category_options,
            key="filter_category_val",
            label_visibility="collapsed",
        )

    with fc2:
        status_options = ["All Statuses", "Ready", "Duplicate", "Review", "Filed", "Failed"]
        selected_status = st.selectbox(
            "Status",
            options=status_options,
            key="filter_status_val",
            label_visibility="collapsed",
        )

    with fc3:
        ext_options = ["All File Types", "PDF", "DOCX", "XLSX", "ZIP", "TXT", "PNG", "JPG"]
        selected_ext = st.selectbox(
            "File Type",
            options=ext_options,
            key="filter_ext_val",
            label_visibility="collapsed",
        )

    with fc4:
        sender_opts = ["All Senders"] + (senders_list or [])
        selected_sender = st.selectbox(
            "Sender",
            options=sender_opts,
            key="filter_sender_val",
            label_visibility="collapsed",
        )

    with fc5:
        date_options = ["All Dates", "Today", "Past 7 Days", "Past 30 Days", "Past 90 Days"]
        selected_date = st.selectbox(
            "Date Range",
            options=date_options,
            key="filter_date_val",
            label_visibility="collapsed",
        )

    with fc6:
        if st.button("↺ Reset", key="btn_reset_all_filters", use_container_width=True):
            st.session_state["search_query_input"] = ""
            st.session_state["filter_category_val"] = "All Categories"
            st.session_state["filter_status_val"] = "All Statuses"
            st.session_state["filter_ext_val"] = "All File Types"
            st.session_state["filter_sender_val"] = "All Senders"
            st.session_state["filter_date_val"] = "All Dates"
            st.rerun()

    return {
        "search_query": search_query.strip(),
        "category": "All" if selected_category == "All Categories" else selected_category,
        "status": "All" if selected_status == "All Statuses" else selected_status,
        "extension": "All" if selected_ext == "All File Types" else selected_ext,
        "sender": "All" if selected_sender == "All Senders" else selected_sender,
        "date_range": selected_date,
    }


def render_bulk_toolbar(selected_count: int, on_approve=None, on_skip=None, on_clear=None):
    """Renders the bulk actions toolbar matching the reference image."""
    bc1, bc2, bc3, bc4, bc_empty = st.columns([1.6, 2.2, 1.4, 2.0, 3.8])

    with bc1:
        # Selection count pill
        st.markdown(
            f"""
            <div style="background-color:#E9F2EC; color:#202824; font-size:12px; font-weight:600; padding:6px 12px; border-radius:6px; border:1px solid #DCE3DE; display:flex; align-items:center; gap:5px; height:36px;">
                <span style="color:#278253;">✓</span>
                <span><b>{selected_count}</b> selected</span>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with bc2:
        btn_approve = st.button(
            "✓  Approve and file",
            key="btn_bulk_approve_action",
            type="primary",
            use_container_width=True,
            disabled=(selected_count == 0),
        )
        if btn_approve and on_approve:
            on_approve()

    with bc3:
        btn_skip = st.button(
            "▷|  Skip",
            key="btn_bulk_skip_action",
            use_container_width=True,
            disabled=(selected_count == 0),
        )
        if btn_skip and on_skip:
            on_skip()

    with bc4:
        btn_clear = st.button(
            "✕  Clear selection",
            key="btn_bulk_clear_action",
            use_container_width=True,
            disabled=(selected_count == 0),
        )
        if btn_clear and on_clear:
            on_clear()
