# Plan: does a divisive-normalization front end, fitted to control trials only, predict the pulse effect?
Status: active
Created: 2026-10-30 by Claude (Opus 5.5)
Related reports: reports/2026-10-29-joint-control-pulse-refits.md; reports/2026-10-30-pulse-weight-joint.md;
reports/2026-10-29-huk-shadlen-replication.md; plans/2026-10-25-amendment-7-normalization.md (abandoned; F2 defined there)

## Goal
Author question 2026-10-30: the pulse acts like ~12-13% coherence (about 3x its stimulus value); can a different
treatment of motion energy account for that? Done = pulse predictions, fixed in advance, from the primary model with the
F2 normalization front end fitted on responded control trials only, compared with the data and with the same model
without a front end.

## Context
- A linear filter cannot change the calibrated pulse area, so filter tuning alone cannot give 3x (filter plan
  2026-10-29, step 7). A nonlinear stage can. F2 (amendment 7): x' = x / (1 + fe_beta * lowpass_fe_tau(|x|)), on the
  drift input; fe_beta 0-20, fe_tau 0.02-1 s. It compresses sustained strong motion. That may let the fit explain the
  shallow psychometric without lowering the gain or raising sv, both of which attenuate pulses (joint refit report).
- The old F2 fits (fits_guess_fast_only_fe-norm, 2026-10-25) include trials without a response (e.g. PSUIM6 4,542 vs
  3,566 responded). Not used (no-response rule).
- Control-trial ME is identical in ddm_inputs_global.npz and _ucla_nofreeze.npz (max diff 0; checked 2026-10-30), so
  the reference control fit fits_resp_final/<m>_L0U0V1Z0G1_control.pkl (responded, fast_only, 50 reps) is valid. Its
  pulse prediction is 3.25 pp at 0.3-1.2 s vs 5.48 pp in the data (pulse_joint_signatures_2026-10-29).
- The free pulse weight leaves the likelihood flat up to w ~2-3, so held-out NLL cannot judge this. The test is the
  predicted pulse effect.

## Assumptions
- The simulator's front end acts on pulse trials exactly as on control trials (same code path; checked in amendment 7
  for the defaults only).
- 15 reps (ccv) and 50 reps (control split) as in the reference fits.

## Steps
- [x] 1. Code: front_end option in primacy.make_model; pulse_joint_signatures accepts control-split fits with a front
      end (new family "primary_fe-norm, control-only fit"); smoke test that fe_beta = 0 reproduces the reference
      simulation exactly.
- [ ] 2. Author submits (Hyak, after git pull):
      sbatch --array=0-49 --export=ALL,JOB_OFFSET=0,MODULE=scripts.ddm.fit_mouse_ddm,EXTRA_ARGS="--responded_only --guess_model fast_only --front_end norm --variants L0U0V1Z0G1 --splits ccv0 ccv1 ccv2 ccv3 ccv4 control --inputs ddm/ddm_inputs_global_ucla_nofreeze.npz --out_dir ddm/fits_resp_fast_only_fe-norm" --time=16:00:00 scripts/slurm/fit_mouse_ddm.slurm
      sbatch --array=50-59 --export=ALL,JOB_OFFSET=0,MODULE=scripts.ddm.fit_mouse_ddm,EXTRA_ARGS="--responded_only --guess_model fast_only --front_end norm --variants L0U0V1Z0G1 --splits ccv0 ccv1 ccv2 ccv3 ccv4 control --inputs ddm/ddm_inputs_global_ucla_nofreeze.npz --out_dir ddm/fits_resp_fast_only_fe-norm --n_reps 50" --time=16:00:00 scripts/slurm/fit_mouse_ddm.slurm
      (grid checked with --list: 0-49 ccv0-4, 50-59 control.)
- [x] 3. Audit: 60 fits, n_train = responded control count, fe_beta / fe_tau at bounds counted.
- [ ] 4. Prediction: simulate each control-split fit on all responded trials of the mouse (nofreeze inputs, 30 reps,
      seed 0, the pulse_joint_signatures statistic). Write the prediction table, commit it, then compare.
