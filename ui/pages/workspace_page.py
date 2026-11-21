"""
ATTACHORA Attachment Queue Page
Two-column workstation layout matching the reference image:
- 72% Attachment Queue workspace with operational summary, search/filters, bulk action bar,
  and compact structured data table with pagination.
- 28% Selected Attachment Inspector with file header, Overview/Preview/Routing tabs,
  miniature document preview card, filing decision keys, and action buttons.
- Bottom status bar.
"""

from datetime import datetime
import math
from pathlib import Path
import streamlit as st
from src.config import CONFIG
from src.database.db_manager import DB
from src.rules_engine.rule_evaluator import match_filing_rules
from src.storage_manager.duplicate_detector import DuplicateDetector
from src.storage_manager.organizer import ORGANIZER
from src.storage_manager.undo_manager import UNDO_MANAGER
from ui.components.preview_panel import render_attachment_preview, render_mini_doc_sheet
from ui.components.search_toolbar import render_bulk_toolbar, render_search_and_filters
from ui.theme import get_filetype_badge_html, render_status_pill


def format_dt_two_lines(dt_val) -> tuple[str, str]:
    """Formats an ISO timestamp into two lines: '21 Nov 2026' and '10:15 AM'."""
    if not dt_val:
        return ("21 Nov 2026", "10:15 AM")
    try:
        dt_str = str(dt_val).replace("T", " ")
        parts = dt_str.split(" ")
        date_part = parts[0]
        time_part = parts[1][:5] if len(parts) > 1 else "10:15"
        d_obj = datetime.strptime(date_part, "%Y-%m-%d")
        d_formatted = d_obj.strftime("%d %b %Y")
        t_obj = datetime.strptime(time_part, "%H:%M")
        t_formatted = t_obj.strftime("%I:%M %p")
        return (d_formatted, t_formatted)
    except Exception:
        return (str(dt_val)[:10], "10:15 AM")


