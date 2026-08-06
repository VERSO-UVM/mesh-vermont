"""Reconstructs a local DSM (absolute surface elevation, including
buildings/canopy) from two statewide VT Open Data rasters, without
downloading either one in full:

    DSM = bare-earth DEM + nDSM (normalized DSM = object height above ground)

Both source rasters are opened remotely via GDAL's /vsicurl/ virtual
filesystem. The DEM clip defines the output grid; the nDSM is then
reprojected/resampled onto that exact same grid (not just clipped
independently) so the two add up pixel-for-pixel correctly, then the
result is written as a single GeoTIFF ready to use as --dem in
run_coverage.py.
"""
import argparse
import time

import numpy as np
import pyproj
import rasterio
from rasterio.enums import Resampling
from rasterio.warp import reproject
from rasterio.windows import Window, from_bounds

DEFAULT_DEM_URL = "https://s3.us-east-2.amazonaws.com/vtopendata-prd/Elevation/STATEWIDE_2023_10M_DEMHF.tif"
DEFAULT_NDSM_URL = "https://s3.us-east-2.amazonaws.com/vtopendata-prd/Elevation/STATEWIDE_2023_35cm_NDSM.tif"


def _vsi(url_or_path):
    if url_or_path.startswith("http://") or url_or_path.startswith("https://"):
        return "/vsicurl/" + url_or_path
    return url_or_path


def _clip_and_resample(vsi_url, lon, lat, radius_km, resolution_m):
    """Reads a decimated (overview-aware) window around (lon, lat) from a
    remote or local raster, resampled to resolution_m. Returns
    (data, transform, crs, nodata)."""
    with rasterio.open(vsi_url) as src:
        to_src_crs = pyproj.Transformer.from_crs("EPSG:4326", src.crs, always_xy=True)
        cx, cy = to_src_crs.transform(lon, lat)
        half = radius_km * 1000.0
        window = from_bounds(cx - half, cy - half, cx + half, cy + half, transform=src.transform)
        window = window.round_offsets().round_lengths()
        window = window.intersection(Window(0, 0, src.width, src.height))

        scale = resolution_m / src.res[0]
        out_width = max(int(window.width / scale), 1)
        out_height = max(int(window.height / scale), 1)

        data = src.read(1, window=window, out_shape=(out_height, out_width), resampling=Resampling.average)
        transform = src.window_transform(window) * rasterio.Affine.scale(
            window.width / out_width, window.height / out_height
        )
        return data.astype("float32"), transform, src.crs, src.nodata


def _reproject_onto(vsi_url, dst_shape, dst_transform, dst_crs, src_nodata_fallback=None):
    """Resamples a remote/local raster directly onto an existing target
    grid (used to align the nDSM onto the DEM clip's exact pixel grid)."""
    with rasterio.open(vsi_url) as src:
        dst = np.full(dst_shape, np.nan, dtype="float32")
        reproject(
            source=rasterio.band(src, 1),
            destination=dst,
            src_transform=src.transform,
            src_crs=src.crs,
            src_nodata=src.nodata if src.nodata is not None else src_nodata_fallback,
            dst_transform=dst_transform,
            dst_crs=dst_crs,
            dst_nodata=np.nan,
            resampling=Resampling.average,
        )
        return dst


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--lon", type=float, required=True)
    ap.add_argument("--lat", type=float, required=True)
    ap.add_argument("--radius-km", type=float, default=30.0)
    ap.add_argument("--resolution-m", type=float, default=10.0)
    ap.add_argument("--dem-url", default=DEFAULT_DEM_URL, help="local path or URL to the bare-earth DEM")
    ap.add_argument("--ndsm-url", default=DEFAULT_NDSM_URL, help="local path or URL to the nDSM")
    ap.add_argument("--out", required=True)
    args = ap.parse_args()

    t0 = time.time()

    print(f"Clipping DEM ({args.dem_url}) ...")
    dem_data, transform, crs, dem_nodata = _clip_and_resample(
        _vsi(args.dem_url), args.lon, args.lat, args.radius_km, args.resolution_m
    )
    if dem_nodata is not None:
        dem_data = np.where(dem_data == dem_nodata, np.nan, dem_data)
    print(f"  -> {dem_data.shape[1]}x{dem_data.shape[0]} px, elevation range "
          f"{np.nanmin(dem_data):.1f} to {np.nanmax(dem_data):.1f} m")

    print(f"Reprojecting nDSM ({args.ndsm_url}) onto the DEM's grid ...")
    ndsm_data = _reproject_onto(_vsi(args.ndsm_url), dem_data.shape, transform, crs)
    print(f"  -> object height range {np.nanmin(ndsm_data):.1f} to {np.nanmax(ndsm_data):.1f} m")

    dsm_data = dem_data + np.nan_to_num(ndsm_data, nan=0.0)
    dsm_data = np.where(np.isnan(dem_data), np.nan, dsm_data).astype("float32")

    profile = {
        "driver": "GTiff", "height": dsm_data.shape[0], "width": dsm_data.shape[1],
        "count": 1, "dtype": "float32", "crs": crs, "transform": transform,
        "compress": "lzw", "nodata": np.nan,
    }
    with rasterio.open(args.out, "w", **profile) as dst:
        dst.write(dsm_data, 1)

    elapsed = time.time() - t0
    import os
    size_mb = os.path.getsize(args.out) / 1e6
    print(f"Wrote {args.out} ({size_mb:.1f} MB) in {elapsed:.1f}s -- "
          f"reconstructed DSM range {np.nanmin(dsm_data):.1f} to {np.nanmax(dsm_data):.1f} m")


if __name__ == "__main__":
    main()
