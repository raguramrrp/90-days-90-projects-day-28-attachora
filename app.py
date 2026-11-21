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
    page_icon="📁",
    layout="wide",
    initial_sidebar_state="expanded",
)

from src.database.db_manager import DB
from ui.components.header import render_header
from ui.components.nav_rail import render_nav_rail
from ui.pages.analytics_page import render_analytics_page
from ui.pages.connections_page import render_connections_page
from ui.pages.history_page import render_history_page
from ui.pages.organized_page import render_organized_page
from ui.pages.rules_page import render_rules_page
from ui.pages.settings_page import render_settings_page
from ui.pages.workspace_page import render_workspace_page
from ui.theme import apply_theme


def main():
    # Inject enterprise custom styling
    apply_theme()

    # Render navigation rail in sidebar
    active_page = render_nav_rail()

    # Render compact horizontal header bar
    render_header(current_page=active_page)

    # Dispatch to appropriate page view
    if active_page == "Workspace":
        render_workspace_page()
    elif active_page == "Connections":
        render_connections_page()
    elif active_page == "Filing Rules":
        render_rules_page()
    elif active_page == "Organized Files":
        render_organized_page()
    elif active_page in ("Operation History", "History & Audit"):
        render_history_page()
    elif active_page in ("Analytics", "Analytics & Reports"):
        render_analytics_page()
    elif active_page == "Settings":
        render_settings_page()
    else:
        render_workspace_page()


if __name__ == "__main__":
    main()
