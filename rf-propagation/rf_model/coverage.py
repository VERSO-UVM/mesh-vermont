"""Radial coverage prediction around a single fixed (transmitting) node.

For a ring of azimuths around the Tx site, walks outward along each
azimuth sampling the DEM, and at each step computes the terrain-aware
path loss back to the origin using the single-knife-edge model in
propagation.py. This mirrors how tools like SPLAT! do radial coverage
prediction -- each azimuth ray only needs one DEM sweep, and the worst
obstruction "so far" is reused for every point further out along the ray.

The result is a set of polar samples (azimuth, distance, received power)
which get rasterized onto a regular lon/lat grid for viewing or export.
"""
from __future__ import annotations

import numpy as np
import pyproj
from scipy.interpolate import griddata

from . import propagation as prop
from .propagation import LinkParams

"""Walks outward from the Tx along a single azimuth, sampling the DEM
    once for the whole ray, then computes received power at each distance
    step using the terrain profile accumulated so far (so the worst
    obstruction before each point is reused instead of resampling)."""

def _ray_received_power(dem, tx_lon, tx_lat, tx_elev, azimuth_deg, distances_m, params: LinkParams):
    geod = pyproj.Geod(ellps="WGS84")
    n = len(distances_m)
    lons, lats, _ = geod.fwd(
        np.full(n, tx_lon), np.full(n, tx_lat), np.full(n, azimuth_deg), distances_m
    )
    elevations = dem.elevation_at_lonlat_arrays(np.asarray(lons), np.asarray(lats))

    tx_total_height = tx_elev + params.tx_height_above_surface_m
    wavelength = prop.C / (params.freq_mhz * 1e6)

    all_distances = np.concatenate(([0.0], distances_m))
    all_elevations = np.concatenate(([tx_elev], elevations))

    received = np.empty(n)
    for k in range(n):
        d_k = distances_m[k]
        rx_total_height = elevations[k] + params.rx_height_above_surface_m
        v_max = prop.worst_case_diffraction_v(
            all_distances[: k + 2], all_elevations[: k + 2], tx_total_height, rx_total_height, wavelength
        )
        fspl = float(prop.free_space_path_loss_db(d_k, params.freq_mhz))
        diff_loss = float(prop.knife_edge_diffraction_loss_db(v_max)[0])
        path_loss = fspl + diff_loss
        received[k] = (
            params.tx_power_dbm
            + params.tx_antenna_gain_dbi
            + params.rx_antenna_gain_dbi
            - path_loss
            - params.cable_loss_db
        )

    return np.asarray(lons), np.asarray(lats), received


"""Compute received-power samples on a ring/radial grid around a Tx site.

    Returns a dict with the raw polar samples (lons, lats, received_power_dbm)
    -- pass this to save_coverage_geotiff or plot_coverage to visualize it.
    """
def compute_coverage(
    dem,
    tx_lon: float,
    tx_lat: float,
    params: LinkParams = LinkParams(),
    radius_km: float = 30.0,
    resolution_m: float = 200.0,
    n_azimuths: int = 72,
):
    tx_elev = dem.elevation_at_lonlat(tx_lon, tx_lat)
    distances_m = np.arange(resolution_m, radius_km * 1000.0 + resolution_m, resolution_m)
    azimuths = np.linspace(0, 360, n_azimuths, endpoint=False)

    all_lons, all_lats, all_power = [], [], []
    for az in azimuths:
        lons, lats, received = _ray_received_power(dem, tx_lon, tx_lat, tx_elev, az, distances_m, params)
        all_lons.append(lons)
        all_lats.append(lats)
        all_power.append(received)

    return {
        "tx_lon": tx_lon,
        "tx_lat": tx_lat,
        "lons": np.concatenate(all_lons),
        "lats": np.concatenate(all_lats),
        "received_power_dbm": np.concatenate(all_power),
        "rx_sensitivity_dbm": params.rx_sensitivity_dbm,
        "radius_km": radius_km,
    }

"""Interpolates the polar (azimuth/distance) coverage samples onto a
    regular lon/lat grid via linear interpolation, falling back to
    nearest-neighbor outside the sample convex hull so the whole grid
    (including corners beyond the radial sweep) is filled."""
