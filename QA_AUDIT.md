> Historical audit: current counts and objective-level coverage are superseded by `OBJECTIVE_COVERAGE_AUDIT.md` and `assessment/coverage-map.csv`.

# Part II content and structure audit

## Locked design

- Quarto website with two substantive sections: **Weekly Study Guides** and **Practice Questions**.
- Weekly lecture presentation controls scope.
- Alberts *Essential Cell Biology* supplies detailed explanation for the lecture-defined topics.
- Weekly learning objectives control constructed-response coverage.
- Weekly and shared quiz/tutorial materials guide question style and integrated practice.
- Answers are hidden by default with Quarto collapsible callouts.

## Weekly coverage

| Week | Study guide | MCQs | Constructed / integrated | Total questions | Learning-objective coverage |
|---|---|---:|---:|---:|---|
| 8 | Bioenergetics and Enzymes | 35 | 24 | 59 | Complete |
| 9 | Glycolysis, Pyruvate, and CAC | 30 | 25 | 55 | Complete |
| 10 | ETC and Oxidative Phosphorylation | 30 | 14 | 44 | Complete |
| 11 | Lipids, Eicosanoids, and Drug Action | 30 | 20 | 50 | Complete |
| 12 | Cell Signaling, Part I | 30 | 19 | 49 | Complete |

## Mechanical QA

- Every practice question has one collapsed **Answer** callout.
- Question numbering is sequential within each weekly file.
- Study-guide and practice index pages link all five weeks.
- No public answer key is separated from the student-facing practice pages; answers remain collapsed within each question.
- The site source contains no uploaded textbook PDF or course-source PDF. Source files remain outside the public repository.

## Source-boundary notes

- Week 9 preserves lecture-specific liver glucokinase regulation and the course's carbon/electron accounting emphasis.
- Week 10 avoids expanding into Chapter 14 topics not required by the stated learning objectives; thermogenin is retained because it is explicitly examinable.
- Week 11 necessarily relies heavily on lecture/tutorial material for pharmacology, because several examinable drug topics are not the core focus of the assigned Alberts chapters.
- Week 12 introduces GPCRs only to the depth used in lecture and emphasizes RTK/Ras/MAP signaling as instructed.

## Deployment QA

The repository includes a GitHub Actions workflow that renders the Quarto project and deploys the `docs/` output to GitHub Pages after pushes to `main`.

A local Quarto render was not performed in the current execution environment because Quarto is not installed there. The GitHub Actions build after merge is therefore the authoritative render test.
