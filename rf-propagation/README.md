# RF Propagation Model

Terrain-aware LoRa/Meshtastic coverage prediction for the Burlington mesh
project: free-space path loss + single-knife-edge diffraction from a DEM,
tuned to Meshtastic's US915 defaults (see
`rf_model/propagation.py:MESHTASTIC_DEFAULTS`).

Given a candidate site and an elevation raster, it produces:
- point-to-point link budgets between sites (LOS/NLOS, path loss, margin)
- a coverage map radiating out from one site, as a quick-look PNG and a
  GeoTIFF you can drop straight into the `mesh vermont.gdb` ArcGIS project

## Setup

```bash
pip install -r requirements.txt
```

No virtual environment — deliberately, so the same commands work whether
you're on Mac, Windows, or Linux without path differences (`venv/bin/python`
vs `venv\Scripts\python.exe`). If you'd rather isolate dependencies, feel
free to use a venv/conda env of your own, but nothing here requires it, and
the commands below all just use plain `python`/`pip`.

All commands below assume you're running them from this folder
(`rf-propagation/`).

## Try it (synthetic data)

Runs the whole pipeline against placeholder terrain, so you can confirm
everything works before wiring up real data:

```bash
python make_synthetic_dem.py   # writes example_data/
python run_coverage.py          # writes output/*.png and *.tif
```

## Using real data

**DEM**: needs to be actual elevation (bare-earth DEM or a full-surface
DSM) — *not* an nDSM (normalized DSM), which stores object heights above
ground rather than elevation and will flatten all real terrain in the
model. Vermont's statewide bare-earth DEM (`STATEWIDE_2023_10M_DEMHF.tif`)
is available from [VT Open Data](https://s3.us-east-2.amazonaws.com/vtopendata-prd/Elevation/) —
clip it to your area of interest (ArcGIS's Clip Raster tool works fine)
and export as a GeoTIFF. Any CRS is fine, the model reprojects lon/lat
queries into the raster's own CRS automatically.

Before running the model on a new DEM export, sanity-check it:

```bash
python check_dem.py path/to/your_dem.tif
```

This flags the two most common problems in seconds: an accidentally-huge
raster (the model loads the whole band into memory) and an nDSM mistaken
for a DEM.

**Candidate sites**: a CSV with columns `name,lon,lat,height_agl_m`. In
ArcGIS, add Lon/Lat fields to `Candidate_Sites` via Calculate Geometry
(point X/Y, EPSG:4326), then export the attribute table to CSV. The
project's site list lives at `../sites.csv` (one level up, in
`mesh-vermont/`).

```bash
python run_coverage.py --dem path/to/your_dem.tif --sites ../sites.csv --radius-km 30
```

`--dem` and `--sites` are the only arguments you need to change — see
`run_coverage.py --help` for the rest (Tx site, coverage radius/resolution,
azimuth count, output folder), all of which have sensible defaults.

### Reading the output

- **PNG**: link margin (dB) above the receiver's sensitivity floor, colored
  and auto-scaled, with a black contour at 0 dB marking the predicted edge
  of reliable coverage. Quick-look only.
- **GeoTIFF**: raw received signal strength in dBm, unstyled, EPSG:4326.
  This is the one for GIS work — symbolize/classify it against your
  radio's actual sensitivity (e.g. -129 dBm for LongFast) to get a real
  coverage boundary, or use it in further raster analysis.

## Model notes / limitations

- Path loss = free-space loss + single-knife-edge diffraction against the
  worst obstruction point along the profile (ITU-R P.526 simplified
  formula), with a 4/3-effective-earth-radius curvature correction. This
  is **not** multi-edge (Deygout) diffraction — terrain with more than one
  significant ridge in the path will be somewhat optimistic. Good for
  comparing candidate sites, not a substitute for a licensed tool (SPLAT!,
  Radio Mobile) for anything safety-critical.
- No vegetation/clutter loss, no rain/atmospheric attenuation, no building
  loss — all "planning best case."
- `MESHTASTIC_DEFAULTS` assumes the LongFast preset (SF11/BW250) receiver
  sensitivity. Running a different modem preset (e.g. ShortFast, much less
  sensitive at ~-109 dBm) means updating `rx_sensitivity_dbm` in
  `LinkParams` to match.
- LoRa's receiver sensitivity is good enough that link margin often stays
  positive well past line-of-sight blockage — the PNG's color scale
  auto-ranges to the actual margin spread so it doesn't wash out to solid
  green.

## Layout

- `rf_model/terrain.py` — DEM loading + bilinear elevation sampling
- `rf_model/propagation.py` — path-loss physics, point-to-point link budget
- `rf_model/coverage.py` — radial coverage sweep, GeoTIFF export, plotting
- `run_coverage.py` — CLI driver: link budgets + coverage map
- `check_dem.py` — pre-flight validation for a DEM before running the model
- `build_dsm.py` — reconstructs a local DSM (DEM + nDSM) for a small area,
  without downloading either statewide source in full
- `make_synthetic_dem.py` + `example_data/` — placeholder DEM/sites for
  testing the pipeline without real data
