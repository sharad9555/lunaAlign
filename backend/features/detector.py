from dataclasses import dataclass
import cv2
import numpy as np

@dataclass
class DetectedFeatures:
    keypoints: list
    descriptors: np.ndarray | None
    method: str

def detect(image: np.ndarray, method: str = "SIFT", max_features: int = 4000) -> DetectedFeatures:
    method = method.upper()
    if method == "SIFT" and hasattr(cv2, "SIFT_create"):
        detector = cv2.SIFT_create(nfeatures=max_features)
    elif method == "ORB":
        detector = cv2.ORB_create(nfeatures=max_features, fastThreshold=8)
    else:
        raise ValueError(f"Feature method unavailable: {method}")
    kp, desc = detector.detectAndCompute(image, None)
    return DetectedFeatures(kp, desc, method)

def terrain_type(keypoint: cv2.KeyPoint) -> str:
    # Honest Phase-1 proxy: keypoints denote locally distinctive terrain structures.
    return "CORNER" if keypoint.response > 0.03 else "GENERIC_KEYPOINT"
