"""Aggregate laptop-only Ceto-Dex gates (RunPod training deferred)."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from cetodex.evidence_contract import wrap_gate_report, write_gate_report
from cetodex.phase0_gate import run_gate as phase0
from cetodex.phase1_recon import run_gate as phase1
from cetodex.phase2_manifest_gate import run_gate as phase2
from cetodex.phase3_contract_gate import run_gate as phase3
from cetodex.phase7_refusal_gate import run_gate as phase7
from cetodex.replay import write_replay_bundle
from cetodex.encounter import build_encounter
from cetodex.models import BBox, DetectionAnnotation
from cetodex.tracker import GreedyIouTracker

ROOT = Path(__file__).resolve().parents[2]
LOCAL = ROOT / "validation" / "local"
ARTIFACTS = ROOT / "artifacts" / "laptop_replay_scaffold"


def _sample_replay_bundle() -> dict[str, Any]:
    tracker = GreedyIouTracker(min_track_frames=3)
    for idx in range(4):
        tracker.update(
            [
                DetectionAnnotation(
                    detection_id=f"det_{idx}",
                    frame_id=f"f_{idx}",
                    class_name="sea_turtle",
                    bbox=BBox(x=50.0 + idx * 10, y=40.0, w=200.0, h=140.0),
                    confidence=0.82,
                    annotator="laptop_gate",
                )
            ]
        )
    tracks = tracker.finalize()
    enc = build_encounter(
        tracks[0],
        asset_id="asset_turtle_fixture",
        class_name="sea_turtle",
        species_label="loggerhead",
        modality="underwater_video",
    )
    manifest_excerpt = [
        {
            "asset_id": "asset_turtle_fixture",
            "species_label": "loggerhead",
            "institution": "fixture",
            "license_status": "public_open",
        }
    ]
    return write_replay_bundle(
        ARTIFACTS,
        encounters=[enc],
        manifest_excerpt=manifest_excerpt,
        model_card={"name": "ceto-dex-scaffold", "weights": "none", "phase": "laptop_only"},
        known_limits=[
            "synthetic encounter only",
            "no trained detector",
            "runpod deferred",
        ],
    )


def run_all(*, offline_recon: bool = False) -> dict[str, Any]:
    reports = {
        "phase0": phase0(),
        "phase1": phase1(live=not offline_recon),
        "phase2": phase2(),
        "phase3": phase3(),
        "phase7": phase7(),
    }
    replay = _sample_replay_bundle()
    passed = all(r["passed"] for r in reports.values())
    aggregate = wrap_gate_report(
        gate="ceto_dex_laptop_aggregate",
        passed=passed,
        stack="laptop_scaffold",
        known_limits=[
            "laptop scaffold complete",
            "detector training deferred to runpod",
            "bulk clip extraction deferred",
            "not field certified",
        ],
        audit_path=ARTIFACTS.relative_to(ROOT).as_posix(),
        extra={"subgates": {k: v["passed"] for k, v in reports.items()}, "replay": replay},
    )
    return aggregate


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run all Ceto-Dex laptop gates")
    parser.add_argument("--out", type=Path, default=LOCAL / "ceto_dex_laptop_aggregate.json")
    parser.add_argument("--offline-recon", action="store_true")
    args = parser.parse_args(argv)

    for mod, out_name in (
        (phase0, "phase0_repo_contract.json"),
        (lambda: phase1(live=not args.offline_recon), "phase1_data_recon.json"),
        (phase2, "phase2_manifest_integrity.json"),
        (phase3, "phase3_annotation_contract.json"),
        (phase7, "phase7_refusal_review.json"),
    ):
        write_gate_report(LOCAL / out_name, mod())

    aggregate = run_all(offline_recon=args.offline_recon)
    write_gate_report(args.out, aggregate)
    print(json.dumps(aggregate, indent=2, sort_keys=True))
    return 0 if aggregate["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
