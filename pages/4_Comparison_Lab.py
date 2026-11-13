from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

from config.weights import TOPOGRAPHY_VARIABLES
from modules.similarity_scoring import score_variables

st.set_page_config(page_title="TerraTwin | Comparison Lab", page_icon="🔬", layout="wide")

st.title("🔬 Comparison Lab")
st.write("Chyulu Hills (Earth) vs Elysium Planitia (Mars): topography only, provisional.")

CSV = Path(__file__).resolve().parents[1] / "data" / "processed" / "terratwin_first_measurements.csv"

if not CSV.exists():
    st.error(f"Measurements file not found: {CSV}. Run the Colab notebook and save the CSV there.")
    st.stop()

data = pd.read_csv(CSV).set_index("site")
earth = data.loc["Chyulu Hills (Earth)"]
mars = data.loc["Elysium Planitia (Mars)"]

# ---- Weights (adjustable) ----
st.sidebar.header("Variable weights")
st.sidebar.caption("Provisional values. They are rescaled to add up to 100%.")
raw_weights = {}
for key, cfg in TOPOGRAPHY_VARIABLES.items():
    raw_weights[key] = st.sidebar.slider(cfg["label"], 0, 100, cfg["default_weight"])

total_w = sum(raw_weights.values())
if total_w == 0:
    st.warning("All weights are zero. Move at least one slider above zero.")
    st.stop()

# ---- Variable-by-variable comparison (shared with the Reports page) ----
table, overall = score_variables(
    earth,
    mars,
    TOPOGRAPHY_VARIABLES,
    weights=raw_weights,
    earth_label="Chyulu Hills",
    planet_label="Elysium Planitia",
)
usable = table.dropna(subset=["Similarity (0-100)"])

# ---- Results ----
c1, c2, c3 = st.columns(3)
c1.metric("Topography similarity (provisional)", "n/a" if overall is None else f"{overall:.1f} / 100")
c2.metric("Variables compared", f"{len(usable)} of {len(table)}")
c3.metric("Categories with data", "1 of 5")

st.subheader("Measurements and similarity")
st.dataframe(table, width="stretch", hide_index=True)

fig = px.bar(
    usable,
    x="Variable",
    y="Similarity (0-100)",
    range_y=[0, 100],
    title="Per-variable similarity",
)
st.plotly_chart(fig, width="stretch")

st.download_button(
    "Download comparison as CSV",
    table.to_csv(index=False),
    file_name="chyulu_vs_elysium_topography.csv",
)

# ---- Data sources ----
st.subheader("Data sources")
st.dataframe(
    data[["dataset", "provider", "native_resolution", "crs", "window_km", "pixel_size_m", "valid_pixels_pct"]].T.astype(str),
    width="stretch",
)

# ---- Limitations ----
st.subheader("Limitations")
st.warning(
    "**Do not treat this score as evidence of equivalence.** It only compares topography, "
    "using weights and comparison ranges that are provisional assumptions. "
    "Changing the study window or the ranges changes the score.\n\n"
    "- **Geology, geomorphology, environment and operational relevance are not compared yet** (no data loaded).\n"
    "- **Study windows are 50 km boxes** around approximate centre points, not surveyed boundaries. "
    "The Chyulu window was checked on a map by the team: its highest pixel falls inside the Chyulu Hills, not Kilimanjaro.\n"
    "- Both sites are read at the same ~200 m pixel size so slope and roughness are comparable. "
    "The Earth data is natively 30 m and was averaged down.\n"
    "- Earth data is a surface model (DSM), so vegetation can affect roughness. Mars data is a MOLA/HRSC blend.\n"
    "- Absolute elevation is not compared because Earth and Mars use different reference surfaces.\n"
    "- Mars maximum slope (38.6°) may come from a single extreme pixel and is unverified.\n"
    "- Mars elevation units are not stored in the file metadata and still need confirming from the USGS documentation."
)