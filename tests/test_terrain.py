"""Terrain measurements on synthetic surfaces with known answers."""

import math

import numpy as np
import pytest

from modules.terrain_analysis import block_average, compute_metrics, slope_degrees, tri_wilson


def plane(slope_deg, n=60, res=200.0):
    x = np.arange(n) * res
    return np.tile(x * math.tan(math.radians(slope_deg)), (n, 1))


@pytest.mark.parametrize("deg", [0.0, 5.0, 20.0, 45.0])
def test_slope_of_tilted_plane(deg):
    s = slope_degrees(plane(deg), 200.0)[1:-1, 1:-1]  # edges are padded, skip them
    assert np.allclose(s, deg, atol=1e-6)


def test_flat_surface_has_zero_roughness_and_full_flat_area():
    m = compute_metrics(np.full((50, 50), 100.0), 200.0)
    assert m["relief_m"] == 0
    assert m["roughness_tri_m"] == 0
    assert m["flat_pct"] == 100.0


def test_tri_of_single_spike():
    z = np.zeros((5, 5))
    z[2, 2] = 8.0
    assert tri_wilson(z)[2, 2] == pytest.approx(8.0)


def test_missing_data_is_ignored_not_zero():
    z = plane(10.0)
    z[:10, :10] = np.nan
    m = compute_metrics(z, 200.0)
    assert m["valid_pct"] < 100
    assert m["elev_min_m"] >= 0  # NaN was not turned into 0 m or a fake low value
    assert m["slope_mean_deg"] == pytest.approx(10.0, abs=0.05)


def test_too_little_data_returns_nan():
    z = np.full((50, 50), np.nan)
    z[0, :5] = 1.0
    assert math.isnan(compute_metrics(z, 200.0)["relief_m"])


def test_block_average_keeps_mean_and_ignores_nan():
    z = np.arange(16, dtype=float).reshape(4, 4)
    out = block_average(z, 2)
    assert out.shape == (2, 2)
    assert out[0, 0] == pytest.approx(np.mean([0, 1, 4, 5]))
    z[0, 0] = np.nan
    assert block_average(z, 2)[0, 0] == pytest.approx(np.mean([1, 4, 5]))
