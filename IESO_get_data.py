import pandas as pd
import requests

from constants import DATA_PATH

def get_file(url: str, name:str):
    """
    Retrieve data from url
    """
    response = requests.get(url)
    if response.status_code == 200:
        with open(name, "wb") as f:
            f.write(response.content)
        print(f"{url} file downloaded successfully")
    else:
        print(f'Failed to downlaod file. Status code: {response.status_code}')

def parser_capa(file_name: str):
    """
    Parse generation data
    """
    return pd.read_csv(file_name, skiprows =3, index_col=False)

def format_capacity(df: pd.DataFrame):
    """
    Format the capacity data to return the max capacity per plant
    """
    output_df = df[(df['Measurement'] == 'Available Capacity')| (df['Measurement'] == 'Capability')].copy()


    hour_cols = [col for col in output_df.columns if col.startswith('Hour')]
    output_df['Total Capa'] = output_df[hour_cols].max(axis=1).astype(float)

    total_gen = output_df.groupby(['Generator', 'Fuel Type'])['Total Capa'].max().reset_index()
    return total_gen


def clean_generator_name(name):
    name = str(name).upper().strip()
    name = name.replace("-", "").replace("_", "").replace(".", "")
    return name




if __name__ == "__main__":

    url = "https://reports-public.ieso.ca/public/GenOutputCapabilityMonth/PUB_GenOutputCapabilityMonth_202510.csv"
    name = DATA_PATH / "capacity_102025.txt"

    get_file(url,name)
    df = parser_capa(name)
    df_capacities = format_capacity(df)

    df_location = pd.read_excel(DATA_PATH / "source_ontario_thesis.xlsx")
    df_location["Generator"]=df_location["Generators"].str.upper()
    df_location.drop('Generators', axis=1, inplace=True)

    df_location["Fuel Type"] = df_location["Fuel Type"].str.upper()
    # Darlington nuclear power plant is in Toronto region 
    df_location.loc[df_location["Generator"].str.contains("DARLINGTON", case=False, na=False), "IESO Region"] = "Toronto"

    df_join = df_capacities.merge(df_location, on = ["Generator", "Fuel Type"], how="left")

    missing_locations = df_join[df_join["Latitude"].isna() | df_join["IESO Region"].isna()]["Generator"].unique()

    print(f"Missing power plant locations {len(missing_locations)} before manual correction  (manual_coords) :")
    print(missing_locations)
    manual_coords = {
    "CRYSLER": {
        "Latitude": 45.219677,
        "Longitude": -75.153938,
        "IESO Region": "East"
    },
    "MCLEANSMTNWF-LT.AG_T1": {
        "Latitude": 45.935435,
        "Longitude": -81.986758,
        "IESO Region": "North"
    },
    "RAILBEDWF-LT.AG_SR": {
        "Latitude": 42.401718,
        "Longitude": -82.154912,
        "IESO Region": "West"
    },
    "ROMNEY": {
        "Latitude": 42.411972,
        "Longitude": -82.162000,
        "IESO Region": "West"
    },
    "SANDUSK-LT.AG_T1": {
        "Latitude": 42.799120,
        "Longitude": -80.194123,
        "IESO Region": "West"
    },
    "COCHRANECGS": {
        "Latitude": 43.85,
        "Longitude": -79.45,
        "IESO Region": "Toronto"
    },
    "GOREWAY BESS": {
        "Latitude": 43.75,
        "Longitude": -79.60,
        "IESO Region": "Toronto"
    },
    "HAGERSVILLE BESS": {
        "Latitude": 43.15,
        "Longitude": -79.90,
        "IESO Region": "Niagara"
    },
    "HALTONHILLS-LT.G1": {
        "Latitude": 43.65,
        "Longitude": -79.95,
        "IESO Region": "Toronto"
    },
    "HALTONHILLS-LT.G2": {
        "Latitude": 43.65,
        "Longitude": -79.95,
        "IESO Region": "Toronto"
    },
    "HALTONHILLS-LT.G3": {
        "Latitude": 43.65,
        "Longitude": -79.95,
        "IESO Region": "Toronto"
    },
    "HYDROGEN READY POWER PLANT (HRPP)": {
        "Latitude": 43.85,
        "Longitude": -79.35,
        "IESO Region": "Toronto"
    },
    "NAPANEE-G3": {
        "Latitude": 44.25,
        "Longitude": -76.95,
        "IESO Region": "East"
    },
    "ONEIDA ENERGY STORAGE": {
        "Latitude": 42.85,
        "Longitude": -80.25,
        "IESO Region": "West"
    },
    "PICKERINGA-G1": {
        "Latitude": 43.82,
        "Longitude": -79.07,
        "IESO Region": "Toronto"
    },
    "PICKERINGA-G4": {
        "Latitude": 43.82,
        "Longitude": -79.07,
        "IESO Region": "Toronto"
    },
    "PICKERINGB-G5": {
        "Latitude": 43.82,
        "Longitude": -79.07,
        "IESO Region": "Toronto"
    },
    "PICKERINGB-G6": {
        "Latitude": 43.82,
        "Longitude": -79.07,
        "IESO Region": "Toronto"
    },
    "PICKERINGB-G7": {
        "Latitude": 43.82,
        "Longitude": -79.07,
        "IESO Region": "Toronto"
    },
    "PICKERINGB-G8": {
        "Latitude": 43.82,
        "Longitude": -79.07,
        "IESO Region": "Toronto"
    },
    "TBAYBOWATER CTS": {
        "Latitude": 48.38,
        "Longitude": -89.25,
        "IESO Region": "Northwest"
    },
    "TILBURY BATTERY STORAGE": {
        "Latitude": 42.25,
        "Longitude": -82.43,
        "IESO Region": "West"
    },
    "YORK BESS": {
        "Latitude": 43.85,
        "Longitude": -79.50,
        "IESO Region": "Toronto"
    }
}
    
    df_join["Latitude"] = df_join.apply(
    lambda row: manual_coords.get(row["Generator"], {}).get("Latitude", row["Latitude"]),
    axis=1)

    df_join["Longitude"] = df_join.apply(
    lambda row: manual_coords.get(row["Generator"], {}).get("Longitude", row["Longitude"]),
    axis=1)

    df_join["IESO Region"] = df_join.apply(
    lambda row: manual_coords.get(row["Generator"], {}).get("IESO Region", row["IESO Region"]),
    axis=1)
    
    missing = df_join[df_join["IESO Region"].isna()]["Generator"].unique()
    print(f"Générateurs toujours manquants {len(missing)} :", missing)
    print(df_join)
    df_agg = df_join.groupby(['IESO Region', 'Fuel Type'])['Total Capa'].sum().reset_index()

    df_agg.to_csv(DATA_PATH / "cap_fuel_type.csv")

