"""
AutoHeal AI — Main pipeline entry point.
thread-safe DB writes, 4-tier alert_level, config-driven thresholds.
"""

from __future__ import annotations

import logging
import threading

import pandas as pd
import sys
import os

# Add autoheal root to path to ensure modules are found
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from simulator.data_simulator import simulator
from core.anomaly import detect_anomaly
from core.health import compute_health
from core.decision import make_decision
from core.explain import generate_reason
from core.actions import get_action, apply_action, machine_state
from alerts.sound import trigger_alert
from db.database import save_to_db

logger = logging.getLogger(__name__)

# Thread lock for DB writes (Streamlit reruns can overlap)
_db_lock = threading.Lock()

# ── Thresholds (from config if available, else sensible defaults) ─────────────
try:
    from config import cfg as _cfg

    _TEMP_WARN  = _cfg.TEMP_WARNING
    _TEMP_CRIT  = _cfg.TEMP_CRITICAL
    _VIB_CRIT   = _cfg.VIBRATION_CRITICAL
    _VOLT_WARN  = _cfg.VOLTAGE_WARNING
    _VOLT_CRIT  = _cfg.VOLTAGE_CRITICAL
except Exception:
    _TEMP_WARN  = 80.0
    _TEMP_CRIT  = 90.0
    _VIB_CRIT   = 1.2
    _VOLT_WARN  = 250.0
    _VOLT_CRIT  = 270.0


def _compute_alert_level(row: dict) -> str:
    """
    4-tier alert badge derived from raw sensor readings + pipeline risk.
    Priority:  CRITICAL > HIGH > MEDIUM > LOW
    """
    temp    = float(row.get("temp",      0))
    vib     = float(row.get("vibration", 0))
    volt    = float(row.get("voltage",   0))
    risk    = str(row.get("risk", "LOW"))
    anomaly = int(row.get("anomaly", 0))

    # CRITICAL: any hard-limit breach
    if temp >= _TEMP_CRIT or vib >= _VIB_CRIT or volt >= _VOLT_WARN:
        return "CRITICAL"

    # HIGH: pipeline says HIGH risk or anomaly with elevated temp
    if risk == "HIGH" or (anomaly == 1 and temp >= _TEMP_WARN):
        return "HIGH"

    # MEDIUM: pipeline risk or anomaly without other triggers
    if risk == "MEDIUM" or (anomaly == 1):
        return "MEDIUM"

    return "LOW"


def run_pipeline(manual_anomaly: str | None = None, machine_id: str | None = None):
    """
    Executes the full AutoHeal AI pipeline.

    Parameters
    ----------
    manual_anomaly : str | None
        Anomaly type to inject ("Overheating", "High Vibration", "Voltage Spike").
    machine_id : str | None
        Logical machine name persisted to DB (uses simulator default when None).

    Returns
    -------
    (data: pd.DataFrame, machine_state: dict)
    """
    # ── 1. Data acquisition ───────────────────────────────────────────────
    if manual_anomaly:
        data = simulator.trigger_anomaly(manual_anomaly)
    else:
        data = simulator.generate_data()

    # ── 2. Core AI pipeline ───────────────────────────────────────────────
    data = detect_anomaly(data)
    data = compute_health(data)
    data = make_decision(data)
    data = generate_reason(data)

    # ── 3. Action engine ──────────────────────────────────────────────────
    data["action"] = data.apply(get_action, axis=1)
    data["result"] = data["action"].apply(apply_action)

    # ── 4. 4-tier alert level ─────────────────────────────────────────────
    data["alert_level"] = data.apply(
        lambda row: _compute_alert_level(row.to_dict()), axis=1
    )

    # ── 5. Sound / notification alert ────────────────────────────────────
    data = trigger_alert(data)

    # ── 6. Thread-safe DB write with graceful degradation ─────────────────
    with _db_lock:
        try:
            save_to_db(data, machine_id=machine_id)
        except Exception as exc:
            logger.warning("DB write failed (non-fatal, pipeline continues): %s", exc)

    return data, machine_state
