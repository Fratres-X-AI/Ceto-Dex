"""Manifest schema, integrity checks, and COCO round-trip helpers."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from cetodex.models import BBox, DetectionAnnotation, SourceAsset

REQUIRED_MANIFEST_FIELDS = (
    "asset_id",
    "source_url",
    "institution",
    "license_status",
    "modality",
    "species_label",
    "sha256",
)

ALLOWED_LICENSE_STATUSES = {
    "public_open",
    "public_with_attribution",
    "permission_required",
    "research_only",
    "unknown",
}


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def load_manifest_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for line_no, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        stripped = line.strip()
        if not stripped:
            continue
        try:
            row = json.loads(stripped)
        except json.JSONDecodeError as exc:
            raise ValueError(f"{path}:{line_no}: invalid JSON: {exc}") from exc
        if not isinstance(row, dict):
            raise ValueError(f"{path}:{line_no}: manifest row must be object")
        rows.append(row)
    return rows


def validate_manifest_row(row: dict[str, Any], seen_ids: set[str], seen_hashes: set[str]) -> list[str]:
    errors: list[str] = []
    for key in REQUIRED_MANIFEST_FIELDS:
        if key not in row or not str(row[key]).strip():
            errors.append(f"missing {key}")
    asset_id = str(row.get("asset_id", ""))
    sha = str(row.get("sha256", ""))
    if asset_id:
        if asset_id in seen_ids:
            errors.append(f"duplicate asset_id {asset_id}")
        seen_ids.add(asset_id)
    if sha:
        if len(sha) != 64:
            errors.append(f"invalid sha256 for {asset_id or '?'}")
        if sha in seen_hashes:
            errors.append(f"duplicate sha256 across splits for {asset_id or '?'}")
        seen_hashes.add(sha)
    license_status = str(row.get("license_status", ""))
    if license_status and license_status not in ALLOWED_LICENSE_STATUSES:
        errors.append(f"unknown license_status {license_status}")
    split = row.get("split")
    if split is not None and split not in {"train", "val", "test", "holdout", "unassigned"}:
        errors.append(f"invalid split {split}")
    return errors


def validate_manifest(path: Path) -> dict[str, Any]:
    rows = load_manifest_jsonl(path)
    errors: list[str] = []
    seen_ids: set[str] = set()
    seen_hashes: set[str] = set()
    splits: dict[str, int] = {}
    for row in rows:
        errors.extend(validate_manifest_row(row, seen_ids, seen_hashes))
        split = str(row.get("split", "unassigned"))
        splits[split] = splits.get(split, 0) + 1
    return {
        "path": str(path),
        "row_count": len(rows),
        "splits": splits,
        "errors": errors,
        "passed": len(errors) == 0 and len(rows) > 0,
    }


def source_asset_from_row(row: dict[str, Any]) -> SourceAsset:
    return SourceAsset(
        asset_id=str(row["asset_id"]),
        source_url=str(row["source_url"]),
        institution=str(row["institution"]),
        license_status=str(row["license_status"]),
        modality=str(row["modality"]),
        species_label=str(row["species_label"]),
        sha256=str(row["sha256"]),
        video_id=row.get("video_id"),
        geography=row.get("geography"),
        depth_m=row.get("depth_m"),
        platform=row.get("platform"),
    )


def detections_to_coco(
    detections: list[DetectionAnnotation],
    *,
    image_id: str,
    width: int,
    height: int,
) -> dict[str, Any]:
    images = [{"id": image_id, "width": width, "height": height}]
    categories = []
    seen: dict[str, int] = {}
    coco_detections: list[dict[str, Any]] = []
    for det in detections:
        if det.class_name not in seen:
            seen[det.class_name] = len(seen) + 1
            categories.append({"id": seen[det.class_name], "name": det.class_name})
        bbox = det.bbox
        coco_detections.append(
            {
                "id": det.detection_id,
                "image_id": image_id,
                "category_id": seen[det.class_name],
                "bbox": [bbox.x, bbox.y, bbox.w, bbox.h],
                "score": det.confidence,
                "annotator": det.annotator,
            }
        )
    return {
        "images": images,
        "categories": categories,
        "annotations": coco_detections,
    }


def detections_from_coco(coco: dict[str, Any]) -> list[DetectionAnnotation]:
    cat_by_id = {c["id"]: c["name"] for c in coco.get("categories", [])}
    out: list[DetectionAnnotation] = []
    for ann in coco.get("annotations", []):
        x, y, w, h = ann["bbox"]
        out.append(
            DetectionAnnotation(
                detection_id=str(ann["id"]),
                frame_id=str(ann["image_id"]),
                class_name=str(cat_by_id[ann["category_id"]]),
                bbox=BBox(x=float(x), y=float(y), w=float(w), h=float(h)),
                confidence=float(ann.get("score", 1.0)),
                annotator=str(ann.get("annotator", "coco_import")),
            )
        )
    return out


def round_trip_coco(detections: list[DetectionAnnotation]) -> list[DetectionAnnotation]:
    coco = detections_to_coco(detections, image_id="frame_0", width=1920, height=1080)
    restored = detections_from_coco(coco)
    if len(restored) != len(detections):
        raise ValueError("coco round-trip changed detection count")
    for original, back in zip(detections, restored, strict=True):
        if original.class_name != back.class_name:
            raise ValueError("coco round-trip changed class_name")
        if original.bbox.to_xyxy() != back.bbox.to_xyxy():
            raise ValueError("coco round-trip changed bbox")
    return restored
