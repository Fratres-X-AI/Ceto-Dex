# Ceto-Dex known limits

**As of RunPod v1 session (2026-08-21):**

## What exists (local, not field certified)

| Artifact | Model | Val / test signal | Label honesty |
|----------|-------|-------------------|---------------|
| `artifacts/runpod_v1/best.pt` | YOLO11s sea turtle | val mAP50 **0.995** | Whole-image proxy boxes from species folders — **inflated metrics** |
| `artifacts/runpod_manatee_v1/best.pt` | YOLO11s manatee | val mAP50 **0.603**, test **0.559** | Blue Spring line-labels → axis bbox proxies; single webcam site |
| `artifacts/runpod_marine_v1/best.pt` | YOLO11m marine utility (7-class) | val mAP50 **0.597** @ epoch 1 (stopped early) | Mixed: DeepFish real bboxes + iNat presence proxies + turtle/manatee |

Weights stay **gitignored**; hashes and gates in [`RUNPOD_V1_MANIFEST.md`](RUNPOD_V1_MANIFEST.md) and `validation/local/phase4*.json`.

## What does not exist

- North Atlantic right whale detector (documented only; no curated train set).
- FathomNet shark/ray boxes in marine merge (export folder layout mismatch — 0 images merged).
- Video-native tracking on real ROV/aerial clips (ByteTrack/BoT-SORT not run on field video).
- Refusal/replay bundles on real encounter clips.
- Field certification or conservation decision authority.

## Dataset caveats

- **Sea turtle v1:** `kim2429/SeaTurtles_Images` — 1,268 images, proxy labels, not real instance boxes.
- **Manatee v1:** Wang et al. / Save the Manatee Club Blue Spring counting set — 783 images, 11,741 instances.
- **Marine utility:** 7,876 images / 29,792 boxes merged (iNat, DeepFish, turtle, manatee). iNat whale/stingray/coral = **presence proxy** only.
- **FathomNet:** API counts best-effort; not used for final turtle train after bulk-fetch failures.

## RunPod session limits

- Marine utility training stopped after ~1 epoch (+ OOM probe b96/b88 failed) — not a converged multi-class model.
- No bulk video on disk; manifest fixtures only for laptop gates.
- Tracking validated on synthetic IOU tracks, not real footage.

## Honest reputation line

> Ceto-Dex RunPod v1: sea-turtle specialist (proxy labels, inflated val mAP50), manatee specialist (Blue Spring, test mAP50 0.559), and an early-stop 7-class marine utility detector (val mAP50 0.597 @ epoch 1). No right whale. Not field certified. Not a conservation decision system.

Upgrade this file only when a gate JSON proves more.
