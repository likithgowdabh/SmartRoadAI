"""
SmartRoad AI — Overview Dashboard (Apple Inspired)
Visualizes live infrastructure metrics, severity distribution, and repair progress.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from components.ui import render_page_header, render_metric_card, render_badge, render_html
from database.db import db

def render_overview_page(navigate_to_fn):
    """Renders the executive operations dashboard."""
    render_html(render_page_header(
        title="Overview",
        subtitle="Road infrastructure monitoring and maintenance activity."
    ))

    metrics = db.get_summary_metrics()

    # 1. Metric Cards Row
    m1, m2, m3, m4 = st.columns(4)
    with m1:
        render_html(render_metric_card(
            title="Total Reports",
            value=metrics["total_reports"],
            subtitle="All logged incidents",
            icon="clipboard-list",
            status="default"
        ))
    with m2:
        render_html(render_metric_card(
            title="Critical Damage",
            value=metrics["critical_damage"],
            subtitle="Immediate repair required",
            icon="alert-triangle",
            status="critical"
        ))
    with m3:
        render_html(render_metric_card(
            title="Under Inspection",
            value=metrics["under_inspection"],
            subtitle="Field engineer assigned",
            icon="scan-search",
            status="warning"
        ))
    with m4:
        render_html(render_metric_card(
            title="Completed Repairs",
            value=metrics["completed_repairs"],
            subtitle="Restored & verified roads",
            icon="check-circle-2",
            status="success"
        ))

    render_html("<div style='height: 24px;'></div>")

    # Fetch live reports for visualization
    reports = db.get_reports(limit=100)
    if not reports:
        st.info("No road report data found in database.")
        return

    df = pd.DataFrame(reports)

    # 2. Charts Row: Damage Over Time & Severity Distribution
    col_chart1, col_chart2 = st.columns([1.6, 1.2])

    with col_chart1:
        render_html("""
        <div style="font-size: 15px; font-weight: 600; color: #1D1D1F; margin-bottom: 8px;">
            Road Damage Reports Over Time
        </div>
        """)

        # Build timeline series
        df["date"] = pd.to_datetime(df["created_at"]).dt.date
        timeline_df = df.groupby(["date", "severity"]).size().reset_index(name="count")

        fig_time = px.area(
            timeline_df,
            x="date",
            y="count",
            color="severity",
            color_discrete_map={
                "Critical": "#D70015",
                "Medium": "#B87900",
                "Low": "#248A3D"
            }
        )
        fig_time.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            margin=dict(l=0, r=0, t=10, b=0),
            height=280,
            font=dict(family="-apple-system, BlinkMacSystemFont, 'SF Pro Text', sans-serif", size=12, color="#6E6E73"),
            xaxis=dict(showgrid=True, gridcolor="#E5E5EA", zeroline=False),
            yaxis=dict(showgrid=True, gridcolor="#E5E5EA", zeroline=False),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )
        st.plotly_chart(fig_time, use_container_width=True)

    with col_chart2:
        render_html("""
        <div style="font-size: 15px; font-weight: 600; color: #1D1D1F; margin-bottom: 8px;">
            Severity Distribution
        </div>
        """)

        sev_counts = df["severity"].value_counts().reset_index()
        sev_counts.columns = ["severity", "count"]

        fig_donut = px.pie(
            sev_counts,
            values="count",
            names="severity",
            hole=0.68,
            color="severity",
            color_discrete_map={
                "Critical": "#D70015",
                "Medium": "#B87900",
                "Low": "#248A3D"
            }
        )
        fig_donut.update_traces(textinfo="percent", hoverinfo="label+value+percent")
        fig_donut.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            margin=dict(l=0, r=0, t=10, b=0),
            height=280,
            font=dict(family="-apple-system, BlinkMacSystemFont, 'SF Pro Text', sans-serif", size=12, color="#6E6E73"),
            legend=dict(orientation="h", yanchor="bottom", y=-0.1, xanchor="center", x=0.5)
        )
        st.plotly_chart(fig_donut, use_container_width=True)

    render_html("<div style='height: 16px;'></div>")

    # 3. Operations Progress & Corridor Distribution
    col_prog1, col_prog2 = st.columns([1.4, 1.4])

    with col_prog1:
        render_html("""
        <div style="font-size: 15px; font-weight: 600; color: #1D1D1F; margin-bottom: 8px;">
            Maintenance Lifecycle Status
        </div>
        """)

        status_order = ["Reported", "Under Inspection", "Scheduled", "In Progress", "Repaired", "Verified"]
        status_counts = df["status"].value_counts().reindex(status_order, fill_value=0).reset_index()
        status_counts.columns = ["status", "count"]

        fig_bar = px.bar(
            status_counts,
            x="count",
            y="status",
            orientation="h",
            color="status",
            color_discrete_sequence=["#6E6E73", "#B87900", "#0071E3", "#0077ED", "#248A3D", "#1E6F31"]
        )
        fig_bar.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            margin=dict(l=0, r=0, t=10, b=0),
            height=260,
            showlegend=False,
            font=dict(family="-apple-system, BlinkMacSystemFont, 'SF Pro Text', sans-serif", size=12, color="#6E6E73"),
            xaxis=dict(showgrid=True, gridcolor="#E5E5EA", zeroline=False),
            yaxis=dict(showgrid=False, zeroline=False)
        )
        st.plotly_chart(fig_bar, use_container_width=True)

    with col_prog2:
        render_html("""
        <div style="font-size: 15px; font-weight: 600; color: #1D1D1F; margin-bottom: 8px;">
            Corridor & Zone Density
        </div>
        """)

        area_counts = df["area"].value_counts().reset_index()
        area_counts.columns = ["area", "count"]

        fig_area = px.bar(
            area_counts,
            x="area",
            y="count",
            color_discrete_sequence=["#0071E3"]
        )
        fig_area.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            margin=dict(l=0, r=0, t=10, b=0),
            height=260,
            font=dict(family="-apple-system, BlinkMacSystemFont, 'SF Pro Text', sans-serif", size=12, color="#6E6E73"),
            xaxis=dict(showgrid=False),
            yaxis=dict(showgrid=True, gridcolor="#E5E5EA", zeroline=False)
        )
        st.plotly_chart(fig_area, use_container_width=True)

    render_html("<div style='height: 24px;'></div>")

    # 4. Top Critical Priority Incidents Table
    render_html("""
    <div style="display: flex; justify-content: space-between; align-items: baseline; margin-bottom: 12px;">
        <div style="font-size: 16px; font-weight: 600; color: #1D1D1F;">
            High-Priority Action Queue
        </div>
        <div style="font-size: 12px; color: #6E6E73;">
            Calculated via AI Severity & Traffic Impact
        </div>
    </div>
    """)

    top_reports = df.sort_values(by="priority_score", ascending=False).head(5)
    for _, r in top_reports.iterrows():
        sev_class = r["severity"].lower()
        badge_html = render_badge(r["severity"], variant=sev_class)
        status_badge = render_badge(r["status"], variant="accent" if r["status"] == "In Progress" else "neutral")

        render_html(f"""
        <div class="apple-card" style="padding: 14px 18px; margin-bottom: 8px; display: flex; justify-content: space-between; align-items: center;">
            <div style="flex-grow: 1;">
                <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 4px;">
                    <span style="font-family: monospace; font-size: 11.5px; font-weight: 600; color: #0071E3;">{r['id']}</span>
                    {badge_html}
                    {status_badge}
                    <span style="font-size: 12px; color: #86868B;">• Priority Score: <strong>{r['priority_score']}</strong></span>
                </div>
                <div style="font-size: 14px; font-weight: 600; color: #1D1D1F;">{r['road_name']}</div>
                <div style="font-size: 12.5px; color: #6E6E73;">{r['area']}, {r['city']} — {r['title']}</div>
            </div>
            <div style="text-align: right;">
                <div style="font-size: 12px; color: #86868B;">Traffic: {r['traffic_level']}</div>
                <div style="font-size: 12px; color: #86868B;">Repeats: {r['repeat_count']} reports</div>
            </div>
        </div>
        """)
