"""Phase 2 — manifest integrity gate on fixture catalog."""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any

from cetodex.evidence_contract import wrap_gate_report, write_gate_report
from cetodex.manifest import validate_manifest

ROOT = Path(__file__).resolve().parents[2]
LOCAL = ROOT / "validation" / "local"
FIXTURE = ROOT / "fixtures" / "sample_manifest.jsonl"


def run_gate(manifest_path: Path | None = None) -> dict[str, Any]:
    path = manifest_path or FIXTURE
    result = validate_manifest(path)
    return wrap_gate_report(
        gate="phase2_manifest_integrity",
        passed=bool(result["passed"]),
        stack="laptop_scaffold",
        known_limits=[
            "fixture manifest only",
            "not production vault layout",
            "no bulk media on disk",
        ],
        extra={"manifest_validation": result},
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Ceto-Dex phase 2 manifest gate")
    parser.add_argument("--manifest", type=Path, default=FIXTURE)
    parser.add_argument("--out", type=Path, default=LOCAL / "phase2_manifest_integrity.json")
    args = parser.parse_args(argv)
    report = run_gate(args.manifest)
    write_gate_report(args.out, report)
    import json

    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if report["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
