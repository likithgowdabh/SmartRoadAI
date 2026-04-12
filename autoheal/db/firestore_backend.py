"""
Google Cloud Firestore backend (optional).

Set AUTOHEAL_DB_BACKEND=firestore and GOOGLE_APPLICATION_CREDENTIALS to a service-account JSON.
"""

from __future__ import annotations

import logging
import uuid
from typing import Any, Optional

import pandas as pd

logger = logging.getLogger(__name__)

_client = None


def init_firestore() -> None:
    """Validate Firestore connectivity; raises if misconfigured."""
    global _client
    from google.cloud import firestore  # noqa: F401 — import check

    _client = firestore.Client()
    # Touch read to fail fast on bad credentials
    next(_client.collections(), None)


def _db():
    global _client
    if _client is None:
        from google.cloud import firestore

        _client = firestore.Client()
    return _client


def _add(coll: str, data: dict[str, Any]) -> str:
    doc_id = str(uuid.uuid4())
    data = {**data, "_doc_id": doc_id}
    _db().collection(coll).document(doc_id).set(data)
    return doc_id


def insert_machine_data(
    machine_id: str,
    temperature: float,
    vibration: float,
    voltage: float,
    timestamp: str,
) -> int:
    _add(
        "machine_data",
        {
            "machine_id": machine_id,
            "temperature": temperature,
            "vibration": vibration,
            "voltage": voltage,
            "timestamp": timestamp,
        },
    )
    return 0


def log_anomaly(
    machine_id: str,
    anomaly_type: str,
    severity: str,
    timestamp: str,
) -> int:
    _add(
        "anomalies",
        {
            "machine_id": machine_id,
            "type": anomaly_type,
            "severity": severity,
            "timestamp": timestamp,
        },
    )
    return 0


def store_action(machine_id: str, action_taken: str, timestamp: str) -> int:
    _add(
        "actions",
        {
            "machine_id": machine_id,
            "action_taken": action_taken,
            "timestamp": timestamp,
        },
    )
    return 0


def append_log(event_description: str, timestamp: str) -> int:
    _add(
        "logs",
        {
            "event_description": event_description,
            "timestamp": timestamp,
        },
    )
    return 0


def _df_from_snapshots(
    snapshots: list[Any],
    columns: list[str],
    extract: dict[str, str],
) -> pd.DataFrame:
    rows = []
    for snap in snapshots:
        d = snap.to_dict() or {}
        row = []
        for c in columns:
            key = extract.get(c, c)
            if c == "id":
                row.append(d.get("_doc_id", snap.id))
            else:
                row.append(d.get(key))
        rows.append(row)
    return pd.DataFrame(rows, columns=columns)


def fetch_recent_logs(limit: int = 50) -> pd.DataFrame:
    from google.cloud.firestore import Query

    limit = max(1, min(int(limit), 10_000))
    q = (
        _db()
        .collection("logs")
        .order_by("timestamp", direction=Query.DESCENDING)
        .limit(limit)
    )
    snaps = list(q.stream())
    return _df_from_snapshots(
        snaps,
        ["id", "event_description", "timestamp"],
        {"id": "_doc_id"},
    )


def fetch_recent_anomalies(limit: int = 20) -> pd.DataFrame:
    from google.cloud.firestore import Query

    limit = max(1, min(int(limit), 10_000))
    q = (
        _db()
        .collection("anomalies")
        .order_by("timestamp", direction=Query.DESCENDING)
        .limit(limit)
    )
    snaps = list(q.stream())
    return _df_from_snapshots(
        snaps,
        ["id", "machine_id", "type", "severity", "timestamp"],
        {"id": "_doc_id", "type": "type"},
    )


def fetch_recent_actions(limit: int = 20) -> pd.DataFrame:
    from google.cloud.firestore import Query

    limit = max(1, min(int(limit), 10_000))
    q = (
        _db()
        .collection("actions")
        .order_by("timestamp", direction=Query.DESCENDING)
        .limit(limit)
    )
    snaps = list(q.stream())
    return _df_from_snapshots(
        snaps,
        ["id", "machine_id", "action_taken", "timestamp"],
        {"id": "_doc_id"},
    )


def fetch_recent_machine_data(limit: int = 100, machine_id: Optional[str] = None) -> pd.DataFrame:
    from google.cloud.firestore import Query

    limit = max(1, min(int(limit), 10_000))
    q = _db().collection("machine_data").order_by(
        "timestamp", direction=Query.DESCENDING
    )
    snaps = list(q.limit(min(limit * 3, 3000)).stream())
    rows = []
    for snap in snaps:
        d = snap.to_dict() or {}
        if machine_id and d.get("machine_id") != machine_id:
            continue
        rows.append(snap)
        if len(rows) >= limit:
            break
    return _df_from_snapshots(
        rows,
        ["id", "machine_id", "temperature", "vibration", "voltage", "timestamp"],
        {"id": "_doc_id"},
    )


