"""
SmartRoad AI — Final Master Application
Tagline: Better Roads. Smarter Cities.
Apple-Inspired Road Intelligence & Maintenance Management Platform.
"""

import os
import sys
import types

# Ensure ultralytics git sandboxing protection
if "ultralytics.utils.git" not in sys.modules:
    git_mod = types.ModuleType("ultralytics.utils.git")
    class DummyGitRepo:
        root = None
        gitdir = None
        refdir = None
        head = None
        ref = None
        commit = None
        is_repo = False
        def __init__(self, *args, **kwargs):
            pass
    git_mod.GitRepo = DummyGitRepo
    sys.modules["ultralytics.utils.git"] = git_mod

import streamlit as st
from PIL import Image

# Determine page icon from user 3D logo
icon_path = "assets/logo.png"
if os.path.exists(icon_path):
    try:
        app_icon = Image.open(icon_path)
    except Exception:
        app_icon = "assets/logo.png"
else:
    app_icon = "🛣️"

# Configure Streamlit page settings
st.set_page_config(
    page_title="SmartRoad AI — Road Intelligence Platform",
    page_icon=app_icon,
    layout="wide",
    initial_sidebar_state="expanded"
)

# Inject Apple Design System CSS
from styles.apple_theme import inject_apple_theme
inject_apple_theme()

from components.icons import get_icon, icon_text
from components.ui import render_html, get_base64_image
from services.auth_service import DEMO_ACCOUNTS, verify_credentials
from database.db import db

# Page Modules
from pages.landing import render_landing_page
from pages.overview import render_overview_page
from pages.reports import render_reports_page
from pages.detection import render_detection_page
from pages.map_view import render_map_page
from pages.maintenance import render_maintenance_page
from pages.analytics import render_analytics_page
from pages.citizen_portal import render_citizen_portal
from pages.users_admin import render_users_admin_page
from pages.settings import render_settings_page

# Session State Initialization
def get_session_state_safe(key: str, default=None):
    try:
        if key not in st.session_state:
            st.session_state[key] = default
        return st.session_state[key]
    except Exception:
        return default

def set_session_state_safe(key: str, value):
    try:
        st.session_state[key] = value
    except Exception:
        pass

# Ensure defaults
get_session_state_safe("current_page", "landing")
get_session_state_safe("user", {
    "id": "usr-admin-1",
    "email": "admin@smartroad.ai",
    "full_name": "Sophia Sterling",
    "role": "admin",
    "department": "City Roads & Works Executive"
})

def navigate_to(page_name: str):
    set_session_state_safe("current_page", page_name)
    try:
        st.rerun()
    except Exception:
        pass

current_user = get_session_state_safe("user", {
    "id": "usr-admin-1",
    "email": "admin@smartroad.ai",
    "full_name": "Sophia Sterling",
    "role": "admin",
    "department": "City Roads & Works Executive"
})
active_page = get_session_state_safe("current_page", "landing")

