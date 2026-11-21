"""
ATTACHORA Attachment Workspace Page
Two-column structured operations hub: 62% queue and 38% detailed inspector & preview panel.
"""

from pathlib import Path
import streamlit as st
from src.classifier.engine import CLASSIFIER
from src.config import CONFIG
from src.database.db_manager import DB
from src.rules_engine.rule_evaluator import match_filing_rules
from src.storage_manager.duplicate_detector import DuplicateDetector
from src.storage_manager.organizer import ORGANIZER
from src.storage_manager.undo_manager import UNDO_MANAGER
from ui.components.preview_panel import render_attachment_preview
from ui.components.search_toolbar import render_search_toolbar
from ui.theme import render_status_badge


def render_workspace_page():
    # Operating Mode & Header Action
    top_c1, top_c2 = st.columns([3, 1])
    with top_c1:
        st.markdown("<h2 style='margin:0;'>Attachment Operations Queue</h2>", unsafe_allow_html=True)
        st.caption("Review extracted attachments, inspect file contents, apply custom routing, and approve filing operations.")
    with top_c2:
        auto_mode = st.toggle("Automatic Mode", value=st.session_state.get("auto_mode", False), key="auto_mode_toggle", help="Automatically file matches with >=90% confidence")
        st.session_state["auto_mode"] = auto_mode

    # Search & Filter Toolbar
    filters = render_search_toolbar()

    # Query attachments with all active filters
    attachments = DB.get_attachments_workspace(
        search_query=filters["search_query"],
        category=filters["category"],
        status=filters["status"],
        extension=filters["extension"],
        sender=filters["sender"],
        duplicate_filter=filters.get("duplicate_filter", "All"),
        sort_by=filters.get("sort_by", "newest"),
    )

    # Automatic Filing Mode Processing
    if auto_mode:
        auto_count = 0
        rules = DB.get_rules(enabled_only=True)
        for att in attachments:
            if att["status"] in ("Pending Approval", "Detected") and att.get("confidence", 0) >= CONFIG.AUTO_CONFIDENCE_THRESHOLD:
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
            st.success(f"Automatic Mode organized {auto_count} attachments autonomously.")
            st.rerun()

    # Empty State Handling
    if not attachments:
        st.markdown(
            """
            <div class="station-card" style="text-align:center; padding: 36px 20px;">
                <h3 style="color:#737C78;">No Attachments Found</h3>
                <p style="color:#737C78; font-size:13px; max-width:500px; margin:0 auto 16px auto;">
                    No attachment records match the current search or filter parameters.
                    Reset filters or import sample messages from the Connections tab.
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )
        return

    # Bulk Selection State
    if "selected_att_ids" not in st.session_state:
        st.session_state["selected_att_ids"] = set()

    # Control Bar
    bar_c1, bar_c2, bar_c3, bar_c4, bar_c5 = st.columns([1.2, 1.2, 1.8, 1.8, 4])

    with bar_c1:
        if st.button("Select All", key="ws_btn_sel_all", use_container_width=True):
            st.session_state["selected_att_ids"] = {a["id"] for a in attachments}
            st.rerun()

    with bar_c2:
        if st.button("Deselect All", key="ws_btn_desel_all", use_container_width=True):
            st.session_state["selected_att_ids"] = set()
            st.rerun()

    selected_ids = list(st.session_state["selected_att_ids"])
    selected_count = len(selected_ids)

    with bar_c3:
        approve_bulk = st.button(
            f"Approve ({selected_count})",
            key="ws_btn_approve_bulk",
            type="primary",
            use_container_width=True,
            disabled=(selected_count == 0),
        )

    with bar_c4:
        skip_bulk = st.button(
            f"Skip ({selected_count})",
            key="ws_btn_skip_bulk",
            use_container_width=True,
            disabled=(selected_count == 0),
        )

    with bar_c5:
        st.markdown(
            f"""
            <div style="font-size:12px; color:#737C78; text-align:right; padding-top:6px;">
                Displaying <b>{len(attachments)}</b> matching attachments | <b>{selected_count}</b> selected
            </div>
            """,
            unsafe_allow_html=True,
        )

    # Handle Bulk Approval
    if approve_bulk and selected_ids:
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
        st.success(f"Organized {success_count} approved attachments.")
        st.rerun()

    # Handle Bulk Skip
    if skip_bulk and selected_ids:
        for att_id in selected_ids:
            ORGANIZER.organize_attachment(
                attachment_id=att_id,
                destination_folder="Unclassified",
                proposed_filename="skipped.dat",
                duplicate_action="skip",
            )
        st.session_state["selected_att_ids"] = set()
        st.info(f"Skipped {len(selected_ids)} attachments.")
        st.rerun()

    # Two-Column Workspace: Left 62%, Right 38%
    col_queue, col_inspector = st.columns([62, 38])

    # Default Active Row Selection
    if "selected_row_att_id" not in st.session_state or not st.session_state["selected_row_att_id"]:
        st.session_state["selected_row_att_id"] = attachments[0]["id"]

    active_id = st.session_state["selected_row_att_id"]

    # ------------------ LEFT COLUMN: QUEUE ------------------
    with col_queue:
        rules = DB.get_rules(enabled_only=True)
        dup_detector = DuplicateDetector(DB)

        for att in attachments:
            att_id = att["id"]
            is_active = (att_id == active_id)
            is_checked = att_id in st.session_state["selected_att_ids"]

            rule_match = match_filing_rules(rules, att, {"sender": att.get("sender"), "received_at": att.get("received_at")})
            dup_info = dup_detector.inspect_duplicate(
                sha256=att["sha256"],
                filename=att["original_filename"],
                exclude_attachment_id=att_id,
            )

            # High-density, professional queue card
            card_class = "queue-row queue-row-selected" if is_active else "queue-row"

            st.markdown(
                f"""
                <div class="{card_class}">
                    <div style="display:flex; justify-content:space-between; align-items:center;">
                        <div style="font-weight:600; font-size:13px; color:#252B29;">
                            {att['original_filename']}
                            <span style="font-size:11px; color:#737C78; font-weight:normal; margin-left:6px;">({att['file_size']/1024:.1f} KB · {att.get('extension', '').upper()})</span>
                        </div>
                        <div>
                            {render_status_badge(att['status'])}
                        </div>
                    </div>
                    <div style="font-size:12px; color:#737C78; margin-top:3px;">
                        <span>From: <b style="color:#252B29;">{att.get('sender_email') or att.get('sender') or 'Unknown'}</b></span>
                        <span style="margin: 0 6px;">·</span>
                        <span>Date: <span style="color:#252B29;">{str(att.get('received_at', ''))[:10]}</span></span>
                    </div>
                    <div style="font-size:12px; color:#356B59; margin-top:3px; display:flex; justify-content:space-between;">
                        <span>Target: <b>{rule_match['destination']}/{rule_match['proposed_filename']}</b></span>
                        <span style="color:{'#6C5CE7' if dup_info['status'] != 'New File' else '#737C78'}; font-weight:500;">● {dup_info['status']}</span>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

            # Compact inline selection and row activation
            rc1, rc2, rc3 = st.columns([1, 4, 2])
            with rc1:
                chk = st.checkbox("Select", value=is_checked, key=f"chk_row_{att_id}", label_visibility="collapsed")
                if chk and not is_checked:
                    st.session_state["selected_att_ids"].add(att_id)
                    st.rerun()
                elif not chk and is_checked:
                    st.session_state["selected_att_ids"].remove(att_id)
                    st.rerun()

            with rc2:
                if not is_active:
                    if st.button(f"Inspect Details", key=f"btn_sel_{att_id}", use_container_width=True):
                        st.session_state["selected_row_att_id"] = att_id
                        st.rerun()
                else:
                    st.markdown("<div style='font-size:12px; color:#356B59; font-weight:600; padding-top:4px;'>Active in Inspector</div>", unsafe_allow_html=True)

            with rc3:
                if att["status"] in ("Pending Approval", "Detected"):
                    if st.button("Approve", key=f"btn_app_{att_id}", use_container_width=True):
                        res = ORGANIZER.organize_attachment(
                            attachment_id=att_id,
                            destination_folder=rule_match["destination"],
                            proposed_filename=rule_match["proposed_filename"],
                            duplicate_action="keep_copy",
                        )
                        if res["success"]:
                            st.success(f"Organized {att['original_filename']}")
                            st.rerun()

    # ------------------ RIGHT COLUMN: INSPECTOR & PREVIEW ------------------
    with col_inspector:
        active_att = DB.get_attachment_by_id(active_id)
        if not active_att:
            st.info("Select an attachment to inspect.")
            return

        rule_match = match_filing_rules(rules, active_att, {"sender": active_att.get("sender"), "received_at": active_att.get("received_at")})

        dup_info = dup_detector.inspect_duplicate(
            sha256=active_att["sha256"],
            filename=active_att["original_filename"],
            exclude_attachment_id=active_att["id"],
        )

        st.markdown("### Attachment Inspector")

        # Inspector Actions Bar
        act_c1, act_c2, act_c3 = st.columns(3)
        with act_c1:
            if active_att["status"] in ("Pending Approval", "Detected"):
                if st.button("Approve File", key=f"insp_app_{active_att['id']}", type="primary", use_container_width=True):
                    res = ORGANIZER.organize_attachment(
                        attachment_id=active_att["id"],
                        destination_folder=rule_match["destination"],
                        proposed_filename=rule_match["proposed_filename"],
                        duplicate_action="keep_copy",
                    )
                    if res["success"]:
                        st.success(f"Organized successfully.")
                        st.rerun()
            elif active_att["status"] == "Organized":
                if st.button("Undo / Restore", key=f"insp_undo_{active_att['id']}", use_container_width=True):
                    res = UNDO_MANAGER.undo_operation(active_att["id"])
                    if res["success"]:
                        st.success(res["message"])
                        st.rerun()

        with act_c2:
            if active_att["status"] in ("Pending Approval", "Detected"):
                if st.button("Skip File", key=f"insp_skip_{active_att['id']}", use_container_width=True):
                    ORGANIZER.organize_attachment(
                        attachment_id=active_att["id"],
                        destination_folder="Unclassified",
                        proposed_filename="skipped.dat",
                        duplicate_action="skip",
                    )
                    st.info("Skipped file.")
                    st.rerun()
            elif active_att["status"] == "Failed":
                if st.button("Retry Filing", key=f"insp_retry_{active_att['id']}", type="primary", use_container_width=True):
                    res = ORGANIZER.organize_attachment(
                        attachment_id=active_att["id"],
                        destination_folder=rule_match["destination"],
                        proposed_filename=rule_match["proposed_filename"],
                    )
                    if res["success"]:
                        st.success("Filing succeeded.")
                        st.rerun()

        with act_c3:
            st.markdown(f"<div style='text-align:right;'>{render_status_badge(active_att['status'])}</div>", unsafe_allow_html=True)

        # Tabbed Inspector: Details & Modify & Preview
        t_meta, t_edit, t_prev = st.tabs(["Details", "Modify & Route", "File Preview"])

        with t_meta:
            st.markdown(
                f"""
                <div class="station-card">
                    <div style="font-size:14px; font-weight:700; color:#252B29; margin-bottom:6px;">
                        {active_att['original_filename']}
                    </div>
                    <div style="font-size:12px; color:#737C78; line-height:1.6;">
                        <div>Sender: <b style="color:#252B29;">{active_att.get('sender_email') or active_att.get('sender')}</b></div>
                        <div>Subject: <b style="color:#252B29;">{active_att.get('subject') or '(No Subject)'}</b></div>
                        <div>Received: <span style="color:#252B29;">{str(active_att.get('received_at'))[:19]}</span></div>
                        <div>File Size: <span style="color:#252B29;">{active_att['file_size']/1024:.1f} KB ({active_att['file_size']} bytes)</span></div>
                        <div>MIME Type: <code>{active_att.get('mime_type')}</code></div>
                        <div>SHA-256: <code class="hash-pill">{active_att['sha256']}</code></div>
                    </div>
                    <div style="border-top:1px solid #E1E5E2; margin-top:8px; padding-top:8px; font-size:12px;">
                        <div>Category: <b style="color:#356B59;">{active_att.get('category')}</b></div>
                        <div>Reason: <i>{active_att.get('classification_reason')}</i></div>
                        <div>Method: <span>{active_att.get('classification_method')}</span></div>
                        <div>Duplicate Status: <b>{dup_info['status']}</b></div>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        with t_edit:
            with st.form(key=f"edit_att_form_{active_att['id']}"):
                st.markdown("##### Manual Override")
                cat_idx = CONFIG.CATEGORIES.index(active_att["category"]) if active_att["category"] in CONFIG.CATEGORIES else 0
                new_cat = st.selectbox("Category", options=CONFIG.CATEGORIES, index=cat_idx)
                new_dest = st.text_input("Destination Folder", value=rule_match["destination"])
                new_fname = st.text_input("Final Filename", value=rule_match["proposed_filename"])

                dup_act = st.selectbox(
                    "Duplicate Handling Strategy",
                    options=["keep_copy", "skip", "keep_reference"],
                    format_func=lambda x: {
                        "keep_copy": "Keep New Copy (Auto-number if conflict)",
                        "skip": "Skip Duplicate (Do not copy)",
                        "keep_reference": "Link Reference to Existing File",
                    }[x],
                )

                submit_edit = st.form_submit_button("Save & Organize File", type="primary")

                if submit_edit:
                    if new_cat != active_att["category"]:
                        DB.log_feedback(active_att["id"], active_att["category"], new_cat)
                        DB.update_attachment_category(active_att["id"], new_cat)

                    res = ORGANIZER.organize_attachment(
                        attachment_id=active_att["id"],
                        destination_folder=new_dest,
                        proposed_filename=new_fname,
                        duplicate_action=dup_act,
                        reference_path=active_att.get("current_path"),
                    )
                    if res["success"]:
                        st.success(res["message"])
                        st.rerun()
                    else:
                        st.error(res.get("error", "Organization failed"))

        with t_prev:
            render_attachment_preview(active_att)
