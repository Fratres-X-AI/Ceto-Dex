"""Phase 3 — annotation contract and COCO round-trip gate."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from cetodex.evidence_contract import wrap_gate_report, write_gate_report
from cetodex.manifest import round_trip_coco
from cetodex.models import BBox, DetectionAnnotation

ROOT = Path(__file__).resolve().parents[2]
LOCAL = ROOT / "validation" / "local"


def _fixture_detections() -> list[DetectionAnnotation]:
    return [
        DetectionAnnotation(
            detection_id="det_001",
            frame_id="frame_001",
            class_name="sea_turtle",
            bbox=BBox(x=120.0, y=80.0, w=240.0, h=180.0),
            confidence=0.91,
            annotator="fixture",
        ),
        DetectionAnnotation(
            detection_id="det_002",
            frame_id="frame_001",
            class_name="right_whale",
            bbox=BBox(x=640.0, y=220.0, w=520.0, h=300.0),
            confidence=0.88,
            annotator="fixture",
        ),
    ]


def run_gate() -> dict[str, Any]:
    detections = _fixture_detections()
    errors: list[str] = []
    try:
        round_trip_coco(detections)
    except ValueError as exc:
        errors.append(str(exc))
    passed = not errors
    return wrap_gate_report(
        gate="phase3_annotation_contract",
        passed=passed,
        stack="laptop_scaffold",
        known_limits=[
            "fixture annotations only",
            "no real model inference",
        ],
        extra={"errors": errors, "detection_count": len(detections)},
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Ceto-Dex phase 3 annotation gate")
    parser.add_argument("--out", type=Path, default=LOCAL / "phase3_annotation_contract.json")
    args = parser.parse_args(argv)
    report = run_gate()
    write_gate_report(args.out, report)
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if report["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
