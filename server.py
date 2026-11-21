"""
ATTACHORA Workstation API & Application Server
Serves the unified REST API connecting the React frontend directly to the existing
Python backend (SQLite DB, Rule Evaluator, File Organizer, IMAP Reader, and Reporter).
"""

from datetime import datetime
import base64
import json
import math
import os
from pathlib import Path
from typing import Any, Dict, List
from starlette.applications import Starlette
from starlette.middleware import Middleware
from starlette.middleware.cors import CORSMiddleware
from starlette.responses import FileResponse, JSONResponse, Response
from starlette.routing import Mount, Route
from starlette.staticfiles import StaticFiles
import uvicorn
from src.analytics.reporter import REPORTER
from src.config import CONFIG
from src.database.db_manager import DB
from src.email_engine.imap_client import IMAPClient, IMAPConnectionError
from src.email_engine.reader import READER, VAULT
from src.rules_engine.rule_evaluator import match_filing_rules
from src.security.sanitizer import sanitize_filename
from src.storage_manager.duplicate_detector import DuplicateDetector
from src.storage_manager.organizer import ORGANIZER
from src.storage_manager.undo_manager import UNDO_MANAGER

BASE_DIR = Path(__file__).resolve().parent
FRONTEND_DIST = BASE_DIR / "frontend" / "dist"


# ------------------ API HANDLERS ------------------

async def get_summary(request):
    """Calculates operational summary strip counts and storage metrics."""
    all_attachments = DB.get_attachments_workspace()
    total_detected = len(all_attachments)

    awaiting_review = sum(1 for a in all_attachments if a.get("status") in ("Pending Approval", "Detected"))
    ready_to_file = sum(1 for a in all_attachments if a.get("status") == "Organized" or (a.get("status") in ("Pending Approval", "Detected") and a.get("confidence", 0) >= 0.85))
    duplicates_count = sum(1 for a in all_attachments if a.get("status") == "Duplicate")
    need_attention = sum(1 for a in all_attachments if a.get("status") == "Failed" or a.get("category") == "Other / Unclassified")

    metrics = REPORTER.get_summary_metrics()

    sync_history = DB.get_sync_history(limit=1)
    last_scan = "10:42 AM"
    if sync_history and sync_history[0].get("completed_at"):
        try:
            ts = str(sync_history[0]["completed_at"]).replace("T", " ")
            t_obj = datetime.strptime(ts.split(" ")[1][:5], "%H:%M")
            last_scan = t_obj.strftime("%I:%M %p")
        except Exception:
            pass

    return JSONResponse({
        "awaiting_review": awaiting_review,
        "ready_to_file": ready_to_file,
        "duplicates_count": duplicates_count,
        "need_attention": need_attention,
        "total_detected": total_detected,
        "total_organized": metrics["total_organized"],
        "storage_organized_mb": metrics["total_storage_organized_mb"],
        "storage_saved_mb": metrics["storage_saved_mb"],
        "last_scan": last_scan,
    })


async def get_attachments(request):
    """Returns filtered and sorted attachment list with filing decisions and duplicate statuses."""
    params = request.query_params
    search_q = params.get("search", "")
    category = params.get("category", "All")
    status = params.get("status", "All")
    extension = params.get("extension", "All")
    sender = params.get("sender", "All")

    attachments = DB.get_attachments_workspace(
        search_query=search_q,
        category=category,
        status=status,
        extension=extension,
        sender=sender,
    )

    rules = DB.get_rules(enabled_only=True)
    dup_detector = DuplicateDetector(DB)

    results = []
    for att in attachments:
        att_id = att["id"]
        rule_match = match_filing_rules(rules, att, {"sender": att.get("sender"), "received_at": att.get("received_at")})
        dup_info = dup_detector.inspect_duplicate(
            sha256=att["sha256"],
            filename=att["original_filename"],
            exclude_attachment_id=att_id,
        )

        item = dict(att)
        item["rule_match"] = rule_match
        item["duplicate_status"] = dup_info["status"]
        results.append(item)

    return JSONResponse({"attachments": results, "total": len(results)})


