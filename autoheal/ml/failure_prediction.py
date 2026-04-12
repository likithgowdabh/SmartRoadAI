"""
Failure risk model: RandomForest on telemetry + anomaly history.

Uses `db.database` for reads. Train with `train_and_save_model()` or `sample_train_and_predict.py`.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Optional

import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier

from db.database import (
    fetch_machine_series_chronological,
    fetch_recent_anomalies,
)

_ARTIFACT_DIR = Path(__file__).resolve().parent / "artifacts"
_MODEL_PATH = _ARTIFACT_DIR / "failure_model.joblib"

FEATURE_COLUMNS = [
    "temperature",
    "vibration",
    "voltage",
    "temp_ma5",
    "vib_ma5",
    "volt_ma5",
    "anomaly_count_24h",
]

HORIZON_HOURS = 6
MIN_TRAIN_ROWS = 40


def _ensure_artifact_dir() -> None:
    _ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)


def _build_labeled_frame(
    machine_limit: int = 8000,
    anomaly_limit: int = 8000,
) -> Optional[pd.DataFrame]:
    md = fetch_machine_series_chronological(limit=machine_limit)
    an = fetch_recent_anomalies(limit=anomaly_limit)
    if md.empty or len(md) < 15:
        return None

    md = md.copy()
    md["ts"] = pd.to_datetime(md["timestamp"], errors="coerce")
    md = md.dropna(subset=["ts"])
    an = an.copy()
    if not an.empty:
        an["ts"] = pd.to_datetime(an["timestamp"], errors="coerce")
        an = an.dropna(subset=["ts"])
    else:
        an["ts"] = pd.Series(dtype="datetime64[ns]")

    frames: list[pd.DataFrame] = []
    for mid, grp in md.groupby("machine_id"):
        g = grp.sort_values("ts").reset_index(drop=True)
        g["temp_ma5"] = g["temperature"].rolling(5, min_periods=1).mean()
        g["vib_ma5"] = g["vibration"].rolling(5, min_periods=1).mean()
        g["volt_ma5"] = g["voltage"].rolling(5, min_periods=1).mean()

        ac24: list[int] = []
        labels: list[int] = []
        for i, row in g.iterrows():
            t = row["ts"]
            if pd.isna(t):
                ac24.append(0)
                labels.append(0)
                continue
            if not an.empty:
                m24 = (
                    (an["machine_id"] == mid)
                    & (an["ts"] >= t - pd.Timedelta(hours=24))
                    & (an["ts"] <= t)
                )
                ac24.append(int(m24.sum()))
                mf = (
                    (an["machine_id"] == mid)
                    & (an["ts"] > t)
                    & (an["ts"] <= t + pd.Timedelta(hours=HORIZON_HOURS))
                )
                labels.append(int(mf.any()))
            else:
                ac24.append(0)
                labels.append(0)

        g["anomaly_count_24h"] = ac24
        g["y_failure"] = labels
        frames.append(g)

    out = pd.concat(frames, ignore_index=True)
    out = out.replace([np.inf, -np.inf], np.nan).dropna(subset=FEATURE_COLUMNS + ["y_failure"])
    return out


def train_and_save_model(
    machine_limit: int = 8000,
    anomaly_limit: int = 8000,
) -> dict[str, Any]:
    """
    Train RandomForest on historical machine_data + anomalies; persist to ml/artifacts/.
    Returns metrics dict (e.g. training_rows, pos_rate).
    """
    df = _build_labeled_frame(machine_limit, anomaly_limit)
    if df is None or len(df) < MIN_TRAIN_ROWS:
        raise ValueError(
            f"Not enough history for training (need ~{MIN_TRAIN_ROWS}+ labeled rows). "
            "Run the simulator longer or seed SQLite with sample data."
        )

    X = df[FEATURE_COLUMNS].values
    y = df["y_failure"].astype(int).values

    clf = RandomForestClassifier(
        n_estimators=80,
        max_depth=8,
        min_samples_leaf=2,
        class_weight="balanced_subsample",
        random_state=42,
        n_jobs=-1,
    )
    clf.fit(X, y)

    _ensure_artifact_dir()
    bundle = {
        "model": clf,
        "feature_columns": FEATURE_COLUMNS,
        "horizon_hours": HORIZON_HOURS,
        "train_rows": len(df),
        "positive_rate": float(y.mean()),
    }
    joblib.dump(bundle, _MODEL_PATH)
    return {k: v for k, v in bundle.items() if k != "model"}


def _load_model() -> Optional[dict[str, Any]]:
    if not _MODEL_PATH.is_file():
        return None
    try:
        return joblib.load(_MODEL_PATH)
    except Exception:
        return None


def _features_for_latest(machine_id: str, history_points: int = 120) -> Optional[np.ndarray]:
    try:
        md = fetch_machine_series_chronological(limit=history_points, machine_id=machine_id)
    except Exception:
        return None
    if md.empty or len(md) < 3:
        return None

    try:
        an = fetch_recent_anomalies(limit=2000)
    except Exception:
        an = pd.DataFrame()
    md = md.copy()
    md["ts"] = pd.to_datetime(md["timestamp"], errors="coerce")
    md = md.dropna(subset=["ts"]).sort_values("ts")
    an = an.copy()
    if not an.empty:
        an["ts"] = pd.to_datetime(an["timestamp"], errors="coerce")
        an = an.dropna(subset=["ts"])

    row = md.iloc[-1]
    t = row["ts"]
    tail = md.tail(5)
    temp_ma5 = tail["temperature"].mean()
    vib_ma5 = tail["vibration"].mean()
    volt_ma5 = tail["voltage"].mean()

    if not an.empty:
        m24 = (
            (an["machine_id"] == machine_id)
            & (an["ts"] >= t - pd.Timedelta(hours=24))
            & (an["ts"] <= t)
        )
        ac24 = int(m24.sum())
    else:
        ac24 = 0

    vec = np.array(
        [
            float(row["temperature"]),
            float(row["vibration"]),
            float(row["voltage"]),
            float(temp_ma5),
            float(vib_ma5),
            float(volt_ma5),
            float(ac24),
        ],
        dtype=np.float64,
    ).reshape(1, -1)
    return vec


def _heuristic_ttf(temp: float, vib: float, volt: float, risk_pct: float) -> float:
    """Hours — simple engineering prior when ML is unavailable."""
    stress = 0.0
    if temp > 85:
        stress += 0.35
    elif temp > 75:
        stress += 0.15
    if vib > 1.0:
        stress += 0.25
    elif vib > 0.7:
        stress += 0.1
    if volt > 270:
        stress += 0.2
    base = 72.0 * (1.0 - risk_pct / 100.0) * (1.0 - min(stress, 0.85))
    return float(max(0.5, base))


def predict_for_machine(
    machine_id: str,
    current_temp: Optional[float] = None,
    current_vib: Optional[float] = None,
    current_volt: Optional[float] = None,
    risk_threshold_pct: float = 55.0,
) -> dict[str, Any]:
    """
    Returns failure probability (0–100%), estimated time-to-failure (hours), and UI message.
    """
    bundle = _load_model()
    vec = _features_for_latest(machine_id)

    if bundle is not None and vec is not None:
        clf: RandomForestClassifier = bundle["model"]
        proba = float(clf.predict_proba(vec)[0, 1])
        pct = round(proba * 100.0, 1)
        last_row = fetch_machine_series_chronological(5, machine_id=machine_id)
        t = float(last_row["temperature"].iloc[-1]) if not last_row.empty else 70.0
        v = float(last_row["vibration"].iloc[-1]) if not last_row.empty else 0.5
        vo = float(last_row["voltage"].iloc[-1]) if not last_row.empty else 230.0
        ttf = _heuristic_ttf(t, v, vo, pct)
        msg = (
            f"Model trained on {bundle.get('train_rows', '?')} historical rows "
            f"({HORIZON_HOURS}h forward anomaly horizon)."
        )
        source = "random_forest"
    else:
        # Heuristic from live readings when no model / thin history
        t = current_temp if current_temp is not None else 70.0
        v = current_vib if current_vib is not None else 0.5
        vo = current_volt if current_volt is not None else 230.0
        raw = 0.12
        if t > 88:
            raw += 0.35
        elif t > 80:
            raw += 0.18
        if v > 1.2:
            raw += 0.28
        elif v > 0.85:
            raw += 0.12
        if vo > 275:
            raw += 0.15
        pct = round(min(95.0, raw * 100.0), 1)
        ttf = _heuristic_ttf(t, v, vo, pct)
        msg = (
            "Heuristic estimate (train a model with `python ml/sample_train_and_predict.py` "
            "once you have enough SQLite / Firestore history)."
        )
        source = "heuristic"

    warn = pct >= risk_threshold_pct
    return {
        "failure_probability_pct": pct,
        "estimated_ttf_hours": round(ttf, 1),
        "message": msg,
        "warn": warn,
        "source": source,
    }

