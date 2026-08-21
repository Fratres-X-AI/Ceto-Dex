# Ceto-Dex data sources

## Primary — sea turtles (underwater video)

| Source | URL | License | Use |
|--------|-----|---------|-----|
| FathomNet Database | https://database.fathomnet.org/fathomnet/ | Public open (verify per asset) | Annotations, clip provenance, institutions |
| FathomNet API | https://api.fathomnet.org | Same | Count/recon before bulk extract |
| MBARI VARS lineage | via FathomNet | Same | ROV/AUV video heritage |

**Split rule:** by `video_id` and institution — never random frames.

## Primary — North Atlantic right whale

| Source | URL | License | Use |
|--------|-----|---------|-----|
| NOAA AI photo-ID | https://www.fisheries.noaa.gov/new-england-mid-atlantic/science-data/artificial-intelligence-right-whale-photo-identification | Research / attribution | Localization reference, ID pipeline history |
| NOAA b-roll gallery | https://videos.fisheries.noaa.gov/ | Public with attribution | Curated clips for replay after per-asset check |
| OBIS-SEAMAP NARWSS | https://seamap.env.duke.edu/dataset/513 | Permission may apply | **Occurrence metadata only — not visual training labels** |
| Kaggle 2015 NARW challenge | Historical competition data | Competition terms | Photo-ID reference; not native survey video |

**Honest limit:** right whale **video-native** training requires curated clip extraction. Public photo-ID sets do not substitute for aerial survey video without a documented curation step.

## Phase 3 optional — manatee

| Source | URL | License |
|--------|-----|---------|
| FWC / public nearshore imagery | https://myfwc.com/research/manatee/ | Permission required — verify before use |

## Hard negatives (FathomNet)

Include deliberately: fish schools, rays, ROV arms, seabed clutter, jellies, debris.

## Catalog fixture

Machine-readable catalog: [`fixtures/phase1_sources_catalog.json`](../fixtures/phase1_sources_catalog.json)

Recon gate output: `validation/local/phase1_data_recon.json`
