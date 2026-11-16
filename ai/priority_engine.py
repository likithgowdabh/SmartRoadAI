"""
SmartRoad AI — Road Maintenance Priority Engine & Duplicate Detection
Formula:
    Priority = (0.40 * Severity) + (0.30 * Traffic) + (0.20 * Repeat Reports) + (0.10 * Safety Risk)

Thresholds:
    75.0 - 100.0 : Critical
    40.0 - 74.9  : Medium
    0.0  - 39.9  : Low
"""

import math
from typing import Dict, Any, Tuple, List, Optional

# Default weights (transparent empirical municipal heuristic)
DEFAULT_WEIGHTS = {
    "severity": 0.40,
    "traffic": 0.30,
    "repeat_reports": 0.20,
    "safety_risk": 0.10,
}

# Standard factor score scales (0 to 100)
SEVERITY_SCORES = {
    "Critical": 100.0,
    "High": 85.0,
    "Medium": 55.0,
    "Low": 25.0,
}

TRAFFIC_SCORES = {
    "Severe": 100.0,
    "High": 80.0,
    "Medium": 50.0,
    "Low": 20.0,
}

SAFETY_RISK_SCORES = {
    "High": 100.0,
    "Medium": 60.0,
    "Low": 25.0,
}

def calculate_priority_score(
    severity: str,
    traffic: str,
    repeat_count: int,
    safety_risk: str,
    custom_weights: Optional[Dict[str, float]] = None
) -> Dict[str, Any]:
    """
    Computes priority index based on multi-factor weighted equation.
    Returns composite score, category ('Critical', 'Medium', 'Low'), and full factor breakdown.
    """
    weights = custom_weights or DEFAULT_WEIGHTS
    
    # 1. Severity factor
    sev_val = SEVERITY_SCORES.get(severity, 50.0)
    
    # 2. Traffic factor
    traf_val = TRAFFIC_SCORES.get(traffic, 50.0)
    
    # 3. Repeat reports factor: scaled linearly up to 4+ reports = 100.0
    repeat_val = min(100.0, max(0.0, (repeat_count if repeat_count >= 1 else 1) * 25.0))
    
    # 4. Safety risk factor
    safety_val = SAFETY_RISK_SCORES.get(safety_risk, 50.0)
    
    # Calculate weighted composite
    w_sev = weights.get("severity", 0.40)
    w_traf = weights.get("traffic", 0.30)
    w_rep = weights.get("repeat_reports", 0.20)
    w_safe = weights.get("safety_risk", 0.10)
    
    raw_score = (
        (w_sev * sev_val) +
        (w_traf * traf_val) +
        (w_rep * repeat_val) +
        (w_safe * safety_val)
    )
    
    score = round(max(0.0, min(100.0, raw_score)), 1)
    
    # Determine category according to prompt specifications
    if score >= 75.0:
        category = "Critical"
    elif score >= 40.0:
        category = "Medium"
    else:
        category = "Low"
        
    return {
        "score": score,
        "category": category,
        "inputs": {
            "severity": severity,
            "traffic": traffic,
            "repeat_count": repeat_count,
            "safety_risk": safety_risk
        },
        "breakdown": {
            "severity_component": round(w_sev * sev_val, 2),
            "traffic_component": round(w_traf * traf_val, 2),
            "repeat_component": round(w_rep * repeat_val, 2),
            "safety_component": round(w_safe * safety_val, 2),
        },
        "weights_used": weights
    }

def haversine_distance_meters(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Calculates great circle distance in meters between two geographical GPS points.
    """
    R = 6371000.0  # Earth radius in meters
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)

    a = (
        math.sin(delta_phi / 2.0) ** 2 +
        math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2.0) ** 2
    )
    c = 2.0 * math.atan2(math.sqrt(a), math.sqrt(1.0 - a))
    return R * c

def find_duplicate_reports(
    latitude: float,
    longitude: float,
    existing_reports: List[Dict[str, Any]],
    threshold_meters: float = 50.0
) -> List[Dict[str, Any]]:
    """
    Identifies existing road reports within proximity threshold (e.g. 50 meters).
    Returns list of nearby matches with distance.
    """
    duplicates = []
    for report in existing_reports:
        # Only compare active/unresolved reports
        if report.get("status") in ["Repaired", "Verified", "Archived"]:
            continue
            
        r_lat = report.get("latitude")
        r_lon = report.get("longitude")
        if r_lat is not None and r_lon is not None:
            dist = haversine_distance_meters(latitude, longitude, float(r_lat), float(r_lon))
            if dist <= threshold_meters:
                dup_record = dict(report)
                dup_record["distance_meters"] = round(dist, 1)
                duplicates.append(dup_record)
                
    # Sort closest first
    duplicates.sort(key=lambda x: x["distance_meters"])
    return duplicates
