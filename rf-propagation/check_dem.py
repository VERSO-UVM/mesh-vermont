"""Pre-flight sanity check for a DEM before running the coverage model.

Run this the moment you export a clipped DEM from ArcGIS -- catches the
most common problems (wrong dataset, huge file, bad CRS) in seconds,
instead of finding out partway through a slow coverage run.
"""
import argparse
import sys

import numpy as np
import rasterio


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("dem_path")
    args = ap.parse_args()

    problems = []

    with rasterio.open(args.dem_path) as ds:
        n_pixels = ds.width * ds.height
        print(f"CRS: {ds.crs}")
        print(f"Size: {ds.width} x {ds.height} px  ({n_pixels/1e6:.1f} million pixels)")
        print(f"Resolution: {ds.res[0]:.2f} x {ds.res[1]:.2f} (in CRS units)")
        print(f"Bounds: {ds.bounds}")
        print(f"Nodata: {ds.nodata}")

        if n_pixels > 200_000_000:
            problems.append(
                f"Raster has {n_pixels/1e6:.0f}M pixels -- the model loads the whole band into "
                f"memory and this will be very slow or hang. Re-export at a coarser resolution "
                f"(10-30m is plenty for a 30km-radius RF coverage run)."
            )

        band = ds.read(1)
        nodata = ds.nodata
        valid = band[band != nodata] if nodata is not None else band
        valid = valid[np.isfinite(valid)]

        if valid.size == 0:
            problems.append("No valid (non-nodata) pixels found.")
        else:
            vmin, vmax, vmed = float(np.min(valid)), float(np.max(valid)), float(np.median(valid))
            print(f"Value range: {vmin:.1f} to {vmax:.1f}  (median {vmed:.1f})")

            if -50 <= vmed <= 50 and vmax < 100:
                problems.append(
                    f"Median value is {vmed:.1f} and max is {vmax:.1f} -- this looks like an "
                    f"nDSM (object heights above ground: 0 for bare ground, ~10-30 for "
                    f"buildings/trees), NOT absolute elevation. This will flatten all real "
                    f"terrain (hills/ridges) in the model. You want a DEM or DSM with values "
                    f"in the range of actual ground elevation (tens to hundreds of meters for "
                    f"Vermont)."
                )

    print()
    if problems:
        print("ISSUES FOUND:")
        for p in problems:
            print(f"  - {p}")
        sys.exit(1)
    else:
        print("Looks good -- ready to use with run_coverage.py --dem", args.dem_path)


if __name__ == "__main__":
    main()
