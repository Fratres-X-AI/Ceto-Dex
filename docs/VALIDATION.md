# Ceto-Dex validation matrix

## Laptop gates (this repo)

| Gate | Module | Pass criteria |
|------|--------|---------------|
| `phase0_repo_contract` | `cetodex.phase0_gate` | Required docs + modules present |
| `phase1_data_recon` | `cetodex.phase1_recon` | Source catalog + license fields documented |
| `phase2_manifest_integrity` | `cetodex.phase2_manifest_gate` | Fixture manifest validates; no duplicate IDs/hashes |
| `phase3_annotation_contract` | `cetodex.phase3_contract_gate` | COCO round-trip preserves detections |
| `phase7_refusal_review` | `cetodex.phase7_refusal_gate` | Synthetic track → encounter; refusal on short track |
| `ceto_dex_laptop_aggregate` | `cetodex.laptop_gate` | All subgates pass |

Run aggregate:

```powershell
python -m cetodex.laptop_gate
```

Outputs land in `validation/local/`.

## RunPod gates (v1 complete — weights local)

| Gate | Requires |
|------|----------|
| `phase4_detector_baseline` | Clip extract + YOLO/RT-DETR train + holdout mAP |
| `phase5_video_encounter` | Real video tracks + FP/hour on negatives |
| `phase6_species_identity` | Per-species label counts + confusion matrix |
| `phase8_train_run_manifest` | Pod record + checkpoint hash + pulled metrics |
| `ceto_dex_full_video_gate` | Full matrix on held-out institutions |

## Split discipline (all phases)

1. Split by `video_id` / survey event — never by frame.
2. Hold out at least one institution where possible.
3. Document negative-video false alarm rate separately from mAP.

## Refusal taxonomy

See `cetodex.models.REFUSE_REASONS`. Every refused encounter must carry a reason from that set.
