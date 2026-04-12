"""
AutoHeal persistence façade.

AUTOHEAL_DB_BACKEND:
  - sqlite (default): autoheal/db/autoheal.db
  - firestore: Google Cloud Firestore (set GOOGLE_APPLICATION_CREDENTIALS)

AUTOHEAL_DB_FALLBACK_SQLITE (default 1): if Firestore fails to init, use SQLite.
"""

from __future__ import annotations

import logging
import os
from typing import Optional

import pandas as pd

logger = logging.getLogger(__name__)

_REQUESTED = os.environ.get("AUTOHEAL_DB_BACKEND", "sqlite").strip().lower()
_FALLBACK_SQLITE = os.environ.get("AUTOHEAL_DB_FALLBACK_SQLITE", "1").strip() == "1"

_backend = None
_effective: Optional[str] = None


def _load_backend():
    """Lazy-init storage backend (Firestore with optional SQLite fallback)."""
    global _backend, _effective
    if _backend is not None:
        return _backend

    from db import sqlite_backend as sqlite_mod

    if _REQUESTED == "firestore":
        try:
            from db import firestore_backend as fs_mod

            fs_mod.init_firestore()
            _backend = fs_mod
            _effective = "firestore"
            logger.info("AutoHeal using Firestore backend.")
            return _backend
        except Exception as exc:
            logger.warning("Firestore unavailable (%s).", exc)
            if not _FALLBACK_SQLITE:
                raise
            _backend = sqlite_mod
            _effective = "sqlite"
            logger.info("AutoHeal fell back to SQLite at %s", sqlite_mod.DB_PATH)
            return _backend

    _backend = sqlite_mod
    _effective = "sqlite"
    logger.info("AutoHeal using SQLite at %s", sqlite_mod.DB_PATH)
    return _backend


def backend_name() -> str:
    _load_backend()
    assert _effective is not None
    return _effective


def init_db() -> None:
    _load_backend().init_db()


def insert_machine_data(
    machine_id: str,
    temperature: float,
    vibration: float,
    voltage: float,
    timestamp: str,
) -> int:
    return _load_backend().insert_machine_data(
        machine_id, temperature, vibration, voltage, timestamp
    )


def log_anomaly(
    machine_id: str,
    anomaly_type: str,
    severity: str,
    timestamp: str,
) -> int:
    return _load_backend().log_anomaly(machine_id, anomaly_type, severity, timestamp)


def store_action(machine_id: str, action_taken: str, timestamp: str) -> int:
    return _load_backend().store_action(machine_id, action_taken, timestamp)


def append_log(event_description: str, timestamp: str) -> int:
    return _load_backend().append_log(event_description, timestamp)


def fetch_recent_logs(limit: int = 50) -> pd.DataFrame:
    return _load_backend().fetch_recent_logs(limit)


def fetch_recent_anomalies(limit: int = 20) -> pd.DataFrame:
    return _load_backend().fetch_recent_anomalies(limit)


def fetch_recent_actions(limit: int = 20) -> pd.DataFrame:
    return _load_backend().fetch_recent_actions(limit)


def fetch_recent_machine_data(limit: int = 100, machine_id: Optional[str] = None) -> pd.DataFrame:
    return _load_backend().fetch_recent_machine_data(limit, machine_id)


def fetch_machine_series_chronological(
    limit: int = 2000,
    machine_id: Optional[str] = None,
) -> pd.DataFrame:
    return _load_backend().fetch_machine_series_chronological(limit, machine_id)


def fetch_anomaly_counts_by_machine() -> pd.DataFrame:
    return _load_backend().fetch_anomaly_counts_by_machine()


def fetch_action_distribution() -> pd.DataFrame:
    return _load_backend().fetch_action_distribution()


def fetch_analytics_kpis() -> dict[str, float]:
    return _load_backend().fetch_analytics_kpis()


def save_to_db(df: pd.DataFrame, machine_id: Optional[str] = None) -> None:
    _load_backend().save_to_db(df, machine_id)


def get_history(limit: int = 10) -> pd.DataFrame:
    return _load_backend().get_history(limit)


def sample_insert_and_fetch() -> None:
    from datetime import datetime

    init_db()
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    mid = "SAMPLE-MACHINE-01"

    insert_machine_data(mid, 72.5, 0.45, 230.0, ts)
    log_anomaly(mid, "Overheating", "HIGH", ts)
    store_action(mid, "Cooling system activated", ts)
    append_log(
        "HIGH | Health 55.0/100 | Overheating | Action: Cooling system activated", ts
    )

    print("Backend:", backend_name())
    print("Recent machine_data:\n", fetch_recent_machine_data(5, machine_id=mid))
    print("Recent anomalies:\n", fetch_recent_anomalies(5))
    print("Recent actions:\n", fetch_recent_actions(5))
    print("Recent logs:\n", fetch_recent_logs(5))


try:
    init_db()
except Exception as _init_exc:
    logger.warning("AutoHeal DB init deferred: %s", _init_exc)


if __name__ == "__main__":
    sample_insert_and_fetch()
