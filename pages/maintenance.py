"""
SmartRoad AI — Maintenance & Operations Management
Dispatches asphalt maintenance squads, tracks repair progress, and logs operational costs.
"""

import streamlit as st
import datetime
from components.ui import render_page_header, render_metric_card, render_badge, render_html
from components.icons import get_icon
from database.db import db

def render_maintenance_page(user_session: dict):
    """Renders the municipal maintenance operations console."""
    render_html(render_page_header(
        title="Maintenance",
        subtitle="Manage work orders, team assignments, repair timelines, and operational expenses."
    ))

    tasks = db.get_maintenance_tasks()

    # Calculate operational metrics
    scheduled_cnt = sum(1 for t in tasks if t["status"] == "Scheduled")
    inprogress_cnt = sum(1 for t in tasks if t["status"] == "In Progress")
    completed_cnt = sum(1 for t in tasks if t["status"] in ["Repaired", "Verified"])
    total_cost = sum(t.get("cost_actual", 0.0) or 0.0 for t in tasks)

    mc1, mc2, mc3, mc4 = st.columns(4)
    with mc1:
        render_html(render_metric_card(
            title="Scheduled Work",
            value=scheduled_cnt,
            subtitle="Awaiting crew deployment",
            icon="calendar-days",
            status="default"
        ))
    with mc2:
        render_html(render_metric_card(
            title="Active Operations",
            value=inprogress_cnt,
            subtitle="Teams currently on-site",
            icon="wrench",
            status="accent"
        ))
    with mc3:
        render_html(render_metric_card(
            title="Repairs Completed",
            value=completed_cnt,
            subtitle="Pavement restored & sealed",
            icon="check-circle-2",
            status="success"
        ))
    with mc4:
        render_html(render_metric_card(
            title="Total Spend",
            value=f"${total_cost:,.0f}",
            subtitle="Direct asphalt & crew costs",
            icon="sliders-horizontal",
            status="default"
        ))

    render_html("<div style='height: 20px;'></div>")

    # Dispatch New Maintenance Task (for Managers and Admins)
    can_dispatch = user_session.get("role") in ["maintenance_manager", "admin"]
    if can_dispatch:
        with st.expander("Dispatch New Maintenance Work Order", expanded=False):
            reports = db.get_reports()
            eligible_reports = [r for r in reports if r["status"] not in ["Repaired", "Verified"]]
            if not eligible_reports:
                st.info("All current road reports are completed.")
            else:
                rep_options = {f"{r['id']} — {r['road_name']} (Priority: {r['priority_score']})": r["id"] for r in eligible_reports}
                with st.form("form_dispatch_task"):
                    f_c1, f_c2 = st.columns(2)
                    with f_c1:
                        sel_rep_str = st.selectbox("Select Road Damage Incident", list(rep_options.keys()))
                        target_rep_id = rep_options[sel_rep_str]
                        assigned_team = st.selectbox("Assigned Maintenance Squad", [
                            "Rapid Response Asphalt Team Alpha",
                            "South Zone Pavement Division #3",
                            "Emergency Highway Paving Squad",
                            "Central Business District Road Unit",
                            "Heavy Machinery Road Resurfacing Crew"
                        ])
                        sched_date = st.date_input("Scheduled Date", value=datetime.date.today())
                    with f_c2:
                        due_date = st.date_input("Target Completion Date", value=datetime.date.today() + datetime.timedelta(days=3))
                        budget_est = st.number_input("Budget Allocation ($)", min_value=100.0, max_value=50000.0, value=1200.0, step=100.0)
                        initial_status = st.selectbox("Initial Order Status", ["Scheduled", "In Progress"])

                    notes = st.text_area("Operational Work Instructions", placeholder="e.g. 50mm cold mix asphalt compaction, seal coat edges.")

                    if st.form_submit_button("Issue Work Order", type="primary"):
                        task_payload = {
                            "report_id": target_rep_id,
                            "assigned_team": assigned_team,
                            "scheduled_date": str(sched_date),
                            "due_date": str(due_date),
                            "status": initial_status,
                            "repair_notes": notes,
                            "budget_estimate": budget_est,
                            "cost_actual": 0.0
                        }
                        new_t_id = db.create_maintenance_task(task_payload, changed_by=user_session.get("full_name", "Manager"))
                        st.success(f"Work Order **{new_t_id}** dispatched to **{assigned_team}**.")
                        st.rerun()

    render_html("<div style='height: 12px;'></div>")

    # Active Task Cards
    render_html("""
    <div style="font-size: 16px; font-weight: 600; color: #1D1D1F; margin-bottom: 12px;">
        Active Operations Roster
    </div>
    """)

    if not tasks:
        st.info("No maintenance work orders currently scheduled.")
        return

    for t in tasks:
        t_id = t["id"]
        status = t["status"]
        team = t["assigned_team"]
        road = t.get("road_name") or "Municipal Arterial"
        area = t.get("area") or "Metro"
        rep_id = t.get("report_id")
        due = t.get("due_date") or "TBD"
        budget = t.get("budget_estimate", 0.0)
        actual = t.get("cost_actual", 0.0)

        with st.expander(f"{t_id} | {team} — {road} | Due: {due} | {status}"):
            c1, c2 = st.columns([1.5, 1.5])
            with c1:
                st.markdown(f"**Linked Incident:** `{rep_id}`")
                st.markdown(f"**Location:** {road}, {area}")
                st.markdown(f"**Assigned Crew:** {team}")
                st.markdown(f"**Scheduled Date:** {t.get('scheduled_date') or 'N/A'}")
                st.markdown(f"**Due Date:** {due}")
                st.markdown(f"**Budget Allocated:** ${budget:,.2f}")
                st.markdown(f"**Actual Expense:** ${actual:,.2f}")
                if t.get("repair_notes"):
                    st.markdown(f"**Work Notes:** {t['repair_notes']}")

            with c2:
                if can_dispatch:
                    st.markdown("**Update Work Order Status & Costs**")
                    with st.form(key=f"form_task_upd_{t_id}"):
                        new_stat = st.selectbox(
                            "Status",
                            ["Scheduled", "In Progress", "Repaired", "Verified"],
                            index=["Scheduled", "In Progress", "Repaired", "Verified"].index(status) if status in ["Scheduled", "In Progress", "Repaired", "Verified"] else 0
                        )
                        new_cost = st.number_input("Actual Incurred Cost ($)", min_value=0.0, max_value=100000.0, value=float(actual), step=50.0)
                        add_notes = st.text_area("Operational Log / Progress Update", value=t.get("repair_notes") or "", height=70)

                        if st.form_submit_button("Record Operational Update"):
                            updates = {
                                "status": new_stat,
                                "cost_actual": new_cost,
                                "repair_notes": add_notes
                            }
                            if new_stat in ["Repaired", "Verified"]:
                                updates["completed_date"] = str(datetime.date.today())
                            db.update_maintenance_task(t_id, updates, changed_by=user_session.get("full_name", "Manager"))
                            st.success(f"Work order {t_id} updated.")
                            st.rerun()
                else:
                    render_html("""
                    <div style="font-size: 13px; color: #86868B; padding-top: 20px;">
                        Status updates are restricted to Maintenance Managers and Administrators.
                    </div>
                    """)
