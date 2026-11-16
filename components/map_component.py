"""
SmartRoad AI — Zero-API-Key Apple Maps-Inspired Leaflet Map Component
Uses 100% free, public tile providers (OpenStreetMap & Esri Gray Canvas)
that require ZERO API keys or tokens.
"""

import json
from typing import List, Dict, Any

def render_apple_road_map(
    reports: List[Dict[str, Any]],
    center_lat: float = 12.9450,
    center_lon: float = 77.6250,
    zoom: int = 12,
    height: int = 540
) -> str:
    """
    Renders an interactive Apple-styled Leaflet map without requiring any API keys.
    Uses OpenStreetMap and Esri Light Gray tiles with layer switching.
    """
    # Color mapping following Apple palette
    color_map = {
        "Critical": "#D70015",
        "Medium": "#B87900",
        "Low": "#248A3D",
        "Repaired": "#0071E3",
        "Verified": "#0071E3"
    }

    # Prepare marker payload
    markers_payload = []
    for r in reports:
        lat = r.get("latitude")
        lon = r.get("longitude")
        if lat is None or lon is None:
            continue
            
        sev = r.get("severity", "Medium")
        status = r.get("status", "Reported")
        color = color_map.get("Repaired" if status in ["Repaired", "Verified"] else sev, "#6E6E73")
        
        markers_payload.append({
            "id": r.get("id"),
            "title": r.get("title") or f"{sev} Hazard",
            "road_name": r.get("road_name") or "Municipal Road",
            "area": r.get("area") or "Metro Ward",
            "lat": float(lat),
            "lon": float(lon),
            "severity": sev,
            "priority": float(r.get("priority_score", 50.0)),
            "status": status,
            "detections": int(r.get("detection_count", 1)),
            "color": color
        })

    markers_json = json.dumps(markers_payload)

    html_code = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/leaflet.min.css" />
    <style>
        body, html {{
            margin: 0;
            padding: 0;
            height: 100%;
            width: 100%;
            font-family: -apple-system, BlinkMacSystemFont, "SF Pro Text", "Inter", sans-serif;
            background-color: #F5F5F7;
        }}
        #map {{
            height: {height}px;
            width: 100%;
            border-radius: 12px;
            border: 1px solid #D2D2D7;
            background: #F5F5F7;
        }}
        /* Leaflet popup styling (Apple design) */
        .leaflet-popup-content-wrapper {{
            background: #FFFFFF;
            border-radius: 12px;
            box-shadow: 0 8px 24px rgba(0,0,0,0.12);
            border: 1px solid #E5E5EA;
            padding: 4px;
        }}
        .leaflet-popup-content {{
            margin: 10px 14px;
            line-height: 1.4;
        }}
        .leaflet-popup-tip {{
            background: #FFFFFF;
        }}
        .sr-pin {{
            display: flex;
            align-items: center;
            justify-content: center;
            width: 26px;
            height: 26px;
            border-radius: 50%;
            border: 2px solid #FFFFFF;
            box-shadow: 0 3px 8px rgba(0,0,0,0.3);
            transition: transform 0.2s cubic-bezier(0.16, 1, 0.3, 1);
            cursor: pointer;
        }}
        .sr-pin:hover {{
            transform: scale(1.22);
            box-shadow: 0 6px 14px rgba(0,0,0,0.35);
        }}
        .sr-badge {{
            display: inline-block;
            padding: 2px 8px;
            border-radius: 999px;
            font-size: 11px;
            font-weight: 600;
            margin-bottom: 6px;
        }}
        /* Layer switcher Apple style */
        .leaflet-control-layers {{
            border-radius: 10px !important;
            border: 1px solid #D2D2D7 !important;
            box-shadow: 0 2px 10px rgba(0,0,0,0.08) !important;
            font-size: 12.5px !important;
            padding: 6px 10px !important;
            background: rgba(255, 255, 255, 0.95) !important;
            backdrop-filter: blur(10px);
        }}
    </style>
</head>
<body>
    <div id="map"></div>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/leaflet.min.js"></script>
    <script>
        // Initialize Map
        const map = L.map('map', {{
            center: [{center_lat}, {center_lon}],
            zoom: {zoom},
            zoomControl: true,
            attributionControl: true
        }});

        // Layer 1: OpenStreetMap Standard (100% Free, Zero API Key Required)
        const osmLayer = L.tileLayer('https://tile.openstreetmap.org/{{z}}/{{x}}/{{y}}.png', {{
            maxZoom: 19,
            attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
        }});

        // Layer 2: Esri World Gray Canvas (Apple-like Minimal Light Gray, Zero API Key)
        const esriGray = L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/Canvas/World_Light_Gray_Base/MapServer/tile/{{z}}/{{y}}/{{x}}', {{
            maxZoom: 16,
            attribution: 'Tiles &copy; Esri &mdash; Esri, DeLorme, NAVTEQ'
        }});

        // Layer 3: Esri World Imagery (Satellite, Zero API Key)
        const satellite = L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{{z}}/{{y}}/{{x}}', {{
            maxZoom: 18,
            attribution: 'Tiles &copy; Esri'
        }});

        // Set OpenStreetMap as the default active layer
        osmLayer.addTo(map);

        // Add Layer Control
        const baseMaps = {{
            "Street Map (OSM)": osmLayer,
            "Apple Minimal Gray": esriGray,
            "Satellite Imagery": satellite
        }};
        L.control.layers(baseMaps, null, {{ position: 'topright' }}).addTo(map);

        // Plot Markers
        const markersData = {markers_json};
        const bounds = [];

        markersData.forEach(item => {{
            const customIcon = L.divIcon({{
                className: 'custom-pin-container',
                html: `<div class="sr-pin" style="background-color: ${{item.color}};">
                        <div style="width: 8px; height: 8px; background: white; border-radius: 50%;"></div>
                       </div>`,
                iconSize: [26, 26],
                iconAnchor: [13, 13],
                popupAnchor: [0, -14]
            }});

            const popupHtml = `
                <div style="min-width: 210px;">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 4px;">
                        <span class="sr-badge" style="background-color: ${{item.color}}1F; color: ${{item.color}};">${{item.severity}}</span>
                        <span style="font-size: 11px; color: #86868B;">${{item.id}}</span>
                    </div>
                    <div style="font-weight: 700; font-size: 14px; color: #1D1D1F; margin-bottom: 2px;">${{item.road_name}}</div>
                    <div style="font-size: 12px; color: #6E6E73; margin-bottom: 8px;">${{item.area}}</div>
                    
                    <div style="display: flex; justify-content: space-between; padding-top: 6px; border-top: 1px solid #E5E5EA; font-size: 12px;">
                        <div><strong style="color: #1D1D1F;">Priority:</strong> ${{item.priority}}</div>
                        <div><strong style="color: #1D1D1F;">Status:</strong> ${{item.status}}</div>
                    </div>
                </div>
            `;

            const marker = L.marker([item.lat, item.lon], {{ icon: customIcon }}).addTo(map);
            marker.bindPopup(popupHtml);
            bounds.push([item.lat, item.lon]);
        }});

        if (bounds.length > 0) {{
            map.fitBounds(bounds, {{ padding: [35, 35], maxZoom: 14 }});
        }}

        // Invalidate size to guarantee perfect layout
        setTimeout(() => {{
            map.invalidateSize();
        }}, 200);
    </script>
</body>
</html>
"""
    return html_code
