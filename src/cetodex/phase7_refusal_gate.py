"""Phase 5/7 laptop gates — tracking, encounters, refusal on synthetic tracks."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from cetodex.encounter import build_encounter
from cetodex.evidence_contract import wrap_gate_report, write_gate_report
from cetodex.models import BBox, DetectionAnnotation
from cetodex.refusal import RefusalConfig
from cetodex.tracker import GreedyIouTracker

ROOT = Path(__file__).resolve().parents[2]
LOCAL = ROOT / "validation" / "local"


def _synthetic_track_frames() -> list[list[DetectionAnnotation]]:
    frames: list[list[DetectionAnnotation]] = []
    for idx in range(5):
        shift = idx * 8.0
        frames.append(
            [
                DetectionAnnotation(
                    detection_id=f"det_t_{idx}",
                    frame_id=f"frame_{idx:03d}",
                    class_name="sea_turtle",
                    bbox=BBox(x=100.0 + shift, y=90.0, w=220.0, h=160.0),
                    confidence=0.7 + idx * 0.05,
                    annotator="synthetic",
                )
            ]
        )
    return frames


def run_video_encounter_gate() -> dict[str, Any]:
    tracker = GreedyIouTracker(iou_threshold=0.25, min_track_frames=3)
    for frame in _synthetic_track_frames():
        tracker.update(frame)
    tracks = tracker.finalize()
    long_tracks = [t for t in tracks if t.frame_count >= 3]
    passed = len(long_tracks) >= 1
    return {
        "passed": passed,
        "track_count": len(tracks),
        "long_track_count": len(long_tracks),
    }


def run_refusal_gate() -> dict[str, Any]:
    tracker = GreedyIouTracker(min_track_frames=1)
    for frame in _synthetic_track_frames():
        tracker.update(frame)
    tracks = tracker.finalize()
    track = tracks[0]

    good = build_encounter(
        track,
        asset_id="asset_turtle_001",
        class_name="sea_turtle",
        species_label="loggerhead",
        modality="underwater_video",
        config=RefusalConfig(min_confidence=0.5, min_frames=3),
    )
    short_track = track
    short_track.detections = track.detections[:1]
    refused = build_encounter(
        short_track,
        asset_id="asset_turtle_001",
        class_name="sea_turtle",
        species_label="loggerhead",
        modality="underwater_video",
    )

    checks = {
        "good_encounter_allowed": good.decision == "auto_label",
        "short_track_refused": refused.decision == "refused",
        "refuse_reason_present": refused.refuse_reason == "too_few_frames",
    }
    return {"passed": all(checks.values()), "checks": checks, "good": good.to_dict(), "refused": refused.to_dict()}


def run_gate() -> dict[str, Any]:
    video = run_video_encounter_gate()
    refusal = run_refusal_gate()
    passed = bool(video["passed"] and refusal["passed"])
    return wrap_gate_report(
        gate="phase7_refusal_review",
        passed=passed,
        stack="laptop_scaffold",
        known_limits=[
            "synthetic tracks only",
            "not trained detector output",
            "no human review UI yet",
        ],
        extra={"video_encounter": video, "refusal": refusal},
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Ceto-Dex phase 7 refusal/review gate")
    parser.add_argument("--out", type=Path, default=LOCAL / "phase7_refusal_review.json")
    args = parser.parse_args(argv)
    report = run_gate()
    write_gate_report(args.out, report)
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if report["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
