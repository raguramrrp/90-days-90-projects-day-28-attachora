"""
ATTACHORA Analytics & Reporting Page
Displays live operational summaries, storage efficiency metrics, category distributions,
and temporal processing volume calculated directly from the SQLite database.
"""

import pandas as pd
import streamlit as st
from src.analytics.reporter import REPORTER
from src.database.db_manager import DB


def render_analytics_page():
    st.markdown(
        """
        <div style="margin-bottom: 14px;">
            <h1 style="font-size:22px; font-weight:700; color:#202824; margin:0 0 4px 0;">
                Operational Analytics & Metrics
            </h1>
            <div style="font-size:13px; color:#66716B;">
                Quantitative insights into document ingestion volume, storage efficiency, deduplication savings, and filing accuracy.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # 1. KPI Metric Strip
    metrics = REPORTER.get_summary_metrics()

    # Time saved calculation (explicitly documented assumption: 1.5 minutes saved per organized document)
    minutes_saved = metrics["total_organized"] * 1.5
    hours_saved = minutes_saved / 60.0

    st.markdown(
        f"""
        <div class="operational-summary-strip" style="margin-bottom:16px;">
            <div class="summary-item">
                <span class="summary-val" style="color:#286B50;">{metrics['total_detected']}</span>
                <span class="summary-lbl">Total Detected</span>
            </div>
            <div class="summary-divider"></div>
            <div class="summary-item">
                <span class="summary-val" style="color:#278253;">{metrics['total_organized']}</span>
                <span class="summary-lbl">Organized to Library</span>
            </div>
            <div class="summary-divider"></div>
            <div class="summary-item">
                <span class="summary-val" style="color:#B77925;">{metrics['duplicates_count']}</span>
                <span class="summary-lbl">Duplicates Prevented</span>
            </div>
            <div class="summary-divider"></div>
            <div class="summary-item">
                <span class="summary-val" style="color:#286B50;">{hours_saved:.1f} hrs</span>
                <span class="summary-lbl">Time Saved*</span>
            </div>
        </div>
        <div style="font-size:11px; color:#8A948E; margin-top:-10px; margin-bottom:16px;">
            * Time saved is calculated using a standard benchmark of 1.5 minutes per manual document classification, sanitization, renaming, and local directory filing.
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Storage Savings Row
    s1, s2 = st.columns(2)
    with s1:
        st.markdown(
            f"""
            <div style="background:#FFFFFF; border:1px solid #DCE3DE; border-radius:8px; padding:12px 16px;">
                <div style="font-size:11px; text-transform:uppercase; font-weight:700; color:#66716B;">Active Library Footprint</div>
                <div style="font-size:20px; font-weight:700; color:#202824; margin-top:4px;">{metrics['total_storage_organized_mb']} MB</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with s2:
        st.markdown(
            f"""
            <div style="background:#FFFFFF; border:1px solid #DCE3DE; border-radius:8px; padding:12px 16px;">
                <div style="font-size:11px; text-transform:uppercase; font-weight:700; color:#66716B;">Storage Preserved via Deduplication</div>
                <div style="font-size:20px; font-weight:700; color:#278253; margin-top:4px;">{metrics['storage_saved_mb']} MB saved</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown("<div style='height:16px;'></div>", unsafe_allow_html=True)

    # 2. Charts & Breakdowns
    chart_c1, chart_c2 = st.columns(2)

    with chart_c1:
        st.markdown("#### Document Volume by Category")
        cat_df = REPORTER.get_category_distribution()
        if not cat_df.empty:
            st.bar_chart(cat_df.set_index("category")["count"], color="#286B50")
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
        st.line_chart(time_df.set_index("processing_date")["count"], color="#286B50")
    else:
        st.caption("Temporal timeline will render as email batches are processed.")
