"""
ATTACHORA Design System & Styling
Provides complete light theme CSS overrides matching the reference UI design:
- 76px narrow left navigation rail with monochrome icons
- Top horizontal navigation bar with centered active tabs and breadcrumb
- Compact operational summary strip
- Full-width search and filter toolbar
- Dense, structured attachment data table with file badges and status pills
- Dedicated right-side selected attachment inspector
- Crisp Inter and JetBrains Mono typography
"""

import streamlit as st

LIGHT_THEME_CSS = """
<style>
/* Import Inter and JetBrains Mono fonts */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500;600&display=swap');

/* Root reset */
html, body, [class*="css"], .stApp {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif !important;
    color: #202824 !important;
    background-color: #F4F6F4 !important;
}

/* Force light background on all app containers */
.main, .stApp, section.main, [data-testid="stAppViewContainer"] {
    background-color: #F4F6F4 !important;
    color: #202824 !important;
}

/* Remove default Streamlit top padding and chrome */
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}
.block-container {
    padding-top: 0.8rem !important;
    padding-bottom: 1.5rem !important;
    padding-left: 1.5rem !important;
    padding-right: 1.5rem !important;
    max-width: 100% !important;
}

/* ------------------ LEFT NAVIGATION RAIL (76px) ------------------ */
section[data-testid="stSidebar"] {
    width: 76px !important;
    min-width: 76px !important;
    max-width: 76px !important;
    background-color: #FFFFFF !important;
    border-right: 1px solid #DCE3DE !important;
    padding: 0 !important;
    overflow-x: hidden !important;
}
section[data-testid="stSidebar"] > div:first-child {
    width: 76px !important;
    padding: 14px 10px !important;
    display: flex !important;
    flex-direction: column !important;
    align-items: center !important;
}
[data-testid="stSidebarCollapseButton"] {
    display: none !important;
}

/* Sidebar Nav Buttons */
.nav-item-btn button {
    width: 46px !important;
    height: 46px !important;
    min-width: 46px !important;
    padding: 0 !important;
    margin: 3px 0 !important;
    border-radius: 8px !important;
    border: none !important;
    background-color: transparent !important;
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
    transition: all 0.15s ease !important;
    box-shadow: none !important;
}
.nav-item-btn button:hover {
    background-color: #F1F6F2 !important;
}
.nav-item-btn.active button {
    background-color: #286B50 !important;
}

/* ------------------ TOP NAVIGATION BAR (62px) ------------------ */
.attachora-topbar {
    display: flex;
    justify-content: space-between;
    align-items: center;
    background-color: #FFFFFF;
    border-bottom: 1px solid #DCE3DE;
    padding: 10px 20px;
    margin-bottom: 16px;
    border-radius: 8px;
    height: 56px;
}
.topbar-brand {
    display: flex;
    align-items: center;
    gap: 10px;
}
.topbar-logo-icon {
    width: 24px;
    height: 24px;
    background-color: #286B50;
    border-radius: 5px;
    display: flex;
    align-items: center;
    justify-content: center;
    color: #FFFFFF;
    font-weight: 700;
    font-size: 13px;
}
.topbar-title {
    font-size: 15px;
    font-weight: 700;
    letter-spacing: 0.04em;
    color: #202824;
}
.topbar-separator {
    color: #DCE3DE;
    font-weight: 300;
    margin: 0 4px;
}
.topbar-breadcrumb {
    font-size: 13px;
    color: #66716B;
    font-weight: 400;
}
.topbar-nav {
    display: flex;
    align-items: center;
    gap: 22px;
}
.topbar-link {
    font-size: 13px;
    font-weight: 500;
    color: #66716B;
    text-decoration: none;
    padding: 16px 0;
    position: relative;
    cursor: pointer;
    transition: color 0.12s ease;
}
.topbar-link:hover {
    color: #202824;
}
.topbar-link.active {
    color: #286B50;
    font-weight: 600;
    border-bottom: 2px solid #286B50;
}
.topbar-actions {
    display: flex;
    align-items: center;
    gap: 14px;
}
.mailbox-pill {
    display: flex;
    align-items: center;
    gap: 6px;
    font-size: 12px;
    font-weight: 500;
    color: #202824;
    background: #FFFFFF;
    padding: 5px 10px;
    border-radius: 6px;
    border: 1px solid #DCE3DE;
}
.status-dot {
    width: 7px;
    height: 7px;
    border-radius: 50%;
    background-color: #278253;
}

/* ------------------ OPERATIONAL SUMMARY STRIP ------------------ */
.operational-summary-strip {
    background-color: #FFFFFF;
    border: 1px solid #DCE3DE;
    border-radius: 8px;
    padding: 12px 20px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 14px;
}
.summary-item {
    display: flex;
    align-items: baseline;
    gap: 8px;
}
.summary-val {
    font-size: 22px;
    font-weight: 700;
    line-height: 1;
}
.summary-lbl {
    font-size: 13px;
    color: #202824;
    font-weight: 500;
}
.summary-divider {
    width: 1px;
    height: 24px;
    background-color: #DCE3DE;
}

/* ------------------ FORM INPUTS & SEARCH ------------------ */
.stTextInput input, .stNumberInput input, .stDateInput input, .stTextArea textarea {
    background-color: #FFFFFF !important;
    color: #202824 !important;
    border: 1px solid #DCE3DE !important;
    border-radius: 6px !important;
    font-size: 13px !important;
    padding: 7px 12px !important;
}
div[data-baseweb="input"] {
    background-color: #FFFFFF !important;
    border: 1px solid #DCE3DE !important;
    border-radius: 6px !important;
}
div[data-baseweb="input"]:focus-within, .stTextInput input:focus {
    border-color: #286B50 !important;
    box-shadow: 0 0 0 1px #286B50 !important;
}
input::placeholder, textarea::placeholder {
    color: #8A948E !important;
}

/* Selectbox & Dropdowns */
div[data-baseweb="select"] {
    background-color: #FFFFFF !important;
    border-radius: 6px !important;
}
div[data-baseweb="select"] > div {
    background-color: #FFFFFF !important;
    color: #202824 !important;
    border: 1px solid #DCE3DE !important;
    border-radius: 6px !important;
    font-size: 13px !important;
}
div[data-baseweb="popover"], div[data-baseweb="menu"], ul[role="listbox"] {
    background-color: #FFFFFF !important;
    border: 1px solid #DCE3DE !important;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08) !important;
}
li[role="option"] {
    background-color: #FFFFFF !important;
    color: #202824 !important;
    font-size: 13px !important;
}
li[role="option"]:hover, li[aria-selected="true"] {
    background-color: #E9F2EC !important;
    color: #286B50 !important;
}

/* ------------------ BUTTONS ------------------ */
.stButton > button {
    background-color: #FFFFFF !important;
    color: #202824 !important;
    border: 1px solid #DCE3DE !important;
    border-radius: 6px !important;
    font-size: 13px !important;
    font-weight: 500 !important;
    padding: 6px 14px !important;
    transition: all 0.12s ease !important;
    box-shadow: none !important;
}
.stButton > button:hover {
    background-color: #F1F6F2 !important;
    border-color: #286B50 !important;
    color: #286B50 !important;
}

/* Primary Green Buttons */
.stButton > button[kind="primary"], .stButton > button[data-testid="baseButton-primary"] {
    background-color: #286B50 !important;
    color: #FFFFFF !important;
    border: 1px solid #286B50 !important;
    font-weight: 600 !important;
}
.stButton > button[kind="primary"]:hover, .stButton > button[data-testid="baseButton-primary"]:hover {
    background-color: #20553F !important;
    border-color: #20553F !important;
    color: #FFFFFF !important;
}

/* ------------------ ATTACHMENT DATA TABLE ------------------ */
.attachora-table-container {
    background: #FFFFFF;
    border: 1px solid #DCE3DE;
    border-radius: 8px;
    overflow: hidden;
    margin-top: 10px;
    margin-bottom: 12px;
}
.attachora-table-header-row {
    background-color: #F7F9F7;
    border-bottom: 1px solid #DCE3DE;
    padding: 8px 12px;
    font-size: 11px;
    font-weight: 700;
    color: #66716B;
    letter-spacing: 0.04em;
    text-transform: uppercase;
}
.attachora-table-row {
    border-bottom: 1px solid #EAEFEA;
    padding: 6px 10px;
    align-items: center;
    transition: background-color 0.12s ease;
}
.attachora-table-row:hover {
    background-color: #F1F6F2;
}
.attachora-table-row.selected {
    background-color: #F1F6F2 !important;
    border-left: 3px solid #286B50 !important;
}

/* File Type Square Badges */
.filetype-badge {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    width: 28px;
    height: 22px;
    border-radius: 4px;
    font-size: 9px;
    font-weight: 700;
    text-transform: uppercase;
    color: #FFFFFF;
    letter-spacing: 0.02em;
    flex-shrink: 0;
}
.badge-pdf { background-color: #D32F2F; }
.badge-docx, .badge-doc { background-color: #1976D2; }
.badge-xlsx, .badge-xls, .badge-csv { background-color: #2E7D32; }
.badge-zip, .badge-tar, .badge-gz { background-color: #E65100; }
.badge-txt, .badge-log { background-color: #546E7A; }
.badge-png, .badge-jpg, .badge-jpeg { background-color: #7B1FA2; }
.badge-code, .badge-py, .badge-json { background-color: #00838F; }

/* Status Pill Badges */
.status-pill {
    display: inline-block;
    padding: 2px 9px;
    font-size: 11px;
    font-weight: 600;
    border-radius: 12px;
    line-height: 1.4;
    text-align: center;
}
.status-ready {
    background-color: #E9F2EC;
    color: #278253 !important;
    border: 1px solid #C9E2D2;
}
.status-duplicate {
    background-color: #EFEFEF;
    color: #66716B !important;
    border: 1px solid #DCDCDC;
}
.status-review {
    background-color: #FEF5E7;
    color: #B77925 !important;
    border: 1px solid #F7E1C3;
}
.status-filed {
    background-color: #E6F4EA;
    color: #278253 !important;
    border: 1px solid #BEE0CC;
}
.status-failed {
    background-color: #FDE8E8;
    color: #BD4545 !important;
    border: 1px solid #F8B4B4;
}

/* ------------------ SELECTED ATTACHMENT INSPECTOR ------------------ */
.inspector-card {
    background-color: #FFFFFF;
    border: 1px solid #DCE3DE;
    border-radius: 8px;
    padding: 16px;
}
.inspector-title {
    font-size: 14px;
    font-weight: 700;
    color: #202824;
    margin-bottom: 12px;
}
.inspector-file-header {
    display: flex;
    align-items: center;
    gap: 12px;
    margin-bottom: 14px;
    padding-bottom: 12px;
    border-bottom: 1px solid #DCE3DE;
}
.inspector-file-badge {
    width: 34px;
    height: 34px;
    border-radius: 6px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 11px;
    font-weight: 700;
    color: #FFFFFF;
    text-transform: uppercase;
    flex-shrink: 0;
}
.inspector-filename {
    font-size: 14px;
    font-weight: 700;
    color: #202824;
    word-break: break-all;
    line-height: 1.25;
}
.inspector-meta {
    font-size: 11px;
    color: #66716B;
    margin-top: 2px;
}

/* Document Mini Preview Card (Structured Sheet) */
.mini-doc-sheet {
    background: #FFFFFF;
    border: 1px solid #DCE3DE;
    border-radius: 6px;
    padding: 14px;
    margin-bottom: 14px;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.04);
}
.mini-doc-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    border-bottom: 1px solid #EAEFEA;
    padding-bottom: 8px;
    margin-bottom: 8px;
}
.mini-doc-brand {
    font-size: 11px;
    font-weight: 700;
    color: #202824;
    letter-spacing: 0.02em;
    display: flex;
    align-items: center;
    gap: 5px;
}
.mini-doc-info {
    font-size: 10px;
    color: #66716B;
    text-align: right;
    line-height: 1.3;
}
.mini-doc-billto {
    font-size: 10px;
    color: #66716B;
    margin-bottom: 10px;
    line-height: 1.4;
}
.mini-doc-billto b {
    color: #202824;
}
.mini-doc-table {
    width: 100%;
    border-collapse: collapse;
    font-size: 10px;
    margin-bottom: 8px;
}
.mini-doc-table th {
    text-align: left;
    color: #66716B;
    border-bottom: 1px solid #DCE3DE;
    padding: 3px 0;
    font-weight: 600;
}
.mini-doc-table td {
    padding: 4px 0;
    color: #202824;
    border-bottom: 1px solid #F1F4F2;
}
.mini-doc-total {
    display: flex;
    justify-content: flex-end;
    gap: 12px;
    font-size: 11px;
    font-weight: 700;
    color: #202824;
    padding-top: 6px;
}

/* Filing Decision Section */
.filing-decision-header {
    font-size: 13px;
    font-weight: 700;
    color: #202824;
    margin-top: 10px;
    margin-bottom: 8px;
}
.filing-decision-row {
    display: flex;
    justify-content: space-between;
    align-items: center;
    font-size: 12px;
    margin-bottom: 6px;
}
.filing-decision-lbl {
    color: #66716B;
}
.filing-decision-val {
    color: #202824;
    font-weight: 500;
    text-align: right;
}

/* Hashes & Identifiers */
.hash-pill {
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 10px !important;
    background-color: #F4F6F4;
    color: #66716B !important;
    padding: 3px 6px;
    border-radius: 4px;
    border: 1px solid #DCE3DE;
    word-break: break-all;
}

/* Tabs */
button[data-baseweb="tab"] {
    color: #66716B !important;
    font-size: 13px !important;
    font-weight: 500 !important;
    padding: 8px 14px !important;
}
button[data-baseweb="tab"][aria-selected="true"] {
    color: #286B50 !important;
    font-weight: 600 !important;
    border-bottom: 2px solid #286B50 !important;
}
</style>
"""


