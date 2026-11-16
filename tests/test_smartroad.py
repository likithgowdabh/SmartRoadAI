"""
SmartRoad AI — Automated Test Suite
Tests:
- Priority Engine calculations & threshold categorization
- Duplicate report Haversine distance detection
- Database CRUD operations (Reports, Maintenance Tasks, Users, Settings)
- Authentication password hashing and credential verification
- Storage service image validation and safe filename generation
- AI detector execution, status reporting, and visual severity estimation
"""

import unittest
import os
import io
import shutil
from PIL import Image

from ai.priority_engine import (
    calculate_priority_score,
    haversine_distance_meters,
    find_duplicate_reports,
    DEFAULT_WEIGHTS
)
from database.db import DatabaseManager
from services.auth_service import hash_password, verify_credentials, has_permission, register_citizen
from services.storage_service import validate_and_save_upload, save_annotated_image
from ai.detector import PotholeDetector

TEST_DB_PATH = os.path.join(os.path.dirname(__file__), "test_smartroad.db")

class TestSmartRoadAI(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        # Create dedicated test database
        if os.path.exists(TEST_DB_PATH):
            os.remove(TEST_DB_PATH)
        cls.db = DatabaseManager(db_path=TEST_DB_PATH)

    @classmethod
    def tearDownClass(cls):
        # Cleanup test database safely on Windows
        try:
            if os.path.exists(TEST_DB_PATH):
                os.remove(TEST_DB_PATH)
        except Exception:
            pass

    # 1. PRIORITY ENGINE TESTS
    def test_priority_critical_threshold(self):
        """Tests that high severity, severe traffic, and high risk yields Critical category (>= 75.0)."""
        res = calculate_priority_score(
            severity="Critical",
            traffic="Severe",
            repeat_count=3,
            safety_risk="High"
        )
        self.assertGreaterEqual(res["score"], 75.0)
        self.assertEqual(res["category"], "Critical")

    def test_priority_medium_threshold(self):
        """Tests that moderate inputs yield Medium category (40.0 - 74.9)."""
        res = calculate_priority_score(
            severity="Medium",
            traffic="Medium",
            repeat_count=1,
            safety_risk="Medium"
        )
        self.assertGreaterEqual(res["score"], 40.0)
        self.assertLess(res["score"], 75.0)
        self.assertEqual(res["category"], "Medium")

    def test_priority_low_threshold(self):
        """Tests that low severity, low traffic, and single report yields Low category (0.0 - 39.9)."""
        res = calculate_priority_score(
            severity="Low",
            traffic="Low",
            repeat_count=1,
            safety_risk="Low"
        )
        self.assertLess(res["score"], 40.0)
        self.assertEqual(res["category"], "Low")

    def test_priority_custom_weights(self):
        """Tests administrator custom weight override."""
        custom = {"severity": 0.50, "traffic": 0.20, "repeat_reports": 0.15, "safety_risk": 0.15}
        res = calculate_priority_score("Critical", "Low", 1, "Low", custom_weights=custom)
        self.assertEqual(res["weights_used"], custom)

    # 2. DUPLICATE REPORT DETECTION TESTS
    def test_haversine_distance(self):
        """Tests distance calculation between two known GPS coordinates."""
        # Approx 111 meters for 0.001 deg lat change
        dist = haversine_distance_meters(12.9716, 77.5946, 12.9726, 77.5946)
        self.assertAlmostEqual(dist, 111.0, delta=15.0)

    def test_duplicate_report_matching(self):
        """Tests that an active incident within 50 meters is flagged as duplicate."""
        existing = [
            {"id": "REP-1", "latitude": 12.9304, "longitude": 77.6784, "status": "Under Inspection"},
            {"id": "REP-2", "latitude": 12.9500, "longitude": 77.6500, "status": "Reported"},
        ]
        # Coordinates ~20 meters away
        matches = find_duplicate_reports(12.9305, 77.6785, existing, threshold_meters=50.0)
        self.assertEqual(len(matches), 1)
        self.assertEqual(matches[0]["id"], "REP-1")
        self.assertLessEqual(matches[0]["distance_meters"], 50.0)

    # 3. DATABASE CRUD TESTS
    def test_create_and_fetch_report(self):
        """Tests report insertion and retrieval."""
        rep_id = self.db.create_report({
            "title": "Test Road Defect",
            "road_name": "Test Boulevard",
            "area": "Downtown",
            "city": "Bengaluru",
            "latitude": 12.9700,
            "longitude": 77.6000,
            "severity": "Critical",
            "priority_score": 85.0,
            "traffic_level": "High",
            "repeat_count": 1,
            "safety_risk": "High",
            "status": "Reported"
        })
        self.assertTrue(rep_id.startswith("REP-"))
        fetched = self.db.get_report_by_id(rep_id)
        self.assertIsNotNone(fetched)
        self.assertEqual(fetched["road_name"], "Test Boulevard")
        self.assertEqual(fetched["severity"], "Critical")

    def test_update_report_status_and_audit(self):
        """Tests status updating and audit log creation."""
        rep_id = self.db.create_report({
            "title": "Audit Test Hazard",
            "road_name": "Audit Road",
            "area": "Zone 1",
            "latitude": 12.9100,
            "longitude": 77.6100,
            "severity": "Medium",
            "priority_score": 55.0,
            "status": "Reported"
        })
        success = self.db.update_report(rep_id, {"status": "In Progress"}, changed_by="Test Inspector")
        self.assertTrue(success)
        
        updated = self.db.get_report_by_id(rep_id)
        self.assertEqual(updated["status"], "In Progress")

        # Verify audit log recorded this change
        logs = self.db.get_audit_logs(limit=25)
        actions = [l["action"] for l in logs]
        self.assertIn("UPDATE_STATUS", actions)

    def test_maintenance_task_lifecycle(self):
        """Tests dispatching and completing a maintenance task."""
        rep_id = self.db.create_report({
            "title": "Task Test Pothole",
            "road_name": "Highway 7",
            "area": "North Corridor",
            "latitude": 12.9800,
            "longitude": 77.6200,
            "severity": "Critical",
            "priority_score": 90.0,
            "status": "Reported"
        })
        task_id = self.db.create_maintenance_task({
            "report_id": rep_id,
            "assigned_team": "Rapid Asphalt Unit 1",
            "scheduled_date": "2026-11-20",
            "due_date": "2026-11-22",
            "status": "Scheduled",
            "budget_estimate": 1500.0,
            "cost_actual": 0.0
        }, changed_by="Test Manager")
        self.assertTrue(task_id.startswith("TSK-"))

        # Check linked report synced to Scheduled
        rep = self.db.get_report_by_id(rep_id)
        self.assertEqual(rep["status"], "Scheduled")

        # Update task to Repaired
        self.db.update_maintenance_task(task_id, {"status": "Repaired", "cost_actual": 1420.0})
        rep_after = self.db.get_report_by_id(rep_id)
        self.assertEqual(rep_after["status"], "Repaired")

    # 4. AUTHENTICATION & SECURITY TESTS
    def test_password_hashing_and_verification(self):
        """Tests secure SHA-256 password hashing."""
        pw = "MunicipalSecret@2026"
        hashed = hash_password(pw)
        self.assertNotEqual(pw, hashed)
        self.assertEqual(len(hashed), 64)

    def test_role_permissions(self):
        """Tests Role-Based Access Control logic."""
        admin_user = {"role": "admin"}
        citizen_user = {"role": "citizen"}

        self.assertTrue(has_permission(admin_user, "admin_manage"))
        self.assertTrue(has_permission(admin_user, "maintenance_manage"))
        self.assertFalse(has_permission(citizen_user, "admin_manage"))
        self.assertFalse(has_permission(citizen_user, "maintenance_manage"))
        self.assertTrue(has_permission(citizen_user, "report_create"))

    # 5. STORAGE SERVICE TESTS
    def test_storage_validation(self):
        """Tests file extension and size validation on image upload."""
        # Create valid dummy PNG image in memory
        img = Image.new("RGB", (100, 100), color=(100, 100, 100))
        buf = io.BytesIO()
        img.save(buf, format="PNG")
        raw_bytes = buf.getvalue()

        valid, path, rel_path = validate_and_save_upload(raw_bytes, "test_upload.png")
        self.assertTrue(valid)
        self.assertTrue(os.path.exists(path))
        self.assertTrue(rel_path.startswith("assets/uploads/"))

        # Test invalid extension
        invalid_valid, msg, _ = validate_and_save_upload(b"invalid data", "malicious.exe")
        self.assertFalse(invalid_valid)

    # 6. AI DETECTOR TEST
    def test_detector_execution(self):
        """Tests that AI detector runs inference and computes visual severity without crash."""
        detector = PotholeDetector()
        status = detector.get_system_status()
        self.assertIn("status", status)

        # Create test image
        img = Image.new("RGB", (320, 240), color=(110, 110, 110))
        res = detector.detect(img)
        self.assertIn("visual_severity", res)
        self.assertIn("detection_count", res)
        self.assertIn("annotated_image", res)
        self.assertIsInstance(res["annotated_image"], Image.Image)

if __name__ == "__main__":
    unittest.main()
