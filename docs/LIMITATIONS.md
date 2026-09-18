# Limitations

- Phase 1 estimates a 2D similarity transform. It is unsuitable for arbitrary relief/viewpoint changes and does not silently substitute a homography.
- Reprojection RMSE is not ground-truth lunar registration error. Ground-control or independently aligned reference data is required for absolute validation.
- No parser currently extracts OHRC/TMC/IIRS product metadata; unknown fields remain unknown.
- The dashboard is an operational baseline, not the final React mission-analysis interface.
- Deep matchers, hyperspectral cube loading, and GeoTIFF preservation remain future, test-gated phases.
- Sub-pixel refinement had a memory-aliasing defect (the LK "initial guess" buffer aliased the caller's seed array, so OpenCV silently overwrote it in place, making the before/after comparison compare the output against itself). This is fixed in `backend/refinement/subpixel.py` and covered by `tests/test_refinement.py`; refinement is now gated to reject any displacement beyond 4px from its RANSAC seed, since it is a local correction, not a re-detection step. A first ablation pass (`experiments/run_ablation.py`, results below) shows the fixed refinement now reduces measured residual on every tested synthetic pair rather than occasionally corrupting it.
