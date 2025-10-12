import folium
import geopandas as gpd


from constants import DATA_PATH, OUTPUT_DIR

# Params
day="1"


# Load cafe locations
cafes = gpd.read_file(DATA_PATH /"cafe_montreal.geojson")

# Clean the json with bounding box over Montreal
cafes_clean = cafes[
    (cafes.geometry.y.between(44, 46)) &
    (cafes.geometry.x.between(-75, -72))
].copy()

# Create the map
m = folium.Map(
    location=[45.5017, -73.5673],
    zoom_start=12,
    tiles="cartodbpositron", 
    attr='© OpenStreetMap contributors, © CartoDB'
)

# Add cafes as points
for idx, row in cafes_clean.iterrows():
    name = row.get("name", "Café")
    lat = row.geometry.y
    lon = row.geometry.x
    folium.CircleMarker(
        location=[lat, lon],
        radius=3,
        color="#6F4E37",
        fill=True,
        fill_color="#6F4E37",
        fill_opacity=0.7,
        popup=f"<b>{name}</b>",
        weight=0 
    ).add_to(m)

# Unable settings
m.fit_bounds(m.get_bounds(), padding=(20, 20))
m.options["zoomControl"] = False
m.options["attributionControl"] = False

# Save the map
output_dir = OUTPUT_DIR / f"day_{day}"
output_dir.mkdir(parents=True, exist_ok=True)

output_file = output_dir / "montreal_cafes.html"
m.save(outfile=output_file)

