"""
ATTACHORA Design System & Styling
Provides complete light theme CSS overrides enforcing readable contrast,
consistent typography (Inter & JetBrains Mono), and enterprise workstation aesthetic.
"""

import streamlit as st

LIGHT_THEME_CSS = """
<style>
/* Import fonts */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500;600&display=swap');

/* Root reset */
html, body, [class*="css"], .stApp {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif !important;
    color: #252B29 !important;
    background-color: #F5F6F5 !important;
}

/* Force light background on all app containers */
.main, .stApp, section.main, [data-testid="stAppViewContainer"] {
    background-color: #F5F6F5 !important;
    color: #252B29 !important;
}

/* Header bar */
.attachora-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    background-color: #FFFFFF;
    padding: 8px 18px;
    border: 1px solid #E1E5E2;
    border-radius: 6px;
    margin-bottom: 12px;
}
.brand-title {
    font-size: 1.1rem;
    font-weight: 700;
    letter-spacing: 0.04em;
    color: #356B59;
}
.brand-subtitle {
    font-size: 0.85rem;
    color: #737C78;
    margin-left: 8px;
    font-weight: 500;
}

/* Typography rules & high contrast */
h1, .stMarkdown h1 {
    font-size: 22px !important;
    font-weight: 700 !important;
    color: #252B29 !important;
    margin-top: 0px !important;
    margin-bottom: 6px !important;
}
h2, .stMarkdown h2 {
    font-size: 18px !important;
    font-weight: 600 !important;
    color: #252B29 !important;
    margin-top: 4px !important;
    margin-bottom: 4px !important;
}
h3, .stMarkdown h3 {
    font-size: 15px !important;
    font-weight: 600 !important;
    color: #252B29 !important;
    margin-top: 4px !important;
    margin-bottom: 4px !important;
}
h4, .stMarkdown h4 {
    font-size: 13px !important;
    font-weight: 600 !important;
    color: #252B29 !important;
    margin-top: 2px !important;
    margin-bottom: 2px !important;
}
p, span, div, label {
    color: #252B29 !important;
    font-size: 13px;
}
[data-testid="stCaptionContainer"] p, [data-testid="stCaptionContainer"] {
    color: #737C78 !important;
    font-size: 12px !important;
}

/* Form inputs & text fields (Forced Light Theme) */
.stTextInput input, .stNumberInput input, .stDateInput input, .stTextArea textarea {
    background-color: #FFFFFF !important;
    color: #252B29 !important;
    border: 1px solid #D5DBD7 !important;
    border-radius: 4px !important;
    font-size: 13px !important;
    padding: 6px 10px !important;
}
div[data-baseweb="input"] {
    background-color: #FFFFFF !important;
    border: 1px solid #D5DBD7 !important;
    border-radius: 4px !important;
}
div[data-baseweb="input"]:focus-within, .stTextInput input:focus {
    border-color: #356B59 !important;
    box-shadow: 0 0 0 1px #356B59 !important;
}
input::placeholder, textarea::placeholder {
    color: #929A96 !important;
}

/* Selectbox & Dropdowns (Forced Light Theme) */
div[data-baseweb="select"] {
    background-color: #FFFFFF !important;
    border-radius: 4px !important;
}
div[data-baseweb="select"] > div {
    background-color: #FFFFFF !important;
    color: #252B29 !important;
    border: 1px solid #D5DBD7 !important;
    border-radius: 4px !important;
    font-size: 13px !important;
}
div[data-baseweb="popover"], div[data-baseweb="menu"], ul[role="listbox"] {
    background-color: #FFFFFF !important;
    border: 1px solid #E1E5E2 !important;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08) !important;
}
li[role="option"] {
    background-color: #FFFFFF !important;
    color: #252B29 !important;
    font-size: 13px !important;
}
li[role="option"]:hover, li[aria-selected="true"] {
    background-color: #EAF1ED !important;
    color: #356B59 !important;
}

/* Buttons (Restrained, Crisp Light Theme) */
.stButton > button {
    background-color: #FFFFFF !important;
    color: #252B29 !important;
    border: 1px solid #D5DBD7 !important;
    border-radius: 4px !important;
    font-size: 13px !important;
    font-weight: 500 !important;
    padding: 5px 12px !important;
    transition: all 0.12s ease !important;
}
.stButton > button:hover {
    background-color: #F3F6F4 !important;
    border-color: #356B59 !important;
    color: #356B59 !important;
}

/* Primary Buttons */
.stButton > button[kind="primary"], .stButton > button[data-testid="baseButton-primary"] {
    background-color: #356B59 !important;
    color: #FFFFFF !important;
    border: 1px solid #356B59 !important;
    font-weight: 600 !important;
}
.stButton > button[kind="primary"]:hover, .stButton > button[data-testid="baseButton-primary"]:hover {
    background-color: #285646 !important;
    border-color: #285646 !important;
    color: #FFFFFF !important;
}

/* Sidebar Navigation */
section[data-testid="stSidebar"] {
    background-color: #FFFFFF !important;
    border-right: 1px solid #E1E5E2 !important;
}
section[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p {
    color: #252B29 !important;
}

/* Tables & DataFrames */
div[data-testid="stDataFrame"] {
    background-color: #FFFFFF !important;
    border: 1px solid #E1E5E2 !important;
    border-radius: 5px !important;
}

/* Cards & Surface Containers */
.station-card {
    background-color: #FFFFFF;
    border: 1px solid #E1E5E2;
    border-radius: 6px;
    padding: 14px 16px;
    margin-bottom: 12px;
}

/* Metric KPI Containers */
.metric-box {
    background-color: #FFFFFF;
    border: 1px solid #E1E5E2;
    border-radius: 6px;
    padding: 10px 14px;
}
.metric-box .lbl {
    font-size: 11px;
    text-transform: uppercase;
    font-weight: 600;
    color: #737C78 !important;
    letter-spacing: 0.03em;
}
.metric-box .val {
    font-size: 1.35rem;
    font-weight: 700;
    color: #252B29 !important;
    line-height: 1.2;
    margin-top: 2px;
}

/* Expanders */
div[data-testid="stExpander"] {
    background-color: #FFFFFF !important;
    border: 1px solid #E1E5E2 !important;
    border-radius: 5px !important;
    margin-bottom: 8px !important;
}
summary[data-testid="stExpanderSummary"] {
    color: #252B29 !important;
    font-weight: 600 !important;
}

/* Badges */
.badge {
    display: inline-block;
    padding: 2px 7px;
    font-size: 11px;
    font-weight: 600;
    border-radius: 3px;
    line-height: 1.3;
    text-transform: uppercase;
    letter-spacing: 0.03em;
}
.badge-organized {
    background-color: #EBF5F0;
    color: #32815A !important;
    border: 1px solid #C3E3D2;
}
.badge-pending {
    background-color: #FEF7EC;
    color: #B78032 !important;
    border: 1px solid #F5DEC0;
}
.badge-duplicate {
    background-color: #F4F1FA;
    color: #6C5CE7 !important;
    border: 1px solid #D5CFF7;
}
.badge-skipped {
    background-color: #EEF1EF;
    color: #737C78 !important;
    border: 1px solid #E1E5E2;
}
.badge-failed {
    background-color: #FDE8E8;
    color: #BC4B4B !important;
    border: 1px solid #F8B4B4;
}
.badge-restored {
    background-color: #EBF8FF;
    color: #2B6CB0 !important;
    border: 1px solid #BEE3F8;
}

/* Hashes & Identifiers */
.hash-pill {
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 11px !important;
    background-color: #EEF1EF;
    color: #252B29 !important;
    padding: 2px 5px;
    border-radius: 3px;
    border: 1px solid #E1E5E2;
}

/* Custom table row styling in queue */
.queue-row {
    background-color: #FFFFFF;
    border: 1px solid #E1E5E2;
    border-radius: 5px;
    padding: 10px 12px;
    margin-bottom: 6px;
    cursor: pointer;
    transition: border-color 0.12s ease, background-color 0.12s ease;
}
.queue-row:hover {
    background-color: #F3F6F4;
    border-color: #C2CAC5;
}
.queue-row-selected {
    background-color: #EAF1ED !important;
    border: 1px solid #356B59 !important;
}

/* Tabs */
button[data-baseweb="tab"] {
    color: #737C78 !important;
    font-size: 13px !important;
    font-weight: 500 !important;
}
button[data-baseweb="tab"][aria-selected="true"] {
    color: #356B59 !important;
    font-weight: 600 !important;
    border-bottom: 2px solid #356B59 !important;
}

/* Remove default Streamlit chrome overhead */
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}
.block-container {
    padding-top: 1.2rem !important;
    padding-bottom: 2rem !important;
    max-width: 100% !important;
}
</style>
"""


def apply_theme():
    """Injects high-contrast, pure-light CSS styling into the Streamlit app."""
    st.markdown(LIGHT_THEME_CSS, unsafe_allow_html=True)


def render_status_badge(status: str) -> str:
    """Returns an HTML string for a colored status badge."""
    s = (status or "Detected").lower()
    if s == "organized":
        return '<span class="badge badge-organized">Organized</span>'
    elif s in ("pending approval", "pending", "detected"):
        return '<span class="badge badge-pending">Pending</span>'
    elif s == "duplicate":
        return '<span class="badge badge-duplicate">Duplicate</span>'
    elif s == "skipped":
        return '<span class="badge badge-skipped">Skipped</span>'
    elif s == "failed":
        return '<span class="badge badge-failed">Failed</span>'
    elif s == "restored":
        return '<span class="badge badge-restored">Restored</span>'
    return f'<span class="badge badge-skipped">{status}</span>'
