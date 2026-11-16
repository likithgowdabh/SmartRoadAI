# SmartRoad AI

> **Better Roads. Smarter Cities.**  
> A premium, Apple-inspired road intelligence and maintenance management platform powered by computer vision.

[![Python](https://img.shields.io/badge/Python-3.11%20%7C%203.12-blue.svg)](https://www.python.org/)
[![Framework](https://img.shields.io/badge/Streamlit-1.34+-FF4B4B.svg)](https://streamlit.io/)
[![Vision](https://img.shields.io/badge/YOLO11-Ultralytics-0071E3.svg)](https://docs.ultralytics.com/)
[![License](https://img.shields.io/badge/License-MIT-248A3D.svg)](LICENSE)

---

## 🌟 Overview

**SmartRoad AI** transforms municipal road maintenance from reactive patching to proactive, intelligence-driven road governance. By uniting computer vision with an empirical multi-factor priority engine, the platform enables city authorities and citizens to detect road damage, calculate maintenance urgency, dispatch field repair squads, and audit municipal investments.

Designed under Apple's human interface design principles (macOS Sequoia & Apple Maps aesthetic), SmartRoad AI delivers clarity, precision, and calm visual hierarchy to enterprise municipal infrastructure.

---

## 💎 Design Philosophy & Aesthetic

* **Typography:** System typography stack (`-apple-system, BlinkMacSystemFont, "SF Pro Display", "Inter"`).
* **Color System:** Restrained municipal palette:
  - Primary Background: `#FFFFFF`
  - Secondary Background: `#F5F5F7`
  - Sidebar: `#FAFAFC`
  - Primary Text: `#1D1D1F`
  - Accent Blue: `#0071E3`
  - Status Indicators: Critical (`#D70015`), Warning (`#B87900`), Success (`#248A3D`).
* **Iconography:** Lucide vector icons styled after Apple SF Symbols with uniform 1.8px stroke width. **Zero emoji icons** in professional views.
* **Layout:** 8-point spatial grid with subtle 1px dividers, refined cards, and minimal drop shadows.

---

## 🚀 Key Features

1. **Executive Overview Dashboard:** Live KPI telemetry (Total Reports, Critical Damage, Under Inspection, Completed Repairs), interactive Plotly area & donut charts, corridor density breakdowns, and top action queues.
2. **Road Reports Management:** Comprehensive data table with search, multi-parameter filtering (Severity, Status), sorting, inspection modal with photographic proof, GPS coordinates, inspector notes, and CSV/JSON export.
3. **AI Pothole Detection Studio:** Real-time road damage bounding, two-column visual comparison (Original vs AI Annotated), visual severity quantification, and one-click incident creation.
4. **Interactive Road Map:** Leaflet map with CartoDB Positron tiles, custom vector pins, popups, and instant incident inspection.
5. **Field Maintenance Management:** Work order dispatching, squad assignments, due date tracking, budget vs actual cost tracking, and status transitions.
6. **Citizen Reporting Portal:** 3-step reporting wizard with automated **Haversine duplicate detection** (flags hazards within 50 meters and increments citizen repeat confirmations).
7. **Municipal Analytics:** Cross-corridor trends, severity vs traffic density regressions, and ward risk profiles.
8. **Administration & Audit Trail:** User directory, role management, and immutable audit logs capturing every status change and priority recalculation.
9. **Universal Persistence:** Automatic detection of Supabase Cloud (PostgreSQL, Storage, RLS) with a seamless, zero-config local SQLite fallback.

---

## 📐 Priority Engine Equation

The platform calculates repair urgency using the empirical equation:

$$\text{Priority} = (0.40 \times \text{Severity}) + (0.30 \times \text{Traffic}) + (0.20 \times \text{Repeat Reports}) + (0.10 \times \text{Safety Risk})$$

### Thresholds:
- **75.0 – 100.0:** **Critical** (Immediate emergency repair)
- **40.0 – 74.9:** **Medium** (Scheduled municipal repair)
- **0.0 – 39.9:** **Low** (Routine maintenance queue)

---

## 🧠 AI Model & RDD2022 Dataset Training

SmartRoad AI integrates with a custom-trained **YOLO11n** model targeting class **D40 (Pothole)** from the international **RDD2022** road damage benchmark.

- **Dataset Tool:** `training/prepare_rdd2022.py` converts Pascal VOC XML annotations into normalized YOLO format and creates clean 80/10/10 non-leaking splits.
- **Colab GPU Pipeline:** `training/smartroad_yolo11_colab.ipynb` runs a complete end-to-end training pipeline on Google Colab's free T4 GPU (~15-20 minutes).
- **Target Weights:** `models/pothole_best.pt`.
- **Diagnostic State:** When weights are not yet present, SmartRoad AI provides a transparent configuration card and operates a genuine Computer Vision gradient/contour surface analyzer without fabricating model claims.

---

## 🛠️ Installation & Quickstart

### 1. Clone the repository
```bash
git clone https://github.com/<your-username>/SmartRoad-AI.git
cd SmartRoad-AI
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Launch application
```bash
streamlit run app.py
```
Open [http://localhost:8501](http://localhost:8501) in your browser.

---

## 🧪 Testing

Run the automated test suite covering priority calculations, duplicate detection, database CRUD, storage, and authentication:

```bash
python -m unittest tests/test_smartroad.py
```

All 13 tests run and pass out-of-the-box.

---

## 👥 Demo Personas (One-Click Switcher)

In the sidebar, use the **Simulate Persona** dropdown to test different role permissions:
- **Sophia Sterling (Admin):** Full system access, audit logs, priority tuning.
- **Marcus Vance (Maintenance Manager):** Work order dispatch, crew management, cost logging.
- **Elena Rostova (Road Inspector):** AI detection, severity updating, inspection notes.
- **Devon Carter (Citizen):** Public map, damage reporting, duplicate suggestions.

---

## 📄 License

MIT License. Designed and engineered for municipal road intelligence.
