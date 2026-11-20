# Report: Which pulse-only model predicts the largest pulse effect?
Date: 2026-11-18   Agent: Codex   Commit: fe8cb41
Plan: plans/2026-10-26-paper-accumulation-variant.md

## Question
Compare pulse-effect magnitude across pulse-only fitted models.

## Summary
VERIFIED normalized UGM without sv predicts largest cohort mean in saved0.3–1.2s response window:5.98632pp. Observed5.47717pp; power+leak closest cohort mean5.23448pp. Largest effect, closest aggregate amplitude, and full likelihood are distinct rankings.

## Findings
- VERIFIED all22 models,10 mice each, no duplicate model/mouse rows. Data references identical across all seven source parts. Sources: pulse_joint_signatures_2026-11-11_{po,ugm}_part*_windows.csv and output manifest.
- VERIFIED linear-leak BIC winner predicts4.82327pp. Choice estimator is pulse-minus-control probability toward pulse direction on symmetric cells, |coherence|<=36%, with response window0.3–1.2s after pulse, averaged across mice. It is not the assignment endpoint or psychometric midpoint shift.

## What didn't work
No failures; scope limited to this summary, not a complete temporal-profile adequacy claim.

## How to reproduce
Read all seven windows CSVs, filter model names from kind=pulse_only IC summary, average0.3–1.2 per model. Saved outputs: pulse_only_effect_magnitude_2026-11-18/{effect_summary,effect_per_mouse,observed_per_mouse}.csv. Source hashes and selection in manifest.json.

## Caveats
Fixed fitted parameters/saved simulation seed; no new significance tests or fit uncertainty. Closest mean need not best fit individual animals/time course.

## Open questions and next steps
- [ ] Use magnitude and temporal/individual adequacy jointly when choosing model predictions to show.
