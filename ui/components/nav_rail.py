"""
ATTACHORA Narrow Navigation Rail Component
76px wide vertical navigation rail with monochrome vector line icons matching the reference image.
"""

import streamlit as st

NAV_ITEMS = [
    {
        "id": "Queue",
        "title": "Attachment Queue",
        "svg": '<polygon points="12 2 2 7 12 12 22 7 12 2"></polygon><polyline points="2 17 12 22 22 17"></polyline><polyline points="2 12 12 17 22 12"></polyline>',
    },
    {
        "id": "Mailbox",
        "title": "Email Connections & Import",
        "svg": '<path d="M4 4h16c1.1 0 2 .9 2 2v12c0 1.1-.9 2-2 2H4c-1.1 0-2-.9-2-2V6c0-1.1.9-2 2-2z"></path><polyline points="22,6 12,13 2,6"></polyline>',
    },
    {
        "id": "Integrity",
        "title": "Integrity & Archive Security",
        "svg": '<path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"></path><polyline points="9 12 11 14 15 10"></polyline>',
    },
    {
        "id": "Rules",
        "title": "Smart Filing Rules",
        "svg": '<path d="M22 19a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h5l2 3h9a2 2 0 0 1 2 2z"></path><line x1="12" y1="11" x2="12" y2="17"></line><line x1="9" y1="14" x2="15" y2="14"></line>',
    },
    {
        "id": "Library",
        "title": "Organized Library Explorer",
        "svg": '<path d="M22 19a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h5l2 3h9a2 2 0 0 1 2 2z"></path>',
    },
    {
        "id": "History",
        "title": "Operation Audit Trail",
        "svg": '<circle cx="12" cy="12" r="10"></circle><polyline points="12 6 12 12 16 14"></polyline>',
    },
    {
        "id": "Analytics",
        "title": "Operational Analytics",
        "svg": '<line x1="18" y1="20" x2="18" y2="10"></line><line x1="12" y1="20" x2="12" y2="4"></line><line x1="6" y1="20" x2="6" y2="14"></line>',
    },
    {
        "id": "Settings",
        "title": "System Settings",
        "svg": '<circle cx="12" cy="12" r="3"></circle><path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1 0 2.83 2 2 0 0 1-2.83 0l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-2 2 2 2 0 0 1-2-2v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83 0 2 2 0 0 1 0-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1-2-2 2 2 0 0 1 2-2h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 0-2.83 2 2 0 0 1 2.83 0l.06.06a1.65 1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 2-2 2 2 0 0 1 2 2v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 0 2 2 0 0 1 0 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 2 2 2 2 0 0 1-2 2h-.09a1.65 1.65 0 0 0-1.51 1z"></path>',
    },
]


def render_nav_rail() -> str:
    """Renders the 76px vertical navigation rail and returns the active page identifier."""
    # Check if query parameter specifies page
    if "page" in st.query_params and st.query_params["page"]:
        st.session_state["active_page"] = st.query_params["page"]

    current = st.session_state.get("active_page", "Queue")

    with st.sidebar:
        # ATTACHORA Brand Logo Mark
        st.markdown(
            """
            <div style="width:100%; display:flex; justify-content:center; margin-bottom:14px;">
                <div style="width:42px; height:42px; background-color:#286B50; border-radius:8px; display:flex; align-items:center; justify-content:center; box-shadow:0 2px 5px rgba(40,107,80,0.25);">
                    <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="#FFFFFF" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
                        <polygon points="12 2 2 22 22 22 12 2"></polygon>
                    </svg>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        # Render each icon link
        items_html = ['<div style="display:flex; flex-direction:column; align-items:center; gap:6px;">']
        for item in NAV_ITEMS:
            item_id = item["id"]
            is_active = (current == item_id or (current == "Workspace" and item_id == "Queue"))
            active_class = "active" if is_active else ""
            stroke_color = "#FFFFFF" if is_active else "#66716B"

            link_html = f"""
            <a href="?page={item_id}" target="_self" class="nav-icon-link {active_class}" title="{item['title']}">
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="{stroke_color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                    {item['svg']}
                </svg>
            </a>
            """
            items_html.append(link_html)

        items_html.append("</div>")
        st.markdown("\n".join(items_html), unsafe_allow_html=True)

    return current
