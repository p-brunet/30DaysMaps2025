import requests
import folium
from folium.plugins import MarkerCluster

from constants import OUTPUT_DIR


def parse_geojson(url: str) -> dict:
    """Retrieve GeoJSON data from URL"""
    response = requests.get(url)
    response.raise_for_status()
    return response.json()
  

def create_map(geojson_data: dict, use_cluster: bool = True) -> folium.Map:
    """Create Folium map with charging stations"""
    features = geojson_data.get('features', [])
    
    # Center of Montréal
    m = folium.Map(location=[45.5017, -73.5673], 
                   zoom_start=12,
                   tiles="https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}.png",
                   attr="© OpenStreetMap, © CartoDB")
    container = MarkerCluster().add_to(m) if use_cluster else m
    
    for feature in geojson_data['features']:
        props = feature['properties']
        lon, lat = feature['geometry']['coordinates']
        
        popup = f"""
        <b>{props['NOM_BORNE_RECHARGE']}</b><br>
        {props['ADRESSE']}<br>
        {props['NIVEAU_RECHARGE']} - {props['MODE_TARIFICATION']}<br>
        <i>{props.get('TYPE_EMPLACEMENT', 'N/A')}</i>
        """
        
        if use_cluster:
            folium.Marker(
                location=[lat, lon],
                popup=folium.Popup(popup, max_width=300),
                icon=folium.Icon(color='green', icon='plug', prefix='fa')
            ).add_to(container)
        else:
            folium.CircleMarker(
                location=[lat, lon],
                radius=4,
                popup=folium.Popup(popup, max_width=300),
                color='green',
                fill=True,
                fillColor='green',
                fillOpacity=0.6,
                opacity=.8,
            ).add_to(container)
    # Legend
    legend_html = f"""
    <div id='legend' style="
        position: fixed;
        bottom: 50px; left: 50px;
        background-color: white;
        border: 2px solid lightgray;
        border-radius: 10px;
        padding: 8px 12px;
        box-shadow: 2px 2px 6px rgba(0,0,0,0.3);
        font-size: 14px;
        z-index: 9999;
    ">
        <b>Total of Charging Points : {len(geojson_data['features'])}</b>
        <p style="margin: 0;"><span style="color: green; font-size: 25px">●</span> Charging Station</p>
    </div>
    """
    container.get_root().html.add_child(folium.Element(legend_html))
    folium.LayerControl().add_to(container)
    
    return m

if __name__ == "__main__":
    url="https://montreal-prod.storage.googleapis.com/resources/b502cee9-ff87-44fa-9a8e-722285202b0d/bornes-recharge-publiques.geojson?X-Goog-Algorithm=GOOG4-RSA-SHA256&X-Goog-Credential=test-datapusher-delete%40amplus-data.iam.gserviceaccount.com%2F20251027%2Fauto%2Fstorage%2Fgoog4_request&X-Goog-Date=20251027T223944Z&X-Goog-Expires=604800&X-Goog-SignedHeaders=host&x-goog-signature=9213dfa0f62f36d4d5d45ab27b950b4c37ce8f9bdc275aad8e1fa8b9bc01443ea9dd8e3082dec888dc3a7e5ded0e6edcb30cdff492901e3852cf07b2fc50a79a6a65b390974d69d6d0364e211f6597839b10054fed919ad19f4fa5a0c3b7f994134f64d3e21789fd7c767c43b05d0330b3ad5a5f14d54e0e3d636cebed76c560b6fc10a5081a91d230fb8e9f7f196c8e3b4e85a2b3a6e0961fdc32fcea6a556346200fc88ca3031e7b42ac67824d3dcb2f4e5cf4f08bf642d830041babdfd9ffb72973fa91bef13567f5fd8ccc126ffcb6be0811bd80aadffe730d4b402c84aaca8b8d5dfb25b6b59c899f728a0e8cd926afd7aabf377f49a4d1ae1aea5e19bc"  
    day = 1
    geojson_data = parse_geojson(url)
    map = create_map(geojson_data, use_cluster=False)
    map.save(OUTPUT_DIR / f"day_{day}" / "charging_points_no_cluster.html")
  