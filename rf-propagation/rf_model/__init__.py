"""Public API for the RF propagation model: DEM loading, link-budget physics,
and radial coverage prediction. See terrain.py, propagation.py, and
coverage.py for the implementations behind each re-exported name."""
from .terrain import DEM
from .propagation import (
    MESHTASTIC_DEFAULTS,
    LinkParams,
    LinkResult,
    link_budget_point_to_point,
)
from .coverage import compute_coverage, save_coverage_geotiff, plot_coverage

__all__ = [
    "DEM",
    "MESHTASTIC_DEFAULTS",
    "LinkParams",
    "LinkResult",
    "link_budget_point_to_point",
    "compute_coverage",
    "save_coverage_geotiff",
    "plot_coverage",
]
