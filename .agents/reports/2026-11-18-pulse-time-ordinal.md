# Report: Time coded1/2/3 in current joint pulse-influence model
Date: 2026-11-18   Agent: Codex   Commit: ed2d38d (base; uncommitted)
Plan: plans/2026-10-26-paper-accumulation-variant.md

## Question
What happens when using ordinal pulse stage rather than actual onset time in the same model?

## Summary
All-available10-mouse joint fit declines5.40 coherence units/stage,cluster p.0226,jackknife p.0440. Same6 across3 times gives smaller uncertain decline1.72,p.4615. Same10 earlier-times-only reproduces p.0532. Including late and relying on common-effect/cohort assumptions contributes to the stronger all-available result; not a pure time-coding discovery. No existing figure changed.

## Findings
- VERIFIED all available:21,725 trials,10 baseline offsets,late6; slope−5.400683,95%cluster-t9CI[−9.846765,−.954601],p.022556;j ackknife p.044027. Binomial slope−5.157713,p.025946. Source: slope_tests.csv and fit_diagnostics.csv.
- VERIFIED matched6:7,434 trials,slope−1.717220,CI[−7.254332,3.819891],cluster-t5p.461490,jackknife p.495277. Binomial slope−1.782442,p.431293. Same source.
- VERIFIED early/middle10:19,313 trials,slope−5.510359,p.053213,jackknife p.100785;prior independent diagnostic reproduced within numerical tolerance. Source: verification.json and slope_tests.csv.
- VERIFIED6 fits×10 starts=60 successes,no bounds,observed slopes positive. Model/covariance reused tested implementation; stage design/probabilities independently expanded algebraically, objectives/primary tests checked, Hessian finite-step sensitivity verified. Sources: fit_diagnostics.csv, manifest.json, verification.json.

## What didn't work
Matched6 uncertainty remains broad; all-available significance does not establish a robust within-cohort primacy result or a between-cohort difference. No stage/time sign restrictions, case exclusions or p-driven model choices introduced.

## How to reproduce
`OPENBLAS_NUM_THREADS=1 .venv/bin/python -m scripts.paper.pulse_time_ordinal --eligible dissemination/paper_accumulation/draft_2026-11-15/pulse_psychometric_timing_2026-11-18/eligible_trials.csv --previous dissemination/paper_accumulation/draft_2026-11-15/pulse_time_continuous_2026-11-18 --output <fresh-directory>`
Actual output: dissemination/paper_accumulation/draft_2026-11-15/pulse_time_ordinal_2026-11-18/. Code/input hashes exported; new files only. Existing .venv,no installs.

## Caveats
Stage1/2/3 imposes linear equal ordinal steps and is not physical seconds. Only6 late mice; joint10 fit assumes shared pulse effect across cohorts. Cluster t/F approximation with6/10 clusters, trial weighting and shared slope/asymptote assumptions remain. Exploratory comparisons not independent confirmatory tests. Model lines are not raw observations.

## Open questions and next steps
- [ ] Author assess ordinal versus actual-time/cohort-support comparisons without selecting only significant analysis.

## Author preference — 18 November 2026
Author likes the left/all-available10-mouse timing plot. Recorded as preferred panel candidate in selection.json and selected_caption.md, with late-six support and matched6 sensitivity retained. No fits/tests or full Figure4 placement changed.

## Direction interaction display — 18 November 2026
User requests direction interaction. No refits: unpacked same selected model into full alpha left/right curves. Left slope+3.046159,right−7.755207;difference−10.801366,95%CI[−19.693530,−1.909203],p.022556 (same original primary hypothesis),jackknife.044027. Verified half right-minus-left curves equal selected w curve exactly. Sources: pulse_time_direction_interaction_2026-11-18/ CSVs/verification/manifest. Main render inspected; matched6 sensitivity retained. Reproduce via scripts.paper.plot_pulse_time_direction_interaction --source <ordinal-output> --output <fresh-directory>. No new test family or existing Figure4 change.
