"""Confidence-gated refusal logic before consequential labels."""

from __future__ import annotations

from dataclasses import dataclass

from cetodex.models import REFUSE_REASONS, TURTLE_SPECIES, Tracklet


@dataclass(frozen=True)
class RefusalConfig:
    min_confidence: float = 0.55
    min_frames: int = 3
    min_bbox_area: float = 400.0
    supported_species: tuple[str, ...] = TURTLE_SPECIES
    supported_modalities: tuple[str, ...] = ("underwater_video", "aerial_video", "surface_video", "photo_sequence")


@dataclass(frozen=True)
class RefusalDecision:
    allowed: bool
    refuse_reason: str | None
    confidence: float


def evaluate_track(
    track: Tracklet,
    *,
    class_name: str,
    species_label: str | None,
    modality: str,
    config: RefusalConfig | None = None,
) -> RefusalDecision:
    cfg = config or RefusalConfig()
    confidence = track.mean_confidence()

    if modality not in cfg.supported_modalities:
        return RefusalDecision(False, "unsupported_modality", confidence)
    if track.frame_count < cfg.min_frames:
        return RefusalDecision(False, "too_few_frames", confidence)
    if confidence < cfg.min_confidence:
        return RefusalDecision(False, "low_confidence", confidence)

    areas = [d.bbox.area() for d in track.detections]
    if areas and max(areas) < cfg.min_bbox_area:
        return RefusalDecision(False, "partial_body_only", confidence)

    classes = {d.class_name for d in track.detections}
    if len(classes) > 1:
        return RefusalDecision(False, "conflicting_frame_labels", confidence)

    if class_name == "sea_turtle" and species_label:
        if species_label not in cfg.supported_species:
            return RefusalDecision(False, "species_evidence_insufficient", confidence)

    return RefusalDecision(True, None, confidence)


def is_valid_refuse_reason(reason: str | None) -> bool:
    return reason is None or reason in REFUSE_REASONS
