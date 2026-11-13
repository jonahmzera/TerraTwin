from datetime import date
from pathlib import Path

import pandas as pd
import streamlit as st

from config.weights import TOPOGRAPHY_VARIABLES
from modules.similarity_scoring import score_variables

st.set_page_config(page_title="TerraTwin | Reports", page_icon="📄", layout="wide")

st.title("📄 Reports")
st.write("Preliminary report for the Chyulu Hills vs Elysium Planitia comparison.")

CSV = Path(__file__).resolve().parents[1] / "data" / "processed" / "terratwin_first_measurements.csv"
if not CSV.exists():
    st.error(f"Measurements file not found: {CSV}. Run the Colab notebook and save the CSV there.")
    st.stop()

data = pd.read_csv(CSV).set_index("site")
earth = data.loc["Chyulu Hills (Earth)"]
mars = data.loc["Elysium Planitia (Mars)"]

# The report always uses the default (equal) weights, not the Comparison Lab sliders,
# so every downloaded report is reproducible.
table, overall = score_variables(
    earth,
    mars,
    TOPOGRAPHY_VARIABLES,
    earth_label="Chyulu Hills",
    planet_label="Elysium Planitia",
)
scored = int(table["Similarity (0-100)"].notna().sum())
overall_text = "not available" if overall is None else f"{overall:.1f} / 100"


def fmt(value):
    """Show missing values as 'missing', never as 0."""
    return "missing" if pd.isna(value) else f"{value:g}"


# ---- Build the report text ----
lines = [
    "# TerraTwin preliminary report",
    "Aether Labs | NASA Space Apps Challenge 2026",
    f"Generated: {date.today().isoformat()}",
    "",
    "## Status",
    "Preliminary. Topography only. This report does not show that the Chyulu Hills "
    "are an analogue of Elysium Planitia.",
    "",
    "## Research question",
    "Do selected topographic measurements of a 50 km area of the Chyulu Hills (Kenya) "
    "resemble those of a 50 km area of Elysium Planitia (Mars)?",
    "",
    "## Datasets",
]
for site in (earth, mars):
    lines.append(
        f"- **{site.name}**: {site['dataset']}, provider {site['provider']}. "
        f"Native resolution: {site['native_resolution']}. CRS: {site['crs']}. "
        f"Window: {site['window_km']} km, pixel size {site['pixel_size_m']:g} m, "
        f"valid pixels {site['valid_pixels_pct']:g}%."
    )
lines += [
    "",
    "## Method",
    "Both windows were read at about 200 m per pixel. Relief (highest minus lowest point), "
    "mean slope, maximum slope and terrain ruggedness (TRI: mean absolute elevation "
    "difference to the 8 neighbouring pixels) were calculated from the elevation grids. "
    "Per-variable similarity = 100 x max(0, 1 - |Earth - Mars| / R), where R is a "
    "provisional comparison range. The overall score is the weighted average of the "
    "per-variable similarities, using equal provisional weights. Missing values are never "
    "treated as zero.",
    "",
    "## Measurements and similarity",
    "| Variable | Chyulu Hills | Elysium Planitia | Difference | R | Similarity | Weight % |",
    "|---|---|---|---|---|---|---|",
]
for _, r in table.iterrows():
    lines.append(
        f"| {r['Variable']} | {fmt(r['Chyulu Hills'])} | {fmt(r['Elysium Planitia'])} | "
        f"{fmt(r['Difference'])} | {fmt(r['Range R'])} | {fmt(r['Similarity (0-100)'])} | "
        f"{fmt(r['Weight (%)'])} |"
    )
lines += [
    "",
    f"Topography similarity (provisional): **{overall_text}**",
    "",
    f"Variables compared: {scored} of {len(table)}. Categories with data: 1 of 5 (topography only).",
    "",
    "## Limitations",
    "- Geology, geomorphology, environment and operational relevance are not compared yet.",
    "- Windows are 50 km boxes around approximate centre points, not surveyed boundaries.",
    "- The Chyulu window was checked on a map: its highest pixel falls inside the Chyulu Hills, not Kilimanjaro.",
    "- Comparison ranges and weights are provisional assumptions. Changing them or the window changes the score.",
    "- The Earth data is natively 30 m and was averaged down to about 200 m to match Mars.",
    "- Earth data is a surface model (DSM), so vegetation can affect roughness.",
    "- Absolute elevation is not compared because Earth and Mars use different reference surfaces.",
    "- Mars maximum slope (38.6 degrees) may come from a single extreme pixel and is unverified.",
    "- Mars elevation units are not stored in the file metadata and still need confirming from USGS documentation.",
    "",
    "## References",
    "- Copernicus DEM GLO-30, European Space Agency / Copernicus programme.",
    "- Fergason, R. L., Hare, T. M., & Laura, J. (2018). HRSC and MOLA Blended Digital "
    "Elevation Model at 200m v2. Astrogeology PDS Annex, U.S. Geological Survey. "
    "https://astrogeology.usgs.gov/search/map/mars_mgs_mola_mex_hrsc_blended_dem_global_200m",
    "",
    "## AI assistance",
    "AI assistance (Claude) was used for code and for planning the analysis. "
    "The team should edit this section to describe exactly what was AI-assisted. "
    "All numbers above come from the datasets listed, not from AI.",
]
report = "\n".join(lines)

# ---- Summary, downloads and the report itself ----
c1, c2, c3 = st.columns(3)
c1.metric("Topography similarity (provisional)", "n/a" if overall is None else f"{overall:.1f} / 100")
c2.metric("Variables compared", f"{scored} of {len(table)}")
c3.metric("Categories with data", "1 of 5")

st.caption("The report uses equal default weights. Slider changes in Comparison Lab do not affect it.")

with st.container(horizontal=True):
    st.download_button(
        "Download report (Markdown)",
        report,
        file_name="terratwin_report.md",
        mime="text/markdown",
        icon=":material/description:",
    )
    st.download_button(
        "Download results (CSV)",
        table.to_csv(index=False),
        file_name="terratwin_results.csv",
        mime="text/csv",
        icon=":material/table:",
    )

with st.container(border=True):
    st.markdown(report)
