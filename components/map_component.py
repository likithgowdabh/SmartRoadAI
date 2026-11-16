"""
SmartRoad AI — Apple Maps-Inspired Clean Leaflet Map Component
Renders an elegant, minimalist road intelligence map using CartoDB Positron tiles.
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
    Renders an interactive Apple-styled Leaflet map.
    Returns complete HTML/JS string ready for st.components.v1.html.
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
            "title": r.get("title"),
            "road_name": r.get("road_name"),
            "area": r.get("area"),
            "lat": float(lat),
            "lon": float(lon),
            "severity": sev,
            "priority": float(r.get("priority_score", 50.0)),
            "status": status,
            "detections": int(r.get("detection_count", 1)),
            "color": color
        })

    markers_json = json.dumps(markers_payload)

    html_code = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8" />
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" integrity="sha256-p4NxAoJBhIIN+hmNHrzRCf9tD/miZyoHS5obTRR9BMY=" crossorigin="" />
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
            }}
            /* Leaflet popup styling (Apple design) */
            .leaflet-popup-content-wrapper {{
                background: #FFFFFF;
                border-radius: 12px;
                box-shadow: 0 4px 18px rgba(0,0,0,0.12);
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
                width: 28px;
                height: 28px;
                border-radius: 50%;
                border: 2px solid #FFFFFF;
                box-shadow: 0 2px 6px rgba(0,0,0,0.25);
                transition: transform 0.15s ease;
            }}
            .sr-pin:hover {{
                transform: scale(1.15);
            }}
            .sr-badge {{
                display: inline-block;
                padding: 2px 8px;
                border-radius: 999px;
                font-size: 11px;
                font-weight: 600;
                margin-bottom: 6px;
            }}
        </style>
    </head>
    <body>
        <div id="map"></div>
        <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js" integrity="sha256-20nQCchB9co0qIjJZRGuk2/Z9VM+kNiyxNV1lvTlZBo=" crossorigin=""></script>
        <script>
            // Initialize Leaflet map with Apple-clean Positron base tiles
            const map = L.map('map', {{
                center: [{center_lat}, {center_lon}],
                zoom: {zoom},
                zoomControl: true
            }});

            // CartoDB Positron - Clean, light gray aesthetic matching Apple Maps
            L.tileLayer('https://{{s}}.basemaps.cartocdn.com/light_all/{{z}}/{{x}}/{{y}}{{r}}.png', {{
                attribution: '&copy; OpenStreetMap &copy; CARTO',
                subdomains: 'abcd',
                maxZoom: 19
            }}).addTo(map);

            const markersData = {markers_json};
            const bounds = [];

            markersData.forEach(item => {{
                // Custom Apple circle pin
                const customIcon = L.divIcon({{
                    className: 'custom-pin-container',
                    html: `<div class="sr-pin" style="background-color: ${{item.color}};">
                            <div style="width: 8px; height: 8px; background: white; border-radius: 50%;"></div>
                           </div>`,
                    iconSize: [28, 28],
                    iconAnchor: [14, 14],
                    popupAnchor: [0, -14]
                }});

                const popupHtml = `
                    <div style="min-width: 200px;">
                        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 4px;">
                            <span class="sr-badge" style="background-color: ${{item.color}}1A; color: ${{item.color}};">${{item.severity}}</span>
                            <span style="font-size: 11px; color: #86868B;">${{item.id}}</span>
                        </div>
                        <div style="font-weight: 600; font-size: 14px; color: #1D1D1F; margin-bottom: 2px;">${{item.road_name}}</div>
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
                map.fitBounds(bounds, {{ padding: [30, 30], maxZoom: 14 }});
            }}
        </script>
    </body>
    </html>
    """
    return html_code
