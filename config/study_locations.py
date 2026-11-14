"""Study locations for TerraTwin.

TARGETS are real landing sites or candidate exploration sites on the Moon and Mars.
EARTH_SITES are the Earth places we characterise in detail:
  - "team": sites the team proposed at the start,
  - "known": well-studied analogue sites, used to VALIDATE the method
    (a good method should rate them as reasonable analogues),
  - "discovered": candidates found by the global screening (added by the pipeline,
    see data/processed/stage2_candidates.csv, not listed here).

Moon and Mars coordinates are planetocentric latitude, longitude east-positive (-180..180).
Coordinates marked "approx" are centre points from public descriptions, not surveyed
boundaries. Every window is a square box around the centre point.
"""

TARGETS = {
    "mars_insight": {
        "name": "Elysium Planitia (InSight landing site)",
        "short": "InSight, Mars",
        "body": "Mars",
        "lat": 4.502,
        "lon": 135.623,
        "dem": "mars_blend",
        "why": "Smooth Amazonian lava plain chosen for a safe landing. InSight landed here in 2018.",
        "coord_source": "Golombek, M. et al. (2020). Geology of the InSight landing site on Mars. "
        "Nature Communications 11, 1014.",
        "approx": False,
        "lithology_primary": ["basalt", "mafic", "lava"],
        "lithology_secondary": ["volcanic", "andesite", "trachyte", "igneous", "regolith", "tuff"],
        "geology_summary": "Basaltic lava flows covered by impact-gardened regolith (Golombek et al., 2020).",
        "environment": {
            "T2M": -60,
            "T2M_RANGE": 75,
            "precip_mm_yr": 0,
            "pressure_kpa": 0.7,
            "source": "InSight TWINS/APSS measurements: air temperature about -95 to -20 degC daily, "
            "surface pressure about 0.7 kPa (Banfield, D. et al. (2020). The atmosphere of Mars as observed "
            "by InSight. Nature Geoscience 13, 190-198). Values are approximate and rounded.",
        },
        "exploration_use": [
            "Testing landing hazard detection on smooth, low-slope plains",
            "Seismometer and heat-probe deployment in loose regolith over basalt",
            "Rover mobility on gentle volcanic plains",
        ],
    },
    "mars_jezero": {
        "name": "Jezero Crater (Perseverance landing site)",
        "short": "Jezero, Mars",
        "body": "Mars",
        "lat": 18.4447,
        "lon": 77.4508,
        "dem": "mars_blend",
        "why": "An ancient crater lake with a river delta, chosen to search for signs of past life. "
        "Perseverance landed here in 2021.",
        "coord_source": "NASA/JPL Mars 2020 mission: Octavia E. Butler landing site, 18.4447 N, 77.4508 E.",
        "approx": False,
        "lithology_primary": ["sandstone", "mudstone", "clay", "carbonate", "conglomerate",
                              "siltstone", "lacustrine", "delta", "shale", "sedimentary"],
        "lithology_secondary": ["basalt", "olivine", "ultramafic", "mafic", "evaporite", "limestone"],
        "geology_summary": "Delta and lake sediments with clays and carbonates over an olivine-rich igneous "
        "crater floor (Farley, K. A. et al. (2022), Science 377).",
        "environment": {
            "T2M": -55,
            "T2M_RANGE": 70,
            "precip_mm_yr": 0,
            "pressure_kpa": 0.7,
            "source": "Perseverance MEDA measurements (Rodriguez-Manfredi, J. A. et al. (2023), "
            "Nature Geoscience 16, 19-28). Values are approximate and rounded.",
        },
        "exploration_use": [
            "Sampling strategy and caching practice in delta and lake sediments",
            "Biosignature detection in clays and carbonates",
            "Rover navigation across crater floor and delta front",
        ],
    },
    "moon_imbrium": {
        "name": "Mare Imbrium (Chang'e 3 landing site)",
        "short": "Mare Imbrium, Moon",
        "body": "Moon",
        "lat": 44.1214,
        "lon": -19.5116,
        "dem": "moon_lola",
        "why": "Young mare basalt plain. China's Chang'e 3 lander and Yutu rover landed here in 2013.",
        "coord_source": "Chang'e 3 landing site, 44.1214 N, 19.5116 W, as located in LROC images "
        "(LROC team, Arizona State University, 2014).",
        "approx": False,
        "lithology_primary": ["basalt", "mafic", "lava"],
        "lithology_secondary": ["volcanic", "igneous", "gabbro", "dolerite", "diabase"],
        "geology_summary": "Eratosthenian mare basalt lava flows under a thin regolith "
        "(Zhang, J. et al. (2015), PNAS 112, 5342-5347).",
        "environment": {
            "T2M": -40,
            "T2M_RANGE": 280,
            "precip_mm_yr": 0,
            "pressure_kpa": 0.0,
            "source": "No atmosphere (surface pressure about 3e-12 kPa). Diviner measures roughly 100 K at "
            "night and up to about 390 K at noon near the equator (Williams, J.-P. et al. (2017), Icarus 283, "
            "300-325); colder at 44 N. Values are approximate and rounded.",
        },
        "exploration_use": [
            "Rover traverses and ground-penetrating radar over layered basalt",
            "In-situ resource tests on basaltic regolith (oxygen extraction, construction)",
            "Lander plume and dust interaction with basaltic fines",
        ],
    },
    "moon_marius": {
        "name": "Marius Hills (lava-tube skylight region)",
        "short": "Marius Hills, Moon",
        "body": "Moon",
        "lat": 14.1,
        "lon": -56.8,
        "dem": "moon_lola",
        "why": "Volcanic dome and cone field with a 65 m skylight into a probable lava tube, a candidate "
        "shelter for a future lunar base.",
        "coord_source": "Haruyama, J. et al. (2009). Possible lunar lava tube skylight observed by SELENE "
        "cameras. GRL 36, L21206. Centre point approx.",
        "approx": True,
        "lithology_primary": ["basalt", "mafic", "lava", "scoria", "cinder"],
        "lithology_secondary": ["volcanic", "igneous", "pyroclastic", "tuff"],
        "geology_summary": "Basaltic volcanic domes, cones and sinuous rilles; probable lava tube under the "
        "skylight (Haruyama et al., 2009).",
        "environment": {
            "T2M": -20,
            "T2M_RANGE": 290,
            "precip_mm_yr": 0,
            "pressure_kpa": 0.0,
            "source": "No atmosphere. Near-equatorial Diviner temperatures roughly 100 K to 390 K "
            "(Williams et al., 2017). Inside lava tubes temperatures may stay near -20 degC "
            "(Horvath, T. et al. (2022), GRL 49). Values are approximate.",
        },
        "exploration_use": [
            "Lava-tube mapping, entry and robotic cave exploration",
            "Radiation and thermal shelter studies for habitats",
            "Navigation among volcanic cones and domes",
        ],
    },
    "moon_south_pole": {
        "name": "Lunar south pole (Shackleton crater region, Artemis area)",
        "short": "South pole, Moon",
        "body": "Moon",
        "lat": -89.67,
        "lon": 129.78,
        "dem": "moon_lola",
        "why": "Candidate region for a permanent Artemis base: near-continuous sunlight on rims and water ice "
        "in permanently shadowed craters.",
        "coord_source": "Shackleton crater centre (IAU Gazetteer of Planetary Nomenclature). Centre point "
        "approx; the 50 km window includes the crater and its rim.",
        "approx": True,
        "lithology_primary": ["anorthosite", "plagioclase", "breccia", "impact"],
        "lithology_secondary": ["gabbro", "norite", "plutonic", "igneous", "metamorphic"],
        "geology_summary": "Feldspar-rich highland crust (anorthosite) reworked by impacts, with possible water "
        "ice in permanently shadowed regions (Colaprete, A. et al. (2010), Science 330).",
        "environment": {
            "T2M": -170,
            "T2M_RANGE": 60,
            "precip_mm_yr": 0,
            "pressure_kpa": 0.0,
            "source": "No atmosphere. Permanently shadowed regions reach about 25 K (Paige, D. A. et al. "
            "(2010), Science 330, 479-482); sunlit rims stay much warmer. Values are rough averages.",
        },
        "exploration_use": [
            "Navigation and operations under low sun angles and long shadows",
            "Drilling and prospecting for ice in cold, rugged terrain",
            "Landing on crater rims with steep slopes nearby",
        ],
    },
}

