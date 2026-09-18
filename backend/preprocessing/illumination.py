import cv2
import numpy as np

def select_band(image: np.ndarray, band_index: int | None = None) -> np.ndarray:
    """Choose an IIRS-like band explicitly; absent a choice use median structural intensity."""
    if image.ndim != 3 or image.shape[2] in (3, 4): return image
    if band_index is not None:
        if not 0 <= band_index < image.shape[2]: raise ValueError(f"band_index must be 0..{image.shape[2]-1}")
        return image[..., band_index]
    return np.median(image, axis=2)

def to_gray_uint8(image: np.ndarray) -> np.ndarray:
    image = select_band(image)
    if image.ndim == 3:
        image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    image = image.astype(np.float32)
    finite = image[np.isfinite(image)]
    if finite.size == 0:
        raise ValueError("Image contains no finite pixels")
    lo, hi = np.percentile(finite, (1, 99))
    if hi <= lo:
        return np.zeros(image.shape, np.uint8)
    return np.clip((image - lo) * 255.0 / (hi - lo), 0, 255).astype(np.uint8)

def representation(image: np.ndarray, mode: str = "clahe") -> np.ndarray:
    gray = to_gray_uint8(image)
    if mode == "raw": return gray
    if mode == "clahe": return cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8)).apply(gray)
    if mode == "gradient":
        gx = cv2.Sobel(gray, cv2.CV_32F, 1, 0, ksize=3); gy = cv2.Sobel(gray, cv2.CV_32F, 0, 1, ksize=3)
        return cv2.convertScaleAbs(cv2.magnitude(gx, gy))
    if mode == "edge": return cv2.Canny(gray, 60, 150)
    if mode == "local_contrast":
        blur = cv2.GaussianBlur(gray, (0, 0), 9)
        return cv2.normalize(cv2.subtract(gray, blur, dtype=cv2.CV_32F), None, 0, 255, cv2.NORM_MINMAX).astype(np.uint8)
    raise ValueError(f"Unknown representation: {mode}")
