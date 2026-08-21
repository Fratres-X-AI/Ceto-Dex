# Ceto-Dex RunPod runbook (deferred)

**Do not start this on Nemo.** This document exists so the separate RunPod run has a clear entry point.

## Prerequisites (laptop must be green first)

```powershell
python -m cetodex.laptop_gate
pytest -q
```

All subgates in `validation/local/ceto_dex_laptop_aggregate.json` must pass.

## Vault layout (RunPod volume)

```
/data/ceto-dex/
  raw/fathomnet/
  raw/noaa-right-whale/
  manifests/
  clips/
  frames/
  annotations/
  splits/
  checkpoints/
  eval/
```

## Separate-run stages

1. **Clip extract** — FathomNet video-linked annotations → MP4 snippets + manifest rows.
2. **Split builder** — train/val/test/holdout by `video_id` + institution.
3. **Detector train** — YOLO11 or RT-DETR; hard negatives included.
4. **Tracker calibrate** — ByteTrack/BoT-SORT on detector outputs.
5. **Species head** — only classes with sufficient verified labels.
6. **Eval + replay** — pull metrics JSON and replay bundle to laptop; terminate pod.

## Babysit rule

Money on the meter = pulse util, log tail, pull artifacts, say terminate.

## Nemo after RunPod

- Light inference smoke on pulled weights (cap batch size).
- Update `docs/KNOWN_LIMITS.md` and gate JSON only with honest metrics.
