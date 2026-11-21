"""
ATTACHORA Organized Library Explorer Page
Displays organized documents in a structured enterprise table with search,
category filtering, disk verification, directory exploration, and single-click Undo restoration.
"""

import os
from pathlib import Path
import pandas as pd
import streamlit as st
from src.config import CONFIG
from src.database.db_manager import DB
from src.storage_manager.undo_manager import UNDO_MANAGER
from ui.theme import get_filetype_badge_html


def render_organized_page():
    st.markdown(
        """
        <div style="margin-bottom: 14px;">
            <h1 style="font-size:22px; font-weight:700; color:#202824; margin:0 0 4px 0;">
                Organized Library Explorer
            </h1>
            <div style="font-size:13px; color:#66716B;">
                Browse structured enterprise filing directories, verify file storage, and rollback file moves.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    col_hdr1, col_hdr2 = st.columns([7, 3])
    with col_hdr1:
        st.markdown(
            f"""
            <div style="font-size:12px; color:#66716B; padding-top:6px;">
                Root Library Path: <code class="hash-pill">{CONFIG.STORAGE_ROOT.resolve()}</code>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with col_hdr2:
        if st.button("Open Library in Windows Explorer", use_container_width=True):
            try:
                os.startfile(str(CONFIG.STORAGE_ROOT.resolve()))
                st.success("Launched Explorer.")
            except Exception as e:
                st.error(f"Could not open explorer: {e}")

    # Search & Filter Toolbar for Library
    f1, f2 = st.columns([7, 3])
    with f1:
        lib_search = st.text_input("Search Organized Documents", placeholder="Filter by filename, sender, or destination...", key="lib_search_kw", label_visibility="collapsed")
    with f2:
        lib_cat = st.selectbox("Category Filter", options=["All Categories"] + list(CONFIG.CATEGORIES), key="lib_cat_filter", label_visibility="collapsed")

    # Query organized attachments
    organized_items = DB.get_attachments_workspace(
        status="Organized",
        search_query=lib_search.strip(),
        category="All" if lib_cat == "All Categories" else lib_cat,
    )

    if not organized_items:
        st.info("No attachments have been organized into the library matching the filter. Approve items in the Queue to file them here.")
        return

    st.markdown(
        f"""
        <div style="font-size:12px; color:#66716B; margin-bottom:8px;">
            Displaying <b>{len(organized_items)}</b> organized documents
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Render Organized Files Table
    st.markdown('<div class="attachora-table-container">', unsafe_allow_html=True)

    # Header Row
    th1, th2, th3, th4, th5, th6 = st.columns([3.2, 2.0, 1.3, 1.2, 1.3, 1.0])
    with th1:
        st.markdown('<div class="attachora-table-header-row" style="border:none; padding:0;">DOCUMENT / STORED NAME</div>', unsafe_allow_html=True)
    with th2:
        st.markdown('<div class="attachora-table-header-row" style="border:none; padding:0;">LOCATION / PATH</div>', unsafe_allow_html=True)
    with th3:
        st.markdown('<div class="attachora-table-header-row" style="border:none; padding:0;">CATEGORY</div>', unsafe_allow_html=True)
    with th4:
        st.markdown('<div class="attachora-table-header-row" style="border:none; padding:0;">SIZE</div>', unsafe_allow_html=True)
    with th5:
        st.markdown('<div class="attachora-table-header-row" style="border:none; padding:0;">STATUS</div>', unsafe_allow_html=True)
    with th6:
        st.markdown('<div class="attachora-table-header-row" style="border:none; padding:0;">ACTION</div>', unsafe_allow_html=True)

    for itm in organized_items:
        itm_id = itm["id"]
        stored_fn = itm.get("stored_filename") or itm.get("original_filename")
        file_path_str = itm.get("current_path")
        file_exists = Path(file_path_str).exists() if file_path_str else False
        ext = itm.get("extension") or ""
        badge_html = get_filetype_badge_html(stored_fn, ext)

        st.markdown('<div class="attachora-table-row">', unsafe_allow_html=True)
        rc1, rc2, rc3, rc4, rc5, rc6 = st.columns([3.2, 2.0, 1.3, 1.2, 1.3, 1.0])

        with rc1:
            st.markdown(
                f"""
                <div style="display:flex; align-items:center; gap:8px;">
                    {badge_html}
                    <div>
                        <div style="font-weight:600; font-size:12px; color:#202824;">{stored_fn}</div>
                        <div style="font-size:11px; color:#66716B;">Orig: {itm.get('original_filename')}</div>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        with rc2:
            parent_dir = Path(file_path_str).parent.name if file_path_str else "Root"
            st.markdown(
                f"""
                <div style="font-family:'JetBrains Mono',monospace; font-size:11px; color:#66716B; padding-top:4px;" title="{file_path_str}">
                    /{parent_dir}
                </div>
                """,
                unsafe_allow_html=True,
            )

        with rc3:
            st.markdown(f'<div style="font-size:12px; color:#202824; padding-top:4px;">{itm.get("category")}</div>', unsafe_allow_html=True)

        with rc4:
            st.markdown(f'<div style="font-size:12px; color:#66716B; padding-top:4px;">{itm.get("file_size", 0)/1024:.1f} KB</div>', unsafe_allow_html=True)

        with rc5:
            if file_exists:
                st.markdown('<div style="color:#278253; font-weight:600; font-size:11px; padding-top:4px;">● Verified on Disk</div>', unsafe_allow_html=True)
            else:
                st.markdown('<div style="color:#BD4545; font-weight:600; font-size:11px; padding-top:4px;">● Missing Payload</div>', unsafe_allow_html=True)

        with rc6:
            if st.button("Undo", key=f"lib_undo_{itm_id}", help="Restores file to staging directory"):
                res = UNDO_MANAGER.undo_operation(itm_id)
                if res["success"]:
                    st.success(res["message"])
                    st.rerun()
                else:
                    st.error(res["error"])

        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)
