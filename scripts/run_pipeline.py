"""TerraTwin data pipeline. Reproduces every number shown in the app.

Run from the project folder, with the virtual environment active:

    python -m scripts.run_pipeline --step all

Steps (each can be run on its own, and downloads are cached in data/cache):
    targets      measure the Moon and Mars target sites (200 m and 1.2 km)
    screen       stage 1: screen all of Earth's land at ~1.2 km
    candidates   pick the most promising, spread-out cells for each target
    earth        stage 2: measure Earth sites at 200 m, add NASA POWER climate and Macrostrat geology
"""

import argparse
import json
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from config.settings import (DETAIL_RES_M, DETAIL_WINDOW_KM, IMAGE_DIR, PROCESSED_DIR,  # noqa: E402
                             SCREEN_WINDOW_KM)
from config.study_locations import EARTH_SITES, TARGETS  # noqa: E402
from modules.terrain_analysis import block_average, compute_metrics, hillshade  # noqa: E402

READ_KM = 80  # targets are read once at 80 km and used for both stages
SCREEN_FACTOR = 6  # 200 m x 6 = 1.2 km


def log(msg):
    print(time.strftime("%H:%M:%S"), msg, flush=True)


def save_hillshade(z, res_m, name):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    IMAGE_DIR.mkdir(parents=True, exist_ok=True)
    fig, ax = plt.subplots(figsize=(4, 4), dpi=100)
    ax.imshow(hillshade(z, res_m), cmap="gray", vmin=0, vmax=1)
    ax.imshow(z, cmap="terrain", alpha=0.35)
    ax.set_axis_off()
    fig.savefig(IMAGE_DIR / f"{name}.png", bbox_inches="tight", pad_inches=0)
    plt.close(fig)


def centre_crop(z, size_px):
    o = (z.shape[0] - size_px) // 2
    return z[o:o + size_px, o:o + size_px]


def step_targets():
    from modules.data_collection import read_planet_window

    rows = []
    for key, t in TARGETS.items():
        log(f"target {key}: reading {READ_KM} km window from {t['dem']}")
        z = read_planet_window(t["dem"], t["body"], t["lat"], t["lon"], READ_KM, DETAIL_RES_M, cache_key=f"target_{key}")
        detail = centre_crop(z, int(DETAIL_WINDOW_KM * 1000 / DETAIL_RES_M))
        d = compute_metrics(detail, DETAIL_RES_M)
        screen_px = int(SCREEN_WINDOW_KM * 1000 / DETAIL_RES_M)
        s = compute_metrics(block_average(centre_crop(z, screen_px), SCREEN_FACTOR), DETAIL_RES_M * SCREEN_FACTOR)
        save_hillshade(detail, DETAIL_RES_M, f"target_{key}")
        rows.append({"key": key, "name": t["name"], "body": t["body"], "lat": t["lat"], "lon": t["lon"],
                     **{f"d_{k}": v for k, v in d.items()}, **{f"s_{k}": v for k, v in s.items()}})
        log(f"  done: relief {d['relief_m']} m, mean slope {d['slope_mean_deg']} deg, valid {d['valid_pct']}%")
    out = pd.DataFrame(rows)
    out.to_csv(PROCESSED_DIR / "targets.csv", index=False)
    log(f"wrote {PROCESSED_DIR / 'targets.csv'}")


def step_screen():
    from modules.global_screening import run_global_screen

    log("global screening: ~4,096 tiles, resumable")
    cells = run_global_screen(progress=log)
    cells.to_csv(PROCESSED_DIR / "global_screen.csv", index=False)
    log(f"wrote {len(cells)} land cells to global_screen.csv")


def on_ice_sheet(lat, lon):
    """Rough mask of the Antarctic and Greenland ice sheets (not Iceland).

    Ice sheets are smooth and can mimic lava plains in terrain-only screening. They are kept out of
    the main shortlist, and a couple per target are kept as "terrain-only lookalikes" so stage 2 can
    show why one dimension is not enough.
    """
    if lat < -60:
        return True
    greenland = lat > 59.5 and -74 < lon < -11 and not (lat < 67 and lon > -25)
    return greenland


def _pick(ranked, n, min_sep_km, known, already=()):
    chosen = list(already)
    out = []
    for _, c in ranked.iterrows():
        if any(_dist_km(c.lat, c.lon, p[0], p[1]) < min_sep_km for p in chosen):
            continue  # keep candidates spread out
        if any(_dist_km(c.lat, c.lon, la, lo) < 100 for la, lo in known):
            continue  # already in the characterised set
        chosen.append((c.lat, c.lon))
        out.append(c)
        if len(out) >= n:
            break
    return out


