# Report: free pulse weight in the joint control + pulse fit
Date: 2026-10-30   Agent: Claude (Opus 5.5)   Commit: see git log for this file (script scripts/ddm/compare_pulse_weight.py)
Plan: plans/2026-10-29-pulse-weight-joint.md

## Question
Every DDM family (and every race/LCA variant) under-predicts the pulse choice effect. Does one extra free weight on the
pulse component (w; w = 1 is the joint model), fitted jointly with all other parameters on control + pulse trials, take
the pulse up, and does it predict held-out trials better? With sv (primary, L0U0V1Z0G1) and without (L0U0V0Z0G1).

## Summary
No. The fitted weight stays at ~1 (median 1.00 with sv, 1.01 without, all-trial fits), and the extra parameter does not
improve held-out NLL in any mouse (no mouse better by 10; Holm p 0.32 / 0.64). An NLL profile over w shows this is the
likelihood, not the optimizer: flat within Monte Carlo noise up to w ~2-3, then worse. Fitted to choices and RTs together,
the data do not ask for a stronger pulse. Confident (VERIFIED for these models, 10 mice).

## Findings
- Held-out NLL, pulse-weight minus joint, summed over cv0-cv4 per mouse (mice as unit; Wilcoxon signed-rank; Holm over the
  3 tests in the summary file). VERIFIED. Source: dissemination/figures/qc/pulse_weight_{heldout,summary}_2026-10-30.csv,
  `.venv/bin/python -m scripts.ddm.compare_pulse_weight`.
  - with sv: sum +14.8, median +0.4; better by >10 in 0/10 mice, worse by >10 in 1/10 (DBM15 +10.0); p = 0.32, Holm 0.64.
  - no sv: sum +8.8, median +1.0; 0/10 better, 0/10 worse by >10; p = 0.11, Holm 0.32.
  - Monte Carlo noise of held-out NLL is ~10 per mouse at 15 reps, so all differences are at noise level.
- Fitted w, all-trial fits: 16/20 within 1.00-1.05. Exceptions: sv DBM13 1.33; no-sv PSUIM5 1.64, PSUIM6 1.34, PSUIM10 4.55
  (425 trials). Fold-wise medians are 1.00-1.09 except no-sv PSUIM5 1.50, PSUIM10 2.77 and sv PSUIM10 5.31 (fold range
  1.0-7.9: unstable in the smallest mouse). VERIFIED. Source: pulse_weight_parameters_2026-10-30.csv.
- Other parameters (drift_gain, sv, a) move by <2% from the joint fits. VERIFIED (session readout of the all-trial fits; same
  values in pulse_weight_parameters_2026-10-30.csv vs fits_joint_unfreeze_integrators).
- NLL profile over w, other parameters held at the pulse-weight all-trial fit, eval seed (scratchpad script
  pw/profile_w.py, not committed; numbers in the plan log): DBM6 and PSUIM6 flat for w 0.5-3 then rising (+20 to +110 at 4-6);
  PSUIM7 already +45 (sv) at w = 2 and +330 at 4; no-sv PSUIM6 minimum near 1.5 (-7 vs w = 1, noise level). VERIFIED.
- sv vs no-sv with the weight free: no-sv minus sv held-out sum +311 (dominated by PSUIM7, +290), median +4.8; sv better by
  >10 in 3 mice, no-sv better by >10 in 2; p = 0.43, Holm 0.64. The weight does not change the D005 picture. VERIFIED.
- Simulated pulse signatures were not rerun: with w ~1 the fits are the joint fits, whose predictions are in
  reports/2026-10-29-joint-control-pulse-refits.md (0.3-1.2 s effect 2.3-4.5 pp vs 5.48 in the data). SUSPECTED identical
  for the 16/20 fits with w <= 1.05; not checked for the four exceptions.

## What didn't work
- First Hyak run (42579333) lost all 100 cv fits: heldout_nll called stimulus.shape on the two-channel tuple after each fit.
  The smoke test used split "all", which skips that path. Fixed (4940d67); reran as 42591827.
- First resubmit exited silently: `ls` with no match under `set -euo pipefail`. Fixed (1ec65e4).
- Local CPU fitting is ~100x slower than Hyak GPU; do not fit here.

## How to reproduce
Fits: Hyak, scripts/slurm/submit_pulse_weight.sh (all + cv, jobs 42579333 tasks 100-119 and 42591827 tasks 0-99), inputs
ddm/ddm_inputs_global_ucla_nofreeze.npz (md5 f18e0e6b...), warm start ddm/fits_joint_unfreeze_integrators, out
ddm/fits_joint_unfreeze_pulse_weight. Comparison: `.venv/bin/python -m scripts.ddm.compare_pulse_weight`.

## Caveats
- One shared weight across pulse times; per-pulse-time weights not fitted.
- The likelihood is dominated by RT quantiles; a choice-only objective wants w ~2.3x larger (tau pilot,
  reports/2026-10-23-pulse-tau-pilot-*.md). The conflict is between the choice effect and the RT distributions.
- 10 mice; the comparison has little power for effects below the ~10 NLL noise per mouse.

## Open questions and next steps
- [ ] Author decision (plan step 4): per-pulse-time weights now look unlikely to help (a shared weight is not wanted);
      recommend stop.
- [ ] Which part of the pulse-trial RT distribution pushes w back to 1? Per-condition NLL decomposition (choice vs RT
      bins) at w = 1 vs 2 in PSUIM7 would show it.
- [ ] Re-examine the data side: is the 5.48 pp window effect robust to the stage pooling and to the pulse-time mix?
