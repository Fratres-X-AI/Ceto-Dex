"""RunPod finish: parse YOLO metrics, write phase4 gate + replay bundle."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from cetodex.evidence_contract import sha256_file, wrap_gate_report, write_gate_report
from cetodex.replay import write_replay_bundle

ROOT = Path(__file__).resolve().parents[2]


def _read_yolo_results(eval_dir: Path) -> dict[str, Any]:
    metrics: dict[str, Any] = {}
    for name in ("results.csv", "results.json"):
        p = eval_dir / name
        if p.is_file():
            metrics[name] = p.read_text(encoding="utf-8")[:8000]
    pred_dir = eval_dir / "predictions.json"
    if pred_dir.is_file():
        metrics["predictions"] = json.loads(pred_dir.read_text(encoding="utf-8"))
    return metrics


def _parse_results_csv(eval_dir: Path, weights: Path | None = None) -> dict[str, float]:
    candidates = [eval_dir / "results.csv"]
    if weights is not None:
        candidates.append(weights.parent.parent / "results.csv")
    for csv_path in candidates:
        if not csv_path.is_file():
            continue
        lines = [ln.strip() for ln in csv_path.read_text(encoding="utf-8").splitlines() if ln.strip()]
        if len(lines) < 2:
            continue
        headers = [h.strip() for h in lines[0].split(",")]
        values = [v.strip() for v in lines[-1].split(",")]
        out: dict[str, float] = {"_source_csv": csv_path.as_posix()}  # type: ignore[assignment]
        for h, v in zip(headers, values, strict=False):
            try:
                out[h] = float(v)
            except ValueError:
                continue
        if out:
            return out
    return {}


def run_finish(
    *,
    root: Path,
    weights: Path,
    yolo_data: Path,
    eval_dir: Path,
) -> dict[str, Any]:
    local = root / "validation" / "local"
    artifacts = root / "artifacts" / "runpod_v1"

    metrics = _parse_results_csv(eval_dir, weights)
    map50 = metrics.get("metrics/mAP50(B)", metrics.get("mAP50", 0.0))
    recall = metrics.get("metrics/recall(B)", metrics.get("recall", 0.0))
    precision = metrics.get("metrics/precision(B)", metrics.get("precision", 0.0))

    passed = map50 >= 0.25 and recall >= 0.20

    weights_sha = sha256_file(weights) if weights.is_file() else None

    gate = wrap_gate_report(
        gate="phase4_detector_baseline",
        passed=passed,
        confidence=float(map50) if map50 else None,
        stack="runpod_one_pass",
        claim="trained_on_fathomnet_holdout",
        known_limits=[
            "fathomnet_public_data_only",
            "sea_turtle_whole_image_proxy_labels_from_species_folders",
            "right_whale_not_in_v1_detector",
            "not_field_certified",
        ],
        artifact_sha256=weights_sha,
        audit_path=str(artifacts.relative_to(root)),
        extra={
            "metrics": metrics,
            "weights": str(weights),
            "yolo_data": str(yolo_data),
            "eval_dir": str(eval_dir),
        },
    )
    write_gate_report(local / "phase4_detector_baseline.json", gate)

    build_stats_path = root / "data" / "yolo" / "build_stats.json"
    manifest_excerpt: list[dict[str, Any]] = []
    if build_stats_path.is_file():
        manifest_excerpt.append(json.loads(build_stats_path.read_text(encoding="utf-8")))

    replay = write_replay_bundle(
        artifacts,
        encounters=[],
        manifest_excerpt=manifest_excerpt,
        model_card={
            "name": "ceto-dex-yolo11s-sea-turtle-v1",
            "weights": str(weights),
            "weights_sha256": weights_sha,
            "classes": ["sea_turtle", "hard_negative"],
            "metrics": metrics,
        },
        known_limits=list(gate["known_limits"]),
    )

    aggregate = wrap_gate_report(
        gate="ceto_dex_runpod_one_pass",
        passed=passed,
        stack="runpod_one_pass",
        claim="trained_on_fathomnet_holdout",
        known_limits=list(gate["known_limits"]),
        artifact_sha256=weights_sha,
        audit_path=str(artifacts.relative_to(root)),
        extra={"phase4": gate["passed"], "replay": replay},
    )
    write_gate_report(local / "ceto_dex_runpod_one_pass.json", aggregate)
    return aggregate


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--weights", type=Path, required=True)
    parser.add_argument("--yolo-data", type=Path, required=True)
    parser.add_argument("--eval-dir", type=Path, required=True)
    args = parser.parse_args(argv)
    report = run_finish(
        root=args.root,
        weights=args.weights,
        yolo_data=args.yolo_data,
        eval_dir=args.eval_dir,
    )
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if report["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
