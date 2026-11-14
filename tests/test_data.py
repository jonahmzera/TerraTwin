"""Sanity checks on the pipeline outputs in data/processed (skipped if not generated yet)."""

import pandas as pd
import pytest

from config.settings import PROCESSED_DIR
from config.study_locations import EARTH_SITES, TARGETS


def load(name):
    path = PROCESSED_DIR / name
    if not path.exists():
        pytest.skip(f"{name} not generated yet")
    return pd.read_csv(path)


def test_every_target_measured_with_full_coverage():
    t = load("targets.csv").set_index("key")
    assert set(TARGETS) <= set(t.index)
    assert (t["d_valid_pct"] > 95).all()


def test_insight_elevation_matches_published_landing_elevation():
    # Golombek et al. (2020): InSight landed at -2,613 m relative to the MOLA geoid.
    t = load("targets.csv").set_index("key")
    assert abs(t.loc["mars_insight", "d_elev_mean_m"] - (-2613)) < 100


def test_plausible_terrain_values():
    t = load("targets.csv")
    for col in ["d_slope_mean_deg", "d_slope_p95_deg"]:
        assert t[col].between(0, 60).all()
    e = load("earth_sites.csv")
    assert e["slope_mean_deg"].dropna().between(0, 60).all()


def test_all_configured_earth_sites_present():
    e = load("earth_sites.csv")
    assert set(EARTH_SITES) <= set(e["key"])


def test_global_screen_covers_the_land():
    cells = load("global_screen.csv")
    assert len(cells) > 10_000
    assert cells["lat"].between(-86, 86).all()
    assert cells["lon"].between(-180, 180).all()
