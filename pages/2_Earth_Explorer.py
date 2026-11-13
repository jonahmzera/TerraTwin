import pandas as pd
import plotly.express as px
import streamlit as st

from config.study_locations import STUDY_LOCATIONS

st.set_page_config(page_title="TerraTwin | Earth Explorer", page_icon="🌍", layout="wide")

st.title("🌍 Earth Explorer")
st.write("Terrestrial study locations.")

earth = pd.DataFrame(
    [
        {
            "Location": loc["name"],
            "Country": loc["country"],
            "Lat (approx)": loc["lat"],
            "Lon (approx)": loc["lon"],
            "Role": loc["role"],
        }
        for loc in STUDY_LOCATIONS.values()
        if loc["body"] == "Earth"
    ]
)

st.dataframe(earth, width="stretch", hide_index=True)

fig = px.scatter_geo(
    earth,
    lat="Lat (approx)",
    lon="Lon (approx)",
    hover_name="Location",
    color="Location",
    projection="natural earth",
)
st.plotly_chart(fig, width="stretch")

st.info(
    "**Chyulu Hills**: measured from Copernicus DEM GLO-30 (50 km window, averaged to ~200 m). "
    "See Comparison Lab for relief, slope and roughness.\n\n"
    "**Lonar Crater**: not measured yet.",
    title="Measurements",
)
st.caption("All measurements come from real datasets, never typed in by hand.")