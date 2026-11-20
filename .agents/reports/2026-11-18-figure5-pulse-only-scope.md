# Report: Figure 5 restricted to pulse-only models
Date: 2026-11-18   Agent: Codex   Commit: 3b55eca (scope notes uncommitted)
Plan: plans/2026-10-26-paper-accumulation-variant.md

## Question
Which accumulation models should open Figure5 and which currently fit best?

## Summary
Author restricts Figure5 to pulse-only fitted models. VERIFIED existing rescored summary distinguishes predictive-score winner from BIC winner. No new fits or significance claims.

## Findings
- VERIFIED pulse_norm_ugm_no_sv has lowest heldout NLL16889.94 among22 pulse_only rows; pulse_linear_leak_urgency next16899.04. Source: dissemination/figures/qc/model_ic_summary_2026-11-12_rescored.csv, kind=pulse_only sorted by heldout.
- VERIFIED pulse_linear_leak has lowest BIC61858.43; predictive winner BIC62129.38. Same file; n11479 for all pulse-only rows. These rounded summary scores are not new subject-level inference.

## What didn't work
Earlier framing incorrectly introduced joint-fit winner for this requested figure; scope is now explicitly pulse-only.

## How to reproduce
Read summary with pandas, filter kind=='pulse_only', sort separately by heldout and bic. Definitions/scoring: scripts/ddm/compare_ic.py and compare_ugm.py.

## Caveats
Predictive and full-fit information criteria are different; no claim of one mechanistic winner. Input/variant coverage is not a complete balanced factorial design. No candidate exclusion based on desired result.

## Open questions and next steps
- [ ] Prepare model-introduction panel from actual pulse-only candidate definitions.
