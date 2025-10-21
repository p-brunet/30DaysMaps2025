"""
Parse IESO KML and display on Folium map
"""

import json
from xml.etree import ElementTree as ET

from constants import DATA_PATH

def parse_kml(kml_file):
    """Parse KML and extract polygons"""
    
    print(f"Parsing: {kml_file}")
    
    tree = ET.parse(kml_file)
    root = tree.getroot()
    
    # KML namespace
    ns = {'kml': 'http://www.opengis.net/kml/2.2'}
    
    # Find all placemarks
    placemarks = root.findall('.//kml:Placemark', ns)
    
    print(f"Found {len(placemarks)} zones")
    
    zones = []
    
    for pm in placemarks:
        # Get zone name
        name_elem = pm.find('.//kml:name', ns)
        name = name_elem.text if name_elem is not None else "Unknown"
        
        # Get description
        desc_elem = pm.find('.//kml:description', ns)
        desc = desc_elem.text if desc_elem is not None else ""
        
        # Get coordinates
        coords_elem = pm.find('.//kml:coordinates', ns)
        
        if coords_elem is not None:
            coord_text = coords_elem.text.strip()
            
            # Parse coordinates (format: lng,lat,alt)
            points = []
            for coord in coord_text.split():
                parts = coord.split(',')
                if len(parts) >= 2:
                    lng = float(parts[0])
                    lat = float(parts[1])
                    points.append([lng, lat])
            
            zones.append({
                'name': name,
                'description': desc,
                'coordinates': points
            })
            
            print(f"  {name}: {len(points)} points")
    
    return zones

def zones_to_geojson(zones):
    """Convert zones to GeoJSON"""
    
    geojson = {
        "type": "FeatureCollection",
        "features": []
    }
    
    for zone in zones:
        # Close polygon if needed
        coords = zone['coordinates']
        if coords[0] != coords[-1]:
            coords.append(coords[0])
        
        feature = {
            "type": "Feature",
            "properties": {
                "name": zone['name'],
                "description": zone['description'],
                "num_points": len(coords)
            },
            "geometry": {
                "type": "Polygon",
                "coordinates": [coords]
            }
        }
        
        geojson['features'].append(feature)
    
    return geojson

def create_folium_map(zones):
    """Create Folium map with zones"""
    
    try:
        import folium
    except ImportError:
        print("Installing folium...")
        import subprocess
        import sys
        subprocess.check_call([sys.executable, "-m", "pip", "install", "folium"])
        import folium
    
    # Center on Ontario
    ontario_center = [45.5, -80.0]
    
    m = folium.Map(
        location=ontario_center,
        zoom_start=6,
        tiles='OpenStreetMap'
    )
    
    # Color palette for zones
    colors = [
        '#3F5BA9', '#F8971B', '#7C3592', '#62AF44', '#A61B4A',
        '#0BA9CC', '#7CCFA9', '#DB4436', '#F4EB37', '#1B97F8'
    ]
    
    for idx, zone in enumerate(zones):
        color = colors[idx % len(colors)]
        
        # Convert coordinates for Folium (needs [lat, lng])
        folium_coords = [[lat, lng] for lng, lat in zone['coordinates']]
        
        # Create popup content
        popup_html = f"""
        <b>{zone['name']}</b><br>
        <i>{zone['description'][:100]}...</i><br>
        Points: {len(zone['coordinates'])}
        """
        
        # Add polygon
        folium.Polygon(
            locations=folium_coords,
            color=color,
            weight=2,
            fill=True,
            fill_color=color,
            fill_opacity=0.3,
            popup=folium.Popup(popup_html, max_width=300),
            tooltip=zone['name']
        ).add_to(m)
        
        # Add zone label at center
        if len(zone['coordinates']) > 0:
            # Calculate centroid
            lats = [lat for lng, lat in zone['coordinates']]
            lngs = [lng for lng, lat in zone['coordinates']]
            center_lat = sum(lats) / len(lats)
            center_lng = sum(lngs) / len(lngs)
            
            folium.Marker(
                [center_lat, center_lng],
                icon=folium.DivIcon(html=f"""
                    <div style="font-size: 10pt; color: {color}; font-weight: bold;">
                        {zone['name']}
                    </div>
                """)
            ).add_to(m)
    
    return m

def main():
    print("="*60)
    print("IESO ZONES - KML TO FOLIUM MAP")
    print("="*60)
    
    kml_file = 'doc.kml'
    
    # Parse KML
    zones = parse_kml(DATA_PATH / kml_file)
    
    if not zones:
        print("No zones found!")
        return
    
    # Save as GeoJSON
    geojson = zones_to_geojson(zones)
    
    with open('ieso_zones.geojson', 'w') as f:
        json.dump(geojson, f, indent=2)
    
    print(f"\n✓ GeoJSON saved: ieso_zones.geojson")
    print(f"  {len(geojson['features'])} zones")
    
    # Create Folium map
    print("\nCreating Folium map...")
    m = create_folium_map(zones)
    
    # Save map
    m.save('ieso_zones_map.html')
    
    print("✓ Map saved: ieso_zones_map.html")
    print("\nOpen ieso_zones_map.html in your browser to view the map!")
    
    # Print zone summary
    print("\n" + "="*60)
    print("ZONE SUMMARY")
    print("="*60)
    for zone in zones:
        print(f"\n{zone['name']}:")
        print(f"  Points: {len(zone['coordinates'])}")
        print(f"  Description: {zone['description'][:80]}...")

if __name__ == "__main__":
    main()