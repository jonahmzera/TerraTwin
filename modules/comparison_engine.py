"""Load the pipeline outputs for the app, and run comparisons.

The app never downloads data: it only reads the CSV files written by
scripts/run_pipeline.py, so it starts fast and works offline.
"""

import pandas as pd
import streamlit as st

from config.settings import IMAGE_DIR, PROCESSED_DIR
from config.study_locations import TARGETS
from modules.similarity_scoring import (DEFAULT_WEIGHTS, rank_sites, score_site, screen_similarity,
                                        terrain_ranges)


def _read(name):
    path = PROCESSED_DIR / name
    return pd.read_csv(path) if path.exists() else None


@st.cache_data
def load_targets():
    return _read("targets.csv")


@st.cache_data
def load_earth_sites():
    return _read("earth_sites.csv")


@st.cache_data
def load_screen():
    return _read("global_screen.csv")


@st.cache_data
def load_candidates():
    return _read("stage2_candidates.csv")


def require(*frames):
    """Stop the page with a clear message if pipeline outputs are missing."""
    if any(f is None for f in frames):
        st.error(
            "Pipeline outputs are missing. Run `python -m scripts.run_pipeline --step all` "
            "from the project folder (see README).",
            title="No data yet",
        )
        st.stop()


def target_options():
    return {k: v["name"] for k, v in TARGETS.items()}


def target_row(targets_df, key):
    return targets_df.set_index("key").loc[key].to_dict()


@st.cache_data
def ranking(target_key, weights_items=tuple(DEFAULT_WEIGHTS.items()), n_draws=200):
    sites, targets = load_earth_sites(), load_targets()
    return rank_sites(sites, target_row(targets, target_key), TARGETS[target_key], dict(weights_items), n_draws)


@st.cache_data
def compare(site_key, target_key, weights_items=tuple(DEFAULT_WEIGHTS.items()), n_draws=500):
    sites, targets = load_earth_sites(), load_targets()
    site = sites.set_index("key").loc[site_key].to_dict()
    site["key"] = site_key
    return score_site(site, target_row(targets, target_key), TARGETS[target_key], terrain_ranges(sites),
                      dict(weights_items), n_draws)


@st.cache_data
def screen_scores(target_key):
    cells, targets = load_screen(), load_targets()
    return cells.assign(score=screen_similarity(cells, target_row(targets, target_key), cells))


def image_path(kind, key):
    p = IMAGE_DIR / f"{kind}_{key}.png"
    return p if p.exists() else None


def site_label(row):
    country = row.get("country")
    country = "" if country is None or pd.isna(country) else f", {country}"
    return f"{row['name']}{country}"
