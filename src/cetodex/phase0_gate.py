"""Phase 0 — repo contract and doctrine presence gate."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

from cetodex import __version__
from cetodex.evidence_contract import wrap_gate_report, write_gate_report

ROOT = Path(__file__).resolve().parents[2]
LOCAL = ROOT / "validation" / "local"

REQUIRED_DOCS = (
    "README.md",
    "docs/DATA_SOURCES.md",
    "docs/CLAIMS.md",
    "docs/VALIDATION.md",
    "docs/RUNPOD.md",
    "docs/KNOWN_LIMITS.md",
)

REQUIRED_MODULES = (
    "src/cetodex/evidence_contract.py",
    "src/cetodex/manifest.py",
    "src/cetodex/refusal.py",
    "src/cetodex/tracker.py",
    "src/cetodex/encounter.py",
    "src/cetodex/replay.py",
    "src/cetodex/phase1_recon.py",
)


def run_gate(root: Path | None = None) -> dict[str, Any]:
    base = root or ROOT
    checks: dict[str, bool] = {}
    for rel in REQUIRED_DOCS:
        checks[f"doc:{rel}"] = (base / rel).is_file()
    for rel in REQUIRED_MODULES:
        checks[f"module:{rel}"] = (base / rel).is_file()
    checks["fixtures_manifest"] = (base / "fixtures" / "sample_manifest.jsonl").is_file()
    checks["version"] = bool(__version__)

    passed = all(checks.values())
    return wrap_gate_report(
        gate="phase0_repo_contract",
        passed=passed,
        stack="laptop_scaffold",
        known_limits=[
            "repo scaffold only",
            "no trained detector",
            "no field certification",
            "runpod training deferred",
        ],
        extra={"checks": checks, "version": __version__},
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Ceto-Dex phase 0 repo contract gate")
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--out", type=Path, default=LOCAL / "phase0_repo_contract.json")
    args = parser.parse_args(argv)
    report = run_gate(args.root)
    write_gate_report(args.out, report)
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if report["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
