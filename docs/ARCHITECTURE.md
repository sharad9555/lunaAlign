# Architecture

```text
image pair + declared sensors
  → safe decode / UNKNOWN-preserving metadata layer
  → illumination representation ensemble + multi-scale pyramid
  → terrain-structure proxy keypoints (SIFT/ORB)
  → ratio candidates → grid diversity selection → similarity RANSAC
  → LK sub-pixel local refinement (guarded)
  → quality gate / failure state
  → registered, overlay, checkerboard, difference, confidence, error and coverage products
  → JSON/CSV experiment record + local dashboard
```

Modules are split under `preprocessing`, `features`, `matching`, `geometry`, `refinement`, `evaluation`, `visualization` (served products), `models` (reserved), and `utils` (reserved). The directory layout allows a deeper matcher or hyperspectral loader to be integrated without replacing the verified classical path.
