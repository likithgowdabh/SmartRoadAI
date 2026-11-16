"""
SmartRoad AI — Interactive Road Intelligence Map
Leaflet map with CartoDB Positron tiles, severity pins, and incident detail inspector.
"""

import streamlit as st
import streamlit.components.v1 as components
from components.ui import render_page_header, render_badge, render_html
from components.icons import get_icon
from components.map_component import render_apple_road_map
from database.db import db

def render_map_page():
    """Renders the GIS road damage monitoring view."""
    render_html(render_page_header(
        title="Road Map",
        subtitle="Geospatial distribution of road hazards and active repair zones."
    ))

    # Filter Toolbar
    mf1, mf2, mf3 = st.columns([2, 1.2, 1.2])
    with mf1:
        loc_search = st.text_input("Filter Location", placeholder="Filter by road name or ward...", label_visibility="collapsed")
    with mf2:
        map_sev = st.selectbox("Severity Filter", ["All", "Critical", "Medium", "Low"], label_visibility="collapsed")
    with mf3:
        map_status = st.selectbox("Status Filter", ["All", "Reported", "Under Inspection", "Scheduled", "In Progress", "Repaired", "Verified"], label_visibility="collapsed")

    # Fetch reports
    reports = db.get_reports(
        severity=map_sev,
        status=map_status,
        search_query=loc_search if loc_search else None
    )

    if not reports:
        st.warning("No road incidents match current map filter criteria.")
        return

    # Visual Legend
    render_html(f"""
    <div style="display: flex; gap: 20px; align-items: center; margin-bottom: 12px; font-size: 12.5px; color: #6E6E73;">
        <span style="display: inline-flex; align-items: center; gap: 6px;">
            <span style="width: 10px; height: 10px; border-radius: 50%; background: #D70015;"></span> Critical Hazard
        </span>
        <span style="display: inline-flex; align-items: center; gap: 6px;">
            <span style="width: 10px; height: 10px; border-radius: 50%; background: #B87900;"></span> Medium Severity
        </span>
        <span style="display: inline-flex; align-items: center; gap: 6px;">
            <span style="width: 10px; height: 10px; border-radius: 50%; background: #248A3D;"></span> Low Severity
        </span>
        <span style="display: inline-flex; align-items: center; gap: 6px;">
            <span style="width: 10px; height: 10px; border-radius: 50%; background: #0071E3;"></span> Restored / Repaired
        </span>
        <span style="margin-left: auto; color: #86868B;">Showing {len(reports)} monitored incidents</span>
    </div>
    """)

    # Render Leaflet Map
    map_html = render_apple_road_map(reports, center_lat=12.9450, center_lon=77.6250, zoom=12, height=520)
    components.html(map_html, height=530)

    # Side-by-side Inspector Panel below the map
    render_html("<div style='height: 20px;'></div>")
    render_html("""
    <div style="font-size: 16px; font-weight: 600; color: #1D1D1F; margin-bottom: 8px;">
        Selected Road Incident Detail
    </div>
    """)

    # Selectbox for detailed inspection
    rep_choices = {f"{r['id']} — {r['road_name']} ({r['area']}) | Priority {r['priority_score']}": r for r in reports}
    chosen_label = st.selectbox("Inspect Incident", list(rep_choices.keys()), label_visibility="collapsed")
    selected_rep = rep_choices[chosen_label]

    det1, det2, det3 = st.columns([1, 1, 1])
    with det1:
        st.markdown(f"**Location:** {selected_rep['road_name']}")
        st.markdown(f"**Ward / Area:** {selected_rep['area']}, {selected_rep['city']}")
        st.markdown(f"**GPS:** `{selected_rep['latitude']}, {selected_rep['longitude']}`")
    with det2:
        render_html(f"<div><strong>Severity:</strong> {render_badge(selected_rep['severity'], variant=selected_rep['severity'].lower())}</div>")
        st.markdown(f"**Priority Score:** `{selected_rep['priority_score']}`")
        st.markdown(f"**Traffic Level:** {selected_rep.get('traffic_level', 'Medium')}")
    with det3:
        render_html(f"<div><strong>Workflow Status:</strong> {render_badge(selected_rep['status'], variant='accent' if selected_rep['status'] == 'In Progress' else 'neutral')}</div>")
        st.markdown(f"**Assigned Inspector:** {selected_rep.get('assigned_to') or 'Unassigned'}")
        st.markdown(f"**Logged At:** {str(selected_rep['created_at'])[:10]}")
