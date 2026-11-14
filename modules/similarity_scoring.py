"""Multi-dimensional analogue scoring with uncertainty.

Per variable:
    similarity = 100 * max(0, 1 - |earth - target| / R)

- Scale-dependent terrain variables (relief, slope, roughness) are compared on a log10
  scale, so "130 m vs 150 m" and "1300 m vs 1500 m" count as equally close.
- R (the comparison range) is not hand-picked: it is the spread (5th to 95th percentile)
  of that variable across the Earth sites being compared. So "similar" means "close,
  relative to how much Earth itself varies".
- Variables are grouped into dimensions (terrain, operations, geology, environment).
  A dimension score is the mean of its variables; the overall score is the weighted mean
  of the dimensions that have data. Missing data is never treated as zero; it lowers
  the reported coverage instead.
- Uncertainty: the score is recomputed many times with randomly varied weights
  (Dirichlet around the chosen weights) and ranges (R x 0.67 to x 1.5, log-uniform).
  The 5th-95th percentile band is reported with every score.
"""

import math

import numpy as np
import pandas as pd

from modules.environmental_analysis import aridity_score
from modules.geological_analysis import geology_match

# key: (label, dimension, log-transform offset or None for linear)
TERRAIN_VARIABLES = {
    "relief_m": ("Local relief (m)", "terrain", 1.0),
    "slope_mean_deg": ("Mean slope (deg)", "terrain", 0.1),
    "roughness_tri_m": ("Ruggedness, TRI (m)", "terrain", 0.1),
    "hypsometric_integral": ("Hypsometric integral", "terrain", None),
    "flat_pct": ("Area flatter than 5 deg (%)", "operations", None),
    "slope_p95_deg": ("95th-percentile slope (deg)", "operations", 0.1),
}

DIMENSIONS = {
    "terrain": "Terrain and topography",
    "operations": "Landing and mobility",
    "geology": "Geology and surface materials",
    "environment": "Climate and environment",
}
DEFAULT_WEIGHTS = {"terrain": 25, "operations": 25, "geology": 25, "environment": 25}

ENV_VARIABLES = {
    "env_temperature": ("Mean temperature (degC)", 100.0),
    "env_daily_range": ("Daily temperature range (degC)", 100.0),
    "env_aridity": ("Aridity (0-100)", 100.0),
}


def _transform(values, offset):
    v = np.asarray(values, dtype="float64")
    if offset is None:
        return v
    with np.errstate(invalid="ignore", divide="ignore"):
        return np.log10(np.clip(v, 0, None) + offset)


def terrain_ranges(earth_df, prefix=""):
    """Comparison range R per terrain variable: 5th-95th percentile spread across Earth."""
    ranges = {}
    for key, (_, _, offset) in TERRAIN_VARIABLES.items():
        col = prefix + key
        if col not in earth_df:
            continue
        v = _transform(earth_df[col].dropna(), offset)
        r = float(np.nanpercentile(v, 95) - np.nanpercentile(v, 5)) if len(v) else np.nan
        ranges[key] = r if r and r > 1e-6 else 1.0
    return ranges


def _sim(earth_t, target_t, r):
    with np.errstate(invalid="ignore"):
        return 100 * np.clip(1 - np.abs(earth_t - target_t) / r, 0, 1)


def screen_similarity(cells, target_row, reference_cells):
    """Stage-1 terrain score for every global cell vs one target (1.2 km metrics, equal weights)."""
    ranges = terrain_ranges(reference_cells)
    sims = []
    for key, (_, _, offset) in TERRAIN_VARIABLES.items():
        t = target_row.get(f"s_{key}")
        if t is None or (isinstance(t, float) and math.isnan(t)):
            continue
        sims.append(_sim(_transform(cells[key], offset), _transform([t], offset)[0], ranges[key]))
    return np.nanmean(np.vstack(sims), axis=0)


def variable_table(site, target_row, target_cfg, ranges):
    """Every compared variable for one Earth site vs one target, with its similarity."""
    rows = []
    for key, (label, dim, offset) in TERRAIN_VARIABLES.items():
        e, t = site.get(key), target_row.get(f"d_{key}")
        ok = e is not None and t is not None and not (pd.isna(e) or pd.isna(t))
        sim = float(_sim(_transform([e], offset)[0], _transform([t], offset)[0], ranges[key])) if ok else None
        rows.append({"dimension": dim, "key": key, "variable": label, "earth": e, "target": t, "similarity": sim,
                     "range_R": ranges[key], "scale": "log10" if offset is not None else "linear"})

    g_score, g_note = geology_match(site, target_cfg)
    rows.append({"dimension": "geology", "key": "geology_match", "variable": "Rock types (Macrostrat)",
                 "earth": site.get("geo_lith") or site.get("geo_name"), "target": target_cfg["geology_summary"],
                 "similarity": g_score, "range_R": None, "scale": g_note})

    env = target_cfg["environment"]
    earth_env = {
        "env_temperature": site.get("power_T2M"),
        "env_daily_range": site.get("power_T2M_RANGE"),
        "env_aridity": aridity_score(site.get("precip_mm_yr")),
    }
    target_env = {"env_temperature": env["T2M"], "env_daily_range": env["T2M_RANGE"], "env_aridity": 100.0}
    for key, (label, r) in ENV_VARIABLES.items():
        e, t = earth_env[key], target_env[key]
        ok = e is not None and not pd.isna(e)
        sim = float(_sim(np.float64(e), np.float64(t), r)) if ok else None
        rows.append({"dimension": "environment", "key": key, "variable": label, "earth": e, "target": t,
                     "similarity": sim, "range_R": r, "scale": "linear"})
    return pd.DataFrame(rows)


