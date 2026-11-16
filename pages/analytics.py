"""
SmartRoad AI — Analytics & Municipal Road Intelligence
Longitudinal trends, ward risk profiling, budget efficiency, and infrastructure insights.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from components.ui import render_page_header, render_metric_card, render_html
from database.db import db

def render_analytics_page():
    """Renders the high-level intelligence and trends analytics."""
    render_html(render_page_header(
        title="Analytics",
        subtitle="Empirical performance benchmarks, risk indexing, and operational efficiency."
    ))

    reports = db.get_reports(limit=500)
    tasks = db.get_maintenance_tasks()

    if not reports:
        st.info("Insufficient telemetry data for analytics.")
        return

    df_rep = pd.DataFrame(reports)
    df_tsk = pd.DataFrame(tasks) if tasks else pd.DataFrame()

    # KPI summary
    avg_prio = round(df_rep["priority_score"].mean(), 1)
    repeat_rate = round((df_rep[df_rep["repeat_count"] > 1].shape[0] / max(1, df_rep.shape[0])) * 100, 1)
    resolution_rate = round((df_rep[df_rep["status"].isin(["Repaired", "Verified"])].shape[0] / max(1, df_rep.shape[0])) * 100, 1)
    
    total_budget = df_tsk["budget_estimate"].sum() if not df_tsk.empty else 0.0
    total_actual = df_tsk["cost_actual"].sum() if not df_tsk.empty else 0.0
    budget_variance = round(((total_actual - total_budget) / max(1.0, total_budget)) * 100, 1)

    ak1, ak2, ak3, ak4 = st.columns(4)
    with ak1:
        render_html(render_metric_card(
            title="Average Priority",
            value=avg_prio,
            subtitle="Municipal hazard scale",
            icon="sliders-horizontal",
            status="default"
        ))
    with ak2:
        render_html(render_metric_card(
            title="Recurrence Rate",
            value=f"{repeat_rate}%",
            subtitle="Multi-reported hazards",
            icon="alert-circle",
            status="warning"
        ))
    with ak3:
        render_html(render_metric_card(
            title="Resolution Index",
            value=f"{resolution_rate}%",
            subtitle="Pavement restored",
            icon="check-circle-2",
            status="success"
        ))
    with ak4:
        render_html(render_metric_card(
            title="Budget Utilization",
            value=f"${total_actual:,.0f}",
            subtitle=f"{budget_variance}% vs allocated",
            icon="wrench",
            status="default"
        ))

    render_html("<div style='height: 24px;'></div>")

    # Visualizations: Priority Correlation & Ward Breakdown
    an_c1, an_c2 = st.columns([1.5, 1.5])
    with an_c1:
        render_html("""
        <div style="font-size: 15px; font-weight: 600; color: #1D1D1F; margin-bottom: 8px;">
            Priority Score vs Traffic Density
        </div>
        """)

        fig_scatter = px.box(
            df_rep,
            x="traffic_level",
            y="priority_score",
            color="severity",
            category_orders={"traffic_level": ["Low", "Medium", "High", "Severe"]},
            color_discrete_map={
                "Critical": "#D70015",
                "Medium": "#B87900",
                "Low": "#248A3D"
            }
        )
        fig_scatter.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            margin=dict(l=0, r=0, t=10, b=0),
            height=300,
            font=dict(family="-apple-system, BlinkMacSystemFont, 'SF Pro Text', sans-serif", size=12, color="#6E6E73"),
            xaxis=dict(showgrid=True, gridcolor="#E5E5EA", zeroline=False),
            yaxis=dict(showgrid=True, gridcolor="#E5E5EA", zeroline=False)
        )
        st.plotly_chart(fig_scatter, use_container_width=True)

    with an_c2:
        render_html("""
        <div style="font-size: 15px; font-weight: 600; color: #1D1D1F; margin-bottom: 8px;">
            Incident Volume by Municipal Ward / Area
        </div>
        """)

        ward_df = df_rep.groupby(["area", "severity"]).size().reset_index(name="count")
        fig_ward = px.bar(
            ward_df,
            x="area",
            y="count",
            color="severity",
            barmode="stack",
            color_discrete_map={
                "Critical": "#D70015",
                "Medium": "#B87900",
                "Low": "#248A3D"
            }
        )
        fig_ward.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            margin=dict(l=0, r=0, t=10, b=0),
            height=300,
            font=dict(family="-apple-system, BlinkMacSystemFont, 'SF Pro Text', sans-serif", size=12, color="#6E6E73"),
            xaxis=dict(showgrid=False),
            yaxis=dict(showgrid=True, gridcolor="#E5E5EA", zeroline=False)
        )
        st.plotly_chart(fig_ward, use_container_width=True)
