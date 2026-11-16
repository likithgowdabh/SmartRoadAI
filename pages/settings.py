"""
SmartRoad AI — Settings & Priority Engine Configuration
Customizes priority equation weights, system thresholds, and cloud database connections.
"""

import streamlit as st
from components.ui import render_page_header, render_badge, render_html
from components.icons import get_icon
from database.db import db
from ai.detector import PotholeDetector

def render_settings_page(user_session: dict):
    """Renders the settings and system configuration view."""
    render_html(render_page_header(
        title="Settings",
        subtitle="Configure the multi-factor priority engine, database parameters, and AI model paths."
    ))

    settings = db.get_system_settings()

    # 1. Priority Engine Tuning
    render_html("""
    <div style="font-size: 16px; font-weight: 600; color: #1D1D1F; margin-bottom: 4px;">
        Municipal Priority Equation Weights
    </div>
    <p style="font-size: 13px; color: #6E6E73; margin-bottom: 14px;">
        Priority = (W₁ × Severity) + (W₂ × Traffic) + (W₃ × Repeat Reports) + (W₄ × Safety Risk)
    </p>
    """)

    cur_sev = float(settings.get("weight_severity", "0.40"))
    cur_traf = float(settings.get("weight_traffic", "0.30"))
    cur_rep = float(settings.get("weight_repeat", "0.20"))
    cur_safe = float(settings.get("weight_safety", "0.10"))

    with st.form("priority_weights_form"):
        w1, w2 = st.columns(2)
        with w1:
            new_sev = st.slider("Severity Factor Weight (W₁)", 0.0, 1.0, cur_sev, 0.05)
            new_traf = st.slider("Traffic Volume Weight (W₂)", 0.0, 1.0, cur_traf, 0.05)
        with w2:
            new_rep = st.slider("Citizen Repeat Frequency Weight (W₃)", 0.0, 1.0, cur_rep, 0.05)
            new_safe = st.slider("Hazard Safety Risk Weight (W₄)", 0.0, 1.0, cur_safe, 0.05)

        total_weight = round(new_sev + new_traf + new_rep + new_safe, 2)
        if total_weight != 1.0:
            st.warning(f"Sum of weights is currently {total_weight}. Standard practice recommends weights sum to 1.0.")
        else:
            st.success(f"Weights sum to 1.00 (Balanced Distribution)")

        if user_session.get("role") == "admin":
            if st.form_submit_button("Save Weights & Recalculate Active Incidents", type="primary"):
                db.update_system_setting("weight_severity", str(new_sev), changed_by=user_session.get("full_name", "Admin"))
                db.update_system_setting("weight_traffic", str(new_traf), changed_by=user_session.get("full_name", "Admin"))
                db.update_system_setting("weight_repeat", str(new_rep), changed_by=user_session.get("full_name", "Admin"))
                db.update_system_setting("weight_safety", str(new_safe), changed_by=user_session.get("full_name", "Admin"))
                st.success("Priority engine configuration updated. Audit record logged.")
                st.rerun()
        else:
            st.info("Priority formula tuning is restricted to System Administrators.")

    render_html("<div style='height: 24px;'></div>")

    # 2. System Diagnostics & Cloud Persistence Status
    render_html("""
    <div style="font-size: 16px; font-weight: 600; color: #1D1D1F; margin-bottom: 8px;">
        Infrastructure Diagnostics
    </div>
    """)

    d1, d2 = st.columns(2)
    with d1:
        render_html(f"""
        <div class="apple-card" style="padding: 18px;">
            <div style="font-size: 14px; font-weight: 600; color: #1D1D1F; margin-bottom: 8px;">Database & Storage Engine</div>
            <div style="font-size: 13px; color: #6E6E73; margin-bottom: 4px;">
                <strong>Active Backend:</strong> {'Supabase PostgreSQL (Cloud)' if db.use_supabase else 'Local SQLite (Full ACID WAL)'}
            </div>
            <div style="font-size: 13px; color: #6E6E73; margin-bottom: 4px;">
                <strong>Database Path:</strong> <code>database/smartroad.db</code>
            </div>
            <div style="font-size: 13px; color: #6E6E73;">
                <strong>RLS Status:</strong> Enforced on Supabase / Simulated in SQLite
            </div>
        </div>
        """)

    with d2:
        det = PotholeDetector()
        det_status = det.get_system_status()
        render_html(f"""
        <div class="apple-card" style="padding: 18px;">
            <div style="font-size: 14px; font-weight: 600; color: #1D1D1F; margin-bottom: 8px;">Computer Vision Engine</div>
            <div style="font-size: 13px; color: #6E6E73; margin-bottom: 4px;">
                <strong>YOLO11 Runtime:</strong> {'Loaded & Ready' if det_status['yolo_installed'] else 'CV Engine Fallback Active'}
            </div>
            <div style="font-size: 13px; color: #6E6E73; margin-bottom: 4px;">
                <strong>Weights Path:</strong> <code>models/pothole_best.pt</code>
            </div>
            <div style="font-size: 13px; color: #6E6E73;">
                <strong>Weights Present:</strong> {'Yes' if det_status['weights_exist'] else 'Awaiting Training (Follow Guide)'}
            </div>
        </div>
        """)
