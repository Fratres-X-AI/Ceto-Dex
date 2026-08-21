#!/usr/bin/env bash
# Saturate RTX PRO 6000 — ramp batch/res until OOM, then long train at ceiling.
set -euo pipefail
ROOT=/workspace/ceto-dex
DATA=$ROOT/data
LOG=$ROOT/run_oom_saturate.log
exec > >(tee -a "$LOG") 2>&1

echo "=== OOM SATURATE START $(date -u +%Y-%m-%dT%H:%M:%SZ) ==="
cd "$ROOT"

while [ ! -f "$DATA/yolo_marine_utility/dataset.yaml" ]; do
  echo "waiting for merged dataset..."
  sleep 45
done

echo "dataset ready; waiting for any in-flight yolo train to finish..."
while pgrep -f "yolo detect train" >/dev/null 2>&1; do
  nvidia-smi --query-gpu=utilization.gpu,memory.used --format=csv,noheader || true
  sleep 90
done

attempt_train() {
  local model=$1 imgsz=$2 batch=$3 name=$4 epochs=$5
  echo "--- ATTEMPT $name | $model imgsz=$imgsz batch=$batch epochs=$epochs ---"
  if yolo detect train \
    data="$DATA/yolo_marine_utility/dataset.yaml" \
    model="$model" \
    epochs="$epochs" \
    imgsz="$imgsz" \
    batch="$batch" \
    device=0 \
    patience=25 \
    workers=8 \
    project="$DATA/checkpoints" \
    name="$name"; then
    echo "SUCCESS $name"
    return 0
  fi
  echo "FAIL $name (OOM or error)"
  return 1
}

OOM_CEILING=""
OOM_BATCH=""
OOM_IMGSZ=""

for b in 96 88 80 72 64 56 48; do
  if attempt_train yolo11x.pt 1280 "$b" "oom_x1280_b${b}" 30; then
    OOM_CEILING="$DATA/checkpoints/oom_x1280_b${b}/weights/best.pt"
    OOM_BATCH=$b
    OOM_IMGSZ=1280
    break
  fi
  sleep 5
done

for b in 56 48 40 32 24; do
  if attempt_train yolo11x.pt 1536 "$b" "oom_x1536_b${b}" 25; then
    OOM_CEILING="$DATA/checkpoints/oom_x1536_b${b}/weights/best.pt"
    OOM_BATCH=$b
    OOM_IMGSZ=1536
    break
  fi
  sleep 5
done

for b in 32 28 24 20 16 12; do
  if attempt_train yolo11x.pt 1920 "$b" "oom_x1920_b${b}" 20; then
    OOM_CEILING="$DATA/checkpoints/oom_x1920_b${b}/weights/best.pt"
    OOM_BATCH=$b
    OOM_IMGSZ=1920
    break
  fi
  sleep 5
done

if [ -z "$OOM_CEILING" ] || [ ! -f "$OOM_CEILING" ]; then
  echo "FATAL: no successful OOM probe run"
  exit 1
fi

echo "CEILING: imgsz=$OOM_IMGSZ batch=$OOM_BATCH weights=$OOM_CEILING"

# Long train at ceiling
yolo detect train \
  data="$DATA/yolo_marine_utility/dataset.yaml" \
  model="$OOM_CEILING" \
  epochs=120 \
  imgsz="$OOM_IMGSZ" \
  batch="$OOM_BATCH" \
  device=0 \
  patience=30 \
  workers=8 \
  project="$DATA/checkpoints" \
  name=marine_utility_x_ceiling

BEST="$DATA/checkpoints/marine_utility_x_ceiling/weights/best.pt"
yolo detect val data="$DATA/yolo_marine_utility/dataset.yaml" model="$BEST" split=test \
  imgsz="$OOM_IMGSZ" batch=$((OOM_BATCH / 2 + 1)) device=0 \
  project="$DATA/eval" name=marine_utility_x_ceiling_test

# Specialist heads — still useful, smaller batches ok sequentially
for spec in "whale:0" "shark:1" "stingray:2" "reef_fish:3"; do
  cls="${spec%%:*}"
  yolo detect train \
    data="$DATA/yolo_marine_utility/dataset.yaml" \
    model="$BEST" \
    epochs=40 \
    imgsz="$OOM_IMGSZ" \
    batch="$OOM_BATCH" \
    classes="${spec#*:}" \
    device=0 \
    patience=15 \
    project="$DATA/checkpoints" \
    name="specialist_${cls}_v1" || true
done

python3 - <<'PY'
import json
from pathlib import Path
root = Path("/workspace/ceto-dex")
csv = root / "data/checkpoints/marine_utility_x_ceiling/results.csv"
lines = csv.read_text().strip().splitlines()
headers = lines[0].split(",")
vals = lines[-1].split(",")
metrics = dict(zip(headers, vals))
gate = {
    "gate": "phase4_marine_utility_oom_ceiling",
    "passed": float(metrics.get("metrics/mAP50(B)", 0)) >= 0.15,
    "confidence": float(metrics.get("metrics/mAP50(B)", 0)),
    "claim": "marine_utility_yolo11x_oom_ceiling_train",
    "known_limits": [
        "mixed_label_quality_real_bbox_and_presence_proxy",
        "oom_saturated_batch_not_latency_optimized",
        "not_field_certified",
    ],
    "metrics": metrics,
    "classes": ["whale","shark","stingray","reef_fish","coral_structure","sea_turtle","manatee"],
    "weights": str(root / "data/checkpoints/marine_utility_x_ceiling/weights/best.pt"),
}
(root / "validation/local/phase4_marine_utility_oom.json").write_text(json.dumps(gate, indent=2) + "\n")
print(json.dumps(gate, indent=2))
PY

echo "=== OOM SATURATE DONE $(date -u +%Y-%m-%dT%H:%M:%SZ) ==="
