from cetodex.models import BBox, DetectionAnnotation
from cetodex.tracker import GreedyIouTracker


def test_tracker_links_frames():
    tracker = GreedyIouTracker(iou_threshold=0.2, min_track_frames=2)
    for i in range(3):
        tracker.update(
            [
                DetectionAnnotation(
                    detection_id=f"d{i}",
                    frame_id=f"f{i}",
                    class_name="sea_turtle",
                    bbox=BBox(10 + i * 5, 10, 100, 80),
                    confidence=0.9,
                    annotator="test",
                )
            ]
        )
    tracks = tracker.finalize()
    assert any(t.frame_count >= 2 for t in tracks)
