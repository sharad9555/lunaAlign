import numpy as np


def coverage(points, shape, grid=8):
    if len(points)==0: return 0.0, [[0]*grid for _ in range(grid)]
    h,w=shape[:2]; cells=np.zeros((grid,grid),dtype=int)
    for x,y in points:
        cells[min(grid-1,max(0,int(y*grid/h))),min(grid-1,max(0,int(x*grid/w)))]+=1
    occupied=np.count_nonzero(cells); cov=float(occupied/cells.size)
    probs=cells[cells>0].astype(float); probs/=probs.sum()
    entropy=float(-(probs*np.log(probs)).sum()/np.log(cells.size)) if len(probs)>1 else 0.0
    ys,xs=np.nonzero(cells); hull_cov=0.0
    if len(xs)>=3:
        import cv2
        hull=cv2.convexHull(np.float32([(x*w/grid,y*h/grid) for x,y in zip(xs,ys)]))
        hull_cov=float(cv2.contourArea(hull)/(w*h))
    return cov, {"cells":cells.tolist(),"entropy":round(entropy,4),"convex_hull_coverage":round(hull_cov,4)}


def summarize(errors, inlier_mask, points, shape, elapsed, grid=8, model="similarity"):
    inliers=errors[inlier_mask] if len(errors) else np.array([]); valid=inliers[np.isfinite(inliers)]
    cov, detail=coverage(points,shape,grid)
    return {"candidate_matches":int(len(errors)),"inliers":int(inlier_mask.sum()),"inlier_ratio":float(inlier_mask.mean()) if len(inlier_mask) else 0.0,
            "rmse_px":float(np.sqrt(np.mean(valid**2))) if len(valid) else None,"median_error_px":float(np.median(valid)) if len(valid) else None,
            "p95_error_px":float(np.percentile(valid,95)) if len(valid) else None,"spatial_coverage":cov,"coverage_grid":detail,
            "processing_time_s":round(elapsed,3),"transform_model":model}
