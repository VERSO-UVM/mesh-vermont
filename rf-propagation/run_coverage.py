"""Example driver: point-to-point link budgets + a coverage map for one node.

Defaults point at the synthetic example data (run make_synthetic_dem.py
first). Swap --dem and --sites for your real USGS 3DEP DEM and your
exported Candidate_Sites CSV.
"""
import argparse
import csv
import os

from clip_sites import location_name
from rf_model import (
    DEM,
    MESHTASTIC_DEFAULTS,
    LinkParams,
    compute_coverage,
    link_budget_point_to_point,
    plot_coverage,
    save_coverage_geotiff,
)

# Everything a LinkParams needs except antenna height, which stays per-site
# in sites.csv (the same radio can be mounted at different heights).
RADIO_FIELDS = (
    "freq_mhz", "tx_power_dbm", "tx_antenna_gain_dbi",
    "rx_antenna_gain_dbi", "rx_sensitivity_dbm", "cable_loss_db",
)


def load_sites(path):
    """Reads a sites CSV (name, lon, lat, height_above_surface_m, radio
    columns) into a list of (name, lon, lat, height_above_surface_m, radio)
    tuples. radio is the row's `radio` column verbatim, or "" if the column
    is missing/blank -- resolved against radios.csv by _radio_fields."""
    sites = []
    with open(path) as f:
        for row in csv.DictReader(f):
            height_str = row["height_above_surface_m"].strip()
            if not height_str:
                raise ValueError(
                    f"Site '{row['name']}' has no height_above_surface_m value in {path} -- "
                    f"fill in an antenna height for it before running the model."
                )
            radio = (row.get("radio") or "").strip()
            sites.append((row["name"], float(row["lon"]), float(row["lat"]), float(height_str), radio))
    return sites


def load_radios(path):
    """Reads a radios CSV (name + RADIO_FIELDS columns) into a dict of
    name -> field dict, for looking up a site's radio parameters by name."""
    radios = {}
    with open(path) as f:
        for row in csv.DictReader(f):
            radios[row["name"].strip()] = {field: float(row[field]) for field in RADIO_FIELDS}
    return radios


def _radio_fields(radios, radio_name, site_name):
    """Looks up a radio's LinkParams field overrides by name. Sites with no
    radio column/value fall back to MESHTASTIC_DEFAULTS, so a sites CSV
    without a `radio` column still runs (just without per-radio tuning)."""
    if not radio_name:
        return MESHTASTIC_DEFAULTS
    if radio_name not in radios:
        raise ValueError(
            f"Site '{site_name}' references radio '{radio_name}', which isn't in radios.csv -- "
            f"add a row for it or fix the typo."
        )
    return radios[radio_name]


def _dedupe_by_location(sites_3tuple, precision=5):
    """Collapses sites sharing the same (rounded) lon/lat down to a single
    labeled point, stripping the height-variant suffix (see
    clip_sites.location_name) from the label. Height-variant sites (e.g.
    Mansfield_1.1_1m/_1.2_5m/_1.3_10m) would otherwise plot as overlapping,
    unreadable markers/text at the exact same map position -- this is only
    for the plotted markers, not the point-to-point link budgets above,
    which still evaluate every individual site."""
    seen = set()
    out = []
    for name, lon, lat in sites_3tuple:
        key = (round(lon, precision), round(lat, precision))
        if key in seen:
            continue
        seen.add(key)
        out.append((location_name(name), lon, lat))
    return out


