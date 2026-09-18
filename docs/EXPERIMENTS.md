# Experiment plan and reproducibility

| ID | Pair / stressor | Required evidence |
|---|---|---|
| EXP-01 | OHRC → OHRC | authorised IDs, metadata, outputs |
| EXP-02 | OHRC → TMC | comparable structural-band rationale |
| EXP-03 | TMC → TMC | geometry diagnostics |
| EXP-04/05 | OHRC/TMC → IIRS | documented band selection |
| EXP-06–09 | illumination, scale, overlap, compression | controlled configuration and metrics |
| EXP-10 | stress benchmark | exported CSV and plots |

For each run, retain input IDs (not necessarily raw restricted data), sensor fields, metadata availability, configuration, source revision, time, metrics, output paths, failure state and interpretation. Compare SIFT+RANSAC with the full pipeline only on the same pair/configuration. Do not claim an improvement until both result records exist.

## Ablation protocol

Run the same pairs with: raw/no ensemble; generic only; no spatial selection; no LK refinement; and full pipeline. Report match count, inlier ratio, RMSE, coverage and runtime. A missing or failed run is reported as such.
