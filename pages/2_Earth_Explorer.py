import pandas as pd
import streamlit as st

from config.settings import POWER_PARAMETERS
from modules.comparison_engine import image_path, load_earth_sites, load_screen, require, site_label
from modules.environmental_analysis import aridity_score, pressure_kpa_from_elevation
from modules.mapping import GROUP_BADGE, GROUP_LABELS, sites_map
from modules.terrain_analysis import METRIC_INFO

st.set_page_config(page_title="TerraTwin | Earth Explorer", page_icon="🌍", layout="wide")

st.title("🌍 Earth Explorer")
st.write("Every Earth site measured in detail: the team's sites, well-known analogues used for validation, "
         "and new candidates found by the global screening.")

sites = load_earth_sites()
require(sites)

groups = st.pills("Show", list(GROUP_LABELS), default=list(GROUP_LABELS), format_func=GROUP_LABELS.get,
                  selection_mode="multi")
shown = sites[sites["group"].isin(groups or [])]
st.plotly_chart(sites_map(shown, land_cells=load_screen()),
                alt="World map of characterised Earth sites, coloured by group")

if shown.empty:
    st.stop()

key = st.selectbox("Site", shown["key"], format_func=lambda k: site_label(shown.set_index("key").loc[k]))
s = shown.set_index("key").loc[key]

st.subheader(site_label(s))
st.badge(GROUP_LABELS[s["group"]], color=GROUP_BADGE[s["group"]])
st.caption(f"Centre {s['lat']:.3f}, {s['lon']:.3f}. 50 km window at 200 m pixels.")
if isinstance(s.get("notes"), str):
    st.write(s["notes"])

left, right = st.columns([2, 3])
img = image_path("earth", key)
if img:
    left.image(str(img), caption="Shaded relief, 50 km x 50 km (Copernicus GLO-30)", alt=f"Shaded relief of {s['name']}")
else:
    left.info("No terrain image for this site.")

with right:
    st.markdown("**Terrain (Copernicus GLO-30, 200 m)**")
    terrain = pd.DataFrame([{"Measure": label, "Value": s.get(k)} for k, label in METRIC_INFO.items()])
    st.dataframe(terrain, hide_index=True, alt="Terrain measurements")

    st.markdown("**Climate (NASA POWER long-term means)**")
    climate = [{"Measure": label, "Value": s.get(f"power_{k}")} for k, label in POWER_PARAMETERS.items()]
    climate.append({"Measure": "Precipitation (mm/yr)", "Value": s.get("precip_mm_yr")})
    climate.append({"Measure": "Aridity score (0-100, 100 = no rain)", "Value": aridity_score(s.get("precip_mm_yr"))})
    climate.append({"Measure": "Air pressure from elevation (kPa, standard atmosphere)",
                    "Value": pressure_kpa_from_elevation(s.get("elev_mean_m"))})
    st.dataframe(pd.DataFrame(climate), hide_index=True, alt="Climate values")

    st.markdown("**Geology (Macrostrat)**")
    if isinstance(s.get("geo_lith"), str) or isinstance(s.get("geo_name"), str):
        st.write(f"{s.get('geo_name') or ''} | rock types: {s.get('geo_lith') or 'not listed'} | "
                 f"age: {s.get('geo_age') or 'unknown'}")
        if isinstance(s.get("geo_desc"), str):
            st.caption(s["geo_desc"])
    else:
        st.write("No mapped geologic unit at this point (common under ice sheets and in some remote areas).")