- [ ] 5. Comparison (rule fixed here, 2026-10-30, before any F2 fit exists):
      Primary: per mouse |predicted - observed| pulse effect in the 0.3-1.2 s window, F2 vs reference; paired
      Wilcoxon over 10 mice, two-sided, plus mean difference and dz.
      F2 "captures the pulse better" if the error is lower (p < 0.05) AND the mean predicted effect moves toward
      5.48 pp. "Accounts for the size" additionally needs the mean prediction >= 4.5 pp (above every joint family) and
      no worse 1.2-5 s window error.
      Secondary (descriptive, no test): Spearman of predicted vs observed per-mouse effects; 1.2-5 s window; toward-pulse
      RT shift; held-out control NLL F2 minus reference (ccv, per 1,000 control trials); fe_beta per mouse.
      If fe_beta ~ 0 (< 0.05) in >= 7/10 mice, report "control trials do not ask for normalization" and stop.
- [ ] 6. Report and STATUS.

## Out of scope
Fitting the front end on pulse trials (circular); filter retuning (filter plan); other front ends (power was compressive
in amendment 7, which shrinks the pulse); per-site interpretation (rig is a covariate only).

## Log
- 2026-10-30: plan written at the author's request ("sure"); old F2 fits found to include no-response trials, refit needed.
- 2026-10-30: step 1 done: primacy.make_model(front_end=), pulse_joint_signatures --fe_norm/--tag. Smoke test PSUIM10 (425 trials, 166 pulse; 5 reps, seed 0): fe_beta 0 gives identical choices and RTs to the reference; fe_beta 2 differs. Fitting code (--front_end norm) already on Hyak; no push needed. Next: author submits step 2.
- 2026-10-30: author submitted step 2: Slurm 42621772 (ccv0-4, 50 jobs) and 42621773 (control split, 10 jobs, 50 reps); out_dir ddm/fits_resp_fast_only_fe-norm. Next: sync pull, audit (step 3), frozen prediction (step 4).
- 2026-11-06: step 3 audit: 59/60 fits (PSUIM6 control split missing; Slurm 42621773 task 58, cause unknown, author to
  check). All success, none at the iteration cap, front_end norm, include_censored False, reps 15/50, n_train = responded
  control count. fe_beta near 0 (<0.05) in 2/59 fits (control split: DBM5 0.034 only), so the stop rule does not apply;
  fe_tau at the lower bound in 8/59. Control-split fe_beta: DBM12 0.63, DBM13 1.81, DBM14 2.19, DBM15 14.18, DBM5 0.03,
  DBM6 1.94, PSUIM10 1.16, PSUIM5 0.36, PSUIM7 1.14.
- 2026-11-06: step 4 for 9 mice (PSUIM6 pending): `pulse_joint_signatures --fe_norm --families --tag _fe-norm_9mice
  --mice <9>` (30 reps, seed 0); tables committed 204834a before comparing. Added --mice (per-mouse simulations are independent).
- 2026-11-06: PROVISIONAL step 5 on 9 mice (final needs PSUIM6): 0.3-1.2 s mean over these 9 mice: data 4.36,
  reference 3.19, normalization 4.65 (mean moves to the data). Per-mouse |error| normalization minus reference: mean
  -0.02 pp, dz -0.02, Wilcoxon p 0.91 (not lower). Spearman predicted vs observed 0.67 vs 0.68. 1.2-5 s error -2.07 vs
  -2.29 (no worse). RT shift toward pulse -40.9 ms vs data -28.0, reference -24.7. Reading: normalization raises the
  predicted pulse effect about uniformly (overshoots DBM12/13/14, still under PSUIM5/7), so it does not track which mice
  respond strongly. Under the rule: not "captures better" (error not lower), pending PSUIM6.
- 2026-11-06: author: add the static power-law mapping under the no-response rule. Control-only power fits (P1, frozen
  pulse prediction under this plan's step 5 rule) and the mapping x accumulator joint fits are in
  plans/2026-11-06-input-mapping-x-accumulator.md (submit_mapping_accumulator.sh). This plan stays norm-only.
