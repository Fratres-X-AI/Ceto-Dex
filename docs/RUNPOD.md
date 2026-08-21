# Ceto-Dex RunPod runbook

**Do not train on Nemo.** Use a GPU pod + data vault; pull weights and gate JSON back; terminate.

## Prerequisites (laptop)

```powershell
python -m cetodex.laptop_gate
pytest -q
```

## Vault layout (RunPod volume)

```
/workspace/ceto-dex/data/
  raw/                    # SeaTurtles_Images, manatee gdrive, deepfish.zip, etc.
  yolo/                   # turtle YOLO layout
  yolo_manatee/
  yolo_marine_utility/    # merged 7-class
  checkpoints/
  eval/
```

## v1 session completed (2026-08-21)

| Script | Output |
|--------|--------|
| `runpod_resume_train.sh` | `sea_turtle_v1` — YOLO11s, proxy labels |
| `runpod_manatee_train.sh` | `manatee_v1` — Blue Spring counting set |
| `runpod_marine_utility_push.sh` | merged dataset + YOLO11m/l |
| `runpod_oom_saturate.sh` | YOLO11x batch ramp (optional) |

Artifact manifest: [`RUNPOD_V1_MANIFEST.md`](RUNPOD_V1_MANIFEST.md).

## Babysit rule

Money on the meter = pulse util, log tail, pull artifacts, say terminate.

## After RunPod (Nemo)

- Weights under `artifacts/runpod_*/best.pt` (gitignored).
- Update `docs/KNOWN_LIMITS.md` only with honest gate metrics.
- Light inference smoke only — cap batch size.
