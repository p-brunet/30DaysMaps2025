import folium
import gpxpy

from constants import DATA_PATH, OUTPUT_DIR

# Params
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
day = 2

# Color per sport
SPORT_COLORS = {
    "cycling": "#5972E4",
    "running": "#07B021"
}

# Totals
totals = {"cycling": 0, "running": 0}

# Create map
m = folium.Map(
    location=[45.5017, -73.5673],
    zoom_start=12,
    tiles="https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}.png",
    attr="© OpenStreetMap, © CartoDB",
)


fg_running = folium.FeatureGroup(name="Running", show=True)
fg_cycling = folium.FeatureGroup(name="Cycling", show=True)
m.add_child(fg_running)
m.add_child(fg_cycling)

# Load traces
for gpx_file in DATA_PATH.glob("*.gpx"):
    with open(gpx_file, 'r') as f:
        gpx = gpxpy.parse(f)

    sport_type = None
    for track in gpx.tracks:
        if hasattr(track, 'type') and track.type:
            sport_type = track.type.lower()
        elif hasattr(track, 'extensions') and 'type' in track.extensions:
            sport_type = track.extensions['type'].lower()

    if sport_type not in SPORT_COLORS:
        continue

    points = []
    for track in gpx.tracks:
        for segment in track.segments:
            for point in segment.points:
                points.append((point.latitude, point.longitude))
            # Compute length
            segment_length = segment.length_3d()
            totals[sport_type] += segment_length

    # Add lines
    folium.PolyLine(
        points,
        color=SPORT_COLORS[sport_type],
        weight=3,
        opacity=0.8,
        popup=folium.Popup(f"{sport_type.capitalize()}: {segment_length/1000:.2f} km", max_width=200)
    ).add_to(fg_cycling if sport_type == "cycling" else fg_running)

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
    <b>Totals per Activity</b><br>
    <i style='background:{SPORT_COLORS["cycling"]}; width:30px; height:3px; display:inline-block; margin:2px 5px;'></i> Biking: {totals["cycling"]/1000:.2f} km<br>
    <i style='background:{SPORT_COLORS["running"]}; width:30px; height:3px; display:inline-block; margin:2px 5px;'></i> Running : {totals["running"]/1000:.2f} km<br>
</div>
"""
m.get_root().html.add_child(folium.Element(legend_html))
folium.LayerControl().add_to(m)

# Save map
m.save(OUTPUT_DIR / f"day_{day}" / "summer_strava_activity.html")

print(f"Map save : {OUTPUT_DIR / "day_{day}" / "summer_strava_activity.html"}")
print(f"Totals : Cycling = {totals['cycling']/1000:.2f} km, Running = {totals['running']/1000:.2f} km")
