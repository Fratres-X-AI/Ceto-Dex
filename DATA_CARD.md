# Ceto-Dex data card

**Project:** Ceto-Dex  
**Purpose:** Underwater video fixtures, source catalog, and training-data
documentation for protected marine species detection, tracking, refusal testing,
and human-review workflows.

---

## Dataset status (v0.1.0-public-bench)

| Posture | Status |
|---------|--------|
| Public-domain or open-license footage in repo | **No bulk footage** — manifest fixtures only |
| Fratres-owned footage cleared for redistribution | **None in first release** |
| Tiny illustrative fixtures | **Yes** — synthetic manifest rows in `fixtures/` |
| Training data redistributed | **No** — users supply or download per source licenses |
| Model weights in repo | **No** — local only; hashes documented |

Do not publish footage until redistribution rights are clear.

---

## Repository fixtures

| File | Contents | Rights |
|------|----------|--------|
| `fixtures/sample_manifest.jsonl` | 3 synthetic manifest rows (turtle, turtle, NARW) | Illustrative schema only — placeholder hashes |
| `fixtures/phase1_sources_catalog.json` | Machine-readable source catalog | Public URLs + license fields |

These fixtures prove the manifest and gate pipeline. They are **not** a training
set.

---

## Documented external sources

### Sea turtles (underwater video)

| Source | License | Use in Ceto-Dex |
|--------|---------|-----------------|
| [FathomNet Database](https://database.fathomnet.org/fathomnet/) | Public open (verify per asset) | Annotations, clip provenance |
| [FathomNet API](https://api.fathomnet.org) | Same | Count/recon before bulk extract |
| `kim2429/SeaTurtles_Images` | Verify before use | RunPod v1 turtle train (proxy labels) |

**Split rule:** by `video_id` and institution — never random frames.

### North Atlantic right whale

| Source | License | Use in Ceto-Dex |
|--------|---------|-----------------|
| [NOAA AI photo-ID](https://www.fisheries.noaa.gov/new-england-mid-atlantic/science-data/artificial-intelligence-right-whale-photo-identification) | Research / attribution | Localization reference only |
| [NOAA b-roll gallery](https://videos.fisheries.noaa.gov/) | Public with attribution | Curated clips after per-asset check |
| OBIS-SEAMAP NARWSS | Permission may apply | **Occurrence metadata only — not visual labels** |

**Honest limit:** right whale video-native training requires curated clip
extraction. Not started in v1.

### Manatee (Phase 3)

| Source | License |
|--------|---------|
| Wang et al. / Save the Manatee Club Blue Spring counting set | Verify before redistribution |
| FWC / public nearshore imagery | Permission required |

Used for RunPod v1 manatee baseline (783 images, single webcam site).

### Marine utility merge

Mixed sources: iNaturalist (presence proxies), DeepFish (real bboxes), turtle
and manatee subsets. iNat whale/stingray/coral classes = **presence proxy only**.

Full catalog: [docs/DATA_SOURCES.md](docs/DATA_SOURCES.md).

---

## Annotation method

| Label type | Where used | Caveat |
|------------|------------|--------|
| Whole-image proxy box | Sea turtle v1 | Inflated mAP — not real instance boxes |
| Line-label → axis bbox | Manatee v1 | Single-site webcam bias |
| Real bounding boxes | DeepFish subset | Best ground truth in merge |
| Presence proxy | iNat classes | Not instance-level truth |

State clearly when labels are proxy labels rather than field-verified truth.

---

## Sensitive data handling

Before publishing any footage or derived artifacts:

- Remove exact coordinates unless already public and permitted
- Remove timestamps if they expose repeat animal locations or vulnerable sites
- Blur or exclude people, vessels, signs, dock markers, and private property
- Avoid publishing repeated encounter patterns for protected species

---

## Known dataset limits

- Camera type and placement bias (ROV vs aerial vs webcam)
- Water clarity/turbidity limits
- Species/class imbalance
- Region or habitat bias (Monterey, Blue Spring, etc.)
- Annotation uncertainty on proxy-label sets
- FathomNet bulk-fetch failures limited turtle data expansion

---

## Recommended user notice

> This repository provides reproducible research tooling and manifest fixtures.
> It is not a complete survey of species presence, abundance, health, habitat
> use, or conservation status. Training data is not redistributed; obtain
> sources under their own licenses.

---

## Redistribution rights

| Item | Redistribution |
|------|----------------|
| Source code (Apache-2.0) | Yes |
| Manifest fixtures | Yes (illustrative) |
| Gate JSON | Yes |
| Training footage | No — follow source licenses |
| Model weights | No — build locally or contact Fratres X AI |

**Contact:** [fratres-x.com](https://www.fratres-x.com) for takedown or corrections.
