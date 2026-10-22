# Report: primacy pipeline built; under the fitted model the timing test has essentially no power
Date: 2026-10-22   Agent: Claude (Opus 5.5)   Commit: a35ef8a
Plan: plans/2026-10-22-primacy-analysis-code.md

## Question
Does the locked primacy analysis work end to end? Could it detect primacy, given how strongly the model says pulses
move choices?

## Summary
The pipeline works on synthetic data: predictions, gates, PyMC GLMMs and sensitivity jobs. No recorded pulse-trial
outcome was read. But the fitted DDM predicts that a ±100%, 50–67 ms pulse changes choices by only ~0.025 logit
(about 0.6 percentage points). Primacy can at most remove that effect, so the largest possible β_middle is ~0.03–0.04,
while the GLMM's standard error with all mice is ~0.05–0.07. Under the model as fitted, the confirmatory test cannot
detect primacy of any size. It becomes informative only if the observed pulse effects are much larger than the model
predicts, which is what the gate (step 6.2) checks.

## Findings
- VERIFIED: the no-pulse input (coherence × onset response + N) equals S + N on control trials to 1.2e-7, all mice.
- VERIFIED: the pulse part of the input integrates to 0.05 (UCLA) / 0.08 (UW) coherence·s, i.e. ~5–8% coherence for 1 s.
- VERIFIED (generating params = single-form L0U0V1Z0G1 control fits, not final): predicted pulse effect, logit, |coh|
  ≤ 36%: DBM14 0.025 / 0.023 / 0.028 (early / middle / late); PSUIM10 0.026 / 0.032. With the drift gain decaying
  40% over 0.5 s: 0.022 / 0.017 / 0.016 and 0.022 / 0.016; 95%: 0.007 / 0.003 / 0.001 and 0.007 / 0.001.
- VERIFIED: predictions reproducible with a fixed seed. Simulated repetitions match independent synthetic datasets
  (150 each, DBM14: RT quantiles within 1.6 SE; 94–98% inside the 95% range).
- VERIFIED: synthetic validation (3 mice, 1 dataset per level) runs. β_middle interval ±0.6 with 3 small mice; a few
  divergences (target_accept raised to 0.95).
- SUSPECTED: the SE of β_middle with all 10 mice is ~0.05–0.07 (scaled from trial counts, not yet simulated). The
  sensitivity run (§9) gives the real number.

## Caveats
- Final fast-only fits are not in yet. The pulse sensitivity depends on drift_gain, sv and the guess rate, but an
  order-of-magnitude change is unlikely.
- Whether the mice react to pulses more than the model predicts is unknown and was deliberately not looked at.

## How to reproduce
`python -m scripts.ddm.check_primacy_pipeline --datasets 1 --levels 0 0.4 0.95` (CPU, ~30 min). The effect-size
table came from `primacy.predict_mouse` with and without `gain_decay` (300 reps); see the commit's analysis-log entry.

## Open questions and next steps
- [ ] Authors: how to proceed given the power result (options in the analysis log, section 5.7).
- [ ] Gates 2–3 pass rule: GATE_MIN_INSIDE = 0.8 proposed; confirm before unblinding.