# --- SIDEBAR NAVIGATION (Apple macOS Sequoia Inspired) ---
with st.sidebar:
    # Logo & Brand Header with User's Uploaded 3D App Icon
    logo_b64 = get_base64_image("assets/logo.png")
    if logo_b64:
        logo_brand_html = f'<img src="{logo_b64}" style="width: 38px; height: 38px; border-radius: 9px; box-shadow: 0 4px 12px rgba(0, 113, 227, 0.28); object-fit: cover; flex-shrink: 0;" alt="SmartRoad AI" />'
    else:
        logo_brand_html = f'<div style="width: 38px; height: 38px; border-radius: 9px; background: #0071E3; display: flex; align-items: center; justify-content: center; color: white;">{get_icon("scan-search", size=20, color="#FFFFFF")}</div>'

    render_html(f"""
    <div style="display: flex; align-items: center; gap: 11px; padding: 2px 4px 14px 4px; border-bottom: 1px solid #E5E5EA; margin-bottom: 12px;">
        {logo_brand_html}
        <div>
            <div style="font-size: 15.5px; font-weight: 700; letter-spacing: -0.025em; color: #1D1D1F; line-height: 1.15;">SmartRoad AI</div>
            <div style="font-size: 11px; color: #86868B; letter-spacing: -0.01em;">Road Intelligence</div>
        </div>
    </div>
    """)

    # Navigation Links Configuration
    nav_items = [
        ("landing", "Product Home", "sparkles"),
        ("overview", "Overview", "layout-dashboard"),
        ("reports", "Road Reports", "clipboard-list"),
        ("detection", "AI Detection", "scan-search"),
        ("map_view", "Road Map", "map-pinned"),
        ("maintenance", "Maintenance", "wrench"),
        ("analytics", "Analytics", "chart-no-axes-combined"),
        ("citizen_portal", "Citizen Portal", "cloud-upload"),
        ("users_admin", "Administration", "users"),
        ("settings", "Settings", "settings"),
    ]

    for page_key, label, icon_name in nav_items:
        is_active = (active_page == page_key)
        btn_type = "primary" if is_active else "secondary"
        
        # Display active pill
        if st.button(
            f"{'● ' if is_active else '   '}{label}",
            key=f"nav_{page_key}",
            type=btn_type,
            use_container_width=True
        ):
            navigate_to(page_key)

    render_html("<div style='height: 28px;'></div>")

    # Active User Profile Card & Fast Switcher
    render_html("""
    <div style="border-top: 1px solid #E5E5EA; padding-top: 14px; margin-bottom: 8px;">
        <div style="font-size: 11px; font-weight: 600; text-transform: uppercase; color: #86868B; letter-spacing: 0.04em; margin-bottom: 6px;">
            Simulate Persona / Role
        </div>
    </div>
    """)

    role_options = {
        "Sophia Sterling (Admin)": DEMO_ACCOUNTS[0],
        "Marcus Vance (Manager)": DEMO_ACCOUNTS[1],
        "Elena Rostova (Inspector)": DEMO_ACCOUNTS[2],
        "Devon Carter (Citizen)": DEMO_ACCOUNTS[3],
    }
    
    current_user_name = current_user.get("full_name", "")
    current_selection_index = 0
    for idx, key in enumerate(role_options.keys()):
        if current_user_name in key:
            current_selection_index = idx
            break

    selected_account_name = st.selectbox(
        "Active User",
        list(role_options.keys()),
        index=current_selection_index,
        label_visibility="collapsed"
    )
    
    chosen_account = role_options[selected_account_name]
    if chosen_account["email"] != current_user["email"]:
        new_u = {
            "id": f"usr-{chosen_account['role'][:3]}",
            "email": chosen_account["email"],
            "full_name": chosen_account["name"],
            "role": chosen_account["role"],
            "department": chosen_account["department"]
        }
        set_session_state_safe("user", new_u)
        try:
            st.rerun()
        except Exception:
            pass

    # User Profile Pill
    render_html(f"""
    <div style="background: #FFFFFF; border: 1px solid #E5E5EA; border-radius: 10px; padding: 10px 12px; margin-top: 10px; display: flex; align-items: center; gap: 10px;">
        <div style="width: 32px; height: 32px; border-radius: 50%; background: #0071E3; color: white; display: flex; align-items: center; justify-content: center; font-size: 12px; font-weight: 600;">
            {current_user['full_name'][0]}
        </div>
        <div style="overflow: hidden;">
            <div style="font-size: 13px; font-weight: 600; color: #1D1D1F; white-space: nowrap; text-overflow: ellipsis; overflow: hidden;">{current_user['full_name']}</div>
            <div style="font-size: 11px; color: #6E6E73; text-transform: capitalize;">{current_user['role'].replace('_', ' ')}</div>
        </div>
    </div>
    """)

# --- MAIN CONTENT ROUTER ---
active = active_page

if active == "landing":
    render_landing_page(navigate_to)
elif active == "overview":
    render_overview_page(navigate_to)
elif active == "reports":
    render_reports_page(current_user)
elif active == "detection":
    render_detection_page(current_user)
elif active == "map_view":
    render_map_page()
elif active == "maintenance":
    render_maintenance_page(current_user)
elif active == "analytics":
    render_analytics_page()
elif active == "citizen_portal":
    render_citizen_portal(current_user)
elif active == "users_admin":
    render_users_admin_page(current_user)
elif active == "settings":
    render_settings_page(current_user)
else:
    render_overview_page(navigate_to)
