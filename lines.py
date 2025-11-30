from constants import DATA_PATH, OUTPUT_DIR
import folium
import geopandas as gpd
from shapely.geometry import MultiLineString, LineString, mapping
from pyproj import Geod

geod = Geod(ellps="WGS84")

def geodesic_length_meters(geom):
    total_m = 0.0

    if isinstance(geom, LineString):
        lines = [geom]
    elif isinstance(geom, MultiLineString):
        lines = list(geom.geoms)
    else:
        raise TypeError(f"Expected LineString or MultiLineString, got {geom.geom_type}")

    for line in lines:
        coords = list(line.coords)
        if len(coords) < 2:
            continue
        # sommation des distances entre points consécutifs
        for (lon1, lat1), (lon2, lat2) in zip(coords[:-1], coords[1:]):
            # geod.inv renvoie (az12, az21, distance)
            _, _, dist = geod.inv(lon1, lat1, lon2, lat2)
            total_m += dist

    return total_m

def create_line_map(gdf, filename):
    """
    Create and save an interactive folium map with a basemap no label
    """
   
    geom = gdf.iloc[0].geometry

    lines = []
    if isinstance(geom, MultiLineString):
        lines = list(geom.geoms)
    elif isinstance(geom, LineString):
        lines = [geom]
    else:
        raise TypeError(f"Expected LineString or MultiLineString, got {geom.geom_type}")
    
    sublines = list(geom.geoms) if isinstance(geom, MultiLineString) else [geom]
    
    # Compute proj
    segment_lengths = [geodesic_length_meters(line) for line in sublines]
    total_m = sum(segment_lengths)
    total_km = total_m/ 1000.0
    total_miles = total_km * 0.621371

    # Create dark basemap
    tiles_url = 'https://{s}.basemaps.cartocdn.com/dark_nolabels/{z}/{x}/{y}{r}.png'
    m = folium.Map(zoom_start=7, tiles=tiles_url, attr='© OpenStreetMap © CartoDB')

    line_name = "HVDC Interconnection Line Radisson Qc - Sandy Pond Ma - 450 kV"

    # Add segment
    for idx, line in enumerate(sublines, start=1):
        seg_km = segment_lengths[idx - 1] / 1000
        seg_miles = seg_km * 0.621371

        tooltip_text = (
            f"<b>Segment {idx}</b><br>"
            f"{line_name}<br>"
            f"Length: {seg_km:,.1f} km ({seg_miles:,.1f} mi)"
        )

        feature = {
            'type': 'Feature',
            'geometry': mapping(line),
            'properties': {k: v for k, v in gdf.iloc[0].items() if k != 'geometry'}
        }
        folium.GeoJson(
            data= feature,
            style_function=lambda x: {
                'color': "#ffff00",
                'weight': 4,
                'opacity': 0.9
            },
            tooltip=folium.Tooltip(tooltip_text, sticky=True)
        ).add_to(m)

    
    m.fit_bounds([
        [geom.bounds[1], geom.bounds[0]],  # south-west
        [geom.bounds[3], geom.bounds[2]]   # north-east
    ])

    name = gdf.iloc[0].get('id', 'Line Feature')
    title_html = f'<h3 align="center" style="font-size:16px"><b>{name}</b></h3>'
    m.get_root().html.add_child(folium.Element(title_html)) 
    legend_html = f'''
    <div style="
        position: fixed;
        bottom: 40px; left: 40px; width: 300px;
        background-color: rgba(0,0,0,0.7);
        color: white;
        padding: 10px;
        font-size: 14px;
        border-radius: 8px;
        z-index:9999;
    ">
      <b>HDVC Radisson Qc - Sandy Pond Ma</b><br>
      Total Length: {total_km:.1f} km ({total_miles:.1f} miles)<br>
    </div>
    '''
   
    m.get_root().html.add_child(folium.Element(legend_html))

    m.save(filename)
   


if __name__ == '__main__':
    day = 27
    output_dir = OUTPUT_DIR / f'day_{day}'
    output_dir.mkdir(parents=True, exist_ok=True)
    
    geojson_line = gpd.read_file(DATA_PATH / 'radisson_line.geojson')
    filename = output_dir / "radisson_line.html"
    
    create_line_map(geojson_line, filename)

    