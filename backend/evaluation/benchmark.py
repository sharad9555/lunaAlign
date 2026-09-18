import cv2
import numpy as np

def variants(image):
    h, w = image.shape[:2]; center = (w/2,h/2)
    affine = cv2.getRotationMatrix2D(center, 8, .9); affine[:,2] += (w*.05, h*.03)
    return {
        "brightness": cv2.convertScaleAbs(image, alpha=1, beta=35),
        "contrast": cv2.convertScaleAbs(image, alpha=1.5, beta=0),
        "gamma": np.uint8(255 * (image / 255.0) ** 1.7),
        "noise": np.clip(image.astype(np.float32)+np.random.default_rng(7).normal(0,12,image.shape),0,255).astype(np.uint8),
        "blur": cv2.GaussianBlur(image,(0,0),2.5),
        "rotation_scale_translation": cv2.warpAffine(image, affine, (w,h)),
        "synthetic_shadow": _shadow(image),
        "partial_crop": _crop(image),
        "viewpoint_like_affine": cv2.warpAffine(image, np.float32([[1,.12,0],[.05,1,0]]), (w,h)),
    }

def _shadow(image):
    shade = image.astype(np.float32).copy(); shade[:, :image.shape[1]//2] *= .35; return shade.astype(np.uint8)
def _crop(image):
    out = np.zeros_like(image); h,w=image.shape[:2]; out[h//8:, w//8:] = image[:h-h//8,:w-w//8]; return out

def lunar_robustness_score(rows):
    """Engineering metric: mean of clipped inlier ratio, coverage, inverse RMSE and success rate."""
    if not rows: return None
    values=[]
    for row in rows:
        m=row["metrics"]; inv_error=1/(1+(m["rmse_px"] or 99)); success=1 if row["status"] == "SUCCESS" else 0
        values.append(.35*m["inlier_ratio"]+.25*m["spatial_coverage"]+.25*inv_error+.15*success)
    return round(100*float(np.mean(values)),2)
