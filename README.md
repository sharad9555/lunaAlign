# LUNALIGN AI

## Sun-Angle & Cross-Sensor Lunar Image Correspondence Engine

LUNALIGN AI is a ₹0, local-first research prototype for SIH26166. Its contribution is an **adaptive, sensor-aware, terrain-structure-aware, illumination-robust, spatially distributed and failure-aware** image-correspondence workflow—not a claim that its individual algorithms are novel.

## What runs locally now

- PNG/JPEG/TIFF pair ingestion, declared OHRC/TMC/IIRS/LRO NAC/SELENE profiles, and UNKNOWN-preserving metadata policy.
- RAW/CLAHE/gradient/edge/local-contrast representations selected by verified support.
- 0.5×/1× coarse-to-fine candidate search (Fast mode uses 1×).
- SIFT/ORB matching, ratio filtering, per-cell spatial diversity caps, similarity RANSAC, guarded pyramidal Lucas–Kanade local refinement.
- Registered, overlay, checkerboard, difference, inlier, confidence, residual-error, and coverage products.
- Quality states, JSON experiment records, a controlled stress benchmark + CSV, Lunar Robustness Score, and intentional failure demo.
- FastAPI API and a local scientific dashboard. No account, telemetry, cloud upload, GPU, or runtime model download.

## Run

```powershell
python -m pip install -r requirements.txt
uvicorn backend.api.main:app --reload
```

Open `http://127.0.0.1:8000`; API schema is at `/docs`. For an offline mechanics demo:

```powershell
python experiments/run_demo.py
```

## Modes and optional models

Fast uses ORB. Balanced uses SIFT. Research mode detects a locally installed optional deep stack and otherwise explicitly falls back to SIFT. CUDA is detected when PyTorch is installed; GPU is never required. No deep matcher is claimed to run unless its local dependency/model has been installed by the operator.

## Ablation & baseline comparison

`python experiments/run_ablation.py` measures `BASELINE_SIFT_RANSAC` against the full pipeline and four single-component ablations (illumination ensemble, multi-scale pyramid, spatial selection, sub-pixel refinement) on controlled synthetic pairs, and writes real CSV/Markdown results to `data/results/ablation/<timestamp>/`. See [Results](docs/RESULTS.md) for what the checked-in sample run actually shows, including a real bug it caught in sub-pixel refinement (now fixed, see [Limitations](docs/LIMITATIONS.md)).

## Important scientific limits

The current residual RMSE is **transform reprojection consistency**, not absolute lunar geolocation accuracy. Performance claims require authorised, documented image pairs and independent ground truth. IIRS support exposes explicit band selection for multiband arrays and structural normalisation; a production hyperspectral product reader and authorised Chandrayaan-2 validation corpus remain dataset-integration work.

Synthetic crater-like demo imagery is clearly labelled synthetic and must not be represented as Chandrayaan-2 imagery.

## Documents

- [Architecture](docs/ARCHITECTURE.md)
- [Method](docs/METHOD.md)
- [Data sources policy](docs/DATA_SOURCES.md)
- [Experiments and ablations](docs/EXPERIMENTS.md)
- [Results and LRS](docs/RESULTS.md)
- [API](docs/API.md)
- [Setup](docs/SETUP.md)
- [Limitations](docs/LIMITATIONS.md)
- [Security](docs/SECURITY.md)
- [Judge demo and Q&A](docs/JUDGING_DEMO.md)
