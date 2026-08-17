"""Runs the coverage model once for every site in sites.csv, reusing one
DEM load per unique location (see clip_sites.group_by_location) rather
than per site -- sites sharing a location (e.g. height variants) share
the DEM object in memory, not just the file on disk.

Expects clip_sites.py to have already produced a data/<location>_dsm.tif
for every location (run that first if any are missing).
"""
import argparse
import os

from clip_sites import group_by_location, load_sites as load_site_coords, safe_filename
from rf_model import DEM
from run_coverage import load_sites, run_for_site


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--sites", default="../sites.csv")
    ap.add_argument("--data-dir", default="data")
    ap.add_argument("--radius-km", type=float, default=30.0)
    ap.add_argument("--resolution-m", type=float, default=250.0)
    ap.add_argument("--azimuths", type=int, default=72)
    ap.add_argument("--out-dir", default="output")
    args = ap.parse_args()

    sites = load_sites(args.sites)
    locations = group_by_location(load_site_coords(args.sites))
    print(f"Loaded {len(sites)} sites across {len(locations)} location(s)\n")

    missing = []
    for loc in locations:
        dem_path = os.path.join(args.data_dir, f"{safe_filename(loc['label'])}_dsm.tif")
        if not os.path.exists(dem_path):
            missing.append((loc["label"], dem_path))
    if missing:
        print("Missing DSM file(s) -- run clip_sites.py first for these locations:")
        for label, path in missing:
            print(f"  {label}: expected {path}")
        return

    for loc in locations:
        dem_path = os.path.join(args.data_dir, f"{safe_filename(loc['label'])}_dsm.tif")
        print(f"===== {loc['label']} ({dem_path}) =====")
        dem = DEM(dem_path)
        for site_name in loc["names"]:
            run_for_site(dem, sites, site_name, args.out_dir, args.radius_km, args.resolution_m, args.azimuths)
        print()


if __name__ == "__main__":
    main()
