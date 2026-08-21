# RunPod v1 artifact manifest (local)

**Session:** 2026-08-21 · Pod terminated after pull  
**Weights are gitignored** — keep these paths on Nemo / vault backup.

## Checkpoints

| Path | SHA-256 | Size | Gate |
|------|---------|------|------|
| `artifacts/runpod_v1/best.pt` | `bb80238e9724bb2ce2957d76203ce772c195822c451530b84a12da3411dafeb5` | ~18 MB | `validation/local/phase4_detector_baseline.json` |
| `artifacts/runpod_manatee_v1/best.pt` | `463b1653144f08abe2b3490657f01bac36cdc9c15d9a4ecd21bb4253c812a2dd` | ~18 MB | `validation/local/phase4_manatee_baseline.json` |
| `artifacts/runpod_marine_v1/best.pt` | `af336f471ca0d6dcfdb35be5ed35e89b26ad48f6878452f68ffcfcd274bfc0436` | ~154 MB | `validation/local/phase4_marine_utility.json` |

## Metadata committed in repo

- `artifacts/runpod_v1/*.json` — model card, ledger, manifest excerpt  
- `artifacts/runpod_manatee_v1/build_stats.json`  
- `artifacts/runpod_marine_v1/build_stats.json`, `results.csv`  
- All `validation/local/phase4*.json` and runpod one-pass gates  

## Scripts (repo)

See `scripts/runpod_*.sh`, `scripts/build_*_yolo.py`, `src/cetodex/runpod_finish.py`.

## Re-run entry

```bash
# On pod after git pull + data vault attached
bash scripts/runpod_resume_train.sh          # turtle only
bash scripts/runpod_manatee_train.sh         # manatee only
bash scripts/runpod_marine_utility_push.sh   # 7-class merge + m/l train
bash scripts/runpod_oom_saturate.sh          # YOLO11x OOM ceiling (after merge)
```
