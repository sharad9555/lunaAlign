# Method

The runtime evaluates RAW/CLAHE/gradient/edge/local-contrast representations (the UI currently exposes the structural candidates) and 0.5×/1× image levels except in Fast mode. The candidate with strongest geometrically verified support is selected. Feature records include coordinate, scale, response-derived terrain proxy, and engineering confidence.

Classical SIFT/ORB are always available when provided by OpenCV. Research mode checks for a locally installed optional deep stack and otherwise announces a SIFT fallback; it never downloads a model at run time. This is deliberate CPU-safe model management, not a claim that a deep model ran.

Spatial filtering sorts matches by descriptor distance then caps each source grid cell. Similarity RANSAC estimates a transform without defaulting to homography. LK local optical flow optionally refines inlier positions; a proposed re-fit is accepted only when its local objective is no worse. Quality thresholds are configurable engineering defaults, not scientifically validated lunar thresholds.
