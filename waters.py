from constants import DATA_PATH, OUTPUT_DIR

import geopandas as gpd
import osmnx as ox

import matplotlib.pyplot as plt
import folium
import branca.colormap as cm

from pathlib import Path

def download_rivers_natural_earth():
    """Download rivers from Natural Earth (much faster)."""
    geojson_path = DATA_PATH / 'quebec_rivers.geojson'
    
    if geojson_path.exists():
        print(f"GeoJSON already exists at {geojson_path}")
        return geojson_path
    
    print("Downloading rivers from Natural Earth...")
    
    # Download Natural Earth rivers (10m resolution)
    url = "https://naciscdn.org/naturalearth/10m/physical/ne_10m_rivers_lake_centerlines.zip"
    
    import requests
    import zipfile
    import io
    
    response = requests.get(url)
    with zipfile.ZipFile(io.BytesIO(response.content)) as z:
        z.extractall(DATA_PATH / 'ne_rivers')
    
    # Load all rivers
    gdf_all_rivers = gpd.read_file(DATA_PATH / 'ne_rivers' / 'ne_10m_rivers_lake_centerlines.shp')
    
    # Filter for Quebec area (approximate bounding box)
    quebec_bbox = (-79.5, 44.5, -57.0, 62.5)  # (minx, miny, maxx, maxy)
    gdf_rivers = gdf_all_rivers.cx[quebec_bbox[0]:quebec_bbox[2], quebec_bbox[1]:quebec_bbox[3]]
    
    # Keep only useful columns
    cols_to_keep = ['name', 'geometry']
    cols_to_keep = [col for col in cols_to_keep if col in gdf_rivers.columns]
    gdf_rivers = gdf_rivers[cols_to_keep].reset_index(drop=True)
    
    print(f"Filtered {len(gdf_rivers)} rivers in Quebec region")
    
    # Save as GeoJSON
    gdf_rivers.to_file(geojson_path, driver='GeoJSON')
    print(f"Saved to {geojson_path}")
    
    return geojson_path

def download_rivers_canvec():
    """Download detailed rivers from CanVec (Natural Resources Canada)."""
    geojson_path = DATA_PATH / 'quebec_rivers.geojson'
    
    if geojson_path.exists():
        print(f"GeoJSON already exists at {geojson_path}")
        return geojson_path
    
    print("Downloading rivers from CanVec...")
    
    import requests
    import zipfile
    import io
    
    # CanVec Hydro data - this covers all of Canada with detailed rivers
    # We'll download the shapefile for hydrographic features
    url = "https://ftp.maps.canada.ca/pub/nrcan_rncan/vector/canvec/shp/Hydro/canvec_250K_QC_Hydro_shp.zip"
    
    print("Downloading... This may take a few minutes (large file ~250MB)")
    response = requests.get(url, stream=True)
    
    # Save and extract
    zip_path = DATA_PATH / "canvec_hydro.zip"
    with open(zip_path, 'wb') as f:
        for chunk in response.iter_content(chunk_size=8192):
            f.write(chunk)
    
    print("Extracting...")
    with zipfile.ZipFile(zip_path, 'r') as z:
        z.extractall(DATA_PATH / 'canvec_hydro')
    
    # Find the watercourse shapefile
    import glob
    shapefiles = glob.glob(str(DATA_PATH / 'canvec_hydro' / '**' / '*watercourse*.shp'), recursive=True)
    
    if not shapefiles:
        shapefiles = glob.glob(str(DATA_PATH / 'canvec_hydro' / '**' / '*.shp'), recursive=True)
        print(f"Available shapefiles: {[Path(s).name for s in shapefiles]}")
    
    print(f"Loading shapefile: {shapefiles[0]}")
    gdf_rivers = gpd.read_file(shapefiles[0])
    
    # Filter only LineString and MultiLineString
    gdf_rivers = gdf_rivers[gdf_rivers.geometry.type.isin(['LineString', 'MultiLineString'])]
    
    # Keep relevant columns
    cols_to_keep = ['geometry']
    if 'name' in gdf_rivers.columns:
        cols_to_keep.append('name')
    if 'nom' in gdf_rivers.columns:
        cols_to_keep.append('nom')
    
    gdf_rivers = gdf_rivers[cols_to_keep].reset_index(drop=True)
    
    print(f"Loaded {len(gdf_rivers)} river features")
    
    # Save as GeoJSON
    print("Saving to GeoJSON...")
    gdf_rivers.to_file(geojson_path, driver='GeoJSON')
    print(f"Saved to {geojson_path}")
    
    return geojson_path

