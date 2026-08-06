"""DEM loading and elevation sampling.

Wraps a single-band elevation GeoTIFF (e.g. USGS 3DEP or SRTM) and provides
bilinear elevation lookups by WGS84 lon/lat, in whatever CRS the raster
itself uses.
"""
from __future__ import annotations

import numpy as np
import pyproj
import rasterio

"""Loads a single-band elevation raster fully into memory and answers
    elevation-at-lon/lat queries against it (with automatic reprojection
    if the raster isn't already in EPSG:4326)."""
class DEM:
    def __init__(self, path: str):
        self.path = path
        self._ds = rasterio.open(path)
        self.crs = self._ds.crs
        self.transform = self._ds.transform
        self.height, self.width = self._ds.height, self._ds.width

        band = self._ds.read(1).astype(np.float64)
        nodata = self._ds.nodata
        if nodata is not None:
            band[band == nodata] = np.nan
        self._band = band

        inv = ~self.transform
        self._inv = (inv.a, inv.b, inv.c, inv.d, inv.e, inv.f)

        if self.crs is None or self.crs.to_epsg() == 4326:
            self._to_dem_crs = None
        else:
            self._to_dem_crs = pyproj.Transformer.from_crs(
                "EPSG:4326", self.crs, always_xy=True
            )

    """Vectorized elevation lookup for arrays of lon/lat points."""
    def elevation_at_lonlat_arrays(self, lons: np.ndarray, lats: np.ndarray) -> np.ndarray:
        lons = np.asarray(lons, dtype=np.float64)
        lats = np.asarray(lats, dtype=np.float64)

        if self._to_dem_crs is not None:
            xs, ys = self._to_dem_crs.transform(lons, lats)
            xs = np.asarray(xs)
            ys = np.asarray(ys)
        else:
            xs, ys = lons, lats

        a, b, c, d, e, f = self._inv
        cols = a * xs + b * ys + c
        rows = d * xs + e * ys + f
        return self._bilinear(rows, cols)

    """Elevation lookup for a single lon/lat point."""
    def elevation_at_lonlat(self, lon: float, lat: float) -> float:
        return float(self.elevation_at_lonlat_arrays(np.array([lon]), np.array([lat]))[0])

    """Bilinear-interpolates raster values at fractional (row, col)
        pixel coordinates, clamping out-of-bounds coordinates to the
        nearest edge pixel."""
    def _bilinear(self, rows: np.ndarray, cols: np.ndarray) -> np.ndarray:
        row0 = np.floor(rows).astype(int)
        col0 = np.floor(cols).astype(int)
        row1 = row0 + 1
        col1 = col0 + 1

        row0c = np.clip(row0, 0, self.height - 1)
        row1c = np.clip(row1, 0, self.height - 1)
        col0c = np.clip(col0, 0, self.width - 1)
        col1c = np.clip(col1, 0, self.width - 1)

        fr = rows - row0
        fc = cols - col0

        v00 = self._band[row0c, col0c]
        v01 = self._band[row0c, col1c]
        v10 = self._band[row1c, col0c]
        v11 = self._band[row1c, col1c]

        top = v00 * (1 - fc) + v01 * fc
        bottom = v10 * (1 - fc) + v11 * fc
        return top * (1 - fr) + bottom * fr
