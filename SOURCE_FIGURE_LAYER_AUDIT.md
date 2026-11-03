> Current update: the low-resolution Week 11 and Week 12 raster source slides have been retired. The three sharp textbook source-vector figures remain. See `OBJECTIVE_COVERAGE_AUDIT.md`.

# Original Source-Figure Layer Audit — Sharp, Compact V2

## Purpose

Replace the unclear, oversized textbook JPEGs with original source-PDF vector artwork. Preserve the lecture-defined scope, prose, learning objectives, practice materials, and existing custom diagrams.

## Active source figures

| Week | Original source figure | Format | Total visuals |
|---:|---|---|---:|
| 8 | Alberts Figure 3–17, reaction coupling | Cropped SVG | 10 |
| 9 | Alberts Figure 13–12, citric acid cycle | Cropped SVG | 8 |
| 10 | Alberts Figure 14–14A, respiratory chain | Cropped SVG, panel A only | 8 |
| 11 | Lecture 11, eicosanoid synthesis | Existing JPEG, unchanged | 9 |
| 12 | Tutorial 7, Ras–MAP pathway | Existing JPEG, unchanged | 9 |

All source assets are committed directly under `assets/source-figures/`. No archive reconstruction or pre-render extraction is required.

## Source extraction

The replacement textbook graphics were extracted from the original chapter PDFs supplied in `part II.zip`, rather than enlarged from the old JPEGs or redrawn.

| Source file | Chapter PDF page | Printed page | Figure | Crop rectangle in visible-page coordinates, points |
|---|---:|---:|---|---|
| `Alberts 2023i Chapter 3.pdf` | 12 | 96 | 3–17 | (40, 460, 207, 654) |
| `Alberts 2023i Chapter 13.pdf` | 14 | 458 | 13–12 | (246, 38, 534, 311) |
| `Alberts 2023i Chapter 14.pdf` | 11 | 483 | 14–14A | (44, 37, 380, 225) |

The crops exclude surrounding textbook prose and page margins. Figure 14–14 is explicitly limited to panel A; its caption and alt text note that Complex II is not depicted. The extracted artwork retains the source's paths and positioned labels. System-font fallbacks are specified; font files are not embedded or distributed.

## Display correction

- Removed the old full-width stretching rule for original source images.
- Original-source previews have `width: auto`, `max-width: 100%`, and `max-height: 360px` on desktop.
- Small-screen previews have a 320px height ceiling.
- The three textbook figures have compact containers and keyboard-accessible links to their vector files in a separate tab, where browser zoom can be used for detail.
- Captions retain source, figure, printed page, chapter-PDF page, and pending permission status.
- The three superseded textbook JPEGs were removed, not left as fallback images.

## Validation performed before merge

- All three SVGs parse as valid XML and render in Chromium.
- Vector previews inspected for legibility and retention of the source diagram.
- Offline HTML/CSS layout fixture tested at 1440×900, 1280×800, and 390×844 CSS pixels.
- At desktop widths, measured image sizes were approximately 260×302, 380×360, and 640×358 pixels for Weeks 8, 9, and 10 respectively.
- At 390px viewport width, no image or page overflow was detected; the images measured approximately 260×302, 320×303, and 320×179 pixels.
- Enlargement-link destinations and `_blank` targets checked. Live popup navigation was not exercised in the offline fixture.
- These are layout-fixture checks, not a claim of a completed live-site browser audit. GitHub Pages build/deployment status must be checked separately after merge.

## Quality rule for later additions

Use vector extraction when source artwork permits it. Otherwise use a tightly cropped, genuinely high-resolution raster source. Do not enlarge a low-resolution screenshot to fill the page. Remove a figure when an adequate source cannot be recovered.

## Deployment history

V1 initially used a ZIP pre-render step that failed with `zipfile.BadZipFile`. That mechanism was removed in PR #7. V2 continues the direct-static-asset approach and introduces no new build dependency.
