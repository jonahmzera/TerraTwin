import pandas as pd
import streamlit as st

from config.study_locations import STUDY_LOCATIONS

st.set_page_config(page_title="TerraTwin | Planetary Explorer", page_icon="🪐", layout="wide")

st.title("🪐 Planetary Explorer")
st.write("Lunar and Martian reference regions.")

planetary = pd.DataFrame(
    [
        {
            "Region": loc["name"],
            "Body": loc["body"],
            "Lat (approx, planetocentric)": loc["lat"],
            "Lon (approx, east positive)": loc["lon"],
            "Role": loc["role"],
        }
        for loc in STUDY_LOCATIONS.values()
        if loc["body"] != "Earth"
    ]
)

body = st.selectbox("Choose a world", ["All"] + sorted(planetary["Body"].unique()))
if body != "All":
    planetary = planetary[planetary["Body"] == body]

st.dataframe(planetary, width="stretch", hide_index=True)

st.info(
    "These coordinates are on the Moon and Mars, so they are not plotted on an Earth map. "
    "Planetary maps come later."
)
st.info(
    "**Elysium Planitia (Mars)**: measured from the USGS MOLA/HRSC blended DEM at 200 m "
    "(50 km window). See Comparison Lab.\n\n"
    "**Mare Imbrium (Moon)**: not measured yet. Planned source: LOLA.",
    title="Measurements",
)