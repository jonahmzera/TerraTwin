import pandas as pd
import streamlit as st

from config.settings import SOURCES
from config.study_locations import EARTH_LIMITS, TARGETS
from modules.comparison_engine import image_path, load_targets, require
from modules.terrain_analysis import METRIC_INFO

st.set_page_config(page_title="TerraTwin | Planetary Explorer", page_icon="🪐", layout="wide")

st.title("🪐 Planetary Explorer")
st.write("The Moon and Mars sites TerraTwin searches Earth for: real landing sites and candidate base regions.")

targets = load_targets()
require(targets)

body = st.segmented_control("World", ["Mars", "Moon"], default="Mars", required=True)
keys = [k for k, t in TARGETS.items() if t["body"] == body]
key = st.selectbox("Target", keys, format_func=lambda k: TARGETS[k]["name"])
t = TARGETS[key]
row = targets.set_index("key").loc[key]

st.subheader(t["name"])
st.write(t["why"])
st.caption(f"Centre {t['lat']}, {t['lon']} (planetocentric, east positive){' (approx)' if t['approx'] else ''}. "
           f"Source: {t['coord_source']}")

left, right = st.columns([2, 3])
img = image_path("target", key)
if img:
    left.image(str(img), caption=f"Shaded relief, 50 km x 50 km ({SOURCES[t['dem']]['name']})",
               alt=f"Shaded relief of {t['name']}")

with right:
    st.markdown("**Terrain, 50 km window at 200 m**")
    terrain = pd.DataFrame([{"Measure": label, "Value": row.get(f"d_{k}")} for k, label in METRIC_INFO.items()])
    st.dataframe(terrain, hide_index=True, alt="Target terrain measurements")
    st.markdown("**Geology**")
    st.write(t["geology_summary"])
    st.markdown("**Environment (literature values)**")
    env = t["environment"]
    st.write(f"Mean temperature about {env['T2M']} degC, daily range about {env['T2M_RANGE']} degC, "
             f"no precipitation, surface pressure about {env['pressure_kpa']} kPa.")
    st.caption(env["source"])

st.markdown("**What an Earth analogue could help with here**")
st.markdown("\n".join(f"- {u}" for u in t["exploration_use"]))

st.warning("\n".join(f"- {x}" for x in EARTH_LIMITS[t["body"]]), title="What no Earth site can reproduce")

if key == "mars_insight":
    st.caption(f"Data check: mean elevation in this window is {row['d_elev_mean_m']:.0f} m. The published InSight "
               "landing elevation is -2,613 m relative to the MOLA geoid (Golombek et al., 2020), which confirms "
               "the Mars DEM values are in metres.")
