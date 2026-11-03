# Source Figure Permissions Register

**Purpose:** Track original figures/images incorporated into the public-facing Part II study guides so permissions can be requested systematically before final release.

**Current status:** Permission review/request **pending**. These records identify the source precisely; they do not assert permission status.

| ID | Week | Web asset | Source type | Source | PDF page | Figure / teaching object | Study-guide placement | Permission status |
|---|---:|---|---|---|---:|---|---|---|
| SF-08-01 | 8 | `w08-lecture-coupling.jpg` | Lecture | *Chapter 3 and Chapter 4 MBB201-8 — Bioenergetics and Enzymes* | 11 | ATP hydrolysis coupled to glucose phosphorylation | §5 Pathways forward | Pending |
| SF-08-02 | 8 | `w08-textbook-coupling.jpg` | Textbook | Alberts et al. 2023, *Essential Cell Biology*, Ch. 3 | 12 | Fig. 3–17, reaction coupling / activated carrier | §5 Pathways forward | Pending |
| SF-09-01 | 9 | `w09-textbook-cac.jpg` | Textbook | Alberts et al. 2023, *Essential Cell Biology*, Ch. 13 | 14 | Fig. 13–12, citric acid cycle | §13 CAC purpose/yield | Pending |
| SF-09-02 | 9 | `w09-tutorial-accounting.jpg` | Tutorial | Tutorial 6 | 5 | Per-glucose glycolysis + PDH + CAC accounting | §14 Stoichiometry per glucose | Pending |
| SF-10-01 | 10 | `w10-lecture-pmf.jpg` | Lecture | *Chapter 14 MBB201-10 — Electron Transport Chain* | 14 | Proton-motive-force teaching graphic | §6 Proton-motive force | Pending |
| SF-10-02 | 10 | `w10-textbook-etc.jpg` | Textbook | Alberts et al. 2023, *Essential Cell Biology*, Ch. 14 | 11 | Fig. 14–14, respiratory chain / proton pumping | §5 ETC proton pumps | Pending |
| SF-11-01 | 11 | `w11-lecture-eicosanoids.jpg` | Lecture | *Chapter 15 MBB201-11 — Lipids* | 7 | Four-stage arachidonic acid → PGH₂ → eicosanoids pathway | §7 Prostaglandin/TxA₂ synthesis | Pending |
| SF-11-02 | 11 | `w11-tutorial-ti.jpg` | Tutorial | Tutorial 7 | 4 | Therapeutic-index teaching graphic | §17 Therapeutic index | Pending |
| SF-12-01 | 12 | `w12-textbook-signaling.jpg` | Textbook | Alberts et al. 2023, *Essential Cell Biology*, Ch. 16 | 3 | Fig. 16–3, four intercellular signaling modes | §2 Signaling types | Pending |
| SF-12-02 | 12 | `w12-tutorial-rasmap.jpg` | Tutorial | Tutorial 7 | 15 | Ras → Raf → MEK → ERK pathway | §18 MAP kinase cascade | Pending |

## Repository implementation

The cropped source images are stored as a compact archive:

`source-assets/source-figures-v1.zip`

During Quarto rendering, `scripts/extract_source_figures.py` extracts them to:

`assets/source-figures/`

They are visually marked **SOURCE FIGURE** in the rendered study guides.

## Permission workflow for finalization

For each registered figure:

1. confirm the exact copyright holder / rights administrator;
2. confirm whether the lecture/tutorial graphic itself incorporates a third-party textbook/publisher image;
3. request permission for public educational web display where required;
4. record permission date, terms, attribution wording, and any restrictions in this register;
5. replace or remove any figure for which permission cannot be obtained.

## Selection rule

Original source figures are included only when their visual information adds something not captured as well by prose or a simplified summary diagram. The goal is not to reproduce source documents wholesale.
