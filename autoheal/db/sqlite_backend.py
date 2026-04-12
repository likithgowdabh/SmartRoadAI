"""
SQLite implementation — used by default and as offline fallback.
"""

from __future__ import annotations

import os
import sqlite3
from contextlib import contextmanager
from typing import Any, Iterator, Optional, Sequence

import pandas as pd

_PACKAGE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(_PACKAGE_DIR, "autoheal.db")


def _configure_connection(conn: sqlite3.Connection) -> None:
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    conn.execute("PRAGMA journal_mode = WAL")
    conn.execute("PRAGMA synchronous = NORMAL")


@contextmanager
def get_connection() -> Iterator[sqlite3.Connection]:
    conn = sqlite3.connect(DB_PATH, timeout=30.0)
    try:
        _configure_connection(conn)
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def init_db() -> None:
    os.makedirs(os.path.dirname(DB_PATH) or ".", exist_ok=True)
    with get_connection() as conn:
        cur = conn.cursor()
        cur.executescript(
            """
            CREATE TABLE IF NOT EXISTS machine_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                machine_id TEXT NOT NULL,
                temperature REAL NOT NULL,
                vibration REAL NOT NULL,
                voltage REAL NOT NULL,
                timestamp TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS anomalies (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                machine_id TEXT NOT NULL,
                type TEXT NOT NULL,
                severity TEXT NOT NULL,
                timestamp TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS actions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                machine_id TEXT NOT NULL,
                action_taken TEXT NOT NULL,
                timestamp TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                event_description TEXT NOT NULL,
                timestamp TEXT NOT NULL
            );

            CREATE INDEX IF NOT EXISTS idx_machine_data_ts
                ON machine_data (timestamp DESC);
            CREATE INDEX IF NOT EXISTS idx_machine_data_mid_ts
                ON machine_data (machine_id, timestamp DESC);

            CREATE INDEX IF NOT EXISTS idx_anomalies_ts
                ON anomalies (timestamp DESC);
            CREATE INDEX IF NOT EXISTS idx_actions_ts
                ON actions (timestamp DESC);
            CREATE INDEX IF NOT EXISTS idx_logs_ts
                ON logs (timestamp DESC);
            """
        )


def insert_machine_data(
    machine_id: str,
    temperature: float,
    vibration: float,
    voltage: float,
    timestamp: str,
) -> int:
    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute(
            """
            INSERT INTO machine_data (machine_id, temperature, vibration, voltage, timestamp)
            VALUES (?, ?, ?, ?, ?)
            """,
            (machine_id, temperature, vibration, voltage, timestamp),
        )
        return int(cur.lastrowid)


def log_anomaly(
    machine_id: str,
    anomaly_type: str,
    severity: str,
    timestamp: str,
) -> int:
    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute(
            """
            INSERT INTO anomalies (machine_id, type, severity, timestamp)
            VALUES (?, ?, ?, ?)
            """,
            (machine_id, anomaly_type, severity, timestamp),
        )
        return int(cur.lastrowid)


def store_action(machine_id: str, action_taken: str, timestamp: str) -> int:
    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute(
            """
            INSERT INTO actions (machine_id, action_taken, timestamp)
            VALUES (?, ?, ?)
            """,
            (machine_id, action_taken, timestamp),
        )
        return int(cur.lastrowid)


def append_log(event_description: str, timestamp: str) -> int:
    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute(
            """
            INSERT INTO logs (event_description, timestamp)
            VALUES (?, ?)
            """,
            (event_description, timestamp),
        )
        return int(cur.lastrowid)


def _rows_to_dataframe(rows: list[sqlite3.Row], columns: list[str]) -> pd.DataFrame:
    if not rows:
        return pd.DataFrame(columns=columns)
    data = [tuple(r[c] for c in columns) for r in rows]
    return pd.DataFrame(data, columns=columns)


def fetch_query(query: str, params: Sequence[Any] = ()) -> list[sqlite3.Row]:
    """Execute a SELECT query. Auto-inits the DB if tables are missing."""
    try:
        with get_connection() as conn:
            cur = conn.cursor()
            cur.execute(query, tuple(params))
            return cur.fetchall()
    except sqlite3.OperationalError as exc:
        if "no such table" in str(exc).lower():
            # Tables haven't been created yet — initialise and retry once.
            try:
                init_db()
                with get_connection() as conn:
                    cur = conn.cursor()
                    cur.execute(query, tuple(params))
                    return cur.fetchall()
            except Exception:
                # DB truly unavailable (read-only fs, etc.) — return empty.
                return []
        raise



