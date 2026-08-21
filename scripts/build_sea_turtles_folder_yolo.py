"""Build YOLO detect dataset from SeaTurtles_Images folder layout (whole-image proxy boxes)."""

from __future__ import annotations

import argparse
import json
import random
import shutil
from pathlib import Path
from typing import Any

try:
    from PIL import Image
except ImportError:
    Image = None  # type: ignore


def _split_for_index(idx: int, val_fraction: float, test_fraction: float) -> str:
    bucket = idx % 100
    if bucket < int(test_fraction * 100):
        return "test"
    if bucket < int((test_fraction + val_fraction) * 100):
        return "val"
    return "train"


def _full_image_label() -> str:
    # Honest proxy: species folder label treated as turtle present (center 90% box)
    return "0 0.5 0.5 0.9 0.9"


def build_from_folders(src: Path, out: Path, val_fraction: float, test_fraction: float) -> dict[str, Any]:
    out.mkdir(parents=True, exist_ok=True)
    for split in ("train", "val", "test"):
        (out / "images" / split).mkdir(parents=True, exist_ok=True)
        (out / "labels" / split).mkdir(parents=True, exist_ok=True)
    stats: dict[str, Any] = {"species": {}, "total": 0, "label_mode": "whole_image_proxy"}

    images_root = src / "Images"
    if not images_root.is_dir():
        images_root = src

    for species_dir in sorted(images_root.iterdir()):
        if not species_dir.is_dir():
            continue
        species_counts = {"train": 0, "val": 0, "test": 0}
        count = 0
        for idx, img_path in enumerate(sorted(species_dir.glob("*"))):
            if img_path.suffix.lower() not in {".jpg", ".jpeg", ".png"}:
                continue
            split = _split_for_index(idx, val_fraction, test_fraction)
            img_out = out / "images" / split
            lbl_out = out / "labels" / split
            stem = f"{species_dir.name.replace(' ', '_')}_{img_path.stem}"
            dst = img_out / f"{stem}{img_path.suffix.lower()}"
            if not dst.exists():
                shutil.copy2(img_path, dst)
            (lbl_out / f"{stem}.txt").write_text(_full_image_label() + "\n", encoding="utf-8")
            species_counts[split] += 1
            count += 1
        stats["species"][species_dir.name] = {"counts": species_counts, "count": count}
        stats["total"] += count

    yaml = out / "dataset.yaml"
    yaml.write_text(
        "\n".join(
            [
                f"path: {out.as_posix()}",
                "train: images/train",
                "val: images/val",
                "test: images/test",
                "names:",
                "  0: sea_turtle",
                "",
            ]
        ),
        encoding="utf-8",
    )
    (out / "build_stats.json").write_text(json.dumps(stats, indent=2) + "\n", encoding="utf-8")
    return stats


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--sea-turtles-root", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--val-fraction", type=float, default=0.12)
    parser.add_argument("--test-fraction", type=float, default=0.08)
    args = parser.parse_args()
    stats = build_from_folders(args.sea_turtles_root, args.out, args.val_fraction, args.test_fraction)
    print(json.dumps(stats, indent=2))
    return 0 if stats["total"] > 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
