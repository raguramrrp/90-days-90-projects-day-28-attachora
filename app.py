"""
ATTACHORA — Intelligent Email Attachment Classification & Filing System
Main application entry point orchestrating navigation, UI theming, and modular page dispatching.
"""

import sys
from pathlib import Path

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).resolve().parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import streamlit as st

# Configure Streamlit page options
st.set_page_config(
    page_title="ATTACHORA — Intelligent Attachment System",
    layout="wide",
    initial_sidebar_state="expanded",
)

from src.database.db_manager import DB
from ui.components.header import render_header
from ui.components.nav_rail import render_nav_rail
from ui.pages.analytics_page import render_analytics_page
from ui.pages.connections_page import render_connections_page
from ui.pages.history_page import render_history_page
from ui.pages.integrity_page import render_integrity_page
from ui.pages.organized_page import render_organized_page
from ui.pages.rules_page import render_rules_page
from ui.pages.settings_page import render_settings_page
from ui.pages.workspace_page import render_workspace_page
from ui.theme import apply_theme


def main():
    # Inject enterprise custom styling matching the reference UI
    apply_theme()

    # Render 76px navigation rail in sidebar
    active_page = render_nav_rail()

    # Render horizontal topbar
    render_header(current_page=active_page)

    # Dispatch to appropriate page view
    if active_page in ("Queue", "Workspace"):
        render_workspace_page()
    elif active_page in ("Mailbox", "Connections"):
        render_connections_page()
    elif active_page in ("Integrity", "Security"):
        render_integrity_page()
    elif active_page in ("Rules", "Filing Rules"):
        render_rules_page()
    elif active_page in ("Library", "Organized Files"):
        render_organized_page()
    elif active_page in ("History", "Operation History", "History & Audit"):
        render_history_page()
    elif active_page in ("Analytics", "Analytics & Reports"):
        render_analytics_page()
    elif active_page == "Settings":
        render_settings_page()
    else:
        render_workspace_page()


if __name__ == "__main__":
    main()
