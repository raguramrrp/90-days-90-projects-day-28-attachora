"""
ATTACHORA Design System & Styling
Injects enterprise CSS conforming to the refined light theme palette and dense workstation aesthetic.
"""

import streamlit as st
from src.config import CONFIG

CUSTOM_CSS = f"""
<style>
/* Reset and core fonts */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');

html, body, [class*="css"] {{
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    color: {CONFIG.COLOR_TEXT_PRIMARY};
    background-color: {CONFIG.COLOR_BG};
}}

.stApp {{
    background-color: {CONFIG.COLOR_BG};
}}

/* Top header bar */
.attachora-header {{
    display: flex;
    justify-content: space-between;
    align-items: center;
    background-color: {CONFIG.COLOR_SURFACE};
    padding: 10px 20px;
    border-bottom: 1px solid {CONFIG.COLOR_BORDER};
    margin: -1rem -1rem 1rem -1rem;
}}

.brand-title {{
    font-size: 1.15rem;
    font-weight: 700;
    letter-spacing: 0.05em;
    color: {CONFIG.COLOR_ACCENT};
    margin: 0;
}}

.brand-subtitle {{
    font-size: 0.82rem;
    color: {CONFIG.COLOR_TEXT_SECONDARY};
    margin-left: 10px;
    font-weight: 500;
}}

/* Status badges */
.badge {{
    display: inline-block;
    padding: 3px 8px;
    font-size: 0.75rem;
    font-weight: 600;
    border-radius: 4px;
    line-height: 1.2;
    text-transform: uppercase;
    letter-spacing: 0.03em;
}}

.badge-organized {{
    background-color: #EBF5F0;
    color: {CONFIG.COLOR_SUCCESS};
    border: 1px solid #C3E3D2;
}}

.badge-pending {{
    background-color: #FEF7EC;
    color: {CONFIG.COLOR_WARNING};
    border: 1px solid #F5DEC0;
}}

.badge-duplicate {{
    background-color: #F4F1FA;
    color: #6C5CE7;
    border: 1px solid #D5CFF7;
}}

.badge-skipped {{
    background-color: #F1F4F2;
    color: {CONFIG.COLOR_TEXT_SECONDARY};
    border: 1px solid {CONFIG.COLOR_BORDER};
}}

.badge-failed {{
    background-color: #FDE8E8;
    color: {CONFIG.COLOR_ERROR};
    border: 1px solid #F8B4B4;
}}

.badge-restored {{
    background-color: #EBF8FF;
    color: #2B6CB0;
    border: 1px solid #BEE3F8;
}}

.hash-pill {{
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.72rem;
    background: #EAEAEA;
    padding: 2px 6px;
    border-radius: 3px;
    color: #4A5568;
}}

/* Compact Table Density */
div[data-testid="stDataFrame"] {{
    border: 1px solid {CONFIG.COLOR_BORDER};
    border-radius: 6px;
    background-color: {CONFIG.COLOR_SURFACE};
}}

/* Form elements & Cards */
.station-card {{
    background-color: {CONFIG.COLOR_SURFACE};
    border: 1px solid {CONFIG.COLOR_BORDER};
    border-radius: 6px;
    padding: 16px;
    margin-bottom: 14px;
}}

.metric-box {{
    background-color: {CONFIG.COLOR_SURFACE};
    border: 1px solid {CONFIG.COLOR_BORDER};
    border-radius: 6px;
    padding: 12px 16px;
    text-align: left;
}}
.metric-box .val {{
    font-size: 1.4rem;
    font-weight: 700;
    color: {CONFIG.COLOR_TEXT_PRIMARY};
}}
.metric-box .lbl {{
    font-size: 0.78rem;
    color: {CONFIG.COLOR_TEXT_SECONDARY};
    text-transform: uppercase;
    font-weight: 600;
}}

/* Custom slim sidebar */
section[data-testid="stSidebar"] {{
    background-color: {CONFIG.COLOR_NAV};
    border-right: 1px solid {CONFIG.COLOR_BORDER};
}}

/* Hide unnecessary default Streamlit chrome */
#MainMenu {{visibility: hidden;}}
footer {{visibility: hidden;}}
header {{visibility: hidden;}}
</style>
"""


def apply_theme():
    """Injects custom CSS stylesheets into Streamlit session."""
    st.markdown(CUSTOM_CSS, unsafe_allow_html=True)


def render_status_badge(status: str) -> str:
    """Returns an HTML string for a colored status badge."""
    s = (status or "Detected").lower()
    if s == "organized":
        return f'<span class="badge badge-organized">Organized</span>'
    elif s in ("pending approval", "pending", "detected"):
        return f'<span class="badge badge-pending">Pending</span>'
    elif s == "duplicate":
        return f'<span class="badge badge-duplicate">Duplicate</span>'
    elif s == "skipped":
        return f'<span class="badge badge-skipped">Skipped</span>'
    elif s == "failed":
        return f'<span class="badge badge-failed">Failed</span>'
    elif s == "restored":
        return f'<span class="badge badge-restored">Restored</span>'
    return f'<span class="badge badge-skipped">{status}</span>'
