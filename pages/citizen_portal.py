"""
SmartRoad AI — Citizen Portal & Damage Reporting Hub
Includes Citizen Registration/Login, Citizen Dashboard, Guided 3-Step Reporting,
Real-Time AI Scan, GPS Capture, and Automated Duplicate Detection.
"""

import os
import io
import streamlit as st
from PIL import Image
from components.ui import (
    render_page_header,
    render_metric_card,
    render_badge,
    render_html,
    render_timeline_step,
    render_empty_state
)
from components.icons import get_icon
from ai.priority_engine import calculate_priority_score, find_duplicate_reports
from ai.detector import PotholeDetector
from services.storage_service import validate_and_save_upload, save_annotated_image
from services.auth_service import register_citizen, verify_credentials, hash_password
from database.db import db

# Initialize detector for instant citizen upload preview
detector = PotholeDetector()

# Common municipal GPS coordinates presets
GPS_PRESETS = {
    "Outer Ring Road (Bellandur)": (12.9304, 77.6784, "Bellandur Corridor"),
    "Old Airport Road (HAL 2nd Stage)": (12.9612, 77.6483, "Indiranagar"),
    "100 Feet Road (Indiranagar)": (12.9719, 77.6412, "Indiranagar"),
    "Hosur Road (Silk Board Junction)": (12.9172, 77.6228, "BTM Layout"),
    "Sarjapur Main Road (Kaikondrahalli)": (12.9125, 77.6852, "Sarjapur"),
    "MG Road (Trinity Circle)": (12.9734, 77.6189, "Central Business District"),
    "Whitefield Main Road (ITPL)": (12.9850, 77.7310, "Whitefield"),
}

