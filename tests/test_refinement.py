import numpy as np
import cv2
import unittest
from backend.refinement.subpixel import refine_lk


class RefinementTests(unittest.TestCase):
    def test_seed_array_not_mutated_in_place(self):
        """Regression test: cv2.calcOpticalFlowPyrLK writes into the nextPts
        buffer it is given. Passing a reshaped-but-not-copied view previously
        let OpenCV silently overwrite the caller's target_points array,
        making every later 'is this a real refinement or a tracking failure'
        comparison compare the output against itself."""
        rng = np.random.default_rng(0)
        source = (rng.random((200, 200)) * 255).astype(np.uint8)
        target = source.copy()
        pts = np.float32([[50, 50], [100, 100], [150, 150]])
        seed_before = pts.copy()
        refine_lk(source, target, pts, pts)
        np.testing.assert_array_equal(pts, seed_before)

    def test_large_displacement_is_rejected(self):
        """A tracked point that lands far from its seed is a tracking
        failure for this *local* refinement step, not a valid correspondence,
        and must not be marked valid."""
        source = np.zeros((300, 300), np.uint8)
        cv2.circle(source, (150, 150), 20, 200, -1)
        target = source.copy()
        source_points = np.float32([[150, 150]])
        # Seed the "initial guess" far from the true match on a blank area.
        bad_seed = np.float32([[280, 280]])
        refined, valid, err = refine_lk(source, target, source_points, bad_seed, max_displacement_px=4.0)
        self.assertFalse(valid[0])

    def test_good_seed_is_accepted(self):
        # Point must sit on real local texture (an edge) - LK cannot lock
        # onto a uniform, gradient-free interior region.
        source = np.zeros((300, 300), np.uint8)
        cv2.circle(source, (150, 150), 40, 200, 2)
        target = source.copy()
        source_points = np.float32([[190, 150]])  # on the ring
        good_seed = np.float32([[191, 149]])
        refined, valid, err = refine_lk(source, target, source_points, good_seed, max_displacement_px=4.0)
        self.assertTrue(valid[0])


if __name__ == "__main__":
    unittest.main()
