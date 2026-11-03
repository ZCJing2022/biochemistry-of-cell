# Original Source-Figure Layer Audit — Repaired V1

## Purpose

Add selected **original** figures from lecture presentations, tutorials, and Alberts textbook chapters while retaining the custom SVG summaries and adapted COURSE VISUAL graphics.

## Deployment repair

The first implementation attempted to reconstruct source images from a ZIP archive during Quarto pre-render. The archive was corrupted in transit, which caused the GitHub Pages render to fail with `zipfile.BadZipFile`.

The repaired implementation removes that dependency entirely. Active source figures are committed directly to:

`assets/source-figures/`

Quarto can therefore render them like any other static asset.

## Active source figures

| Week | Active original source figures | Total visuals |
|---:|---:|---:|
| 8 | 1 | 10 |
| 9 | 1 | 8 |
| 10 | 1 | 8 |
| 11 | 1 | 9 |
| 12 | 1 | 9 |

### Active original figures

- Week 8 — Alberts Ch. 3 Fig. 3–17, reaction coupling.
- Week 9 — Alberts Ch. 13 Fig. 13–12, citric acid cycle.
- Week 10 — Alberts Ch. 14 Fig. 14–14, respiratory chain/proton pumping.
- Week 11 — original Lecture 11 eicosanoid-synthesis pathway.
- Week 12 — original Tutorial 7 Ras–MAP kinase pathway.

## QA

- Each guide has exactly one directly embedded SOURCE FIGURE in this repaired first batch.
- All five image files exist directly in `assets/source-figures/`.
- No QMD references an inactive source-image filename.
- The broken pre-render hook and archive/extraction script have been removed.
- Existing prose, learning objectives, custom visuals, and COURSE VISUAL adaptations are retained.
