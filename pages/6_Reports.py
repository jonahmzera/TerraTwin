import streamlit as st

from config.study_locations import TARGETS
from modules.comparison_engine import compare, load_earth_sites, load_targets, ranking, require, site_label
from modules.report_generator import build_report
from modules.similarity_scoring import DEFAULT_WEIGHTS

st.set_page_config(page_title="TerraTwin | Reports", page_icon="📄", layout="wide")

st.title("📄 Reports")
st.write("Download a self-contained report for any Earth site and target: scores, uncertainty, where the "
         "analogy holds and breaks, method, limitations and data sources.")

sites, targets = load_earth_sites(), load_targets()
require(sites, targets)

c1, c2 = st.columns(2)
target_key = c1.selectbox("Moon or Mars target", list(TARGETS), format_func=lambda k: TARGETS[k]["name"])
ranked = ranking(target_key)
site_key = c2.selectbox("Earth site (best match first)", ranked["key"],
                        format_func=lambda k: site_label(ranked.set_index("key").loc[k]))

site = sites.set_index("key").loc[site_key].to_dict()
site["key"] = site_key
result = compare(site_key, target_key)
report = build_report(site, target_key, result, ranked, DEFAULT_WEIGHTS)

st.caption("Reports use equal default weights so every download is reproducible.")
with st.container(horizontal=True):
    st.download_button("Download report (Markdown)", report, file_name=f"terratwin_{site_key}_vs_{target_key}.md",
                       mime="text/markdown", icon=":material/description:", type="primary")
    st.download_button("Download variables (CSV)", result["table"].to_csv(index=False),
                       file_name=f"terratwin_{site_key}_vs_{target_key}_variables.csv", mime="text/csv",
                       icon=":material/table:")
    st.download_button("Download full ranking (CSV)", ranked.to_csv(index=False),
                       file_name=f"terratwin_ranking_{target_key}.csv", mime="text/csv",
                       icon=":material/leaderboard:")

with st.container(border=True):
    st.markdown(report)
