# Plan: free pulse weight in the joint fit (then LCA illustration)
Status: active
Created: 2026-10-29 by Claude (Opus 5.5)
Related reports: reports/2026-10-29-joint-control-pulse-refits.md (incl. sv addendum),
reports/2026-10-23-pulse-tau-pilot-20261023T191030Z_fa8de8b.md (w_choice / w_joint = 2.33 with control-only parameters)

## Goal
Find out whether one extra weight on the pulse component, fitted jointly with every other parameter (sv free) on control +
pulse trials, reproduces both the choice effect (0.3-1.2 s window 5.48 pp, no late reversal) and the toward-pulse RT shift
(-60 ms). If yes: per-pulse-time weights next (author's question). If no: the pulse-amplification route is in trouble.

## Context
- All 12 families under-predict the pulse effect (2.3-4.5 pp); sv attenuates it and creates the late reversal; without
  sv the fit lowers drift_gain instead. Single gain pinned by coherence is the bottleneck (SUSPECTED).
- tau pilot: with parameters fixed at control-only fits, the choice-matched weight was 2.33x the choice+RT weight.

## Assumptions
- Three dense mice (PSUIM6, PSUIM7, DBM6; rig as covariate only) are enough for a go/no-go check.
- Split "all" only: train NLL vs the joint primary fit (nested at w = 1; warm start reproduces it) with 1 extra parameter;
  ~10 NLL Monte Carlo noise at 15 reps.

## Steps
- [x] 1. fit_mouse_ddm --pulse_weight: free noise_weight in [0, 20] on the pulse component (two-channel input);
      check w = 1 equals the single-channel input (max diff 1.2e-7) and controls carry no pulse component.
- [ ] 2. Fit locally: PSUIM6, PSUIM7, DBM6, L0U0V1Z0G1, split all, 15 reps, warm start from
      ddm/fits_joint_unfreeze_integrators, out ddm/fits_joint_unfreeze_pulse_weight.
- [ ] 3. Read out: fitted w, sv, drift_gain vs the joint fit; delta train NLL; simulate (pulse_joint_signatures
      statistics) the 0.3-1.2 / 1.2-5 s effects and the toward-pulse RT shift vs data.
- [ ] 4. Decide (author): per-pulse-time weights, or stop.
- [x] 5. LCA illustration (author asked 2026-10-29): two accumulators with leak, inhibition, noise correlation; check it
      equals the DDM in the limit; roughly matched to control trials in the same mice; pulse signatures vs data.
- [ ] 3b. Comparison (author, 2026-10-29): same fit without sv (L0U0V0Z0G1 --pulse_weight, free guess bias, warm start
      from the joint no-sv fit), same mice, same out dir.
- [ ] 6. Report addendum; STATUS.

## Out of scope
Hyak runs, CV over all mice (only if step 3 is promising).

## Log
- 2026-10-29: author approved step 1-3 ("ok"); asked to add LCA families (step 5, after the weight check).
- 2026-10-29: author asked for the no-sv comparison now ("start this now"); started 3 fits alongside the sv runs (CPU shared, both slower).
- 2026-10-29: local fits stopped after ~1 h: CPU-only here, 20-50 min per optimizer iteration (Hyak jobs have a GPU;
  joint fits ran 114-226 iterations in ~1 h). No output written. Moved to Hyak and widened to all 10 mice, cv0-cv4 + all,
  sv and no-sv (120 jobs): scripts/slurm/submit_pulse_weight.sh. Steps 2 and 3b now = that array; step 3 adds held-out
  NLL vs the joint fits (same folds).
- 2026-10-29: submitted by the author on Hyak (HEAD ee2995b): PW_pulse_weight 42579333 (0-119). Next: pull, step 3 readout.
- 2026-10-29: author OK'd the LCA illustration while the Hyak array runs (step 5 brought forward): scripts/ddm/pulse_lca_signatures.py; DDM-limit check 2000/2000 trials identical in each of PSUIM6, PSUIM7, DBM6. Full run started.
- 2026-10-29: step 5 done (two runs; second adds baseline-input LCAs after the author shared Kirkpatrick et al. 2021, and fixes a x100 print bug): no race/LCA variant exceeds 5.1 pp vs 13.1 in data -> reports/2026-10-29-pulse-race-lca-illustration.md.
- 2026-10-30: 42579333 returned only the 20 "all" fits: every cv task (0-99) crashed in heldout_nll after fitting
  (stimulus.shape on the two-channel tuple; my bug, not caught by the smoke test, which used split all). Fixed in 4940d67
  (pushed); rerun with `bash scripts/slurm/submit_pulse_weight.sh --cv` (tasks 0-99; "all" outputs untouched).
  "All" fits: w stays ~1 (16/20 within 1.05; sv DBM13 1.33; no-sv PSUIM5 1.65, PSUIM6 1.34, PSUIM10 4.5 at n=425); train NLL vs joint
  -0.0 to -7.3, no mouse beyond 10. NLL profile over w (other params fixed, eval seed, scratchpad pw/profile_w.py):
  flat within MC noise for w 0.5-3 in DBM6/PSUIM6, rises from w=4; PSUIM7 rises from w=2 (+45 at 2, +330 at 4).
  Optimizer not stuck: the joint likelihood does not support amplifying the pulse.
