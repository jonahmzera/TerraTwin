"""Climate of Earth sites from NASA POWER, and how it compares with the Moon and Mars.

NASA POWER climatology (long-term averages) is requested for the centre point of each
Earth site. Moon and Mars values are approximate literature values, stored with their
sources in config/study_locations.py. No Earth site can match the vacuum of the Moon or
the thin atmosphere of Mars, so the environment comparison is reported as "how close
Earth gets", and the pressure gap is always listed as a breakdown of the analogy.
"""

import math

import requests

from config.settings import POWER_PARAMETERS, SOURCES

SEA_LEVEL_KPA = 101.325


def fetch_power_climate(lat, lon, timeout=60):
    """Annual climatology at a point. Missing values (-999) become None."""
    params = dict(parameters=",".join(POWER_PARAMETERS), community="RE", longitude=round(lon, 4),
                  latitude=round(lat, 4), format="JSON")
    try:
        r = requests.get(SOURCES["nasa_power"]["url"], params=params, timeout=timeout)
        r.raise_for_status()
        p = r.json()["properties"]["parameter"]
    except Exception as exc:
        return {"power_error": str(exc)[:200]}
    out = {}
    for key in POWER_PARAMETERS:
        v = p.get(key, {}).get("ANN")
        out[f"power_{key}"] = None if v is None or v <= -998 else round(float(v), 2)
    if out.get("power_PRECTOTCORR") is not None:
        out["precip_mm_yr"] = round(out["power_PRECTOTCORR"] * 365.25, 1)
    return out


def pressure_kpa_from_elevation(elev_m):
    """Standard-atmosphere surface pressure (kPa) at an elevation, for context only."""
    if elev_m is None or (isinstance(elev_m, float) and math.isnan(elev_m)):
        return None
    return round(SEA_LEVEL_KPA * (1 - 2.25577e-5 * elev_m) ** 5.25588, 1)


def aridity_score(precip_mm_yr):
    """0-100, higher = drier. Log scale: 1 mm/yr -> 100, 10 -> 67, 100 -> 33, 1000+ -> 0.

    The Moon and Mars have no rain, so drier Earth sites are better environmental analogues.
    """
    if precip_mm_yr is None or (isinstance(precip_mm_yr, float) and math.isnan(precip_mm_yr)):
        return None
    p = max(precip_mm_yr, 1.0)
    return round(100 * min(1.0, max(0.0, (3 - math.log10(p)) / 3)), 1)


def environment_variables(site, target):
    """Paired Earth vs target values for the environment dimension.

    Returns a list of dicts: variable, earth, target, range R (for similarity), scored flag.
    """
    env = target["environment"]
    precip = site.get("precip_mm_yr")
    return [
        {"key": "env_temperature", "label": "Mean temperature (degC)", "earth": site.get("power_T2M"),
         "target": env["T2M"], "range": 100.0},
        {"key": "env_daily_range", "label": "Daily temperature range (degC)", "earth": site.get("power_T2M_RANGE"),
         "target": env["T2M_RANGE"], "range": 100.0},
        {"key": "env_aridity", "label": "Aridity (0-100, from precipitation)", "earth": aridity_score(precip),
         "target": 100.0, "range": 100.0},
    ]
