"""Convert FathomNet COCO exports to YOLO detect layout with video-safe splits."""

from __future__ import annotations

import argparse
import json
import random
import shutil
from collections import defaultdict
from pathlib import Path
from typing import Any


def _load_coco_dir(coco_dir: Path) -> tuple[dict[str, Any], Path]:
    for name in ("annotations.json", "instances.json", "coco.json"):
        candidate = coco_dir / name
        if candidate.is_file():
            return json.loads(candidate.read_text(encoding="utf-8")), coco_dir
    ann_dir = coco_dir / "annotations"
    if ann_dir.is_dir():
        for p in sorted(ann_dir.glob("*.json")):
            return json.loads(p.read_text(encoding="utf-8")), coco_dir
    raise FileNotFoundError(f"No COCO json under {coco_dir}")


def _image_path(coco_root: Path, file_name: str) -> Path:
    for sub in ("images", "Images", ""):
        p = coco_root / sub / file_name if sub else coco_root / file_name
        if p.is_file():
            return p
    images = list(coco_root.rglob(file_name))
    if images:
        return images[0]
    raise FileNotFoundError(file_name)


def _split_key(image: dict[str, Any]) -> str:
    for key in ("video_id", "videoId", "deployment_id", "id"):
        if key in image and image[key]:
            return str(image[key])
    return str(image.get("id", "unknown"))


def _to_yolo_line(bbox: list[float], w: int, h: int, class_id: int) -> str:
    x, y, bw, bh = bbox
    cx = (x + bw / 2.0) / w
    cy = (y + bh / 2.0) / h
    nw = bw / w
    nh = bh / h
    return f"{class_id} {cx:.6f} {cy:.6f} {nw:.6f} {nh:.6f}"


def build_dataset(
    *,
    turtle_coco: Path,
    negative_coco: Path,
    out: Path,
    val_fraction: float,
    holdout_fraction: float,
    seed: int = 42,
) -> dict[str, Any]:
    random.seed(seed)
    out.mkdir(parents=True, exist_ok=True)

    splits = ("train", "val", "test")
    for split in splits:
        (out / "images" / split).mkdir(parents=True, exist_ok=True)
        (out / "labels" / split).mkdir(parents=True, exist_ok=True)

    stats: dict[str, Any] = {"classes": ["sea_turtle", "hard_negative"], "splits": {}, "errors": []}

    def ingest(coco_dir: Path, class_id: int, class_name: str) -> None:
        coco, root = _load_coco_dir(coco_dir)
        images = {img["id"]: img for img in coco.get("images", [])}
        anns_by_image: dict[int, list[dict[str, Any]]] = defaultdict(list)
        for ann in coco.get("annotations", []):
            anns_by_image[ann["image_id"]].append(ann)

        groups: dict[str, list[int]] = defaultdict(list)
        for img_id, img in images.items():
            groups[_split_key(img)].append(img_id)

        group_keys = sorted(groups.keys())
        random.shuffle(group_keys)
        n = len(group_keys)
        n_hold = max(1, int(n * holdout_fraction)) if n >= 3 else 0
        n_val = max(1, int(n * val_fraction)) if n >= 3 else max(0, n - 1)
        holdout = set(group_keys[:n_hold])
        val = set(group_keys[n_hold : n_hold + n_val])
        train = set(group_keys[n_hold + n_val :])

        def assign(img_id: int) -> str:
            key = _split_key(images[img_id])
            if key in holdout:
                return "test"
            if key in val:
                return "val"
            return "train"

        counts = {s: 0 for s in splits}
        for img_id, img in images.items():
            anns = anns_by_image.get(img_id, [])
            if not anns:
                continue
            split = assign(img_id)
            try:
                src = _image_path(root, img["file_name"])
            except FileNotFoundError as exc:
                stats["errors"].append(str(exc))
                continue
            w, h = int(img["width"]), int(img["height"])
            stem = Path(img["file_name"]).stem
            dst_img = out / "images" / split / f"{class_name}_{stem}{Path(img['file_name']).suffix}"
            if not dst_img.exists():
                shutil.copy2(src, dst_img)
            lines = [_to_yolo_line(a["bbox"], w, h, class_id) for a in anns if "bbox" in a]
            if not lines:
                continue
            label_path = out / "labels" / split / f"{dst_img.stem}.txt"
            label_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
            counts[split] += 1
        stats["splits"][class_name] = counts

    ingest(turtle_coco, 0, "sea_turtle")
    ingest(negative_coco, 1, "hard_negative")

    yaml_path = out / "dataset.yaml"
    yaml_path.write_text(
        "\n".join(
            [
                f"path: {out.as_posix()}",
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
    stats["dataset_yaml"] = str(yaml_path)
    stats["stats_path"] = str(out / "build_stats.json")
    (out / "build_stats.json").write_text(json.dumps(stats, indent=2) + "\n", encoding="utf-8")
    return stats


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--turtle-coco", type=Path, required=True)
    parser.add_argument("--negative-coco", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--val-fraction", type=float, default=0.15)
    parser.add_argument("--holdout-fraction", type=float, default=0.10)
    args = parser.parse_args()
    stats = build_dataset(
        turtle_coco=args.turtle_coco,
        negative_coco=args.negative_coco,
        out=args.out,
        val_fraction=args.val_fraction,
        holdout_fraction=args.holdout_fraction,
    )
    print(json.dumps(stats, indent=2))
    if stats["errors"] and sum(sum(v.values()) for v in stats["splits"].values()) == 0:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
