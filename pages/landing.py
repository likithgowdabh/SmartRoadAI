"""
SmartRoad AI — Premium Apple-Inspired Landing Page
Hero, Product Overview, Live Municipal Metrics, and Call to Actions.
"""

import os
import base64
import streamlit as st
from components.icons import get_icon
from components.ui import render_html
from database.db import db

def get_base64_image(rel_path: str) -> str:
    """Encodes local image to base64 data URI for zero-latency DOM embedding."""
    if os.path.exists(rel_path):
        with open(rel_path, "rb") as f:
            ext = os.path.splitext(rel_path)[1].replace(".", "")
            if ext == "jpg":
                ext = "jpeg"
            return f"data:image/{ext};base64," + base64.b64encode(f.read()).decode("utf-8")
    return ""

def render_landing_page(navigate_to_fn):
    """Renders the Apple-style product introduction page."""
    metrics = db.get_summary_metrics()

    logo_b64 = get_base64_image("assets/logo.png")
    img_blue = get_base64_image("assets/feat_vision_blue.png")
    img_skin = get_base64_image("assets/feat_priority_skin.png")
    img_green = get_base64_image("assets/feat_dispatch_green.png")

    # Hero Section - Glossy 3D Icon, Restrained Typography
    logo_tag = f'<img src="{logo_b64}" style="width: 86px; height: 86px; border-radius: 20px; box-shadow: 0 10px 28px rgba(0, 113, 227, 0.25); margin-bottom: 18px; transition: transform 0.3s cubic-bezier(0.16, 1, 0.3, 1);" class="apple-hero-logo" />' if logo_b64 else ""

    render_html(f"""
    <div style="text-align: center; padding: 2.2rem 1rem 1.6rem 1rem; max-width: 900px; margin: 0 auto;">
        <div>{logo_tag}</div>
        <div style="display: inline-flex; align-items: center; gap: 6px; padding: 5px 16px; background: rgba(0, 113, 227, 0.08); border-radius: 999px; font-size: 13px; font-weight: 500; color: #0071E3; margin-bottom: 18px;">
            {get_icon("sparkles", size=14, color="#0071E3")}
            <span>Municipal Computer Vision Platform</span>
        </div>
        <h1 style="font-size: clamp(38px, 6vw, 64px); font-weight: 700; letter-spacing: -0.035em; color: #1D1D1F; line-height: 1.08; margin-bottom: 16px;">
            Better Roads.<br/>
            <span style="color: #0071E3;">Smarter Cities.</span>
        </h1>
        <p style="font-size: clamp(16px, 2.2vw, 20px); font-weight: 400; color: #6E6E73; line-height: 1.45; max-width: 680px; margin: 0 auto 10px auto; letter-spacing: -0.015em;">
            SmartRoad AI is an intelligent road monitoring and maintenance management platform that uses computer vision to detect potholes, calculate repair priority, and streamline city operations.
        </p>
    </div>
    """)

    # Interactive Action Buttons
    c_pad1, col_act1, col_act2, c_pad2 = st.columns([1.5, 2, 2, 1.5])
    with col_act1:
        if st.button("Open Dashboard", type="primary", use_container_width=True):
            navigate_to_fn("overview")
    with col_act2:
        if st.button("Report Road Damage", use_container_width=True):
            navigate_to_fn("citizen_portal")

    render_html("<div style='height: 36px;'></div>")

    # Live Municipal Telemetry Stats
    render_html(f"""
    <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 16px; margin-bottom: 44px;">
        <div class="apple-card" style="text-align: center; padding: 22px 16px; margin: 0;">
            <div style="font-size: 12.5px; font-weight: 500; color: #6E6E73; margin-bottom: 4px;">Total Monitored Incidents</div>
            <div style="font-size: 36px; font-weight: 600; color: #1D1D1F; letter-spacing: -0.02em;">{metrics['total_reports']}</div>
            <div style="font-size: 11.5px; color: #248A3D; margin-top: 4px;">Active telemetry</div>
        </div>
        <div class="apple-card" style="text-align: center; padding: 22px 16px; margin: 0;">
            <div style="font-size: 12.5px; font-weight: 500; color: #6E6E73; margin-bottom: 4px;">Critical Structural Hazards</div>
            <div style="font-size: 36px; font-weight: 600; color: #D70015; letter-spacing: -0.02em;">{metrics['critical_damage']}</div>
            <div style="font-size: 11.5px; color: #6E6E73; margin-top: 4px;">Prioritized dispatch</div>
        </div>
        <div class="apple-card" style="text-align: center; padding: 22px 16px; margin: 0;">
            <div style="font-size: 12.5px; font-weight: 500; color: #6E6E73; margin-bottom: 4px;">Under Rapid Inspection</div>
            <div style="font-size: 36px; font-weight: 600; color: #B87900; letter-spacing: -0.02em;">{metrics['under_inspection']}</div>
            <div style="font-size: 11.5px; color: #6E6E73; margin-top: 4px;">Field crew deployed</div>
        </div>
        <div class="apple-card" style="text-align: center; padding: 22px 16px; margin: 0;">
            <div style="font-size: 12.5px; font-weight: 500; color: #6E6E73; margin-bottom: 4px;">Completed & Verified Repairs</div>
            <div style="font-size: 36px; font-weight: 600; color: #248A3D; letter-spacing: -0.02em;">{metrics['completed_repairs']}</div>
            <div style="font-size: 11.5px; color: #6E6E73; margin-top: 4px;">Pavement restored</div>
        </div>
    </div>
    """)

    # Core Value Pillars with Topic Badges in Blue, Skin/Amber, and Green color spaces
    render_html(f"""
    <div style="margin-top: 10px; margin-bottom: 50px;">
        <div style="text-align: center; margin-bottom: 28px;">
            <h2 style="font-size: 26px; font-weight: 600; letter-spacing: -0.02em; color: #1D1D1F; margin-bottom: 6px;">Built for Serious City Governance</h2>
            <p style="font-size: 14.5px; color: #6E6E73; max-width: 540px; margin: 0 auto;">Precision engineering meets intuitive design to transform municipal asphalt operations.</p>
        </div>
        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 20px;">
            <!-- Topic 1: Blue Color Space (YOLO11 Road Vision) -->
            <div class="apple-card" style="padding: 22px 20px;">
                <img src="{img_blue}" style="width: 100%; height: 130px; object-fit: contain; border-radius: 12px; margin-bottom: 14px;" alt="YOLO11 Road Vision" />
                <h3 style="font-size: 17px; font-weight: 600; color: #1D1D1F; margin-bottom: 6px;">YOLO11 Road Vision</h3>
                <p style="font-size: 13px; color: #6E6E73; line-height: 1.5; margin: 0;">
                    Trained specifically on road damage benchmarks (RDD2022) to locate surface depressions, evaluate pixel damage ratios, and determine visual severity in milliseconds.
                </p>
            </div>
            <!-- Topic 2: Skin/Amber Color Space (Multi-Factor Priority Engine) -->
            <div class="apple-card" style="padding: 22px 20px;">
                <img src="{img_skin}" style="width: 100%; height: 130px; object-fit: contain; border-radius: 12px; margin-bottom: 14px;" alt="Multi-Factor Priority Engine" />
                <h3 style="font-size: 17px; font-weight: 600; color: #1D1D1F; margin-bottom: 6px;">Multi-Factor Priority Engine</h3>
                <p style="font-size: 13px; color: #6E6E73; line-height: 1.5; margin: 0;">
                    Synthesizes damage severity, arterial traffic volume, citizen recurrence, and structural safety risk into a transparent 0–100 priority score with audit history.
                </p>
            </div>
            <!-- Topic 3: Green Color Space (End-to-End Field Dispatch) -->
            <div class="apple-card" style="padding: 22px 20px;">
                <img src="{img_green}" style="width: 100%; height: 130px; object-fit: contain; border-radius: 12px; margin-bottom: 14px;" alt="End-to-End Field Dispatch" />
                <h3 style="font-size: 17px; font-weight: 600; color: #1D1D1F; margin-bottom: 6px;">End-to-End Field Dispatch</h3>
                <p style="font-size: 13px; color: #6E6E73; line-height: 1.5; margin: 0;">
                    Dispatches asphalt maintenance crews, tracks before-and-after photographic evidence, logs material costs, and verifies repair compliance with municipal standards.
                </p>
            </div>
        </div>
    </div>
    """)
