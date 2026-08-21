"""Build YOLO dataset from Blue Spring manatee counting JSON line labels."""

from __future__ import annotations

import argparse
import json
import shutil
import zipfile
from pathlib import Path
from typing import Any


def _line_to_bbox(sx: float, sy: float, ex: float, ey: float, img_w: int, img_h: int) -> tuple[float, float, float, float]:
    x1 = max(0.0, min(sx, ex))
    y1 = max(0.0, min(sy, ey))
    x2 = min(float(img_w), max(sx, ex))
    y2 = min(float(img_h), max(sy, ey))
    return x1, y1, max(1.0, x2 - x1), max(1.0, y2 - y1)


def _yolo_line(bbox: tuple[float, float, float, float], w: int, h: int, class_id: int = 0) -> str:
    x, y, bw, bh = bbox
    cx = (x + bw / 2.0) / w
    cy = (y + bh / 2.0) / h
    return f"{class_id} {cx:.6f} {cy:.6f} {bw / w:.6f} {bh / h:.6f}"


def _split_for_index(idx: int) -> str:
    bucket = idx % 100
    if bucket < 8:
        return "test"
    if bucket < 20:
        return "val"
    return "train"


def build_from_dataset_root(root: Path, out: Path) -> dict[str, Any]:
    images_dir = root / "images"
    labels_dir = root / "labels"
    if not images_dir.is_dir() or not labels_dir.is_dir():
        raise FileNotFoundError(f"Expected images/ and labels/ under {root}")

    out.mkdir(parents=True, exist_ok=True)
    for split in ("train", "val", "test"):
        (out / "images" / split).mkdir(parents=True, exist_ok=True)
        (out / "labels" / split).mkdir(parents=True, exist_ok=True)

    stats: dict[str, Any] = {"images": 0, "boxes": 0, "skipped": 0}
    json_files = sorted(labels_dir.glob("*.json"))
    for idx, json_path in enumerate(json_files):
        data = json.loads(json_path.read_text(encoding="utf-8"))
        img_name = data.get("img_id") or json_path.stem
        img_candidates = list(images_dir.glob(img_name + ".*"))
        if not img_candidates:
            img_candidates = list(images_dir.glob(json_path.stem + ".*"))
        if not img_candidates:
            stats["skipped"] += 1
            continue
        img_path = img_candidates[0]
        try:
            from PIL import Image

            with Image.open(img_path) as im:
                w, h = im.size
        except Exception:
            stats["skipped"] += 1
            continue

        lines: list[str] = []
        for box in data.get("boxes", []):
            sx, sy, ex, ey = float(box["sx"]), float(box["sy"]), float(box["ex"]), float(box["ey"])
            lines.append(_yolo_line(_line_to_bbox(sx, sy, ex, ey, w, h), w, h))
        if not lines:
            stats["skipped"] += 1
            continue

        split = _split_for_index(idx)
        stem = f"manatee_{json_path.stem}"
        dst_img = out / "images" / split / f"{stem}{img_path.suffix.lower()}"
        shutil.copy2(img_path, dst_img)
        (out / "labels" / split / f"{stem}.txt").write_text("\n".join(lines) + "\n", encoding="utf-8")
        stats["images"] += 1
        stats["boxes"] += len(lines)

    yaml = out / "dataset.yaml"
    yaml.write_text(
        "\n".join(
            [
                f"path: {out.as_posix()}",
                "train: images/train",
                "val: images/val",
                "test: images/test",
                "names:",
                "  0: manatee",
                "",
            ]
        ),
        encoding="utf-8",
    )
    (out / "build_stats.json").write_text(json.dumps(stats, indent=2) + "\n", encoding="utf-8")
    return stats


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--zip-path", type=Path, required=True)
    parser.add_argument("--extract-root", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()

    args.extract_root.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(args.zip_path, "r") as zf:
        zf.extractall(args.extract_root)

    dataset_root = args.extract_root / "dataset"
    if not dataset_root.is_dir():
        # find nested dataset folder
        matches = list(args.extract_root.rglob("dataset/images"))
        if matches:
            dataset_root = matches[0].parent
        else:
            raise FileNotFoundError("Could not locate dataset/images after unzip")

    stats = build_from_dataset_root(dataset_root, args.out)
    print(json.dumps(stats, indent=2))
    return 0 if stats["images"] >= 50 else 1


if __name__ == "__main__":
    raise SystemExit(main())
