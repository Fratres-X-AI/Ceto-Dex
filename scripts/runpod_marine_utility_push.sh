#!/usr/bin/env bash
# Parallel data build then sequential max-GPU training
set -euo pipefail
ROOT=/workspace/ceto-dex
DATA=$ROOT/data
LOG=$ROOT/run_marine_push.log
exec > >(tee -a "$LOG") 2>&1
echo "=== MARINE UTILITY PUSH v2 START $(date -u +%Y-%m-%dT%H:%M:%SZ) ==="
cd "$ROOT"
python -m pip install -q --break-system-packages pillow ultralytics requests

pids=()
python scripts/build_inat_yolo.py --out "$DATA/yolo_inat_marine" &
pids+=($!)
python scripts/build_deepfish_yolo.py \
  --zip-path "$DATA/raw/deepfish.zip" \
  --extract-root "$DATA/raw/deepfish_extract" \
  --out "$DATA/yolo_deepfish" \
  --max-images 6000 &
pids+=($!)

if [ ! -f "$DATA/yolo_fathom_shark/.done" ]; then
  (
    mkdir -p "$DATA/raw/fathomnet_shark/img"
    fathomnet-generate -f yolo --img-download "$DATA/raw/fathomnet_shark/img" \
      -c Carcharhinus -o "$DATA/yolo_fathom_shark" --taxa fathomnet || true
    touch "$DATA/yolo_fathom_shark/.done"
  ) &
  pids+=($!)
fi
if [ ! -f "$DATA/yolo_fathom_ray/.done" ]; then
  (
    mkdir -p "$DATA/raw/fathomnet_ray/img"
    fathomnet-generate -f yolo --img-download "$DATA/raw/fathomnet_ray/img" \
      -c Rajiformes -o "$DATA/yolo_fathom_ray" --taxa fathomnet || true
    touch "$DATA/yolo_fathom_ray/.done"
  ) &
  pids+=($!)
fi

for pid in "${pids[@]}"; do wait "$pid" || true; done
echo "=== DATA BUILDS DONE $(date -u +%Y-%m-%dT%H:%M:%SZ) ==="

python scripts/merge_marine_yolo.py \
  --out "$DATA/yolo_marine_utility" \
  --inat "$DATA/yolo_inat_marine" \
  --deepfish "$DATA/yolo_deepfish" \
  --fathom-shark "$DATA/yolo_fathom_shark" \
  --fathom-ray "$DATA/yolo_fathom_ray" \
  --turtle "$DATA/yolo" \
  --manatee "$DATA/yolo_manatee"

TRAIN_N=$(find "$DATA/yolo_marine_utility/images/train" -type f | wc -l)
VAL_N=$(find "$DATA/yolo_marine_utility/images/val" -type f | wc -l)
echo "Merged marine utility: train=$TRAIN_N val=$VAL_N"
test "$TRAIN_N" -ge 500

yolo detect train data="$DATA/yolo_marine_utility/dataset.yaml" model=yolo11m.pt \
  epochs=80 imgsz=1280 batch=64 patience=15 device=0 workers=8 \
  project="$DATA/checkpoints" name=marine_utility_m_v1
BEST_M="$DATA/checkpoints/marine_utility_m_v1/weights/best.pt"
yolo detect val data="$DATA/yolo_marine_utility/dataset.yaml" model="$BEST_M" split=test \
  imgsz=1280 batch=32 device=0 project="$DATA/eval" name=marine_utility_m_test

yolo detect train data="$DATA/yolo_marine_utility/dataset.yaml" model="$BEST_M" \
  epochs=50 imgsz=1280 batch=48 patience=12 device=0 workers=8 \
  project="$DATA/checkpoints" name=marine_utility_l_v1
BEST_L="$DATA/checkpoints/marine_utility_l_v1/weights/best.pt"
yolo detect val data="$DATA/yolo_marine_utility/dataset.yaml" model="$BEST_L" split=test \
  imgsz=1280 batch=24 device=0 project="$DATA/eval" name=marine_utility_l_test

python3 - <<'PY'
import json
from pathlib import Path
root = Path("/workspace/ceto-dex")
csv = root / "data/checkpoints/marine_utility_l_v1/results.csv"
lines = csv.read_text().strip().splitlines()
headers = lines[0].split(",")
vals = lines[-1].split(",")
metrics = dict(zip(headers, vals))
gate = {
    "gate": "phase4_marine_utility",
    "passed": float(metrics.get("metrics/mAP50(B)", 0)) >= 0.20,
    "confidence": float(metrics.get("metrics/mAP50(B)", 0)),
    "claim": "multi_class_marine_utility_whale_shark_stingray_reef_coral_turtle_manatee",
    "known_limits": [
        "mixed_label_quality_real_bbox_and_presence_proxy",
        "inat_whales_stingrays_coral_use_presence_proxy_boxes",
        "deepfish_and_fathomnet_real_bboxes",
        "not_field_certified",
    ],
    "metrics": metrics,
    "classes": ["whale","shark","stingray","reef_fish","coral_structure","sea_turtle","manatee"],
    "weights": str(root / "data/checkpoints/marine_utility_l_v1/weights/best.pt"),
}
out = root / "validation/local/phase4_marine_utility.json"
out.parent.mkdir(parents=True, exist_ok=True)
out.write_text(json.dumps(gate, indent=2) + "\n")
print(json.dumps(gate, indent=2))
PY
echo "=== MARINE UTILITY PUSH v2 DONE $(date -u +%Y-%m-%dT%H:%M:%SZ) ==="
