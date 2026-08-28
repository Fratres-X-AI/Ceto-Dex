<h1 align="center">Ceto-Dex</h1>
<p align="center"><strong>Marine video detection with refusal-first review</strong></p>
<p align="center">
  Detect and track protected marine species in underwater video.<br/>
  Refuse low-confidence runs. Leave replay evidence for human review.
</p>

<p align="center">
  <a href="https://github.com/Fratres-X-AI/Ceto-Dex/actions/workflows/ci.yml"><img src="https://github.com/Fratres-X-AI/Ceto-Dex/actions/workflows/ci.yml/badge.svg" alt="CI" /></a>
  <a href="LICENSE"><img src="https://img.shields.io/badge/license-Apache--2.0-blue.svg" alt="License" /></a>
  <a href="https://www.python.org/downloads/"><img src="https://img.shields.io/badge/python-3.10%2B-blue.svg" alt="Python" /></a>
  <img src="https://img.shields.io/badge/maturity-bench%20%2F%20research-orange.svg" alt="Maturity" />
</p>

---

## Why Ceto-Dex exists

Most computer-vision demos stop at a bounding box. Conservation work needs the
part that comes after:

> **Detect, track, and refuse when the evidence is not good enough.**

Ceto-Dex is an open research tool for video-native protected marine megafauna
detection with **confidence-gated refusal** and **replay evidence**. It helps
reviewers triage underwater footage without turning uncertain detections into
confident conservation claims.

Ceto-Dex is **not** a demo product, **not** field-certified, and **not** a
conservation authority.

---

## What it does

| Capability | Detail |
|------------|--------|
| **Manifest + provenance** | Split-safe asset IDs, license fields, institution discipline |
| **Annotation contract** | COCO round-trip without losing class or bbox |
| **Tracking scaffold** | Greedy IOU tracks for pipeline validation |
| **Refusal gates** | Block low-confidence, short, or unsupported labels |
| **Replay bundle schema** | SHA256 ledger on fixture encounters |
| **RunPod v1 detectors** | Sea turtle, manatee, early-stop marine utility (weights local, not in repo) |

Primary species scope:

- **Sea turtles** — underwater/nearshore video
- **North Atlantic right whale** — documented only; no curated train set yet
- **Manatee** — Phase 3 optional expansion (v1 baseline exists)

---

## What it does not do

- Field-certified species detection or population surveys
- Autonomous conservation enforcement or regulatory decisions
- Replacement for marine biologist review
- Right whale individual ID without a curated photo/video gate
- Proof of habitat use, health status, or site compliance from a box alone

See [docs/CLAIMS.md](docs/CLAIMS.md) and [docs/KNOWN_LIMITS.md](docs/KNOWN_LIMITS.md).

---

## 60-second validation

```powershell
git clone https://github.com/Fratres-X-AI/Ceto-Dex.git
cd Ceto-Dex
pip install -e ".[dev]"
pytest -q
python -m cetodex.laptop_gate --offline-recon
```

Offline recon (no network):

```powershell
python -m cetodex.laptop_gate --offline-recon
```

Gate JSON lands in `validation/local/`. Every gate includes `known_limits`.

---

## Example refusal output

```json
{
  "project": "Ceto-Dex",
  "decision": "refuse",
  "refuse_reason": "low_confidence",
  "human_review_required": true,
  "known_limits": [
    "bench/proxy-label validation only",
    "not field-certified",
    "not a conservation authority"
  ]
}
```

Refusal does **not** mean no animal is present. It means the software is not
confident enough to make a useful automated claim.

---

## Current maturity (RunPod v1, 2026-08-21)

| Gate | Status |
|------|--------|
| Phase 0 repo contract | Laptop |
| Phase 1 data recon | Laptop (live FathomNet API best-effort) |
| Phase 2 manifest integrity | Laptop (fixture) |
| Phase 3 annotation contract | Laptop (COCO round-trip) |
| Phase 7 refusal/review | Laptop (synthetic tracks) |
| Phase 4 detector (RunPod v1) | **RunPod** — turtle, manatee, marine utility early-stop |
| Phase 5–7 video/refusal on real clips | **Deferred** |
| Phase 8–11 full validation/release | **Partial** — runpod gates exist; no real-video replay |

**Honest reputation line:**

> Ceto-Dex RunPod v1: sea-turtle specialist (proxy labels), manatee specialist
> (test mAP50 0.559), early-stop 7-class marine utility (val mAP50 0.597 @
> epoch 1). No right whale. Not field certified. Weights local under
> `artifacts/runpod_*/`.

Do not upgrade this sentence until holdout gates and replay bundles exist on
**real video clips**.

---

## Human-review policy

Ceto-Dex outputs are decision-support artifacts. A human reviewer should confirm
species, context, and confidence before any conservation, reporting, or field
action is taken.

See [docs/HUMAN_REVIEW_PROTOCOL.md](docs/HUMAN_REVIEW_PROTOCOL.md).

---

## Responsible use

Use Ceto-Dex to support conservation review, dataset triage, and reproducible
video analysis. Do not use it to harass wildlife, expose sensitive species
locations, or automate regulatory decisions without qualified human review.

---

## Docs

| Doc | Purpose |
|-----|---------|
| [MODEL_CARD.md](MODEL_CARD.md) | Model limits, training data, refusal behavior |
| [DATA_CARD.md](DATA_CARD.md) | Dataset rights, fixtures, sensitive-data handling |
| [docs/HUMAN_REVIEW_PROTOCOL.md](docs/HUMAN_REVIEW_PROTOCOL.md) | Review states, checklist, public language |
| [docs/DATA_SOURCES.md](docs/DATA_SOURCES.md) | Source catalog and license posture |
| [docs/CLAIMS.md](docs/CLAIMS.md) | Allowed vs not-allowed public claims |
| [docs/VALIDATION.md](docs/VALIDATION.md) | Gate matrix and pass criteria |
| [docs/KNOWN_LIMITS.md](docs/KNOWN_LIMITS.md) | What v1 does and does not prove |
| [docs/RUNPOD.md](docs/RUNPOD.md) | GPU training runbook (v1 session complete) |
| [docs/RUNPOD_V1_MANIFEST.md](docs/RUNPOD_V1_MANIFEST.md) | Local weight hashes |
| [SECURITY.md](SECURITY.md) | Vulnerability reporting |

---

## Fratres stack

Ceto-Dex reopens the parked Natura/BioDex conservation lane because it produces
**field evidence** and strengthens the autonomy perception story (confidence,
refusal, replay). It shares the Fratres doctrine: refuse over hallucinate, gates
over claims, audit by default.

By [Fratres X AI](https://www.fratres-x.com).

---

## License

Apache-2.0. See [LICENSE](LICENSE).

## Citation

See [CITATION.cff](CITATION.cff).
