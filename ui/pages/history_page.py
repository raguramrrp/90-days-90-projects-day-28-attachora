"""
ATTACHORA Operation History & Audit Log Page
Maintains an immutable audit trail of every extraction, classification, filing,
skip, duplicate linking, and restoration event.
"""

import pandas as pd
import streamlit as st
from src.analytics.reporter import REPORTER
from src.database.db_manager import DB
from ui.theme import render_status_badge


def render_history_page():
    st.subheader("Operation History & Audit Trail")
    st.caption("Complete, tamper-evident log of all attachment lifecycle operations and state transitions.")

    # Top controls & CSV export
    top_c1, top_c2 = st.columns([3, 1])
    with top_c2:
        csv_data = REPORTER.export_operations_csv()
        st.download_button(
            label="Export History (CSV)",
            data=csv_data,
            file_name="attachora_operations_audit.csv",
            mime="text/csv",
            use_container_width=True,
        )

    # Filter toolbar for operations
    f1, f2, f3 = st.columns(3)
    with f1:
        op_status = st.selectbox(
            "Filter by Status",
            options=["All", "Organized", "Pending Approval", "Detected", "Duplicate", "Skipped", "Restored", "Failed"],
            key="hist_status_filter",
        )
    with f2:
        op_type = st.selectbox(
            "Filter by Operation Type",
            options=["All", "Classify", "Organize", "Skip", "Duplicate-Ref", "Undo"],
            key="hist_type_filter",
        )
    with f3:
        search_kw = st.text_input("Search Filename / Sender / SHA", key="hist_search_kw")

    operations = DB.get_operations(
        status=op_status,
        operation_type=op_type,
        search_query=search_kw,
        limit=200,
    )

    if not operations:
        st.info("No operation records found matching the filter criteria.")
        return

    st.markdown(f"**Total Records Found:** {len(operations)}")

    # Table view
    table_data = []
    for op in operations:
        table_data.append(
            {
                "ID": op["id"],
                "Timestamp": str(op.get("timestamp"))[:19],
                "Type": op["operation_type"],
                "Status": op["status"],
                "Original Filename": op.get("original_filename"),
                "Final Destination": op.get("destination_path") or "N/A",
                "Category": op.get("category"),
                "Sender": op.get("sender_email") or op.get("sender"),
                "SHA-256": (op.get("sha256") or "")[:12] + "...",
            }
        )

    df = pd.DataFrame(table_data)
    st.dataframe(df, use_container_width=True, height=450)

    # Detailed record inspector modal/expander
    with st.expander("Inspect Individual Operation Record Details"):
        selected_op_id = st.number_input("Enter Operation ID to Inspect", min_value=1, max_value=max([op['id'] for op in operations]), value=operations[0]["id"])
        selected_record = next((op for op in operations if op["id"] == selected_op_id), None)
        if selected_record:
            st.json(selected_record)
