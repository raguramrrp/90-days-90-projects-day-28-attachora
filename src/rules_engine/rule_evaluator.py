"""
ATTACHORA Rule Evaluator
Evaluates smart filing rules containing AND/OR condition groups against attachment
and email metadata in order of priority.
"""

from datetime import datetime
import json
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
from src.rules_engine.template_engine import (
    extract_sender_domain,
    render_filename_template,
)


def _evaluate_condition(
    condition: Dict[str, Any],
    attachment: Dict[str, Any],
    email: Dict[str, Any],
) -> bool:
    """Evaluates a single rule condition against attachment and email fields."""
    field = condition.get("field", "").lower()
    op = condition.get("operator", "equals").lower()
    target_val = condition.get("value")

    # Resolve context value
    if field == "sender_email":
        val = (email.get("sender_email") or email.get("sender") or "").lower()
    elif field == "sender_domain":
        val = extract_sender_domain(email.get("sender_email") or email.get("sender") or "")
    elif field == "subject":
        val = (email.get("subject") or "").lower()
    elif field == "filename":
        val = (attachment.get("original_filename") or "").lower()
    elif field in ("extension", "ext"):
        val = (attachment.get("extension") or "").lower().lstrip(".")
    elif field == "mime_type":
        val = (attachment.get("mime_type") or "").lower()
    elif field == "category":
        val = (attachment.get("category") or "").lower()
    elif field == "file_size":
        val = int(attachment.get("file_size") or 0)
    elif field == "received_date":
        val = str(email.get("received_at") or "")
    else:
        return False

    # String normalization for comparison
    str_target = str(target_val).lower() if target_val is not None else ""

    # Operators
    if op == "equals":
        if isinstance(val, int):
            try:
                return val == int(target_val)
            except Exception:
                return False
        return str(val) == str_target

    elif op == "contains":
        return str_target in str(val)

    elif op == "starts_with":
        return str(val).startswith(str_target)

    elif op == "ends_with":
        return str(val).endswith(str_target)

    elif op in ("in", "in_list"):
        # e.g. target_val is "pdf, docx, txt"
        parts = [p.strip().lower() for p in str_target.replace(";", ",").split(",")]
        return str(val) in parts

    elif op == "greater_than":
        try:
            return float(val) > float(target_val)
        except Exception:
            return False

    elif op == "less_than":
        try:
            return float(val) < float(target_val)
        except Exception:
            return False

    elif op == "after":
        try:
            dt_val = datetime.fromisoformat(str(val)[:10])
            dt_tgt = datetime.fromisoformat(str(target_val)[:10])
            return dt_val > dt_tgt
        except Exception:
            return False

    elif op == "before":
        try:
            dt_val = datetime.fromisoformat(str(val)[:10])
            dt_tgt = datetime.fromisoformat(str(target_val)[:10])
            return dt_val < dt_tgt
        except Exception:
            return False

    return False


def evaluate_rule_group(
    conditions_data: Dict[str, Any],
    attachment: Dict[str, Any],
    email: Dict[str, Any],
) -> bool:
    """Evaluates an AND/OR group of conditions."""
    logic = conditions_data.get("logic", "AND").upper()
    rules = conditions_data.get("rules", [])

    if not rules:
        return False

    results = [_evaluate_condition(cond, attachment, email) for cond in rules]

    if logic == "AND":
        return all(results)
    elif logic == "OR":
        return any(results)
    return False


def match_filing_rules(
    rules: List[Dict[str, Any]],
    attachment: Dict[str, Any],
    email: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """Evaluates all enabled rules in priority order.

    Returns match details including matched rule name, destination folder, and proposed filename.
    """
    email_data = email or {}

    for rule in rules:
        if not rule.get("enabled", 1):
            continue

        cond_spec = rule.get("conditions")
        if not cond_spec and isinstance(rule.get("conditions_json"), str):
            try:
                cond_spec = json.loads(rule["conditions_json"])
            except Exception:
                cond_spec = {}

        if not cond_spec:
            continue

        if evaluate_rule_group(cond_spec, attachment, email_data):
            destination = rule.get("destination", "Documents")
            template = rule.get("filename_template", "{original_filename}")
            proposed_name = render_filename_template(template, attachment, email_data)

            return {
                "matched": True,
                "rule_id": rule.get("id"),
                "rule_name": rule.get("rule_name"),
                "priority": rule.get("priority", 10),
                "destination": destination,
                "proposed_filename": proposed_name,
                "reason": f"Matched Rule '{rule.get('rule_name')}' (Priority {rule.get('priority', 10)})",
            }

    # Fallback when no rule matches
    category = attachment.get("category", "Other / Unclassified")
    default_dest = f"Unclassified/{category.replace(' ', '_').replace('/', '-')}"
    default_name = render_filename_template("{original_filename}", attachment, email_data)

    return {
        "matched": False,
        "rule_id": None,
        "rule_name": "Default Unclassified Fallback",
        "priority": 999,
        "destination": default_dest,
        "proposed_filename": default_name,
        "reason": "No enabled custom filing rule matched attachment criteria",
    }