async def approve_attachment(request):
    """Approves a single attachment and organizes it to the target library folder."""
    att_id = int(request.path_params["id"])
    att = DB.get_attachment_by_id(att_id)
    if not att:
        return JSONResponse({"success": False, "error": f"Attachment #{att_id} not found"}, status_code=404)

    rules = DB.get_rules(enabled_only=True)
    rule_match = match_filing_rules(rules, att, {"sender": att.get("sender"), "received_at": att.get("received_at")})

    res = ORGANIZER.organize_attachment(
        attachment_id=att_id,
        destination_folder=rule_match["destination"],
        proposed_filename=rule_match["proposed_filename"],
        duplicate_action="keep_copy",
    )
    return JSONResponse(res)


async def bulk_approve(request):
    """Bulk approves a list of attachment IDs."""
    data = await request.json()
    ids = data.get("ids", [])
    rules = DB.get_rules(enabled_only=True)
    success_count = 0

    for att_id in ids:
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

    return JSONResponse({"success": True, "count": success_count})


async def bulk_skip(request):
    """Bulk skips a list of attachment IDs."""
    data = await request.json()
    ids = data.get("ids", [])
    for att_id in ids:
        ORGANIZER.organize_attachment(
            attachment_id=att_id,
            destination_folder="Unclassified",
            proposed_filename="skipped.dat",
            duplicate_action="skip",
        )
    return JSONResponse({"success": True, "count": len(ids)})


async def undo_attachment(request):
    """Reverses an organized attachment and restores payload to staging."""
    att_id = int(request.path_params["id"])
    res = UNDO_MANAGER.undo_operation(att_id)
    return JSONResponse(res)


async def override_routing(request):
    """Manually overrides category, destination path, and duplicate strategy."""
    att_id = int(request.path_params["id"])
    att = DB.get_attachment_by_id(att_id)
    if not att:
        return JSONResponse({"success": False, "error": "Not found"}, status_code=404)

    data = await request.json()
    new_cat = data.get("category", att["category"])
    new_dest = data.get("destination", "Unclassified")
    new_fname = data.get("filename", att["original_filename"])
    dup_act = data.get("duplicate_action", "keep_copy")

    if new_cat != att["category"]:
        DB.log_feedback(att_id, att["category"], new_cat)
        DB.update_attachment_category(att_id, new_cat)

    res = ORGANIZER.organize_attachment(
        attachment_id=att_id,
        destination_folder=new_dest,
        proposed_filename=new_fname,
        duplicate_action=dup_act,
        reference_path=att.get("current_path"),
    )
    return JSONResponse(res)


async def get_rules(request):
    """Returns active filing rules."""
    rules = DB.get_rules(enabled_only=False)
    return JSONResponse({"rules": rules})


async def save_rule(request):
    """Creates a new filing rule."""
    data = await request.json()
    rule_id = DB.add_rule(
        rule_name=data["rule_name"],
        conditions_json=json.dumps(data.get("conditions", {})),
        destination=data["destination"],
        filename_template=data.get("filename_template", "{date}_{category}_{original_filename}"),
        priority=int(data.get("priority", 10)),
        enabled=1,
    )
    return JSONResponse({"success": True, "rule_id": rule_id})


async def delete_rule(request):
    """Deletes a filing rule."""
    rule_id = int(request.path_params["id"])
    DB.delete_rule(rule_id)
    return JSONResponse({"success": True})


async def get_history(request):
    """Returns immutable operation audit trail."""
    params = request.query_params
    operations = DB.get_operations(
        status=params.get("status", "All"),
        operation_type=params.get("operation_type", "All"),
        search_query=params.get("search", ""),
        limit=250,
    )
    return JSONResponse({"operations": operations})


async def export_history_csv(request):
    """Exports operations as CSV."""
    csv_str = REPORTER.export_operations_csv()
    return Response(
        csv_str,
        media_type="text/csv",
        headers={"Content-Disposition": 'attachment; filename="attachora_operations_audit.csv"'},
    )


async def get_analytics(request):
    """Returns analytical metrics and chart datasets."""
    cat_df = REPORTER.get_category_distribution()
    senders_df = REPORTER.get_top_senders(limit=8)
    time_df = REPORTER.get_processing_timeline()

    return JSONResponse({
        "categories": cat_df.to_dict(orient="records") if not cat_df.empty else [],
        "senders": senders_df.to_dict(orient="records") if not senders_df.empty else [],
        "timeline": time_df.to_dict(orient="records") if not time_df.empty else [],
    })


SYSTEM_SETTINGS = {
    "auto_mode": False,
    "confidence_threshold": 0.85,
    "duplicate_policy": "keep_copy",
}


