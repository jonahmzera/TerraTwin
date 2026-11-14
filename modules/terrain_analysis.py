"""Terrain measurements from an elevation grid.

All functions take a 2-D float array of elevations in metres (NaN = no data) on a
square grid with pixel size `res_m`. Earth, Moon and Mars grids are all brought to the
same pixel size before measuring, because slope and roughness depend on scale.

Methods
- Slope: Horn (1981) 3x3 finite differences, as used by GDAL and ArcGIS.
  Horn, B. K. P. (1981). Hill shading and the reflectance map. Proc. IEEE 69(1), 14-47.
- Roughness (TRI): mean absolute elevation difference between a pixel and its 8 neighbours,
  the "Wilson" variant used by GDAL. Wilson, M. F. J. et al. (2007). Marine Geodesy 30, 3-35.
- Hypsometric integral: (mean - min) / (max - min). Strahler, A. N. (1952). GSA Bulletin 63.
"""

import numpy as np

METRIC_INFO = {
    "relief_m": "Local relief: highest minus lowest point (m)",
    "relief_robust_m": "Robust relief: 99th minus 1st percentile of elevation (m)",
    "slope_mean_deg": "Mean slope (degrees)",
    "slope_p95_deg": "95th-percentile slope (degrees); robust to single extreme pixels",
    "slope_max_deg": "Maximum slope (degrees); can come from one pixel",
    "roughness_tri_m": "Terrain ruggedness, TRI (m)",
    "flat_pct": "Share of the area flatter than 5 degrees (%)",
    "hypsometric_integral": "Hypsometric integral (0-1): low = mostly lowland with a few peaks",
}


def _neighbours(z):
    """Return the 8 neighbour arrays of z. The border is padded with NaN, so edge pixels
    (which lack a full 3x3 neighbourhood) are excluded instead of biased."""
    p = np.pad(z.astype("float64"), 1, mode="constant", constant_values=np.nan)
    h, w = z.shape
    return {
        "a": p[0:h, 0:w], "b": p[0:h, 1:w + 1], "c": p[0:h, 2:w + 2],
        "d": p[1:h + 1, 0:w], "f": p[1:h + 1, 2:w + 2],
        "g": p[2:h + 2, 0:w], "h": p[2:h + 2, 1:w + 1], "i": p[2:h + 2, 2:w + 2],
    }


def slope_degrees(z, res_m):
    """Horn (1981) slope in degrees. Pixels next to no-data become NaN."""
    n = _neighbours(z)
    dzdx = ((n["c"] + 2 * n["f"] + n["i"]) - (n["a"] + 2 * n["d"] + n["g"])) / (8 * res_m)
    dzdy = ((n["g"] + 2 * n["h"] + n["i"]) - (n["a"] + 2 * n["b"] + n["c"])) / (8 * res_m)
    return np.degrees(np.arctan(np.hypot(dzdx, dzdy)))


def tri_wilson(z):
    """Mean absolute difference to the 8 neighbours (TRI, Wilson et al. 2007)."""
    n = _neighbours(z)
    diffs = np.stack([np.abs(v - z) for v in n.values()])
    return diffs.mean(axis=0)


def compute_metrics(z, res_m, flat_slope_deg=5.0):
    """Measure a grid. Returns a dict of metrics (NaN where they cannot be computed)."""
    z = np.asarray(z, dtype="float64")
    valid = np.isfinite(z)
    valid_pct = 100.0 * valid.mean() if z.size else 0.0
    out = {k: np.nan for k in METRIC_INFO}
    out["valid_pct"] = round(valid_pct, 1)
    if valid.sum() < 100:
        return out

    zv = z[valid]
    slope = slope_degrees(z, res_m)
    tri = tri_wilson(z)
    s = slope[np.isfinite(slope)]
    t = tri[np.isfinite(tri)]

    zmin, zmax = zv.min(), zv.max()
    out.update(
        elev_min_m=round(float(zmin), 1),
        elev_max_m=round(float(zmax), 1),
        elev_mean_m=round(float(zv.mean()), 1),
        relief_m=round(float(zmax - zmin), 1),
        relief_robust_m=round(float(np.percentile(zv, 99) - np.percentile(zv, 1)), 1),
        hypsometric_integral=round(float((zv.mean() - zmin) / (zmax - zmin)), 3) if zmax > zmin else np.nan,
    )
    if s.size:
        out.update(
            slope_mean_deg=round(float(s.mean()), 2),
            slope_p95_deg=round(float(np.percentile(s, 95)), 2),
            slope_max_deg=round(float(s.max()), 2),
            flat_pct=round(float(100.0 * (s < flat_slope_deg).mean()), 1),
        )
    if t.size:
        out["roughness_tri_m"] = round(float(t.mean()), 2)
    return out


def block_average(z, factor):
    """Average non-overlapping factor x factor blocks, ignoring NaN (coarsens the grid)."""
    if factor <= 1:
        return z
    h, w = (z.shape[0] // factor) * factor, (z.shape[1] // factor) * factor
    blocks = z[:h, :w].reshape(h // factor, factor, w // factor, factor)
    with np.errstate(invalid="ignore"):
        counts = np.isfinite(blocks).sum(axis=(1, 3))
        sums = np.nansum(blocks, axis=(1, 3))
        out = sums / np.where(counts == 0, np.nan, counts)
    out[counts < (factor * factor) / 2] = np.nan  # mostly-empty blocks become no-data
    return out


def hillshade(z, res_m, azimuth=315.0, altitude=45.0):
    """Simple hillshade (0-1) for display only."""
    n = _neighbours(z)
    dzdx = ((n["c"] + 2 * n["f"] + n["i"]) - (n["a"] + 2 * n["d"] + n["g"])) / (8 * res_m)
    dzdy = ((n["g"] + 2 * n["h"] + n["i"]) - (n["a"] + 2 * n["b"] + n["c"])) / (8 * res_m)
    slope = np.arctan(np.hypot(dzdx, dzdy))
    aspect = np.arctan2(dzdy, -dzdx)
    az, alt = np.radians(360.0 - azimuth + 90.0), np.radians(altitude)
    shade = np.sin(alt) * np.cos(slope) + np.cos(alt) * np.sin(slope) * np.cos(az - aspect)
    return np.clip(shade, 0, 1)