def download_pyrenees_rivers_osm():
    """Download rivers from OpenStreetMap for the Pyrenees."""
    geojson_path = DATA_PATH / 'pyrenees_rivers_osm.geojson'
    
    if geojson_path.exists():
        print(f"GeoJSON already exists at {geojson_path}")
        return geojson_path
    
    print("Downloading rivers from OpenStreetMap for Pyrenees...")
    
    # Pyrenees bounding box (France/Spain border)
    # [North, South, East, West]
    bbox = (43.5, 42.3, 3.5, -2.5)  # (north, south, east, west)
    
    tags = {'waterway': ['river', 'stream']}
    
    try:
        print("Downloading... This should take 2-5 minutes")
        gdf_rivers = ox.features_from_bbox(bbox=bbox, tags=tags)
        
        # Keep only LineString and MultiLineString
        gdf_rivers = gdf_rivers[gdf_rivers.geometry.type.isin(['LineString', 'MultiLineString'])]
        
        # Keep only useful columns
        cols_to_keep = ['name', 'waterway', 'geometry']
        cols_to_keep = [col for col in cols_to_keep if col in gdf_rivers.columns]
        gdf_rivers = gdf_rivers[cols_to_keep].reset_index(drop=True)
        
        print(f"Downloaded {len(gdf_rivers)} river features")
        
        # Save as GeoJSON
        gdf_rivers.to_file(geojson_path, driver='GeoJSON')
        print(f"Saved to {geojson_path}")
        
    except Exception as e:
        print(f"Error downloading from OSM: {e}")
        return None
    
    return geojson_path

def load_rivers_data(name= "quebec_rivers.geojson"):
    """Load Quebec rivers geojson data."""
    gdf_rivers = gpd.read_file(DATA_PATH / name)
    return gdf_rivers

def plot_rivers_matplotlib(gdf_rivers, output_dir, name):
    """Plot and save rivers map with matplotlib."""
    fig, ax = plt.subplots(1, 1, figsize=(14, 10))
    
    gdf_rivers.plot(ax=ax, color='steelblue', linewidth=0.8, alpha=0.7)
    
    ax.set_title('Rivers of Quebec', fontsize=16, fontweight='bold')
    ax.set_xlabel('Longitude')
    ax.set_ylabel('Latitude')
    ax.set_facecolor('#f0f0f0')
    
    fig.savefig(output_dir / f'{name}.png', bbox_inches='tight', dpi=300)
    plt.close(fig)

def create_rivers_folium_map(gdf_rivers, output_dir, filename):
    """Create and save an interactive folium map of Quebec rivers."""
    
    # Calculate center of the rivers for map positioning
    bounds = gdf_rivers.total_bounds  # [minx, miny, maxx, maxy]
    center_lat = (bounds[1] + bounds[3]) / 2
    center_lon = (bounds[0] + bounds[2]) / 2
    
    m = folium.Map(
        location=[center_lat, center_lon],
        zoom_start=6,
        tiles='CartoDB dark_matter'
    )
    
    # Style for river lines
    def style_function(feature):
        return {
            'color': '#4DB8FF',  # Light blue for rivers
            'weight': 2,
            'opacity': 0.8
        }
    
    # Add rivers to map
    folium.GeoJson(
        gdf_rivers,
        style_function=style_function,
        tooltip=folium.GeoJsonTooltip(
            fields=['name'] if 'name' in gdf_rivers.columns else [],
            aliases=['River Name'] if 'name' in gdf_rivers.columns else []
        )
    ).add_to(m)
    
    m.save(output_dir / f"{filename}.html")

if __name__ == '__main__':
    day = 4  
    output_dir = OUTPUT_DIR / f'day_{day}'
    output_dir.mkdir(parents=True, exist_ok=True)
    # Create geojson
    download_pyrenees_rivers_osm()

    # Load rivers data
    gdf_rivers = load_rivers_data(name='pyrenees_rivers_osm.geojson')
    
    # Create matplotlib visualization
    plot_rivers_matplotlib(gdf_rivers, output_dir, 'pyrenees_rivers_plt')
    
    # Create folium interactive map
    create_rivers_folium_map(gdf_rivers, output_dir, 'pyrenees_rivers_folium')
    
    print(f"Maps saved in {output_dir}")