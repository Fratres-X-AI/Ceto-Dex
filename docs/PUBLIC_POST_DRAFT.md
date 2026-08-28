# Ceto-Dex public announcement draft

**Use after:** CI green, repo public, tag `v0.1.0-public-bench` published.

---

## LinkedIn (short)

We open-sourced **Ceto-Dex** — video-native protected marine species detection
with refusal-first review.

Most CV demos stop at a bounding box. Conservation work needs the opposite:
**detect, track, and refuse when the evidence is not good enough.**

What it does:
- Triage underwater video for candidate encounters
- Gate low-confidence outputs for human review
- Leave replay evidence (input hash, config, known limits)

What it does **not** do:
- Field certification
- Conservation authority
- Replacement for biologist review

RunPod v1 baselines: sea turtle + manatee (proxy-label honest). No right whale
yet. Bench/research maturity only.

Repo: https://github.com/Fratres-X-AI/Ceto-Dex  
License: Apache-2.0

By Fratres X AI.

---

## GitHub release notes (paste into release)

### v0.1.0-public-bench

First public-bench release.

**Includes:** refusal gates, replay evidence schema, laptop validation matrix,
RunPod v1 detector documentation (weights local).

**Does not include:** trained weights, bulk footage, field certification.

See `docs/KNOWN_LIMITS.md` before citing metrics.

---

## Do not say

- "Production marine life detector"
- "Field-certified conservation AI"
- "Proved species presence"
- Population or habitat claims without separate validation