def render_workspace_page():
    # ------------------ 1. PAGE HEADING & LAST SCAN ------------------
    head_c1, head_c2 = st.columns([7, 3])
    with head_c1:
        st.markdown(
            """
            <div style="margin-bottom: 12px;">
                <h1 style="font-size:22px; font-weight:700; color:#202824; margin:0 0 4px 0; letter-spacing:-0.01em;">
                    Attachment queue
                </h1>
                <div style="font-size:13px; color:#66716B;">
                    Review, classify and file incoming documents.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with head_c2:
        sync_history = DB.get_sync_history(limit=1)
        last_scan_time = "10:42 AM"
        if sync_history and sync_history[0].get("completed_at"):
            _, last_scan_time = format_dt_two_lines(sync_history[0]["completed_at"])

        st.markdown(
            f"""
            <div style="text-align:right; font-size:12px; color:#66716B; padding-top:6px;">
                <span style="font-size:14px; vertical-align:middle; margin-right:4px;">🕒</span>
                <span>Last scan {last_scan_time}</span>
            </div>
            """,
            unsafe_allow_html=True,
        )

    # ------------------ 2. OPERATIONAL SUMMARY STRIP ------------------
    # Query real database records to compute summary values
    all_attachments = DB.get_attachments_workspace()
    total_detected = len(all_attachments)

    awaiting_review = sum(1 for a in all_attachments if a.get("status") in ("Pending Approval", "Detected"))
    ready_to_file = sum(1 for a in all_attachments if a.get("status") == "Organized" or (a.get("status") in ("Pending Approval", "Detected") and a.get("confidence", 0) >= 0.85))
    duplicates_count = sum(1 for a in all_attachments if a.get("status") == "Duplicate")
    need_attention = sum(1 for a in all_attachments if a.get("status") == "Failed" or a.get("category") == "Other / Unclassified")

    st.markdown(
        f"""
        <div class="operational-summary-strip">
            <div class="summary-item">
                <span class="summary-val" style="color:#286B50;">{awaiting_review}</span>
                <span class="summary-lbl">Awaiting review</span>
            </div>
            <div class="summary-divider"></div>
            <div class="summary-item">
                <span class="summary-val" style="color:#278253;">{ready_to_file}</span>
                <span class="summary-lbl">Ready to file</span>
            </div>
            <div class="summary-divider"></div>
            <div class="summary-item">
                <span class="summary-val" style="color:#B77925;">{duplicates_count}</span>
                <span class="summary-lbl">Duplicates</span>
            </div>
            <div class="summary-divider"></div>
            <div class="summary-item">
                <span class="summary-val" style="color:#BD4545;">{need_attention}</span>
                <span class="summary-lbl">Need attention</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # ------------------ 3. TWO-COLUMN LAYOUT (72% / 28%) ------------------
    col_workspace, col_inspector = st.columns([72, 28])

    # ------------------ LEFT COLUMN: ATTACHMENT QUEUE (72%) ------------------
    with col_workspace:
        # Distinct senders for filter dropdown
        distinct_senders = sorted(list({a.get("sender_email") or a.get("sender") for a in all_attachments if a.get("sender_email") or a.get("sender")}))

        # 3.1 Search & Filter Toolbar
        filters = render_search_and_filters(senders_list=distinct_senders)

        # Filter query against database
        filtered_attachments = DB.get_attachments_workspace(
            search_query=filters["search_query"],
            category=filters["category"],
            status=filters["status"],
            extension=filters["extension"],
            sender=filters["sender"],
        )

        # Selection state
        if "selected_att_ids" not in st.session_state:
            st.session_state["selected_att_ids"] = set()

        selected_ids = list(st.session_state["selected_att_ids"])
        selected_count = len(selected_ids)

        # Bulk Actions Handlers
        def handle_bulk_approve():
            rules = DB.get_rules(enabled_only=True)
            cnt = 0
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
                    cnt += 1
            st.session_state["selected_att_ids"] = set()
            st.success(f"Organized and filed {cnt} approved documents.")
            st.rerun()

        def handle_bulk_skip():
            for att_id in selected_ids:
                ORGANIZER.organize_attachment(
                    attachment_id=att_id,
                    destination_folder="Unclassified",
                    proposed_filename="skipped.dat",
                    duplicate_action="skip",
                )
            st.session_state["selected_att_ids"] = set()
            st.info(f"Skipped {len(selected_ids)} documents.")
            st.rerun()

        def handle_bulk_clear():
            st.session_state["selected_att_ids"] = set()
            st.rerun()

        # 3.2 Bulk Action Toolbar
        render_bulk_toolbar(
            selected_count=selected_count,
            on_approve=handle_bulk_approve,
            on_skip=handle_bulk_skip,
            on_clear=handle_bulk_clear,
        )

        # 3.3 Pagination Setup (6 items per page matching reference image)
        page_size = 6
        total_items = len(filtered_attachments)
        total_pages = max(1, math.ceil(total_items / page_size))

        if "workspace_page_num" not in st.session_state:
            st.session_state["workspace_page_num"] = 1

        curr_page = min(st.session_state["workspace_page_num"], total_pages)
        start_idx = (curr_page - 1) * page_size
        end_idx = min(total_items, start_idx + page_size)
        page_items = filtered_attachments[start_idx:end_idx]

        # Active Inspector Selection
        if "selected_row_att_id" not in st.session_state or not st.session_state["selected_row_att_id"]:
            if filtered_attachments:
                st.session_state["selected_row_att_id"] = filtered_attachments[0]["id"]
            else:
                st.session_state["selected_row_att_id"] = None

        active_id = st.session_state["selected_row_att_id"]

        # 3.4 Attachment Data Table Container
        st.markdown('<div class="attachora-table-container">', unsafe_allow_html=True)

        # Table Header Row
        th0, th1, th2, th3, th4, th5, th6 = st.columns([0.4, 2.7, 2.4, 1.3, 1.6, 2.0, 1.0])
        with th0:
            all_on_page_checked = bool(page_items and all(a["id"] in st.session_state["selected_att_ids"] for a in page_items))
            chk_all = st.checkbox("All", value=all_on_page_checked, key=f"tbl_hdr_chk_{curr_page}", label_visibility="collapsed")
            if chk_all and not all_on_page_checked:
                for a in page_items:
                    st.session_state["selected_att_ids"].add(a["id"])
                st.rerun()
            elif not chk_all and all_on_page_checked:
                for a in page_items:
                    st.session_state["selected_att_ids"].discard(a["id"])
                st.rerun()

        with th1:
            st.markdown("<div class=\"attachora-table-header-row\" style=\"border:none; padding:0;\">ATTACHMENT</div>", unsafe_allow_html=True)
        with th2:
            st.markdown("<div class=\"attachora-table-header-row\" style=\"border:none; padding:0;\">SENDER / SUBJECT</div>", unsafe_allow_html=True)
        with th3:
            st.markdown("<div class=\"attachora-table-header-row\" style=\"border:none; padding:0;\">RECEIVED</div>", unsafe_allow_html=True)
        with th4:
            st.markdown("<div class=\"attachora-table-header-row\" style=\"border:none; padding:0;\">CATEGORY</div>", unsafe_allow_html=True)
        with th5:
            st.markdown("<div class=\"attachora-table-header-row\" style=\"border:none; padding:0;\">DESTINATION</div>", unsafe_allow_html=True)
        with th6:
            st.markdown("<div class=\"attachora-table-header-row\" style=\"border:none; padding:0;\">STATUS</div>", unsafe_allow_html=True)

        rules = DB.get_rules(enabled_only=True)

        # Empty State
        if not page_items:
            st.markdown(
                """
                <div style="text-align:center; padding:32px 16px; color:#66716B; font-size:13px;">
                    No attachment records match the current search or filter criteria.
                </div>
                """,
                unsafe_allow_html=True,
            )
        else:
            # Render Table Rows
            for att in page_items:
                att_id = att["id"]
                is_active = (att_id == active_id)
                is_checked = (att_id in st.session_state["selected_att_ids"])

                rule_match = match_filing_rules(rules, att, {"sender": att.get("sender"), "received_at": att.get("received_at")})
                dest_path = f"/{rule_match['destination']}" if not rule_match["destination"].startswith("/") else rule_match["destination"]

                date_line, time_line = format_dt_two_lines(att.get("received_at"))
                sender_str = att.get("sender_email") or att.get("sender") or "unknown@company.com"
                subject_str = att.get("subject") or "No Subject"

                # Row styling
                row_cls = "attachora-table-row selected" if (is_active or is_checked) else "attachora-table-row"

                st.markdown(f'<div class="{row_cls}">', unsafe_allow_html=True)
                rc0, rc1, rc2, rc3, rc4, rc5, rc6 = st.columns([0.4, 2.7, 2.4, 1.3, 1.6, 2.0, 1.0])

                with rc0:
                    chk = st.checkbox("Select row", value=is_checked, key=f"row_chk_{att_id}", label_visibility="collapsed")
                    if chk and not is_checked:
                        st.session_state["selected_att_ids"].add(att_id)
                        st.session_state["selected_row_att_id"] = att_id
                        st.rerun()
                    elif not chk and is_checked:
                        st.session_state["selected_att_ids"].discard(att_id)
                        st.rerun()

                with rc1:
                    badge_html = get_filetype_badge_html(att["original_filename"], att.get("extension", ""))
                    # Render badge and interactive filename button
                    bc_a, bc_b = st.columns([0.8, 3.2])
                    with bc_a:
                        st.markdown(badge_html, unsafe_allow_html=True)
                    with bc_b:
                        disp_fn = att["original_filename"]
                        if len(disp_fn) > 24:
                            disp_fn = disp_fn[:21] + "..."
                        if st.button(disp_fn, key=f"fn_btn_{att_id}", help=att["original_filename"]):
                            st.session_state["selected_row_att_id"] = att_id
                            st.rerun()

                with rc2:
                    st.markdown(
                        f"""
                        <div style="line-height:1.35; padding-top:2px;">
                            <div style="font-weight:600; font-size:12px; color:#202824; overflow:hidden; text-overflow:ellipsis; white-space:nowrap;" title="{sender_str}">{sender_str}</div>
                            <div style="font-size:11px; color:#66716B; overflow:hidden; text-overflow:ellipsis; white-space:nowrap;" title="{subject_str}">{subject_str}</div>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )

                with rc3:
                    st.markdown(
                        f"""
                        <div style="line-height:1.35; padding-top:2px;">
                            <div style="font-size:12px; color:#202824;">{date_line}</div>
                            <div style="font-size:11px; color:#66716B;">{time_line}</div>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )

                with rc4:
                    cat_val = att.get("category", "Documents")
                    st.markdown(
                        f"""
                        <div style="font-size:12px; color:#202824; font-weight:500; padding-top:6px;">
                            {cat_val}
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )

                with rc5:
                    st.markdown(
                        f"""
                        <div style="font-size:12px; color:#66716B; font-family:'JetBrains Mono',monospace; overflow:hidden; text-overflow:ellipsis; white-space:nowrap; padding-top:6px;" title="{dest_path}">
                            {dest_path}
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )

                with rc6:
                    st.markdown(
                        f"""
                        <div style="padding-top:4px;">
                            {render_status_pill(att.get('status'))}
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )

                st.markdown('</div>', unsafe_allow_html=True)

        st.markdown('</div>', unsafe_allow_html=True)

        # 3.5 Pagination Controls Footer
        pg_c1, pg_c2 = st.columns([6, 4])
        with pg_c1:
            st.markdown(
                f"""
                <div style="font-size:12px; color:#66716B; padding-top:8px;">
                    Showing <b>{start_idx + 1}–{end_idx}</b> of <b>{total_items}</b> results
                </div>
                """,
                unsafe_allow_html=True,
            )

        with pg_c2:
            # Render pagination buttons `< 1 2 3 4 >`
            btn_cols = st.columns(min(7, total_pages + 2))
            with btn_cols[0]:
                if st.button("<", key="pg_prev_btn", disabled=(curr_page <= 1), use_container_width=True):
                    st.session_state["workspace_page_num"] = max(1, curr_page - 1)
                    st.rerun()

            for p_idx in range(1, total_pages + 1):
                if p_idx < len(btn_cols) - 1:
                    with btn_cols[p_idx]:
                        p_type = "primary" if p_idx == curr_page else "secondary"
                        if st.button(str(p_idx), key=f"pg_btn_{p_idx}", type=p_type, use_container_width=True):
                            st.session_state["workspace_page_num"] = p_idx
                            st.rerun()

            with btn_cols[-1]:
                if st.button(">", key="pg_next_btn", disabled=(curr_page >= total_pages), use_container_width=True):
                    st.session_state["workspace_page_num"] = min(total_pages, curr_page + 1)
                    st.rerun()

    # ------------------ RIGHT COLUMN: ATTACHMENT INSPECTOR (28%) ------------------
    with col_inspector:
        st.markdown('<div class="inspector-card">', unsafe_allow_html=True)

        active_att = DB.get_attachment_by_id(active_id) if active_id else None

        if not active_att:
            st.markdown(
                """
                <div class="inspector-title">Selected attachment</div>
                <div style="text-align:center; padding:40px 10px; color:#66716B; font-size:13px;">
                    Select an attachment from the queue on the left to inspect metadata, view previews, and route files.
                </div>
                """,
                unsafe_allow_html=True,
            )
            st.markdown('</div>', unsafe_allow_html=True)
        else:
            # Header matching reference image
            ext_label = (active_att.get("extension") or "pdf").upper()
            badge_color = "#D32F2F" if ext_label == "PDF" else ("#1976D2" if ext_label in ("DOCX", "DOC") else "#286B50")
            size_kb = int(active_att.get("file_size", 0) / 1024)
            rec_date, _ = format_dt_two_lines(active_att.get("received_at"))

            st.markdown(
                f"""
                <div class="inspector-title">Selected attachment</div>
                <div class="inspector-file-header">
                    <div class="inspector-file-badge" style="background-color:{badge_color};">
                        {ext_label[:3]}
                    </div>
                    <div>
                        <div class="inspector-filename">{active_att['original_filename']}</div>
                        <div class="inspector-meta">{ext_label} · {size_kb} KB · Received {rec_date}</div>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

            # Three Tabs: Overview | Preview | Routing
            tab_overview, tab_preview, tab_routing = st.tabs(["Overview", "Preview", "Routing"])

            # ------------------ TAB 1: OVERVIEW ------------------
            with tab_overview:
                # 1. Mini Document Preview Card
                render_mini_doc_sheet(active_att)

                # 2. Filing Decision Section
                dup_detector = DuplicateDetector(DB)
                dup_info = dup_detector.inspect_duplicate(
                    sha256=active_att["sha256"],
                    filename=active_att["original_filename"],
                    exclude_attachment_id=active_att["id"],
                )
                rule_match = match_filing_rules(rules, active_att, {"sender": active_att.get("sender"), "received_at": active_att.get("received_at")})
                dest_full = f"/{rule_match['destination']}" if not rule_match["destination"].startswith("/") else rule_match["destination"]

                st.markdown(
                    f"""
                    <div class="filing-decision-header">Filing decision</div>
                    <div class="filing-decision-row">
                        <span class="filing-decision-lbl">Category:</span>
                        <span style="background-color:#E9F2EC; color:#286B50; font-weight:600; padding:2px 8px; border-radius:4px; font-size:11px;">
                            {active_att.get('category')}
                        </span>
                    </div>
                    <div class="filing-decision-row">
                        <span class="filing-decision-lbl">Destination:</span>
                        <span class="filing-decision-val" style="font-family:'JetBrains Mono',monospace; font-size:11px;">{dest_full}</span>
                    </div>
                    <div class="filing-decision-row">
                        <span class="filing-decision-lbl">Rule match:</span>
                        <span class="filing-decision-val">{rule_match['rule_name']}</span>
                    </div>
                    <div class="filing-decision-row">
                        <span class="filing-decision-lbl">Duplicate check:</span>
                        <span class="filing-decision-val">{dup_info['status']}</span>
                    </div>
                    <div style="margin-top:6px; margin-bottom:14px;">
                        <span class="filing-decision-lbl" style="font-size:11px;">SHA-256:</span>
                        <div class="hash-pill" style="margin-top:3px;">{active_att['sha256']}</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

            # ------------------ TAB 2: PREVIEW ------------------
            with tab_preview:
                render_attachment_preview(active_att)

            # ------------------ TAB 3: ROUTING ------------------
            with tab_routing:
                with st.form(key=f"inspector_route_form_{active_att['id']}"):
                    st.markdown("<b>Override Classification & Destination</b>", unsafe_allow_html=True)
                    cat_idx = CONFIG.CATEGORIES.index(active_att["category"]) if active_att["category"] in CONFIG.CATEGORIES else 0
                    new_category = st.selectbox("Category", options=CONFIG.CATEGORIES, index=cat_idx)
                    new_destination = st.text_input("Destination Path", value=rule_match["destination"])
                    new_filename = st.text_input("Target Filename", value=rule_match["proposed_filename"])

                    dup_strategy = st.selectbox(
                        "Duplicate Strategy",
                        options=["keep_copy", "skip", "keep_reference"],
                        format_func=lambda x: {
                            "keep_copy": "Keep New Copy (Auto-number if conflict)",
                            "skip": "Skip Duplicate (Do not file)",
                            "keep_reference": "Link Reference to Existing File",
                        }[x],
                    )

                    save_routing = st.form_submit_button("Save & File Document", type="primary")

                    if save_routing:
                        if new_category != active_att["category"]:
                            DB.log_feedback(active_att["id"], active_att["category"], new_category)
                            DB.update_attachment_category(active_att["id"], new_category)

                        res = ORGANIZER.organize_attachment(
                            attachment_id=active_att["id"],
                            destination_folder=new_destination,
                            proposed_filename=new_filename,
                            duplicate_action=dup_strategy,
                            reference_path=active_att.get("current_path"),
                        )
                        if res["success"]:
                            st.success(res["message"])
                            st.rerun()
                        else:
                            st.error(res.get("error", "Filing failed"))

            # Bottom Action Buttons matching reference image: [Edit destination] and [Approve file]
            st.markdown("<div style='margin-top:16px;'></div>", unsafe_allow_html=True)
            insp_btn_c1, insp_btn_c2 = st.columns(2)
            with insp_btn_c1:
                if st.button("Edit destination", key=f"btn_edit_dest_{active_att['id']}", use_container_width=True):
                    st.info("Switch to the 'Routing' tab above to customize category and destination.")
            with insp_btn_c2:
                btn_label = "Approve file" if active_att.get("status") != "Organized" else "Re-file"
                if st.button(btn_label, key=f"btn_approve_single_{active_att['id']}", type="primary", use_container_width=True):
                    res = ORGANIZER.organize_attachment(
                        attachment_id=active_att["id"],
                        destination_folder=rule_match["destination"],
                        proposed_filename=rule_match["proposed_filename"],
                        duplicate_action="keep_copy",
                    )
                    if res["success"]:
                        st.success(f"Organized {active_att['original_filename']}")
                        st.rerun()
                    else:
                        st.error(res.get("error", "Filing failed"))

            # Undo option if already organized
            if active_att.get("status") == "Organized":
                if st.button("Undo / Restore to Staging", key=f"btn_undo_single_{active_att['id']}", use_container_width=True):
                    undo_res = UNDO_MANAGER.undo_operation(active_att["id"])
                    if undo_res["success"]:
                        st.success(undo_res["message"])
                        st.rerun()

        st.markdown('</div>', unsafe_allow_html=True)

    # ------------------ 4. BOTTOM STATUS BAR ------------------
    st.markdown(
        f"""
        <div style="display:flex; align-items:center; gap:8px; font-size:12px; color:#66716B; padding-top:16px; border-top:1px solid #DCE3DE; margin-top:20px;">
            <span style="color:#278253; font-weight:700;">✓</span>
            <span>Local storage · <b>{total_detected}</b> attachments indexed · All changes saved</span>
        </div>
        """,
        unsafe_allow_html=True,
    )