def fetch_recent_logs(limit: int = 50) -> pd.DataFrame:
    limit = max(1, min(int(limit), 10_000))
    rows = fetch_query(
        """
        SELECT id, event_description, timestamp
        FROM logs
        ORDER BY id DESC
        LIMIT ?
        """,
        (limit,),
    )
    return _rows_to_dataframe(rows, ["id", "event_description", "timestamp"])


def fetch_recent_anomalies(limit: int = 20) -> pd.DataFrame:
    limit = max(1, min(int(limit), 10_000))
    rows = fetch_query(
        """
        SELECT id, machine_id, type, severity, timestamp
        FROM anomalies
        ORDER BY id DESC
        LIMIT ?
        """,
        (limit,),
    )
    return _rows_to_dataframe(rows, ["id", "machine_id", "type", "severity", "timestamp"])


def fetch_recent_actions(limit: int = 20) -> pd.DataFrame:
    limit = max(1, min(int(limit), 10_000))
    rows = fetch_query(
        """
        SELECT id, machine_id, action_taken, timestamp
        FROM actions
        ORDER BY id DESC
        LIMIT ?
        """,
        (limit,),
    )
    return _rows_to_dataframe(rows, ["id", "machine_id", "action_taken", "timestamp"])


def fetch_recent_machine_data(limit: int = 100, machine_id: Optional[str] = None) -> pd.DataFrame:
    limit = max(1, min(int(limit), 10_000))
    if machine_id:
        rows = fetch_query(
            """
            SELECT id, machine_id, temperature, vibration, voltage, timestamp
            FROM machine_data
            WHERE machine_id = ?
            ORDER BY id DESC
            LIMIT ?
            """,
            (machine_id, limit),
        )
    else:
        rows = fetch_query(
            """
            SELECT id, machine_id, temperature, vibration, voltage, timestamp
            FROM machine_data
            ORDER BY id DESC
            LIMIT ?
            """,
            (limit,),
        )
    return _rows_to_dataframe(
        rows, ["id", "machine_id", "temperature", "vibration", "voltage", "timestamp"]
    )


def fetch_machine_series_chronological(
    limit: int = 2000,
    machine_id: Optional[str] = None,
) -> pd.DataFrame:
    """Oldest→newest for time-series charts (last `limit` points)."""
    limit = max(1, min(int(limit), 10_000))
    if machine_id:
        rows = fetch_query(
            """
            SELECT * FROM (
                SELECT id, machine_id, temperature, vibration, voltage, timestamp
                FROM machine_data
                WHERE machine_id = ?
                ORDER BY id DESC
                LIMIT ?
            ) sub
            ORDER BY timestamp ASC
            """,
            (machine_id, limit),
        )
    else:
        rows = fetch_query(
            """
            SELECT * FROM (
                SELECT id, machine_id, temperature, vibration, voltage, timestamp
                FROM machine_data
                ORDER BY id DESC
                LIMIT ?
            ) sub
            ORDER BY timestamp ASC
            """,
            (limit,),
        )
    return _rows_to_dataframe(
        rows, ["id", "machine_id", "temperature", "vibration", "voltage", "timestamp"]
    )


def fetch_anomaly_counts_by_machine() -> pd.DataFrame:
    rows = fetch_query(
        """
        SELECT machine_id, COUNT(*) AS anomaly_count
        FROM anomalies
        GROUP BY machine_id
        ORDER BY anomaly_count DESC
        """
    )
    return _rows_to_dataframe(rows, ["machine_id", "anomaly_count"])


def fetch_action_distribution() -> pd.DataFrame:
    rows = fetch_query(
        """
        SELECT action_taken, COUNT(*) AS cnt
        FROM actions
        GROUP BY action_taken
        ORDER BY cnt DESC
        """
    )
    return _rows_to_dataframe(rows, ["action_taken", "cnt"])


def fetch_analytics_kpis() -> dict[str, float]:
    rows = fetch_query(
        """
        SELECT
            (SELECT COUNT(*) FROM anomalies) AS total_anomalies,
            (SELECT COUNT(*) FROM actions) AS total_actions,
            (SELECT COUNT(*) FROM machine_data) AS total_readings,
            (SELECT AVG(temperature) FROM machine_data) AS avg_temperature
        """
    )
    if not rows:
        return {
            "total_anomalies": 0.0,
            "total_actions": 0.0,
            "total_readings": 0.0,
            "avg_temperature": 0.0,
        }
    r = rows[0]
    return {
        "total_anomalies": float(r["total_anomalies"] or 0),
        "total_actions": float(r["total_actions"] or 0),
        "total_readings": float(r["total_readings"] or 0),
        "avg_temperature": float(r["avg_temperature"] or 0.0),
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
