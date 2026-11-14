import pandas as pd
import streamlit as st

from config.settings import PROCESSED_DIR, SOURCES
from config.study_locations import EARTH_LIMITS
from modules.comparison_engine import load_earth_sites, require
from modules.similarity_scoring import DIMENSIONS, TERRAIN_VARIABLES

st.set_page_config(page_title="TerraTwin | Methods and data", page_icon="🧪", layout="wide")

st.title("🧪 Methods and data")
st.write("Everything needed to check, reproduce or challenge TerraTwin's results.")

st.subheader("Data sources")
st.dataframe(
    pd.DataFrame([{"Dataset": s["name"], "Provider": s["provider"], "Resolution": s["native_resolution"],
                   "Citation": s["citation"]} for s in SOURCES.values()]),
    hide_index=True, alt="Datasets used",
)

st.subheader("Pipeline")
st.markdown(
    "All numbers come from `scripts/run_pipeline.py`. It reads the open datasets directly from their public "
    "hosts (no logins) and writes the CSV files in `data/processed/` that this app displays.\n\n"
    "1. **Targets.** An 80 km window around each Moon and Mars site is resampled onto a local azimuthal "
    "equidistant grid at 200 m. The central 50 km is measured for stage 2; the window averaged to 1.2 km is "
    "measured for stage 1.\n"
    "2. **Global screening.** About 4,096 Terrain Tiles cover the Earth. Each is cut into cells of about 78 km, "
    "block-averaged to about 1.2 km pixels (correcting the Web Mercator stretch), and measured. Cells that are "
    "mostly sea are skipped.\n"
    "3. **Candidates.** For each target, the six highest-scoring cells outside the Antarctic and Greenland ice "
    "sheets are picked, at least 500 km apart and at least 100 km from the known analogue sites, so the "
    "shortlist is diverse and new. Smooth ice sheets top the terrain-only ranking for several targets, so two "
    "ice-sheet cells per target are also kept as 'lookalikes', to show what the other dimensions reveal about "
    "them (they match on terrain and cold, but score zero on rock type).\n"
    "4. **Characterisation.** Each Earth site (team, known and discovered) is measured at 200 m from Copernicus "
    "GLO-30 in a 50 km window. NASA POWER climate and Macrostrat geology are added at the centre point."
)

st.subheader("Measurements")
st.markdown(
    "- **Slope:** Horn (1981) 3x3 method, the same as GDAL and ArcGIS.\n"
    "- **Ruggedness (TRI):** mean absolute height difference to the 8 neighbouring pixels (Wilson et al., 2007).\n"
    "- **Relief:** highest minus lowest point in the window.\n"
    "- **Hypsometric integral:** (mean - min) / (max - min); describes the shape of the landscape "
    "(Strahler, 1952).\n"
    "- **Flat area:** share of pixels with slope under 5 degrees at 200 m, a proxy for landing and driving room.\n"
    "- **95th-percentile slope:** steep terrain that is common, not a single extreme pixel."
)

st.subheader("Scoring")
st.latex(r"\text{similarity} = 100 \times \max\left(0,\ 1 - \frac{|x_{Earth} - x_{target}|}{R}\right)")
st.markdown(
    "- **R is set by the data, not by hand:** the 5th to 95th percentile spread of the variable across the Earth "
    "sites compared. Relief, slope and ruggedness are compared on a log scale.\n"
    "- **Dimensions:** " + ", ".join(DIMENSIONS.values()) + ". A dimension score is the mean of its variables; "
    "the overall score is the weighted mean of dimensions with data. Missing data is never counted as zero; it "
    "lowers the coverage figure.\n"
    "- **Geology:** 100 if a primary rock type of the target appears in the Macrostrat unit, 60 for a related "
    "rock type, 0 otherwise.\n"
    "- **Climate:** NASA POWER annual mean temperature, daily temperature range and aridity "
    "(log-scaled precipitation) against rounded literature values for the target.\n"
    "- **Uncertainty:** each score is recomputed 200-500 times with random weights (Dirichlet around the "
    "chosen weights) and comparison ranges (x0.67 to x1.5). The 5th-95th percentile band is reported."
)
st.dataframe(pd.DataFrame([{"Variable": v[0], "Dimension": DIMENSIONS[v[1]], "Scale": "log10" if v[2] else "linear"}
                           for v in TERRAIN_VARIABLES.values()]), hide_index=True, alt="Terrain variables")

st.subheader("Validation")
sites = load_earth_sites()
require(sites)
colab = PROCESSED_DIR / "terratwin_first_measurements.csv"
if colab.exists() and "chyulu_hills" in set(sites["key"]):
    old = pd.read_csv(colab).set_index("site").loc["Chyulu Hills (Earth)"]
    new = sites.set_index("key").loc["chyulu_hills"]
    st.markdown("**Independent reproduction of the first Colab measurement (Chyulu Hills, 50 km, ~200 m)**")
    st.dataframe(pd.DataFrame([
        {"Measure": "Relief (m)", "Colab notebook": old["relief_m"], "Pipeline": new["relief_m"]},
        {"Measure": "Mean slope (deg)", "Colab notebook": old["slope_mean_deg"], "Pipeline": new["slope_mean_deg"]},
        {"Measure": "TRI (m)", "Colab notebook": old["roughness_tri_m"], "Pipeline": new["roughness_tri_m"]},
    ]), hide_index=True, alt="Colab versus pipeline measurements")
    st.caption("The two use different code and grids (geographic box vs local equidistant projection), so "
               "small differences are expected. Agreement within a few percent shows the measurements are stable.")
st.markdown(
    "- **Known analogues as a test:** sites such as Haughton Crater, the Atacama Desert and Mauna Kea are scored "
    "exactly like new candidates. If the method works, they should rank reasonably well for the targets they are "
    "used for. Global Discovery shows where they rank.\n"
    "- **Mars elevation units:** the mean elevation measured around the InSight landing site agrees with the "
    "published landing elevation of -2,613 m (Golombek et al., 2020), confirming metres."
)

st.subheader("Limitations")
st.markdown(
    "- Windows are fixed squares around centre points; a smaller area inside could be a stronger analogue.\n"
    "- Stage 1 uses ~1.2 km pixels and a merged global DEM; it can miss small features such as single craters "
    "or lava tubes. Stage 2 re-measures candidates at 200 m.\n"
    "- Pixels at or below sea level are treated as sea in stage 1, so below-sea-level deserts (e.g. the Dead Sea "
    "basin) are under-represented.\n"
    "- Copernicus is a surface model: vegetation and buildings add roughness.\n"
    "- Moon and Mars climate values are rounded literature values. Geology matching uses map keywords, not "
    "mineralogy.\n"
    "- Not yet scored: vegetation cover, dust and aerosols, ice and permafrost, caves and subsurface. They are "
    "described in site notes where known.\n"
    "- Earth cannot reproduce: " + " ".join(EARTH_LIMITS["Mars"][:1] + EARTH_LIMITS["Moon"][1:2])
)
