"""Path-loss physics: free-space loss + single knife-edge terrain diffraction.

Model summary
-------------
1. Free-space path loss (FSPL) from distance and frequency.
2. Sample terrain elevation along the great-circle path between Tx and Rx.
3. Find the point along that profile with the worst Fresnel-zone
   intrusion (accounting for a 4/3-effective-earth-radius curvature
   bulge), and convert it to a diffraction parameter v.
4. Add ITU-R P.526 single-knife-edge diffraction loss on top of FSPL when
   the path isn't clear.

This is a single-edge approximation (not multi-edge Deygout correction) -
adequate for site-planning purposes, not a substitute for a licensed
propagation tool for anything safety-critical.
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pyproj

C = 299_792_458.0  # speed of light, m/s
EARTH_RADIUS_M = 6_371_000.0
K_FACTOR = 4.0 / 3.0  # standard effective-earth-radius factor

# Representative defaults for a Meshtastic LongFast (US915) node. Tune per
# your actual radio config -- these are reasonable planning-grade values,
# not measured for a specific device.
MESHTASTIC_DEFAULTS = dict(
    freq_mhz=915.0,
    tx_power_dbm=27.0,  # ~500 mW; Part 15 allows up to 30 dBm (1 W)
    tx_antenna_gain_dbi=3.0,  # typical omni whip on a fixed node
    rx_antenna_gain_dbi=3.0,
    tx_height_above_surface_m=10.0,  # fixed/repeater node mounted on a pole or roof
    rx_height_above_surface_m=2.0,  # handheld / vehicle-mounted node
    rx_sensitivity_dbm=-129.0,  # SX1262, LongFast preset (SF11/BW250) typical
    cable_loss_db=0.5,
)


@dataclass
class LinkParams:
    """Radio + antenna configuration for a link budget calculation. Defaults
    to MESHTASTIC_DEFAULTS; override individual fields per site/radio."""

    freq_mhz: float = MESHTASTIC_DEFAULTS["freq_mhz"]
    tx_power_dbm: float = MESHTASTIC_DEFAULTS["tx_power_dbm"]
    tx_antenna_gain_dbi: float = MESHTASTIC_DEFAULTS["tx_antenna_gain_dbi"]
    rx_antenna_gain_dbi: float = MESHTASTIC_DEFAULTS["rx_antenna_gain_dbi"]
    tx_height_above_surface_m: float = MESHTASTIC_DEFAULTS["tx_height_above_surface_m"]
    rx_height_above_surface_m: float = MESHTASTIC_DEFAULTS["rx_height_above_surface_m"]
    rx_sensitivity_dbm: float = MESHTASTIC_DEFAULTS["rx_sensitivity_dbm"]
    cable_loss_db: float = MESHTASTIC_DEFAULTS["cable_loss_db"]
    step_m: float = 100.0  # terrain profile sampling interval


@dataclass
class LinkResult:
    """Output of a single link budget calculation between two points."""

    distance_m: float
    fspl_db: float
    diffraction_loss_db: float
    path_loss_db: float
    received_power_dbm: float
    margin_db: float
    is_los: bool


def free_space_path_loss_db(distance_m, freq_mhz):
    """Free-space path loss (dB) for the given distance(s) and frequency,
    per the standard FSPL formula. Distance is floored at 1m."""
    # Floor at 1m so log10(0) can't happen for a Tx/Rx at (near) the same point.
    distance_km = np.maximum(np.asarray(distance_m, dtype=np.float64), 1.0) / 1000.0
    return 20 * np.log10(distance_km) + 20 * np.log10(freq_mhz) + 32.44


def curvature_bulge_m(d1_m, d2_m, k=K_FACTOR):
    """Apparent terrain rise (m) at a point between two ends of a path,
    caused by Earth's curvature under the k-factor effective-earth-radius
    approximation. d1_m/d2_m are the distances from that point to each end."""
    return (d1_m * d2_m) / (2 * k * EARTH_RADIUS_M)


def knife_edge_diffraction_loss_db(v):
    """ITU-R P.526 simplified single-knife-edge diffraction loss (dB)."""
    v = np.atleast_1d(np.asarray(v, dtype=np.float64))
    loss = np.zeros_like(v)
    # Below v = -0.78 the obstruction is far enough below the line-of-sight
    # that diffraction loss is negligible (~0 dB) and the formula isn't
    # meant to be applied -- those entries stay at the zero-init above.
    mask = v > -0.78
    vv = v[mask]
    loss[mask] = 6.9 + 20 * np.log10(np.sqrt((vv - 0.1) ** 2 + 1) + vv - 0.1)
    return np.maximum(loss, 0.0)


def worst_case_diffraction_v(distances_m, elevations_m, tx_total_height_m, rx_total_height_m, wavelength_m):
    """Max diffraction parameter v over all interior profile points.
    distances_m: distances from Tx for each profile sample, 0 <= d <= d_total
    (endpoint samples at d=0 and d=d_total are included but ignored)
    elevations_m: terrain elevation (not including antenna height) at each sample"""
    d_total = distances_m[-1] if len(distances_m) else 0.0
    # Only interior points can obstruct the path -- the Tx/Rx endpoints
    # themselves aren't candidate obstructions.
    interior = (distances_m > 0) & (distances_m < d_total)
    if not np.any(interior) or d_total <= 0:
        return -999.0  # no interior points (or zero-length path) -> treat as fully clear

    d_i = distances_m[interior]
    elev_i = elevations_m[interior]
    d2_i = d_total - d_i

    # Height of the straight Tx-Rx line-of-sight line at each interior
    # point, linearly interpolated by fraction of distance covered.
    los_height_i = tx_total_height_m + (rx_total_height_m - tx_total_height_m) * (d_i / d_total)
    bulge_i = curvature_bulge_m(d_i, d2_i)
    # How far the (curvature-adjusted) terrain pokes above the LOS line;
    # positive means the terrain obstructs the path at this point.
    h_i = (elev_i + bulge_i) - los_height_i

    # Standard Fresnel diffraction parameter v for each candidate obstruction.
    v_i = h_i * np.sqrt(2.0 / wavelength_m * (1.0 / d_i + 1.0 / d2_i))
    return float(np.max(v_i))


def link_budget_point_to_point(dem, tx_lonlat, rx_lonlat, params: LinkParams = LinkParams()) -> LinkResult:
    """Full terrain-aware link budget between two fixed points."""
    tx_lon, tx_lat = tx_lonlat
    rx_lon, rx_lat = rx_lonlat

    geod = pyproj.Geod(ellps="WGS84")
    _, _, distance_m = geod.inv(tx_lon, tx_lat, rx_lon, rx_lat)

    n_points = max(int(distance_m // params.step_m), 2)
    lonlats = geod.npts(tx_lon, tx_lat, rx_lon, rx_lat, n_points)
    lons = [p[0] for p in lonlats]
    lats = [p[1] for p in lonlats]
    # npts returns interior points only (excludes endpoints)
    distances = np.linspace(0, distance_m, n_points + 2)[1:-1]

    tx_elev = dem.elevation_at_lonlat(tx_lon, tx_lat)
    rx_elev = dem.elevation_at_lonlat(rx_lon, rx_lat)
    elevations = dem.elevation_at_lonlat_arrays(np.array(lons), np.array(lats))

    tx_total_height = tx_elev + params.tx_height_above_surface_m
    rx_total_height = rx_elev + params.rx_height_above_surface_m

    # Stitch the Tx/Rx endpoints back onto the interior profile so the
    # diffraction search sees the full 0..d_total path.
    all_distances = np.concatenate(([0.0], distances, [distance_m]))
    all_elevations = np.concatenate(([tx_elev], elevations, [rx_elev]))

    wavelength = C / (params.freq_mhz * 1e6)
    v_max = worst_case_diffraction_v(all_distances, all_elevations, tx_total_height, rx_total_height, wavelength)

    fspl = float(free_space_path_loss_db(distance_m, params.freq_mhz))
    diff_loss = float(knife_edge_diffraction_loss_db(v_max)[0])
    path_loss = fspl + diff_loss

    rx_power = (
        params.tx_power_dbm
        + params.tx_antenna_gain_dbi
        + params.rx_antenna_gain_dbi
        - path_loss
        - params.cable_loss_db
    )
    margin = rx_power - params.rx_sensitivity_dbm

    return LinkResult(
        distance_m=distance_m,
        fspl_db=fspl,
        diffraction_loss_db=diff_loss,
        path_loss_db=path_loss,
        received_power_dbm=rx_power,
        margin_db=margin,
        is_los=v_max <= -0.78,
    )
