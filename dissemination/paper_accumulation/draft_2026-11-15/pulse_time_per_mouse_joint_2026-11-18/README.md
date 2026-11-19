# Original joint pulse-time model fitted per mouse

This analysis implements the notebook model within each mouse, not separate4-parameter fits for each direction/time. Each mouse jointly fits controls and all available pulse times, with shared lower/upper asymptotes. Equation, coefficient bounds and trial-count-weighted squared-error criterion match notebook cell5. Alpha is the additive coherence offset in coh+A; full alpha includes baseline alpha1. The original displayed modulation (without baseline) and native negative midpoint are exported separately. Beta change remains relative to that mouse control slope.

Primary exact-method dataset: original valid_data response-coded labels (25,508 trials). Scheduled-eligible sensitivity uses the current symmetric-schedule/post-offset/+100ms-after-onset table (21,725 trials). These selections are not interchangeable. The original trial labels include early-response relabeling, which must be addressed before paper adoption. No preprocessing or accepted Figure4 outputs changed.

Optimization: retain exact original-start candidate plus pooled-fit seed and27 deterministic starts spanning both signs of alpha2/alpha4; select minimum same-objective WLS. All580 attempts across20 mouse fits converged. Four primary fits and three sensitivity fits contact one or more coefficient bounds. All observed-condition slopes are positive. Numerical near-optimum directional contrasts are stable, but this does not quantify parameter uncertainty or prove a global optimum.

Main original-data preview: all10_early_middle.png/pdf/svg. Same-six all-time companion: same6_all_times. Paired individual alpha preview and every mouse's observed/predicted curves at early/middle times are retained. Points/SEM summarize mice rather than pooled trials. No mice excluded.

Exploratory exact paired sign-flip tests compare right-minus-left alpha and beta at3 times, Holm across6 contrasts. Separate2-test Holm family tests middle-minus-early directional changes in alpha/beta. Late n=6; earlier n=10. T-based95% intervals in group_tests.csv are unadjusted. Tests condition on fitted coefficients, without propagating fitting uncertainty. Linear stage dependence is an imposed model assumption.

Primary results: alpha directional difference early20.5953 coherence units (Holm p0.0234375), middle14.4814 (p0.029296875), late8.0646 (p1). Directional alpha difference declines by6.1139 early→middle (Holm p0.0234375 in separate2-test family). No beta contrast passes correction. Scheduled-eligible sensitivity does not pass correction (early alpha p0.26953125, middle p1); some fits are unstable, notably DBM12. Do not choose the original mask because it is significant or call the result robust to trial eligibility.

Files: coefficients.csv, observed_cells.csv, fitted_curves.csv, mouse_stage_parameters.csv, mouse_direction_contrasts.csv, group_parameters.csv, group_tests.csv, all_starts.csv, covariance arrays, diagnostics.csv, near_minimum_stability.csv, manifest.json and verification.json. Independent verification recomputed predictions/objectives/parameter mappings; sign-flip p values were independently enumerated and Holm checked with statsmodels. Main and early-fit adequacy renders inspected.

Reproduce in a fresh output directory:
`.venv/bin/python -m scripts.paper.pulse_time_per_mouse_joint --eligible dissemination/paper_accumulation/draft_2026-11-15/pulse_psychometric_timing_2026-11-18/eligible_trials.csv --output <new-directory>`
