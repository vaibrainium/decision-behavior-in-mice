# Plan: interactive fit browser (artifact) for all fitted model families
Status: done
Created: 2026-11-09 by Claude (Opus 5.5)
Related reports: reports/2026-11-09-mapping-accumulator-exploratory.md, reports/2026-11-09-pulse-effect-bootstrap.md

## Goal
Author request 2026-11-09: a page with one tab per model family (control-only fits, joint all-trial fits, every
variation), each showing data vs model split by condition (control; early/middle/late x left/right pulse), first pooled
over mice, then per mouse; plus a tab with the actual negative log likelihoods (held-out and fitted). For the author's
own comparison; decisions later. Descriptive only.

## Context
- Model simulations: pulse_joint_signatures.simulate (30 reps, seed 0, the mouse's own responded trials, |coh| <= 36,
  symmetric cells), cached; counterfactual sv = 0 runs via --override.
- Conventions (checked 2026-11-09): coh > 0 and pulse sign +1 = rightward (P(right) 0.68 vs 0.37; 0.60 vs 0.49).
- NLL: the fitting objective (censored quantile QMLE, 9 bins, responded trials), from the fit pickles.

## Assumptions
- Psychometric (P right vs signed coherence) and chronometric (mean RT vs signed coherence) are the "functions".
- Coherences +-100% are not shown (simulations cover |coh| <= 36, where all pulse trials are).

## Steps
- [x] 1. Simulate missing families (no_sv, no_guess, fixed_guess_bias, free_leak_0-200, stine_nominal_DDM/ES, norm
      control-only) into the cache.
- [x] 2. scripts/ddm/build_fit_browser.py: per family x (pooled, mouse) x condition x coherence: n, P(right), mean RT
      with SEs, for data and model; NLL table (held-out cv0-cv4 sum, fitted "all", control-only test on pulse trials);
      writes JSON + HTML from a template.
- [x] 3. Publish the artifact; commit script, template and JSON.
- [x] 4. Verify: aggregate numbers spot-checked against the windows/summary CSVs; NLL totals against
      mapping_accumulator_heldout_nll_2026-11-09_final.csv.

## Out of scope
New fits; interpretation.

## Log
- 2026-11-09: plan written.
- 2026-11-09: built (python -m scripts.ddm.build_fit_browser --cache <sim cache> --html <out>; 45 s) and published:
  https://claude.ai/artifact/QrrEoVZa3dKgSSETBhf7S2 (private). 43 families (3 control-only, 32 joint, 8 sv = 0
  counterfactuals). Checks: held-out totals equal mapping_accumulator_heldout_nll_2026-11-09_final.csv (5 families
  compared exactly); n held-out 25,493 for all 32 joint families; control-only pulse test n 11,479; page script passes
  a syntax check. Data JSON: dissemination/figures/qc/fit_browser_2026-11-09.json.
