# Report: intuitive cohort-recovery D
Date: 2026-11-18   Agent: Codex   Commit: 294cddc (base; rendering uncommitted)
Plan: plans/2026-10-26-paper-accumulation-variant.md, R

## Question
Make D more intuitive after author requests simple explanation/redesign.

## Summary
Draft replaces dot axes with generator-to-conclusion rows and direct percentages/counts. C-generated100% (1024/1024), E/ES-generated0% (0/1024) favor C. Rates match both C-vs-E and C-vs-ES comparisons, stated explicitly; no new analysis.

## Findings
- VERIFIED: source rates for the two matched comparisons are identical and in{0,1} for all3 generators, so a single displayed percentage truthfully represents each comparison. Source figure3_control_results_2026-11-17/source_data/fig3_D_recombined_cohorts.csv under draft directory. Exported source_cohort_recovery.csv includes original rates and derived exact counts.
- VERIFIED: recovery_cohorts.py cohorts() defines preference as mean normalized NLL advantage>0 plus two-sided mouse-level t-test with Holm-adjusted p<0.05 across4 alternatives. Display is group preference, not five-way model winner.
- VERIFIED: PNG inspected; source compiles, PDF/SVG exported. Footer explicitly discloses reuse of2 simulated datasets/mouse; cohorts not independent. Conditional generating-parameter/schedule scope retained in caption.

## What didn't work
No failed render. This display does not establish a universal false-positive rate; prior simplified explanation should be understood as a conditional recovery check.

## How to reproduce
```bash
.venv/bin/python -m scripts.paper.figure3D_recovery_intuitive --input dissemination/paper_accumulation/draft_2026-11-15/figure3_control_results_2026-11-17/source_data/fig3_D_recombined_cohorts.csv --output dissemination/paper_accumulation/draft_2026-11-15/figure3D_intuitive_FRESH
```
Current output figure3D_intuitive_2026-11-18. Caption/source/manifest adjacent; source and renderer SHA256 in manifest.json.

## Caveats
Draft for review, main/supplement placement not settled. C/A/B unchanged, no new tests/simulations/fits or commits.

## Open questions and next steps
- [ ] Author assess direct-label D.
- [ ] Continue C recovery-matrix review and decide D placement.
