"""Stage 1: screen the whole Earth for terrain that resembles each planetary target.

The Earth is split into ~4,000 Terrain Tiles (zoom 6, Web Mercator). Each tile is cut
into cells of roughly 60-110 km. Every cell is measured at roughly 1.2 km pixels with the
same terrain metrics used for the planetary targets (which are averaged to the same
pixel size). Cells that are mostly sea are skipped.

Web Mercator pixels shrink towards the poles (ground size = 1223 m x cos(latitude)),
so tiles are block-averaged by about 1/cos(latitude) to keep the pixel size close to
1.2 km everywhere. This is a screening step: it is coarse on purpose, and every
promising cell is re-measured at 200 m in stage 2.
"""

import json
import math
from concurrent.futures import ThreadPoolExecutor, as_completed

import numpy as np
import pandas as pd

from config.settings import CACHE_DIR
from modules.data_collection import read_terrain_tile
from modules.terrain_analysis import block_average, compute_metrics

ZOOM = 6
TILE_PX = 512
MERC_PX_M = 2 * math.pi * 6378137 / (2 ** ZOOM * TILE_PX)  # Web Mercator pixel size at the equator
SCREEN_DIR = CACHE_DIR / "screen"


def tile_lat(y, z=ZOOM):
    """Latitude of the top edge of tile row y."""
    n = math.pi - 2 * math.pi * y / 2 ** z
    return math.degrees(math.atan(math.sinh(n)))


def pixel_lat(y, py, z=ZOOM):
    n = math.pi - 2 * math.pi * (y + py / TILE_PX) / 2 ** z
    return math.degrees(math.atan(math.sinh(n)))


def screen_tile(x, y):
    """Measure every land cell of one tile. Results are cached as JSON (resumable)."""
    SCREEN_DIR.mkdir(parents=True, exist_ok=True)
    path = SCREEN_DIR / f"{ZOOM}_{x}_{y}.json"
    if path.exists():
        return json.loads(path.read_text())

    arr, _ = read_terrain_tile(ZOOM, x, y)
    lat_c = (tile_lat(y) + tile_lat(y + 1)) / 2
    cos_lat = math.cos(math.radians(lat_c))
    k = 8 if cos_lat > 0.75 else 4 if cos_lat > 0.375 else 2 if cos_lat > 0.19 else 1
    cell_px = TILE_PX // k
    cells = []
    for i in range(k):
        for j in range(k):
            sub = arr[i * cell_px:(i + 1) * cell_px, j * cell_px:(j + 1) * cell_px].copy()
            land = np.isfinite(sub) & (sub > 0)
            if land.mean() < 0.5:
                continue  # mostly sea
            sub[~land] = np.nan  # pixels at or below sea level are treated as sea
            clat = pixel_lat(y, (i + 0.5) * cell_px)
            ccos = math.cos(math.radians(clat))
            f = max(1, round(1 / ccos))
            res = MERC_PX_M * ccos * f
            m = compute_metrics(block_average(sub, f), res)
            lon = -180 + 360 * (x + (j + 0.5) * cell_px / TILE_PX) / 2 ** ZOOM
            cells.append({"lat": round(clat, 3), "lon": round(lon, 3), "res_m": round(res),
                          "cell_km": round(cell_px * MERC_PX_M * ccos / 1000),
                          "land_pct": round(100 * float(land.mean()), 1),
                          **{key: (None if (isinstance(v, float) and math.isnan(v)) else float(v))
                             for key, v in m.items()}})
    path.write_text(json.dumps(cells))
    return cells


def run_global_screen(workers=16, progress=print):
    """Screen every zoom-6 tile. Returns a DataFrame with one row per land cell."""
    jobs = [(x, y) for y in range(2 ** ZOOM) for x in range(2 ** ZOOM)]
    rows, failed = [], []
    with ThreadPoolExecutor(max_workers=workers) as pool:
        futures = {pool.submit(screen_tile, x, y): (x, y) for x, y in jobs}
        for n, fut in enumerate(as_completed(futures), 1):
            try:
                rows.extend(fut.result())
            except Exception as exc:  # network hiccup: reported, can be re-run (cache resumes)
                failed.append((futures[fut], str(exc)[:120]))
            if n % 200 == 0:
                progress(f"  screened {n}/{len(jobs)} tiles, {len(rows)} land cells, {len(failed)} failed")
    if failed:
        progress(f"  {len(failed)} tiles failed; re-run this step to retry them. First: {failed[0]}")
    return pd.DataFrame(rows)
