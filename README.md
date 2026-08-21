# Ceto-Dex

Video-native protected marine megafauna detection with **confidence-gated refusal** and **replay evidence**.

Primary scope:
- **Sea turtles** — underwater/nearshore video; species ID only where labels support it.
- **North Atlantic right whale** — aerial/surface/vessel imagery and video; individual ID is an advanced gate.
- **Manatee** — Phase 3 optional expansion.

This is a **reputation builder**, not a demo product. Public claims require gate JSON and named known limits.

## Laptop status (2026-08-21)

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

## Quick validation (Nemo)

```powershell
cd C:\Users\elxsh\Projects\Ceto-Dex
pip install -e ".[dev]"
pytest -q
python -m cetodex.laptop_gate
```

Offline recon (no network):

```powershell
python -m cetodex.laptop_gate --offline-recon
```

## Honest reputation line

> Ceto-Dex RunPod v1: sea-turtle specialist (proxy labels), manatee specialist (test mAP50 0.559), early-stop 7-class marine utility (val mAP50 0.597 @ epoch 1). No right whale. Not field certified. Weights local under `artifacts/runpod_*/`.

Do not upgrade this sentence until holdout gates and replay bundles exist on **real video clips**.

## Docs

- [DATA_SOURCES.md](docs/DATA_SOURCES.md)
- [CLAIMS.md](docs/CLAIMS.md)
- [VALIDATION.md](docs/VALIDATION.md)
- [KNOWN_LIMITS.md](docs/KNOWN_LIMITS.md)
- [RUNPOD.md](docs/RUNPOD.md) — runbook (v1 session complete)
- [RUNPOD_V1_MANIFEST.md](docs/RUNPOD_V1_MANIFEST.md) — local weight hashes
- [BUILDER_HANDOFF.md](docs/BUILDER_HANDOFF.md)

## Fratres stack

Ceto-Dex reopens the parked Natura/BioDex lane because it produces **field evidence** and strengthens the autonomy perception story (confidence, refusal, replay). See `The-Don/docs/FRATRES_PORTFOLIO_MAP.md`.
