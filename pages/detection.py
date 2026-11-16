"""
SmartRoad AI — AI Pothole Detection Studio (Apple Inspired)
Real computer vision inference, image comparison, severity rating, and incident filing.
"""

import os
import io
import streamlit as st
from PIL import Image
from components.ui import render_page_header, render_metric_card, render_badge, render_html
from components.icons import get_icon
from ai.detector import PotholeDetector
from ai.priority_engine import calculate_priority_score
from services.storage_service import validate_and_save_upload, save_annotated_image
from database.db import db

detector = PotholeDetector()

def render_detection_page(user_session: dict):
    """Renders the AI pothole detection studio."""
    render_html(render_page_header(
        title="Pothole Detection",
        subtitle="Computer vision surface analysis, damage bounding, and priority calculation."
    ))

    status_info = detector.get_system_status()

    # Active Deep Learning AI Model Status Banner
    if status_info["status"] == "ready":
        render_html(f"""
        <div class="apple-card" style="padding: 16px 20px; margin-bottom: 24px; border-left: 4px solid #248A3D; background: #FFFFFF;">
            <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 12px;">
                <div style="display: flex; align-items: center; gap: 14px;">
                    <div style="width: 42px; height: 42px; border-radius: 11px; background: rgba(36, 138, 61, 0.12); display: flex; align-items: center; justify-content: center; flex-shrink: 0;">
                        {get_icon("scan-search", size=22, color="#248A3D")}
                    </div>
                    <div>
                        <div style="display: flex; align-items: center; gap: 8px;">
                            <strong style="font-size: 15.5px; color: #1D1D1F; font-weight: 700;">YOLO Pothole Neural Network Active</strong>
                            <span class="apple-badge apple-badge-success" style="font-size: 11px;">Production Ready</span>
                        </div>
                        <div style="font-size: 12.5px; color: #6E6E73; margin-top: 3px;">
                            Model: <code>models/pothole_best.pt</code> ({status_info['weights_size_mb']} MB weights) • Architecture: YOLOv8/v11 Tensor Engine • Benchmark: RDD2022
                        </div>
                    </div>
                </div>
                <div style="display: flex; gap: 16px; font-size: 12px; color: #6E6E73;">
                    <div><span style="color: #1D1D1F; font-weight: 600;">Hardware:</span> PyTorch CPU/AVX2</div>
                    <div><span style="color: #1D1D1F; font-weight: 600;">Latency:</span> ~35ms / Frame</div>
                    <div><span style="color: #248A3D; font-weight: 600;">Status:</span> Online</div>
                </div>
            </div>
        </div>
        """)
    else:
        render_html(f"""
        <div class="apple-card" style="padding: 16px 20px; margin-bottom: 24px; border-left: 4px solid #0071E3; background: #FAFAFC;">
            <div style="display: flex; align-items: center; gap: 10px;">
                {get_icon("scan-search", size=18, color="#0071E3")}
                <strong style="font-size: 14px; color: #1D1D1F;">AI Model Initializing</strong>
            </div>
        </div>
        """)

    # Image Input Section: Upload or Choose Sample
    render_html("""
    <div style="font-size: 15px; font-weight: 600; color: #1D1D1F; margin-bottom: 8px;">
        Input Road Imagery
    </div>
    """)

    tab_upload, tab_sample = st.tabs(["Upload Photo", "Pre-loaded Municipal Samples"])

    image_to_process = None
    original_filename = "road_inspection.jpg"

    with tab_upload:
        uploaded_file = st.file_uploader(
            "Select road damage photo (JPG, PNG, WEBP)",
            type=["jpg", "jpeg", "png", "webp"],
            label_visibility="collapsed"
        )
        if uploaded_file is not None:
            image_bytes = uploaded_file.read()
            valid, path_or_msg, rel_path = validate_and_save_upload(image_bytes, uploaded_file.name)
            if not valid:
                st.error(path_or_msg)
            else:
                image_to_process = Image.open(io.BytesIO(image_bytes))
                original_filename = uploaded_file.name

    with tab_sample:
        st.markdown("<p style='font-size: 13px; color: #6E6E73;'>Select an authentic road pavement inspection sample:</p>", unsafe_allow_html=True)
        sample_cols = st.columns(4)
        sample_paths = [
            ("assets/sample_pothole_1.jpg", "Outer Ring Road (Cluster)"),
            ("assets/sample_pothole_2.jpg", "Airport Arterial Road"),
            ("assets/sample_pothole_3.jpg", "100 Feet Commercial Road"),
            ("assets/sample_pothole_4.jpg", "Hosur Expressway Crater"),
        ]
        for idx, (sp, label) in enumerate(sample_paths):
            with sample_cols[idx]:
                if os.path.exists(sp):
                    st.image(sp, caption=label, use_column_width=True)
                    if st.button(f"Analyze Sample {idx+1}", key=f"btn_sample_{idx}", use_container_width=True):
                        image_to_process = Image.open(sp)
                        original_filename = f"sample_{idx+1}.jpg"

    # Execution & Results Display
    if image_to_process is not None:
        render_html("<div style='height: 24px;'></div>")
        render_html("""
        <div style="border-top: 1px solid #E5E5EA; padding-top: 20px; margin-bottom: 16px;">
            <h2 style="font-size: 20px; font-weight: 600; color: #1D1D1F; margin: 0;">AI Inference Results</h2>
        </div>
        """)

        with st.spinner("Processing computer vision tensors..."):
            results = detector.detect(image_to_process)

        # Telemetry Banner
        count = results["detection_count"]
        severity = results["visual_severity"]
        damage_pct = results["damage_area_percentage"]
        duration = results["execution_time_ms"]
        engine = results["inference_engine"]

        # Calculate preliminary priority assuming high traffic
        priority_data = calculate_priority_score(
            severity=severity,
            traffic="High",
            repeat_count=1,
            safety_risk="High" if severity == "Critical" else "Medium"
        )
        prio_score = priority_data["score"]

        # 4 Metric Cards
        rc1, rc2, rc3, rc4 = st.columns(4)
        with rc1:
            render_html(render_metric_card(
                title="Pothole Detections",
                value=count,
                subtitle=f"Inference: {duration} ms",
                icon="scan-search",
                status="default"
            ))
        with rc2:
            render_html(render_metric_card(
                title="Visual Severity",
                value=severity,
                subtitle=f"{damage_pct}% road area damaged",
                icon="alert-triangle",
                status=severity.lower()
            ))
        with rc3:
            render_html(render_metric_card(
                title="Priority Index",
                value=prio_score,
                subtitle=f"Tier: {priority_data['category']}",
                icon="sliders-horizontal",
                status=priority_data["category"].lower()
            ))
        with rc4:
            render_html(render_metric_card(
                title="Neural Engine",
                value="YOLO Vision",
                subtitle=f"Deep Learning • {status_info.get('weights_size_mb', 21.5)} MB",
                icon="sparkles",
                status="success"
            ))

        render_html("<div style='height: 18px;'></div>")

        # Two-Column Image Comparison Layout
        cmp_left, cmp_right = st.columns(2)
        with cmp_left:
            render_html("""
            <div style="font-size: 14px; font-weight: 600; color: #1D1D1F; margin-bottom: 6px;">
                Original Pavement Imagery
            </div>
            """)
            st.image(image_to_process, use_column_width=True)

        with cmp_right:
            render_html("""
            <div style="font-size: 14px; font-weight: 600; color: #1D1D1F; margin-bottom: 6px;">
                AI Annotated Surface (Bounding Boxes)
            </div>
            """)
            st.image(results["annotated_image"], use_column_width=True)

        # File Official Incident Section
        render_html("<div style='height: 24px;'></div>")
        render_html("""
        <div style="font-size: 16px; font-weight: 600; color: #1D1D1F; margin-bottom: 8px;">
            Commit to Municipal Incident Record
        </div>
        """)

        with st.form(key="form_save_ai_report"):
            f_col1, f_col2 = st.columns(2)
            with f_col1:
                rep_title = st.text_input("Incident Title", value=f"{severity} Road Surface Hazard ({count} detections)")
                rep_road = st.text_input("Road Name", value="Richmond Road (Near Junction)")
                rep_area = st.text_input("Area / Ward", value="Central Ward 82")
            with f_col2:
                rep_lat = st.number_input("Latitude", value=12.9605, format="%.6f")
                rep_lon = st.number_input("Longitude", value=77.6045, format="%.6f")
                rep_traffic = st.selectbox("Arterial Traffic Volume", ["Severe", "High", "Medium", "Low"], index=1)

            rep_notes = st.text_area("Field Inspector Observation", value=f"Automated AI detection identified {count} surface breaks covering {damage_pct}% pavement area.")

            submit_report = st.form_submit_button("Create Official Municipal Report", type="primary")
            if submit_report:
                _, raw_rel = save_annotated_image(image_to_process, "raw_capture")
                _, ann_rel = save_annotated_image(results["annotated_image"], "ai_detection")

                final_priority = calculate_priority_score(
                    severity=severity,
                    traffic=rep_traffic,
                    repeat_count=1,
                    safety_risk="High" if severity == "Critical" else "Medium"
                )

                new_report_data = {
                    "title": rep_title,
                    "description": rep_notes,
                    "road_name": rep_road,
                    "area": rep_area,
                    "city": "Bengaluru",
                    "latitude": rep_lat,
                    "longitude": rep_lon,
                    "severity": severity,
                    "priority_score": final_priority["score"],
                    "traffic_level": rep_traffic,
                    "repeat_count": 1,
                    "safety_risk": "High" if severity == "Critical" else "Medium",
                    "status": "Under Inspection",
                    "image_url": raw_rel,
                    "annotated_image_url": ann_rel,
                    "detection_count": count,
                    "citizen_id": user_session.get("id"),
                    "assigned_to": user_session.get("full_name"),
                    "inspector_notes": rep_notes
                }
                new_id = db.create_report(new_report_data)
                st.success(f"Report **{new_id}** successfully created with Priority Score **{final_priority['score']}**.")
                st.balloons()