EARTH_SITES = {
    # ---- Sites proposed by the team ----
    "chyulu_hills": {
        "name": "Chyulu Hills", "country": "Kenya", "lat": -2.7, "lon": 37.8, "group": "team",
        "notes": "Young basaltic cone field with the Leviathan lava tube, one of the longest known "
        "lava tubes on Earth. Rarely discussed as a planetary analogue.",
    },
    "lonar_crater": {
        "name": "Lonar Crater", "country": "India", "lat": 19.976, "lon": 76.508, "group": "team",
        "notes": "About 1.8 km impact crater formed in Deccan flood basalt, an unusual Earth example of an "
        "impact into basalt (as on the lunar maria).",
    },
    # ---- Well-known analogue sites (validation set) ----
    "haughton": {"name": "Haughton Crater", "country": "Canada", "lat": 75.38, "lon": -89.68, "group": "known",
                 "notes": "Polar desert impact crater; NASA Haughton-Mars Project."},
    "atacama_yungay": {"name": "Atacama Desert (Yungay)", "country": "Chile", "lat": -24.08, "lon": -70.0,
                       "group": "known", "notes": "Hyper-arid desert used for Mars life-detection tests."},
    "death_valley": {"name": "Death Valley", "country": "USA", "lat": 36.45, "lon": -116.9, "group": "known",
                     "notes": "Arid basin with playas, alluvial fans and volcanic features."},
    "mauna_kea": {"name": "Mauna Kea", "country": "USA (Hawaii)", "lat": 19.82, "lon": -155.47, "group": "known",
                  "notes": "Basaltic volcano used for lunar ISRU and rover field tests."},
    "holuhraun": {"name": "Holuhraun lava field", "country": "Iceland", "lat": 64.87, "lon": -16.83,
                  "group": "known", "notes": "2014-15 basaltic lava field; Mars volcanic and rover analogue."},
    "dry_valleys": {"name": "McMurdo Dry Valleys", "country": "Antarctica", "lat": -77.5, "lon": 162.0,
                    "group": "known", "notes": "Cold polar desert; Mars ice and habitability analogue."},
    "craters_of_the_moon": {"name": "Craters of the Moon", "country": "USA", "lat": 43.42, "lon": -113.52,
                            "group": "known", "notes": "Basaltic lava field with lava tubes; NASA field tests."},
    "sp_crater": {"name": "San Francisco Volcanic Field (SP Crater)", "country": "USA", "lat": 35.58,
                  "lon": -111.63, "group": "known", "notes": "Apollo and Artemis astronaut geology training."},
    "meteor_crater": {"name": "Meteor Crater", "country": "USA", "lat": 35.027, "lon": -111.022, "group": "known",
                      "notes": "Young simple impact crater; Apollo training site."},
    "rio_tinto": {"name": "Rio Tinto", "country": "Spain", "lat": 37.7, "lon": -6.6, "group": "known",
                  "notes": "Acidic, iron-rich river; Mars mineralogy and life analogue."},
    "mdrs_utah": {"name": "Mars Desert Research Station area", "country": "USA", "lat": 38.41, "lon": -110.79,
                  "group": "known", "notes": "Sedimentary desert used for Mars crew simulations."},
}

# Known analogue sites, used to flag discovered candidates that are close to a well-studied site.
KNOWN_SITE_KEYS = [k for k, v in EARTH_SITES.items() if v["group"] == "known"]

# Conditions Earth cannot reproduce at any site. Listed in every comparison.
EARTH_LIMITS = {
    "Mars": [
        "Gravity: Mars is 0.38 g; every Earth site is 1 g.",
        "Atmosphere: Mars surface pressure is about 0.6% of Earth's, mostly CO2.",
        "Radiation: no global magnetic field and a thin atmosphere, so surface radiation is far higher.",
    ],
    "Moon": [
        "Gravity: the Moon is 0.17 g; every Earth site is 1 g.",
        "Vacuum: no atmosphere, so no wind erosion, no convective cooling, and sharp, unweathered dust.",
        "Radiation and day length: no magnetic field or atmosphere, and a 29.5-day day-night cycle.",
    ],
}
