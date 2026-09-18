import cv2, numpy as np
import unittest
from pathlib import Path
from backend.preprocessing.illumination import representation
from backend.core.pipeline import register
from backend.matching.spatial import diverse_subset
from backend.geometry.quality import quality_gate

def lunar_like():
    im = np.zeros((400, 500), np.uint8)
    for x, y, r in [(90,80,35),(260,130,55),(400,260,44),(170,300,25)]: cv2.circle(im,(x,y),r,180,2); cv2.circle(im,(x,y),r-5,90,-1)
    cv2.line(im,(20,370),(450,50),150,3); return cv2.GaussianBlur(im,(0,0),1)

class Phase1Tests(unittest.TestCase):
    def test_representations(self):
        self.assertEqual(representation(lunar_like(), "gradient").shape, (400, 500))

    def test_registration(self):
        src = lunar_like(); matrix = cv2.getRotationMatrix2D((250,200), 3, 1.04); matrix[:,2] += (12,-8)
        tgt = cv2.warpAffine(src, matrix, (500,400))
        result = register(src, tgt, Path("data/results/test-run"))
        self.assertGreaterEqual(result.metrics["inliers"], 6)
        self.assertIsNotNone(result.metrics["rmse_px"])
        self.assertIn("coverage_map", result.paths)
        self.assertIn(result.status, {"SUCCESS", "LOW_CONFIDENCE", "INSUFFICIENT_FEATURES"})

    def test_quality_rejects_weak_result(self):
        decision, _ = quality_gate({"inliers": 0, "inlier_ratio": 0, "rmse_px": None, "spatial_coverage": 0})
        self.assertEqual(decision, "REJECT")

if __name__ == "__main__":
    unittest.main()