def combine(table, weights):
    """Dimension scores and the overall weighted score from a variable table."""
    dims = table.dropna(subset=["similarity"]).groupby("dimension")["similarity"].mean()
    used = {d: w for d, w in weights.items() if d in dims.index and w > 0}
    total = sum(used.values())
    overall = sum(dims[d] * w for d, w in used.items()) / total if total else None
    coverage = 100 * sum(used.values()) / sum(w for w in weights.values() if w > 0) if total else 0.0
    return dims.to_dict(), overall, coverage


def monte_carlo(table, weights, n=500, seed=42):
    """Overall-score band from random weights and comparison ranges. Returns (p5, p50, p95)."""
    rng = np.random.default_rng(seed)
    t = table.dropna(subset=["similarity"])
    dims = [d for d in weights if weights[d] > 0 and d in set(t["dimension"])]
    if not dims:
        return None, None, None
    w0 = np.array([weights[d] for d in dims], dtype=float)
    draws = rng.dirichlet(4 * w0 / w0.sum() * len(dims), size=n)
    # Range perturbation: similarity s = 1 - d/R  ->  with R*k: 1 - (1 - s)/k   (vectorised over draws)
    dim_scores = np.empty((n, len(dims)))
    for j, d in enumerate(dims):
        s = t.loc[t["dimension"] == d, "similarity"].to_numpy(dtype=float) / 100
        if d in ("terrain", "operations", "environment"):
            k = np.exp(rng.uniform(np.log(0.67), np.log(1.5), size=(n, s.size)))
            dim_scores[:, j] = np.clip(1 - (1 - s) / k, 0, 1).mean(axis=1)
        else:
            dim_scores[:, j] = s.mean()
    out = 100 * (draws * dim_scores).sum(axis=1)
    return tuple(float(np.percentile(out, q)) for q in (5, 50, 95))


def score_site(site, target_row, target_cfg, ranges, weights=None, n_draws=300):
    weights = weights or DEFAULT_WEIGHTS
    table = variable_table(site, target_row, target_cfg, ranges)
    dims, overall, coverage = combine(table, weights)
    p5, _, p95 = monte_carlo(table, weights, n=n_draws)
    return {"table": table, "dims": dims, "overall": overall, "coverage": coverage, "p5": p5, "p95": p95}


def rank_sites(sites_df, target_row, target_cfg, weights=None, n_draws=200):
    """Score every Earth site against one target. Returns a ranked DataFrame."""
    ranges = terrain_ranges(sites_df)
    rows = []
    for _, s in sites_df.iterrows():
        r = score_site(s.to_dict(), target_row, target_cfg, ranges, weights, n_draws)
        rows.append({"key": s["key"], "name": s["name"], "country": s.get("country"), "group": s["group"],
                     "lat": s["lat"], "lon": s["lon"], "overall": r["overall"], "p5": r["p5"], "p95": r["p95"],
                     "coverage_pct": r["coverage"], **{f"dim_{d}": r["dims"].get(d) for d in DIMENSIONS}})
    out = pd.DataFrame(rows).sort_values("overall", ascending=False, na_position="last").reset_index(drop=True)
    out.insert(0, "rank", range(1, len(out) + 1))
    return out


def holds_and_breaks(table, strong=70, weak=40):
    """Plain-language lists of where the analogy holds and where it breaks down."""
    holds, breaks = [], []
    for _, r in table.dropna(subset=["similarity"]).iterrows():
        e = r["earth"] if isinstance(r["earth"], str) else _fmt(r["earth"])
        t = r["target"] if isinstance(r["target"], str) else _fmt(r["target"])
        if r["key"] == "geology_match":
            line = f"{r['variable']}: {r['scale']} (similarity {r['similarity']:.0f})"
        else:
            line = f"{r['variable']}: Earth {e} vs target {t} (similarity {r['similarity']:.0f})"
        if r["similarity"] >= strong:
            holds.append(line)
        elif r["similarity"] < weak:
            breaks.append(line)
    return holds, breaks


def _fmt(v):
    if v is None or (isinstance(v, float) and math.isnan(v)):
        return "missing"
    return f"{v:,.2f}".rstrip("0").rstrip(".") if isinstance(v, float) else str(v)
