# Plan: code for the primacy test (next-steps step 6), validated on simulated data only
Status: done
Created: 2026-10-22 by Claude (Opus 5.5)
Related reports: reports/2026-10-22-leak-urgency-diagnosis.md; dissemination/reports/primacy-analysis-plan.md (locked,
amendments 1–3)

## Goal
Scripts that run the locked primacy analysis end to end, as soon as the final control-only fits exist:
- pulse-trial predictions (with and without the pulse);
- the section 7 gate;
- the section 6 GLMM (primary: β_middle over all mice; secondary: UW late pulses and trend; rig interaction);
- RT residuals;
- the section 9 sensitivity simulation.

Each part is validated on synthetic data with known primacy.

## Context
- The pulse input is S + N. S = coherence × onset step response + pulse delta × measured pulse response, and N = ME − S
  (`build_ddm_inputs.py`). The no-pulse counterfactual is coherence × onset response + N.
- `gain_decay` is implemented in both simulator backends.
- Locked plan: ≥ 200 simulated repetitions per trial; trials with |coh| ≤ 36% (primary); y = choice in pulse direction
  among trials with a response; offset logit(p̂).

## Assumptions
- Pulse direction = sign(sched_pulse_type); timing = |sched_pulse_type| (1 early, 2 middle, 3 late).
- Gate 1: "the 95% interval of the pooled departure β0 contains 0, or |β0| < 25% of the predicted pulse effect".
  The predicted effect is the mean of logit p̂(pulse) − logit p̂(no pulse), on the logit scale.
- Sensitivity: "decay by X over the first 0.5 s" means gain_decay = −ln(1 − X) / 0.5 (exponential form of the model).
- Local machine has no GPU; validation uses 2–3 mice and reduced repetitions.

## Blinding rule
No step compares predictions with real pulse-trial choices or RTs. The analysis command refuses real data unless
`--unblind` is passed, and that flag is not used in this plan.

## Steps
- [x] 1. `scripts/ddm/primacy.py`: pulse-trial table, no-pulse input (check it equals S on control trials),
      per-trial predictions (p̂ with and without the pulse, mean RT, P(censored), per-repetition summaries); CLI job
      per mouse writing `ddm/primacy/<baseline>/<mouse>.pkl`.
- [x] 2. Gate (§7: pooled departure, RT quantiles, censored fraction) and RT residuals.
- [x] 3. GLMM in PyMC (primary, UW-secondary, trend, rig interaction). Blocked until PyMC is installed (asked
      2026-10-22).
- [x] 4. `scripts/ddm/primacy_sensitivity.py`: synthetic datasets with gain decay at 0, 10, 20 and 40%; refit the
      control-only model per dataset (Hyak job) or use the generating parameters (`--no_refit`, local, approximate).
- [x] 5. Verify on synthetic data (2–3 mice, reduced repetitions):
  - decay 0 gives β_middle ≈ 0 with an interval covering 0, and passes the gate;
  - decay 40% gives β_middle < 0;
  - predictions are reproducible with a fixed seed.
  Result: machinery verified (reproducible; repetitions match independent synthetic data; GLMMs sample). The expected
  β_middle < 0 at 40% (even 95%) decay was NOT seen: the predicted effect is ≤ 0.04 logit against an interval of ±0.6
  with 3 mice. This is the power finding, not a code fault.
- [x] 6. Document commands in the analysis log (section 8) and the next-steps plan (step 6); report.

## Out of scope
- Running anything on real pulse choices.
- The model-free check (amendment 2): code can be written later, but not run before the confirmatory test.

## Log
- 2026-10-22: PyMC/ArviZ not installed; step 3 written but untested until installed.
- 2026-10-22: PyMC 5.25.1 installed (user OK; numpy 1.26 kept). Steps 1–5 done on synthetic data. Gate-1 intercept-only
  bug fixed. Finding: predicted pulse effect ~0.025 logit, so the timing test has ~no power under the fitted model
  (reports/2026-10-22-primacy-power.md). Paused for the authors' decision. Step 6 done (analysis log 5.7, 8.5b; next-steps 6.6).
- 2026-10-22: authors chose option 2 (predictive check first); gate rule accepted. Plan done; report reports/2026-10-22-primacy-power.md.
