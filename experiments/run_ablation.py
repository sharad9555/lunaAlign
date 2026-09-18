"""EXP-10 style ablation + baseline-vs-proposed comparison (docs/EXPERIMENTS.md protocol).

Runs the SAME controlled, synthetic pairs through several pipeline configurations
and writes real measured metrics. No numbers here are invented: every value comes
from an actual `register()` call. This is a mechanics/engineering benchmark on
synthetic crater-like imagery, NOT a Chandrayaan-2 scientific validation.

Usage:
    python experiments/run_ablation.py
Outputs:
    data/results/ablation/<timestamp>/ablation.csv
    data/results/ablation/<timestamp>/ablation.md
"""
from pathlib import Path
import csv, time, sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from backend.core.demo import lunar_like_pair
from backend.evaluation.benchmark import variants
from backend.core.pipeline import register

CONFIGS = {
    # name: (representation_ensemble, multiscale, spatial_selection, subpixel_refinement)
    "BASELINE_SIFT_RANSAC":   dict(representation_ensemble=False, multiscale=False, spatial_selection=False, subpixel_refinement=False),
    "NO_ILLUM_ENSEMBLE":      dict(representation_ensemble=False, multiscale=True,  spatial_selection=True,  subpixel_refinement=True),
    "NO_MULTISCALE":          dict(representation_ensemble=True,  multiscale=False, spatial_selection=True,  subpixel_refinement=True),
    "NO_SPATIAL_SELECTION":   dict(representation_ensemble=True,  multiscale=True,  spatial_selection=False, subpixel_refinement=True),
    "NO_SUBPIXEL_REFINEMENT": dict(representation_ensemble=True,  multiscale=True,  spatial_selection=True,  subpixel_refinement=False),
    "FULL_LUNALIGN":          dict(representation_ensemble=True,  multiscale=True,  spatial_selection=True,  subpixel_refinement=True),
}


def build_pairs():
    """Controlled synthetic pairs covering the stressors EXPERIMENTS.md calls out.
    Every pair is generated locally and clearly labelled synthetic."""
    src, tgt_normal = lunar_like_pair(failure=False)
    pairs = {"normal_rotation_scale_shift": (src, tgt_normal)}
    stressed = variants(src)
    for name in ("synthetic_shadow", "rotation_scale_translation", "viewpoint_like_affine", "noise"):
        pairs[name] = (src, stressed[name])
    return pairs


def run():
    out_dir = ROOT / "data" / "results" / "ablation" / str(int(time.time()))
    out_dir.mkdir(parents=True, exist_ok=True)
    fieldnames = ["pair", "config", "status", "candidate_matches", "inliers", "inlier_ratio",
                  "rmse_px", "median_error_px", "spatial_coverage", "processing_time_s"]
    rows = []
    pairs = build_pairs()
    for pair_name, (src, tgt) in pairs.items():
        for config_name, flags in CONFIGS.items():
            result = register(src, tgt, ROOT / "data" / "results" / "_ablation_runs",
                               method="SIFT", performance_mode="BALANCED",
                               source_sensor="SYNTHETIC", target_sensor="SYNTHETIC", **flags)
            m = result.metrics
            rows.append({"pair": pair_name, "config": config_name, "status": result.status,
                         "candidate_matches": m["candidate_matches"], "inliers": m["inliers"],
                         "inlier_ratio": round(m["inlier_ratio"], 4),
                         "rmse_px": round(m["rmse_px"], 4) if m["rmse_px"] is not None else None,
                         "median_error_px": round(m["median_error_px"], 4) if m["median_error_px"] is not None else None,
                         "spatial_coverage": round(m["spatial_coverage"], 4),
                         "processing_time_s": m["processing_time_s"]})
            print(f"{pair_name:30s} {config_name:24s} status={result.status:18s} "
                  f"inliers={m['inliers']:4d} ratio={m['inlier_ratio']:.3f} "
                  f"rmse={m['rmse_px']}")

    csv_path = out_dir / "ablation.csv"
    with csv_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    md_path = out_dir / "ablation.md"
    with md_path.open("w", encoding="utf-8") as f:
        f.write("# Ablation study — measured results (synthetic mechanics benchmark)\n\n")
        f.write("Not a Chandrayaan-2 scientific validation. Every number below came from an\n"
                "actual `register()` run in this repository; none are invented.\n\n")
        for pair_name in pairs:
            f.write(f"## Pair: `{pair_name}`\n\n")
            f.write("| Config | Status | Matches | Inliers | Inlier ratio | RMSE (px) | Median err (px) | Coverage | Time (s) |\n")
            f.write("|---|---|---|---|---|---|---|---|---|\n")
            for row in rows:
                if row["pair"] != pair_name:
                    continue
                f.write(f"| {row['config']} | {row['status']} | {row['candidate_matches']} | {row['inliers']} | "
                        f"{row['inlier_ratio']} | {row['rmse_px']} | {row['median_error_px']} | "
                        f"{row['spatial_coverage']} | {row['processing_time_s']} |\n")
            f.write("\n")

    print(f"\nWritten: {csv_path}\nWritten: {md_path}")
    return csv_path, md_path


if __name__ == "__main__":
    run()
