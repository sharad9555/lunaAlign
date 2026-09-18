# LUNALIGN AI — Phase 2 Improvements

This version extends the original local prototype with research/production-oriented features while keeping the offline demo path dependency-light.

## Added

1. **Real-data ingestion readiness** — PNG/JPEG/TIFF plus optional GeoTIFF metadata and JSON sidecars. No mission data is bundled or fabricated.
2. **Sun-geometry aware normalization** — optional solar azimuth/elevation correction with an explicit `available/unavailable` state.
3. **Sensor profiles** — OHRC, TMC, IIRS, LRO-NAC, SELENE and UNKNOWN profiles with conservative assumptions.
4. **Adaptive geometry** — similarity → affine → optional homography model selection using RANSAC consistency.
5. **Stronger spatial metrics** — grid coverage, entropy and convex-hull coverage.
6. **Optional confidence calibration** — labelled true/false correspondences can train a logistic calibration model. The system never pretends an engineering score is a probability.
7. **Persistent experiment history** — SQLite database at `data/lunalign.sqlite3` and `/api/history`.
8. **Metadata inspection endpoint** — `/api/inspect-metadata`.
9. **Sensor endpoint** — `/api/sensors`.
10. **Expanded benchmark suite** — deterministic brightness/contrast/gamma/noise/blur/affine/shadow/crop stress tests.
11. **Interactive local dashboard** — solar geometry fields, adaptive-model display, correspondence table, image zoom and history.
12. **React migration scaffold** — `frontend/src/` and `index.react.html` are included for a component-based frontend migration.

## Real Chandrayaan-2 data

The application is intentionally **data-ready rather than data-faking**. To validate scientifically, supply an authorised mission dataset and its ground-truth/control points. A sample metadata sidecar is provided at `data/sample/metadata.example.json`.

For an image `scene.tif`, place a sidecar named either `scene.tif.json` or `scene.json` with fields such as:

```json
{
  "solar_azimuth": 135.0,
  "solar_elevation": 42.0,
  "phase_angle": 38.0,
  "incidence_angle": 44.0,
  "emission_angle": 6.0,
  "pixel_resolution": 0.25
}
```

The browser upload path also exposes direct solar geometry fields so experiments can be reproduced without a sidecar.

## Confidence calibration

Prepare labelled rows:

```json
[
  {"features":[35.2,0.8,1.1,0.12],"label":1},
  {"features":[120.4,8.2,7.0,0.02],"label":0}
]
```

Train with:

```bash
python scripts_train_calibration.py labels.json models/confidence_calibration.json
```

Install `scikit-learn` only for this training step. The runtime does not require it.

## Run

```bash
python -m venv .venv
# Windows
.venv\\Scripts\\activate
pip install -r requirements.txt
uvicorn backend.api.main:app --reload
```

Open `http://127.0.0.1:8000`.

## Important scientific limitation

Synthetic stress tests and internal reprojection residuals are **not** Chandrayaan-2 ground-truth accuracy. A real validation claim requires authorised mission imagery, documented metadata, control points/ground truth, a held-out test set and published evaluation protocol.
