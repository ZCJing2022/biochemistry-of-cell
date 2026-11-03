# Source Figure Permissions Register

**Purpose:** Track original figures/images currently embedded in the public-facing Part II study guides so permissions can be requested systematically before final release.

**Current status:** Permission review/request **pending**.

| ID | Week | Web asset | Source type | Source | PDF page | Figure / teaching object | Study-guide placement | Permission status |
|---|---:|---|---|---|---:|---|---|---|
| SF-08-02 | 8 | `w08-textbook-coupling-hires.svg` | Textbook vector crop | Alberts et al. 2023, *Essential Cell Biology*, Ch. 3 | 12 | Fig. 3–17, printed p. 96: favorable C-to-D reaction drives unfavorable X-to-Y reaction | §5 Pathways forward | Pending |
| SF-09-01 | 9 | `w09-textbook-cac-hires.svg` | Textbook vector crop | Alberts et al. 2023, *Essential Cell Biology*, Ch. 13 | 14 | Fig. 13–12, printed p. 458: citric acid cycle | §13 CAC purpose/yield | Pending |
| SF-10-02 | 10 | `w10-textbook-etc-hires.svg` | Textbook vector crop | Alberts et al. 2023, *Essential Cell Biology*, Ch. 14 | 11 | Fig. 14–14A, printed p. 483: respiratory chain / proton pumping; panel A only | §5 ETC proton pumps | Pending |
| SF-11-01 | 11 | `w11-lecture-eicosanoids.jpg` | Lecture | *Chapter 15 MBB201-11 — Lipids* | 7 | Four-stage arachidonic acid → PGH₂ → eicosanoids pathway | §7 Prostaglandin/TxA₂ synthesis | Pending |
| SF-12-02 | 12 | `w12-tutorial-rasmap.jpg` | Tutorial | Tutorial 7 | 15 | Ras → Raf → MEK → ERK pathway | §18 MAP kinase cascade | Pending |

## Implementation

The active source images are committed directly under:

`assets/source-figures/`

No pre-render extraction step is required. The three textbook SVGs replace the former low-resolution JPEGs. They preserve the extracted diagram geometry and labels, with system-font fallbacks and no embedded font files. Figure 14–14 is deliberately limited to panel A; the caption states that Complex II is not depicted in this source panel.

Each textbook figure has a compact inline preview and a link to the vector file. Original source-image previews are capped at 360 CSS pixels in height on desktop and 320 on small screens. Full source pages and surrounding textbook prose are not included.

## Planned source figures

Additional lecture/tutorial/textbook figures can be added in later batches. They should be added to this register only when actually embedded in the study guides.

## Permission workflow for finalization

1. confirm copyright holder / rights administrator;
2. confirm whether a lecture/tutorial graphic itself incorporates third-party artwork;
3. request permission for public educational web display where required;
4. record permission date, terms, attribution wording, and restrictions;
5. replace or remove any figure for which permission cannot be obtained.
