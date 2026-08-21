"""Runs the coverage model once for every site in sites.csv, reusing one
DEM load per unique location (see clip_sites.group_by_location) rather
than per site -- sites sharing a location (e.g. height variants) share
the DEM object in memory, not just the file on disk.

Expects clip_sites.py to have already produced a
data/<location>_<dsm-radius-km>km_<dsm-resolution-m>m_dsm.tif for every
location (run that first if any are missing). --dsm-radius-km/
--dsm-resolution-m must match whatever clip_sites.py was run with -- they
identify which DSM file to load, and are independent of --radius-km/
--resolution-m below, which control the coverage model's own sampling.

Pass --dem to skip the per-location lookup entirely and run every site
against one shared DSM instead (e.g. a single wide clip_dsm.py clip like
camels_hump_50km_5m_dsm.tif that already covers every site) -- loaded
once, since one rasterio dataset can safely answer elevation queries for
sites anywhere within its extent.
"""
import argparse
import os

from clip_sites import dsm_filename, group_by_location, load_sites as load_site_coords
from rf_model import DEM
from run_coverage import load_radios, load_sites, run_for_site


def main():
    """CLI entry point: verifies every location's DSM clip already exists
    (bailing out with a helpful message if not), then runs the coverage
    model for every site, loading each location's DEM only once."""
    ap = argparse.ArgumentParser()
    ap.add_argument("--sites", default="../sites.csv")
    ap.add_argument("--radios", default="../radios.csv", help="radio profiles CSV")
    ap.add_argument("--data-dir", default="data")
    ap.add_argument(
        "--dem", default=None,
        help="use this single DEM/DSM for every site instead of per-location clips "
             "(e.g. data/camels_hump_50km_5m_dsm.tif)",
    )
    ap.add_argument("--dsm-radius-km", type=float, default=30.0, help="radius clip_sites.py was run with")
    ap.add_argument("--dsm-resolution-m", type=float, default=10.0, help="resolution clip_sites.py was run with")
    ap.add_argument("--radius-km", type=float, default=30.0, help="coverage model's own sweep radius")
    ap.add_argument("--resolution-m", type=float, default=250.0, help="coverage model's own sample spacing")
    ap.add_argument("--azimuths", type=int, default=72)
    ap.add_argument("--out-dir", default="output")
    args = ap.parse_args()

    sites = load_sites(args.sites)
    radios = load_radios(args.radios)
    print(f"Loaded {len(radios)} radio profile(s) from {args.radios}")

    if args.dem:
        # Single shared DSM path: skip the per-location file lookup and run
        # every site in sites.csv as a Tx node against the one DEM. Sites
        # that fall outside its extent still error out clearly via
        # run_for_site's contains_lonlat check rather than silently
        # producing a wrong result off clamped edge pixels.
        print(f"Loading shared DEM from {args.dem}")
        dem = DEM(args.dem)
        print(f"Loaded {len(sites)} sites from {args.sites}\n")
        for site_name, *_ in sites:
            print(f"===== {site_name} =====")
            run_for_site(dem, sites, radios, site_name, args.out_dir, args.radius_km, args.resolution_m, args.azimuths)
            print()
        return

    locations = group_by_location(load_site_coords(args.sites))
    print(f"Loaded {len(sites)} sites across {len(locations)} location(s)\n")

    missing = []
    for loc in locations:
        dem_path = os.path.join(
            args.data_dir, dsm_filename(loc["label"], args.dsm_radius_km, args.dsm_resolution_m)
        )
        if not os.path.exists(dem_path):
            missing.append((loc["label"], dem_path))
    if missing:
        print("Missing DSM file(s) -- run clip_sites.py first for these locations:")
        for label, path in missing:
            print(f"  {label}: expected {path}")
        return

    for loc in locations:
        dem_path = os.path.join(
            args.data_dir, dsm_filename(loc["label"], args.dsm_radius_km, args.dsm_resolution_m)
        )
        print(f"===== {loc['label']} ({dem_path}) =====")
        dem = DEM(dem_path)
        for site_name in loc["names"]:
            run_for_site(dem, sites, radios, site_name, args.out_dir, args.radius_km, args.resolution_m, args.azimuths)
        print()


if __name__ == "__main__":
    main()
