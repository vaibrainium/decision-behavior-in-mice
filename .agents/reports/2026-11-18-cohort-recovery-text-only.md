# Report: cohort recovery in text, not figure
Date: 2026-11-18   Agent: Codex   Commit: 294cddc (base; update uncommitted)
Plan: plans/2026-10-26-paper-accumulation-variant.md, R

## Question
Author chooses to report D cohort-recombination result in text rather than a figure.

## Summary
Current Figure3 is A–C. Results paragraph retains exact counts and reuse/conditional scope, with obsolete Figure2D reference removed. Current caption packet removes D; previous caption preserved in cohort_recovery_text_2026-11-18/. D artwork retained as historical, explicitly excluded from current layout.

## Findings
- AUTHOR DECISION: cohort-recovery result text only, no D main or supplementary panel requested.
- VERIFIED: revised Results paragraph reports all1024 C-generated recombinations and zero E/ES-generated recombinations favor C over matched alternatives; source rates unchanged. Trial reuse/conditional recovery caveats explicit. Source CSV copied byte-identically and hashed in placement.json.
- VERIFIED: draft README/index/captions prominently list Figure3 A–C. C matrix still pending review; A alternatives/B approval unchanged. No newly assembled combined artwork claimed.

## What didn't work
No failed operations or new analyses.

## How to reproduce
Read dissemination/paper_accumulation/draft_2026-11-15/results.md recovery paragraph and cohort_recovery_text_2026-11-18/{results_paragraph.md,placement.json}. Compare source CSV hash with original figure3_control_results_2026-11-17/source_data/fig3_D_recombined_cohorts.csv. Full definition/decision rule remains in Methods and prior report.

## Caveats
Historical combined figure/Word packet not regenerated or globally renumbered during panel-led review. D artwork/source preserved for provenance, not selected for publication. No new results or fit changes.

## Open questions and next steps
- [ ] Review Figure3C recovery matrix.
- [ ] Choose A alternative later and assemble A–C after C approval.
