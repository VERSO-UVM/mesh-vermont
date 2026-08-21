"""Merges multiple per-site coverage GeoTIFFs (from run_coverage.py /
run_all_sites.py) into one raster covering the whole network, taking the
strongest (max) received power at every pixel where sites' discs overlap
-- i.e. "whichever site would actually serve you best here."

Each per-site GeoTIFF already has its area outside that site's own sweep
radius masked to NaN/nodata (see rf_model.coverage._rasterize), so a plain
elementwise max across the merged inputs is not the same as this: NaN
cells correctly fall back to whichever other input actually has data
there, rather than winning/losing the max comparison. rasterio.merge
handles that nodata masking natively -- confirmed here rather than
assumed.
"""
import argparse
import glob
import os

import numpy as np
import rasterio
from rasterio.merge import merge


def merge_coverage(input_paths, out_path, method="max"):
    """Merges the GeoTIFFs at input_paths into a single raster at out_path
    using the given rasterio.merge method ("max" for strongest-signal-wins),
    respecting each input's own NaN/nodata mask. Returns (merged_array,
    transform, crs) for the caller to inspect/plot."""
    if not input_paths:
        raise ValueError("No input coverage GeoTIFFs given -- nothing to merge.")

    srcs = [rasterio.open(p) for p in input_paths]
    try:
        crs = srcs[0].crs
        merged, transform = merge(srcs, method=method, nodata=np.nan)
    finally:
        for s in srcs:
            s.close()

    profile = {
        "driver": "GTiff", "height": merged.shape[1], "width": merged.shape[2],
        "count": 1, "dtype": "float32", "crs": crs, "transform": transform, "nodata": np.nan,
    }
    os.makedirs(os.path.dirname(out_path) or ".", exist_ok=True)
    with rasterio.open(out_path, "w", **profile) as dst:
        dst.write(merged[0].astype("float32"), 1)

    return merged[0], transform, crs


def main():
    """CLI entry point: globs per-site coverage GeoTIFFs, merges them
    taking the max (or --method) value per pixel, and writes the result."""
    ap = argparse.ArgumentParser()
    ap.add_argument(
        "--inputs", default="output/*_coverage.tif",
        help="glob pattern for per-site coverage GeoTIFFs to merge",
    )
    ap.add_argument("--out", default="output/coverage_combined.tif")
    ap.add_argument(
        "--method", default="max", choices=["max", "min", "first", "last"],
        help="max = strongest signal wins per pixel (the usual choice for network coverage)",
    )
    args = ap.parse_args()

    input_paths = sorted(p for p in glob.glob(args.inputs) if os.path.abspath(p) != os.path.abspath(args.out))
    print(f"Merging {len(input_paths)} coverage raster(s):")
    for p in input_paths:
        print(f"  {p}")

    merged, _, _ = merge_coverage(input_paths, args.out, args.method)

    valid = merged[np.isfinite(merged)]
    print(f"\nWrote {args.out}")
    if valid.size:
        print(f"Combined coverage: {valid.size} valid px, "
              f"received power {valid.min():.1f} to {valid.max():.1f} dBm")


if __name__ == "__main__":
    main()
