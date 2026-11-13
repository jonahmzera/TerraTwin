# Starting study locations for TerraTwin.
# Coordinates are APPROXIMATE centre points, to be replaced by proper
# study boundaries once the real datasets are loaded.
# Moon and Mars use planetocentric latitude/longitude, NOT Earth coordinates.

STUDY_LOCATIONS = {
    "chyulu_hills": {
        "name": "Chyulu Hills",
        "body": "Earth",
        "country": "Kenya",
        "lat": -2.7,
        "lon": 37.8,
        "role": "Candidate volcanic terrain (not a confirmed analogue)",
    },
    "lonar_crater": {
        "name": "Lonar Crater",
        "body": "Earth",
        "country": "India",
        "lat": 19.98,
        "lon": 76.51,
        "role": "Impact crater validation case",
    },
    "mare_imbrium": {
        "name": "Mare Imbrium",
        "body": "Moon",
        "country": "-",
        "lat": 32.8,
        "lon": -15.6,
        "role": "Lunar reference region",
    },
    "elysium_planitia": {
        "name": "Elysium Planitia",
        "body": "Mars",
        "country": "-",
        "lat": 3.0,
        "lon": 154.7,
        "role": "Martian volcanic reference region",
    },
}