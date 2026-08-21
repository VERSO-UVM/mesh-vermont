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

**DEM/DSM**: needs to be actual elevation — *not* an nDSM (normalized DSM),
which stores object heights above ground rather than elevation and will
flatten all real terrain in the model. Any CRS is fine, the model
reprojects lon/lat queries into the raster's own CRS automatically.

The easiest source is VT Open Data's statewide DSM
(`STATEWIDE_2023_35cm_DSMFR.tif`, "First Return" — ground + buildings +
canopy already combined, a complete real product). It's ~414GB, but you
never download it in full: `clip_sites.py` pulls only a small windowed
clip per site directly from the remote file (via GDAL's overview-aware
decimated reads), and skips any site that already has a clipped file on
disk, so it's always safe to re-run after adding a new candidate site:

```bash
python clip_sites.py --sites ../sites.csv --radius-km 30
```

This writes one `data/<site_name>_dsm.tif` per site in `sites.csv`. Use
`--force` to re-fetch a site that's already been clipped (e.g. after VT
Open Data updates the source). For a single one-off site instead of the
whole CSV, `clip_dsm.py` takes `--lon`/`--lat` directly.

Before running the model on a new DEM/DSM, sanity-check it:

```bash
python check_dem.py path/to/your_dem.tif
```

This flags the two most common problems in seconds: an accidentally-huge
raster (the model loads the whole band into memory) and an nDSM mistaken
for a DEM.

**Candidate sites**: a CSV with columns
`name,lon,lat,height_above_surface_m,radio`. In ArcGIS, add Lon/Lat fields
to `Candidate_Sites` via Calculate Geometry (point X/Y, EPSG:4326), then
export the attribute table to CSV. The project's site list lives at
`../sites.csv` (one level up, in `mesh-vermont/`).

The `radio` column names a row in `../radios.csv` (see below) — it's how
each site says which physical radio/antenna combo is mounted there. Leave
it blank to fall back to `MESHTASTIC_DEFAULTS`.

**Radios**: a CSV with columns
`name,freq_mhz,tx_power_dbm,tx_antenna_gain_dbi,rx_antenna_gain_dbi,rx_sensitivity_dbm,cable_loss_db`
— everything a link budget needs about a radio *except* antenna height,
which stays in `sites.csv` since the same radio can be mounted at
different heights at different sites. The project's radio list lives at
`../radios.csv`. For a point-to-point link budget, the Tx site's radio
supplies freq/tx power/tx gain/cable loss and the Rx site's radio supplies
rx gain/rx sensitivity, so mixed-radio links resolve correctly; a
coverage sweep (no specific Rx site) uses the Tx site's radio for every
field.

The fleet's two real radios, `rak_wismesh_repeater_mini` (outdoor) and
`heltec_v4` (indoor), both use the same SX1262 chip + LongFast preset as
`meshtastic_longfast`, so `rx_sensitivity_dbm` is carried over unchanged
(-129 dBm). `tx_power_dbm` is from each vendor's published spec (22 dBm /
28 dBm) but `tx_antenna_gain_dbi`/`rx_antenna_gain_dbi` (3.0) are
unverified stock-antenna placeholders — neither vendor publishes a gain
figure for the antenna they ship in the box. Also unresolved: which RAK
variant is actually in use (the "Mini" ships in 22 dBm and 30 dBm "1W"
versions with a real link-budget difference) — confirm and correct
`tx_power_dbm` before trusting range predictions from this radio.

```bash
python run_coverage.py --dem data/Votey_Hall_dsm.tif --sites ../sites.csv --radios ../radios.csv --radius-km 30
```

`--dem`, `--sites`, and `--radios` are the arguments you'll most often
change — see `run_coverage.py --help` for the rest (Tx site, coverage
radius/resolution, azimuth count, output folder), all of which have
sensible defaults.

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
- `MESHTASTIC_DEFAULTS` (the fallback for sites with no `radio` set)
  assumes the LongFast preset (SF11/BW250) receiver sensitivity. Running a
  different modem preset (e.g. ShortFast, much less sensitive at ~-109
  dBm) is a matter of adding/using the right row in `radios.csv` rather
  than editing code.
- LoRa's receiver sensitivity is good enough that link margin often stays
  positive well past line-of-sight blockage — the PNG's color scale
  auto-ranges to the actual margin spread so it doesn't wash out to solid
  green.

## Layout

- `rf_model/terrain.py` — DEM loading + bilinear elevation sampling
- `rf_model/propagation.py` — path-loss physics, point-to-point link budget
- `rf_model/coverage.py` — radial coverage sweep, GeoTIFF export, plotting
- `run_coverage.py` — CLI driver: link budgets + coverage map; also loads
  `sites.csv`/`radios.csv` (`load_sites`, `load_radios`)
- `../radios.csv` — radio profiles (freq, tx power, antenna gain, rx
  sensitivity, cable loss), referenced by name from `radio` in `sites.csv`
- `check_dem.py` — pre-flight validation for a DEM before running the model
- `clip_dsm.py` — clips a small windowed DSM around one lon/lat from VT
  Open Data's statewide DSM, without downloading it in full
- `clip_sites.py` — runs `clip_dsm.py` for every site in a sites CSV,
  skipping any that already have a clipped file on disk
- `make_synthetic_dem.py` + `example_data/` — placeholder DEM/sites for
  testing the pipeline without real data