def apply_theme():
    """Injects high-contrast, reference-aligned CSS styling into the Streamlit app."""
    st.markdown(LIGHT_THEME_CSS, unsafe_allow_html=True)


def get_filetype_badge_html(filename: str, ext: str = "") -> str:
    """Returns HTML for a colored square file type badge matching reference image."""
    e = (ext or filename.split(".")[-1] if "." in filename else "dat").lower()
    if e in ("pdf",):
        cls = "badge-pdf"
        label = "PDF"
    elif e in ("docx", "doc"):
        cls = "badge-docx"
        label = "DOC"
    elif e in ("xlsx", "xls", "csv"):
        cls = "badge-xlsx"
        label = "XLS"
    elif e in ("zip", "tar", "gz", "rar", "7z"):
        cls = "badge-zip"
        label = "ZIP"
    elif e in ("txt", "log", "md"):
        cls = "badge-txt"
        label = "TXT"
    elif e in ("png", "jpg", "jpeg", "webp", "gif"):
        cls = "badge-png"
        label = "IMG"
    elif e in ("py", "json", "js", "html", "css", "sql"):
        cls = "badge-code"
        label = "CODE"
    else:
        cls = "badge-txt"
        label = e[:3].upper()

    return f'<span class="filetype-badge {cls}">{label}</span>'


def render_status_pill(status: str) -> str:
    """Returns an HTML string for a colored status pill badge matching reference image."""
    s = (status or "Ready").lower()
    if s in ("ready", "ready to file", "organized"):
        return '<span class="status-pill status-ready">Ready</span>'
    elif s in ("duplicate", "exact duplicate", "conflict"):
        return '<span class="status-pill status-duplicate">Duplicate</span>'
    elif s in ("review", "pending", "pending approval", "detected"):
        return '<span class="status-pill status-review">Review</span>'
    elif s in ("filed", "completed"):
        return '<span class="status-pill status-filed">Filed</span>'
    elif s in ("failed", "error"):
        return '<span class="status-pill status-failed">Failed</span>'
    return f'<span class="status-pill status-ready">{status}</span>'
