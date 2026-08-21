"""Convert DeepFish zip (YOLO txt per frame) to standard YOLO detect layout."""

from __future__ import annotations

import argparse
import json
import random
import shutil
import zipfile
from pathlib import Path


def _split_for_path(path: str) -> str:
    random.seed(path)
    r = random.random()
    if r < 0.08:
        return "test"
    if r < 0.20:
        return "val"
    return "train"


def build(zip_path: Path, extract_root: Path, out: Path, class_id: int = 0, max_images: int = 8000) -> dict:
    extract_root.mkdir(parents=True, exist_ok=True)
    if not (extract_root / "Deepfish").is_dir():
        with zipfile.ZipFile(zip_path, "r") as zf:
            zf.extractall(extract_root)

    for split in ("train", "val", "test"):
        (out / "images" / split).mkdir(parents=True, exist_ok=True)
        (out / "labels" / split).mkdir(parents=True, exist_ok=True)

    root = extract_root / "Deepfish"
    saved = 0
    skipped_empty = 0
    for txt in sorted(root.rglob("*.txt")):
        if txt.name == "classes.txt":
            continue
        if "Nagative_samples" in txt.as_posix():
            continue
        label_text = txt.read_text(encoding="utf-8").strip()
        if not label_text:
            skipped_empty += 1
            continue
        img = txt.with_suffix(".jpg")
        if not img.is_file():
            continue
        split = _split_for_path(str(txt))
        stem = f"deepfish_{txt.stem}"
        dst_img = out / "images" / split / f"{stem}.jpg"
        dst_lbl = out / "labels" / split / f"{stem}.txt"
        if not dst_img.exists():
            shutil.copy2(img, dst_img)
        remapped = []
        for line in label_text.splitlines():
            parts = line.split()
            if len(parts) < 5:
                continue
            remapped.append(f"{class_id} {' '.join(parts[1:])}")
        if not remapped:
            continue
        dst_lbl.write_text("\n".join(remapped) + "\n", encoding="utf-8")
        saved += 1
        if saved >= max_images:
            break

    yaml = out / "dataset.yaml"
    yaml.write_text(
        "\n".join(
            [
                f"path: {out.as_posix()}",
                "train: images/train",
                "val: images/val",
                "test: images/test",
                "names:",
                "  0: reef_fish",
                "",
            ]
        ),
        encoding="utf-8",
    )
    stats = {"images": saved, "skipped_empty": skipped_empty, "source": "DeepFish", "label_mode": "real_bbox"}
    (out / "build_stats.json").write_text(json.dumps(stats, indent=2) + "\n")
    return stats


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--zip-path", type=Path, required=True)
    parser.add_argument("--extract-root", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--max-images", type=int, default=8000)
    args = parser.parse_args()
    stats = build(args.zip_path, args.extract_root, args.out, max_images=args.max_images)
    print(json.dumps(stats, indent=2))
    return 0 if stats["images"] >= 200 else 1


if __name__ == "__main__":
    raise SystemExit(main())
