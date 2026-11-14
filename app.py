"""
TerraTwin: Planetary Analogue Discovery System
Aether Labs | NASA Space Apps Challenge 2026

Main entry point:  python -m streamlit run app.py
"""

import pandas as pd
import streamlit as st

from config.study_locations import TARGETS
from modules.comparison_engine import (load_earth_sites, load_screen, load_targets, ranking, require,
                                       site_label)

VERSION = "1.0.0"

st.set_page_config(page_title="TerraTwin", page_icon="🌍", layout="wide")

st.title("🌍 TerraTwin")
st.caption(f"Aether Labs | NASA Space Apps Challenge 2026 | v{VERSION}")
st.markdown(
    "**Searching the whole Earth for places that can help us explore the Moon and Mars.** "
    "TerraTwin compares Earth with real landing sites and candidate base locations on the Moon and Mars, "
    "using open NASA and partner-agency data. It reports how similar a place is in each dimension, where the "
    "analogy breaks down, and how confident we are."
)

targets, sites, cells = load_targets(), load_earth_sites(), load_screen()
require(targets, sites, cells)

# ---- The funnel ----
st.subheader("How it works")
c1, c2, c3, c4 = st.columns(4)
c1.metric("Land cells screened", f"{len(cells):,}", help="Stage 1: all of Earth's land at ~1.2 km pixels, ~78 km cells")
c2.metric("Earth sites characterised", f"{len(sites)}", help="Stage 2: measured at 200 m, with climate and geology")
c3.metric("Moon and Mars targets", f"{len(targets)}", help="Real landing sites and candidate base regions")
c4.metric("Analogue dimensions", "4", help="Terrain, landing and mobility, geology, climate")

st.markdown(
    "1. **Measure the targets.** Terrain at five Moon and Mars sites (InSight, Perseverance, Chang'e 3, "
    "Marius Hills, lunar south pole) from MOLA/HRSC and LOLA elevation data.\n"
    "2. **Screen all of Earth.** Every land cell is scored for terrain similarity to each target, with the same "
    "method and pixel size.\n"
    "3. **Characterise the best candidates** at 200 m, adding NASA POWER climate and Macrostrat geology. "
    "Well-known analogue sites are scored the same way, as a check that the method works.\n"
    "4. **Explain the result.** For every pair: scores by dimension, an uncertainty band, where the analogy "
    "holds, where it breaks down, and what Earth cannot reproduce."
)

# ---- Headline findings ----
st.subheader("Headline findings")
st.caption("Best site per target among the characterised Earth sites, with default (equal) weights. "
           "Open Global Discovery for the full rankings.")
for key, t in TARGETS.items():
    r = ranking(key)
    top = r.iloc[0]
    new = r[r["group"].isin(["team", "discovered"])].iloc[0]
    known_rank = r[r["group"] == "known"]["rank"].min()
    with st.container(border=True):
        a, b, c = st.columns([2, 3, 3])
        a.markdown(f"**{t['short']}**")
        a.caption(t["name"])
        b.metric("Best site overall", site_label(top), f"{top['overall']:.0f} / 100", delta_color="off",
                 delta_arrow="off")
        c.metric("Best new or team site", site_label(new),
                 f"{new['overall']:.0f} / 100 (band {new['p5']:.0f}-{new['p95']:.0f})", delta_color="off",
                 delta_arrow="off")
        st.caption(f"Best-placed well-known analogue ranks #{int(known_rank)} of {len(r)}.")

st.info(
    "Scores show closeness on measured variables, relative to how much Earth itself varies. They are not proof "
    "that two places are equivalent. No Earth site reproduces lunar or Martian gravity, vacuum or radiation.",
    title="How to read the scores",
)
