# Question explanations — V1

## Implementation

All five weekly practice banks and all three practice exams have a separate **Explanation** callout immediately after each existing **Answer** callout. Both panels are initially collapsed and use independent controls. An integrated exam problem has one explanation panel with a narrative for every labeled subpart, following its existing grouped model answer.

## Coverage

| Page | Answers retained | Explanations added |
|---|---:|---:|
| Week 8 | 59 | 59 |
| Week 9 | 59 | 59 |
| Week 10 | 49 | 49 |
| Week 11 | 55 | 55 |
| Week 12 | 54 | 54 |
| Exam 1 | 43 | 43 |
| Exam 2 | 43 | 43 |
| Exam 3 | 43 | 43 |
| **Total** | **405** | **405** |

The 15 exam integrated panels contain 75 form-specific subpart narratives. All 114 exam MCQ placements use the matching authored rationale for their common concept; parallel-form stems remain unchanged. Weekly narratives are authored by stable question/objective ID, not generated through keyword matching.

## Source basis and limits

Narratives explain the existing course questions and model answers, preserving the documented source terminology and discrepancies. They do not introduce outside scholarship or constitute a new independent scientific audit. Review links lead to the relevant weekly guide(s). Existing questions, option order, answers, objective wording, source lines, 100-mark exam scheme and 120-minute time budget remain unchanged.

## Reproduction and checks

Edit assessment/explanations-*.tsv. Run `python3 scripts/build_objective_assessments.py --write`, then `--check`; render Quarto and run `--check-html docs`. Checks require complete narrative coverage, unchanged answer text, unique panel IDs, paired Answer/Explanation order, no nesting of panels, initially closed controls, one-to-one collapse targets, existing objective anchors, and valid guide-image paths. Normal Pages publishing continues to render committed static QMD files with no new pre-render dependency.