def step_candidates(n_main=6, n_ice=2, min_sep_km=500):
    from modules.similarity_scoring import screen_similarity

    cells = pd.read_csv(PROCESSED_DIR / "global_screen.csv")
    targets = pd.read_csv(PROCESSED_DIR / "targets.csv").set_index("key")
    known = [(v["lat"], v["lon"]) for v in EARTH_SITES.values()]
    ice = np.array([on_ice_sheet(la, lo) for la, lo in zip(cells["lat"], cells["lon"])])
    picks = []
    for key in targets.index:
        sim = screen_similarity(cells, targets.loc[key], cells)
        ranked = cells.assign(score=sim, ice=ice).dropna(subset=["score"]).sort_values("score", ascending=False)
        main = _pick(ranked[~ranked["ice"]], n_main, min_sep_km, known)
        lookalikes = _pick(ranked[ranked["ice"]], n_ice, min_sep_km, known)
        for kind, chosen in (("main", main), ("ice_lookalike", lookalikes)):
            for i, c in enumerate(chosen, 1):
                rank_all = int((ranked["score"] > c.score).sum()) + 1
                picks.append({"key": f"cand_{key}_{'ice' if kind != 'main' else ''}{i}", "target": key,
                              "kind": kind, "lat": c.lat, "lon": c.lon, "screen_score": round(c.score, 1),
                              "screen_rank": rank_all})
        log(f"{key}: {len(main)} candidates (best {main[0].score:.1f}) + {len(lookalikes)} ice-sheet lookalikes")
    pd.DataFrame(picks).to_csv(PROCESSED_DIR / "stage2_candidates.csv", index=False)


def _dist_km(lat1, lon1, lat2, lon2):
    p1, p2 = np.radians(lat1), np.radians(lat2)
    dl = np.radians(lon2 - lon1)
    a = np.sin((p2 - p1) / 2) ** 2 + np.cos(p1) * np.cos(p2) * np.sin(dl / 2) ** 2
    return 2 * 6371 * np.arcsin(np.sqrt(a))


def step_earth():
    from modules.data_collection import read_earth_window
    from modules.environmental_analysis import fetch_power_climate
    from modules.geological_analysis import fetch_lithology, reverse_geocode

    sites = [{"key": k, **v} for k, v in EARTH_SITES.items()]
    cand_path = PROCESSED_DIR / "stage2_candidates.csv"
    if cand_path.exists():
        for _, c in pd.read_csv(cand_path).iterrows():
            tname = TARGETS[c.target]["short"]
            if c.kind == "ice_lookalike":
                note = (f"Ice-sheet lookalike for {tname}: its terrain scored {c.screen_score} in screening "
                        f"(rank {c.screen_rank} of all land cells), but the surface is ice, not rock. Kept to "
                        "show why terrain alone is not enough.")
            else:
                note = (f"Found by global terrain screening for {tname}: score {c.screen_score}, "
                        f"rank {c.screen_rank} of all land cells.")
            sites.append({"key": c.key, "name": None, "country": None, "lat": c.lat, "lon": c.lon,
                          "group": "lookalike" if c.kind == "ice_lookalike" else "discovered",
                          "screen_target": c.target, "notes": note})
    rows = []
    for s in sites:
        log(f"earth {s['key']} ({s['lat']}, {s['lon']})")
        try:
            z = read_earth_window(s["lat"], s["lon"], DETAIL_WINDOW_KM, DETAIL_RES_M, cache_key=f"earth_{s['key']}")
            m = compute_metrics(z, DETAIL_RES_M)
            save_hillshade(z, DETAIL_RES_M, f"earth_{s['key']}")
        except Exception as exc:
            log(f"  terrain failed: {exc}")
            m = {}
        climate = fetch_power_climate(s["lat"], s["lon"])
        geo = fetch_lithology(s["lat"], s["lon"])
        if not s.get("name"):
            place = reverse_geocode(s["lat"], s["lon"])
            s["name"], s["country"] = place.get("name"), place.get("country")
        rows.append({**{k: s.get(k) for k in ["key", "name", "country", "lat", "lon", "group", "screen_target",
                                              "notes"]},
                     **m, **climate, **geo})
        time.sleep(0.3)
    pd.DataFrame(rows).to_csv(PROCESSED_DIR / "earth_sites.csv", index=False)
    log(f"wrote {len(rows)} sites to earth_sites.csv")


STEPS = {"targets": step_targets, "screen": step_screen, "candidates": step_candidates, "earth": step_earth}

if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--step", choices=[*STEPS, "all"], default="all")
    args = ap.parse_args()
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    for name, fn in STEPS.items():
        if args.step in (name, "all"):
            fn()
    log(json.dumps({"finished": args.step}))