def fetch_machine_series_chronological(
    limit: int = 2000,
    machine_id: Optional[str] = None,
) -> pd.DataFrame:
    df = fetch_recent_machine_data(limit=limit, machine_id=machine_id)
    if df.empty:
        return df
    return df.sort_values("timestamp", ascending=True).reset_index(drop=True)


def fetch_anomaly_counts_by_machine() -> pd.DataFrame:
    counts: dict[str, int] = {}
    for snap in _db().collection("anomalies").stream():
        d = snap.to_dict() or {}
        mid = str(d.get("machine_id", "unknown"))
        counts[mid] = counts.get(mid, 0) + 1
    if not counts:
        return pd.DataFrame(columns=["machine_id", "anomaly_count"])
    rows = sorted(counts.items(), key=lambda x: -x[1])
    return pd.DataFrame(rows, columns=["machine_id", "anomaly_count"])


def fetch_action_distribution() -> pd.DataFrame:
    counts: dict[str, int] = {}
    for snap in _db().collection("actions").stream():
        d = snap.to_dict() or {}
        act = str(d.get("action_taken", ""))
        counts[act] = counts.get(act, 0) + 1
    if not counts:
        return pd.DataFrame(columns=["action_taken", "cnt"])
    rows = sorted(counts.items(), key=lambda x: -x[1])
    return pd.DataFrame(rows, columns=["action_taken", "cnt"])


def fetch_analytics_kpis() -> dict[str, float]:
    anom = sum(1 for _ in _db().collection("anomalies").stream())
    acts = sum(1 for _ in _db().collection("actions").stream())
    temps: list[float] = []
    reads = 0
    for snap in _db().collection("machine_data").stream():
        d = snap.to_dict() or {}
        reads += 1
        t = d.get("temperature")
        if t is not None:
            try:
                temps.append(float(t))
            except (TypeError, ValueError):
                pass
    avg_t = sum(temps) / len(temps) if temps else 0.0
    return {
        "total_anomalies": float(anom),
        "total_actions": float(acts),
        "total_readings": float(reads),
        "avg_temperature": float(avg_t),
    }


def save_to_db(df: pd.DataFrame, machine_id: Optional[str] = None) -> None:
    if df is None or df.empty:
        return

    row = df.iloc[0]
    ts = str(row["timestamp"])
    mid = machine_id if machine_id is not None else str(row.get("machine_id", "unknown"))

    insert_machine_data(
        mid,
        float(row["temp"]),
        float(row["vibration"]),
        float(row["voltage"]),
        ts,
    )

    severity = str(row.get("alert_level", row.get("risk", "LOW")))
    if int(row.get("anomaly", 0)) == 1:
        raw_reason = str(row.get("reason", "Unknown"))
        anomaly_type = raw_reason.split("|")[0].strip() or "Unknown"
        log_anomaly(mid, anomaly_type, severity, ts)

    store_action(mid, str(row.get("result", "No action")), ts)

    health = float(row.get("health", 0.0))
    risk = str(row.get("risk", "LOW"))
    reason = str(row.get("reason", ""))
    result = str(row.get("result", ""))
    event = f"{risk} | Health {health:.1f}/100 | {reason} | Action: {result}"
    append_log(event, ts)


def get_history(limit: int = 10) -> pd.DataFrame:
    df = fetch_recent_logs(limit)
    if df.empty:
        return pd.DataFrame(columns=["timestamp", "health", "risk", "action"])

    rows_out: list[dict[str, Any]] = []
    for _, r in df.iterrows():
        desc = str(r["event_description"])
        ts = str(r["timestamp"])
        risk = "LOW"
        health = 0.0
        action = desc
        parts = [p.strip() for p in desc.split("|")]
        if parts:
            risk = parts[0] if parts[0] in ("LOW", "MEDIUM", "HIGH", "CRITICAL") else "LOW"
        for p in parts:
            if p.startswith("Health "):
                try:
                    health = float(p.replace("Health", "").strip().split("/")[0])
                except ValueError:
                    health = 0.0
            if p.startswith("Action:"):
                action = p.replace("Action:", "").strip()
        rows_out.append(
            {"timestamp": ts, "health": health, "risk": risk, "action": action}
        )
    return pd.DataFrame(rows_out)


def init_db() -> None:
    """No schema migration required for Firestore."""
    logger.debug("Firestore backend: init_db is a no-op.")
