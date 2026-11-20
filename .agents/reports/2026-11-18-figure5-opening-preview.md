# Report: Figure 5 pulse-only opening preview
Date: 2026-11-18   Agent: Codex   Commit: c16cedf
Plan: plans/2026-10-26-paper-accumulation-variant.md

## Question
Introduce pulse-only accumulation models and identify best predictive fit versus BIC.

## Summary
VERIFIED A is a conceptual model-component schematic, B shows all22 pulse-only candidates in parallel held-out NLL/BIC columns. Predictive and BIC winners highlighted separately. Preview only; no fits or scoring rerun.

## Findings
- VERIFIED all22 candidate scores/counts/parameter counts exactly match source summary, kind=pulse_only. v2/verification.json and pulse_only_candidates.csv.
- VERIFIED predictive winner pulse_norm_ugm_no_sv; BIC winner pulse_linear_leak. See preceding scope report for source values.
- VERIFIED unequal input/variant coverage explicitly labelled; no balanced-factorial or causal component claim. Population and scoring definitions from compare_ic.py/compare_ugm.py.

## What didn't work
First preview BIC ticks were dense; reduced to three major intervals in fresh v2. Original retained.

## How to reproduce
`.venv/bin/python -m scripts.paper.figure5_pulse_only_opening --output <fresh-directory>`. Source: dissemination/figures/qc/model_ic_summary_2026-11-12_rescored.csv. Hashes in manifest.json. No packages/decision fits changed.

## Caveats
Aggregate descriptive ranking, no new subject-level inferential test. Full22-candidate layout and panel assignments await review; Figure4 final unchanged.

## Open questions and next steps
- [ ] Review A model introduction, then B score layout.
