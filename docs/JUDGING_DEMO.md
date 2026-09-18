# SIH judge-facing flow

## Two minutes

1. Open the local dashboard; point out **Local Processing Enabled**.
2. Click **Run LunaAlign Demo**: representation ensemble, multi-scale matching, diversity filtering, RANSAC and local refinement run live.
3. Switch among overlay/checkerboard, verified inliers, confidence, error and coverage views.
4. Show the metrics and explain that residual RMSE is internal transform consistency, not absolute lunar geolocation.
5. Click **Run Failure Demo**. The extreme crop is rejected/low confidence instead of being presented as a registration.

## Five-minute technical explanation

Sensor declarations guide structural processing; unknown metadata remains unknown. Multiple illumination representations compete using verified support. Grid quotas prevent match concentration. Similarity RANSAC is selected for the current planar/local patch baseline. Lucas–Kanade uses RANSAC correspondences as seeds and is accepted only if it improves its local fitted criterion. The quality gate evaluates inliers, ratio, residual and coverage.

## Ten-minute presentation outline

Problem and risk → baseline limitation → adaptive architecture → cross-sensor structural strategy → uniformity/sub-pixel/failure evidence → benchmark protocol → limitations/future validation. Novelty wording: **an integrated adaptive framework optimized for Chandrayaan-2 multi-modal registration**, not invention of individual algorithms.

## Expected Q&A

**Is it ISRO validated?** No; validation requires authorised labelled pairs or control data.  
**Is RMSE ground truth?** No; it is a reprojection residual unless independent ground truth is supplied.  
**How does IIRS work?** Select and record an appropriate band, derive structural products and use stricter verification; never silently treat a cube as RGB.  
**What if it fails?** The quality gate reports the failure rather than forcing a warp.
