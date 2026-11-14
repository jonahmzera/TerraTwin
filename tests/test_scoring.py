"""Similarity scoring rules."""

import math

import numpy as np
import pandas as pd
import pytest

from config.study_locations import TARGETS
from modules.environmental_analysis import aridity_score
from modules.geological_analysis import geology_match
from modules.similarity_scoring import combine, monte_carlo, terrain_ranges, variable_table

TERRAIN = {"relief_m": 200.0, "slope_mean_deg": 0.3, "roughness_tri_m": 0.7, "hypsometric_integral": 0.5,
           "flat_pct": 100.0, "slope_p95_deg": 0.6}


def target_row():
    return {f"d_{k}": v for k, v in TERRAIN.items()}


def earth_frame():
    rng = np.random.default_rng(0)
    return pd.DataFrame({
        "relief_m": rng.uniform(50, 3000, 40), "slope_mean_deg": rng.uniform(0.2, 20, 40),
        "roughness_tri_m": rng.uniform(0.5, 40, 40), "hypsometric_integral": rng.uniform(0.1, 0.8, 40),
        "flat_pct": rng.uniform(0, 100, 40), "slope_p95_deg": rng.uniform(0.5, 40, 40),
    })


def test_identical_terrain_scores_100():
    site = {**TERRAIN, "power_T2M": -60, "power_T2M_RANGE": 75, "precip_mm_yr": 0.0, "geo_lith": "basalt"}
    t = variable_table(site, target_row(), TARGETS["mars_insight"], terrain_ranges(earth_frame()))
    assert (t["similarity"] == 100).all()


def test_missing_values_lower_coverage_not_score():
    site = {**TERRAIN}  # no climate, no geology
    t = variable_table(site, target_row(), TARGETS["mars_insight"], terrain_ranges(earth_frame()))
    dims, overall, coverage = combine(t, {"terrain": 25, "operations": 25, "geology": 25, "environment": 25})
    assert overall == pytest.approx(100)
    assert coverage == pytest.approx(50)
    assert "geology" not in dims


def test_further_is_less_similar():
    ranges = terrain_ranges(earth_frame())
    near = variable_table({**TERRAIN, "relief_m": 250.0}, target_row(), TARGETS["mars_insight"], ranges)
    far = variable_table({**TERRAIN, "relief_m": 2500.0}, target_row(), TARGETS["mars_insight"], ranges)
    get = lambda t: t.set_index("key").loc["relief_m", "similarity"]  # noqa: E731
    assert get(near) > get(far)


def test_uncertainty_band_contains_score():
    site = {**TERRAIN, "relief_m": 900.0, "power_T2M": 20, "power_T2M_RANGE": 12, "precip_mm_yr": 300.0,
            "geo_lith": "volcanic"}
    weights = {"terrain": 25, "operations": 25, "geology": 25, "environment": 25}
    t = variable_table(site, target_row(), TARGETS["mars_insight"], terrain_ranges(earth_frame()))
    _, overall, _ = combine(t, weights)
    p5, p50, p95 = monte_carlo(t, weights, n=400)
    assert p5 <= overall <= p95
    assert p5 < p95


def test_aridity_scale():
    assert aridity_score(0) == 100
    assert aridity_score(10) == pytest.approx(66.7, abs=0.1)
    assert aridity_score(5000) == 0
    assert aridity_score(None) is None


def test_geology_match_levels():
    t = TARGETS["moon_imbrium"]
    assert geology_match({"geo_lith": "basalt; olivine"}, t)[0] == 100
    assert geology_match({"geo_lith": "volcanic"}, t)[0] == 60
    assert geology_match({"geo_lith": "granite"}, t)[0] == 0
    score, _ = geology_match({}, t)
    assert score is None or (isinstance(score, float) and math.isnan(score))
    # Rows read back from CSV hold NaN (a float) where there is no geology
    score, _ = geology_match({"geo_units": float("nan"), "geo_lith": float("nan")}, t)
    assert score is None


def test_geology_majority_vote_across_maps():
    # Craters of the Moon case: one map shows bedrock granite, two show the young basalt on top.
    units = ('[{"name": "Granite and gneiss", "lith": "gneiss, granite"},'
             ' {"name": "Basalt", "lith": "basalt, latite"}, {"name": "Basalt (Quaternary)", "lith": "basalt"}]')
    score, note = geology_match({"geo_units": units}, TARGETS["moon_imbrium"])
    assert score == 100
    assert "2 of 3" in note
