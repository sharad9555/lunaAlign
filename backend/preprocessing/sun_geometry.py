"""Sun-geometry aware illumination helpers.

The functions are intentionally conservative: when solar metadata is absent, the
pipeline falls back to image-only normalization rather than inventing geometry.
"""
import cv2
import numpy as np


def _norm_angle(v):
    return float(v) % 360.0


def illumination_descriptor(solar_azimuth=None, solar_elevation=None, shape=None):
    if solar_azimuth in (None, "UNKNOWN") or solar_elevation in (None, "UNKNOWN"):
        return {"available": False, "reason": "solar azimuth/elevation unavailable"}
    az, el = _norm_angle(float(solar_azimuth)), float(solar_elevation)
    if shape is None:
        return {"available": True, "azimuth_deg": az, "elevation_deg": el}
    h, w = shape[:2]
    # A deterministic illumination prior, not a physical DEM/shadow model.
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    xx = (xx / max(1, w - 1) - 0.5) * 2.0
    yy = (yy / max(1, h - 1) - 0.5) * 2.0
    azr = np.deg2rad(az)
    elev = np.deg2rad(max(-89.0, min(89.0, el)))
    direction = np.cos(azr) * xx + np.sin(azr) * yy
    prior = np.clip(0.5 + 0.5 * np.sin(elev) * direction, 0.65, 1.35)
    return {"available": True, "azimuth_deg": az, "elevation_deg": el, "prior_mean": float(prior.mean())}


def sun_normalize(gray: np.ndarray, solar_azimuth=None, solar_elevation=None) -> np.ndarray:
    """Apply a gentle geometry-informed shading correction when metadata exists."""
    if solar_azimuth in (None, "UNKNOWN") or solar_elevation in (None, "UNKNOWN"):
        return gray
    info = illumination_descriptor(solar_azimuth, solar_elevation, gray.shape)
    # Keep correction deliberately weak; it is a prior, not radiometric calibration.
    h, w = gray.shape[:2]
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    xx = (xx / max(1, w - 1) - .5) * 2
    yy = (yy / max(1, h - 1) - .5) * 2
    azr = np.deg2rad(info["azimuth_deg"])
    elr = np.deg2rad(info["elevation_deg"])
    direction = np.cos(azr) * xx + np.sin(azr) * yy
    gain = np.clip(1.0 - 0.12 * np.cos(elr) * direction, .82, 1.18)
    out = gray.astype(np.float32) * gain
    return np.clip(out, 0, 255).astype(np.uint8)
