from dataclasses import dataclass
import cv2
import numpy as np

@dataclass
class GeometryResult:
    matrix: np.ndarray | None
    inlier_mask: np.ndarray
    model: str
    score: float = 0.0


def _points(kp1, kp2, matches):
    src = np.float32([kp1[m.queryIdx].pt for m in matches]).reshape(-1, 1, 2)
    dst = np.float32([kp2[m.trainIdx].pt for m in matches]).reshape(-1, 1, 2)
    return src, dst


def _fit(model, src, dst, threshold):
    if model == "similarity":
        matrix, mask = cv2.estimateAffinePartial2D(src, dst, method=cv2.RANSAC, ransacReprojThreshold=threshold, maxIters=5000, confidence=.995, refineIters=10)
    elif model == "affine":
        matrix, mask = cv2.estimateAffine2D(src, dst, method=cv2.RANSAC, ransacReprojThreshold=threshold, maxIters=5000, confidence=.995, refineIters=10)
    else:
        matrix, mask = cv2.findHomography(src, dst, cv2.RANSAC, threshold, maxIters=5000, confidence=.995)
    mask = mask.ravel().astype(bool) if mask is not None else np.zeros(len(src), bool)
    if matrix is None or not mask.any(): return None, mask, -1e9
    pts = src.reshape(-1,2); dstp = dst.reshape(-1,2)
    if model == "homography":
        hp = cv2.perspectiveTransform(src, matrix).reshape(-1,2)
    else:
        hp = pts @ matrix[:,:2].T + matrix[:,2]
    err = np.linalg.norm(hp - dstp, axis=1); valid = err[mask]
    rmse = float(np.sqrt(np.mean(valid**2))) if len(valid) else 999
    score = float(mask.sum()) + float(mask.mean())*10.0 - rmse
    return matrix, mask, score


def estimate_adaptive(kp1, kp2, matches, threshold=3.0, allow_homography=True):
    if len(matches) < 3: return GeometryResult(None, np.zeros(len(matches), bool), "none")
    src, dst = _points(kp1, kp2, matches)
    models = [("similarity", 3), ("affine", 3)]
    if allow_homography and len(matches) >= 4: models.append(("homography", 4))
    candidates=[]
    for name, minimum in models:
        if len(matches) < minimum: continue
        matrix, mask, score = _fit(name, src, dst, threshold)
        if matrix is not None: candidates.append((score, name, matrix, mask))
    if not candidates: return GeometryResult(None, np.zeros(len(matches), bool), "none")
    _, name, matrix, mask = max(candidates, key=lambda x: x[0])
    return GeometryResult(matrix, mask, name)


def estimate_similarity(kp1, kp2, matches, threshold=3.0):
    r = estimate_adaptive(kp1, kp2, matches, threshold, allow_homography=False)
    return GeometryResult(r.matrix, r.inlier_mask, "similarity")


def warp_points(points, matrix, model):
    p=np.asarray(points,dtype=np.float32).reshape(-1,1,2)
    if model == "homography": return cv2.perspectiveTransform(p, matrix).reshape(-1,2)
    return (p.reshape(-1,2) @ matrix[:,:2].T + matrix[:,2])


def reprojection_errors(kp1, kp2, matches, matrix, model="similarity"):
    if matrix is None: return np.full(len(matches), np.nan)
    src=np.float32([kp1[m.queryIdx].pt for m in matches]); dst=np.float32([kp2[m.trainIdx].pt for m in matches])
    return np.linalg.norm(warp_points(src,matrix,model)-dst,axis=1)