def _rasterize(coverage, grid_resolution_deg=None, grid_size=400):
    lons, lats, power = coverage["lons"], coverage["lats"], coverage["received_power_dbm"]
    lon_min, lon_max = lons.min(), lons.max()
    lat_min, lat_max = lats.min(), lats.max()

    if grid_resolution_deg:
        grid_lon = np.arange(lon_min, lon_max, grid_resolution_deg)
        grid_lat = np.arange(lat_min, lat_max, grid_resolution_deg)
    else:
        grid_lon = np.linspace(lon_min, lon_max, grid_size)
        grid_lat = np.linspace(lat_min, lat_max, grid_size)

    grid_x, grid_y = np.meshgrid(grid_lon, grid_lat)
    grid_power = griddata((lons, lats), power, (grid_x, grid_y), method="linear")

    # fill area outside the convex hull of samples (griddata linear -> NaN)
    nearest = griddata((lons, lats), power, (grid_x, grid_y), method="nearest")
    grid_power = np.where(np.isnan(grid_power), nearest, grid_power)

    return grid_lon, grid_lat, grid_power

"""Rasterize polar samples to an even lon/lat grid and write a GeoTIFF
    (EPSG:4326) that can be dragged directly into an ArcGIS project."""
def save_coverage_geotiff(coverage, out_path: str, grid_size: int = 400):
    import rasterio
    from rasterio.transform import from_bounds

    grid_lon, grid_lat, grid_power = _rasterize(coverage, grid_size=grid_size)

    transform = from_bounds(
        grid_lon.min(), grid_lat.min(), grid_lon.max(), grid_lat.max(),
        grid_power.shape[1], grid_power.shape[0],
    )
    # north-up rasters need row 0 = max latitude
    grid_power_flipped = np.flipud(grid_power)

    with rasterio.open(
        out_path, "w", driver="GTiff",
        height=grid_power_flipped.shape[0], width=grid_power_flipped.shape[1],
        count=1, dtype="float32", crs="EPSG:4326", transform=transform, nodata=np.nan,
    ) as dst:
        dst.write(grid_power_flipped.astype("float32"), 1)

"""Quick-look matplotlib PNG: received power relative to Rx sensitivity.

    LoRa receivers are extremely sensitive, so margin often stays strongly
    positive even well past 20-30 km NLOS -- the color scale auto-ranges to
    the actual margin spread (always including 0 dB) unless you override
    vmin/vmax, otherwise a fixed +-20 dB scale washes out to solid green.
    """
def plot_coverage(coverage, out_path: str, grid_size: int = 400, candidate_sites=None, vmin=None, vmax=None):
    import matplotlib.pyplot as plt

    grid_lon, grid_lat, grid_power = _rasterize(coverage, grid_size=grid_size)
    margin = grid_power - coverage["rx_sensitivity_dbm"]

    if vmin is None:
        vmin = min(0.0, float(np.nanpercentile(margin, 1)))
    if vmax is None:
        vmax = max(0.0, float(np.nanpercentile(margin, 99)))

    fig, ax = plt.subplots(figsize=(8, 7))
    im = ax.pcolormesh(grid_lon, grid_lat, margin, shading="auto", cmap="RdYlGn", vmin=vmin, vmax=vmax)
    ax.contour(grid_lon, grid_lat, margin, levels=[0], colors="black", linewidths=1.5)
    fig.colorbar(im, ax=ax, label="Link margin over Rx sensitivity (dB)")
    ax.plot(coverage["tx_lon"], coverage["tx_lat"], marker="^", color="black", markersize=10, label="Tx node")

    if candidate_sites:
        for name, lon, lat in candidate_sites:
            ax.plot(lon, lat, marker="o", color="blue", markersize=5)
            ax.annotate(name, (lon, lat), fontsize=8, xytext=(3, 3), textcoords="offset points")

    ax.set_xlabel("Longitude")
    ax.set_ylabel("Latitude")
    ax.set_title(f"Predicted coverage, {coverage['radius_km']:.0f} km radius (0 dB = at sensitivity limit)")
    ax.legend(loc="upper right")
    ax.set_aspect("equal")
    fig.tight_layout()
    fig.savefig(out_path, dpi=150)
    plt.close(fig)
