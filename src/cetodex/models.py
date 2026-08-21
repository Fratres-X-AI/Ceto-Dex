"""Domain constants and typed records for Ceto-Dex."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any

PRIMARY_CLASSES = ("sea_turtle", "right_whale")

TURTLE_SPECIES = (
    "loggerhead",
    "green",
    "hawksbill",
    "kemp_ridley",
    "leatherback",
    "olive_ridley",
    "flatback",
)

PHASE3_OPTIONAL = ("manatee",)

REFUSE_REASONS = (
    "low_confidence",
    "too_few_frames",
    "partial_body_only",
    "high_blur_or_turbidity",
    "source_out_of_distribution",
    "species_evidence_insufficient",
    "conflicting_frame_labels",
    "unsupported_modality",
)


@dataclass(frozen=True)
class BBox:
    x: float
    y: float
    w: float
    h: float

    def area(self) -> float:
        return max(0.0, self.w) * max(0.0, self.h)

    def to_xyxy(self) -> tuple[float, float, float, float]:
        return (self.x, self.y, self.x + self.w, self.y + self.h)


@dataclass
class SourceAsset:
    asset_id: str
    source_url: str
    institution: str
    license_status: str
    modality: str
    species_label: str
    sha256: str
    video_id: str | None = None
    geography: str | None = None
    depth_m: float | None = None
    platform: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class FrameSample:
    frame_id: str
    asset_id: str
    frame_index: int
    split: str
    timestamp_ms: int | None = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class DetectionAnnotation:
    detection_id: str
    frame_id: str
    class_name: str
    bbox: BBox
    confidence: float
    annotator: str

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["bbox"] = asdict(self.bbox)
        return data


@dataclass
class Tracklet:
    track_id: str
    detections: list[DetectionAnnotation] = field(default_factory=list)

    @property
    def frame_count(self) -> int:
        return len(self.detections)

    def mean_confidence(self) -> float:
        if not self.detections:
            return 0.0
        return sum(d.confidence for d in self.detections) / len(self.detections)


@dataclass
class Encounter:
    encounter_id: str
    track_id: str
    asset_id: str
    class_name: str
    species_label: str | None
    confidence: float
    decision: str
    refuse_reason: str | None = None
    frame_count: int = 0

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)
