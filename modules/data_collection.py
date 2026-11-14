"""Read elevation windows from open Earth, Moon and Mars datasets.

Each window is resampled onto a local azimuthal-equidistant grid centred on the site,
so every body is measured on the same kind of square grid with the same pixel size
(no stretching near the poles, distances in metres). Files are read remotely with
HTTP range requests (only the needed part is downloaded) and cached in data/cache.
"""

import math
from functools import lru_cache

import numpy as np
import rasterio
import requests
from pyproj import CRS, Transformer
from rasterio.transform import from_origin
from rasterio.warp import Resampling, reproject

from config.settings import CACHE_DIR, MARS_RADIUS_M, MOON_RADIUS_M, SOURCES

GDAL_ENV = dict(
    GDAL_DISABLE_READDIR_ON_OPEN="EMPTY_DIR",
    CPL_VSIL_CURL_ALLOWED_EXTENSIONS=".tif",
    GDAL_HTTP_MAX_RETRY="4",
    GDAL_HTTP_RETRY_DELAY="2",
    GDAL_HTTP_CONNECTTIMEOUT="20",
    GDAL_HTTP_TIMEOUT="120",  # without this, one stalled connection can hang the pipeline forever
    GDAL_HTTP_LOW_SPEED_TIME="60",
    GDAL_HTTP_LOW_SPEED_LIMIT="1000",
    VSI_CACHE="TRUE",
)

RADIUS = {"Mars": MARS_RADIUS_M, "Moon": MOON_RADIUS_M}


def local_crs(lat, lon, body):
    """Azimuthal equidistant projection centred on the site, for the right body."""
    if body == "Earth":
        return CRS.from_proj4(f"+proj=aeqd +lat_0={lat} +lon_0={lon} +datum=WGS84 +units=m +no_defs")
    return CRS.from_proj4(f"+proj=aeqd +lat_0={lat} +lon_0={lon} +R={RADIUS[body]} +units=m +no_defs")


def _grid(size_km, res_m):
    n = int(round(size_km * 1000 / res_m))
    half = n * res_m / 2
    return n, from_origin(-half, half, res_m, res_m)


def _reproject_into(dst, src_ds, dst_transform, dst_crs, resampling, src_crs=None):
    """Warp one source dataset into dst (float32, NaN = empty), keeping existing values."""
    scale = (src_ds.scales or (1.0,))[0] or 1.0
    offset = (src_ds.offsets or (0.0,))[0] or 0.0
    tmp = np.full(dst.shape, np.nan, dtype="float32")
    reproject(
        source=rasterio.band(src_ds, 1),
        destination=tmp,
        src_crs=src_crs or src_ds.crs,
        src_nodata=src_ds.nodata,
        dst_transform=dst_transform,
        dst_crs=dst_crs,
        dst_nodata=np.nan,
        resampling=resampling,
        SAMPLE_GRID="YES",
        SOURCE_EXTRA=4,
    )
    tmp = tmp * scale + offset
    fill = np.isnan(dst) & np.isfinite(tmp)
    dst[fill] = tmp[fill]


def _cache_path(key):
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    return CACHE_DIR / f"{key}.npy"


def read_planet_window(dem_key, body, lat, lon, size_km, res_m, cache_key=None):
    """Elevation window (m) from a global Mars or Moon DEM on a local square grid."""
    path = _cache_path(cache_key) if cache_key else None
    if path and path.exists():
        return np.load(path)
    n, transform = _grid(size_km, res_m)
    dst = np.full((n, n), np.nan, dtype="float32")
    src_res = {"mars_blend": 200, "moon_lola": 118}[dem_key]
    resampling = Resampling.average if res_m > src_res * 1.2 else Resampling.bilinear
    with rasterio.Env(**GDAL_ENV):
        with rasterio.open("/vsicurl/" + SOURCES[dem_key]["url"]) as ds:
            _reproject_into(dst, ds, transform, local_crs(lat, lon, body), resampling)
    if path:
        np.save(path, dst)
    return dst


@lru_cache(maxsize=1)
def copernicus_tiles():
    """Set of existing Copernicus GLO-30 tile names (ocean-only tiles do not exist)."""
    url = SOURCES["copernicus_glo30"]["url"] + "/tileList.txt"
    return set(requests.get(url, timeout=60).text.split())


def _cop_tile_name(lat_floor, lon_floor):
    ns = "N" if lat_floor >= 0 else "S"
    ew = "E" if lon_floor >= 0 else "W"
    return f"Copernicus_DSM_COG_10_{ns}{abs(lat_floor):02d}_00_{ew}{abs(lon_floor):03d}_00_DEM"


def read_earth_window(lat, lon, size_km, res_m, cache_key=None):
    """Elevation window (m) from Copernicus GLO-30, averaged onto a local square grid."""
    path = _cache_path(cache_key) if cache_key else None
    if path and path.exists():
        return np.load(path)
    n, transform = _grid(size_km, res_m)
    crs = local_crs(lat, lon, "Earth")
    dst = np.full((n, n), np.nan, dtype="float32")

    # Geographic bounds of the window (sample its edge), plus a small margin.
    to_geo = Transformer.from_crs(crs, "EPSG:4326", always_xy=True)
    half = n * res_m / 2
    edge = np.linspace(-half, half, 21)
    xs = np.concatenate([edge, edge, np.full(21, -half), np.full(21, half)])
    ys = np.concatenate([np.full(21, -half), np.full(21, half), edge, edge])
    lons, lats = to_geo.transform(xs, ys)
    tiles = copernicus_tiles()
    with rasterio.Env(**GDAL_ENV):
        for la in range(math.floor(min(lats)), math.floor(max(lats)) + 1):
            for lo in range(math.floor(min(lons)), math.floor(max(lons)) + 1):
                name = _cop_tile_name(la, ((lo + 180) % 360) - 180)
                if name not in tiles:
                    continue  # ocean
                url = f"/vsicurl/{SOURCES['copernicus_glo30']['url']}/{name}/{name}.tif"
                with rasterio.open(url) as ds:
                    _reproject_into(dst, ds, transform, crs, Resampling.average)
    if path:
        np.save(path, dst)
    return dst


def read_terrain_tile(z, x, y):
    """One Terrain Tiles GeoTIFF (Web Mercator) as float32 metres, plus its transform."""
    url = f"/vsicurl/{SOURCES['terrain_tiles']['url']}/{z}/{x}/{y}.tif"
    with rasterio.Env(**GDAL_ENV):
        with rasterio.open(url) as ds:
            arr = ds.read(1).astype("float32")
            if ds.nodata is not None:
                arr[arr == ds.nodata] = np.nan
            return arr, ds.transform
