"""
TerraTwin
Aether Labs
NASA Space Apps Challenge 2026

Main application entry point.
"""

import streamlit as st

PROJECT_NAME = "TerraTwin"
ORGANISATION = "Aether Labs"
VERSION = "0.1.0"

st.set_page_config(page_title=PROJECT_NAME, page_icon="🌍", layout="wide")

st.title(f"🌍 {PROJECT_NAME}")
st.caption(f"{ORGANISATION} | NASA Space Apps Challenge 2026 | v{VERSION}")

st.header("Planetary Analogue Discovery System")
st.write(
    "TerraTwin helps find places on Earth that resemble other planets, "
    "so scientists can test rovers and study conditions close to home."
)

col1, col2, col3 = st.columns(3)
col1.metric("Study locations", "4", help="2 on Earth, 1 on the Moon, 1 on Mars")
col2.metric("Comparisons measured", "1", help="Chyulu Hills (Earth) vs Elysium Planitia (Mars)")
col3.metric("Status", "Preliminary")

st.info(
    "First result: Chyulu Hills (Kenya) vs Elysium Planitia (Mars), topography only. "
    "Open **Comparison Lab** for the scores and **Reports** to download the summary. "
    "No site is claimed as a confirmed analogue yet.",
    title="Where we are",
)