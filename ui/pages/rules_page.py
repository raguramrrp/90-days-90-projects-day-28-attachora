"""
ATTACHORA Smart Filing Rules Page
Manages configurable organization rules, condition groups (AND/OR), priority ordering,
destination directory mapping, and rule testing against active attachments.
"""

import json
import streamlit as st
from src.config import CONFIG
from src.database.db_manager import DB
from src.rules_engine.rule_evaluator import match_filing_rules


def render_rules_page():
    st.subheader("Smart Filing Rule Engine")
    st.caption("Define deterministic routing rules, destination directories, and filename templates evaluated in strict priority sequence.")

    tab1, tab2, tab3 = st.tabs(["Active Filing Rules", "Create Custom Rule", "Rule Tester"])

    # ------------------ TAB 1: ACTIVE RULES ------------------
    with tab1:
        rules = DB.get_rules(enabled_only=False)

        if not rules:
            st.info("No filing rules defined.")
        else:
            for rule in rules:
                rule_id = rule["id"]
                is_enabled = bool(rule.get("enabled", 1))

                with st.expander(f"Priority #{rule.get('priority')}: {rule['rule_name']} ({'Active' if is_enabled else 'Disabled'})", expanded=False):
                    c1, c2, c3 = st.columns([3, 2, 2])
                    with c1:
                        st.markdown(f"**Target Destination:** `{rule.get('destination')}`")
                        st.markdown(f"**Filename Template:** `{rule.get('filename_template')}`")

                    with c2:
                        st.caption("Condition Group:")
                        st.code(rule.get("conditions_json", "{}"), language="json")

                    with c3:
                        # Toggle enable/disable
                        new_state = st.checkbox("Enabled", value=is_enabled, key=f"enable_rule_{rule_id}")
                        if new_state != is_enabled:
                            DB.update_rule(
                                rule_id=rule_id,
                                rule_name=rule["rule_name"],
                                conditions_json=rule["conditions_json"],
                                destination=rule["destination"],
                                filename_template=rule["filename_template"],
                                priority=rule["priority"],
                                enabled=1 if new_state else 0,
                            )
                            st.rerun()

                        # Priority adjustment
                        new_prio = st.number_input("Priority Order", min_value=1, max_value=100, value=rule.get("priority", 10), key=f"prio_rule_{rule_id}")
                        if new_prio != rule.get("priority"):
                            DB.update_rule(
                                rule_id=rule_id,
                                rule_name=rule["rule_name"],
                                conditions_json=rule["conditions_json"],
                                destination=rule["destination"],
                                filename_template=rule["filename_template"],
                                priority=int(new_prio),
                                enabled=rule["enabled"],
                            )
                            st.rerun()

                        if st.button("Delete Rule", key=f"del_rule_{rule_id}", type="secondary"):
                            DB.delete_rule(rule_id)
                            st.success(f"Rule '{rule['rule_name']}' deleted.")
                            st.rerun()

    # ------------------ TAB 2: CREATE RULE ------------------
    with tab2:
        st.markdown("#### Create New Filing Rule")

        with st.form("create_rule_form"):
            c_name, c_prio = st.columns([3, 1])
            with c_name:
                rule_name = st.text_input("Rule Name", placeholder="e.g. Stripe Receipts to Invoices")
            with c_prio:
                rule_priority = st.number_input("Priority Rank", min_value=1, max_value=99, value=10)

            c_dest, c_tmpl = st.columns(2)
            with c_dest:
                destination = st.text_input("Destination Folder Path", value="Finance/Invoices", help="Subfolder within ATTACHORA_LIBRARY")
            with c_tmpl:
                fn_template = st.text_input("Filename Template", value="{date}_{category}_{original_filename}", help="Supported tokens: {date}, {category}, {sender}, {sender_domain}, {subject}, {original_filename}")

            st.markdown("##### Condition Definition")
            cond_logic = st.selectbox("Group Logic", ["AND", "OR"], help="All conditions must match (AND) or any condition matches (OR)")

            col1, col2, col3 = st.columns(3)
            with col1:
                field_1 = st.selectbox("Field", ["category", "filename", "sender_email", "sender_domain", "subject", "extension", "mime_type", "file_size"])
            with col2:
                operator_1 = st.selectbox("Operator", ["equals", "contains", "starts_with", "ends_with", "in_list", "greater_than", "less_than"])
            with col3:
                value_1 = st.text_input("Condition Value", placeholder="e.g. Invoices or stripe.com")

            submit_rule = st.form_submit_button("Save New Rule", type="primary")

            if submit_rule:
                if not rule_name or not destination or not value_1:
                    st.error("Rule name, destination folder, and condition value are required.")
                else:
                    conditions_dict = {
                        "logic": cond_logic,
                        "rules": [
                            {"field": field_1, "operator": operator_1, "value": value_1}
                        ]
                    }
                    conditions_json = json.dumps(conditions_dict)

                    DB.add_rule(
                        rule_name=rule_name,
                        conditions_json=conditions_json,
                        destination=destination,
                        filename_template=fn_template,
                        priority=int(rule_priority),
                        enabled=1,
                    )
                    st.success(f"Rule '{rule_name}' successfully created!")
                    st.rerun()

    # ------------------ TAB 3: RULE TESTER ------------------
    with tab3:
        st.markdown("#### Test Filing Rules Against Real Attachments")
        st.caption("Select an attachment currently in your queue to simulate which rule will take precedence.")

        attachments = DB.get_attachments_workspace()
        if not attachments:
            st.info("No attachments currently registered in the database to test against.")
        else:
            options_map = {f"#{a['id']}: {a['original_filename']} ({a['category']})": a for a in attachments}
            selected_label = st.selectbox("Select Target Attachment", options=list(options_map.keys()))
            target_att = options_map[selected_label]

            rules = DB.get_rules(enabled_only=True)
            match_res = match_filing_rules(rules, target_att, {"sender": target_att.get("sender"), "received_at": target_att.get("received_at")})

            st.markdown(
                f"""
                <div class="station-card">
                    <h4>Simulation Result</h4>
                    <p><b>Matched Rule:</b> <span style="color:#356B59;">{match_res['rule_name']} (Priority {match_res['priority']})</span></p>
                    <p><b>Target Destination:</b> <code>{match_res['destination']}</code></p>
                    <p><b>Generated Filename:</b> <code>{match_res['proposed_filename']}</code></p>
                    <p><b>Explanation:</b> {match_res['reason']}</p>
                </div>
                """,
                unsafe_allow_html=True,
            )
