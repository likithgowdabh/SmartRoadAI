"""
AutoHeal AI — Central Configuration
=====================================
Override any value via environment variable or a `.env` file in the project root.

Usage:
    from config import cfg
    print(cfg.DB_BACKEND)
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path

# ── try to load .env if python-dotenv is available ────────────────────────────
try:
    from dotenv import load_dotenv

    _env_file = Path(__file__).resolve().parent.parent / ".env"
    if _env_file.is_file():
        load_dotenv(_env_file)
except ImportError:
    pass  # dotenv is optional


@dataclass
class AutoHealConfig:
    # ── App identity ──────────────────────────────────────────────────────────
    APP_NAME: str = "AutoHeal AI"
    APP_VERSION: str = "3.0"

    # ── Database backend  ("sqlite" | "firestore") ───────────────────────────
    # Set env var AUTOHEAL_DB_BACKEND=firestore to switch to Firestore.
    DB_BACKEND: str = field(
        default_factory=lambda: os.environ.get(
            "AUTOHEAL_DB_BACKEND", "sqlite"
        ).strip().lower()
    )

    # ── Firestore ─────────────────────────────────────────────────────────────
    # Path to your Google service account JSON file.
    # Set env var GOOGLE_APPLICATION_CREDENTIALS or AUTOHEAL_FIREBASE_CREDS.
    FIREBASE_CREDENTIALS_PATH: str = field(
        default_factory=lambda: os.environ.get(
            "AUTOHEAL_FIREBASE_CREDS",
            os.environ.get("GOOGLE_APPLICATION_CREDENTIALS", ""),
        )
    )

    # If Firestore fails to connect, automatically fall back to SQLite.
    DB_FALLBACK_SQLITE: bool = field(
        default_factory=lambda: os.environ.get(
            "AUTOHEAL_DB_FALLBACK_SQLITE", "1"
        ).strip() == "1"
    )

    # ── Sensor thresholds ─────────────────────────────────────────────────────
    TEMP_WARNING: float = 80.0       # °C — triggers cooling action
    TEMP_CRITICAL: float = 90.0      # °C — triggers shutdown
    VIBRATION_WARNING: float = 0.7   # g  — triggers load reduction
    VIBRATION_CRITICAL: float = 1.2  # g  — triggers shutdown
    VOLTAGE_WARNING: float = 250.0   # V  — triggers shutdown (spike)
    VOLTAGE_CRITICAL: float = 270.0  # V  — immediate critical alert

    # ── Alert thresholds ──────────────────────────────────────────────────────
    # Failure probability (%) above which the UI shows a risk warning.
    FAILURE_WARN_THRESHOLD_PCT: float = 55.0

    # ── Business impact defaults ──────────────────────────────────────────────
    DOWNTIME_HOURS_DEFAULT: float = 6.0
    COST_PER_HOUR: float = 25_000.0  # INR

    # ── Simulation ────────────────────────────────────────────────────────────
    # Normal sensor ranges used by the data simulator.
    SIM_TEMP_MIN: float = 60.0
    SIM_TEMP_MAX: float = 90.0
    SIM_VIB_MIN: float = 0.2
    SIM_VIB_MAX: float = 1.0
    SIM_VOLT_MIN: float = 210.0
    SIM_VOLT_MAX: float = 270.0

    # Anomaly injection ranges.
    SIM_OVERHEAT_MIN: float = 91.0
    SIM_OVERHEAT_MAX: float = 105.0
    SIM_HIGH_VIB_MIN: float = 1.1
    SIM_HIGH_VIB_MAX: float = 2.0
    SIM_VOLT_SPIKE_MIN: float = 271.0
    SIM_VOLT_SPIKE_MAX: float = 300.0

    # ── Path helpers ──────────────────────────────────────────────────────────
    @property
    def PROJECT_ROOT(self) -> Path:
        return Path(__file__).resolve().parent

    @property
    def DB_PATH(self) -> Path:
        return self.PROJECT_ROOT / "db" / "autoheal.db"

    @property
    def ML_ARTIFACTS_DIR(self) -> Path:
        return self.PROJECT_ROOT / "ml" / "artifacts"

    # ── Derived helpers ───────────────────────────────────────────────────────
    @property
    def backend_display_name(self) -> str:
        """Human-readable backend label for the UI."""
        return "Firebase Firestore" if self.DB_BACKEND == "firestore" else "SQLite"

    @property
    def backend_icon(self) -> str:
        return "☁️" if self.DB_BACKEND == "firestore" else "🗄️"


# ── Singleton ─────────────────────────────────────────────────────────────────
cfg = AutoHealConfig()
