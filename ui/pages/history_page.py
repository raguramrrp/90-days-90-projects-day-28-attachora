"""
ATTACHORA Operation History & Audit Log Page
Maintains an immutable audit trail of every extraction, classification, filing,
skip, duplicate linking, and restoration event.
"""

import pandas as pd
import streamlit as st
from src.analytics.reporter import REPORTER
from src.database.db_manager import DB


def render_history_page():
    st.markdown(
        """
        <div style="margin-bottom: 14px;">
            <h1 style="font-size:22px; font-weight:700; color:#202824; margin:0 0 4px 0;">
                Operation History & Audit Trail
            </h1>
            <div style="font-size:13px; color:#66716B;">
                Complete, tamper-evident log of all attachment lifecycle operations, routing decisions, and state transitions.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Top controls & CSV export
    top_c1, top_c2 = st.columns([7, 3])
    with top_c2:
        csv_data = REPORTER.export_operations_csv()
        st.download_button(
            label="↓ Export Audit History (CSV)",
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
        search_kw = st.text_input("Search Filename / Sender / Hash", key="hist_search_kw")

    operations = DB.get_operations(
        status=op_status,
        operation_type=op_type,
        search_query=search_kw,
        limit=200,
    )

    if not operations:
        st.info("No operation records found matching the filter criteria.")
        return

    st.markdown(
        f"""
        <div style="font-size:12px; color:#66716B; margin-bottom:8px;">
            Displaying <b>{len(operations)}</b> immutable audit records
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Table view
    table_data = []
    for op in operations:
        table_data.append(
            {
                "Op ID": f"#{op['id']}",
                "Timestamp": str(op.get("timestamp"))[:19],
                "Operation Type": op["operation_type"],
                "Document Name": op.get("original_filename"),
                "Source Path": Path(op.get("source_path", "")).name if op.get("source_path") else "Staging",
                "Destination": op.get("destination_path") or "N/A",
                "Category": op.get("category"),
                "Result / Status": op["status"],
            }
        )

    df = pd.DataFrame(table_data)
    st.dataframe(df, use_container_width=True, height=450)

    # Detailed record inspector
    with st.expander("Inspect Raw JSON Audit Payload"):
        selected_op_id = st.number_input("Enter Operation ID to Inspect", min_value=1, max_value=max([op['id'] for op in operations]), value=operations[0]["id"])
        selected_record = next((op for op in operations if op["id"] == selected_op_id), None)
        if selected_record:
            st.json(selected_record)
