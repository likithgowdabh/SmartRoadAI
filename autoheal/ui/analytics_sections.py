"""
Analytics dashboard — Streamlit + Plotly.
Premium upgrade: time filter, machine filter, enhanced KPIs, 5 dark-themed charts,
backend badge, and ML-powered failure risk section.
"""

from __future__ import annotations

from datetime import datetime, timedelta
from typing import Optional

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from db.database import (
    backend_name,
    fetch_action_distribution,
    fetch_analytics_kpis,
    fetch_anomaly_counts_by_machine,
    fetch_machine_series_chronological,
)
from ml.failure_prediction import predict_for_machine

# ── Config (graceful fallback if not present) ─────────────────────────────────
try:
    from config import cfg as _cfg

    _BACKEND_DISPLAY = _cfg.backend_display_name
    _BACKEND_ICON = _cfg.backend_icon
    _FAIL_THRESHOLD = int(_cfg.FAILURE_WARN_THRESHOLD_PCT)
except Exception:
    _BACKEND_DISPLAY = backend_name().title()
    _BACKEND_ICON = "🗄️"
    _FAIL_THRESHOLD = 55

# ── Plotly theme constants ─────────────────────────────────────────────────────
_LAYOUT_BASE: dict = dict(
    template="plotly_dark",
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(15,23,42,0.4)",
    font=dict(family="Inter, sans-serif", color="#e2e8f0"),
    margin=dict(l=8, r=8, t=42, b=8),
)
_ACCENT = ["#38bdf8", "#818cf8", "#34d399", "#fb923c", "#f472b6", "#a78bfa"]


def _layout(**extra) -> dict:
    return {**_LAYOUT_BASE, **extra}


# ── Helpers ───────────────────────────────────────────────────────────────────
def _action_bucket(label: str) -> str:
    s = (label or "").lower()
    if "shutdown" in s:
        return "Shutdown"
    if "cool" in s:
        return "Cooling"
    if "load" in s:
        return "Load Reduction"
    if "no action" in s or "no autonomous" in s or "none" in s:
        return "No Action"
    return "Other"


_TIME_DELTAS: dict[str, Optional[timedelta]] = {
    "All":          None,
    "Last 10 min":  timedelta(minutes=10),
    "Last 1 hour":  timedelta(hours=1),
    "Last 6 hours": timedelta(hours=6),
    "Last 24 hours": timedelta(hours=24),
}


def _filter_by_time(df: pd.DataFrame, window: str) -> pd.DataFrame:
    """Return rows within the selected time window. Handles naive timestamps."""
    delta = _TIME_DELTAS.get(window)
    if delta is None or df.empty:
        return df
    df = df.copy()
    df["_ts"] = pd.to_datetime(df["timestamp"], errors="coerce")
    # Use local 'now' since simulator timestamps are local
    cutoff = datetime.now() - delta
    mask = df["_ts"] >= cutoff
    return df[mask].drop(columns=["_ts"])


# ── Premium KPI card HTML ─────────────────────────────────────────────────────
def _kpi_html(label: str, value: str, sub: str = "", color: str = "#38bdf8") -> str:
    sub_fragment = (
        f"<div style='font-size:0.7rem;color:#64748b;margin-top:4px;'>{sub}</div>"
        if sub else ""
    )
    return f"""
    <div style="
        background:linear-gradient(135deg,rgba(15,23,42,0.9),rgba(30,41,59,0.65));
        border:1px solid rgba(56,189,248,0.15);
        border-radius:14px; padding:16px 14px; text-align:center; min-height:96px;
        box-shadow:0 2px 12px rgba(0,0,0,0.3);
    ">
        <div style="font-size:0.68rem;color:#64748b;text-transform:uppercase;
                    letter-spacing:0.09em;margin-bottom:5px;">{label}</div>
        <div style="font-size:2rem;font-weight:700;color:{color};
                    font-family:'Inter',sans-serif;line-height:1.1;">{value}</div>
        {sub_fragment}
    </div>
    """


