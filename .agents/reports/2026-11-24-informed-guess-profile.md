# Report: informed fast guesses — implementation, fixed-parameter profile, recovery
Date: 2026-11-24   Agent: Claude (Opus 5.5)   Commit: 886d3d1 (all changes below uncommitted)
Plan: plans/2026-11-24-informed-guess-family.md

## Question
Can fast guesses that report the DV (Molano-Mazón 2024 action-initiation idea) explain the PSUIM6/7 fast-window pulse
effect and fast control accuracy, and are the new parameters identifiable enough to justify a Hyak fit family?

## Summary
Implemented and tested: guess_w = 0 reproduces the current model exactly. With every other parameter fixed, w ≈ 0.5 and
read_lag 0.1 s improves held-out NLL by about 8-9 in PSUIM6/7, does nothing in DBM5, and worsens DBM12. w is
recoverable to about ±0.08 in PSUIM7-sized data; read_lag is not. A refit is worth running (moderate confidence that
it helps PSUIM6/7; low confidence that it passes tier A, because DBM12 gets worse at fixed parameters).

## Findings
- VERIFIED: w = 0 reproduces the stored PSUIM7 test NLL (max |diff| 0.0) and MouseDDM.simulate output exactly.
  Source: tests/test_informed_guesses.py; profile.csv (guess_w = 0, seed 12345).
- VERIFIED: fixed-parameter profile. ΔNLL summed over pcv folds, mean ± sd over 2 seeds:

  | Mouse | Setting | ΔNLL | Notes |
  |---|---|---|---|
  | PSUIM7 | w 0.5, lag 0.1 | −8.3 ± 2.7 | mostly RT |
  | PSUIM7 | w 1, lag 0.1 | +66 | choice cost; fast effect 26.4 vs data 26.7 pp |
  | PSUIM6 | w 0.5, lag 0.1 | −9.3 ± 8.6 | |
  | DBM5 | any | about 0 | |
  | DBM12 | w 0.25–1 | +2.5 to +45 | choice |

  Source: draft_2026-11-15/informed_guess_profile_2026-11-24/profile.csv; scripts/paper/informed_guess_profile.py.
- VERIFIED: guardrail on fast (< 0.6 s) control accuracy at 100% coherence, comparing data with w = 0 and w = 0.5 (lag 0.1):
  - PSUIM7: 0.77, 0.53, 0.67;
  - PSUIM6: 0.74, 0.51, 0.60;
  - DBM12: 0.68, 0.59, 0.65;
  - DBM5: 0.44, 0.50, 0.53.

  At w = 1, PSUIM7's intermediate coherences overshoot. Source: control_guardrail.csv.
- VERIFIED: recovery (PSUIM7, full pulse fit as truth, fit w and read_lag only, n_reps 15):

  | w true | lag true | w_hat (2 datasets) | lag_hat |
  |---|---|---|---|
  | 0.5 | 0.12 | 0.45, 0.42 | 0.15, 0.07 |
  | 0.25 | 0.20 | 0.29, 0.35 | 0.33, 0.12 |
  | 0 | 0.10 | 0.009, 0.034 | 0.33, 0.16 |

  nll_hat was at or below nll_truth everywhere (by 0.02–5.5), so the optimizer reached the truth's level or better. The
  weak lag identification comes from the likelihood, not from the search.
  Source: draft_2026-11-15/informed_guess_recovery_2026-11-24/recovery.csv; scripts/paper/informed_guess_recovery.py.
- SUSPECTED: a free refit (re-tuning the other parameters) recovers more of the fast-window effect than the fixed-parameter
  profile shows, and DBM12's cost shrinks to about 0 because w can fall to 0. Not tested.

## What didn't work
- A readout at guess RT − ndt (lag ≈ 0.42–0.45 s) barely helps (counterfactual report). The lag must be short (about 0.1 s).
- w = 1 matches the fast pulse effect but costs heavily in choice; an all-informed guess process is ruled out at fixed parameters.

## How to reproduce
```
OPENBLAS_NUM_THREADS=1 .venv/bin/python -m tests.test_informed_guesses
OPENBLAS_NUM_THREADS=1 .venv/bin/python -W ignore -m scripts.paper.informed_guess_profile --output <new dir>
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=8 .venv/bin/python -W ignore -m scripts.paper.informed_guess_recovery --output <new dir>
.venv/bin/python -m scripts.slurm.make_task_table --informed   # draft table, not submitted
```
Inputs: ddm/ddm_inputs_global_ucla_nofreeze.npz; fits from ddm/fits_pulse_norm_ugm (L1U1V0Z0G1).

## Caveats
- Profile: 2 seeds, 4 mice, other parameters fixed. Recovery: one mouse, 2 datasets per truth, 2 free parameters only.
  The full family has 10 free parameters, so identifiability of w can only be worse.
- read_lag is not interpretable. Only w is used in the mechanism rule.

## Open questions and next steps
- [ ] Author: go or no-go on stage 3. The draft table scripts/slurm/tasks_2026-11-24_informed.csv has 60 fits,
      303.5 h requested (est 157.5 h). It is independent of the pending transient fits and can run alongside them.
- [ ] After the fits: score with 5 seeds and evaluate the criteria in the plan (rules 1-6).
- [ ] Commit src/ddm, fit script, tests, scripts and table in small packets when the author asks.