def run_for_site(dem, sites, radios, tx_name, out_dir, radius_km, resolution_m, azimuths):
    """Runs one Tx site's point-to-point link budgets + coverage map against an
    already-loaded DEM and site list. Sites outside the DEM's actual extent
    are skipped (with a warning) rather than silently computing a wrong
    link budget from clamped edge-pixel elevation -- callers with sites
    spread across multiple regions should pass a DEM that only covers the
    area they actually clipped for that Tx site.

    Each link budget uses the Tx site's radio for freq/tx_power/tx_gain/
    cable_loss and the Rx site's radio for rx_gain/rx_sensitivity, so
    sites running different radios still get a correct one-directional
    link budget for that direction."""
    # next(...) raises StopIteration (via the generator) if tx_name isn't in
    # sites -- deliberately unguarded so a typo'd --tx-site fails loudly.
    tx = next(s for s in sites if s[0] == tx_name)
    if not dem.contains_lonlat(tx[1], tx[2]):
        raise ValueError(f"Tx site '{tx_name}' falls outside the DEM's extent -- wrong DEM for this site?")
    tx_radio = _radio_fields(radios, tx[4], tx[0])

    print(f"\n--- Point-to-point link budgets from {tx_name} ---")
    for name, lon, lat, height_above_surface, radio_name in sites:
        if name == tx_name:
            continue
        if not dem.contains_lonlat(lon, lat):
            print(f"{tx_name:22s} -> {name:22s} SKIPPED (outside this DEM's extent, not covered by this clip)")
            continue
        rx_radio = _radio_fields(radios, radio_name, name)
        params = LinkParams(
            freq_mhz=tx_radio["freq_mhz"],
            tx_power_dbm=tx_radio["tx_power_dbm"],
            tx_antenna_gain_dbi=tx_radio["tx_antenna_gain_dbi"],
            rx_antenna_gain_dbi=rx_radio["rx_antenna_gain_dbi"],
            rx_sensitivity_dbm=rx_radio["rx_sensitivity_dbm"],
            cable_loss_db=tx_radio["cable_loss_db"],
            tx_height_above_surface_m=tx[3],
            rx_height_above_surface_m=height_above_surface,
        )
        result = link_budget_point_to_point(dem, (tx[1], tx[2]), (lon, lat), params)
        status = "LOS " if result.is_los else "NLOS"
        verdict = "LINK OK" if result.margin_db > 0 else "LINK FAILS"
        print(
            f"{tx_name:22s} -> {name:22s} {status}  "
            f"dist={result.distance_m/1000:5.1f}km  path_loss={result.path_loss_db:6.1f}dB  "
            f"rx={result.received_power_dbm:7.1f}dBm  margin={result.margin_db:+6.1f}dB  {verdict}"
        )

    print(f"\nComputing coverage from {tx_name} out to {radius_km} km...")
    # No specific Rx site for a coverage sweep, so assume the same radio
    # model is listening on the far end (Tx site's own radio for every field).
    params = LinkParams(
        freq_mhz=tx_radio["freq_mhz"],
        tx_power_dbm=tx_radio["tx_power_dbm"],
        tx_antenna_gain_dbi=tx_radio["tx_antenna_gain_dbi"],
        rx_antenna_gain_dbi=tx_radio["rx_antenna_gain_dbi"],
        rx_sensitivity_dbm=tx_radio["rx_sensitivity_dbm"],
        cable_loss_db=tx_radio["cable_loss_db"],
        tx_height_above_surface_m=tx[3],
    )
    coverage = compute_coverage(
        dem, tx[1], tx[2], params=params,
        radius_km=radius_km, resolution_m=resolution_m, n_azimuths=azimuths,
    )

    os.makedirs(out_dir, exist_ok=True)
    png_path = os.path.join(out_dir, f"{tx_name}_coverage.png")
    tif_path = os.path.join(out_dir, f"{tx_name}_coverage.tif")
    nearby_sites = [(s[0], s[1], s[2]) for s in sites if dem.contains_lonlat(s[1], s[2])]
    plot_coverage(coverage, png_path, candidate_sites=_dedupe_by_location(nearby_sites))
    save_coverage_geotiff(coverage, tif_path)
    print(f"Wrote {png_path}")
    print(f"Wrote {tif_path} (EPSG:4326 -- drag straight into your ArcGIS project)")


def main():
    """CLI entry point: parses args, loads the DEM and sites CSV once, then
    delegates to run_for_site for a single Tx site."""
    ap = argparse.ArgumentParser()
    ap.add_argument("--dem", default="example_data/synthetic_dem.tif")
    ap.add_argument("--sites", default="example_data/example_sites.csv")
    ap.add_argument("--radios", default="example_data/example_radios.csv", help="radio profiles CSV")
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
    radios = load_radios(args.radios)
    print(f"Loaded {len(radios)} radio profile(s) from {args.radios}")

    tx_name = args.tx_site or sites[0][0]
    run_for_site(dem, sites, radios, tx_name, args.out_dir, args.radius_km, args.resolution_m, args.azimuths)


if __name__ == "__main__":
    main()
