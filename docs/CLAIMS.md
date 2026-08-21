# Ceto-Dex claims doctrine

## Allowed now (laptop scaffold)

- Manifest schema with provenance, license status, and split-safe asset IDs.
- COCO annotation round-trip without losing class or bbox.
- Greedy IOU tracking on synthetic tracks for pipeline validation.
- Refusal gates that block low-confidence, short, or unsupported labels.
- Replay bundle **schema** with SHA256 ledger on fixture encounters.

## Not allowed yet

- "Production marine life detector"
- "Field-certified conservation AI"
- Species ID accuracy claims without per-species holdout metrics
- Right whale individual ID claims without curated photo/video gate
- Cross-institution generalization claims without holdout eval

## Public sentence template

Use the gate output sentence from [README.md](../README.md). Append only what the latest gate JSON proves.

## Alignment with Fratres evidence contract

All gate JSON must include `known_limits`. Empty `known_limits` = overselling.

See [VALIDATION.md](VALIDATION.md) for gate names and pass criteria.
