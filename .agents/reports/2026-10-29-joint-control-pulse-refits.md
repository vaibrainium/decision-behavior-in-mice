# Report: all DDM families refit on control + pulse trials together
Date: 2026-10-29   Agent: Claude (Opus 5.5)   Commit: 92620b5 (+ this commit: scripts and outputs)
Plan: plans/2026-10-29-joint-control-pulse-refits.md

## Question
Author: refit every model family on all responded trials (control and pulse together, RT < 5 s) "and see what
happens": does the ranking change, do parameters move, and does fitting pulse trials make the models reproduce the
pulse effect?

## Summary
Adding pulse trials to the fit changes almost nothing. The ranking is the control-only one (L1U1 best in the sum, but
beyond 10 NLL in only 2/10 mice; urgency alone drops behind the primary model). The primary model's parameters stay at
~1.0x its control-only fit, so the earlier UCLA parameter shift (known issue) does not reproduce and looks like a flat
likelihood ridge. No family reproduces the size of the pulse effect: every one predicts 2.3-4.5 pp in the 0.3-1.2 s
window against 5.48 pp in the data, and none reaches the 10-16 pp of PSUIM5/6/7 or DBM6. The predicted late reversal
is a property of drift variability and leak, not of integration: families without sv, and the extrema and Stine
models, predict none. High confidence on the descriptive results; the mechanism of the reversal is SUSPECTED.

## Findings
- VERIFIED, audit: 720/720 fits (12 families x 10 mice x cv0-cv4 + all, 15 reps); 0 failed, 0 at the iteration cap;
  nested checks pass except 1 fixed-guess-bias fit (PSUIM6 cv1) 17.2 NLL above the primary model. Parameters at
  bounds: guess_tau upper in 6-11 fits per family; free leak 0-200 at leak 0 in 29/60; Stine nominal DDM ndt at 0 in
  16/60. Simulated non-responses by 5 s at most 0.34 (cap 0.5). Source: scripts/ddm/compare_joint_refits.py ->
  dissemination/figures/qc/joint_refits_audit_2026-10-29.csv; pulse_joint_signatures_2026-10-29_control.csv.
- VERIFIED, ranking (held-out NLL over cv0-cv4, minus primary, summed over mice; mice beyond 10 better/worse; pxp):
  leak+urgency -72.3 (2/1, 0.89); leak -15.2 (2/2); primary 0; urgency +17.7 (0/1); fixed guess bias +20.8;
  free leak 0-200 +96.8; no sv +317.3; extrema E +328.0; ES +517.6; no guesses +533.1; Stine DDM +858.3;
  Stine ES +961.2. Control-only ccv order is the same except urgency (-17.1 there). PSUIM7 carries most of the large
  deltas (no sv +289, ES +293, Stine DDM +437); leak+urgency's gain is mostly PSUIM6 (-51.0), and it is worse in
  PSUIM7 (+23.0). Source: joint_refits_ranking_2026-10-29.csv, joint_refits_heldout_nll_2026-10-29.csv.
- VERIFIED, parameters: primary joint "all" / control-only "control" fit, median over mice: UCLA a 0.93,
  drift_gain 0.98, sv 1.00, ndt 1.28; UW about 1.0 (drift_offset differs, near 0). The old v1 all-trial fit of
  PSUIM6 (fits_resp_final, 50 reps) and the new one reach the same train NLL (16,379.1 vs 16,378.9) with ndt ratios to
  the control fit of 2.90 vs 4.46. Source: joint_refits_parameter_shifts_2026-10-29.csv; inline check in this session.
- VERIFIED, pulse signatures (each family's joint "all" fit simulated on each mouse's trials, 30 reps, seed 0; same
  statistic as the descriptive package, data reproduce its 5.48 pp):
  | model | 0.3-1.2 s (pp) | 1.2-5 s (pp) | mice with late < 0 | toward-pulse median RT shift (ms) |
  |---|---|---|---|---|
  | data | 5.48 | 1.22 | 3 | -60 |
  | primary, control-only fit | 3.25 | -1.02 | 7 | -29 |
  | primary (joint) | 3.43 | -1.27 | 8 | -38 |
  | leak + urgency | 3.25 | -2.14 | 10 | -44 |
  | leak | 3.85 | -2.13 | 9 | -48 |
  | no sv | 3.00 | 1.01 | 0 | -19 |
  | extrema E | 4.03 | -0.33 | 5 | -39 |
  | extrema sampling ES | 4.47 | 0.25 | 2 | -37 |
  | Stine nominal DDM | 2.31 | 0.32 | 2 | -33 |
  | Stine nominal ES | 2.73 | 0.00 | 4 | -86 |
  Per-mouse RMSE in the 0.3-1.2 s window is 5.4-6.5 pp for every model: predicted per-mouse effects span about
  1-6 pp, while the data span -4.2 to 15.5. Source: scripts/ddm/pulse_joint_signatures.py ->
  pulse_joint_signatures_2026-10-29{.png,_summary.csv,_windows.csv,_profile.csv}.
- SUSPECTED: the late reversal comes from selection on trial-level drift (sv) and from leak; removing sv removes it
  (0/10 mice), and leak deepens it. Not tested beyond this comparison.

## What didn't work
- Fitting pulse trials did not raise the predicted pulse effect (primary 3.25 -> 3.43 pp), although pulse trials are
  39-54% of each mouse's trials. Weighting is not the bottleneck: one gain links coherence and pulse.

## How to reproduce
Fits: scripts/slurm/submit_joint_unfreeze.sh on Hyak (jobs 42560879-42560885, HEAD 82ab8e1), pulled with
`bash scripts/sync_ddm_data.sh pull`. Then `.venv/bin/python -m scripts.ddm.compare_joint_refits` and
`.venv/bin/python -m scripts.ddm.pulse_joint_signatures --cache <dir>` (29 min on 32 CPU threads).
Inputs ddm/ddm_inputs_global_ucla_nofreeze.npz (md5 f18e0e6be3b78311e1f5fcdcaa4d0249), ddm/pulse_timing_global.npz.

## Caveats
- 10 mice; per-mouse window effects in small mice rest on few pulse trials (PSUIM10: 166), so the data spread
  includes sampling noise. No test of model vs data per mouse was run.
- Held-out NLL has about 10 NLL Monte Carlo noise per mouse at 15 reps; joint and control-only rankings use different
  held-out sets, so only orders are compared.
- Simulations use 30 reps and one seed.

## Open questions and next steps
- [ ] Author: whether a race / competing-accumulator illustration is worth running (proposed in the session: rho in
      {-1, -0.5, 0}, with and without inhibition, matched to control trials in PSUIM6/7 and DBM6; 1-2 h locally).
- [ ] Check the sv-selection account of the reversal directly (primary model with sv fixed at 0 vs fitted, same mice).
- [ ] Known issue on UCLA parameter shift: mark as not reproduced (ridge), pending author.
