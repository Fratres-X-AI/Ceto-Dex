"""Merge multiple YOLO datasets into one multi-class marine utility set."""

from __future__ import annotations

import argparse
import json
import shutil
from pathlib import Path

# Global class order — useful marine utility taxonomy for Ceto-Dex
GLOBAL_NAMES = [
    "whale",
    "shark",
    "stingray",
    "reef_fish",
    "coral_structure",
    "sea_turtle",
    "manatee",
]


def _remap_file(src_lbl: Path, dst_lbl: Path, class_map: dict[int, int]) -> int:
    lines_out: list[str] = []
    for line in src_lbl.read_text(encoding="utf-8").splitlines():
        parts = line.split()
        if len(parts) < 5:
            continue
        old = int(float(parts[0]))
        new = class_map.get(old)
        if new is None:
            continue
        lines_out.append(f"{new} {' '.join(parts[1:])}")
    if not lines_out:
        return 0
    dst_lbl.write_text("\n".join(lines_out) + "\n", encoding="utf-8")
    return len(lines_out)


def merge_sources(out: Path, sources: list[tuple[Path, dict[int, int], str]]) -> dict:
    for split in ("train", "val", "test"):
        (out / "images" / split).mkdir(parents=True, exist_ok=True)
        (out / "labels" / split).mkdir(parents=True, exist_ok=True)

    stats: dict[str, object] = {"sources": {}, "images": 0, "boxes": 0}
    for src, class_map, tag in sources:
        src_stats = {"images": 0, "boxes": 0}
        for split in ("train", "val", "test"):
            img_dir = src / "images" / split
            lbl_dir = src / "labels" / split
            if not img_dir.is_dir():
                continue
            for img in sorted(img_dir.iterdir()):
                if img.suffix.lower() not in {".jpg", ".jpeg", ".png"}:
                    continue
                lbl = lbl_dir / f"{img.stem}.txt"
                if not lbl.is_file():
                    continue
                stem = f"{tag}_{img.stem}"
                dst_img = out / "images" / split / f"{stem}{img.suffix.lower()}"
                dst_lbl = out / "labels" / split / f"{stem}.txt"
                if not dst_img.exists():
                    shutil.copy2(img, dst_img)
                n = _remap_file(lbl, dst_lbl, class_map)
                if n:
                    src_stats["images"] += 1
                    src_stats["boxes"] += n
        stats["sources"][tag] = src_stats
        stats["images"] = int(stats["images"]) + src_stats["images"]
        stats["boxes"] = int(stats["boxes"]) + src_stats["boxes"]

    yaml = out / "dataset.yaml"
    yaml.write_text(
        "\n".join(
            [
                f"path: {out.as_posix()}",
                "train: images/train",
                "val: images/val",
                "test: images/test",
                "names:",
                *[f"  {i}: {n}" for i, n in enumerate(GLOBAL_NAMES)],
                "",
            ]
        ),
        encoding="utf-8",
    )
    (out / "build_stats.json").write_text(json.dumps(stats, indent=2) + "\n")
    return stats


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--inat", type=Path)
    parser.add_argument("--deepfish", type=Path)
    parser.add_argument("--fathom-shark", type=Path)
    parser.add_argument("--fathom-ray", type=Path)
    parser.add_argument("--turtle", type=Path)
    parser.add_argument("--manatee", type=Path)
    args = parser.parse_args()

    # inat local: 0 whale, 1 stingray, 2 reef_fish, 3 coral
    sources: list[tuple[Path, dict[int, int], str]] = []
    if args.inat and args.inat.is_dir():
        sources.append((args.inat, {0: 0, 1: 2, 2: 3, 3: 4}, "inat"))
    if args.deepfish and args.deepfish.is_dir():
        sources.append((args.deepfish, {0: 3}, "deepfish"))
    if args.fathom_shark and args.fathom_shark.is_dir():
        sources.append((args.fathom_shark, {0: 1}, "fshark"))
    if args.fathom_ray and args.fathom_ray.is_dir():
        sources.append((args.fathom_ray, {0: 2}, "fray"))
    if args.turtle and args.turtle.is_dir():
        sources.append((args.turtle, {0: 5}, "turtle"))
    if args.manatee and args.manatee.is_dir():
        sources.append((args.manatee, {0: 6}, "manatee"))

    stats = merge_sources(args.out, sources)
    print(json.dumps(stats, indent=2))
    return 0 if int(stats["images"]) >= 500 else 1


if __name__ == "__main__":
    raise SystemExit(main())
