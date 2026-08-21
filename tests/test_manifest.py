from pathlib import Path

from cetodex.manifest import round_trip_coco, validate_manifest
from cetodex.models import BBox, DetectionAnnotation

ROOT = Path(__file__).resolve().parents[1]


def test_fixture_manifest_valid():
    result = validate_manifest(ROOT / "fixtures" / "sample_manifest.jsonl")
    assert result["passed"]
    assert result["row_count"] == 3


def test_coco_round_trip():
    dets = [
        DetectionAnnotation(
            detection_id="1",
            frame_id="f0",
            class_name="sea_turtle",
            bbox=BBox(1, 2, 3, 4),
            confidence=0.9,
            annotator="test",
        )
    ]
    round_trip_coco(dets)
