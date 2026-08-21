"""Greedy IOU tracker for laptop validation (not production ByteTrack)."""

from __future__ import annotations

from cetodex.iou import iou
from cetodex.models import DetectionAnnotation, Tracklet


class GreedyIouTracker:
    def __init__(self, *, iou_threshold: float = 0.3, min_track_frames: int = 3, max_misses: int = 1) -> None:
        self.iou_threshold = iou_threshold
        self.min_track_frames = min_track_frames
        self.max_misses = max_misses
        self._next_track_id = 1
        self._active: dict[str, Tracklet] = {}
        self._misses: dict[str, int] = {}
        self._finished: list[Tracklet] = []

    def _close_track(self, track_id: str) -> None:
        track = self._active.pop(track_id, None)
        self._misses.pop(track_id, None)
        if track and track.frame_count >= self.min_track_frames:
            self._finished.append(track)

    def _new_track(self, detection: DetectionAnnotation) -> None:
        track_id = f"trk_{self._next_track_id:04d}"
        self._next_track_id += 1
        self._active[track_id] = Tracklet(track_id=track_id, detections=[detection])
        self._misses[track_id] = 0

    def update(self, frame_detections: list[DetectionAnnotation]) -> list[Tracklet]:
        unmatched = list(frame_detections)
        matched_tracks: set[str] = set()

        for track_id, track in list(self._active.items()):
            if not unmatched:
                break
            last = track.detections[-1]
            best_idx = -1
            best_iou = 0.0
            for idx, det in enumerate(unmatched):
                score = iou(last.bbox, det.bbox)
                if score >= self.iou_threshold and score > best_iou:
                    best_iou = score
                    best_idx = idx
            if best_idx >= 0:
                track.detections.append(unmatched.pop(best_idx))
                self._misses[track_id] = 0
                matched_tracks.add(track_id)

        for det in unmatched:
            self._new_track(det)

        for track_id in list(self._active.keys()):
            if track_id in matched_tracks:
                continue
            self._misses[track_id] = self._misses.get(track_id, 0) + 1
            if self._misses[track_id] > self.max_misses:
                self._close_track(track_id)

        return list(self._active.values()) + self._finished

    def finalize(self) -> list[Tracklet]:
        for track_id in list(self._active.keys()):
            self._close_track(track_id)
        return self._finished
