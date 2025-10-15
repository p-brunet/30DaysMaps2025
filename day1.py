import folium
from folium.plugins import MarkerCluster
import geopandas as gpd

from constants import DATA_PATH, OUTPUT_DIR

# Params
day = "1"

api_jawg = DATA_PATH / "API_jawg.txt"  

try:
    with open(api_jawg, 'r') as file:
        JAWG_TOKEN = file.readline()
except FileNotFoundError:
    print(f"Error: The file '{api_jawg}' was not found.")
    

# Load cafés
cafes = gpd.read_file(DATA_PATH / "cafe_montreal.geojson")
cafes = cafes[
    (cafes.geometry.y.between(44, 46)) &
    (cafes.geometry.x.between(-75, -72))
].copy()
cafes["name"] = cafes["name"].fillna("Café sans nom")

# Create base map
m = folium.Map(
    location=[45.5017, -73.5673],
    zoom_start=13,
    min_zoom=11,  
    max_zoom=18,
    tiles="https://cartodb-basemaps-a.global.ssl.fastly.net/light_nolabels/{z}/{x}/{y}.png",
    attr="© OpenStreetMap, © CartoDB",

)

# Add bean markers
icon_path = DATA_PATH/"coffee.png"

for _, row in cafes.iterrows():
    lat, lon = row.geometry.y, row.geometry.x
    name = row["name"]
    icon = folium.CustomIcon(str(icon_path), icon_size=(8, 8), icon_anchor=(10, 10))
    folium.Marker(
        location=[lat, lon],
        popup=f"<b>{name}</b>",
        icon=icon
    ).add_to(m)

# Fit to bounds
bounds = cafes.total_bounds
m.fit_bounds([[bounds[1], bounds[0]], [bounds[3], bounds[2]]])
m.options['maxBounds'] = [[bounds[1], bounds[0]], [bounds[3], bounds[2]]]

# Add layer control
folium.LayerControl().add_to(m)

# Save
output_dir = OUTPUT_DIR / f"day_{day}"
output_dir.mkdir(parents=True, exist_ok=True)
m.save(output_dir / "montreal_cafes.html")


