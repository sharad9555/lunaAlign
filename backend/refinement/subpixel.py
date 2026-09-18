import cv2
import numpy as np

def refine_lk(source, target, source_points, target_points, max_displacement_px: float = 4.0):
    """Pyramidal Lucas-Kanade *local* refinement seeded by RANSAC correspondences.

    cv2's `ok`/status flag only means the flow computation did not numerically
    fail - it does NOT mean LK tracked the correct structure. On repetitive or
    low-texture terrain (crater rims, edge maps) LK can lock onto a nearby
    stronger gradient and "refine" a point tens of pixels away, which is the
    opposite of sub-pixel refinement. Since this is meant to be a *local*
    correction around an already-verified RANSAC seed, any move larger than
    `max_displacement_px` is treated as a tracking failure, not a real
    refinement, and rejected.
    """
    if len(source_points) == 0: return np.empty((0,2)), np.empty(0, bool), np.empty(0)
    # IMPORTANT: cv2.calcOpticalFlowPyrLK writes its result back into the
    # `nextPts` buffer it is given (that's how OPTFLOW_USE_INITIAL_FLOW's
    # "initial guess" argument doubles as the output). np.float32(x).reshape(...)
    # does NOT copy when `x` is already float32 - it returns a view - so without
    # an explicit .copy() here, the seed target_points array the caller passed
    # in gets silently overwritten in place, and any later comparison against
    # "the original seed" is actually comparing the output against itself.
    seed = np.array(target_points, dtype=np.float32, copy=True)
    p0 = np.array(source_points, dtype=np.float32, copy=True).reshape(-1, 1, 2)
    p1 = seed.reshape(-1, 1, 2).copy()
    criteria = (cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, 30, 0.005)
    refined, ok, err = cv2.calcOpticalFlowPyrLK(source, target, p0, p1, winSize=(21,21), maxLevel=3, criteria=criteria,
                                                 flags=cv2.OPTFLOW_USE_INITIAL_FLOW)
    refined = refined.reshape(-1, 2).copy()
    displacement = np.linalg.norm(refined - seed, axis=1)
    valid = ok.ravel().astype(bool) & np.isfinite(refined).all(axis=1) & (displacement <= max_displacement_px)
    return refined, valid, err.ravel()
