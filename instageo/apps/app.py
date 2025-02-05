# ------------------------------------------------------------------------------
# This code is licensed under the Attribution-NonCommercial-ShareAlike 4.0
# International (CC BY-NC-SA 4.0) License.
#
# You are free to:
# - Share: Copy and redistribute the material in any medium or format
# - Adapt: Remix, transform, and build upon the material
#
# Under the following terms:
# - Attribution: You must give appropriate credit, provide a link to the license,
#   and indicate if changes were made. You may do so in any reasonable manner,
#   but not in any way that suggests the licensor endorses you or your use.
# - NonCommercial: You may not use the material for commercial purposes.
# - ShareAlike: If you remix, transform, or build upon the material, you must
#   distribute your contributions under the same license as the original.
#
# For more details, see https://creativecommons.org/licenses/by-nc-sa/4.0/
# ------------------------------------------------------------------------------

"""InstaGeo Serve Module.

InstaGeo Serve is a web application that enables the visualisation of GeoTIFF files in an
interactive map.
"""

import glob
import json
import os
from pathlib import Path

import streamlit as st
import pandas as pd

# from instageo import INSTAGEO_APPS_PATH
# from instageo.apps.viz import create_map_with_geotiff_tiles
from viz import create_map_with_geotiff_tiles


def generate_map(
    # directory: str, 
    year: int, month: int, country_tiles: list[str], selected_country: str,
) -> None:
    """Generate the plotly map.

    Arguments:
        directory (str): Directory containing GeoTiff files.
        year (int): Selected year.
        month (int): Selected month formatted as an integer in the range 1-12.
        country_tiles (list[str]): List of MGRS tiles for the selected country.

    Returns:
        None.
    """
    try:
        # if not directory or not Path(directory).is_dir():
        #     raise ValueError("Invalid directory path.")
        directory = "C:\\Users\\DUNOYERS\\working\\InstaGeo-E2E-Geospatial-ML\\instageo\\apps"
        prediction_tiles = glob.glob(os.path.join(directory, f"{year}/{month}/*.tif"))
        print(prediction_tiles)
        tiles_to_consider = [
            tile
            for tile in prediction_tiles
            if os.path.basename(tile).split("_")[4].strip("T") in country_tiles
        ]

        if not tiles_to_consider:
            raise FileNotFoundError(
                "No GeoTIFF files found for the given year, month, and country."
            )

        fig = create_map_with_geotiff_tiles(tiles_to_consider, selected_country)
        st.plotly_chart(fig, use_container_width=True)


    except (ValueError, FileNotFoundError, Exception) as e:
        st.error(f"An error occurred: {str(e)}")

import plotly.graph_objects as go

def main() -> None:
    """Instageo Serve Main Entry Point."""
    st.set_page_config(layout="wide")
    st.title("Desert Locus Potential Breeding Locations")

    st.sidebar.subheader(
        "This application enables the visualisation of GeoTIFF files on an interactive map.",
        divider="rainbow",
    )
    st.sidebar.header("⚙️ Settings")

    # Load country-to-tiles mapping
    with open(
        # INSTAGEO_APPS_PATH / "utils/country_code_to_mgrs_tiles.json"
        "utils/country_code_to_mgrs_tiles.json"
    ) as json_file:
        countries_to_tiles_map = json.load(json_file)
    
    # Define a polygon for the breeding region in Iran
    BREEDING_REGION_IRAN = {
        "name": "Breeding Region",
        "lat": [32.5, 33.0, 33.0, 32.5, 32.5],  # Latitude coordinates (polygon)
        "lon": [53.5, 53.5, 54.0, 54.0, 53.5],  # Longitude coordinates (polygon)
    }
    # Sidebar Inputs
    country_code = st.sidebar.selectbox(
        "🌎 Select a Country (ISO 3166-1 Alpha-2 Code):",
        options=list(countries_to_tiles_map.keys()),
    )
    year = st.sidebar.number_input("📅 Select Year", 2016, 2017)
    month = st.sidebar.number_input("📅 Select Month", 1, 12)

    # Load country center data
    centers_df = pd.read_csv('countries.csv')

    # Variable de session pour stocker les coordonnées
    if "hover_lat" not in st.session_state:
        st.session_state.hover_lat = None
        st.session_state.hover_lon = None

    # with st.sidebar.container():
        # directory = st.sidebar.text_input(
        #     "GeoTiff Directory:",
        #     help="Write the path to the directory containing your GeoTIFF files",
        # )
        # country_code = st.sidebar.selectbox(
        #     "ISO 3166-1 Alpha-2 Country Code:",
        #     options=list(countries_to_tiles_map.keys()),
        # )
        # year = st.sidebar.number_input("Select Year", 2016, 2017)
        # month = st.sidebar.number_input("Select Month", 1, 12)

    # Function to create a map
    def create_map(country_code):
        """Generates a Plotly map centered on the selected country."""
        fig = go.Figure(go.Scattermapbox())

        # Find country center from CSV
        country_info = centers_df[centers_df['ISO'] == country_code]
        if not country_info.empty:
            center_lat = country_info.iloc[0]['latitude']
            center_lon = country_info.iloc[0]['longitude']
            zoom_level = 5
        else:
            center_lat, center_lon, zoom_level = 32.4279, 53.6880, 2  # Default: Iran

        # Create the map
        fig.update_layout(
            mapbox_style="open-street-map",
            mapbox=dict(center=go.layout.mapbox.Center(lat=center_lat, lon=center_lon), zoom=zoom_level),
            margin={"r": 0, "t": 0, "l": 0, "b": 0}
        )

        # If Iran is selected, add the "Breeding Region" polygon
        if country_code == "IR":
            fig.add_trace(go.Scattermapbox(
                fill="toself",
                lon=BREEDING_REGION_IRAN["lon"],
                lat=BREEDING_REGION_IRAN["lat"],
                marker={"size": 10, "color": "red"},
                fillcolor="rgba(255, 0, 0, 0.3)",  # Semi-transparent red
                name="Breeding Region"
            ))
        # Ajout du mode "hover" pour capturer les coordonnées
        fig.update_traces(mode="markers+text", hoverinfo="lat+lon")

        return fig

    # Affichage de la carte avec callback pour récupérer les coordonnées
    fig = create_map(country_code)
    hover_data = st.plotly_chart(fig, use_container_width=True)

    # Extraire les coordonnées de l'événement hover
    if hover_data is not None and hover_data.get("points"):
        point = hover_data["points"][0]
        lat, lon = point["lat"], point["lon"]
        st.session_state.hover_lat, st.session_state.hover_lon = lat, lon

    # Afficher les coordonnées sous la carte
    if st.session_state.hover_lat and st.session_state.hover_lon:
        st.sidebar.write(f"📍 Coordonnées survolées : **{st.session_state.hover_lat}, {st.session_state.hover_lon}**")

    # Bouton de génération de carte
    if st.sidebar.button("🗺️ Générer la carte"):
        country_tiles = countries_to_tiles_map[country_code]
        generate_map(year, month, country_tiles, country_code)
    else:
        st.plotly_chart(
            create_map_with_geotiff_tiles(tiles_to_overlay=[]), use_container_width=True
        )

if __name__ == "__main__":
    main()
