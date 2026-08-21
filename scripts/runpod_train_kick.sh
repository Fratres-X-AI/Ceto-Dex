#!/usr/bin/env bash
set -euo pipefail
DATA=/workspace/ceto-dex/data
ROOT=/workspace/ceto-dex
LOG=$ROOT/run_train_kick.log
exec >> "$LOG" 2>&1
echo "=== TRAIN KICK $(date -u +%Y-%m-%dT%H:%M:%SZ) ==="
test -f "$DATA/yolo_marine_utility/dataset.yaml"
yolo detect train data="$DATA/yolo_marine_utility/dataset.yaml" model=yolo11m.pt \
  epochs=80 imgsz=1280 batch=64 patience=15 device=0 workers=8 \
  project="$DATA/checkpoints" name=marine_utility_m_v1
BEST_M="$DATA/checkpoints/marine_utility_m_v1/weights/best.pt"
yolo detect train data="$DATA/yolo_marine_utility/dataset.yaml" model="$BEST_M" \
  epochs=50 imgsz=1280 batch=48 patience=12 device=0 workers=8 \
  project="$DATA/checkpoints" name=marine_utility_l_v1
echo "=== TRAIN KICK DONE $(date -u +%Y-%m-%dT%H:%M:%SZ) ==="
