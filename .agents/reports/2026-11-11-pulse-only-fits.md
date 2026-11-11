# Report: models fitted to pulse trials only
Date: 2026-11-11   Agent: Claude (Opus 5.5)   Commit: 325e206 (+ this report's commit)
Plan: plans/2026-11-10-pulse-only-fits.md

## Question
Author 2026-11-10: none of the all-trial models is satisfactory for the pulse. Can each family reproduce the pulse
behaviour when it is fitted to pulse trials only (not also constrained by controls)? Plan's reading, fixed before
results: still missing -> structural; captured but parameters / control prediction differ -> control-pulse tension.
EXPLORATORY, descriptive; no decision rules.

## Summary
- Fitting pulse trials alone does not fix the pulse misfit. The per-mouse spread of the early effect stays unexplained
  (chi-square 91-140 on 10 df, as for all-trial fits 100-143), and with sv the late reversal remains (-1.0 to -2.9 pp
  vs data +1.2). By the plan's reading these are structural for these families, not a control-vs-pulse tension.
- The early mean effect rises a little (4.2-5.2 pp with sv vs 3.1-4.2 all-trial), inside the data CI (3.2-7.9).
- Without sv, pulse-only fits match both window means (early 3.8-5.1, late +0.7 to +1.2; data 5.5 and 1.2) but have
  worse held-out NLL on pulse trials in every pair (+25 to +68, carried by 1-3 mice) and predict controls worse
  (+159 to +587).
- Pulse-trial parameters differ consistently from all-trial ones: longer non-decision time (ndt higher in 6-9/10 mice
  per family) and more fast guesses (p_guess higher in 5-8/10). Moderately confident (descriptive, 10 mice).

## Findings
Fits: 960 (linear and power x primary / leak / urgency / leak+urgency, each with and without sv; splits pcv0-pcv4 +
pulse), ddm/fits_pulse_{linear,power}_integrators, all present and valid (25 resumed from checkpoints).
1. VERIFIED, pulse effect (pulse_effect_bootstrap_2026-11-11_pulseonly_models.csv; data CSV same stem; |coh| <= 36,
   symmetric cells, 30 simulation reps; data mean over mice early 5.48 [3.17, 7.87], late 1.22 [-1.02, 3.36], trial
   bootstrap):
   - with sv (8 families): early 4.22-5.23, chi-square over mice 103-140; late -2.86 to -1.00, chi-square 22.0-39.7
     (p <= 0.015); late mean outside the data CI for 7 of 8 (pulse_linear_urgency -1.00 just inside).
   - no sv (8 families): early 3.80-5.07, chi-square 91-109; late +0.74 to +1.20, chi-square 18.2-20.7 (p 0.024-0.051),
     all inside the data CI.
   - all-trial fits from the same run, for comparison: early 3.08-4.20 (chi-square 100-143), late -1.07 to -2.80.
2. VERIFIED, NLL (pulse_only_nll_2026-11-11.csv; compare_pulse_only.py). Held-out (pcv0-pcv4, 11,479 pulse trials,
   10 mice): range 16,899 (linear leak+urgency) to 16,994 (power leak, no sv); vs pulse_linear_primary 16,933 the
   with-sv families lie within -34 to +9 (0-2 mice better by > 10). No-sv minus sv (pulse_only_sv_pairs_2026-11-11.csv):
   +24.8 to +68.1 held-out (0-2 mice better, 1-3 worse by 10); control trials predicted: +158.8 to +586.8.
3. VERIFIED, parameters (pulse_only_params_2026-11-11.csv; pulse-only vs all-trial fit, same mouse / mapping /
   variant, 9 families with a joint counterpart): ndt median 0.11-0.36 -> 0.18-0.34 s, higher in 6-9/10 mice;
   p_guess higher in 5-8/10; drift_offset higher in 5-7/10 (medians near 0, ratios not meaningful). sv, a, drift_gain
   without a consistent direction.
4. VERIFIED: held-out and fitted NLL are not on one scale: per trial, the fitted NLL is 0.7-2.9 and the held-out sum
   0.6-2.4 for the same trials, in pulse-only and joint fits alike (the quantile objective's value per trial depends on
   cell sizes). So the pulse-only held-out NLL is not comparable with the control-only fits' pulse-trial NLL either.
5. SUSPECTED (not tested): longer ndt / more guesses on pulse trials could reflect a slower or less engaged state on
   pulse trials, or the models absorbing a pulse-locked RT effect they cannot produce otherwise.

## What didn't work
- Nothing failed. Note for the next agent: never regenerate a committed task table (indices shifted under a running
  batch on 2026-11-10; restored; see the plan log).

## How to reproduce
- Simulations: `python -m scripts.ddm.build_fit_browser --cache <sim_full> --sim_only --families <pulse_* families>`
  then `--tag _v4 --html <out>` (fit_browser_2026-11-11_v4.json); `python -m scripts.ddm.pulse_joint_signatures --cache
  <sig cache, |coh|<=36> --families <4 pulse_* each> --tag _po_part{0..3}`; `python -m scripts.ddm.pulse_effect_bootstrap
  --runs <MODEL_RUNS> pulse_joint_signatures_2026-11-11_po_part{0..3} --tag _pulseonly`; `python -m
  scripts.ddm.compare_pulse_only`.
- Inputs: ddm_inputs_global_ucla_nofreeze.npz (responded trials), pulse_timing_global.npz.

## Caveats
- One fit per mouse and family (no parameter uncertainty in the predictions); simulation noise approximated as in the
  bootstrap report (data variance / 30).
- Pulse trials are 45% of trials (166-2,740 per mouse); small mice dominate the chi-square noise.
- Many families and two windows; p values descriptive.

## Open questions and next steps
- [ ] The per-mouse early-effect spread is not explained by any family, now including pulse-only fits: look at what
      differs between mice (pulse timing, coherence mix, per-mouse parameters; rig as a covariate only).
- [ ] sv buys RT fit (likelihood) but produces the late reversal; no-sv matches the pulse means but fits RTs worse. A
      different form of across-trial variability (e.g. starting point, bounded sv) is the open option; needs fits.
- [ ] Why ndt and guesses are larger on pulse trials (finding 5).
