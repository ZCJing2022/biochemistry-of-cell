# Learning-objective and image-quality audit — V2

## Verified structure

78 source objectives in original order; 35 MCQs per weekly bank; one explicit worked question per objective; 23 retained integrated weekly questions. Total weekly items: 276. Each exam: 38 MCQs + 5 integrated problems (25 subparts), 100 marks, 120-minute planning budget. Every exam maps all 78 objective IDs. Correct-letter counts differ by at most one within each bank/form; exact exam MCQ stems are distinct across forms. Conceptual overlap is intentional.

## Images

Removed the two remaining low-resolution raster slide images from the Week 11 and Week 12 guides and active assets. Their existing sharp course diagrams remain. The source slide artwork itself contains raster material; enlarging or re-saving it is not evidence of recovered detail. The three textbook source-vector figures from PR #8 remain. No new image-generation or archive-extraction step is introduced.

## Reproduction

Edit assessment/*.tsv; run `python3 scripts/build_objective_assessments.py --write`, then `--check`, render Quarto, then `--check-html docs`. Commit the generated QMD/coverage files. Normal Pages builds read the static QMDs; no pre-render hook is added. Source text/counts were checked against the five uploaded Learning Objectives PDFs, not inferred from the guides.

## Limits

The automated checks establish IDs, counts, option/answer structure, coverage links and generated-output consistency; they do not mechanically prove the scientific correctness of prose. Timing is a design budget, not a student-pilot result.

## Source wording and counting notes {#source-notes}

These assessments follow the supplied Learning Objectives, lecture presentations, tutorials and assigned Alberts chapters. The original objective wording below is retained, with whitespace and mathematical glyphs normalized. Questions make compound requirements explicit rather than silently treating a topic mention as coverage.

- **Week 9, reaction 6:** slide 9:14 calls this substrate-level phosphorylation, whereas slides 9:17–9:18 show production of 1,3-BPG in reaction 6 and direct ATP formation in reaction 7. The questions distinguish these steps and include all three consequences named on slide 9:14, including the NAD+ requirement for anaerobic continuation.
- **Week 9, counting basis:** the overview (9:6) and accounting give two NADH per glucose. Slide 9:19 also contains a one-NADH label. Questions explicitly distinguish per-three-carbon-unit, per-pyruvate, per-cycle-turn and per-glucose counts; they use the complete per-glucose accounting.
- **Week 10, location:** slide 10:3 says the ETC is in the matrix; the detailed structure/ETC slides 10:5 and 10:9 place its proteins in the inner membrane. The assessment uses the explicit membrane/compartment description, also supported by Alberts Chapter 14.
- **Week 11, aspirin target:** slide 11:17 uses “PGH2” in its aspirin explanation, while 11:13–11:14 identify covalent modification of COX/PGHS. Questions distinguish the enzyme PGHS from its product PGH2.
- **Week 11, pharmacology wording:** “bioavailability” follows the lecture's stated operational meaning, the amount of drug in circulation. The TI exercises supply dose values and use TD50/ED50 (or LD50/ED50); the lecture's diagram uses ED50 although adjacent text also says EC50. Exercises are not clinical prescribing advice.
- **Week 12, terminology:** objective 1 says “intracellular”; lecture 12:3 calls the four listed modes **intercellular** signaling. Slides 12:10–12:12 use “GPCRs” as shorthand for the receptor-associated G-protein arrangement; the questions distinguish the seven-pass receptor from its heterotrimeric G protein.
- **Week 12, adaptor connection:** one sentence on lecture 12:20 names Src in the Sos connection. Tutorial 7, PDF p. 15, explicitly describes Grb2–Sos; that is the assembly used in the pathway questions. Ras activates Raf by binding, not by phosphorylating it.

The 38-ATP illustration in Week 10 is labeled FYI. These exams do not require a new ATP-per-carrier convention or add topics outside the learning-objective scope.
