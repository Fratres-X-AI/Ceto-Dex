# Ceto-Dex model card

**Project:** Ceto-Dex  
**Release:** v0.1.0-public-bench  
**Task:** Protected marine species detection and tracking in underwater video  
**Primary behavior:** Detect, track, and refuse low-confidence runs for human review.

---

## Intended use

Ceto-Dex is intended for conservation researchers, field-science teams, and
computer-vision developers who need a reproducible starting point for reviewing
underwater footage.

**Appropriate uses:**

- Triage underwater video for candidate protected-species encounters
- Compare detection confidence across clips
- Produce replayable run artifacts
- Route uncertain clips to human review

**Inappropriate uses:**

- Automated conservation enforcement
- Field-certified species counts or population estimates
- Regulatory decisions without qualified review
- Publishing sensitive animal locations without permission

---

## Models (RunPod v1, local weights — not distributed in repo)

| Artifact | Architecture | Val / test signal | Label honesty |
|----------|--------------|-------------------|---------------|
| `artifacts/runpod_v1/best.pt` | YOLO11s sea turtle | val mAP50 **0.995** | Whole-image proxy boxes — **inflated metrics** |
| `artifacts/runpod_manatee_v1/best.pt` | YOLO11s manatee | val mAP50 **0.603**, test **0.559** | Blue Spring line-labels → axis bbox proxies; single webcam site |
| `artifacts/runpod_marine_v1/best.pt` | YOLO11m marine utility (7-class) | val mAP50 **0.597** @ epoch 1 (stopped early) | Mixed: DeepFish real bboxes + iNat presence proxies + turtle/manatee |

Weight SHA256 hashes and gate JSON: [`docs/RUNPOD_V1_MANIFEST.md`](docs/RUNPOD_V1_MANIFEST.md).

**Not trained:** North Atlantic right whale detector (documented only).

---

## Training data summary

| Model | Source | Images | Annotation method |
|-------|--------|-------:|-------------------|
| Sea turtle v1 | `kim2429/SeaTurtles_Images` | 1,268 | Proxy whole-image boxes from species folders |
| Manatee v1 | Wang et al. / Save the Manatee Club Blue Spring counting set | 783 | Line-labels → axis bbox proxies |
| Marine utility | Merged iNat, DeepFish, turtle, manatee | 7,876 / 29,792 boxes | Mixed real bboxes + presence proxies |

See [DATA_CARD.md](DATA_CARD.md) and [docs/DATA_SOURCES.md](docs/DATA_SOURCES.md).

---

## Refusal behavior

The refusal wrapper (`cetodex.refusal`) refuses when:

- Confidence is below threshold (default 0.55)
- Candidate species is unsupported
- Track has too few frames (default < 3)
- Bounding box area is too small (partial body only)
- Frame labels conflict within a track
- Modality is unsupported

Refusal reasons are enumerated in `cetodex.models.REFUSE_REASONS`. Refusal
means the output requires human review. It does not mean no animal is present.

---

## Evaluation posture

- **Laptop gates:** manifest, COCO contract, synthetic track refusal — CI green
- **RunPod v1:** proxy-label detector baselines with honest known_limits
- **Not yet:** video-native tracking on real ROV/aerial clips; refusal/replay on
  field encounter clips; per-institution holdout matrix

Bench and proxy-label results must be labeled as such. Do not extrapolate to
field deployment.

---

## Known limitations

- Underwater turbidity, glare, occlusion, low resolution, and camera motion
  degrade detection quality
- Proxy labels are not equivalent to field truth
- Sea turtle val mAP50 is inflated by whole-image proxy boxes
- Marine utility training stopped after ~1 epoch — not converged
- FathomNet shark/ray boxes not merged (export folder layout mismatch)
- The system assists review but does not replace domain experts

Full list: [docs/KNOWN_LIMITS.md](docs/KNOWN_LIMITS.md).

---

## Ethical and conservation notes

Protected-species tools should minimize harm. Do not publish exact locations,
times, or repeated movement patterns if doing so could increase disturbance,
poaching, harassment, or unauthorized tourism pressure.

---

## Citation

```bibtex
@software{ceto_dex_2026,
  title = {Ceto-Dex: Marine video detection with refusal-first review},
  author = {Bean, Kyle and Fratres X AI},
  year = {2026},
  url = {https://github.com/Fratres-X-AI/Ceto-Dex},
  version = {0.1.0-public-bench}
}
```

Also see [CITATION.cff](CITATION.cff).
