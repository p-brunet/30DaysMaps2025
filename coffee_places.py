import folium
import geopandas as gpd
from constants import DATA_PATH, OUTPUT_DIR

# Params
day = "1"

# Load cafés
cafes = gpd.read_file(DATA_PATH / "cafe_montreal.geojson")
cafes = cafes[
    (cafes.geometry.y.between(44, 46)) &
    (cafes.geometry.x.between(-75, -72))
].copy()
cafes["name"] = cafes["name"].fillna("Café sans nom")

# Create the map
m = folium.Map(
    location=[45.5017, -73.5673],
    zoom_start=13,
    min_zoom=11,
    max_zoom=18,
    tiles="https://cartodb-basemaps-a.global.ssl.fastly.net/light_all//{z}/{x}/{y}.png",
    attr="© OpenStreetMap, © CartoDB",
)

icon_path = DATA_PATH / "coffee.png"

# Add beans
for _, row in cafes.iterrows():
    lat, lon = row.geometry.y, row.geometry.x
    name = row["name"]

    icon = folium.CustomIcon(str(icon_path), icon_size=(10, 10), icon_anchor=(5, 5))
    marker = folium.Marker(
        location=[lat, lon],
        popup=f"<b>{name}</b>",
        icon=icon
    )
    marker.add_to(m)

# Add legend
legend_html = f"""
<div id='legend' style="
    position: fixed; 
    bottom: 100px; left: 100px; 
    background-color: white; 
    border: 2px solid lightgray; 
    border-radius: 10px; 
    padding: 8px 12px; 
    box-shadow: 2px 2px 6px rgba(0,0,0,0.3);
    font-size: 14px;
    z-index: 9999;
">
    <img src='{icon_path.as_posix()}' style="width:10px; height:10px; vertical-align:left; margin-right:6px;">
    <b>Coffee Place</b>
</div>
"""
m.get_root().html.add_child(folium.Element(legend_html))

bounds = cafes.total_bounds
m.fit_bounds([[bounds[1], bounds[0]], [bounds[3], bounds[2]]])
m.options['maxBounds'] = [[bounds[1], bounds[0]], [bounds[3], bounds[2]]]

# Control layers
folium.LayerControl().add_to(m)

# Save
output_dir = OUTPUT_DIR / f"day_{day}"
output_dir.mkdir(parents=True, exist_ok=True)
m.save(output_dir / "montreal_cafes.html")

print(f"Map saved : {output_dir / 'montreal_cafes.html'}")
