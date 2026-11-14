"""Project-wide settings: paths, data sources and processing constants.

Every dataset TerraTwin uses is open and read directly from its public host.
Nothing here requires a login or an API key.
"""

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"
PROCESSED_DIR = DATA_DIR / "processed"
CACHE_DIR = DATA_DIR / "cache"  # downloaded windows, not committed to Git
IMAGE_DIR = PROCESSED_DIR / "img"

# ---- Body radii (metres), used for local map projections ----
MARS_RADIUS_M = 3_396_190  # IAU 2000 Mars sphere, as used by the USGS Mars 2000 CRS
MOON_RADIUS_M = 1_737_400  # IAU Moon sphere, as used by LOLA products

# ---- Processing scales ----
DETAIL_WINDOW_KM = 50  # stage 2: characterisation window (square)
DETAIL_RES_M = 200  # stage 2: common pixel size for all bodies
SCREEN_RES_M = 1200  # stage 1: approximate pixel size of the global screening
SCREEN_WINDOW_KM = 78  # stage 1: approximate cell size of the global screening
FLAT_SLOPE_DEG = 5  # pixels flatter than this count as "landing-friendly" at 200 m

# ---- Data sources ----
SOURCES = {
    "copernicus_glo30": {
        "name": "Copernicus DEM GLO-30 (DSM)",
        "provider": "ESA / Copernicus programme, hosted on AWS Open Data",
        "url": "https://copernicus-dem-30m.s3.amazonaws.com",
        "native_resolution": "30 m",
        "citation": "European Space Agency (2024). Copernicus Global Digital Elevation Model. "
        "Distributed by OpenTopography / AWS Open Data. https://doi.org/10.5069/G9028PQB",
    },
    "terrain_tiles": {
        "name": "Terrain Tiles (GeoTIFF, zoom 6)",
        "provider": "Mapzen / Tilezen, hosted on AWS Open Data (built from SRTM, GMTED2010, ETOPO1 and others)",
        "url": "https://s3.amazonaws.com/elevation-tiles-prod/geotiff",
        "native_resolution": "~1.2 km at the equator (zoom 6)",
        "citation": "Terrain Tiles, AWS Open Data Registry. https://registry.opendata.aws/terrain-tiles/ "
        "(includes SRTM courtesy NASA/USGS, GMTED2010 courtesy USGS, ETOPO1 courtesy NOAA).",
    },
    "mars_blend": {
        "name": "Mars MGS MOLA - MEX HRSC Blended DEM Global 200 m v2",
        "provider": "USGS Astrogeology (MOLA: NASA/GSFC, HRSC: ESA/DLR/FU Berlin)",
        "url": "https://planetarymaps.usgs.gov/mosaic/Mars/HRSC_MOLA_Blend/Mars_HRSC_MOLA_BlendDEM_Global_200mp_v2.tif",
        "native_resolution": "200 m",
        "citation": "Fergason, R. L., Hare, T. M., & Laura, J. (2018). HRSC and MOLA Blended Digital Elevation "
        "Model at 200m v2. Astrogeology PDS Annex, U.S. Geological Survey.",
    },
    "moon_lola": {
        "name": "LRO LOLA Global LDEM 118 m (Mar 2014)",
        "provider": "NASA LRO LOLA team, mosaic hosted by USGS Astrogeology",
        "url": "https://planetarymaps.usgs.gov/mosaic/Lunar_LRO_LOLA_Global_LDEM_118m_Mar2014.tif",
        "native_resolution": "118 m",
        "citation": "LOLA Science Team (2014). LRO LOLA Elevation Model 118m (LDEM GDR). "
        "Smith, D. E., et al. (2010), Geophys. Res. Lett., 37, L18204.",
    },
    "nasa_power": {
        "name": "NASA POWER climatology (MERRA-2 / CERES based)",
        "provider": "NASA Langley Research Center, Prediction Of Worldwide Energy Resources project",
        "url": "https://power.larc.nasa.gov/api/temporal/climatology/point",
        "native_resolution": "0.5 x 0.625 degrees (meteorology)",
        "citation": "NASA Langley Research Center POWER Project, funded through the NASA Earth Science "
        "Applied Science Program. https://power.larc.nasa.gov/",
    },
    "macrostrat": {
        "name": "Macrostrat geologic map units",
        "provider": "Macrostrat, University of Wisconsin-Madison (compiles published geologic maps)",
        "url": "https://macrostrat.org/api/v2/geologic_units/map",
        "native_resolution": "varies by source map",
        "citation": "Peters, S. E., Husson, J. M., & Czaplewski, J. (2018). Macrostrat: A platform for "
        "geological data integration and deep-time Earth crust research. G-Cubed, 19, 1393-1409.",
    },
}

POWER_PARAMETERS = {
    "T2M": "Mean air temperature at 2 m (degC)",
    "T2M_RANGE": "Mean daily temperature range at 2 m (degC)",
    "PRECTOTCORR": "Precipitation (mm/day)",
    "RH2M": "Relative humidity at 2 m (%)",
    "WS10M": "Wind speed at 10 m (m/s)",
    "ALLSKY_SFC_SW_DWN": "Solar irradiance at the surface (kWh/m2/day)",
}
