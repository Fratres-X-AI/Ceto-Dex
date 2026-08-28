# Ceto-Dex human-review protocol

## Purpose

Ceto-Dex is a decision-support tool. Its output should help a reviewer find,
triage, and reproduce candidate protected-species encounters in underwater
video. It should not replace expert judgment.

---

## Review states

| State | Meaning | Required action |
|-------|---------|-----------------|
| `candidate` | The system found a possible species encounter. | Human reviewer confirms or rejects. |
| `track_candidate` | The system linked detections across frames. | Human reviewer checks continuity and identity. |
| `refuse` | The system does not have enough evidence. | Human reviewer inspects if the clip matters. |
| `unsupported` | The class, footage type, or configuration is outside scope. | Do not use output as species evidence. |

---

## Refusal triggers

Ceto-Dex refuses when (`cetodex.models.REFUSE_REASONS`):

- `low_confidence` — below configured threshold (default 0.55)
- `too_few_frames` — track shorter than minimum (default 3)
- `partial_body_only` — bounding box area too small
- `high_blur_or_turbidity` — input quality too degraded
- `source_out_of_distribution` — footage unlike training distribution
- `species_evidence_insufficient` — species label not supported
- `conflicting_frame_labels` — inconsistent class across track frames
- `unsupported_modality` — footage type outside supported set

Refusal does **not** mean no animal is present. It means the software is not
confident enough to make a useful automated claim.

---

## Reviewer checklist

For each candidate or refused clip:

- [ ] Confirm the input video or frame hash
- [ ] Confirm the model and config version
- [ ] Review the bounding boxes or track overlays
- [ ] Check whether the class is supported by this release
- [ ] Note visibility issues: turbidity, glare, occlusion, camera motion,
      partial animal, or crowding
- [ ] Mark final review status: accepted, rejected, uncertain, or out-of-scope
- [ ] Preserve known limits in any exported summary

---

## Public reporting language

**Use:**

> Ceto-Dex produced a candidate detection that requires human review.

> Ceto-Dex refused this clip because confidence or reproducibility was
> insufficient.

**Do not use:**

> Ceto-Dex proved species presence.

> Ceto-Dex certified this site or count.

See also [CLAIMS.md](CLAIMS.md).

---

## Minimum evidence artifact

Each reviewed run should retain:

- Input hash
- Model identifier
- Configuration identifier
- Timestamp of analysis
- Candidate class
- Detection/track summary
- Decision: candidate, track_candidate, refuse, or unsupported
- Refusal reason, if any
- Reviewer status, if reviewed
- Known limits

Schema reference: gate JSON in `validation/local/` and replay bundles under
`artifacts/*/`.

---

## Conservation caution

Do not publish exact site, date/time, or repeated movement details for protected
species if disclosure could increase harassment, poaching, disturbance, or
uncontrolled tourism pressure.
