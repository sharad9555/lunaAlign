import math


def quality_gate(metrics, min_inliers=8, min_ratio=.18, max_rmse=3.0, min_coverage=.03):
    if metrics["inliers"] < min_inliers: return "REJECT", "too few geometrically verified matches"
    if metrics["inlier_ratio"] < min_ratio: return "LOW CONFIDENCE", "high outlier proportion"
    if metrics["rmse_px"] is None or metrics["rmse_px"] > max_rmse: return "LOW CONFIDENCE", "high internal reprojection residual"
    if metrics["spatial_coverage"] < min_coverage: return "MEDIUM CONFIDENCE", "matches are spatially concentrated"
    return "HIGH CONFIDENCE", "quality-gate conditions met"


def correspondence_confidence(distance,error,local_error,response):
    descriptor=1/(1+max(0,float(distance))/100); geometric=1/(1+max(0,float(error))); local=1/(1+max(0,float(local_error))); terrain=min(1,max(0,float(response)*10))
    return round(.35*descriptor+.35*geometric+.2*local+.1*terrain,4)


def confidence_features(distance,error,local_error,response):
    return [float(distance), float(error), float(local_error), float(response)]


def calibrated_confidence(distance,error,local_error,response, calibration=None):
    if calibration and "weights" in calibration:
        x=confidence_features(distance,error,local_error,response); z=float(calibration.get("bias",0))+sum(a*b for a,b in zip(calibration["weights"],x)); return round(1/(1+math.exp(-max(-40,min(40,z)))),4), True
    return correspondence_confidence(distance,error,local_error,response), False
