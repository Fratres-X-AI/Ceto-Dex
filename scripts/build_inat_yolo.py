"""Download iNaturalist research-grade photos into YOLO layout (presence proxy boxes)."""

from __future__ import annotations

import argparse
import json
import time
import urllib.parse
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

UA = "CetoDex/0.1 (Fratres X AI; marine utility training)"


def _split_for_index(idx: int) -> str:
    bucket = idx % 100
    if bucket < 8:
        return "test"
    if bucket < 20:
        return "val"
    return "train"


def _proxy_label(class_id: int) -> str:
    return f"{class_id} 0.5 0.5 0.85 0.85"


def _fetch_page(taxon: str, page: int, per_page: int) -> dict:
    params = urllib.parse.urlencode(
        {
            "taxon_name": taxon,
            "photos": "true",
            "quality_grade": "research",
            "per_page": per_page,
            "page": page,
        }
    )
    req = urllib.request.Request(f"https://api.inaturalist.org/v1/observations?{params}", headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=60) as resp:
        return json.loads(resp.read().decode("utf-8"))


def _download(url: str, dest: Path) -> bool:
    try:
        req = urllib.request.Request(url.replace("/square.", "/medium."), headers={"User-Agent": UA})
        with urllib.request.urlopen(req, timeout=60) as resp:
            dest.write_bytes(resp.read())
        return dest.stat().st_size > 5000
    except Exception:
        return False


def build_taxon(out: Path, taxon: str, class_id: int, max_images: int, prefix: str) -> int:
    out.mkdir(parents=True, exist_ok=True)
    for split in ("train", "val", "test"):
        (out / "images" / split).mkdir(parents=True, exist_ok=True)
        (out / "labels" / split).mkdir(parents=True, exist_ok=True)

    jobs: list[tuple[int, str, str]] = []
    page = 1
    seen: set[int] = set()
    while len(jobs) < max_images:
        data = _fetch_page(taxon, page, 200)
        results = data.get("results") or []
        if not results:
            break
        for obs in results:
            if len(jobs) >= max_images:
                break
            oid = int(obs["id"])
            if oid in seen:
                continue
            photos = obs.get("photos") or []
            if not photos:
                continue
            url = photos[0].get("url")
            if not url:
                continue
            seen.add(oid)
            split = _split_for_index(len(jobs))
            stem = f"{prefix}_{oid}"
            jobs.append((class_id, split, url, stem))
        page += 1
        time.sleep(0.08)
        if page > max(3, max_images // 80 + 2):
            break

    saved = 0

    def _one(job: tuple[int, str, str, str]) -> bool:
        class_id, split, url, stem = job
        img_path = out / "images" / split / f"{stem}.jpg"
        lbl_path = out / "labels" / split / f"{stem}.txt"
        if img_path.is_file() or _download(url, img_path):
            lbl_path.write_text(_proxy_label(class_id) + "\n", encoding="utf-8")
            return True
        return False

    with ThreadPoolExecutor(max_workers=12) as pool:
        futs = [pool.submit(_one, j) for j in jobs]
        for fut in as_completed(futs):
            if fut.result():
                saved += 1
                if saved % 50 == 0:
                    print(f"{taxon}: {saved}/{max_images}", flush=True)
    return saved


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()

    # class ids are local to this bundle; merge step remaps globally
    specs = [
        ("Eubalaena glacialis", 0, 180, "narw"),
        ("Megaptera novaeangliae", 0, 180, "hump"),
        ("Balaenoptera acutorostrata", 0, 120, "minke"),
        ("Dasyatis", 1, 150, "sting"),
        ("Myliobatis", 1, 150, "eagle"),
        ("Taeniura lymma", 1, 120, "bluespot"),
        ("Chaetodon", 2, 180, "bfish"),
        ("Holocentrus", 2, 120, "squirrel"),
        ("Acropora", 3, 120, "acropora"),
    ]
    names = ["whale", "stingray", "reef_fish", "coral_structure"]
    stats: dict[str, int] = {}
    for taxon, class_id, cap, prefix in specs:
        stats[taxon] = build_taxon(args.out, taxon, class_id, cap, prefix)

    yaml = args.out / "dataset.yaml"
    yaml.write_text(
        "\n".join(
            [
                f"path: {args.out.as_posix()}",
                "train: images/train",
                "val: images/val",
                "test: images/test",
                "names:",
                *[f"  {i}: {n}" for i, n in enumerate(names)],
                "",
            ]
        ),
        encoding="utf-8",
    )
    (args.out / "build_stats.json").write_text(json.dumps({"taxa": stats, "label_mode": "presence_proxy"}, indent=2) + "\n")
    print(json.dumps(stats, indent=2))
    return 0 if sum(stats.values()) >= 100 else 1


if __name__ == "__main__":
    raise SystemExit(main())
