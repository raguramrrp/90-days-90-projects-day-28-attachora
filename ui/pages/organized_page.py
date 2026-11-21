"""
ATTACHORA Organized Files Page
Explores the structured local storage library, verifies organized files on disk,
and executes safe single-click Undo and file restoration operations.
"""

import os
from pathlib import Path
import streamlit as st
from src.config import CONFIG
from src.database.db_manager import DB
from src.storage_manager.undo_manager import UNDO_MANAGER


def render_organized_page():
    st.subheader("Organized Files Explorer")
    st.caption("Inspect successfully classified and filed documents in the local library, explore directory hierarchies, and rollback file moves.")

    col_hdr1, col_hdr2 = st.columns([3, 1])
    with col_hdr1:
        st.markdown(f"**Root Library Location:** `{CONFIG.STORAGE_ROOT.resolve()}`")
    with col_hdr2:
        if st.button("Open Library in Windows Explorer", use_container_width=True):
            try:
                os.startfile(str(CONFIG.STORAGE_ROOT.resolve()))
                st.success("Launched Explorer.")
            except Exception as e:
                st.error(f"Could not open explorer: {e}")

    # Query organized attachments from database
    organized_items = DB.get_attachments_workspace(status="Organized")

    if not organized_items:
        st.info("No attachments have been organized into the library yet. Approve items in the Workspace page to file them here.")
        return

    st.markdown(f"**Total Organized Files:** {len(organized_items)}")

    # Group by destination folder
    folders = {}
    for item in organized_items:
        curr_p = item.get("current_path") or ""
        folder_name = Path(curr_p).parent.name if curr_p else "Root"
        folders.setdefault(folder_name, []).append(item)

    for folder_name, items in folders.items():
        with st.expander(f"📁 {folder_name} ({len(items)} files)", expanded=True):
            for itm in items:
                itm_id = itm["id"]
                file_path_str = itm.get("current_path")
                file_exists = Path(file_path_str).exists() if file_path_str else False

                c1, c2, c3, c4 = st.columns([3, 2, 2, 2])
                with c1:
                    st.markdown(f"**{itm.get('stored_filename') or itm.get('original_filename')}**")
                    st.caption(f"Original: {itm.get('original_filename')}")

                with c2:
                    st.markdown(f"Category: `{itm.get('category')}`")
                    st.caption(f"Size: {itm.get('file_size', 0)/1024:.1f} KB")

                with c3:
                    if file_exists:
                        st.markdown("<span style='color:#32815A; font-weight:600;'>● On Disk</span>", unsafe_allow_html=True)
                    else:
                        st.markdown("<span style='color:#BC4B4B; font-weight:600;'>● Missing</span>", unsafe_allow_html=True)
                    st.caption(f"SHA: {itm.get('sha256')[:10]}...")

                with c4:
                    if st.button("Undo / Restore", key=f"undo_btn_{itm_id}", help="Moves file back to staging and marks as Restored in audit log"):
                        res = UNDO_MANAGER.undo_operation(itm_id)
                        if res["success"]:
                            st.success(res["message"])
                            st.rerun()
                        else:
                            st.error(res["error"])
