"""Build a Markdown report for one Earth site vs one planetary target."""

from datetime import date

import pandas as pd

from config.settings import SOURCES
from config.study_locations import EARTH_LIMITS, TARGETS
from modules.similarity_scoring import DIMENSIONS, holds_and_breaks


def _f(v, nd=1):
    if v is None or (isinstance(v, float) and pd.isna(v)):
        return "missing"
    if isinstance(v, (int, float)):
        return f"{v:,.{nd}f}"
    return str(v)


def build_report(site, target_key, result, ranking_df, weights):
    t = TARGETS[target_key]
    table = result["table"]
    holds, breaks = holds_and_breaks(table)
    rank_row = ranking_df[ranking_df["key"] == site["key"]]
    rank_text = (f"{int(rank_row['rank'].iloc[0])} of {len(ranking_df)} characterised Earth sites"
                 if len(rank_row) else "not ranked")

    L = [
        f"# TerraTwin analogue report: {site['name']} vs {t['name']}",
        "Aether Labs | NASA Space Apps Challenge 2026",
        f"Generated {date.today().isoformat()} from the TerraTwin pipeline outputs.",
        "",
        "## Summary",
        f"- **Earth site:** {site['name']}{', ' + site['country'] if isinstance(site.get('country'), str) else ''} "
        f"({site['lat']:.3f}, {site['lon']:.3f}); group: {site['group']}.",
        f"- **Target:** {t['name']} ({t['body']}, {t['lat']}, {t['lon']}). {t['why']}",
        f"- **Overall analogue score:** {_f(result['overall'])} / 100 "
        f"(uncertainty band {_f(result['p5'])} to {_f(result['p95'])}), "
        f"data coverage {_f(result['coverage'], 0)}% of the weighted dimensions.",
        f"- **Rank for this target:** {rank_text}.",
        "",
        "The score measures how closely this site matches the target on the measured variables, relative to "
        "how much Earth itself varies. It is not proof of equivalence.",
        "",
        "## Scores by dimension",
        "| Dimension | Score (0-100) | Weight |",
        "|---|---|---|",
    ]
    for d, label in DIMENSIONS.items():
        L.append(f"| {label} | {_f(result['dims'].get(d))} | {weights.get(d, 0)} |")
    L += ["", "## Where the analogy holds"]
    L += [f"- {h}" for h in holds] or ["- No variable reached a similarity of 70."]
    L += ["", "## Where the analogy breaks down"]
    L += [f"- {b}" for b in breaks] or ["- No measured variable fell below a similarity of 40."]
    L += [f"- {x}" for x in EARTH_LIMITS[t["body"]]]
    L += ["", "## All measured variables",
          "| Dimension | Variable | Earth | Target | Similarity |", "|---|---|---|---|---|"]
    for _, r in table.iterrows():
        tgt = r["target"] if not isinstance(r["target"], str) else "see geology summary"
        L.append(f"| {r['dimension']} | {r['variable']} | {_f(r['earth'], 2)} | {_f(tgt, 2)} | {_f(r['similarity'])} |")
    L += [
        "",
        "## Site context",
        f"- Notes: {site.get('notes') or '-'}",
        f"- Mapped geology (Macrostrat): {site.get('geo_name') or 'none'}; rock types: {site.get('geo_lith') or 'none'}; "
        f"age: {site.get('geo_age') or 'unknown'}.",
        f"- Target geology: {t['geology_summary']}",
        f"- Target environment: {t['environment']['source']}",
        "",
        "## How this site could help exploration",
    ]
    L += [f"- {u}" for u in t["exploration_use"]]
    L += [
        "",
        "## Method",
        "Terrain was measured in a 50 km square window at 200 m pixels for both bodies (Earth: Copernicus GLO-30 "
        "averaged to 200 m; Mars: MOLA/HRSC 200 m; Moon: LOLA 118 m averaged to 200 m), on a local azimuthal "
        "equidistant grid. Slope: Horn (1981). Ruggedness: TRI (Wilson et al., 2007). Per-variable similarity = "
        "100 x max(0, 1 - |Earth - target| / R), with R the 5th-95th percentile spread of that variable across the "
        "characterised Earth sites (log scale for relief, slope and ruggedness). Climate: NASA POWER long-term means "
        "at the site centre, compared with literature values for the target. Geology: keyword match between "
        "Macrostrat rock types and the target's expected rock types. Uncertainty: 5th-95th percentile of the overall "
        "score over random weights and comparison ranges.",
        "",
        "## Limitations",
        "- Windows are 50 km boxes around a centre point; a smaller area inside could match better or worse.",
        "- Earth elevation is a surface model (DSM), so forests and buildings add roughness.",
        "- Moon and Mars climate values are rounded literature values, not measurements at the exact site.",
        "- The geology match uses map keywords only; it is not a mineralogical comparison.",
        "- Vegetation, dust, ice and subsurface conditions are described in notes but not yet scored.",
        "",
        "## Data sources",
    ]
    L += [f"- {s['name']}: {s['citation']}" for s in SOURCES.values()]
    return "\n".join(L)
