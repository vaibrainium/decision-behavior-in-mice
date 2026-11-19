# Joint pulse-time model with categorical mouse ID

Final reported inference is in observed_hessian_inference/. Fits/points identical to parent; parent Gauss–Newton/Fisher covariance retained as approximation.

Equation: A_m(d,t)=u_m+a_D*d+a_T*t+a_DT*d*t; B(d,t)=b0+b_D*d+b_T*t+b_DT*d*t; p=L+(1-L-G)*logistic(B*(coherence+A)). Ten categorical mouse offsets replace alpha1; other9 coefficients shared. All coefficients retain original bounds. Primary trial-count WLS matches notebook objective conditional on mouse, with separate binomial-deviance sensitivity.7 deterministic starts each, all converged, no bound contacts or nonpositive observed slopes.10 mouse baselines, not a numeric ID slope.

Early/middle restricted primary19,313 responses; original-label/control sensitivity23,684. Main inference uses observed score-Hessian mouse-cluster CR1 sandwich and t9/F2,9. Leave-one-mouse fits provide cluster jackknife covariance; no subjects removed from primary. Main test family is2 omnibus blocks (alpha direction/direction×time, beta direction/direction×time), Holm2. Separate exploratory early/middle alpha follow-ups Holm2. Generic coefficient raw p values are not primary discoveries.

This estimates common pulse effects with mouse-specific baseline biases; it does not estimate random pulse effects or different animal slopes/lapses. Trial weights are unequal across mice. Individual fit adequacy shown in restricted_early_fit_adequacy.png is imperfect. Clustering does not repair mean-model misspecification.10-cluster reference: https://facultysites.dss.ucdavis.edu/research/Cameron_Miller_JHR_2015_February.pdf . Existing Figure4 unchanged.

Fit/source provenance: manifest.json, coefficients/cells/predictions, fit_diagnostics.csv, cluster scores/covariances, leave_one_mouse_fits.csv. Independent checks:6 unit tests for derivatives/objectives/categorical coding/Wald/full Hessian identity; parent initial covariance matches statsmodels linearization<6e-7 relative; final Hessian covariance stable to10x numerical-step change and Holm independently reproduced.

Fit: `.venv/bin/python -m scripts.paper.pulse_time_mouse_fixed_effects --eligible dissemination/paper_accumulation/draft_2026-11-15/pulse_psychometric_timing_2026-11-18/eligible_trials.csv --output <new-directory>`
Then scripts.paper.refine_mouse_fixed_effects_inference as in final README.
Tests: `.venv/bin/python -m unittest tests.test_pulse_time_mouse_fixed_effects -v`.

## Finite-sample factor correction
Current covariance/tests are in observed_hessian_inference_v2_trial_count/ (sibling for this inference directory). Total trial count replaces grouped-cell count in CR1, preserving frequency-aggregation invariance. Point estimates and jackknife unchanged; earlier covariance p values superseded.
