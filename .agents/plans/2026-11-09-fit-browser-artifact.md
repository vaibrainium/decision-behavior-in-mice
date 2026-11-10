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
- 2026-11-09: v2 (author: "fit the psychometric function to data and model ... (use 100 coh if no pulse at that). Also,
  plot correct and incorrect rt distribution"). All coherences incl. +-100% (symmetric cells; models re-simulated, 30
  reps). Psychometric fit per condition: P(right) = gl + (1-gl-gr) Phi((c-mu)/sigma), ML; lapses fitted on control and
  shared; bias = -mu; data CIs from 200 binomial bootstrap resamples. Pulse trials at +-100% exist only with the pulse
  against the motion, so each pulse condition borrows the control trials at the missing +-100% end (without this the
  late slopes were sigma 78-88, CI up to 126; with it 48-52). RT: defective densities, correct/error, 0% excluded.
  Checks: NLL table identical to v1; pooled data biases control -1.08, early L/R -6.40/+18.41, middle L/R -3.82/+9.21,
  late L/R -1.2/+9.7; RT densities integrate to 1.000 (data and models); no sigma at bound; script syntax OK.
  Same URL (version 2). Data JSON: dissemination/figures/qc/fit_browser_2026-11-09_v2.json (v1 kept). Build: 6 min.
- 2026-11-10: v3 (author: "use my psychometric fit method"). Psychometric fits now call
  src/utils/pmf_utils.fit_psychometric_function(model_type="logit_4", default bounds; config/main.yaml psych_model):
  lapse + (1-guess-lapse)/(1+exp(-beta(c-mean))), WLS on proportions with weights sqrt(n), each condition fitted alone
  with 4 free parameters (no shared lapses). Borrowed control +-100% end kept. Bootstrap: 200 binomial resamples refit
  the same way. Checks: pooled control fit equals a direct call on the summary rows (mean 1.161, beta 0.051, lapse
  0.147, guess 0.120); NLL and RT data identical to v2; 0 failed fits; syntax OK. Caveat shown on the page: with 4 free
  parameters, late-pulse and single-mouse fits are poorly constrained (lapse/guess trade off with mean; e.g. pooled late
  left guess 0.27, mean -17.7, CI -34 to -4). JSON: fit_browser_2026-11-10_v3.json. Same URL, version 3.
