# Plan: power of a fluctuation-kernel test of temporal weighting (synthetic only)
Status: active
Created: 2026-10-25 by Claude (Opus 5.5)
Related: analysis log 5.13 (amendment 7 stopped); finding 2026-10-25: ~43% of motion-energy noise varies within trials

## Goal
Decide, from simulations only (no recorded choices), whether reverse correlation on within-trial motion-energy
fluctuations could detect primacy (drift-gain decay) and separate integration from extrema detection with these
trials. If yes, draft amendment 8; if not, stop.

## Design (fixed before running)
- Trials: control trials, |coh| ≤ 36%, responded (0.3–5 s), all 10 mice; stimuli = each trial's own motion energy.
- Fluctuation f(t) = N(t) − mean of N over frames 10–299 (removes the fixed per-trial bias), 60 Hz frames.
- Kernel per mouse: mean f(t) for rightward minus leftward choices, 100 ms bins from 0.1 to 0.9 s after onset,
  using only frames before the response.
- Reference: the same kernel on choices simulated from the flat-weighting model (fits_final control fit, primary
  model), 10 simulated datasets averaged.
- Statistic per mouse: primacy index = (mean over bins 0.1–0.4 s) − (mean over 0.5–0.9 s) of K_obs − K_ref
  (% coherence; > 0 = primacy); group test = mean over mice, t-test across mice (df 9), two-sided 95%.
  (Changed 2026-10-25 before the power run: the ratio b = d/c was unstable when the reference kernel is small.)
- Power: synthetic "observed" datasets from the same model with gain decay 0 (null), 20% and 40% over 0.5 s, 20 each.
  Report false positives at 0 and detection at 20/40%.
- Integration vs extrema (secondary): response-aligned kernels from the integrator and E simulations, compared in shape.

## Steps
- [x] 1. `scripts/ddm/fluctuation_kernel.py` (synthetic mode only; real-data mode refuses without --unblind).
- [x] 2. Run power simulation; record.
- [x] 3. Power of the response-aligned test, integrator vs extrema detection (design below, fixed before running).
- [ ] 4. Decide with the authors: amendment 8 (response-aligned test only) or stop.

## Design, step 3 (added 2026-10-25, before running; V. Thakur agreed)
- Same trials, fluctuation and response-aligned bins (-0.6..0 s, 100 ms, frames before the response and >= 0.1 s after onset).
- Late-weight index per mouse = mean of the kernel over the last two bins (-0.2..0 s) minus the mean over the first two (-0.6..-0.4 s), % coh.
- Generators: the integrator (fits_final control fit, primary model) and E (fits_guess_fast_only_leak20-200 control fit);
  20 synthetic datasets of each, one per mouse each time, at the real trial counts and stimuli.
- Predictions: each model's index per mouse from 10 separate simulated reps (different seeds from the datasets).
- Classification per dataset: sum over mice of (index - pred_I)^2 vs (index - pred_E)^2; the smaller one wins.
  Report the correct-classification rate for each generator.
- Also the group sign test: t-test across mice of the index vs 0; report how often it is significant (> 0) under I and (< 0) under E.
- Success criterion for drafting amendment 8: >= 90% correct classification under both generators.

## Log
- 2026-10-25: plan written (V. Thakur agreed to the power check).
- 2026-10-25: power run finished (`python -m scripts.ddm.fluctuation_kernel --power --datasets 20 --ref_reps 10`, commit cf6add0 + this script;
  output /mnt/data/processed/ddm/fluctuation_kernel_power.csv, 600 rows). Synthetic only, no recorded choices.
  Primacy index (mean over mice; SD across the 20 datasets of that mean): decay 0: -0.081 (0.162); 20%: -0.042 (0.145);
  40%: +0.014 (0.205). Group detection of primacy: 0% / 5% / 0%; any departure 0% / 10% / 5%. Per-mouse SD of the index
  is ~0.5-0.66 % coh, while 40% decay shifts the mean by ~0.1 % coh. The whole reference kernel is only ~0.1-0.4 % coh
  (fluctuation SD 5-6 % coh), so choices carry almost no information about the fluctuations. VERDICT: no power for temporal weighting.
  Secondary (mean over mice of 10 simulated reps, not a per-dataset power test): response-aligned kernels separate in
  shape. Integrator [0.22, 0.25, 0.36, 0.47, 0.58, 0.46] rises toward the response; E [0.75, 0.76, 0.58, 0.30, 0.10, -0.00]
  is ~0 in the last 200 ms (bins -0.6..0 s). Whether this survives single-dataset noise is untested.
- 2026-10-25: step 3 done. Classification 20/20 correct under both generators (criterion met); per mouse reliable only in
  PSUIM6/7. Report: reports/2026-10-25-fluctuation-kernel-power.md. Next: step 4 (author decision).
