#!/usr/bin/env bash
set -euo pipefail
ROOT=/workspace/ceto-dex
DATA=$ROOT/data
LOG=$ROOT/run_manatee.log
exec > >(tee -a "$LOG") 2>&1
echo "=== Ceto-Dex MANATEE train START $(date -u +%Y-%m-%dT%H:%M:%SZ) ==="
cd "$ROOT"
python -m pip install -q --break-system-packages pillow ultralytics
python scripts/build_manatee_counting_yolo.py \
  --zip-path "$DATA/raw/manatee_gdrive/dataset.zip" \
  --extract-root "$DATA/raw/manatee_dataset" \
  --out "$DATA/yolo_manatee"
TRAIN_N=$(find "$DATA/yolo_manatee/images/train" -type f | wc -l)
VAL_N=$(find "$DATA/yolo_manatee/images/val" -type f | wc -l)
echo "Manatee dataset train=$TRAIN_N val=$VAL_N"
test "$TRAIN_N" -ge 50
yolo detect train data="$DATA/yolo_manatee/dataset.yaml" model=yolo11s.pt epochs=40 imgsz=640 batch=32 \
  project="$DATA/checkpoints" name=manatee_v1 patience=10 device=0
BEST="$DATA/checkpoints/manatee_v1/weights/best.pt"
test -f "$BEST"
yolo detect val data="$DATA/yolo_manatee/dataset.yaml" model="$BEST" split=test imgsz=640 batch=32 device=0 \
  project="$DATA/eval" name=manatee_holdout_val
python -m cetodex.runpod_finish \
  --root "$ROOT" \
  --weights "$BEST" \
  --yolo-data "$DATA/yolo_manatee/dataset.yaml" \
  --eval-dir "$DATA/eval/manatee_holdout_val"
mv "$ROOT/validation/local/phase4_detector_baseline.json" "$ROOT/validation/local/phase4_manatee_baseline.json"
mv "$ROOT/validation/local/ceto_dex_runpod_one_pass.json" "$ROOT/validation/local/ceto_dex_manatee_one_pass.json"
echo "=== Ceto-Dex MANATEE train DONE $(date -u +%Y-%m-%dT%H:%M:%SZ) ==="
