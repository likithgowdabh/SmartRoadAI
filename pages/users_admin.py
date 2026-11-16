"""
SmartRoad AI — User Management & Municipal Audit Trail
Administrative controls, staff directory, role assignment, and immutable audit logs.
"""

import streamlit as st
import pandas as pd
from components.ui import render_page_header, render_badge, render_html
from components.icons import get_icon
from database.db import db
from services.auth_service import register_citizen, hash_password

def render_users_admin_page(user_session: dict):
    """Renders the administration and audit logs console."""
    render_html(render_page_header(
        title="Administration",
        subtitle="Staff management, role governance, and municipal audit logging."
    ))

    tab_users, tab_audit = st.tabs(["User Directory", "System Audit Log"])

    with tab_users:
        render_html("""
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px;">
            <div style="font-size: 16px; font-weight: 600; color: #1D1D1F;">Registered Personnel</div>
        </div>
        """)

        users = db.get_users()
        df_users = pd.DataFrame(users)
        st.dataframe(
            df_users[["id", "full_name", "email", "role", "department", "phone", "created_at"]],
            use_container_width=True,
            hide_index=True
        )

        # Add Staff Form
        if user_session.get("role") == "admin":
            render_html("<div style='height: 16px;'></div>")
            with st.expander("Register New Municipal Staff Member"):
                with st.form("form_add_staff"):
                    u_c1, u_c2 = st.columns(2)
                    with u_c1:
                        new_name = st.text_input("Full Name *")
                        new_email = st.text_input("Email Address *")
                        new_pw = st.text_input("Temporary Password *", type="password")
                    with u_c2:
                        new_role = st.selectbox("Assigned Role *", ["inspector", "maintenance_manager", "admin", "citizen"])
                        new_dept = st.text_input("Department / Division", value="Public Works")
                        new_phone = st.text_input("Phone Number")

                    if st.form_submit_button("Create User Account", type="primary"):
                        if not new_email or not new_pw or not new_name:
                            st.error("Please fill in all required fields.")
                        else:
                            user_data = {
                                "email": new_email.strip().lower(),
                                "password_hash": hash_password(new_pw),
                                "full_name": new_name.strip(),
                                "role": new_role,
                                "department": new_dept,
                                "phone": new_phone
                            }
                            db.create_user(user_data)
                            st.success(f"Staff account for **{new_name}** ({new_role}) created.")
                            st.rerun()

    with tab_audit:
        render_html("""
        <div style="font-size: 16px; font-weight: 600; color: #1D1D1F; margin-bottom: 8px;">
            Immutable Municipal Audit Trail
        </div>
        <p style="font-size: 13px; color: #6E6E73; margin-bottom: 14px;">
            Every status transition, priority recalculation, and administrative override is permanently recorded.
        </p>
        """)

        logs = db.get_audit_logs(limit=100)
        if not logs:
            st.info("No audit entries recorded.")
        else:
            df_logs = pd.DataFrame(logs)
            st.dataframe(
                df_logs[["timestamp", "action", "entity_type", "entity_id", "changed_by", "old_value", "new_value"]],
                use_container_width=True,
                hide_index=True
            )
