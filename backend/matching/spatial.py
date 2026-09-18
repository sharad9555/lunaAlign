import numpy as np

def diverse_subset(matches, keypoints, shape, grid: int = 8, per_cell: int = 10):
    """Select best descriptor matches across cells, preventing a single crater from dominating."""
    h, w = shape[:2]; buckets = {}
    for m in sorted(matches, key=lambda x: x.distance):
        x, y = keypoints[m.queryIdx].pt
        cell = (min(grid - 1, int(y * grid / h)), min(grid - 1, int(x * grid / w)))
        buckets.setdefault(cell, []).append(m)
    selected = [m for values in buckets.values() for m in values[:per_cell]]
    return selected, {f"{r},{c}": len(v) for (r,c), v in buckets.items()}
