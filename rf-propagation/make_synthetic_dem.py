"""Generates a placeholder DEM + candidate site list for local testing.

This is ONLY here so the model is runnable out of the box. Replace with:
  - A real DEM: download USGS 3DEP (10m or 1/3 arc-second) for Vermont from
    https://apps.nationalmap.gov/downloader/ , or SRTM 30m via
    https://dwtkns.com/srtm30m/ -- clip/merge to a GeoTIFF covering your
    candidate sites + a margin, reproject to EPSG:4326 if needed.
  - Real candidate sites: in ArcGIS, add Lon/Lat fields to Candidate_Sites
    with Calculate Geometry (Point X/Y, EPSG:4326), then export the
    attribute table to CSV (name, lon, lat, height_above_surface_m).
"""
import numpy as np
import rasterio
from rasterio.transform import from_bounds

OUT_DEM = "example_data/synthetic_dem.tif"
OUT_SITES = "example_data/example_sites.csv"

# Roughly Burlington, VT and the foothills to the east (Green Mountains).
LON_MIN, LON_MAX = -73.35, -72.95
LAT_MIN, LAT_MAX = 44.30, 44.65
SIZE = 400  # pixels per side


def make_dem():
    """Synthesizes a fake elevation raster (lake lowland to the west, rising
    terrain with a few Gaussian hills to the east) and writes it as a
    north-up GeoTIFF in EPSG:4326."""
    lon = np.linspace(LON_MIN, LON_MAX, SIZE)
    lat = np.linspace(LAT_MIN, LAT_MAX, SIZE)
    lon_grid, lat_grid = np.meshgrid(lon, lat)

    # Lake Champlain lowland to the west, rising terrain to the east,
    # plus a few hill/ridge bumps so line-of-sight actually gets blocked.
    base = 40 + (lon_grid - LON_MIN) / (LON_MAX - LON_MIN) * 350

    def hill(lon0, lat0, height, sigma_deg):
        """Adds a Gaussian-shaped hill centered at (lon0, lat0)."""
        return height * np.exp(-(((lon_grid - lon0) ** 2 + (lat_grid - lat0) ** 2) / (2 * sigma_deg ** 2)))

    terrain = base.copy()
    terrain += hill(-73.05, 44.50, 220, 0.05)   # ridge north of Burlington
    terrain += hill(-73.00, 44.40, 260, 0.04)   # ridge east of downtown
    terrain += hill(-73.10, 44.35, 180, 0.06)
    terrain += hill(-73.20, 44.55, 90, 0.05)
    terrain += np.random.default_rng(42).normal(0, 4, terrain.shape)  # texture

    # flat, low lake surface west of Burlington's shoreline
    lake_mask = lon_grid < -73.28
    terrain[lake_mask] = 29.0

    terrain = terrain.astype("float32")

    transform = from_bounds(LON_MIN, LAT_MIN, LON_MAX, LAT_MAX, SIZE, SIZE)
    # meshgrid built lat increasing downward (row 0 = LAT_MIN), but a
    # north-up GeoTIFF needs row 0 = LAT_MAX -- flip rows to match.
    terrain_north_up = np.flipud(terrain)

    with rasterio.open(
        OUT_DEM, "w", driver="GTiff", height=SIZE, width=SIZE, count=1,
        dtype="float32", crs="EPSG:4326", transform=transform, nodata=-9999.0,
    ) as dst:
        dst.write(terrain_north_up, 1)

    print(f"wrote {OUT_DEM}")


def make_sites():
    """Writes a small CSV of illustrative fixed-node candidates around
    Burlington. Replace with your real Candidate_Sites export."""
    sites = [
        ("Downtown_Burlington", -73.2121, 44.4759, 12.0),
        ("Overlook_Ridge_East", -73.05, 44.50, 15.0),
        ("Winooski_Repeater", -73.1843, 44.4919, 10.0),
        ("South_End", -73.2270, 44.4489, 10.0),
        ("Ridge_Hilltop", -73.00, 44.40, 20.0),
    ]
    with open(OUT_SITES, "w") as f:
        f.write("name,lon,lat,height_above_surface_m\n")
        for name, lon, lat, h in sites:
            f.write(f"{name},{lon},{lat},{h}\n")
    print(f"wrote {OUT_SITES}")


if __name__ == "__main__":
    import os
    os.makedirs("example_data", exist_ok=True)
    make_dem()
    make_sites()
