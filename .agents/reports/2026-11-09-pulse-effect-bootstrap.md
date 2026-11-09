# Report: bootstrap uncertainty of the data pulse effect; model predictions vs data noise
Date: 2026-11-09   Agent: Claude (Opus 5.5)   Commit: b08da82 (+ this report's commit)
Plan: plans/2026-11-09-pulse-effect-bootstrap.md

## Question
Are the model-data mismatches in the pulse effect (mean too small at 0.3-1.2 s; reversal at 1.2-5 s; per-mouse spread)
larger than the sampling noise of the data? EXPLORATORY, descriptive (no decision rules).

## Summary
- The mean early effect (5.48 pp) is uncertain: 95% CI 3.2-7.9 pp. Motion-energy integrators (3.3-5.3) lie inside
  it, so "integrators predict too small a mean effect" (reports/2026-11-09-mapping-accumulator-exploratory.md) is NOT
  established by the mean alone; only nominal-input integrators and ME urgency (2.3-3.1) fall below the CI.
- The per-mouse spread is real: Cochran's Q 51.7 on 9 df (p < 0.001, I^2 0.83) early; 21.0 (p 0.013, I^2 0.57) late.
  No family captures it: early chi-square over mice 77-177 on 10 df for all 28 families.
- The late mean (+1.22 pp, CI -1.0 to 3.4) excludes the reversal of the leak/urgency integrators (-1.3 to -2.9) but not
  that of the plain sv integrators (nominal primary -0.86, control-only primary -1.02). The strongest late misfits are
  leak+urgency under power and norm (chi-square 35 on 10 df). So the late reversal is mainly a leak/urgency problem;
  sv alone is not clearly inconsistent with the data at 1.2-5 s.

## Findings
Source: `.venv/bin/python -m scripts.ddm.pulse_effect_bootstrap` (2,000 replicates, seed 0) ->
dissemination/figures/qc/pulse_effect_bootstrap_2026-11-09_{data,heterogeneity,models}.csv. Model predictions from
pulse_joint_signatures_{2026-11-08_explore_partial,2026-11-09_explore_norm,2026-11-09_explore_norm_lu}_windows.csv.
1. VERIFIED: the weighted-count statistic reproduces stats_of on the data (max |diff| 3.6e-15).
2. VERIFIED, data, mean over 10 mice (trial bootstrap within mouse; 50-trial-block bootstrap; hierarchical mice + trials):
   0.3-1.2 s: 5.48 pp, CI 3.17-7.87 (block 2.94-7.84; hierarchical 0.88-9.92).
   1.2-5 s: 1.22 pp, CI -1.02-3.36 (block -0.38-3.17; hierarchical -2.27-5.32).
   Per-mouse SEs 1.1-6.6 pp (PSUIM10 and DBM13 largest; 325 and 396 trials). Block and trial bootstraps agree except
   DBM13 (one session): no sign that within-session drift inflates the trial-level precision overall.
3. VERIFIED, heterogeneity across mice: early Q 51.71, df 9, p 5e-8, I^2 0.83 (SD across mice 6.6 pp vs median
   within-mouse SE 3.1); late Q 20.99, df 9, p 0.013, I^2 0.57.
4. VERIFIED, models (28 families; models.csv):
   - early mean inside the data CI for all ME, power and norm families except urgency (3.08), and all extrema
     families; below it for urgency and nominal_primary 2.88, nominal_urgency 2.88, nominal_leak_urgency 2.72, nominal_no_sv 2.35, nominal_power 2.33.
   - early per mouse: chi-square 77 (power E) to 177 (nominal + power) on 10 df, all p < 2e-12; 2-4 mice outside their CI.
   - late mean outside the data CI (below -1.02) for every leak, urgency, leak+urgency, power and norm integrator and
     ME primary (-1.07 to -2.90); inside for nominal primary (-0.86), control-only primary (-1.02), nominal_no_sv (+0.76)
     all ES families and E under linear, norm and nominal (power E -1.50 is outside).
   - late per mouse: chi-square 16.2 (nominal primary, p 0.10) to 35.5 (power leak+urgency, p 1e-4); 1-4 mice outside.
5. SUSPECTED (reasoning, not tested): the late reversal grows with leak and urgency because both erase the pulse from the
   decision variable while the selection of slow trials it caused remains; sv contributes (nominal no_sv +0.76 vs
   primary -0.86) but alone stays within the data's noise.

## What didn't work
- Session bootstrap: 5 mice have 1-3 sessions (idx_session); replaced by 50-trial blocks within sessions.

## How to reproduce
`.venv/bin/python -m scripts.ddm.pulse_effect_bootstrap [--n_boot 2000] [--block 50]` (about 35 s on CPU).
Inputs: ddm_inputs_global_ucla_nofreeze.npz (responded trials), trial table via pulse_leak_urgency_signatures.observed.

## Caveats
- Percentile CIs; chi-square uses bootstrap SEs, which are themselves noisy for the small mice (PSUIM10, DBM13).
- Model simulation noise approximated as data variance / 30; per-family prediction uncertainty from parameter estimation
  is not included (would make the tests more lenient).
- Many families and two windows; p values descriptive only.
- The hierarchical CI treats these 10 mice as a sample of mice; for model-vs-data comparisons on the same mice the
  within-mouse (trial) CI is the relevant one.

## Open questions and next steps
- [ ] The per-mouse spread is real and unexplained by any family: check whether it tracks per-mouse fitted parameters
      or task variables (pulse timing, coherence mix, rig as covariate only).
- [ ] sv = 0 counterfactual (fixed parameters, sv set to 0) on leak/urgency families, to separate the sv and leak/urgency
      contributions to the late reversal; refitting without sv is not indicated by these numbers.
- [ ] Correct the wording "integrators predict too small a mean effect" in the mapping report's summary when results
      are written up (the mean shortfall is within the data CI for motion-energy integrators).

## Addendum 2026-11-09: sv = 0 counterfactual (author: "ok do it")
Fitted "all" parameters unchanged except sv set to 0, simulated as before (30 reps, seed 0).
Commands: `.venv/bin/python -m scripts.ddm.pulse_joint_signatures --cache <dir> --tag _sv0 --override sv=0 --families
primary leak urgency leak_urgency power_primary power_leak_urgency norm_leak_urgency nominal_primary`;
`.venv/bin/python -m scripts.ddm.pulse_effect_bootstrap --runs pulse_joint_signatures_2026-11-09_sv0 --tag _sv0`.
Outputs: pulse_joint_signatures_2026-11-09_sv0_*.csv, pulse_effect_bootstrap_2026-11-09_sv0_models.csv.
- VERIFIED: with sv = 0 the late reversal disappears in every model, including leak, urgency and leak+urgency:
  late effect +0.57 to +1.66 pp (0-1 mice negative) vs -0.86 to -2.90 (7-10 mice negative) with the fitted sv. All
  inside the data CI (-1.0 to 3.4).
- VERIFIED: leak/urgency still lower the late effect without sv (linear: primary +1.66, leak +0.69, urgency +1.39,
  leak+urgency +0.57), i.e. they amplify but do not create the reversal.
- VERIFIED: the counterfactual is not a usable model: the early effect drops to 1.7-3.3 pp (mostly below the data CI
  3.2-7.9), simulated non-response share rises to 0.42-0.61 in the worst mouse (0.18-0.34 with sv), and per-mouse late
  chi-square is not better (20-31 on 10 df). Refitting without sv costs +317 held-out NLL (linear).
- Revises finding 5 above: the reversal needs sv (selection of slow trials on a persistent per-trial drift); leak and
  urgency amplify it. The data's late effect (+1.2) lies between the fitted-sv models (-0.9 to -2.9) and sv = 0
  (+0.6 to +1.7). SUSPECTED implication: the persistent across-trial variability the RTs need is partly not a
  per-trial drift offset (e.g. a starting-point or bound variability, or session-level drift), which would not select
  against the pulse in the same way; untested.
