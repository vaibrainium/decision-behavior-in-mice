# Report: Joint notebook pulse-time model per mouse
Date: 2026-11-18   Agent: Codex   Commit: ed2d38d (base; new fits uncommitted)
Plan: plans/2026-10-26-paper-accumulation-variant.md

## Question
Does the original notebook pulse-time pattern persist when fitting the same joint model within each mouse and testing subject effects?

## Summary
Original notebook selection supports direction-dependent alpha for early/middle pulses across mice. Beta comparisons and late alpha are inconclusive. Results do not retain corrected significance with the current scheduled-label/response-timing selection, where some individual fits are unstable. The original-method result is reproduced, but publication robustness is unresolved. No exclusions or existing figure replacement.

## Findings
- VERIFIED:20 mouse fits across2 selections,29 starts each;580/580 attempts converged. All selected SSEs no worse than native; only DBM12 original shows material improvement0.337345.4 primary and3 sensitivity fits contact bounds. All observed-condition slopes positive. Sources: diagnostics.csv and all_starts.csv in output directory.
- VERIFIED original selection, alpha right−left early: mean20.595345, unadjusted t95%CI[10.368584,30.822106], dz1.440634;9/10 positive, exact p.00390625, Holm6 p.0234375. Middle:14.481409,[6.241303,22.721516],dz1.257190;9/10 positive, rawp.005859375,Holm6 p.029296875. Source: mouse_direction_contrasts.csv and group_tests.csv.
- VERIFIED original selection, alpha right−left late:8.064573,6 mice,Holm6 p1. Directional alpha difference middle−early:−6.113936,CI[−10.969384,−1.258488],dz−.900771,Holm2 p.0234375. This tests the fitted ordinal interaction and is conditional on model assumptions. Beta contrasts do not pass correction. Source: group_tests.csv.
- VERIFIED scheduled-eligible sensitivity: alpha early mean15.655013,Holm6 p.26953125;middle5.766257,p1;late−13.322710,p1;early→middle directional change−9.888757,Holm2 p.3203125. DBM12 has alpha4 at−30 bound and a large adverse directional estimate; no subject exclusion. Source: corresponding rows in group_tests.csv/diagnostics.csv.
- VERIFIED numerical checks: model predictions/objectives and all stage transformations reproduced independently; exact sign flips independently enumerated; Holm checked against statsmodels. Near-minimum early directional spread at most0.029468 coherence units across starts (not parameter uncertainty). Source: verification.json and near_minimum_stability.csv.

## What didn't work
Original data effect is not robustly retained under newer eligibility. Numerical multistart fixes one native local solution but cannot remove identification/selection sensitivity. No p-driven mask, coefficient bound, model, or subject selection was made. Separate direction-by-time curves from earlier analyses were not reused; this is the correct joint notebook specification.

## How to reproduce
`.venv/bin/python -m scripts.paper.pulse_time_per_mouse_joint --eligible dissemination/paper_accumulation/draft_2026-11-15/pulse_psychometric_timing_2026-11-18/eligible_trials.csv --output <fresh-directory>`
Actual output: dissemination/paper_accumulation/draft_2026-11-15/pulse_time_per_mouse_joint_2026-11-18/. Source/notebook/input hashes and definitions in manifest.json, independent checks in verification.json. Existing .venv, no package installation. All mice retained; no raw inputs/accepted outputs changed.

## Caveats
Primary selection retains response-dependent pulse labels, and is used for exact method comparison, not chosen as the final scientific mask. Separate sensitivity changes labels and response eligibility together, so does not isolate their contributions. Subject tests condition on estimated coefficients; some coefficients hit bounds and covariance is ill-conditioned.6 late mice limit power; absence of significance is not equivalence. Linear ordinal time trend is imposed. Two correction families were fixed before fitting (6 directional contrasts,2 interactions), not selected afterward.

## Open questions and next steps
- [ ] Author review per-mouse joint results and which selection answers the intended question.
- [ ] Before paper adoption, isolate label versus response-window changes and address unstable individual coefficients; do not drop DBM12 or select the significant mask.

## Selection-accounting clarification
See 2026-11-18-pulse-timing-trial-accounting.md. All retained trial labels agree; all324 label-disagreement rows are excluded. Sensitivity therefore changes trial inclusion, including asymmetric schedules, null pulses and control virtual timing gates; it is not a pure relabeling check. Full3,783-row exclusion accounting exported.

## Restricted-data preview — 18 November 2026
User requests visualization of the restricted21,725-trial model. Fresh display at pulse_time_restricted_preview_2026-11-18/ uses saved coefficients/tests only, all10 early/middle and same6 all-time companion. Means/SEM independently rechecked against mouse coefficients; render inspected. Reproduce with scripts.paper.preview_restricted_pulse_time. No fits, masks or tests changed.
