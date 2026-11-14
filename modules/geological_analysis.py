"""Surface geology of Earth sites (Macrostrat) and a simple match to the target's geology.

Macrostrat returns the mapped geologic unit at a point, from published geologic maps.
We compare its rock types with the rock types expected at the target:
  100 = a primary rock type matches (e.g. basalt for a mare basalt plain)
   60 = only a related rock type matches (e.g. "volcanic" without "basalt")
    0 = no match
  missing = Macrostrat has no map unit there (for example under ice sheets).
This is a coarse, keyword-based match, and it is reported as such.
"""

import json
from collections import Counter

import requests

from config.settings import SOURCES

HEADERS = {"User-Agent": "TerraTwin-research/1.0 (NASA Space Apps Challenge 2026)"}


def fetch_lithology(lat, lon, timeout=60):
    """Mapped geologic unit at a point. Prefers the most detailed map with rock types."""
    try:
        r = requests.get(SOURCES["macrostrat"]["url"], params={"lat": lat, "lng": lon}, headers=HEADERS,
                         timeout=timeout)
        r.raise_for_status()
        units = r.json().get("success", {}).get("data", [])
    except Exception as exc:
        return {"geo_error": str(exc)[:200]}
    units = [u for u in units if (u.get("lith") or u.get("name") or u.get("descrip"))]
    if not units:
        return {"geo_lith": None, "geo_name": None, "geo_age": None, "geo_desc": None, "geo_units": None}
    # Several published maps can cover one point, and they can disagree (for example a bedrock map under
    # young lava). Keep every unit from the most detailed scale available; geology_match takes a majority vote.
    order = ["large", "medium", "small", "tiny"]
    best = min((order.index(u.get("scale")) if u.get("scale") in order else 9) for u in units)
    units = [u for u in units if (order.index(u.get("scale")) if u.get("scale") in order else 9) == best]
    first = next((u for u in units if u.get("lith")), units[0])
    liths = list(dict.fromkeys((u.get("lith") or "").strip() for u in units if u.get("lith")))
    return {
        "geo_lith": " | ".join(liths) or None,
        "geo_name": (first.get("name") or "").strip() or None,
        "geo_age": first.get("best_int_name"),
        "geo_desc": ((first.get("descrip") or "").strip()[:300]) or None,
        "geo_scale": units[0].get("scale"),
        "geo_units": json.dumps([{"name": u.get("name"), "lith": u.get("lith"), "descrip": (u.get("descrip") or "")[:200]}
                                 for u in units]),
    }


def reverse_geocode(lat, lon, timeout=30):
    """Place name for a discovered candidate (OpenStreetMap Nominatim, 1 request per second)."""
    try:
        r = requests.get("https://nominatim.openstreetmap.org/reverse",
                         params={"lat": lat, "lon": lon, "format": "jsonv2", "zoom": 8, "accept-language": "en"},
                         headers=HEADERS, timeout=timeout)
        r.raise_for_status()
        j = r.json()
        addr = j.get("address", {})
        name = (addr.get("county") or addr.get("state_district") or addr.get("state") or addr.get("region")
                or j.get("name"))
        return {"name": f"Near {name}" if name else f"Cell {lat:.2f}, {lon:.2f}", "country": addr.get("country")}
    except Exception:
        return {"name": f"Cell {lat:.2f}, {lon:.2f}", "country": None}


def _match_text(text, target):
    text = text.lower()
    prim = [w for w in target["lithology_primary"] if w in text]
    if prim:
        return 100.0, prim
    sec = [w for w in target["lithology_secondary"] if w in text]
    if sec:
        return 60.0, sec
    return 0.0, []


def geology_match(site, target):
    """Score 0, 60 or 100 (None if no map data), plus a short explanation.

    When several maps cover the point, each map unit is scored and the most common score wins
    (ties go to the lower score, to stay conservative).
    """
    units = site.get("geo_units")
    units = json.loads(units) if isinstance(units, str) and units.strip() else None  # NaN from CSV = none
    if units:
        texts = [" ".join(str(u.get(k) or "") for k in ("lith", "name", "descrip")) for u in units]
    else:
        texts = [" ".join(str(site.get(k) or "") for k in ["geo_lith", "geo_name", "geo_desc"])]
    texts = [t for t in texts if t.strip() and t.strip().lower() != "nan"]
    if not texts:
        return None, "No mapped geology at this point"
    scored = [_match_text(t, target) for t in texts]
    counts = Counter(s for s, _ in scored)
    top = max(counts.values())
    score = min(s for s, c in counts.items() if c == top)
    words = sorted({w for s, ws in scored if s == score for w in ws})
    agree = f"{counts[score]} of {len(scored)} map units" if len(scored) > 1 else "map unit"
    if score == 100:
        return score, f"matches {', '.join(words)} ({agree})"
    if score == 60:
        return score, f"related: {', '.join(words)} ({agree})"
    return 0.0, f"no shared rock types ({agree})"
