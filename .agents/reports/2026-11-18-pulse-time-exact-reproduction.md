# Report: Exact notebook population-fit reproduction
Date: 2026-11-18   Agent: Codex   Commit: ed2d38d (base; uncommitted)
Plan: plans/2026-10-26-paper-accumulation-variant.md

## Question
Why do the assistant's timing plots differ from the author's population-model screenshot?

## Summary
Exact reproduction succeeds on current valid_data. The discrepancy was introduced by changing model specification, aggregation, alpha convention and selection; it was not a failure to reproduce the original population fit due to one animal. Original reference points are fully recovered. Prior per-mouse and alternate population fits remain distinct exploratory analyses, not implementations of the notebook model.

## Findings
- VERIFIED: all10 fitted parameters match notebook cell14 saved output to6-decimal rounding on the same25,508 rows. Exact functions extracted from notebook cell5, original single-start WLS unchanged. Source: parameters.csv and manifest.json.
- VERIFIED original plotted alpha values, early/middle/late: left−10.113690/−3.115907/+3.881876; right+13.560653/+10.009833/+6.459013. Source: display_values.csv. The screenshot is directly explained by these population parameters.
- VERIFIED mapping: additive offset A=alpha1+alpha2*d+alpha3*t+alpha4*d*t in coh+A; screenshot shows A-alpha1. Original baseline alpha1=0.487439. Native helper midpoint=-A. Source: notebook cell5 and independently checked transformations in verification.json.
- VERIFIED model differences: original joint fit shares2 asymptotes across all curves, links time linearly and pools trials with trial-count WLS. Earlier assistant previews estimated independent individual curves then averaged coefficients, or fit equal-mouse population curves with stage-specific parameters/asymptotes. These are materially different analyses. The DBM12 boundary finding pertains only to the individual model.
- VERIFIED: original error bars use SE2+t*SE4 and omit covariance/shared-time effects. Reproduction plots now use full contrast covariance; means unchanged. Corrected conditional SEs are not animal-population intervals. Source: display_values.csv, saved full covariance arrays, verification.json.
- VERIFIED: holding original model fixed on current early/middle eligibility still gives direction-separated offsets. Current-selection model coefficients exported separately; no main figure replaced. Source: same_model_current_* cells and parameters.csv.

## What didn't work
Assistant substituted different estimators before directly reproducing the reference, then overemphasized individual-fit instability as the explanation for mismatch. Corrected by exact model reproduction. Keep the real individual-fit boundary finding separate; it does not invalidate the author's joint model or explain its plotted values.

## How to reproduce
`.venv/bin/python -m scripts.paper.reproduce_pulse_time_notebook --eligible dissemination/paper_accumulation/draft_2026-11-15/pulse_psychometric_timing_2026-11-18/eligible_trials.csv --output <fresh-directory>`
Output: dissemination/paper_accumulation/draft_2026-11-15/pulse_time_notebook_reproduction_2026-11-18/. Existing .venv; raw notebook/data unchanged. Source hashes in manifest.json.

## Caveats
Direct reproduction is descriptive, not validation of imposed linear stage trend or pooled covariance for group inference. Response-coded versus scheduled labels and late-cohort support remain relevant when choosing a paper analysis. No new hypothesis tests or automatic Figure4 replacement.

## Open questions and next steps
- [ ] Agree on the exact population model/alpha convention for timing panel, using this successful reproduction as baseline.
- [ ] Then update trial selection and animal-level uncertainty explicitly, one change at a time.
