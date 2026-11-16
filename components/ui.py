"""
SmartRoad AI — Apple-Inspired UI Component Library
Reusable widgets with consistent spacing, typography, and visual hierarchy.
Guaranteed clean HTML rendering (zero Markdown code-block interpretation).
"""

import os
import base64
from typing import Optional, List, Dict, Any
import streamlit as st
from components.icons import get_icon

def get_base64_image(rel_path: str) -> str:
    """Encodes local image to base64 data URI for zero-latency DOM embedding."""
    if os.path.exists(rel_path):
        with open(rel_path, "rb") as f:
            ext = os.path.splitext(rel_path)[1].replace(".", "").lower()
            if ext == "jpg":
                ext = "jpeg"
            return f"data:image/{ext};base64," + base64.b64encode(f.read()).decode("utf-8")
    return ""

def render_html(html_str: str):
    """
    Renders pure HTML cleanly into Streamlit DOM.
    Bypasses Markdown parsing to eliminate any 4-space code block conversion issues.
    """
    # Clean leading whitespace from each line
    cleaned = "\n".join(line.strip() for line in html_str.strip().splitlines() if line.strip())
    if hasattr(st, "html"):
        st.html(cleaned)
    else:
        st.markdown(cleaned, unsafe_allow_html=True)

def render_page_header(title: str, subtitle: Optional[str] = None, tag: Optional[str] = None) -> str:
    """Renders a refined Apple-styled page header."""
    tag_html = f'<span class="apple-badge apple-badge-accent" style="margin-left: 10px; font-size: 11px;">{tag}</span>' if tag else ""
    sub_html = f'<p class="apple-header-subtitle">{subtitle}</p>' if subtitle else ""
    return f'<div class="apple-header"><div><h1 class="apple-header-title">{title}{tag_html}</h1>{sub_html}</div></div>'

def render_metric_card(
    title: str,
    value: Any,
    subtitle: Optional[str] = None,
    icon: str = "layout-dashboard",
    status: str = "default"
) -> str:
    """Renders an Apple-styled stat/metric card."""
    icon_colors = {
        "critical": "#D70015",
        "warning": "#B87900",
        "success": "#248A3D",
        "accent": "#0071E3",
        "default": "#6E6E73"
    }
    color = icon_colors.get(status, "#6E6E73")
    icon_svg = get_icon(icon, size=16, color=color)
    sub_html = f'<div class="apple-stat-subtitle">{subtitle}</div>' if subtitle else ""
    
    return f'<div class="apple-stat-card"><div><div class="apple-stat-title">{icon_svg}<span>{title}</span></div><div class="apple-stat-value">{value}</div></div>{sub_html}</div>'

def render_badge(text: str, variant: str = "neutral") -> str:
    """Renders an Apple-styled status badge pill."""
    icon_map = {
        "critical": "alert-triangle",
        "warning": "alert-circle",
        "success": "check-circle-2",
        "accent": "sparkles",
        "neutral": "info"
    }
    icon_name = icon_map.get(variant.lower(), "info")
    icon_svg = get_icon(icon_name, size=12, color="currentColor")
    return f'<span class="apple-badge apple-badge-{variant.lower()}">{icon_svg} {text}</span>'

def render_empty_state(title: str, description: str, icon: str = "clipboard-list") -> str:
    """Renders a calm, human-designed empty state container."""
    icon_svg = get_icon(icon, size=32, color="#86868B")
    return f'<div style="background: #FFFFFF; border: 1px dashed #D2D2D7; border-radius: 12px; padding: 40px 24px; text-align: center; margin: 1.5rem 0;"><div style="margin-bottom: 12px;">{icon_svg}</div><h3 style="font-size: 16px; font-weight: 600; color: #1D1D1F; margin: 0 0 6px 0;">{title}</h3><p style="font-size: 13.5px; color: #6E6E73; max-width: 420px; margin: 0 auto; line-height: 1.4;">{description}</p></div>'

def render_card(content_html: str, title: Optional[str] = None, icon: Optional[str] = None) -> str:
    """Wraps HTML inside an Apple styled card."""
    header_html = ""
    if title:
        icon_svg = get_icon(icon, size=18, color="#0071E3") if icon else ""
        header_html = f'<div style="display: flex; align-items: center; gap: 8px; margin-bottom: 14px; padding-bottom: 10px; border-bottom: 1px solid #E5E5EA;">{icon_svg}<h3 style="font-size: 15px; font-weight: 600; color: #1D1D1F; margin: 0;">{title}</h3></div>'
    return f'<div class="apple-card">{header_html}{content_html}</div>'

def render_timeline_step(title: str, timestamp: str, description: str, status: str = "completed") -> str:
    """Renders a single step in a maintenance or audit timeline."""
    is_active = status == "current"
    bullet_color = "#0071E3" if is_active or status == "completed" else "#D2D2D7"
    return f'<div style="display: flex; gap: 14px; position: relative; padding-bottom: 18px;"><div style="display: flex; flex-direction: column; align-items: center;"><div style="width: 10px; height: 10px; border-radius: 50%; background-color: {bullet_color}; margin-top: 5px;"></div><div style="width: 1px; flex-grow: 1; background-color: #E5E5EA; margin-top: 4px;"></div></div><div><div style="display: flex; align-items: baseline; gap: 8px;"><span style="font-size: 13.5px; font-weight: 600; color: #1D1D1F;">{title}</span><span style="font-size: 11.5px; color: #86868B;">{timestamp}</span></div><p style="font-size: 12.5px; color: #6E6E73; margin: 2px 0 0 0; line-height: 1.4;">{description}</p></div></div>'
