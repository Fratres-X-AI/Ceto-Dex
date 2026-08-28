# Release notes — v0.1.0-public-bench

**Date:** 2026-08-28  
**Tag:** `v0.1.0-public-bench`  
**Visibility:** private until release gate green; then public

---

## Summary

First public-bench release of Ceto-Dex: marine video detection scaffolding with
refusal-first review, replay evidence schema, laptop validation gates, and
honest RunPod v1 detector documentation.

---

## Included

- Laptop gate pipeline (manifest, COCO contract, synthetic refusal, aggregate)
- Refusal taxonomy and `cetodex.refusal` evaluation
- Replay bundle schema with SHA256 ledger
- RunPod v1 gate JSON and weight hashes (weights local, not in repo)
- Public documentation: README, MODEL_CARD, DATA_CARD, HUMAN_REVIEW_PROTOCOL,
  SECURITY, CITATION.cff
- CI: pytest + `cetodex.laptop_gate --offline-recon`

---

## Not included

- Trained model weights (build locally; see RUNPOD.md)
- Bulk training footage
- North Atlantic right whale detector
- Video-native tracking on real field clips
- Field certification or conservation authority claims

---

## Honest claim for announcement

> Ceto-Dex detects and tracks protected marine species in difficult underwater
> video and refuses low-confidence runs for human review. RunPod v1 baselines
> exist for sea turtle and manatee with proxy-label honesty. Not field-certified.
> Not a conservation authority.

---

## Post-release checklist

- [ ] CI green on `master`
- [ ] Fresh clone + laptop gate passes
- [ ] Flip repo visibility to public
- [ ] Create GitHub release from tag `v0.1.0-public-bench`
- [ ] LinkedIn / community post with honest maturity line

See [PUBLIC_POST_DRAFT.md](PUBLIC_POST_DRAFT.md) for announcement copy.
