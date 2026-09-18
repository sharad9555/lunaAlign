import cv2
from backend.features.detector import DetectedFeatures

def ratio_match(a: DetectedFeatures, b: DetectedFeatures, ratio: float = 0.75):
    if a.descriptors is None or b.descriptors is None: return []
    norm = cv2.NORM_L2 if a.method == "SIFT" else cv2.NORM_HAMMING
    raw = cv2.BFMatcher(norm).knnMatch(a.descriptors, b.descriptors, k=2)
    return [m for pair in raw if len(pair) == 2 for m, n in [pair] if m.distance < ratio * n.distance]
