import pandas as pd
import streamlit as st

from config.study_locations import EARTH_LIMITS, TARGETS
from modules.comparison_engine import (compare, image_path, load_earth_sites, load_targets, ranking, require,
                                       site_label)
from modules.mapping import GROUP_LABELS
from modules.similarity_scoring import DEFAULT_WEIGHTS, DIMENSIONS, holds_and_breaks

st.set_page_config(page_title="TerraTwin | Comparison Lab", page_icon="🔬", layout="wide")

st.title("🔬 Comparison Lab")
st.write("Compare any Earth site with any Moon or Mars target, dimension by dimension.")

sites, targets = load_earth_sites(), load_targets()
require(sites, targets)

c1, c2 = st.columns(2)
target_key = c1.selectbox("Moon or Mars target", list(TARGETS), format_func=lambda k: TARGETS[k]["name"])
ranked = ranking(target_key)
site_key = c2.selectbox(
    "Earth site (best match first)", ranked["key"],
    format_func=lambda k: f"{site_label(ranked.set_index('key').loc[k])} "
                          f"[{GROUP_LABELS[ranked.set_index('key').loc[k, 'group']]}]",
)

# ---- Weights ----
st.sidebar.header("Dimension weights")
st.sidebar.caption("How much each dimension counts. Rescaled to 100%. Equal weights are the default; "
                   "a landing-site engineer might weight terrain and mobility higher, a geologist geology.")
weights = {d: st.sidebar.slider(label, 0, 100, DEFAULT_WEIGHTS[d]) for d, label in DIMENSIONS.items()}
if sum(weights.values()) == 0:
    st.warning("All weights are zero. Move at least one slider above zero.")
    st.stop()

result = compare(site_key, target_key, tuple(weights.items()))
site = sites.set_index("key").loc[site_key]
t = TARGETS[target_key]

# ---- Headline ----
m1, m2, m3 = st.columns(3)
m1.metric("Overall analogue score", "n/a" if result["overall"] is None else f"{result['overall']:.0f} / 100",
          border=True)
m2.metric("Uncertainty band (5th-95th pct)",
          "n/a" if result["p5"] is None else f"{result['p5']:.0f} to {result['p95']:.0f}", border=True,
          help="Spread of the score when weights and comparison ranges are varied at random (500 runs).")
m3.metric("Data coverage", f"{result['coverage']:.0f}%", border=True,
          help="Share of the weighted dimensions that have data for this site.")

# ---- Side by side ----
a, b = st.columns(2)
with a:
    st.markdown(f"**Earth: {site_label(site)}**")
    img = image_path("earth", site_key)
    if img:
        st.image(str(img), alt=f"Shaded relief of {site['name']}", width="stretch")
with b:
    st.markdown(f"**{t['body']}: {t['name']}**")
    img = image_path("target", target_key)
    if img:
        st.image(str(img), alt=f"Shaded relief of {t['name']}", width="stretch")
st.caption("Both panels show a 50 km x 50 km window at 200 m pixels, at the same scale.")

# ---- Dimension scores ----
st.subheader("Scores by dimension")
dims = pd.DataFrame([{"Dimension": label, "Score": result["dims"].get(d)} for d, label in DIMENSIONS.items()])
st.bar_chart(dims, x="Dimension", y="Score", horizontal=True, y_label="Similarity (0-100)", x_label="",
             sort=False)

holds, breaks = holds_and_breaks(result["table"])
h, br = st.columns(2)
with h:
    st.success("\n".join(f"- {x}" for x in holds) or "No variable reached 70.", title="Where the analogy holds")
with br:
    st.error("\n".join(f"- {x}" for x in breaks + EARTH_LIMITS[t["body"]]), title="Where it breaks down")

st.subheader("All variables")
table = result["table"].copy()
table["earth"] = table["earth"].astype(str)
table["target"] = table["target"].astype(str)
st.dataframe(
    table[["dimension", "variable", "earth", "target", "similarity", "scale"]],
    hide_index=True,
    column_config={
        "similarity": st.column_config.ProgressColumn("Similarity", min_value=0, max_value=100, format="%.0f"),
        "scale": st.column_config.TextColumn("Scale or match"),
    },
    alt="All compared variables with similarity",
)

st.subheader("How this site could help")
st.markdown("\n".join(f"- {u}" for u in t["exploration_use"]))
if isinstance(site.get("notes"), str):
    st.caption(f"Site notes: {site['notes']}")
