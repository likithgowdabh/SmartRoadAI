# AutoHeal AI — analytics, ML, and cloud database setup

## Run the dashboard

From the `autoheal` folder (so `main`, `db`, `ml`, and `ui` resolve on `PYTHONPATH`):

```bash
cd autoheal
pip install -r ../requirements.txt
streamlit run ui/app.py
```

Open the expander **“Analytics dashboard & failure forecast”** for Plotly charts, KPIs, and failure risk.

---

## Storage backends

| Mode | Environment | Notes |
|------|-------------|--------|
| **SQLite** (default) | _(unset or `AUTOHEAL_DB_BACKEND=sqlite`)_ | File: `db/autoheal.db` |
| **Firestore** | `AUTOHEAL_DB_BACKEND=firestore` + Google credentials | See below |
| **Fallback** | `AUTOHEAL_DB_FALLBACK_SQLITE=1` (default) | If Firestore init fails, SQLite is used |

### Firestore (Google Cloud)

1. Create a Firebase / GCP project and enable **Firestore** (Native mode).
2. Create a **service account** with a role that can read/write Firestore (e.g. `Cloud Datastore User`).
3. Download the JSON key and set:

```bash
set GOOGLE_APPLICATION_CREDENTIALS=C:\path\to\service-account.json
set AUTOHEAL_DB_BACKEND=firestore
```

On Linux/macOS use `export` instead of `set`.

4. Collections used (created automatically): `machine_data`, `anomalies`, `actions`, `logs`.  
   Documents include a `timestamp` string (`YYYY-MM-DD HH:MM:SS`) for ordering. If the console asks for an **index** on `timestamp`, approve the suggested link once.

### MongoDB Atlas (optional)

This repo ships **SQLite + Firestore**. To use MongoDB instead, add a small backend module mirroring `db/firestore_backend.py` and switch the router in `db/database.py`.

---

## Train the failure model

The model learns whether an **anomaly row** appears in the **next 6 hours** after each sensor reading (per machine), using rolling temperature/vibration/voltage features and anomaly count in the last 24 hours.

From `autoheal`:

```bash
python ml/sample_train_and_predict.py
```

If training raises “not enough history”, let Streamlit run longer (auto-refresh) or use the demo simulator until you have dozens of rows in `machine_data` and some `anomalies`.

Artifacts are written to `ml/artifacts/failure_model.joblib`.

---

## Project layout

- `db/database.py` — façade (SQLite or Firestore + fallback)
- `db/sqlite_backend.py` — local SQLite
- `db/firestore_backend.py` — cloud Firestore
- `ml/failure_prediction.py` — train / predict API
- `ml/sample_train_and_predict.py` — example CLI
- `ui/analytics_sections.py` — analytics + prediction UI
- `ui/app.py` — main Streamlit app

---

## Troubleshooting

- **`ModuleNotFoundError: db`**: run Streamlit from the `autoheal` directory, not the repo root.
- **Firestore permission errors**: verify `GOOGLE_APPLICATION_CREDENTIALS` and IAM roles.
- **Charts empty**: confirm `machine_data` has rows (pipeline must have run at least once).
