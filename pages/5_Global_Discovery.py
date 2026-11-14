import streamlit as st

from config.study_locations import TARGETS
from modules.comparison_engine import (load_candidates, load_earth_sites, load_screen, load_targets, ranking,
                                       require, screen_scores)
from modules.mapping import GROUP_LABELS, screen_map

st.set_page_config(page_title="TerraTwin | Global Discovery", page_icon="🔭", layout="wide")

st.title("🔭 Global Discovery")
st.write("Stage 1 scores every land cell on Earth for terrain similarity to a target. Stage 2 re-measures the "
         "best, spread-out candidates in detail and ranks them alongside well-known analogue sites.")

cells, targets, sites, cands = load_screen(), load_targets(), load_earth_sites(), load_candidates()
require(cells, targets, sites, cands)

target_key = st.selectbox("Moon or Mars target", list(TARGETS), format_func=lambda k: TARGETS[k]["name"])
scored = screen_scores(target_key)

# ---- Stage 1 map ----
st.subheader("Stage 1: terrain similarity across Earth")
c = cands[cands["target"] == target_key].merge(sites[["key", "name", "country"]], on="key", how="left")
c = c.assign(label=c["name"].fillna("") + " (screen score " + c["screen_score"].round(0).astype(int).astype(str) + ")")
st.plotly_chart(screen_map(scored, highlight=c), alt="Global map of terrain similarity to the selected target")
q = scored["score"].quantile([0.5, 0.9, 0.99])
st.caption(f"{len(scored):,} land cells of about 78 km, measured at about 1.2 km pixels. Median score "
           f"{q[0.5]:.0f}, top 10% above {q[0.9]:.0f}, top 1% above {q[0.99]:.0f}. Stars mark the cells "
           "re-measured in stage 2: six outside the ice sheets (at least 500 km apart and away from known "
           "analogue sites) and two ice-sheet lookalikes.")
st.info("Terrain alone can mislead. For the InSight lava plain, the best terrain matches on Earth are the "
        "Antarctic ice sheets: smooth, flat and genuinely Mars-cold. Only the rock-type dimension shows they "
        "are ice, not basalt (geology score 0). They could be good analogues for icy Martian plains, but not "
        "for InSight's lava. That is why TerraTwin scores four dimensions and shows each one.",
        title="Why one dimension is not enough")

# ---- Stage 2 ranking ----
st.subheader("Stage 2: ranked Earth sites")
r = ranking(target_key)
r = r.assign(Group=r["group"].map(GROUP_LABELS))
st.dataframe(
    r[["rank", "name", "country", "Group", "overall", "p5", "p95", "dim_terrain", "dim_operations",
       "dim_geology", "dim_environment", "coverage_pct"]],
    hide_index=True,
    column_config={
        "rank": st.column_config.NumberColumn("Rank", width="small"),
        "name": "Site", "country": "Country",
        "overall": st.column_config.ProgressColumn("Overall", min_value=0, max_value=100, format="%.0f"),
        "p5": st.column_config.NumberColumn("Low (p5)", format="%.0f"),
        "p95": st.column_config.NumberColumn("High (p95)", format="%.0f"),
        "dim_terrain": st.column_config.NumberColumn("Terrain", format="%.0f"),
        "dim_operations": st.column_config.NumberColumn("Landing/mobility", format="%.0f"),
        "dim_geology": st.column_config.NumberColumn("Geology", format="%.0f"),
        "dim_environment": st.column_config.NumberColumn("Climate", format="%.0f"),
        "coverage_pct": st.column_config.NumberColumn("Coverage %", format="%.0f"),
    },
    alt="Ranking of characterised Earth sites for the selected target",
)

known = r[r["group"] == "known"]
new = r[r["group"].isin(["team", "discovered"])]
overlap = (new["p95"] >= known["overall"].max()).sum() if len(known) else 0
c1, c2, c3 = st.columns(3)
c1.metric("Best known analogue", f"#{int(known['rank'].min())}" if len(known) else "-",
          help="Validation: well-known analogue sites should rank reasonably well.")
c2.metric("Median rank of known analogues", f"{known['rank'].median():.0f} of {len(r)}" if len(known) else "-")
c3.metric("New or team sites that could beat the best known one", f"{overlap}",
          help="Sites whose upper uncertainty bound reaches the best known analogue's score.")

st.download_button("Download this ranking (CSV)", r.drop(columns=["Group"]).to_csv(index=False),
                   file_name=f"terratwin_ranking_{target_key}.csv", mime="text/csv", icon=":material/table:")
