"""
SmartRoad AI — Export & Reporting Service
Exports municipal data to CSV and JSON formats.
"""

import io
import csv
import json
from typing import List, Dict, Any

def export_reports_to_csv(reports: List[Dict[str, Any]]) -> str:
    """Serializes reports list to standard CSV string."""
    if not reports:
        return ""
    
    output = io.StringIO()
    fields = [
        "id", "title", "road_name", "area", "city", "latitude", "longitude",
        "severity", "priority_score", "traffic_level", "repeat_count",
        "safety_risk", "status", "detection_count", "assigned_to", "created_at"
    ]
    
    writer = csv.DictWriter(output, fieldnames=fields, extrasaction="ignore")
    writer.writeheader()
    for r in reports:
        writer.writerow(r)
        
    return output.getvalue()

def export_reports_to_json(reports: List[Dict[str, Any]]) -> str:
    """Serializes reports list to formatted JSON string."""
    return json.dumps(reports, indent=2, default=str)
