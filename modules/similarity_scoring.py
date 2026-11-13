"""Shared similarity scoring for TerraTwin.

Used by both the Comparison Lab and the Reports page, so the two always
show the same numbers.

Per variable:
    similarity = 100 * max(0, 1 - |earth - planet| / R)
where R is the provisional comparison range from config/weights.py.

Missing values are never treated as zero: a variable with missing data gets
no similarity and is left out of the overall score.
"""

import pandas as pd


def score_variables(earth, planet, variables, weights=None,
                    earth_label="Earth site", planet_label="Planetary site"):
    """Compare two rows of measurements variable by variable.

    earth, planet: pandas Series (one row each from the measurements CSV).
    variables: dict like TOPOGRAPHY_VARIABLES in config/weights.py.
    weights: optional {variable_key: raw weight}. Defaults to each
        variable's "default_weight". Weights are rescaled to add up to 100%.

    Returns (table, overall). overall is None when no variable can be scored
    or all weights are zero.
    """
    if weights is None:
        weights = {key: cfg["default_weight"] for key, cfg in variables.items()}
    total = sum(weights.values())

    rows = []
    weighted_sum = 0.0  # uses unrounded similarities, so rounding never shifts the overall score
    used_weight = 0.0
    for key, cfg in variables.items():
        e, p = earth[key], planet[key]
        if pd.isna(e) or pd.isna(p):
            difference = None
            similarity = None
        else:
            difference = abs(e - p)
            raw_similarity = 100 * max(0.0, 1 - difference / cfg["range"])
            similarity = round(raw_similarity, 1)
            weighted_sum += raw_similarity * weights[key]
            used_weight += weights[key]
        rows.append(
            {
                "Variable": cfg["label"],
                earth_label: e,
                planet_label: p,
                "Difference": None if difference is None else round(difference, 2),
                "Range R": cfg["range"],
                "Similarity (0-100)": similarity,
                "Weight (%)": round(100 * weights[key] / total, 1) if total else 0.0,
            }
        )

    table = pd.DataFrame(rows)
    overall = weighted_sum / used_weight if used_weight else None
    return table, overall
