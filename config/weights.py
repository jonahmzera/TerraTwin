# Provisional comparison settings. These are development assumptions,
# NOT scientifically established values. Every one must be justified
# or changed before the final submission.
#
# "range" is the comparison range R in:
#   similarity = 100 * max(0, 1 - |earth - planet| / R)

TOPOGRAPHY_VARIABLES = {
    "relief_m": {
        "label": "Local relief (m)",
        "range": 3000,
        "default_weight": 25,
    },
    "slope_mean_deg": {
        "label": "Mean slope (degrees)",
        "range": 5,
        "default_weight": 25,
    },
    "slope_max_deg": {
        "label": "Maximum slope (degrees)",
        "range": 45,
        "default_weight": 25,
    },
    "roughness_tri_m": {
        "label": "Roughness, TRI (m)",
        "range": 10,
        "default_weight": 25,
    },
}