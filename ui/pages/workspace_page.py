"""
ATTACHORA Attachment Workspace Page
Primary operations hub for inspecting extracted attachments, evaluating proposed filing
actions, reviewing duplicate classifications, and approving or skipping operations.
"""

from pathlib import Path
import streamlit as st
from src.classifier.engine import CLASSIFIER
from src.config import CONFIG
from src.database.db_manager import DB
from src.rules_engine.rule_evaluator import match_filing_rules
from src.storage_manager.duplicate_detector import DuplicateDetector
from src.storage_manager.organizer import ORGANIZER
from ui.components.preview_panel import render_attachment_preview
from ui.components.search_toolbar import render_search_toolbar
from ui.theme import render_status_badge


def render_workspace_page():
    # Operating Mode Toggle
    top_c1, top_c2 = st.columns([3, 1])
    with top_c1:
        st.subheader("Attachment Operations Queue")
        st.caption("Inspect extracted attachments, review proposed filing targets, and execute approved file operations.")
    with top_c2:
        auto_mode = st.toggle("Automatic Filing Mode", value=st.session_state.get("auto_mode", False), key="auto_mode_toggle")
        st.session_state["auto_mode"] = auto_mode
        if auto_mode:
            st.caption("Auto-organizing high-confidence matches (>=90%)")

    # Search & Filter Toolbar
    filters = render_search_toolbar()

    # Query attachments from DB
    attachments = DB.get_attachments_workspace(
        search_query=filters["search_query"],
        category=filters["category"],
        status=filters["status"],
        extension=filters["extension"],
        sender=filters["sender"],
    )

    if not attachments:
        st.info("No attachments found matching the current search criteria or queue is empty. Import sample .EML files in Connections to begin.")
        return

    # Check for Automatic Mode Execution
    if auto_mode:
        auto_count = 0
        rules = DB.get_rules(enabled_only=True)
        for att in attachments:
            if att["status"] in ("Pending Approval", "Detected") and att.get("confidence", 0) >= CONFIG.AUTO_CONFIDENCE_THRESHOLD:
                # Match filing rule
                rule_match = match_filing_rules(rules, att, {"sender": att.get("sender"), "received_at": att.get("received_at")})
                res = ORGANIZER.organize_attachment(
                    attachment_id=att["id"],
                    destination_folder=rule_match["destination"],
                    proposed_filename=rule_match["proposed_filename"],
                    duplicate_action="keep_copy",
                )
                if res["success"]:
                    auto_count += 1
        if auto_count > 0:
            st.success(f"Automatic Mode organized {auto_count} attachments automatically!")
            st.rerun()

    # Selection controls
    ctrl_c1, ctrl_c2, ctrl_c3, ctrl_c4, ctrl_c5 = st.columns([1.2, 1.2, 1.5, 1.5, 2.5])

    # Bulk selections stored in session state
    if "selected_att_ids" not in st.session_state:
        st.session_state["selected_att_ids"] = set()

    with ctrl_c1:
        if st.button("Select All", use_container_width=True):
            st.session_state["selected_att_ids"] = {a["id"] for a in attachments}
            st.rerun()

    with ctrl_c2:
        if st.button("Deselect All", use_container_width=True):
            st.session_state["selected_att_ids"] = set()
            st.rerun()

    selected_ids = list(st.session_state["selected_att_ids"])
    selected_count = len(selected_ids)

    with ctrl_c3:
        approve_btn = st.button(f"Approve Selected ({selected_count})", type="primary", use_container_width=True, disabled=(selected_count == 0))

    with ctrl_c4:
        skip_btn = st.button(f"Skip Selected ({selected_count})", use_container_width=True, disabled=(selected_count == 0))

    # Handle Bulk Approval
    if approve_btn and selected_ids:
        rules = DB.get_rules(enabled_only=True)
        success_count = 0
        for att_id in selected_ids:
            att = DB.get_attachment_by_id(att_id)
            if not att:
                continue
            rule_match = match_filing_rules(rules, att, {"sender": att.get("sender"), "received_at": att.get("received_at")})
            res = ORGANIZER.organize_attachment(
                attachment_id=att_id,
                destination_folder=rule_match["destination"],
                proposed_filename=rule_match["proposed_filename"],
                duplicate_action="keep_copy",
            )
            if res.get("success"):
                success_count += 1

        st.session_state["selected_att_ids"] = set()
        st.success(f"Successfully organized {success_count} approved attachments!")
        st.rerun()

    # Handle Bulk Skip
    if skip_btn and selected_ids:
        for att_id in selected_ids:
            ORGANIZER.organize_attachment(
                attachment_id=att_id,
                destination_folder="Unclassified",
                proposed_filename="skipped.dat",
                duplicate_action="skip",
            )
        st.session_state["selected_att_ids"] = set()
        st.info(f"Skipped {len(selected_ids)} selected attachments.")
        st.rerun()

    # Main Workspace Layout: Table on left, Preview / Action Drawer on right
    col_table, col_preview = st.columns([6, 4])

    with col_table:
        st.markdown(f"**Queue Volume:** {len(attachments)} attachments | Selected: {selected_count}")

        # Render Table-First Rows
        for att in attachments:
            att_id = att["id"]
            is_checked = att_id in st.session_state["selected_att_ids"]

            # Compute proposed values
            rules = DB.get_rules(enabled_only=True)
            rule_match = match_filing_rules(rules, att, {"sender": att.get("sender"), "received_at": att.get("received_at")})

            # Check duplicate status
            dup_detector = DuplicateDetector(DB)
            dup_info = dup_detector.inspect_duplicate(
                sha256=att["sha256"],
                filename=att["original_filename"],
                exclude_attachment_id=att_id,
            )

            # Container for each table row
            is_active = st.session_state.get("selected_row_att_id") == att_id
            bg_color = "#E7EFEB" if is_active else "#FFFFFF"
            border_color = "#356B59" if is_active else "#E1E5E2"

            with st.container():
                st.markdown(
                    f"""
                    <div style="background:{bg_color}; border:1px solid {border_color}; border-radius:6px; padding:8px 12px; margin-bottom:8px;">
                        <div style="display:flex; justify-content:space-between; align-items:center;">
                            <div>
                                <span style="font-weight:600; font-size:0.92rem; color:#252B29;">{att['original_filename']}</span>
                                <span style="font-size:0.75rem; color:#737C78; margin-left:8px;">({att['file_size']/1024:.1f} KB)</span>
                            </div>
                            <div>
                                {render_status_badge(att['status'])}
                            </div>
                        </div>
                        <div style="font-size:0.8rem; color:#737C78; margin-top:3px;">
                            Sender: <span style="color:#252B29;">{att['sender_email'] or att['sender']}</span> &nbsp;•&nbsp;
                            Subject: <span style="color:#252B29;">{att.get('subject', '')[:35]}</span>
                        </div>
                        <div style="font-size:0.78rem; color:#356B59; margin-top:3px; display:flex; justify-content:space-between;">
                            <span>Proposed: <b>{rule_match['destination']}/{rule_match['proposed_filename']}</b></span>
                            <span style="color:{'#6C5CE7' if dup_info['status'] != 'New File' else '#737C78'};">● {dup_info['status']}</span>
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

                row_c1, row_c2, row_c3 = st.columns([1, 2, 2])
                with row_c1:
                    checked = st.checkbox("Select", value=is_checked, key=f"chk_att_{att_id}")
                    if checked and not is_checked:
                        st.session_state["selected_att_ids"].add(att_id)
                        st.rerun()
                    elif not checked and is_checked:
                        st.session_state["selected_att_ids"].remove(att_id)
                        st.rerun()

                with row_c2:
                    if st.button("Inspect & Edit", key=f"inspect_{att_id}", use_container_width=True):
                        st.session_state["selected_row_att_id"] = att_id
                        st.rerun()

                with row_c3:
                    if att["status"] in ("Pending Approval", "Detected"):
                        if st.button("Approve", key=f"app_{att_id}", type="secondary", use_container_width=True):
                            ORGANIZER.organize_attachment(
                                attachment_id=att_id,
                                destination_folder=rule_match["destination"],
                                proposed_filename=rule_match["proposed_filename"],
                                duplicate_action="keep_copy",
                            )
                            st.success(f"Organized {att['original_filename']}")
                            st.rerun()

    # Detail & Preview Panel on Right
    with col_preview:
        active_att_id = st.session_state.get("selected_row_att_id")
        active_att = DB.get_attachment_by_id(active_att_id) if active_att_id else (attachments[0] if attachments else None)

        if active_att:
            st.markdown("#### Attachment Inspector & Actions")

            # Editable Destination and Category
            with st.expander("Modify Proposed Destination & Category", expanded=False):
                with st.form(key=f"edit_form_{active_att['id']}"):
                    new_category = st.selectbox(
                        "Correct Category",
                        options=CONFIG.CATEGORIES,
                        index=CONFIG.CATEGORIES.index(active_att["category"]) if active_att["category"] in CONFIG.CATEGORIES else 0,
                    )
                    new_dest = st.text_input("Destination Folder", value=rule_match["destination"])
                    new_filename = st.text_input("Proposed Filename", value=rule_match["proposed_filename"])

                    dup_strategy = st.radio(
                        "Duplicate Strategy",
                        options=["keep_copy", "skip", "keep_reference"],
                        format_func=lambda x: {
                            "keep_copy": "Keep New Copy (Auto-number if conflict)",
                            "skip": "Skip Duplicate (Do not copy)",
                            "keep_reference": "Reference Existing File",
                        }[x],
                    )

                    save_action = st.form_submit_button("Apply Changes & Organize")
                    if save_action:
                        # Record category feedback if modified
                        if new_category != active_att["category"]:
                            DB.log_feedback(active_att["id"], active_att["category"], new_category)
                            DB.update_attachment_category(active_att["id"], new_category)

                        res = ORGANIZER.organize_attachment(
                            attachment_id=active_att["id"],
                            destination_folder=new_dest,
                            proposed_filename=new_filename,
                            duplicate_action=dup_strategy,
                            reference_path=active_att.get("current_path"),
                        )
                        if res["success"]:
                            st.success(res["message"])
                            st.rerun()
                        else:
                            st.error(res.get("error", "Failed"))

            # Render live preview
            render_attachment_preview(active_att)
        else:
            st.info("Select an attachment row to preview.")
