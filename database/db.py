"""
SmartRoad AI — Universal Database & Persistence Layer
Supports Supabase PostgreSQL with seamless local SQLite fallback.
"""

import os
import sqlite3
import json
import uuid
import datetime
from typing import Dict, Any, List, Optional, Tuple
from dotenv import load_dotenv

load_dotenv()

DB_DIR = os.path.dirname(__file__)
SQLITE_DB_PATH = os.path.join(DB_DIR, "smartroad.db")
SCHEMA_PATH = os.path.join(DB_DIR, "schema.sql")

SUPABASE_URL = os.getenv("SUPABASE_URL", "").strip()
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "").strip()

class DatabaseManager:
    """Universal Database Manager handling queries, transactions, and seeding."""

    def __init__(self, db_path: str = SQLITE_DB_PATH):
        self.db_path = db_path
        self.use_supabase = bool(SUPABASE_URL and SUPABASE_KEY and SUPABASE_URL.startswith("http"))
        self._init_sqlite()
        self._seed_initial_data()

    def get_connection(self) -> sqlite3.Connection:
        """Returns SQLite connection configured for reliability and concurrency."""
        conn = sqlite3.connect(self.db_path, check_same_thread=False)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON;")
        conn.execute("PRAGMA journal_mode = WAL;")
        return conn

    def _init_sqlite(self):
        """Initializes SQLite schema if not already initialized."""
        if not os.path.exists(SCHEMA_PATH):
            return
        with open(SCHEMA_PATH, "r", encoding="utf-8") as f:
            sql_script = f.read()
        
        # Filter out lines starting with --
        clean_lines = []
        for line in sql_script.splitlines():
            stripped = line.strip()
            if not stripped.startswith("--") and stripped:
                clean_lines.append(line)
        cleaned_sql = "\n".join(clean_lines)

        with self.get_connection() as conn:
            conn.executescript(cleaned_sql)
            conn.commit()

    def _seed_initial_data(self):
        """Seeds realistic municipal demo data if database is empty."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) as count FROM users")
            user_count = cursor.fetchone()["count"]
            if user_count > 0:
                return  # Database already seeded

            # Import password hasher from auth_service
            import hashlib
            def hash_pw(pw: str) -> str:
                return hashlib.sha256(pw.encode()).hexdigest()

            # 1. Seed Default Users
            users_data = [
                ("usr-admin-1", "admin@smartroad.ai", hash_pw("Admin@123"), "Sophia Sterling", "admin", "City Roads & Works Executive", "+1 (555) 019-2834"),
                ("usr-mgr-1", "manager@smartroad.ai", hash_pw("Manager@123"), "Marcus Vance", "maintenance_manager", "Asphalt Operations Division", "+1 (555) 018-9921"),
                ("usr-insp-1", "inspector@smartroad.ai", hash_pw("Inspector@123"), "Elena Rostova", "inspector", "Municipal Infrastructure Quality", "+1 (555) 014-5542"),
                ("usr-cit-1", "citizen@smartroad.ai", hash_pw("Citizen@123"), "Devon Carter", "citizen", "Resident - Zone 4", "+1 (555) 012-7719"),
            ]
            cursor.executemany(
                "INSERT INTO users (id, email, password_hash, full_name, role, department, phone) VALUES (?, ?, ?, ?, ?, ?, ?)",
                users_data
            )

            # 2. Seed Realistic Reports (Metropolitan City Coordinates - Bengaluru Tech & Commercial Corridors)
            reports_data = [
                ("REP-2026-001", "Severe Surface Rupture & Pothole Cluster", "Multiple deep potholes near expressway flyover causing severe deceleration and vehicle tire damage.", "Outer Ring Road (Near Bellandur Junction)", "Bellandur Corridor", "Bengaluru", 12.9304, 77.6784, "Critical", 88.5, "Severe", 4, "High", "Under Inspection", "assets/sample_pothole_1.jpg", "assets/sample_annotated_1.jpg", 3, "usr-cit-1", "Elena Rostova", "Urgent structural inspection required before monsoon shift."),
                ("REP-2026-002", "Transverse Edge Fracture & Pothole", "Asphalt breakup on eastbound slow lane near commercial bus terminal.", "Old Airport Road (HAL 2nd Stage)", "Indiranagar", "Bengaluru", 12.9612, 77.6483, "Critical", 82.0, "High", 3, "High", "Scheduled", "assets/sample_pothole_2.jpg", "assets/sample_annotated_2.jpg", 2, "usr-cit-1", "Elena Rostova", "Scheduled for cold mix patching."),
                ("REP-2026-003", "Medium Road Cavity Near Storm Drain", "Sunken asphalt patch around municipal manhole cover.", "100 Feet Road (Near 12th Main)", "Indiranagar", "Bengaluru", 12.9719, 77.6412, "Medium", 64.0, "High", 2, "Medium", "In Progress", "assets/sample_pothole_3.jpg", None, 1, "usr-cit-1", "Marcus Vance", "Civil works team en route with hot-mix machinery."),
                ("REP-2026-004", "Alligator Cracking & Depression", "Surface fatigue cracking transitioning into pothole formation.", "Sarjapur Main Road (Near Kaikondrahalli)", "Sarjapur", "Bengaluru", 12.9125, 77.6852, "Medium", 58.0, "Medium", 1, "Medium", "Reported", None, None, 1, "usr-cit-1", None, None),
                ("REP-2026-005", "Deep Crater on Arterial Intersection", "Severe crater depth > 80mm causing traffic backlog.", "Hosur Road (Near Silk Board Junction)", "BTM Layout", "Bengaluru", 12.9172, 77.6228, "Critical", 94.0, "Severe", 5, "High", "In Progress", "assets/sample_pothole_4.jpg", "assets/sample_annotated_4.jpg", 4, "usr-cit-1", "Marcus Vance", "High priority repair underway."),
                ("REP-2026-006", "Minor Surface Spalling", "Shallow asphalt surface peeling along cycle track border.", "Residency Road", "Central Business District", "Bengaluru", 12.9698, 77.6012, "Low", 31.0, "Low", 1, "Low", "Repaired", None, None, 1, "usr-cit-1", "Elena Rostova", "Cold asphalt patch completed and compacted."),
                ("REP-2026-007", "Longitudinal Crack with Pothole", "Crack expanding along lane divisor with minor pothole.", "MG Road (Near Trinity Circle)", "CBD", "Bengaluru", 12.9734, 77.6189, "Medium", 52.0, "Medium", 1, "Low", "Verified", None, None, 1, "usr-cit-1", "Elena Rostova", "Repairs inspected and verified by municipal engineer."),
                ("REP-2026-008", "Severe Subsidence Near Metro Pillar", "Large depression forming adjacent to Pillar 148.", "Kanakapura Road (Near Sarakki)", "JP Nagar", "Bengaluru", 12.9067, 77.5753, "Critical", 79.5, "High", 2, "High", "Under Inspection", None, None, 2, "usr-cit-1", "Elena Rostova", "Coordinating with Metro Rail infrastructure board."),
            ]

            cursor.executemany(
                """INSERT INTO reports (
                    id, title, description, road_name, area, city, latitude, longitude,
                    severity, priority_score, traffic_level, repeat_count, safety_risk,
                    status, image_url, annotated_image_url, detection_count, citizen_id,
                    assigned_to, inspector_notes
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                reports_data
            )

            # 3. Seed Maintenance Tasks
            tasks_data = [
                ("TSK-2026-01", "REP-2026-002", "Rapid Response Asphalt Team Alpha", "2026-11-18", "2026-11-20", None, "Scheduled", "Mobilizing 4-ton cold-mix crew with roller.", None, None, 1200.0, 0.0),
                ("TSK-2026-02", "REP-2026-003", "South Zone Pavement Division #3", "2026-11-16", "2026-11-17", None, "In Progress", "Excavating sub-base surrounding storm drain cover.", None, None, 1850.0, 950.0),
                ("TSK-2026-03", "REP-2026-005", "Emergency Highway Paving Squad", "2026-11-15", "2026-11-16", None, "In Progress", "Night operation deployment under police traffic diversion.", None, None, 3400.0, 2100.0),
                ("TSK-2026-04", "REP-2026-006", "City Center Maintenance Works", "2026-11-10", "2026-11-11", "2026-11-11", "Repaired", "Resurfacing finished and seal-coated.", None, None, 650.0, 620.0),
                ("TSK-2026-05", "REP-2026-007", "CBD Rapid Road Unit", "2026-11-08", "2026-11-09", "2026-11-09", "Verified", "Quality verification passed by Senior Inspector Rostova.", None, None, 800.0, 780.0),
            ]
            cursor.executemany(
                """INSERT INTO maintenance_tasks (
                    id, report_id, assigned_team, scheduled_date, due_date, completed_date,
                    status, repair_notes, before_image_url, after_image_url, budget_estimate, cost_actual
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                tasks_data
            )

            # 4. Seed Audit Logs
            audit_data = [
                ("AUD-001", "report", "REP-2026-005", "PRIORITY_RECALCULATED", "System Priority Engine", "65.0", "94.0"),
                ("AUD-002", "report", "REP-2026-005", "STATUS_CHANGE", "Marcus Vance", "Scheduled", "In Progress"),
                ("AUD-003", "task", "TSK-2026-02", "TEAM_ASSIGNED", "Marcus Vance", "Unassigned", "South Zone Pavement Division #3"),
                ("AUD-004", "report", "REP-2026-007", "VERIFICATION_APPROVED", "Elena Rostova", "Repaired", "Verified"),
            ]
            cursor.executemany(
                "INSERT INTO audit_logs (id, entity_type, entity_id, action, changed_by, old_value, new_value) VALUES (?, ?, ?, ?, ?, ?, ?)",
                audit_data
            )

            # 5. Seed System Settings
            settings_data = [
                ("weight_severity", "0.40", "Weight of visual damage severity in priority formula"),
                ("weight_traffic", "0.30", "Weight of traffic volume in priority formula"),
                ("weight_repeat", "0.20", "Weight of citizen repeat report frequency in priority formula"),
                ("weight_safety", "0.10", "Weight of hazard risk rating in priority formula"),
                ("duplicate_radius_meters", "50", "Distance threshold in meters to suggest duplicate road report"),
                ("auto_dispatch_critical", "true", "Automatically create scheduled task for priority >= 85.0"),
            ]
            cursor.executemany(
                "INSERT INTO system_settings (key, value, description) VALUES (?, ?, ?)",
                settings_data
            )

            conn.commit()

    # --- CRUD: REPORTS ---
    def get_reports(
        self,
        severity: Optional[str] = None,
        status: Optional[str] = None,
        search_query: Optional[str] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """Retrieves road reports with optional filtering."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            query = "SELECT * FROM reports WHERE 1=1"
            params = []

            if severity and severity != "All":
                query += " AND severity = ?"
                params.append(severity)
            if status and status != "All":
                query += " AND status = ?"
                params.append(status)
            if search_query:
                query += " AND (road_name LIKE ? OR area LIKE ? OR title LIKE ?)"
                wildcard = f"%{search_query}%"
                params.extend([wildcard, wildcard, wildcard])

            query += " ORDER BY priority_score DESC, created_at DESC LIMIT ? OFFSET ?"
            params.extend([limit, offset])

            cursor.execute(query, params)
            rows = cursor.fetchall()
            return [dict(row) for row in rows]

    def get_report_by_id(self, report_id: str) -> Optional[Dict[str, Any]]:
        """Fetches single report by its ID."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM reports WHERE id = ?", (report_id,))
            row = cursor.fetchone()
            return dict(row) if row else None

    def create_report(self, report_data: Dict[str, Any]) -> str:
        """Inserts a new road damage report."""
        if "id" not in report_data:
            report_data["id"] = f"REP-{datetime.datetime.now().year}-{str(uuid.uuid4())[:6].upper()}"

        # Safe defaults for NOT NULL columns
        defaults = {
            "city": "Bengaluru",
            "severity": "Medium",
            "priority_score": 50.0,
            "traffic_level": "Medium",
            "repeat_count": 1,
            "safety_risk": "Medium",
            "status": "Reported",
            "detection_count": 0
        }
        for k, v in defaults.items():
            if k not in report_data or report_data[k] is None:
                report_data[k] = v

        fields = [
            "id", "title", "description", "road_name", "area", "city",
            "latitude", "longitude", "severity", "priority_score",
            "traffic_level", "repeat_count", "safety_risk", "status",
            "image_url", "annotated_image_url", "detection_count",
            "citizen_id", "assigned_to", "inspector_notes"
        ]
        values = [report_data.get(f) for f in fields]
        placeholders = ", ".join(["?"] * len(fields))
        columns = ", ".join(fields)

        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(f"INSERT INTO reports ({columns}) VALUES ({placeholders})", values)
            
            # Log creation in audit
            cursor.execute(
                "INSERT INTO audit_logs (id, entity_type, entity_id, action, changed_by, old_value, new_value) VALUES (?, ?, ?, ?, ?, ?, ?)",
                (f"AUD-{str(uuid.uuid4())[:6].upper()}", "report", report_data["id"], "REPORT_CREATED", report_data.get("citizen_id", "Citizen"), None, f"Initial priority: {report_data.get('priority_score')}")
            )
            conn.commit()

        return report_data["id"]

    def update_report(self, report_id: str, updates: Dict[str, Any], changed_by: str = "Admin") -> bool:
        """Updates specific fields of an existing report and writes to audit log."""
        if not updates:
            return False
            
        old_report = self.get_report_by_id(report_id)
        if not old_report:
            return False

        set_clauses = []
        params = []
        for k, v in updates.items():
            set_clauses.append(f"{k} = ?")
            params.append(v)
            
        set_clauses.append("updated_at = CURRENT_TIMESTAMP")
        params.append(report_id)

        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(f"UPDATE reports SET {', '.join(set_clauses)} WHERE id = ?", params)

            # Record audit changes
            for k, new_v in updates.items():
                old_v = old_report.get(k)
                if str(old_v) != str(new_v):
                    cursor.execute(
                        "INSERT INTO audit_logs (id, entity_type, entity_id, action, changed_by, old_value, new_value) VALUES (?, ?, ?, ?, ?, ?, ?)",
                        (f"AUD-{str(uuid.uuid4())[:6].upper()}", "report", report_id, f"UPDATE_{k.upper()}", changed_by, str(old_v), str(new_v))
                    )
            conn.commit()
        return True

    # --- CRUD: MAINTENANCE TASKS ---
    def get_maintenance_tasks(self, status: Optional[str] = None) -> List[Dict[str, Any]]:
        """Retrieves maintenance tasks with associated report details."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            query = """
            SELECT t.*, r.title as report_title, r.road_name, r.area, r.severity, r.priority_score
            FROM maintenance_tasks t
            LEFT JOIN reports r ON t.report_id = r.id
            WHERE 1=1
            """
            params = []
            if status and status != "All":
                query += " AND t.status = ?"
                params.append(status)

            query += " ORDER BY t.created_at DESC"
            cursor.execute(query, params)
            return [dict(row) for row in cursor.fetchall()]

    def create_maintenance_task(self, task_data: Dict[str, Any], changed_by: str = "Manager") -> str:
        """Dispatches a new maintenance task."""
        if "id" not in task_data:
            task_data["id"] = f"TSK-{datetime.datetime.now().year}-{str(uuid.uuid4())[:4].upper()}"

        fields = [
            "id", "report_id", "assigned_team", "scheduled_date", "due_date",
            "completed_date", "status", "repair_notes", "before_image_url",
            "after_image_url", "budget_estimate", "cost_actual"
        ]
        values = [task_data.get(f) for f in fields]
        placeholders = ", ".join(["?"] * len(fields))

        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(f"INSERT INTO maintenance_tasks ({', '.join(fields)}) VALUES ({placeholders})", values)
            
            # Sync report status to 'Scheduled' or 'In Progress'
            cursor.execute(
                "UPDATE reports SET status = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?",
                (task_data.get("status", "Scheduled"), task_data["report_id"])
            )

            # Audit record
            cursor.execute(
                "INSERT INTO audit_logs (id, entity_type, entity_id, action, changed_by, old_value, new_value) VALUES (?, ?, ?, ?, ?, ?, ?)",
                (f"AUD-{str(uuid.uuid4())[:6].upper()}", "task", task_data["id"], "TASK_DISPATCHED", changed_by, None, f"Assigned to {task_data.get('assigned_team')}")
            )
            conn.commit()
            
        return task_data["id"]

    def update_maintenance_task(self, task_id: str, updates: Dict[str, Any], changed_by: str = "Manager") -> bool:
        """Updates maintenance task progress and records audit trail."""
        set_clauses = [f"{k} = ?" for k in updates.keys()]
        params = list(updates.values())
        params.append(task_id)

        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(f"UPDATE maintenance_tasks SET {', '.join(set_clauses)} WHERE id = ?", params)
            
            # If status updated, sync linked report
            if "status" in updates:
                cursor.execute("SELECT report_id FROM maintenance_tasks WHERE id = ?", (task_id,))
                row = cursor.fetchone()
                if row and row["report_id"]:
                    cursor.execute("UPDATE reports SET status = ? WHERE id = ?", (updates["status"], row["report_id"]))

            cursor.execute(
                "INSERT INTO audit_logs (id, entity_type, entity_id, action, changed_by, old_value, new_value) VALUES (?, ?, ?, ?, ?, ?, ?)",
                (f"AUD-{str(uuid.uuid4())[:6].upper()}", "task", task_id, "TASK_UPDATED", changed_by, None, json.dumps(updates))
            )
            conn.commit()
        return True

    # --- USERS & AUTH ---
    def get_users(self) -> List[Dict[str, Any]]:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, email, full_name, role, department, phone, created_at FROM users ORDER BY created_at DESC")
            return [dict(row) for row in cursor.fetchall()]

    def get_user_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users WHERE LOWER(email) = LOWER(?)", (email.strip(),))
            row = cursor.fetchone()
            return dict(row) if row else None

    def create_user(self, user_data: Dict[str, Any]) -> str:
        if "id" not in user_data:
            user_data["id"] = f"usr-{str(uuid.uuid4())[:8]}"

        fields = ["id", "email", "password_hash", "full_name", "role", "department", "phone"]
        values = [user_data.get(f) for f in fields]
        placeholders = ", ".join(["?"] * len(fields))

        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(f"INSERT INTO users ({', '.join(fields)}) VALUES ({placeholders})", values)
            conn.commit()
        return user_data["id"]

    # --- AUDIT LOGS & SETTINGS ---
    def get_audit_logs(self, limit: int = 50) -> List[Dict[str, Any]]:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM audit_logs ORDER BY timestamp DESC, rowid DESC LIMIT ?", (limit,))
            return [dict(row) for row in cursor.fetchall()]

    def get_system_settings(self) -> Dict[str, str]:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT key, value FROM system_settings")
            return {row["key"]: row["value"] for row in cursor.fetchall()}

    def update_system_setting(self, key: str, value: str, changed_by: str = "Admin") -> bool:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("UPDATE system_settings SET value = ?, updated_at = CURRENT_TIMESTAMP WHERE key = ?", (value, key))
            cursor.execute(
                "INSERT INTO audit_logs (id, entity_type, entity_id, action, changed_by, old_value, new_value) VALUES (?, ?, ?, ?, ?, ?, ?)",
                (f"AUD-{str(uuid.uuid4())[:6].upper()}", "setting", key, "SETTING_CHANGED", changed_by, None, value)
            )
            conn.commit()
        return True

    # --- STATS FOR OVERVIEW & ANALYTICS ---
    def get_summary_metrics(self) -> Dict[str, Any]:
        """Calculates live KPI metrics directly from database."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) as total FROM reports")
            total_reports = cursor.fetchone()["total"]

            cursor.execute("SELECT COUNT(*) as critical FROM reports WHERE severity = 'Critical' AND status != 'Repaired' AND status != 'Verified'")
            critical_active = cursor.fetchone()["critical"]

            cursor.execute("SELECT COUNT(*) as inspecting FROM reports WHERE status = 'Under Inspection'")
            under_inspection = cursor.fetchone()["inspecting"]

            cursor.execute("SELECT COUNT(*) as repaired FROM reports WHERE status IN ('Repaired', 'Verified')")
            repaired_count = cursor.fetchone()["repaired"]

            cursor.execute("SELECT AVG(priority_score) as avg_prio FROM reports")
            avg_priority = cursor.fetchone()["avg_prio"] or 0.0

            return {
                "total_reports": total_reports,
                "critical_damage": critical_active,
                "under_inspection": under_inspection,
                "completed_repairs": repaired_count,
                "average_priority": round(avg_priority, 1)
            }

# Singleton instance
db = DatabaseManager()
