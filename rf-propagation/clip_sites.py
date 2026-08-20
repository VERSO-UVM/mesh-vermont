"""Ensures a clipped DSM exists for every unique location in sites.csv,
fetching only the ones that are missing -- safe to re-run any time you add
a new candidate site, since existing files are skipped (see
clip_dsm.clip_dsm).

Multiple sites at the same lon/lat (e.g. testing several antenna heights
at one physical location) share a single DSM clip -- the DSM only encodes
ground/surface elevation, which doesn't change with antenna height, so
there's no reason to fetch it more than once per location.
"""
import argparse
import csv
import os
import re

from clip_dsm import DEFAULT_DSM_URL, clip_dsm

# Strips a trailing ".<n>_<height>m" height-variant suffix while keeping
# the location index before the dot, e.g. "Mansfield_2.3_10m" ->
# "Mansfield_2" (not "Mansfield" -- there are 3 distinct Mansfield
# locations, only the part after the dot distinguishes height variants).
_HEIGHT_VARIANT_SUFFIX = re.compile(r"\.\d+_\d+m$")


def load_sites(path):
    """Reads a sites CSV (name, lon, lat columns) into a list of
    (name, lon, lat) tuples."""
    sites = []
    with open(path) as f:
        for row in csv.DictReader(f):
            sites.append((row["name"], float(row["lon"]), float(row["lat"])))
    return sites


def safe_filename(name):
    """Collapses any run of characters unsafe for a filename into a single
    underscore, so a site/location label can be used directly as a path
    component."""
    return re.sub(r"[^A-Za-z0-9_-]+", "_", name.strip())


def location_name(site_name):
    """Strips the height-variant suffix (see _HEIGHT_VARIANT_SUFFIX) from a
    site name, leaving the shared physical-location label."""
    return _HEIGHT_VARIANT_SUFFIX.sub("", site_name)


def dsm_filename(label, radius_km, resolution_m):
    """Builds the output filename for a location's DSM clip, e.g.
    "camels_hump_50km_5m_dsm.tif" -- radius/resolution are baked into the
    name so clips of the same location at different sizes/resolutions
    don't collide, and the file's provenance is clear at a glance. Values
    are formatted with %g so whole numbers print without a trailing
    ".0" (30km, not 30.0km) while fractional ones keep their precision."""
    return f"{safe_filename(label)}_{radius_km:g}km_{resolution_m:g}m_dsm.tif"


def group_by_location(sites, precision=5):
    """Groups sites sharing the same (rounded) lon/lat, using the first
    site's location_name() as the group's label. Returns a list of
    (label, lon, lat, [site names at this location])."""
    groups = {}
    order = []
    for name, lon, lat in sites:
        # Round to `precision` decimal degrees (~1m at 5dp) so sites at the
        # "same" physical location but with float-rounding differences in
        # their CSV coordinates still group together.
        key = (round(lon, precision), round(lat, precision))
        if key not in groups:
            groups[key] = {"label": location_name(name), "lon": lon, "lat": lat, "names": []}
            order.append(key)
        groups[key]["names"].append(name)
    return [groups[k] for k in order]


def main():
    """CLI entry point: loads sites.csv, groups sites into unique
    locations, and fetches a DSM clip for each location that doesn't
    already have one on disk."""
    ap = argparse.ArgumentParser()
    ap.add_argument("--sites", default="../sites.csv")
    ap.add_argument("--radius-km", type=float, default=30.0)
    ap.add_argument("--resolution-m", type=float, default=10.0)
    ap.add_argument("--dsm-url", default=DEFAULT_DSM_URL)
    ap.add_argument("--out-dir", default="data")
    ap.add_argument("--force", action="store_true", help="re-fetch even for locations that already have a file")
    args = ap.parse_args()

    os.makedirs(args.out_dir, exist_ok=True)
    sites = load_sites(args.sites)
    locations = group_by_location(sites)
    print(f"Loaded {len(sites)} sites from {args.sites} -> {len(locations)} unique location(s)\n")

    for loc in locations:
        out_path = os.path.join(args.out_dir, dsm_filename(loc["label"], args.radius_km, args.resolution_m))
        names = ", ".join(loc["names"])
        print(f"--- {loc['label']} ({loc['lon']}, {loc['lat']}) [{names}] -> {out_path} ---")
        clip_dsm(loc["lon"], loc["lat"], out_path, args.radius_km, args.resolution_m, args.dsm_url, args.force)
        print()


if __name__ == "__main__":
    main()