def render_citizen_portal(user_session: dict):
    """Renders the complete Citizen Portal."""
    render_html(render_page_header(
        title="Citizen Portal",
        subtitle="Empowering residents to report potholes, track repairs, and verify road quality."
    ))

    # Top Tabs: Report Damage, My Citizen Dashboard, Account Access
    tab_report, tab_dashboard, tab_auth = st.tabs([
        "Report Road Damage",
        "My Citizen Dashboard",
        "Citizen Account & Registration"
    ])

    # ========================================================
    # TAB 1: GUIDED 3-STEP ROAD DAMAGE REPORTING
    # ========================================================
    with tab_report:
        render_html("""
        <div style="text-align: center; margin-bottom: 24px;">
            <div style="display: flex; justify-content: space-between; max-width: 620px; margin: 0 auto; position: relative;">
                <div style="text-align: center; flex: 1;">
                    <div style="width: 32px; height: 32px; border-radius: 50%; background: #0071E3; color: white; display: flex; align-items: center; justify-content: center; margin: 0 auto 6px auto; font-weight: 600; font-size: 13px;">1</div>
                    <div style="font-size: 12px; font-weight: 600; color: #1D1D1F;">Capture Photo</div>
                </div>
                <div style="text-align: center; flex: 1;">
                    <div style="width: 32px; height: 32px; border-radius: 50%; background: #0071E3; color: white; display: flex; align-items: center; justify-content: center; margin: 0 auto 6px auto; font-weight: 600; font-size: 13px;">2</div>
                    <div style="font-size: 12px; font-weight: 600; color: #1D1D1F;">GPS Location</div>
                </div>
                <div style="text-align: center; flex: 1;">
                    <div style="width: 32px; height: 32px; border-radius: 50%; background: #0071E3; color: white; display: flex; align-items: center; justify-content: center; margin: 0 auto 6px auto; font-weight: 600; font-size: 13px;">3</div>
                    <div style="font-size: 12px; font-weight: 600; color: #1D1D1F;">Review & File</div>
                </div>
            </div>
        </div>
        """)

        # Step 1: Photo & Instant AI Scan
        st.markdown("#### Step 1: Pothole Photographic Evidence")
        c_up1, c_up2 = st.columns([1.5, 1.5])
        
        uploaded_photo = None
        photo_bytes = None
        
        with c_up1:
            photo_file = st.file_uploader(
                "Upload clear photo of road damage (JPG, PNG, WEBP)",
                type=["jpg", "jpeg", "png", "webp"],
                key="citizen_photo_upload"
            )
            if photo_file is not None:
                photo_bytes = photo_file.read()
                try:
                    uploaded_photo = Image.open(io.BytesIO(photo_bytes))
                    st.image(uploaded_photo, caption="Uploaded Road Evidence", use_column_width=True)
                except Exception as e:
                    st.error(f"Invalid image format: {e}")
            else:
                # Option to use sample photo for fast testing
                st.caption("Or test instantly with a municipal sample:")
                if st.button("Use Sample Pothole Capture", key="btn_use_sample"):
                    sample_p = "assets/sample_pothole_1.jpg"
                    if os.path.exists(sample_p):
                        uploaded_photo = Image.open(sample_p)
                        with open(sample_p, "rb") as f:
                            photo_bytes = f.read()
                        st.image(uploaded_photo, caption="Sample Pothole Loaded", use_column_width=True)

        # AI Pre-Scan Result
        ai_scan_result = None
        with c_up2:
            if uploaded_photo is not None:
                with st.spinner("Analyzing road surface with AI..."):
                    ai_scan_result = detector.detect(uploaded_photo)
                
                det_cnt = ai_scan_result["detection_count"]
                v_sev = ai_scan_result["visual_severity"]
                dmg_pct = ai_scan_result["damage_area_percentage"]
                
                render_html(f"""
                <div class="apple-card" style="padding: 16px; margin: 0;">
                    <div style="font-size: 13px; font-weight: 600; color: #0071E3; margin-bottom: 8px;">
                        {get_icon("scan-search", size=15, color="#0071E3")} AI Surface Pre-Scan Complete
                    </div>
                    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 8px; margin-bottom: 8px;">
                        <div>
                            <div style="font-size: 11px; color: #86868B;">Detections</div>
                            <div style="font-size: 16px; font-weight: 600;">{det_cnt} Potholes</div>
                        </div>
                        <div>
                            <div style="font-size: 11px; color: #86868B;">Visual Severity</div>
                            <div>{render_badge(v_sev, variant=v_sev.lower())}</div>
                        </div>
                    </div>
                    <div style="font-size: 11.5px; color: #6E6E73;">
                        Damage covers approximately <strong>{dmg_pct}%</strong> of local pavement surface.
                    </div>
                </div>
                """)
                st.image(ai_scan_result["annotated_image"], caption="AI Detection Overlay", use_column_width=True)
            else:
                render_html("""
                <div style="background: #FAFAFC; border: 1px dashed #D2D2D7; border-radius: 10px; height: 180px; display: flex; flex-direction: column; align-items: center; justify-content: center; text-align: center; padding: 20px;">
                    <div style="color: #86868B; font-size: 13px;">Upload or select a photo on the left to activate instant AI pothole detection.</div>
                </div>
                """)

        render_html("<div style='height: 20px;'></div>")

        # Step 2: Location & GPS Capture
        st.markdown("#### Step 2: Location & GPS Capture")
        
        # Preset Quick Selection
        preset_choice = st.selectbox(
            "Quick-Select Known Arterial Road (or enter custom coordinates below):",
            ["Custom GPS Coordinates"] + list(GPS_PRESETS.keys())
        )
        
        default_lat = 12.9345
        default_lon = 77.6210
        default_road = ""
        default_area = ""

        if preset_choice in GPS_PRESETS:
            default_lat, default_lon, default_area = GPS_PRESETS[preset_choice]
            default_road = preset_choice

        l_c1, l_c2 = st.columns(2)
        with l_c1:
            inp_road = st.text_input("Road / Street Name *", value=default_road, placeholder="e.g. 100 Feet Road, Koramangala")
            inp_area = st.text_input("Neighborhood / Ward *", value=default_area, placeholder="e.g. Koramangala Ward 151")
        with l_c2:
            inp_lat = st.number_input("GPS Latitude *", value=float(default_lat), format="%.6f")
            inp_lon = st.number_input("GPS Longitude *", value=float(default_lon), format="%.6f")

        # Step 3: Observations & Duplicate Verification
        st.markdown("#### Step 3: Road Conditions & Submission")
        o_c1, o_c2 = st.columns(2)
        with o_c1:
            initial_sev = ai_scan_result["visual_severity"] if ai_scan_result else "Medium"
            inp_sev = st.selectbox("Damage Severity Rating", ["Critical", "Medium", "Low"], index=["Critical", "Medium", "Low"].index(initial_sev))
            inp_traffic = st.selectbox("Arterial Traffic Level", ["Severe", "High", "Medium", "Low"], index=1)
        with o_c2:
            inp_risk = st.selectbox("Safety Hazard to Motorcyclists / Pedestrians", ["High", "Medium", "Low"], index=0 if inp_sev == "Critical" else 1)
            inp_desc = st.text_area("Observations / Description", placeholder="e.g. Sharp pavement edge, hazard worsens during rain.")

        # Check for nearby duplicates actively
        all_reps = db.get_reports()
        nearby_dups = find_duplicate_reports(inp_lat, inp_lon, all_reps, threshold_meters=50.0)
        
        if nearby_dups:
            closest_dup = nearby_dups[0]
            render_html(f"""
            <div style="background: #FEF7E6; border: 1px solid rgba(184, 121, 0, 0.25); border-radius: 8px; padding: 14px 18px; margin: 14px 0;">
                <div style="display: flex; align-items: center; gap: 8px; font-weight: 600; color: #B87900; font-size: 13.5px; margin-bottom: 4px;">
                    {get_icon("alert-circle", size=16, color="#B87900")} Nearby Active Report Already Found ({closest_dup['distance_meters']}m away)
                </div>
                <div style="font-size: 12.5px; color: #6E6E73; line-height: 1.4;">
                    Report <strong>{closest_dup['id']}</strong> on <strong>{closest_dup['road_name']}</strong> is already open. Submitting will register your confirmation, elevating its municipal priority score!
                </div>
            </div>
            """)

        # Submit button
        if st.button("Submit Official Incident Report", type="primary", use_container_width=True):
            if not inp_road or not inp_area:
                st.error("Please provide both Road Name and Neighborhood/Ward.")
            else:
                saved_raw_rel = None
                saved_ann_rel = None

                # Persist photos if available
                if uploaded_photo is not None:
                    _, raw_path = save_annotated_image(uploaded_photo, "citizen_raw")
                    saved_raw_rel = raw_path
                if ai_scan_result is not None:
                    _, ann_path = save_annotated_image(ai_scan_result["annotated_image"], "citizen_annotated")
                    saved_ann_rel = ann_path

                if nearby_dups:
                    target_d = nearby_dups[0]
                    new_repeat = target_d.get("repeat_count", 1) + 1
                    re_calc = calculate_priority_score(
                        severity=target_d.get("severity", inp_sev),
                        traffic=target_d.get("traffic_level", inp_traffic),
                        repeat_count=new_repeat,
                        safety_risk=target_d.get("safety_risk", inp_risk)
                    )
                    db.update_report(
                        target_d["id"],
                        {"repeat_count": new_repeat, "priority_score": re_calc["score"]},
                        changed_by=f"Citizen Recurrence ({user_session.get('full_name', 'Citizen')})"
                    )
                    st.success(f"Citizen Recurrence Logged! Report **{target_d['id']}** repeat frequency updated to **{new_repeat}** with elevated priority score **{re_calc['score']}**.")
                else:
                    new_prio = calculate_priority_score(
                        severity=inp_sev,
                        traffic=inp_traffic,
                        repeat_count=1,
                        safety_risk=inp_risk
                    )
                    new_payload = {
                        "title": f"{inp_sev} Road Hazard on {inp_road}",
                        "description": inp_desc or f"Citizen submitted report with {inp_sev} severity.",
                        "road_name": inp_road,
                        "area": inp_area,
                        "city": "Bengaluru",
                        "latitude": inp_lat,
                        "longitude": inp_lon,
                        "severity": inp_sev,
                        "priority_score": new_prio["score"],
                        "traffic_level": inp_traffic,
                        "repeat_count": 1,
                        "safety_risk": inp_risk,
                        "status": "Reported",
                        "image_url": saved_raw_rel,
                        "annotated_image_url": saved_ann_rel,
                        "detection_count": ai_scan_result["detection_count"] if ai_scan_result else 1,
                        "citizen_id": user_session.get("id", "usr-cit-1"),
                        "assigned_to": None,
                        "inspector_notes": None
                    }
                    new_rep_id = db.create_report(new_payload)
                    st.success(f"Report **{new_rep_id}** filed successfully with Priority Score **{new_prio['score']}**!")
                    st.balloons()

    # ========================================================
    # TAB 2: CITIZEN DASHBOARD (MY REPORTS & TIMELINE)
    # ========================================================
    with tab_dashboard:
        all_reports = db.get_reports()
        cit_id = user_session.get("id", "usr-cit-1")
        
        # Reports by this citizen (or seeded citizen demo reports)
        my_reports = [r for r in all_reports if r.get("citizen_id") == cit_id or cit_id == "usr-cit-1"]

        # Dashboard Metrics
        total_sub = len(my_reports)
        active_sub = sum(1 for r in my_reports if r["status"] in ["Reported", "Under Inspection", "Scheduled", "In Progress"])
        resolved_sub = sum(1 for r in my_reports if r["status"] in ["Repaired", "Verified"])

        cd1, cd2, cd3 = st.columns(3)
        with cd1:
            render_html(render_metric_card("My Submissions", total_sub, "Logged hazards", "clipboard-list", "default"))
        with cd2:
            render_html(render_metric_card("Active Repair Pipeline", active_sub, "Municipal crews dispatched", "wrench", "accent"))
        with cd3:
            render_html(render_metric_card("Pavement Restored", resolved_sub, "Verified repairs", "check-circle-2", "success"))

        render_html("<div style='height: 20px;'></div>")
        st.markdown("#### My Road Repair Tracking")

        if not my_reports:
            render_html(render_empty_state("No Submitted Reports Yet", "Use the 'Report Road Damage' tab to submit photographic and location evidence.", "cloud-upload"))
        else:
            for rep in my_reports:
                r_id = rep["id"]
                road = rep["road_name"]
                area = rep["area"]
                status = rep["status"]
                sev = rep["severity"]
                prio = rep["priority_score"]
                created = str(rep["created_at"])[:10]

                status_variant = "success" if status in ["Repaired", "Verified"] else ("accent" if status == "In Progress" else "neutral")

                with st.expander(f"{r_id} — {road} ({area}) | Status: {status}"):
                    c_det1, c_det2 = st.columns([1.2, 1.8])
                    with c_det1:
                        img_p = rep.get("annotated_image_url") or rep.get("image_url")
                        if img_p and os.path.exists(img_p):
                            st.image(img_p, caption=f"Report Photo: {r_id}", use_column_width=True)
                        else:
                            st.caption("No image attached")
                        st.markdown(f"**Logged Date:** {created}")
                        st.markdown(f"**GPS Coordinates:** `{rep['latitude']}, {rep['longitude']}`")

                    with c_det2:
                        render_html(f"""
                        <div style="display: flex; gap: 8px; margin-bottom: 12px;">
                            {render_badge(sev, variant=sev.lower())}
                            {render_badge(status, variant=status_variant)}
                            <span style="font-size: 12px; color: #86868B; align-self: center;">Priority: <strong>{prio}</strong></span>
                        </div>
                        """)
                        st.markdown(f"**Description:** {rep.get('description') or 'Citizen road hazard submission.'}")
                        
                        # Lifecycle Progress Timeline
                        st.markdown("**Repair Lifecycle Progress:**")
                        lifecycle = ["Reported", "Under Inspection", "Scheduled", "In Progress", "Repaired", "Verified"]
                        cur_idx = lifecycle.index(status) if status in lifecycle else 0

                        steps_html = []
                        for idx, step_name in enumerate(lifecycle):
                            step_stat = "completed" if idx < cur_idx else ("current" if idx == cur_idx else "pending")
                            time_str = "Completed" if idx < cur_idx else ("Active" if idx == cur_idx else "Pending")
                            steps_html.append(render_timeline_step(step_name, time_str, f"Phase {idx+1} of municipal repair protocol", status=step_stat))
                        
                        render_html("".join(steps_html))

                        if rep.get("inspector_notes"):
                            st.markdown(f"**Municipal Inspector Note:** *\"{rep['inspector_notes']}\"*")

    # ========================================================
    # TAB 3: CITIZEN REGISTRATION & LOGIN
    # ========================================================
    with tab_auth:
        st.markdown("#### Citizen Identity & Account Management")
        render_html(f"""
        <div class="apple-card" style="padding: 18px; margin-bottom: 20px;">
            <div style="display: flex; align-items: center; gap: 12px;">
                <div style="width: 36px; height: 36px; border-radius: 50%; background: #0071E3; color: white; display: flex; align-items: center; justify-content: center; font-weight: 600;">
                    {user_session['full_name'][0]}
                </div>
                <div>
                    <div style="font-size: 15px; font-weight: 600; color: #1D1D1F;">{user_session['full_name']}</div>
                    <div style="font-size: 12px; color: #6E6E73;">Current Role: <strong>{user_session['role'].replace('_', ' ').capitalize()}</strong> ({user_session['email']})</div>
                </div>
            </div>
        </div>
        """)

        auth_subtab_login, auth_subtab_reg = st.tabs(["Sign In to Existing Account", "Register New Citizen Profile"])
        
        with auth_subtab_login:
            with st.form("form_citizen_signin"):
                log_email = st.text_input("Citizen Email Address")
                log_pw = st.text_input("Password", type="password")
                if st.form_submit_button("Sign In as Citizen"):
                    user_record = verify_credentials(log_email, log_pw)
                    if user_record:
                        st.session_state["user"] = user_record
                        st.success(f"Welcome back, {user_record['full_name']}!")
                        st.rerun()
                    else:
                        st.error("Invalid email or password.")

        with auth_subtab_reg:
            with st.form("form_citizen_register"):
                reg_name = st.text_input("Full Name *")
                reg_email = st.text_input("Email Address *")
                reg_pw = st.text_input("Password *", type="password")
                reg_phone = st.text_input("Mobile Number (for SMS repair updates)")
                
                if st.form_submit_button("Create Citizen Account", type="primary"):
                    if not reg_name or not reg_email or not reg_pw:
                        st.error("Please fill in Full Name, Email, and Password.")
                    else:
                        ok, msg = register_citizen(reg_email, reg_pw, reg_name, phone=reg_phone)
                        if ok:
                            st.success("Citizen account created! You can now sign in.")
                        else:
                            st.error(msg)