# ── Main render function ───────────────────────────────────────────────────────
def render_analytics_panel(
    active_machine: str,
    current_temp: float,
    current_vib: float,
    current_volt: float,
) -> None:

    # ── Backend badge ──────────────────────────────────────────────────────
    st.markdown(
        f"""
        <div style="display:inline-flex;align-items:center;gap:8px;
                    background:rgba(56,189,248,0.07);
                    border:1px solid rgba(56,189,248,0.2);
                    border-radius:20px;padding:5px 16px;margin-bottom:16px;">
            <span style="font-size:1rem;">{_BACKEND_ICON}</span>
            <span style="font-size:0.78rem;color:#94a3b8;">Storage backend:</span>
            <span style="font-size:0.82rem;font-weight:700;color:#38bdf8;">{_BACKEND_DISPLAY}</span>
            <span style="font-size:0.72rem;color:#475569;">— charts read live from DB</span>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # ── Filter controls ────────────────────────────────────────────────────
    fl1, fl2 = st.columns([1, 1])
    with fl1:
        time_window: str = st.selectbox(
            "⏱ Time window",
            list(_TIME_DELTAS.keys()),
            index=0,
            key="analytics_time_window",
        )
    with fl2:
        try:
            _all_series_quick = fetch_machine_series_chronological(limit=200)
        except Exception:
            _all_series_quick = pd.DataFrame(columns=["machine_id"])
        _machine_opts = ["All machines"] + (
            sorted(_all_series_quick["machine_id"].unique().tolist())
            if not _all_series_quick.empty else []
        )
        _default_idx = (
            _machine_opts.index(active_machine)
            if active_machine in _machine_opts else 0
        )
        machine_filter: str = st.selectbox(
            "🏭 Machine",
            _machine_opts,
            index=_default_idx,
            key="analytics_machine_filter",
        )

    selected_machine: Optional[str] = (
        None if machine_filter == "All machines" else machine_filter
    )

    st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)

    # ── KPI cards ──────────────────────────────────────────────────────────
    try:
        kpis = fetch_analytics_kpis()
    except Exception:
        kpis = {"total_readings": 0, "total_anomalies": 0,
                "total_actions": 0, "avg_temperature": 0.0}
    n_read = max(1, int(kpis["total_readings"]))
    fail_rate = 100.0 * kpis["total_anomalies"] / n_read

    k1, k2, k3, k4 = st.columns(4)
    _kpis = [
        (k1, "Total Anomalies",   str(int(kpis["total_anomalies"])), "all time",           "#f87171"),
        (k2, "Total Actions",     str(int(kpis["total_actions"])),   "autonomous",         "#34d399"),
        (k3, "Avg Temperature",   f"{kpis['avg_temperature']:.1f}°C", "all readings",      "#fbbf24"),
        (k4, "Failure Rate",      f"{fail_rate:.1f}%",              "anomalies ÷ reads",  "#fb923c"),
    ]
    for col, lbl, val, sub, clr in _kpis:
        with col:
            st.markdown(_kpi_html(lbl, val, sub, clr), unsafe_allow_html=True)

    st.markdown("<div style='height:20px'></div>", unsafe_allow_html=True)

    # ── Sensor trend charts ────────────────────────────────────────────────
    st.markdown("#### 📈 Sensor Trends")

    try:
        series = fetch_machine_series_chronological(limit=2000, machine_id=selected_machine)
    except Exception as _e:
        series = pd.DataFrame()
        st.warning(f"⚠️ Sensor data unavailable: {_e}", icon="🔌")
    series = _filter_by_time(series, time_window)

    if series.empty:
        st.info(
            "No sensor data in this window yet. Run the live dashboard for a few cycles.",
            icon="📡",
        )
    else:
        _sensor_cfg = [
            ("temperature", "Temperature (°C)", "#f87171"),
            ("vibration",   "Vibration (g)",    "#fbbf24"),
            ("voltage",     "Voltage (V)",       "#38bdf8"),
        ]
        for col_name, lbl, clr in _sensor_cfg:
            if col_name not in series.columns:
                continue
            color_arg = (
                {"color": "machine_id", "color_discrete_sequence": _ACCENT}
                if selected_machine is None
                else {"color_discrete_sequence": [clr]}
            )
            fig = px.line(
                series,
                x="timestamp",
                y=col_name,
                title=lbl + " vs Time",
                **color_arg,
            )
            fig.update_traces(line=dict(width=2))
            fig.update_layout(**_layout(height=260))
            st.plotly_chart(fig, use_container_width=True, key=f"analytics_{col_name}_line")

    st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)

    # ── Anomalies & action distribution ───────────────────────────────────
    st.markdown("#### 🔍 Anomalies & Actions")
    bar_col, pie_col = st.columns(2)

    with bar_col:
        try:
            ac = fetch_anomaly_counts_by_machine()
        except Exception:
            ac = pd.DataFrame()
        if ac.empty:
            st.caption("No anomaly aggregates yet — wait for a few pipeline cycles.")
        else:
            fig_b = px.bar(
                ac,
                x="machine_id",
                y="anomaly_count",
                title="Anomalies per Machine",
                color="anomaly_count",
                color_continuous_scale=["#1e293b", "#f43f5e"],
                text_auto=True,
            )
            fig_b.update_traces(
                textposition="outside",
                textfont=dict(color="#e2e8f0", size=11),
                marker_line_color="rgba(0,0,0,0)",
            )
            fig_b.update_layout(
                **_layout(height=330, coloraxis_showscale=False, showlegend=False)
            )
            st.plotly_chart(fig_b, use_container_width=True, key="analytics_anom_bar")

    with pie_col:
        try:
            ad = fetch_action_distribution()
        except Exception:
            ad = pd.DataFrame()
        if ad.empty:
            st.caption("No action aggregates yet.")
        else:
            ad = ad.copy()
            ad["category"] = ad["action_taken"].map(_action_bucket)
            pie_df = ad.groupby("category", as_index=False)["cnt"].sum()
            fig_p = go.Figure(
                data=[
                    go.Pie(
                        labels=pie_df["category"],
                        values=pie_df["cnt"],
                        hole=0.44,
                        marker=dict(
                            colors=_ACCENT[: len(pie_df)],
                            line=dict(color="#0f172a", width=2),
                        ),
                        textfont=dict(color="#e2e8f0", size=12),
                    )
                ]
            )
            fig_p.update_layout(title="Action Distribution", **_layout(height=330))
            st.plotly_chart(fig_p, use_container_width=True, key="analytics_action_pie")

    st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)

    # ── Failure risk (ML + heuristic) ──────────────────────────────────────
    st.markdown("#### 🤖 Failure Risk Prediction (ML + Heuristic)")

    thr = st.slider(
        "Alert if failure probability ≥ (%)",
        20, 90, _FAIL_THRESHOLD,
        key="pred_threshold",
    )

    pred = predict_for_machine(
        active_machine,
        current_temp=current_temp,
        current_vib=current_vib,
        current_volt=current_volt,
        risk_threshold_pct=float(thr),
    )

    pct_clr = "#f87171" if pred["failure_probability_pct"] >= thr else "#34d399"
    p1, p2, p3 = st.columns(3)
    with p1:
        st.markdown(
            _kpi_html("Failure Probability (6h)", f"{pred['failure_probability_pct']}%", color=pct_clr),
            unsafe_allow_html=True,
        )
    with p2:
        st.markdown(
            _kpi_html("Est. Time to Failure", f"{pred['estimated_ttf_hours']}h", color="#fbbf24"),
            unsafe_allow_html=True,
        )
    with p3:
        src_lbl = pred["source"].replace("_", " ").title()
        st.markdown(
            _kpi_html("Model Source", src_lbl, color="#818cf8"),
            unsafe_allow_html=True,
        )

    st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)

    if pred["warn"]:
        st.error(
            f"⚠️ **Elevated Risk** — probability **{pred['failure_probability_pct']}%** "
            f"exceeds your **{thr}%** threshold. Schedule inspection or reduce load immediately.",
            icon="🚨",
        )
    else:
        st.success("✅ Risk within threshold — continue monitoring.", icon="🛡️")

    st.caption(f"ℹ️ {pred['message']}")
