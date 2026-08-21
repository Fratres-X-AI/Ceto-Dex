"""Phase 1 — data source reconnaissance (counts, licenses, gaps). Laptop-safe."""

from __future__ import annotations

import argparse
import json
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any

from cetodex.evidence_contract import wrap_gate_report, write_gate_report

ROOT = Path(__file__).resolve().parents[2]
LOCAL = ROOT / "validation" / "local"
CATALOG = ROOT / "fixtures" / "phase1_sources_catalog.json"

FATHOMNET_API = "https://api.fathomnet.org"
TURTLE_CONCEPTS = (
    "Cheloniidae",
    "Caretta caretta",
    "Chelonia mydas",
    "Eretmochelys imbricata",
    "Dermochelys coriacea",
    "Lepidochelys kempii",
)
WHALE_NOTE = "right_whale_public_photo_id_and_survey_metadata"


def _http_json(url: str, timeout: float = 20.0) -> tuple[dict[str, Any] | list[Any] | None, str | None]:
    req = urllib.request.Request(url, headers={"Accept": "application/json", "User-Agent": "Ceto-Dex/0.1"})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            payload = resp.read().decode("utf-8")
            return json.loads(payload), None
    except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as exc:
        return None, str(exc)


def query_fathomnet_concept(concept: str) -> dict[str, Any]:
    # FathomNet exposes concept search via REST; count endpoint may vary by deployment.
    quoted = urllib.parse.quote(concept)
    urls = (
        f"{FATHOMNET_API}/v1/image/count?concept={quoted}",
        f"{FATHOMNET_API}/v1/concepts/{quoted}",
    )
    results: dict[str, Any] = {"concept": concept, "attempts": []}
    for url in urls:
        data, err = _http_json(url)
        results["attempts"].append({"url": url, "error": err, "ok": err is None})
        if data is not None:
            results["response"] = data
            break
    return results


def load_catalog() -> dict[str, Any]:
    return json.loads(CATALOG.read_text(encoding="utf-8"))


def run_recon(*, live: bool = True) -> dict[str, Any]:
    catalog = load_catalog()
    fathomnet: dict[str, Any] = {"live_query_attempted": live, "concepts": []}
    live_errors: list[str] = []

    if live:
        for concept in TURTLE_CONCEPTS:
            row = query_fathomnet_concept(concept)
            fathomnet["concepts"].append(row)
            if "response" not in row:
                live_errors.append(concept)

    right_whale = catalog["sources"]["north_atlantic_right_whale"]
    gaps: list[str] = []
    if right_whale.get("video_training_ready") is False:
        gaps.append("right_whale_requires_curated_video_or_photo_pipeline_not_bulk_survey_csv")
    if fathomnet["live_query_attempted"] and live_errors:
        gaps.append("fathomnet_live_count_partial_or_unavailable_use_catalog_and_manual_verify")

    training_readiness = {
        "sea_turtle_detection": "conditional_on_fathomnet_clip_extraction",
        "sea_turtle_species": "conditional_on_per_species_label_counts",
        "right_whale_detection": "conditional_on_aerial_surface_video_curation",
        "right_whale_individual_id": "advanced_gate_public_photo_id_exists_not_video_native_yet",
        "manatee": "phase3_optional",
    }

    return {
        "catalog": catalog,
        "fathomnet": fathomnet,
        "live_errors": live_errors,
        "gaps": gaps,
        "training_readiness": training_readiness,
        "recommend_runpod_after": [
            "manifest_integrity_gate_green",
            "clip_extraction_complete",
            "train_val_test_splits_by_video_id",
        ],
    }


def run_gate(*, live: bool = True) -> dict[str, Any]:
    recon = run_recon(live=live)
    catalog = recon["catalog"]
    required_sources = ("fathomnet", "north_atlantic_right_whale")
    checks = {
        "catalog_present": CATALOG.is_file(),
        "catalog_has_required_sources": all(s in catalog.get("sources", {}) for s in required_sources),
        "license_fields_documented": all(
            "license_status" in catalog["sources"][s] for s in required_sources
        ),
        "training_readiness_documented": bool(recon["training_readiness"]),
    }
    passed = all(checks.values())
    return wrap_gate_report(
        gate="phase1_data_recon",
        passed=passed,
        stack="laptop_scaffold",
        known_limits=[
            "recon and catalog only",
            "no bulk video download",
            "no detector weights",
            "live API counts best-effort",
        ],
        extra={"checks": checks, "recon": recon},
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Ceto-Dex phase 1 data recon gate")
    parser.add_argument("--out", type=Path, default=LOCAL / "phase1_data_recon.json")
    parser.add_argument("--offline", action="store_true", help="Skip live FathomNet API calls")
    args = parser.parse_args(argv)
    report = run_gate(live=not args.offline)
    write_gate_report(args.out, report)
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if report["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
