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
    """Reads a sites CSV (name, lon, lat, height_agl_m columns) into a list
    of (name, lon, lat, height_agl_m) tuples."""
    sites = []
    with open(path) as f:
        for row in csv.DictReader(f):
            sites.append((row["name"], float(row["lon"]), float(row["lat"]), float(row["height_agl_m"])))
    return sites


"""CLI entry point: parses args, prints point-to-point link budgets from
    the Tx site to every other site, then computes and saves a coverage
    map (PNG + GeoTIFF) radiating out from the Tx site."""
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

    os.makedirs(args.out_dir, exist_ok=True)

    print(f"Loading DEM from {args.dem}")
    dem = DEM(args.dem)

    sites = load_sites(args.sites)
    print(f"Loaded {len(sites)} candidate sites from {args.sites}")

    tx_name = args.tx_site or sites[0][0]
    tx = next(s for s in sites if s[0] == tx_name)

    print("\n--- Point-to-point link budgets from", tx_name, "---")
    for name, lon, lat, height_agl in sites:
        if name == tx_name:
            continue
        params = LinkParams(tx_height_agl_m=tx[3], rx_height_agl_m=height_agl)
        result = link_budget_point_to_point(dem, (tx[1], tx[2]), (lon, lat), params)
        status = "LOS " if result.is_los else "NLOS"
        verdict = "LINK OK" if result.margin_db > 0 else "LINK FAILS"
        print(
            f"{tx_name:22s} -> {name:22s} {status}  "
            f"dist={result.distance_m/1000:5.1f}km  path_loss={result.path_loss_db:6.1f}dB  "
            f"rx={result.received_power_dbm:7.1f}dBm  margin={result.margin_db:+6.1f}dB  {verdict}"
        )

    print(f"\nComputing coverage from {tx_name} out to {args.radius_km} km...")
    params = LinkParams(tx_height_agl_m=tx[3])
    coverage = compute_coverage(
        dem, tx[1], tx[2], params=params,
        radius_km=args.radius_km, resolution_m=args.resolution_m, n_azimuths=args.azimuths,
    )

    png_path = os.path.join(args.out_dir, f"{tx_name}_coverage.png")
    tif_path = os.path.join(args.out_dir, f"{tx_name}_coverage.tif")
    plot_coverage(coverage, png_path, candidate_sites=[(s[0], s[1], s[2]) for s in sites])
    save_coverage_geotiff(coverage, tif_path)
    print(f"Wrote {png_path}")
    print(f"Wrote {tif_path} (EPSG:4326 -- drag straight into your ArcGIS project)")


if __name__ == "__main__":
    main()
