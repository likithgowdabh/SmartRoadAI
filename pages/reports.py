"""
SmartRoad AI — Road Reports Interface (Apple Inspired)
Data table, multi-parameter filtering, inspection detail modal, and workflow management.
"""

import os
import streamlit as st
import pandas as pd
from PIL import Image
from components.ui import render_page_header, render_badge, render_card, render_html
from components.icons import get_icon
from database.db import db
from services.export_service import export_reports_to_csv, export_reports_to_json

def render_reports_page(user_session: dict):
    """Renders the comprehensive road reports interface."""
    render_html(render_page_header(
        title="Road Reports",
        subtitle="Manage, inspect, and update municipal road damage reports."
    ))

    # Top Filter & Action Bar
    f1, f2, f3, f4 = st.columns([2, 1.2, 1.2, 1.4])
    with f1:
        search_query = st.text_input("Search reports", placeholder="Search by road, area, or description...", label_visibility="collapsed")
    with f2:
        sev_filter = st.selectbox("Severity", ["All", "Critical", "Medium", "Low"], label_visibility="collapsed")
    with f3:
        status_filter = st.selectbox("Status", ["All", "Reported", "Under Inspection", "Scheduled", "In Progress", "Repaired", "Verified"], label_visibility="collapsed")
    with f4:
        sort_by = st.selectbox("Sort By", ["Highest Priority", "Newest First", "Oldest First"], label_visibility="collapsed")

    # Fetch filtered data
    all_reports = db.get_reports(
        severity=sev_filter,
        status=status_filter,
        search_query=search_query if search_query else None
    )

    if not all_reports:
        render_html(f"""
        <div class="apple-card" style="text-align: center; padding: 40px 20px;">
            <div style="margin-bottom: 10px;">{get_icon("clipboard-list", size=32, color="#86868B")}</div>
            <h3 style="font-size: 16px; font-weight: 600; color: #1D1D1F; margin-bottom: 4px;">No Matching Reports Found</h3>
            <p style="font-size: 13.5px; color: #6E6E73; margin: 0;">Try adjusting your search criteria or clear the filters.</p>
        </div>
        """)
        return

    # Sorting
    if sort_by == "Highest Priority":
        all_reports.sort(key=lambda x: x["priority_score"], reverse=True)
    elif sort_by == "Newest First":
        all_reports.sort(key=lambda x: x["created_at"], reverse=True)
    elif sort_by == "Oldest First":
        all_reports.sort(key=lambda x: x["created_at"])

    # Export toolbar
    exp1, exp2, _ = st.columns([1, 1, 3])
    with exp1:
        csv_data = export_reports_to_csv(all_reports)
        st.download_button(
            label="Export CSV",
            data=csv_data,
            file_name="smartroad_reports.csv",
            mime="text/csv",
            use_container_width=True
        )
    with exp2:
        json_data = export_reports_to_json(all_reports)
        st.download_button(
            label="Export JSON",
            data=json_data,
            file_name="smartroad_reports.json",
            mime="application/json",
            use_container_width=True
        )

    render_html("<div style='height: 12px;'></div>")

    # Render Report Cards with Expandable Details
    for report in all_reports:
        r_id = report["id"]
        sev = report["severity"]
        status = report["status"]
        prio = report["priority_score"]
        road = report["road_name"]
        area = report["area"]
        city = report["city"]
        created = str(report["created_at"])[:10]

        sev_badge = render_badge(sev, variant=sev.lower())
        status_variant = "success" if status in ["Repaired", "Verified"] else ("accent" if status == "In Progress" else "neutral")
        status_badge = render_badge(status, variant=status_variant)

        with st.expander(f"{r_id} — {road} ({area}) | Priority: {prio} | {sev}"):
            c_left, c_right = st.columns([1.2, 1.8])

            with c_left:
                st.markdown(f"**Photographic Evidence**")
                img_path = report.get("annotated_image_url") or report.get("image_url")
                if img_path and os.path.exists(img_path):
                    st.image(img_path, caption=f"Evidence for {r_id}", use_column_width=True)
                else:
                    render_html("""
                    <div style="background: #F5F5F7; border: 1px dashed #D2D2D7; border-radius: 8px; height: 180px; display: flex; align-items: center; justify-content: center; color: #86868B; font-size: 13px;">
                        No photographic capture attached
                    </div>
                    """)

                render_html(f"""
                <div style="font-size: 12.5px; color: #6E6E73; margin-top: 10px;">
                    <div><strong>GPS Coordinates:</strong> {report['latitude']}, {report['longitude']}</div>
                    <div><strong>Citizen ID:</strong> {report.get('citizen_id') or 'Anonymous Citizen'}</div>
                    <div><strong>Logged Date:</strong> {created}</div>
                </div>
                """)

            with c_right:
                st.markdown(f"### {report['title']}")
                st.markdown(f"<p style='color: #6E6E73; font-size: 14px;'>{report.get('description') or 'No citizen description provided.'}</p>", unsafe_allow_html=True)

                render_html(f"""
                <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 10px; background: #FAFAFC; padding: 12px; border-radius: 8px; border: 1px solid #E5E5EA; margin-bottom: 14px;">
                    <div>
                        <div style="font-size: 11px; color: #86868B; text-transform: uppercase;">Severity</div>
                        <div>{sev_badge}</div>
                    </div>
                    <div>
                        <div style="font-size: 11px; color: #86868B; text-transform: uppercase;">Priority Score</div>
                        <div style="font-size: 18px; font-weight: 600; color: #1D1D1F;">{prio}</div>
                    </div>
                    <div>
                        <div style="font-size: 11px; color: #86868B; text-transform: uppercase;">Status</div>
                        <div>{status_badge}</div>
                    </div>
                    <div>
                        <div style="font-size: 11px; color: #86868B; text-transform: uppercase;">Traffic Level</div>
                        <div style="font-size: 13.5px; font-weight: 500;">{report.get('traffic_level', 'Medium')}</div>
                    </div>
                    <div>
                        <div style="font-size: 11px; color: #86868B; text-transform: uppercase;">Repeat Reports</div>
                        <div style="font-size: 13.5px; font-weight: 500;">{report.get('repeat_count', 1)} times</div>
                    </div>
                    <div>
                        <div style="font-size: 11px; color: #86868B; text-transform: uppercase;">Pothole Count</div>
                        <div style="font-size: 13.5px; font-weight: 500;">{report.get('detection_count', 0)} detected</div>
                    </div>
                </div>
                """)

                # Status update form (Role-based: Staff & Admin)
                can_update = user_session.get("role") in ["inspector", "maintenance_manager", "admin"]
                if can_update:
                    st.markdown("**Update Inspection & Operational Status**")
                    with st.form(key=f"form_update_{r_id}"):
                        u_col1, u_col2 = st.columns(2)
                        with u_col1:
                            new_status = st.selectbox(
                                "Workflow Status",
                                ["Reported", "Under Inspection", "Scheduled", "In Progress", "Repaired", "Verified"],
                                index=["Reported", "Under Inspection", "Scheduled", "In Progress", "Repaired", "Verified"].index(status)
                            )
                        with u_col2:
                            new_assigned = st.text_input("Assigned Inspector / Lead", value=report.get("assigned_to") or "")

                        new_notes = st.text_area("Inspection Notes", value=report.get("inspector_notes") or "", height=70)
                        
                        submit_btn = st.form_submit_button("Save Status Update")
                        if submit_btn:
                            updates = {
                                "status": new_status,
                                "assigned_to": new_assigned,
                                "inspector_notes": new_notes
                            }
                            db.update_report(r_id, updates, changed_by=user_session.get("full_name", "Staff"))
                            st.success(f"Report {r_id} updated successfully.")
                            st.rerun()
                else:
                    if report.get("inspector_notes"):
                        st.markdown(f"**Inspector Notes:** {report['inspector_notes']}")
