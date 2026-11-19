# Final mouse-ID inference

Use coefficients.csv, regression_tests.csv, display_values.csv and restricted_mouse_fixed_effects.png/pdf/svg here. No fitting/data changes from parent: this replaces approximate Gauss–Newton/Fisher covariance with full observed nonlinear score-Hessian bread in the mouse-cluster CR1 sandwich. t9/F2,9 references are approximate with10 mice. Parent approximation and jackknife retained; inference not selected by significance.

Restricted early/middle primary19,313 trials; original-label early/middle/control sensitivity23,684. Alpha directional omnibus Holm2p0.0000319679; beta0.100328. Alpha early/middle right-left21.853675/13.788067, exploratory follow-up Holm2p0.00755245/0.000180428. Pointwise95% cluster-t9 intervals7.42510–36.28225 and9.12126–18.45487. Timing interaction alone rawp0.109578, so decline is not established.

Restricted binomial alpha omnibus Holm2p0.0000420311,beta0.131328; original-selection WLS alpha0.000248748,beta0.820196. Cluster jackknife restricted WLS alpha≈0.0000287,beta0.088488. Shared pulse/slope/lapse assumptions and trial weighting differ from independent mouse-effect averages. Mouse fixed offsets are not random pulse slopes. Few clusters and imperfect individual adequacy limit inference; no Figure4 adoption.

Reproduce covariance/plots from saved fits:
`.venv/bin/python -m scripts.paper.refine_mouse_fixed_effects_inference --source dissemination/paper_accumulation/draft_2026-11-15/pulse_time_mouse_fixed_effects_2026-11-18 --output <fresh-directory>`

## Finite-sample factor correction
Current covariance/tests are in observed_hessian_inference_v2_trial_count/ (sibling for this inference directory). Total trial count replaces grouped-cell count in CR1, preserving frequency-aggregation invariance. Point estimates and jackknife unchanged; earlier covariance p values superseded.
