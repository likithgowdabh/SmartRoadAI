"""
SmartRoad AI — Authentication & Role-Based Access Control (RBAC)
Supports Citizen, Inspector, Maintenance Manager, and Administrator roles.
"""

import hashlib
import os
from typing import Dict, Any, Optional, List, Tuple
from database.db import db

ROLES = {
    "citizen": {
        "title": "Citizen",
        "description": "Report potholes, view public damage map, track status of submitted repairs.",
        "permissions": ["report_create", "report_view", "map_view"]
    },
    "inspector": {
        "title": "Road Inspector",
        "description": "Run AI model inference, verify road damage, assess severity, update inspection notes.",
        "permissions": ["report_create", "report_view", "map_view", "ai_detect", "inspection_update"]
    },
    "maintenance_manager": {
        "title": "Maintenance Manager",
        "description": "Schedule repairs, dispatch road crews, track task progress, log repair costs.",
        "permissions": ["report_create", "report_view", "map_view", "ai_detect", "inspection_update", "maintenance_manage", "task_dispatch"]
    },
    "admin": {
        "title": "System Administrator",
        "description": "Full municipal administration, priority formula tuning, user management, audit logs.",
        "permissions": ["report_create", "report_view", "map_view", "ai_detect", "inspection_update", "maintenance_manage", "task_dispatch", "admin_manage", "audit_view"]
    }
}

DEMO_ACCOUNTS = [
    {"email": "admin@smartroad.ai", "name": "Sophia Sterling", "role": "admin", "department": "City Roads Executive"},
    {"email": "manager@smartroad.ai", "name": "Marcus Vance", "role": "maintenance_manager", "department": "Asphalt Operations"},
    {"email": "inspector@smartroad.ai", "name": "Elena Rostova", "role": "inspector", "department": "Infrastructure Quality"},
    {"email": "citizen@smartroad.ai", "name": "Devon Carter", "role": "citizen", "department": "Resident"},
]

def hash_password(password: str) -> str:
    """Computes SHA-256 hash of password."""
    return hashlib.sha256(password.encode("utf-8")).hexdigest()

def verify_credentials(email: str, password: str) -> Optional[Dict[str, Any]]:
    """Validates user email and password against database."""
    user = db.get_user_by_email(email)
    if not user:
        return None
    hashed = hash_password(password)
    if user["password_hash"] == hashed:
        return {
            "id": user["id"],
            "email": user["email"],
            "full_name": user["full_name"],
            "role": user["role"],
            "department": user.get("department", "Public Works")
        }
    return None

def register_citizen(email: str, password: str, full_name: str, phone: Optional[str] = None) -> Tuple[bool, str]:
    """Registers a new citizen in the database."""
    existing = db.get_user_by_email(email)
    if existing:
        return False, "An account with this email address already exists."
    
    user_data = {
        "email": email.strip().lower(),
        "password_hash": hash_password(password),
        "full_name": full_name.strip(),
        "role": "citizen",
        "department": "Resident / Citizen",
        "phone": phone
    }
    user_id = db.create_user(user_data)
    return True, user_id

def has_permission(user: Optional[Dict[str, Any]], permission: str) -> bool:
    """Checks if active user has specific capability."""
    if not user:
        return False
    role = user.get("role", "citizen")
    role_info = ROLES.get(role, {})
    return permission in role_info.get("permissions", [])
