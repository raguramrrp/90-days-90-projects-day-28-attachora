"""
ATTACHORA Analytics & Reporting Page
Displays live operational summaries, storage efficiency metrics, category distributions,
and temporal processing volume calculated directly from the SQLite database.
"""

import pandas as pd
import streamlit as st
from src.analytics.reporter import REPORTER


def render_analytics_page():
    st.subheader("Operational Analytics & Reports")
    st.caption("Quantitative insights into attachment volume, storage consumption, deduplication efficiency, and sender activity.")

    # 1. KPI Metric Cards
    metrics = REPORTER.get_summary_metrics()

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown(
            f"""
            <div class="metric-box">
                <div class="lbl">Total Detected</div>
                <div class="val">{metrics['total_detected']}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with c2:
        st.markdown(
            f"""
            <div class="metric-box">
                <div class="lbl">Organized to Library</div>
                <div class="val" style="color:#32815A;">{metrics['total_organized']}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with c3:
        st.markdown(
            f"""
            <div class="metric-box">
                <div class="lbl">Awaiting Approval</div>
                <div class="val" style="color:#B78032;">{metrics['awaiting_approval']}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with c4:
        st.markdown(
            f"""
            <div class="metric-box">
                <div class="lbl">Duplicates Identified</div>
                <div class="val" style="color:#6C5CE7;">{metrics['duplicates_count']}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown("<div style='margin-top: 15px;'></div>", unsafe_allow_html=True)

    s1, s2 = st.columns(2)
    with s1:
        st.markdown(
            f"""
            <div class="metric-box">
                <div class="lbl">Total Library Storage</div>
                <div class="val">{metrics['total_storage_organized_mb']} MB</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with s2:
        st.markdown(
            f"""
            <div class="metric-box">
                <div class="lbl">Storage Saved (Deduplication)</div>
                <div class="val" style="color:#356B59;">{metrics['storage_saved_mb']} MB</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown("---")

    # 2. Charts & Breakdowns
    chart_c1, chart_c2 = st.columns(2)

    with chart_c1:
        st.markdown("#### Attachment Volume by Category")
        cat_df = REPORTER.get_category_distribution()
        if not cat_df.empty:
            st.bar_chart(cat_df.set_index("category")["count"])
        else:
            st.info("No categorical data available yet.")

    with chart_c2:
        st.markdown("#### Top Email Senders")
        senders_df = REPORTER.get_top_senders(limit=8)
        if not senders_df.empty:
            display_df = senders_df[["sender_email", "attachment_count", "total_mb"]].rename(
                columns={
                    "sender_email": "Sender Email",
                    "attachment_count": "Attachments",
                    "total_mb": "Volume (MB)",
                }
            )
            st.dataframe(display_df, use_container_width=True)
        else:
            st.info("No sender activity recorded yet.")

    st.markdown("---")

    # 3. Processing Timeline
    st.markdown("#### Ingestion Timeline Over Time")
    time_df = REPORTER.get_processing_timeline()
    if not time_df.empty:
        st.line_chart(time_df.set_index("processing_date")["count"])
    else:
        st.caption("Temporal timeline will render as email batches are processed.")
