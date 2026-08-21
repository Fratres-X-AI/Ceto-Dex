from cetodex.encounter import build_encounter
from cetodex.models import BBox, DetectionAnnotation, Tracklet
from cetodex.refusal import RefusalConfig, evaluate_track


def _track(n: int, conf: float = 0.8) -> Tracklet:
    dets = [
        DetectionAnnotation(
            detection_id=f"d{i}",
            frame_id=f"f{i}",
            class_name="sea_turtle",
            bbox=BBox(10 + i, 10, 200, 150),
            confidence=conf,
            annotator="test",
        )
        for i in range(n)
    ]
    return Tracklet(track_id="t1", detections=dets)


def test_refusal_short_track():
    decision = evaluate_track(_track(1), class_name="sea_turtle", species_label="green", modality="underwater_video")
    assert not decision.allowed
    assert decision.refuse_reason == "too_few_frames"


def test_encounter_auto_label():
    enc = build_encounter(
        _track(4),
        asset_id="a1",
        class_name="sea_turtle",
        species_label="loggerhead",
        modality="underwater_video",
        config=RefusalConfig(min_frames=3),
    )
    assert enc.decision == "auto_label"
