"""Replay bundle schema for prove-it evidence (not demos)."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from cetodex.evidence_contract import sha256_file, wrap_gate_report, write_gate_report
from cetodex.models import Encounter


def encounter_to_replay_row(encounter: Encounter, *, clip_path: str | None = None) -> dict[str, Any]:
    row = encounter.to_dict()
    if clip_path:
        row["clip_path"] = clip_path
    return row


def write_replay_bundle(
    path: Path,
    *,
    encounters: list[Encounter],
    manifest_excerpt: list[dict[str, Any]],
    model_card: dict[str, Any],
    known_limits: list[str],
) -> dict[str, Any]:
    path.mkdir(parents=True, exist_ok=True)
    enc_path = path / "encounters.jsonl"
    lines = [json.dumps(encounter_to_replay_row(e), sort_keys=True) for e in encounters]
    enc_path.write_text("\n".join(lines) + "\n", encoding="utf-8")

    manifest_path = path / "manifest_excerpt.json"
    manifest_path.write_text(json.dumps(manifest_excerpt, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    model_path = path / "model_card.json"
    model_path.write_text(json.dumps(model_card, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    limits_path = path / "KNOWN_LIMITS.json"
    limits_path.write_text(json.dumps({"known_limits": known_limits}, indent=2) + "\n", encoding="utf-8")

    ledger = {
        "encounters_sha256": sha256_file(enc_path),
        "manifest_excerpt_sha256": sha256_file(manifest_path),
        "model_card_sha256": sha256_file(model_path),
    }
    ledger_path = path / "ledger.json"
    ledger_path.write_text(json.dumps(ledger, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    return {
        "bundle_path": str(path),
        "encounter_count": len(encounters),
        "ledger": ledger,
    }
