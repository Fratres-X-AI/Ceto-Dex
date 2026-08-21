"""Tracklet-to-encounter builder for video-native evidence."""

from __future__ import annotations

from cetodex.models import Encounter, Tracklet
from cetodex.refusal import RefusalConfig, evaluate_track


def build_encounter(
    track: Tracklet,
    *,
    asset_id: str,
    class_name: str,
    species_label: str | None,
    modality: str,
    encounter_id: str | None = None,
    config: RefusalConfig | None = None,
) -> Encounter:
    decision = evaluate_track(
        track,
        class_name=class_name,
        species_label=species_label,
        modality=modality,
        config=config,
    )
    enc_id = encounter_id or f"enc_{track.track_id}"
    status = "auto_label" if decision.allowed else "refused"
    return Encounter(
        encounter_id=enc_id,
        track_id=track.track_id,
        asset_id=asset_id,
        class_name=class_name,
        species_label=species_label if decision.allowed else None,
        confidence=decision.confidence,
        decision=status,
        refuse_reason=decision.refuse_reason,
        frame_count=track.frame_count,
    )
