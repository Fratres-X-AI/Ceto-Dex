#!/usr/bin/env bash
# Resume train from existing SeaTurtles clone — skip broken FathomNet bulk fetch
set -euo pipefail
ROOT=/workspace/ceto-dex
DATA=$ROOT/data
LOG=$ROOT/run_one_pass.log
exec >> "$LOG" 2>&1
echo "=== RESUME TRAIN $(date -u +%Y-%m-%dT%H:%M:%SZ) ==="
cd "$ROOT"
python -m pip install -q --break-system-packages -e ".[dev]" ultralytics pillow
python scripts/build_sea_turtles_folder_yolo.py \
  --sea-turtles-root "$DATA/raw/SeaTurtles_Images" \
  --out "$DATA/yolo"
TRAIN_N=$(find "$DATA/yolo/images/train" -type f 2>/dev/null | wc -l)
VAL_N=$(find "$DATA/yolo/images/val" -type f 2>/dev/null | wc -l)
echo "Dataset train=$TRAIN_N val=$VAL_N"
test "$TRAIN_N" -ge 50
test "$VAL_N" -ge 10
yolo detect train data="$DATA/yolo/dataset.yaml" model=yolo11s.pt epochs=50 imgsz=640 batch=32 \
  project="$DATA/checkpoints" name=sea_turtle_v1 patience=12 device=0
BEST="$DATA/checkpoints/sea_turtle_v1/weights/best.pt"
test -f "$BEST"
yolo detect val data="$DATA/yolo/dataset.yaml" model="$BEST" split=test imgsz=640 batch=32 device=0 \
  project="$DATA/eval" name=holdout_val
python -m cetodex.runpod_finish --root "$ROOT" --weights "$BEST" \
  --yolo-data "$DATA/yolo/dataset.yaml" --eval-dir "$DATA/eval/holdout_val"
echo "=== RESUME DONE $(date -u +%Y-%m-%dT%H:%M:%SZ) ==="
