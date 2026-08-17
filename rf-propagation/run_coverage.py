"""Example driver: point-to-point link budgets + a coverage map for one node.

Defaults point at the synthetic example data (run make_synthetic_dem.py
first). Swap --dem and --sites for your real USGS 3DEP DEM and your
exported Candidate_Sites CSV.
"""
import argparse
import csv
import os

from rf_model import DEM, LinkParams, compute_coverage, link_budget_point_to_point, plot_coverage, save_coverage_geotiff


def load_sites(path):
    """Reads a sites CSV (name, lon, lat, height_above_surface_m columns) into a list
    of (name, lon, lat, height_above_surface_m) tuples."""
    sites = []
    with open(path) as f:
        for row in csv.DictReader(f):
            height_str = row["height_above_surface_m"].strip()
            if not height_str:
                raise ValueError(
                    f"Site '{row['name']}' has no height_above_surface_m value in {path} -- "
                    f"fill in an antenna height for it before running the model."
                )
            sites.append((row["name"], float(row["lon"]), float(row["lat"]), float(height_str)))
    return sites


"""Runs one Tx site's point-to-point link budgets + coverage map against an
    already-loaded DEM and site list. Sites outside the DEM's actual extent
    are skipped (with a warning) rather than silently computing a wrong
    link budget from clamped edge-pixel elevation -- callers with sites
    spread across multiple regions should pass a DEM that only covers the
    area they actually clipped for that Tx site."""
def run_for_site(dem, sites, tx_name, out_dir, radius_km, resolution_m, azimuths):
    tx = next(s for s in sites if s[0] == tx_name)
    if not dem.contains_lonlat(tx[1], tx[2]):
        raise ValueError(f"Tx site '{tx_name}' falls outside the DEM's extent -- wrong DEM for this site?")

    print(f"\n--- Point-to-point link budgets from {tx_name} ---")
    for name, lon, lat, height_above_surface in sites:
        if name == tx_name:
            continue
        if not dem.contains_lonlat(lon, lat):
            print(f"{tx_name:22s} -> {name:22s} SKIPPED (outside this DEM's extent, not covered by this clip)")
            continue
        params = LinkParams(tx_height_above_surface_m=tx[3], rx_height_above_surface_m=height_above_surface)
        result = link_budget_point_to_point(dem, (tx[1], tx[2]), (lon, lat), params)
        status = "LOS " if result.is_los else "NLOS"
        verdict = "LINK OK" if result.margin_db > 0 else "LINK FAILS"
        print(
            f"{tx_name:22s} -> {name:22s} {status}  "
            f"dist={result.distance_m/1000:5.1f}km  path_loss={result.path_loss_db:6.1f}dB  "
            f"rx={result.received_power_dbm:7.1f}dBm  margin={result.margin_db:+6.1f}dB  {verdict}"
        )

    print(f"\nComputing coverage from {tx_name} out to {radius_km} km...")
    params = LinkParams(tx_height_above_surface_m=tx[3])
    coverage = compute_coverage(
        dem, tx[1], tx[2], params=params,
        radius_km=radius_km, resolution_m=resolution_m, n_azimuths=azimuths,
    )

    os.makedirs(out_dir, exist_ok=True)
    png_path = os.path.join(out_dir, f"{tx_name}_coverage.png")
    tif_path = os.path.join(out_dir, f"{tx_name}_coverage.tif")
    nearby_sites = [(s[0], s[1], s[2]) for s in sites if dem.contains_lonlat(s[1], s[2])]
    plot_coverage(coverage, png_path, candidate_sites=nearby_sites)
    save_coverage_geotiff(coverage, tif_path)
    print(f"Wrote {png_path}")
    print(f"Wrote {tif_path} (EPSG:4326 -- drag straight into your ArcGIS project)")


"""CLI entry point: parses args, loads the DEM and sites CSV once, then
    delegates to run_for_site for a single Tx site."""
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dem", default="example_data/synthetic_dem.tif")
    ap.add_argument("--sites", default="example_data/example_sites.csv")
    ap.add_argument("--tx-site", default=None, help="name of site to run coverage from (default: first site)")
    ap.add_argument("--radius-km", type=float, default=30.0)
    ap.add_argument("--resolution-m", type=float, default=250.0)
    ap.add_argument("--azimuths", type=int, default=72)
    ap.add_argument("--out-dir", default="output")
    args = ap.parse_args()

    print(f"Loading DEM from {args.dem}")
    dem = DEM(args.dem)

    sites = load_sites(args.sites)
    print(f"Loaded {len(sites)} candidate sites from {args.sites}")

    tx_name = args.tx_site or sites[0][0]
    run_for_site(dem, sites, tx_name, args.out_dir, args.radius_km, args.resolution_m, args.azimuths)


if __name__ == "__main__":
    main()
