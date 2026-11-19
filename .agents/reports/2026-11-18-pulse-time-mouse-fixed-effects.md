# Report: Joint pulse-time model with categorical mouse offsets
Date: 2026-11-18   Agent: Codex   Commit: ed2d38d (base; uncommitted)
Plan: plans/2026-10-26-paper-accumulation-variant.md

## Question
Does adding mouse ID to a joint notebook-shaped regression support pulse effects under restricted eligibility?

## Summary
Common pulse effects with separate mouse baselines support a directional alpha effect. Beta direction effect and timing decline remain inconclusive. Conclusion agrees across objectives, original selection and cluster jackknife. This changes the estimand/constraints relative to averaging independently fitted animal effects.10-cluster inference exploratory; no Figure4 adoption.

## Findings
- VERIFIED: primary19,313 restricted and sensitivity23,684 original-label early/middle/control responses;10 mouse offsets+9 common coefficients=19 parameters.4 fits×7 starts all converged; no bounds/nonpositive slopes. Source: fit_diagnostics.csv and manifest.json.
- VERIFIED final restricted WLS: alpha block F2,9=47.867329, Holm2p3.196792e-5; beta F3.000986,p.100328. Source: observed_hessian_inference/regression_tests.csv. Full observed nonlinear score Hessian is final bread.
- VERIFIED alpha early/middle right-left21.853675/13.788067 coherence units, pointwise95% cluster-t9 intervals[7.42510,36.28225]/[9.12126,18.45487], exploratory Holm2p.00755245/.000180428. Alpha direction×time rawp.109578: timing decline not established. Sources: final tests/coefficients/display_values.csv.
- VERIFIED sensitivities: restricted binomial alpha omnibus Holm2p4.20311e-5,beta.131328; original WLS alpha.000248748,beta.820196; cluster jackknife restricted WLS alpha≈2.87e-5,beta.088488. Source: final tests. No objective/mask selected by p.
- VERIFIED:6 unit tests pass; initial sandwich agrees with statsmodels linearized covariance<6e-7 relative. Final observed Hessians positive definite, covariance stable to10x finite-difference step; Holm independently checked. Sources: tests/test_pulse_time_mouse_fixed_effects.py and parent/final verification.json/manifests.
- VERIFIED visual adequacy: some mouse slopes/asymptotes differ from shared model. Main/individual early renders inspected. Source: restricted_early_fit_adequacy.png.

## What didn't work
Initial Gauss–Newton/Fisher bread omits nonlinear residual-curvature terms. Preserved it as audit approximation; final uses full observed score Hessian without refitting, conclusion unchanged. System Python documentation command hit pandas ABI incompatibility; reran scientific checks in .venv, no installs.

## How to reproduce
Fit: `.venv/bin/python -m scripts.paper.pulse_time_mouse_fixed_effects --eligible dissemination/paper_accumulation/draft_2026-11-15/pulse_psychometric_timing_2026-11-18/eligible_trials.csv --output <fresh-directory>`.
Final inference: `.venv/bin/python -m scripts.paper.refine_mouse_fixed_effects_inference --source <fit-directory> --output <fresh-inference-directory>`.
Checks: `.venv/bin/python -m unittest tests.test_pulse_time_mouse_fixed_effects -v`.
Actual folder: dissemination/paper_accumulation/draft_2026-11-15/pulse_time_mouse_fixed_effects_2026-11-18/, final in observed_hessian_inference/. Hashes exported; existing .venv.

## Caveats
10 clusters, unequal trial counts; t9/F2,9 approximations not guaranteed finite-sample calibration. Common slopes/lapses/pulse terms are assumptions; clustering does not fix mean-model misspecification. Conditional common-effect estimate differs from equal-mouse independent estimates. Pointwise intervals not simultaneous. Two primary omnibus and two separate exploratory follow-up tests fixed before fits. No random pulse effects tested. Reference: Cameron/Miller2015, https://facultysites.dss.ucdavis.edu/research/Cameron_Miller_JHR_2015_February.pdf .

## Open questions and next steps
- [ ] Author assess shared-effect formulation and individual adequacy before paper adoption.
- [ ] Consider animal sensitivity/pulse heterogeneity if pursuing stronger group inference; significance alone does not validate common-effect assumptions.

## Finite correction update
Cluster frequency correction now uses underlying trials rather than grouped cells; current inference is observed_hessian_inference_v2_trial_count/. Coefficients and scientific conclusion unchanged; earlier covariance-based p values superseded. See 2026-11-18-cluster-frequency-correction.md. Separate per-mouse sign-flip tests unaffected.
