"""Clips a small window directly out of VT Open Data's statewide DSM
(surface elevation including buildings/canopy -- ground + object height
already combined, a real product, not reconstructed) without downloading
the full ~414GB file.

Simpler than build_dsm.py: this is a single already-complete source, so
there's no second raster to align/combine. Use this instead of
build_dsm.py whenever you don't specifically need to mix two different
sources (e.g. a non-VCGI nDSM).
"""
import argparse
import os
import time

import numpy as np
import pyproj
import rasterio
from rasterio.enums import Resampling
from rasterio.windows import Window, from_bounds

DEFAULT_DSM_URL = "https://s3.us-east-2.amazonaws.com/vtopendata-prd/Elevation/STATEWIDE_2023_35cm_DSMFR.tif"


def _vsi(url_or_path):
    if url_or_path.startswith("http://") or url_or_path.startswith("https://"):
        return "/vsicurl/" + url_or_path
    return url_or_path


def clip_dsm(lon, lat, out_path, radius_km=30.0, resolution_m=10.0, dsm_url=DEFAULT_DSM_URL, force=False):
    """Clips a radius_km window around (lon, lat) from dsm_url (remote or
    local) at resolution_m, writing out_path. Skips the fetch entirely if
    out_path already exists, unless force=True. Returns True if a fetch
    happened, False if it was skipped."""
    if os.path.exists(out_path) and not force:
        print(f"{out_path} already exists, skipping fetch (use --force to re-fetch)")
        return False

    t0 = time.time()
    vsi_url = _vsi(dsm_url)

    with rasterio.open(vsi_url) as src:
        print(f"Source CRS: {src.crs}, native res: {src.res}, size: {src.width}x{src.height}")

        to_src_crs = pyproj.Transformer.from_crs("EPSG:4326", src.crs, always_xy=True)
        cx, cy = to_src_crs.transform(lon, lat)
        half = radius_km * 1000.0
        window = from_bounds(cx - half, cy - half, cx + half, cy + half, transform=src.transform)
        window = window.round_offsets().round_lengths()
        window = window.intersection(Window(0, 0, src.width, src.height))

        scale = resolution_m / src.res[0]
        out_width = max(int(window.width / scale), 1)
        out_height = max(int(window.height / scale), 1)

        print(f"Fetching window {window.width:.0f}x{window.height:.0f} native px "
              f"-> {out_width}x{out_height} px @ {resolution_m}m ...")

        data = src.read(1, window=window, out_shape=(out_height, out_width), resampling=Resampling.average)
        if src.nodata is not None:
            data = np.where(data == src.nodata, np.nan, data)

        transform = src.window_transform(window) * rasterio.Affine.scale(
            window.width / out_width, window.height / out_height
        )

        profile = {
            "driver": "GTiff", "height": out_height, "width": out_width,
            "count": 1, "dtype": "float32", "crs": src.crs, "transform": transform,
            "compress": "lzw", "nodata": np.nan,
        }
        with rasterio.open(out_path, "w", **profile) as dst:
            dst.write(data.astype("float32"), 1)

    elapsed = time.time() - t0
    size_mb = os.path.getsize(out_path) / 1e6
    valid = data[np.isfinite(data)]
    print(f"Wrote {out_path} ({size_mb:.1f} MB) in {elapsed:.1f}s -- "
          f"elevation range {np.nanmin(valid):.1f} to {np.nanmax(valid):.1f} m")
    return True


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--lon", type=float, required=True)
    ap.add_argument("--lat", type=float, required=True)
    ap.add_argument("--radius-km", type=float, default=30.0)
    ap.add_argument("--resolution-m", type=float, default=10.0)
    ap.add_argument("--dsm-url", default=DEFAULT_DSM_URL, help="local path or URL to the DSM (First Return)")
    ap.add_argument("--out", required=True)
    ap.add_argument("--force", action="store_true", help="re-fetch even if --out already exists")
    args = ap.parse_args()

    clip_dsm(args.lon, args.lat, args.out, args.radius_km, args.resolution_m, args.dsm_url, args.force)


if __name__ == "__main__":
    main()
