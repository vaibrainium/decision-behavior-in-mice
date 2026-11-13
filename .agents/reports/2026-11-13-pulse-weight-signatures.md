# Report: pulse signatures of the existing pulse-weight fits
Date: 2026-11-13   Agent: Claude (Opus 5.5)   Commit: 4226404 (+ uncommitted primacy / pulse_joint_signatures / rescore_fits changes)
Plan: plans/2026-11-12-pulse-weight-signatures.md (done)

## Question
Does a free pulse weight (shared, or per pulse time) close the early-effect gap in PSUIM6 / PSUIM7 (data 15.5 / 13.5
pp in 0.3-1.2 s; earlier models at most ~9)? EXPLORATORY; no new fits.

## Summary
No. Per-time weights roughly double the predicted early effect in PSUIM6 (to 7.5 pp with sv, weight 3.16) and raise
PSUIM7 to 6.5 pp (no sv, weight 2.11), still about half the data. Across mice the best early-window chi2 is 74.6
(pw_per_time_no_sv), worse than normalized UGM without sv (51.3 all-trial, 44.7 pulse-only fit). Rescored BIC is
+274 to +907 vs the best model (power_leak_urgency). Confidence: moderate (one simulation seed per signature; weights
of many fits sit at the seed value 1.0).

## Findings
- VERIFIED. Early (0.3-1.2 s) pulse effect, model vs data (pp): PSUIM6 data 15.5 (CI 12.1-18.8); pw_shared 3.8,
  pw_shared_no_sv 4.6, pw_per_time 7.5, pw_per_time_no_sv 6.9. PSUIM7 data 13.5 (CI 11.3-15.6); 3.7, 4.4, 3.7, 6.5.
  Source: dissemination/figures/qc/pulse_joint_signatures_2026-11-12_pw_windows.csv, pulse_effect_bootstrap_2026-11-12_pw_data.csv.
- VERIFIED. Across 10 mice, early-window chi2 vs data: pw_shared 136.4, pw_shared_no_sv 117.1, pw_per_time 107.9,
  pw_per_time_no_sv 74.6 (control-only primary 146.0); late window (1.2-5 s) 18.2-19.7 for all four. Source:
  pulse_effect_bootstrap_2026-11-12_pw_models.csv; comparison rows from pulse_effect_bootstrap_2026-11-11_ugm_models.csv.
- VERIFIED. Rescored information criteria (all-trial fits; d vs power_leak_urgency): d_BIC pw_shared 274, pw_per_time
  338, pw_shared_no_sv 793, pw_per_time_no_sv 907 (plain primary 194); d_heldout 210, 193, 521, 504 (primary 195);
  seed SD 13-31. Source: model_ic_summary_2026-11-12_rescored.csv (compare_ic with rescored_nll_2026-11-12.csv and
  rescored_nll_2026-11-12_pw.csv).
- VERIFIED. Fitted weights: pw_shared PSUIM6 and PSUIM7 = 1.000, pw_per_time PSUIM7 = 1.000 / 1.000 (identical model to
  pw_shared, hence identical signatures); per-time PSUIM6 3.16 / 1.05 (sv), 2.65 / 1.19 (no sv); PSUIM7 no sv 2.11 /
  0.96. Bounds 0-20, seeded at 1.0 or from earlier fits (fit_mouse_ddm.py:124-127, 334). Consistent with
  reports/2026-10-30-pulse-weight-joint.md and 2026-10-31-pulse-time-weights.md.
- VERIFIED. Full-data bits on early-pulse trials, PSUIM6 / PSUIM7: pw_per_time_no_sv has the highest choice bits
  (153 / 145 mbits vs ~136 / 126 for power_leak_urgency); see reports/2026-11-13-bits-per-trial.md.
- SUSPECTED. Fits with weight exactly 1.000 may not have explored the weight dimension (DE seeded at 1.0, noisy
  objective at 15 reps); the 2026-10-30 NLL profile over w argues the optimum is near 1 for most mice, but PSUIM7 sv was
  not profiled here.

## What didn't work
- Nothing failed; plan step 1 check (rescoring a test fold reproduces stored test NLL) was not run separately; the
  rescore of all-trial fits ran with the same code path.

## How to reproduce
```
.venv/bin/python -m scripts.ddm.pulse_joint_signatures --cache <dir> --tag _pw --families pw_shared pw_shared_no_sv pw_per_time pw_per_time_no_sv
.venv/bin/python -m scripts.ddm.pulse_effect_bootstrap --runs pulse_joint_signatures_2026-11-12_pw --tag _pw
.venv/bin/python -m scripts.ddm.rescore_fits --cache <dir> --families pw_shared pw_shared_no_sv pw_per_time pw_per_time_no_sv --tag _pw
.venv/bin/python -m scripts.ddm.compare_ic --browser dissemination/figures/qc/fit_browser_2026-11-12_v7.json --rescored dissemination/figures/qc/rescored_nll_2026-11-12.csv dissemination/figures/qc/rescored_nll_2026-11-12_pw.csv
```
(Commands as run on 2026-11-12, from the session transcript.) Fits:
fits_joint_unfreeze_pulse_weight, fits_joint_unfreeze_pulse_time_weights, split "all".

## Caveats
- Linear input only (the pulse-weight fits predate power / normalized mappings); a weight on a better-fitting
  accumulator was not tested.
- Mouse is the unit; PSUIM6/7 are 2 of 10 mice (the early-effect heterogeneity: Q = 51.7, df 9, I2 0.83).

## Open questions and next steps
- [ ] If the author wants it: per-time weights on normalized UGM no-sv or power_leak_urgency (new Hyak fits; author submits).
- [ ] Profile the PSUIM7 sv weight to confirm 1.0 is an optimum, not a stuck seed.