async def auto_file_ready(request):
    """Automatically files all attachments meeting the confidence threshold and not duplicate."""
    all_attachments = DB.get_attachments_workspace()
    rules = DB.get_rules(enabled_only=True)
    success_count = 0

    for att in all_attachments:
        if att.get("status") in ("Pending Approval", "Detected") and att.get("confidence", 0) >= SYSTEM_SETTINGS["confidence_threshold"]:
            att_id = att["id"]
            rule_match = match_filing_rules(rules, att, {"sender": att.get("sender"), "received_at": att.get("received_at")})
            res = ORGANIZER.organize_attachment(
                attachment_id=att_id,
                destination_folder=rule_match["destination"],
                proposed_filename=rule_match["proposed_filename"],
                duplicate_action=SYSTEM_SETTINGS["duplicate_policy"],
            )
            if res.get("success"):
                success_count += 1

    return JSONResponse({"success": True, "count": success_count})


async def get_settings(request):
    """Returns current system automation settings."""
    return JSONResponse(SYSTEM_SETTINGS)


async def save_settings(request):
    """Updates system automation settings."""
    data = await request.json()
    if "auto_mode" in data:
        SYSTEM_SETTINGS["auto_mode"] = bool(data["auto_mode"])
    if "confidence_threshold" in data:
        SYSTEM_SETTINGS["confidence_threshold"] = float(data["confidence_threshold"])
    if "duplicate_policy" in data:
        SYSTEM_SETTINGS["duplicate_policy"] = str(data["duplicate_policy"])
    return JSONResponse({"success": True, "settings": SYSTEM_SETTINGS})


async def sync_now(request):
    """Scans and imports sample email dataset. In auto mode, auto-files high confidence matches."""
    sample_dir = CONFIG.SAMPLE_EMAILS_DIR
    imported = 0
    total_atts = 0
    if sample_dir.exists():
        eml_files = sorted(list(sample_dir.glob("*.eml")))
        for eml in eml_files:
            staged = READER.import_eml_file(eml)
            imported += 1
            total_atts += len(staged)

    auto_filed = 0
    if SYSTEM_SETTINGS["auto_mode"]:
        all_attachments = DB.get_attachments_workspace()
        rules = DB.get_rules(enabled_only=True)
        for att in all_attachments:
            if att.get("status") in ("Pending Approval", "Detected") and att.get("confidence", 0) >= SYSTEM_SETTINGS["confidence_threshold"]:
                att_id = att["id"]
                rule_match = match_filing_rules(rules, att, {"sender": att.get("sender"), "received_at": att.get("received_at")})
                res = ORGANIZER.organize_attachment(
                    attachment_id=att_id,
                    destination_folder=rule_match["destination"],
                    proposed_filename=rule_match["proposed_filename"],
                    duplicate_action=SYSTEM_SETTINGS["duplicate_policy"],
                )
                if res.get("success"):
                    auto_filed += 1

    return JSONResponse({
        "success": True,
        "emails_scanned": imported,
        "attachments_detected": total_atts,
        "auto_filed": auto_filed,
    })


async def test_mailbox_connection(request):
    """Tests real IMAP server credentials and returns available folder list."""
    data = await request.json()
    host = data.get("host", "").strip()
    port = int(data.get("port", 993))
    username = data.get("username", "").strip()
    password = data.get("password", "")
    use_ssl = bool(data.get("use_ssl", True))

    if not host or not username or not password:
        return JSONResponse({"success": False, "error": "Host, username, and password / app password are required."}, status_code=400)

    try:
        client = IMAPClient(host=host, port=port, username=username, password=password, use_ssl=use_ssl)
        success, msg, mailboxes = client.test_connection()
        return JSONResponse({"success": success, "message": msg, "mailboxes": mailboxes})
    except Exception as e:
        return JSONResponse({"success": False, "error": str(e)}, status_code=400)


async def save_mailbox_account(request):
    """Saves real IMAP account profile into SQLite database and secure runtime vault."""
    data = await request.json()
    account_email = data.get("account_email", "").strip()
    imap_host = data.get("imap_host", "").strip()
    imap_port = int(data.get("imap_port", 993))
    mailbox = data.get("mailbox", "INBOX").strip()
    password = data.get("password", "")

    if not account_email or not imap_host:
        return JSONResponse({"success": False, "error": "Account email and host are required."}, status_code=400)

    acc_id = DB.add_account(
        account_email=account_email,
        imap_host=imap_host,
        imap_port=imap_port,
        mailbox=mailbox,
        auth_type="password",
    )

    if password:
        VAULT.set_memory_credential(account_email, password)

    return JSONResponse({"success": True, "account_id": acc_id})


