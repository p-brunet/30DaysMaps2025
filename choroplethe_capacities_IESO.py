from constants import DATA_PATH, OUTPUT_DIR
import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
import folium
import branca.colormap as cm
from pathlib import Path

def load_and_prepare_data():
    """Load and prepare capacity and geojson data."""
    df_region = pd.read_csv(DATA_PATH / "cap_fuel_type.csv")
    df_cap = df_region.groupby(['IESO Region'])['Total Capa'].sum().reset_index()
    df_renewables = df_region[(df_region['Fuel Type'].isin(["WIND", "SOLAR"]))].groupby(['IESO Region'])['Total Capa'].sum().reset_index()
    gdf = gpd.read_file(DATA_PATH / 'ieso_zones.geojson')
    gdf = gdf.rename(columns={'name': 'IESO Region'})
    gdf_cap = gdf.merge(df_cap, on='IESO Region', how='left')
    gdf_r = gdf.merge(df_renewables, on='IESO Region', how='left')
    return gdf_cap, gdf_r

def plot_total_capacity(gdf_cap, output_dir):
    """Plot and save total capacity map."""
    fig, ax = plt.subplots(1, 1, figsize=(12, 8))
    gdf_cap.plot(column='Total Capa', ax=ax, legend=True,
                 legend_kwds={'label': "Total Capacity (MW)"},
                 cmap='OrRd', missing_kwds={'color': 'lightgrey'})
    ax.set_title('Total Capacity by IESO Region')
    fig.savefig(output_dir / 'total_capacity.png', bbox_inches='tight', dpi=300)
    plt.close(fig)

def plot_renewables_capacity(gdf_r, output_dir):
    """Plot and save renewables capacity map."""
    fig, ax = plt.subplots(1, 1, figsize=(12, 8))
    gdf_r.plot(column='Total Capa', ax=ax, legend=True,
               legend_kwds={'label': "Total Capacity (MW) for PV and Wind"},
               cmap='YlGn', missing_kwds={'color': 'lightgrey'})
    ax.set_title('Total Capacity of PV and Wind by IESO Region')
    fig.savefig(output_dir / 'renewables_capacity.png', bbox_inches='tight', dpi=300)
    plt.close(fig)

def create_folium_map(gdf, column, title, output_dir, filename, cmap_type='total'):
    """
    Create and save an interactive folium map with a dark basemap and robust colormap.
    cmap_type: 'total' (orange/red) or 'renewables' (green)
    """
    gdf_clean = gdf.dropna(subset=[column])
    vmin = 0
    vmax = gdf_clean[column].max() if not gdf_clean.empty and not gdf_clean[column].empty else 1000 

    
    if cmap_type == 'total':
        colormap = cm.LinearColormap(
            colors=['#D3D3D3', '#FFA500', '#FF0000'],
            vmin=vmin,
            vmax=vmax,
            caption=f'Total Capacity (MW)'
        )
        
    else:  # renewables
        colormap = cm.LinearColormap(
            colors=['#D3D3D3', '#9ACD32', '#008000'],
            vmin=vmin,
            vmax=vmax,
            caption=f'Renewables Capacity (MW)'
        )
        

    m = folium.Map(
        location=[44, -78],
        zoom_start=6,
        tiles='CartoDB dark_matter'
    )

    def style_function(feature):
        value = feature['properties'].get(column)
        if value is None or pd.isna(value) or value == 0:
            return {'fillColor': 'grey', 'color': 'black', 'weight': 1, 'fillOpacity': 0.7}
        else:
            return {
                'fillColor': colormap(value),
                'color': 'white',
                'weight': 1,
                'fillOpacity': 0.7
            }
        
    folium.GeoJson(
        gdf,
        style_function= style_function,
        tooltip=folium.GeoJsonTooltip(fields=['IESO Region', column], aliases=['IESO Region', 'Total Capacity in MW'])
    ).add_to(m)

    colormap.add_to(m)
    CSS = """
    #legend text { fill: white !important; font-size: 14px; }
    """
    m.get_root().header.add_child(folium.Element(f"<style>{CSS}</style>"))

    m.save(output_dir / f"{filename}.html")

if __name__ == '__main__':
    day = 3
    output_dir = OUTPUT_DIR / f'day_{day}'
    output_dir.mkdir(parents=True, exist_ok=True)
    use_folium = True

    gdf_cap, gdf_r = load_and_prepare_data()

    plot_total_capacity(gdf_cap, output_dir)
    plot_renewables_capacity(gdf_r, output_dir)

    if use_folium:
        create_folium_map(gdf_cap, 'Total Capa', 'Total Capacity', output_dir, 'total_capacity_folium', cmap_type='total')
        create_folium_map(gdf_r, 'Total Capa', 'Renewables Capacity', output_dir, 'renewables_capacity_folium', cmap_type='renewables')
