# Original Source-Figure Layer Audit — V1

## Purpose

Extend the approved hybrid visual grammar so that essential **original** figures/images from lecture presentations, tutorials, and Alberts textbook chapters can appear directly in the weekly study guides.

The custom SVGs remain useful as orientation and exam-summary graphics. Original source figures are added where the source itself communicates structure, mechanism, or visual detail better than a redraw.

## Implementation

### Build mechanism

Binary source crops are stored compactly in:

`source-assets/source-figures-v1.zip`

Before every Quarto render:

`scripts/extract_source_figures.py`

extracts the images into:

`assets/source-figures/`

The Quarto project invokes this script through the `pre-render` hook.

### Visual treatment

Original figures use:

`source-original-visual`

and render with a **SOURCE FIGURE** label, visually distinct from:

- custom study-guide visuals;
- adapted **COURSE VISUAL** SVGs.

## Source figures added

| Week | Original source figures | Total visuals after V1 |
|---:|---:|---:|
| 8 | 2 | 11 |
| 9 | 2 | 9 |
| 10 | 2 | 9 |
| 11 | 2 | 10 |
| 12 | 2 | 10 |

### Week 8
- original Lecture 8 ATP–glucose coupling graphic;
- original Alberts Ch. 3 Fig. 3–17 reaction-coupling figure.

### Week 9
- original Alberts Ch. 13 Fig. 13–12 citric acid cycle;
- original Tutorial 6 per-glucose metabolic accounting graphic.

### Week 10
- original Alberts Ch. 14 Fig. 14–14 respiratory-chain/proton-pumping figure;
- original Lecture 10 proton-motive-force graphic.

### Week 11
- original Lecture 11 eicosanoid-synthesis pathway graphic;
- original Tutorial 7 therapeutic-index graphic.

### Week 12
- original Alberts Ch. 16 Fig. 16–3 signaling-modes figure;
- original Tutorial 7 Ras–MAP kinase pathway graphic.

## QA

- 10 original source figures are referenced across Weeks 8–12.
- Each weekly guide references exactly 2 original source figures in V1.
- Every original source figure has:
  - meaningful alt text;
  - a source-aware caption;
  - source file/chapter identification;
  - PDF page or figure number where available;
  - permission status marked pending.
- All original prose and learning-objective checklists remain intact.
- The permissions/source record is maintained in `SOURCE_FIGURE_PERMISSIONS_REGISTER.md`.

## Selection principle

The source-image layer is deliberately selective. It does not replace every custom diagram with a scan. Instead:

**original source figure = preserve rich source representation**  
**custom SVG = simplify and organize for learning/exam review**

Future source-image batches should add figures only when they materially improve the page and should be entered in the permissions register.