async def get_mailbox_accounts(request):
    """Returns saved email accounts."""
    accounts = DB.get_accounts()
    return JSONResponse({"accounts": accounts})


async def sync_real_mailbox(request):
    """Performs real IMAP fetch and extraction from configured mailbox."""
    data = await request.json()
    account_id = data.get("account_id")
    password = data.get("password")

    if not account_id:
        accounts = DB.get_accounts()
        if accounts:
            account_id = accounts[0]["id"]
        else:
            return JSONResponse({"success": False, "error": "No email account configured. Please save your IMAP account first."}, status_code=400)

    res = READER.sync_imap_account(account_id=account_id, password_override=password)
    return JSONResponse(res)


async def upload_eml_file(request):
    """Accepts uploaded raw .eml file and extracts/classifies attachments."""
    data = await request.json()
    filename = data.get("filename", "uploaded_email.eml")
    eml_content_b64 = data.get("content_b64")
    if not eml_content_b64:
        return JSONResponse({"success": False, "error": "No file content provided."}, status_code=400)

    try:
        raw_bytes = base64.b64decode(eml_content_b64)
        staged = READER.import_eml_bytes(raw_bytes, filename=filename)
        return JSONResponse({
            "success": True,
            "filename": filename,
            "attachments_count": len(staged),
            "attachments": staged,
        })
    except Exception as e:
        return JSONResponse({"success": False, "error": f"Failed to parse EML: {str(e)}"}, status_code=400)


# ------------------ ROUTING SETUP ------------------

routes = [
    Route("/api/summary", get_summary, methods=["GET"]),
    Route("/api/attachments", get_attachments, methods=["GET"]),
    Route("/api/attachments/{id:int}/approve", approve_attachment, methods=["POST"]),
    Route("/api/attachments/{id:int}/undo", undo_attachment, methods=["POST"]),
    Route("/api/attachments/{id:int}/override", override_routing, methods=["POST"]),
    Route("/api/attachments/bulk-approve", bulk_approve, methods=["POST"]),
    Route("/api/attachments/bulk-skip", bulk_skip, methods=["POST"]),
    Route("/api/rules", get_rules, methods=["GET"]),
    Route("/api/rules", save_rule, methods=["POST"]),
    Route("/api/rules/{id:int}", delete_rule, methods=["DELETE"]),
    Route("/api/history", get_history, methods=["GET"]),
    Route("/api/history/export", export_history_csv, methods=["GET"]),
    Route("/api/analytics", get_analytics, methods=["GET"]),
    Route("/api/sync", sync_now, methods=["POST"]),
    Route("/api/auto-file", auto_file_ready, methods=["POST"]),
    Route("/api/settings", get_settings, methods=["GET"]),
    Route("/api/settings", save_settings, methods=["POST"]),
    Route("/api/mailbox/test", test_mailbox_connection, methods=["POST"]),
    Route("/api/mailbox/save", save_mailbox_account, methods=["POST"]),
    Route("/api/mailbox/accounts", get_mailbox_accounts, methods=["GET"]),
    Route("/api/mailbox/sync-real", sync_real_mailbox, methods=["POST"]),
    Route("/api/upload-eml", upload_eml_file, methods=["POST"]),
]

# Mount frontend static distribution if built
if FRONTEND_DIST.exists():
    routes.append(Mount("/", app=StaticFiles(directory=str(FRONTEND_DIST), html=True), name="static"))

middleware = [
    Middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_methods=["*"],
        allow_headers=["*"],
    )
]

app = Starlette(debug=False, routes=routes, middleware=middleware)

if __name__ == "__main__":
    port = int(os.getenv("PORT", "8501"))
    print(f"==============================================================================")
    print(f"[ATTACHORA] Starting Attachment Operations Workstation")
    print(f"==============================================================================")
    print(f"Local Workstation URL: http://localhost:{port}")
    print(f"Press Ctrl+C to stop the application.\n")
    uvicorn.run(app, host="127.0.0.1", port=port, log_level="warning")
