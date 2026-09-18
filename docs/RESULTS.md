# Results and reporting policy

The demo generator produces a normal controlled transform and an extreme partial-overlap failure. Run `python experiments/run_demo.py` to create current, machine-measured products in `data/results/`. Those results are synthetic mechanics verification only—not Chandrayaan-2 validation.

Each live registration exports `experiment.json` with its ID, selected representation, transform, measured metrics, quality decision, and correspondence records. The benchmark endpoint exports CSV and reports Lunar Robustness Score (LRS):

`100 × mean(0.35·inlier_ratio + 0.25·coverage + 0.25/(1+RMSE) + 0.15·success)`.

LRS is an internal engineering stress-test measure; it never replaces official metrics or ground-truth evaluation.

## Ablation study (mechanics-level, synthetic)

`python experiments/run_ablation.py` runs `BASELINE_SIFT_RANSAC` (single raw representation, single scale, no spatial cap, no sub-pixel step - i.e. the Part 28 baseline) against `FULL_LUNALIGN` and four single-component ablations, on the same controlled synthetic pairs (rotation+scale+shift, synthetic shadow, rotation/scale/translation, an affine viewpoint-like shear, and additive noise). Output is written to `data/results/ablation/<timestamp>/{ablation.csv,ablation.md}`. A sample run (measured, not fabricated) is checked into this repo at `data/results/ablation/1789197561/`.

What the current run actually shows, honestly:

- **Spatial selection trades raw inlier count for coverage, not lower error.** `NO_SPATIAL_SELECTION` consistently keeps 2-3x more inliers than `FULL_LUNALIGN`, but its RMSE is equal or higher every time, and on the affine-shear pair it is the only config that reaches the `SUCCESS` quality gate (the others land in `LOW_CONFIDENCE`) purely because it has more raw matches, even though they are more clustered. This is a real tension the current quality-gate thresholds don't fully account for, not a settled win for one strategy.
- **Sub-pixel refinement measurably reduces residual once its displacement-gate rejects LK tracking failures.** Comparing `metrics.initial_rmse_px` to `metrics.refined_rmse_px` inside each run's `experiment.json`, refinement consistently lowers the residual on the points it accepts (e.g. 0.97px -> 0.61px on one pair). An earlier version of this metric was corrupted by a memory-aliasing bug in `refine_lk` (see LIMITATIONS.md) - fixed and covered by `tests/test_refinement.py`.
- **The illumination-representation ensemble and multi-scale pyramid help on some stressors and not others.** Neither ablation shows a uniform win across all five synthetic pairs; this is expected because different stressors (shadow vs. noise vs. shear) favour different representations, which is the reason the pipeline searches candidates instead of hard-coding one.

These are mechanics/engineering results on synthetic crater-like imagery, run on a handful of controlled pairs - useful for showing the pipeline's internal trade-offs honestly, not a claim of performance on real Chandrayaan-2 data. That requires the authorised imagery described in DATA_SOURCES.md.
