#!/usr/bin/env bash
# Ceto-Dex one-pass — data build + YOLO train + eval + gates
set -euo pipefail

ROOT="${CETO_DEX_ROOT:-/workspace/ceto-dex}"
DATA="${ROOT}/data"
LOG="${ROOT}/run_one_pass.log"
MAX_EPOCHS="${CETO_MAX_EPOCHS:-50}"
MODEL="${CETO_MODEL:-yolo11s.pt}"
IMGSZ="${CETO_IMGSZ:-640}"
BATCH="${CETO_BATCH:-32}"

exec > >(tee -a "${LOG}") 2>&1
echo "=== Ceto-Dex one-pass START $(date -Is) ==="

cd "${ROOT}"
export PYTHONUNBUFFERED=1

python -m pip install -q --break-system-packages -e ".[dev]" ultralytics fathomnet opencv-python-headless pyyaml

mkdir -p "${DATA}"/{raw,coco,yolo,checkpoints,eval,artifacts}

echo "--- Data: clone SeaTurtles_Images if missing ---"
if [ ! -d "${DATA}/raw/SeaTurtles_Images/.git" ]; then
  git clone --depth 1 https://github.com/kim2429/SeaTurtles_Images.git "${DATA}/raw/SeaTurtles_Images"
fi

echo "--- Data: FathomNet turtle COCO (small) ---"
fathomnet-generate --output "${DATA}/raw/turtle" --concepts "Cheloniidae" --taxa fathomnet --format coco -v --img-download "${DATA}/raw/turtle/images"

echo "--- Data: FathomNet negatives (single concept, bounded) ---"
fathomnet-generate --output "${DATA}/raw/negatives" --concepts "Bathochordaeus" --taxa fathomnet --format coco -v --img-download "${DATA}/raw/negatives/images"

echo "--- Data: SeaTurtles labelme -> YOLO ---"
python scripts/build_sea_turtles_yolo.py \
  --sea-turtles-root "${DATA}/raw/SeaTurtles_Images" \
  --out "${DATA}/yolo_sea_turtles"

echo "--- Data: merge FathomNet COCO into YOLO layout ---"
python scripts/coco_to_yolo.py \
  --turtle-coco "${DATA}/raw/turtle" \
  --negative-coco "${DATA}/raw/negatives" \
  --out "${DATA}/yolo_fathomnet" \
  --val-fraction 0.15 \
  --holdout-fraction 0.10

echo "--- Data: combine train/val/test dirs ---"
COMB="${DATA}/yolo"
mkdir -p "${COMB}/images"/{train,val,test} "${COMB}/labels"/{train,val,test}
for split in train val test; do
  for sub in yolo_sea_turtles yolo_fathomnet; do
    if [ -d "${DATA}/${sub}/images/${split}" ]; then
      cp -n "${DATA}/${sub}/images/${split}/"* "${COMB}/images/${split}/" 2>/dev/null || true
      cp -n "${DATA}/${sub}/labels/${split}/"* "${COMB}/labels/${split}/" 2>/dev/null || true
    fi
  done
done
cat > "${COMB}/dataset.yaml" <<YAML
path: ${COMB}
train: images/train
val: images/val
test: images/test
names:
  0: sea_turtle
  1: hard_negative
YAML

TRAIN_N=$(find "${COMB}/images/train" -type f 2>/dev/null | wc -l)
VAL_N=$(find "${COMB}/images/val" -type f 2>/dev/null | wc -l)
echo "Combined dataset: train=${TRAIN_N} val=${VAL_N}"
if [ "${TRAIN_N}" -lt 10 ]; then
  echo "ERROR: insufficient training images"
  exit 1
fi

echo "--- YOLO train ---"
yolo detect train \
  data="${COMB}/dataset.yaml" \
  model="${MODEL}" \
  epochs="${MAX_EPOCHS}" \
  imgsz="${IMGSZ}" \
  batch="${BATCH}" \
  project="${DATA}/checkpoints" \
  name="sea_turtle_v1" \
  patience=12 \
  save=True \
  plots=True \
  device=0

BEST="${DATA}/checkpoints/sea_turtle_v1/weights/best.pt"
test -f "${BEST}"

echo "--- YOLO val (test split) ---"
yolo detect val \
  data="${COMB}/dataset.yaml" \
  model="${BEST}" \
  split=test \
  imgsz="${IMGSZ}" \
  batch="${BATCH}" \
  device=0 \
  project="${DATA}/eval" \
  name="holdout_val"

echo "--- Gates + replay ---"
python -m cetodex.runpod_finish \
  --root "${ROOT}" \
  --weights "${BEST}" \
  --yolo-data "${COMB}/dataset.yaml" \
  --eval-dir "${DATA}/eval/holdout_val"

echo "=== Ceto-Dex one-pass DONE $(date -Is) ==="
