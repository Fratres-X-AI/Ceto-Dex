"""Build YOLO dataset from FathomNet exports + SeaTurtles_Images (labelme/json)."""

from __future__ import annotations

import argparse
import json
import random
import shutil
from pathlib import Path
from typing import Any


def _bbox_from_points(points: list[list[float]]) -> tuple[float, float, float, float]:
    xs = [p[0] for p in points]
    ys = [p[1] for p in points]
    x1, x2 = min(xs), max(xs)
    y1, y2 = min(ys), max(ys)
    return x1, y1, x2 - x1, y2 - y1


def _yolo_line(bbox: tuple[float, float, float, float], w: int, h: int, class_id: int) -> str:
    x, y, bw, bh = bbox
    cx = (x + bw / 2.0) / w
    cy = (y + bh / 2.0) / h
    return f"{class_id} {cx:.6f} {cy:.6f} {bw / w:.6f} {bh / h:.6f}"


def ingest_labelme_dir(src: Path, out: Path, class_id: int, prefix: str, split: str) -> int:
    count = 0
    img_dir = out / "images" / split
    lbl_dir = out / "labels" / split
    img_dir.mkdir(parents=True, exist_ok=True)
    lbl_dir.mkdir(parents=True, exist_ok=True)

    for json_path in src.rglob("*.json"):
        if json_path.name.endswith(".json") and "labelme" not in json_path.name.lower():
            try:
                data = json.loads(json_path.read_text(encoding="utf-8"))
            except json.JSONDecodeError:
                continue
        else:
            continue
        image_path_value = data.get("imagePath") or data.get("image_path")
        if not image_path_value:
            continue
        img_path = (json_path.parent / image_path_value).resolve()
        if not img_path.is_file():
            candidates = list(json_path.parent.glob(json_path.stem + ".*"))
            img_path = next((p for p in candidates if p.suffix.lower() in {".jpg", ".jpeg", ".png"}), None)
            if img_path is None:
                continue
        shapes = data.get("shapes", [])
        lines: list[str] = []
        for shape in shapes:
            pts = shape.get("points", [])
            if len(pts) < 2:
                continue
            lines.append(_yolo_line(_bbox_from_points(pts), int(data.get("imageWidth", 1)), int(data.get("imageHeight", 1)), class_id))
        if not lines:
            # full-image turtle label if no shapes — skip weak labels
            continue
        stem = f"{prefix}_{json_path.stem}"
        dst_img = img_dir / f"{stem}{img_path.suffix.lower()}"
        if not dst_img.exists():
            shutil.copy2(img_path, dst_img)
        (lbl_dir / f"{stem}.txt").write_text("\n".join(lines) + "\n", encoding="utf-8")
        count += 1
    return count


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--sea-turtles-root", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()

    random.seed(42)
    args.out.mkdir(parents=True, exist_ok=True)
    stats: dict[str, Any] = {"sea_turtle": {}, "source": str(args.sea_turtles_root)}

    # Walk repo: assign splits by top-level folder hash
    roots = [p for p in args.sea_turtles_root.iterdir() if p.is_dir()]
    if not roots:
        roots = [args.sea_turtles_root]

    for root in roots:
        key = root.name
        bucket = random.choice(["train", "train", "train", "val", "test"])
        n = ingest_labelme_dir(root, args.out, class_id=0, prefix=f"st_{key}", split=bucket)
        stats["sea_turtle"][key] = {"split": bucket, "count": n}

    yaml = args.out / "dataset.yaml"
    yaml.write_text(
        "\n".join(
            [
                f"path: {args.out.as_posix()}",
                "train: images/train",
                "val: images/val",
                "test: images/test",
                "names:",
                "  0: sea_turtle",
                "  1: hard_negative",
                "",
            ]
        ),
        encoding="utf-8",
    )
    (args.out / "build_stats.json").write_text(json.dumps(stats, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(stats, indent=2))
    total = sum(v.get("count", 0) for v in stats["sea_turtle"].values())
    return 0 if total > 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
