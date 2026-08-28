"""Shared Fratres gate / evidence JSON contract (Ceto-Dex)."""

from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

REQUIRED_KEYS = ("gate", "passed", "timestamp")
OPTIONAL_KEYS = (
    "ok",
    "scenario",
    "confidence",
    "refuse_reason",
    "known_limits",
    "artifact_sha256",
    "audit_path",
    "claim",
    "stack",
    "private",
)


REPO_ROOT = Path(__file__).resolve().parents[2]


def repo_relative(path: Path) -> str:
    """Render a path relative to the repo root as posix, never leaking a local
    absolute path (e.g. a username) into public evidence JSON."""
    try:
        return path.resolve().relative_to(REPO_ROOT).as_posix()
    except ValueError:
        return Path(path).name


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def validate_gate_report(data: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    for key in REQUIRED_KEYS:
        if key not in data:
            errors.append(f"missing {key}")
    if "passed" in data and not isinstance(data["passed"], bool):
        errors.append("passed must be bool")
    if "confidence" in data:
        conf = data["confidence"]
        if not isinstance(conf, (int, float)) or not (0.0 <= float(conf) <= 1.0):
            errors.append("confidence must be in [0, 1]")
    if "known_limits" in data and not isinstance(data["known_limits"], list):
        errors.append("known_limits must be a list")
    if "artifact_sha256" in data:
        sha = str(data["artifact_sha256"])
        if sha and len(sha) != 64:
            errors.append("artifact_sha256 must be 64 hex chars")
    return errors


def wrap_gate_report(
    *,
    gate: str,
    passed: bool,
    scenario: str | None = None,
    confidence: float | None = None,
    refuse_reason: str | None = None,
    known_limits: list[str] | None = None,
    artifact_sha256: str | None = None,
    audit_path: str | None = None,
    claim: str = "laptop_scaffold_only",
    stack: str | None = None,
    private: bool = True,
    extra: dict[str, Any] | None = None,
) -> dict[str, Any]:
    report: dict[str, Any] = {
        "gate": gate,
        "passed": passed,
        "ok": passed,
        "timestamp": utc_now(),
        "claim": claim,
        "private": private,
    }
    if scenario is not None:
        report["scenario"] = scenario
    if confidence is not None:
        report["confidence"] = confidence
    if refuse_reason is not None:
        report["refuse_reason"] = refuse_reason
    if known_limits is not None:
        report["known_limits"] = known_limits
    if artifact_sha256 is not None:
        report["artifact_sha256"] = artifact_sha256
    if audit_path is not None:
        report["audit_path"] = audit_path
    if stack is not None:
        report["stack"] = stack
    if extra:
        report.update(extra)
    errors = validate_gate_report(report)
    if errors:
        raise ValueError(f"invalid gate report: {errors}")
    return report


def write_gate_report(path: Path, report: dict[str, Any]) -> Path:
    errors = validate_gate_report(report)
    if errors:
        raise ValueError(f"invalid gate report: {errors}")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return path
