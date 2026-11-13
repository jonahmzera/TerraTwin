import streamlit as st

st.set_page_config(page_title="TerraTwin | Home", page_icon="🌍", layout="wide")

st.title("🏠 Home")
st.write(
    "Welcome to TerraTwin, the Planetary Analogue Discovery System. "
    "Use the menu on the left to explore Earth sites, planets, and comparisons."
)

st.subheader("What TerraTwin does")
st.write(
    "1. Pick a place on Earth.\n"
    "2. Compare its conditions with another planet.\n"
    "3. Discover which Earth sites are the best analogues."
)

st.subheader("Pages")
st.markdown(
    "- **Earth Explorer**: Earth study locations on a map.\n"
    "- **Planetary Explorer**: Moon and Mars reference regions.\n"
    "- **Comparison Lab**: Chyulu Hills vs Elysium Planitia, with adjustable weights.\n"
    "- **Global Discovery**: not built yet.\n"
    "- **Reports**: download the preliminary report and results."
)

st.info(
    "Only topography is compared so far, for one pair of sites. "
    "Scores are provisional and do not prove that two places are analogues.",
    title="Preliminary results",
)