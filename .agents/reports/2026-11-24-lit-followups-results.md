# Report: literature follow-ups — Figure 4D leak calibration, front-end onset gain, guess-readout counterfactual
Date: 2026-11-24   Agent: Claude (Opus 5.5)   Commit: 886d3d1 (new scripts and outputs uncommitted)
Plan: plans/2026-11-24-lit-followups.md   Background: reports/2026-11-24-lit-brunton-piet-molano.md

## Question
(5) Does the descriptive Figure 4D exponential (τ = 1.11 s, mouse-bootstrap 95% 0.45–3.73 s) say anything about leak? (6) Does the fitted divisive front end (a Brunton-style adaptation) explain the onset-stage pattern? (4b) Would fast responses that read the decision variable (Molano-Mazón 2024) supply the missing PSUIM6/7 pulse amplitude?

## Summary
Item 1: the spine Brunton citation was narrowed (D011; re-locked hash b3630df9343a6a67).

The Figure 4D τ does not identify leak. A zero-leak accumulator already gives a readout τ of about 0.8 s, and leak from 0 to 2 /s moves it only to about 0.5 s. At data size, every leak in that range is compatible with the observed interval. Higher leak at fixed other parameters makes the models stop responding, so it can't be calibrated without refits.

The front end gives early pulses only 1.05–1.57× the gain of middle pulses. The PSUIM6/7 deficit is overall amplitude, not onset weighting.

The strongest lead is fast responses. With fixed fitted parameters, letting guesses read the decision variable with a 0.1 s lag moves PSUIM7's early-pulse effect from 11.4 to 21.3 pp (data 25.1), and matches its fast 100%-coherence accuracy (79.0 vs 78.9%). It overshoots mice whose fast responses are evidence-blind, and helps PSUIM6 less. This shows the mechanism can work; it is not a model test.

## Findings
- VERIFIED (5): no_sv joint base (L0U0V0Z0G1) with leak fixed at 0 / 0.5 / 1 / 2 /s:
  - Pooled readout τ, mean of 2 seeds: 0.80 / 0.68 / 0.63 / 0.50 s. Early K about 7.9 throughout.
  - Per-rep (data-size dataset) 95% τ ranges are wide, e.g. 0.30–10.5 s at zero leak.
  - Share of reps with τ inside the data interval: 0.73 / 0.57 / 0.63 / 0.38.
  - Zero-leak consistency with the bridge: K 7.56–8.21 and late 2.26, vs 7.51 and 2.14 there. A different RNG, so consistent rather than identical.
  - Source: leak_readout_calibration_2026-11-24/summary.csv, pooled_readouts.csv; scripts/paper/leak_readout_calibration.py.
- VERIFIED (5): the primary base (with sv) gives τ 0.29 / 0.24 / 0.21 / 0.17 s and a negative late γT (−5.8 at zero leak). Every rep at every leak has τ at or below the data point. This model's readout declines too fast even without leak, consistent with the late reversal already reported for sv models.
- VERIFIED (5): leak ≥ 5 /s with other parameters fixed gives ≥ 73% simulated non-response (no_sv) and slopes ≈ 0. The readout is undefined or unstable (failures and boundary fits in summary.csv). At 2 /s, non-response is already 46% (no_sv) and 64% (primary). So the range above about 2 /s cannot be calibrated this way.
- VERIFIED (6): pulse-motion-energy-weighted front-end gain, early/middle ratio 1.05–1.57 per mouse (PSUIM7 1.41, PSUIM6 1.14):
  - Observed early/middle: PSUIM7 25.1/13.6 pp, PSUIM6 17.5/11.9. The model, which already contains this gain, gives 11.1/8.3 and 6.6/6.0.
  - Gain ratio against observed early − middle across mice: Spearman ρ = 0.35, p = 0.33 uncorrected, n = 10.
  - Source: front_end_onset_gain_2026-11-24/mouse_comparison.csv, manifest.json.
- VERIFIED (6): the filter-delayed pulse motion energy is above 10% of its maximum from about 100 to 400 ms (early stage). The logged onset is about 50 ms. A gain read at the logged onset is always 1 and is not used.
- VERIFIED (4b): best pulse model pulse_norm_ugm_no_sv, early pulses, 2 seeds × 30 reps, versions paired on all draws. All-RT effect: PSUIM7 coin 11.4 → readout at guess RT − ndt 14.8 → readout lag 0.2 s 19.2 → 0.1 s 21.3 (data 25.1). PSUIM6 5.7 → 6.7 → 7.5 → 7.9 (data 17.5).
  - By RT window, coin model vs data: PSUIM7 0.3–0.6 s 1.6 vs 25.1; 0.6–1.0 s 35.8 vs 37.7; 1–5 s 0.4 vs 8.1.
  - Source: guess_readout_counterfactual{,_lag0.1s,_lag0.2s}_2026-11-24/effects_by_mouse_seedmean.csv.
- VERIFIED (4b): fast (< 0.6 s) control accuracy at 100% coherence is 72% in PSUIM6 (93 trials) and 79% in PSUIM7 (266). The fitted ndt is 0.42 / 0.45 s, so the model can't make stimulus-driven responses before about 0.5 s.
  - With a 0.1 s lag, PSUIM7 100% accuracy is 79.0% (data 78.9), but 18–36% overshoots (62–68 vs 48–57).
  - Equal-mouse fast accuracy overshoots at 9–36% coherence (54–61 vs 42–50). The equal-mouse fast early-pulse effect overshoots too (17.7 vs 4.5).
  - The joint models (no_sv, primary) with readout at guess RT − ndt also overshoot 18% fast accuracy (56–59 vs 42).
- VERIFIED: the counterfactual kernel equals the production _simulate_ddm_trials_numba exactly for DDM outcomes (assert, first mouse).

## What didn't work
- Reading the decision variable at guess RT − full ndt: it barely changes the pulse effect, because the DV has not received the pulse yet.
- Gain at the logged pulse onset, which comes before the pulse's motion energy. Replaced by a pulse-weighted gain; the first output was deleted unreported.

## How to reproduce
From /src with OMP_NUM_THREADS=8 OPENBLAS_NUM_THREADS=1, each into a new directory:
- `.venv/bin/python -m scripts.paper.leak_readout_calibration --output <dir>`
- `.venv/bin/python -m scripts.paper.front_end_onset_gain --output <dir>`
- `.venv/bin/python -m scripts.paper.guess_readout_counterfactual --output <dir> [--families pulse_norm_ugm_no_sv --read-lag 0.1]`

Inputs, fit paths and source hashes are in each manifest.json. CPU only, no fits.

## Caveats
- All parameters were fitted under other assumptions: coin-flip guesses, and the fitted leak. These are counterfactuals, not model comparisons.
- The per-rep τ spread is simulation sampling at data size; it includes neither mouse resampling nor parameter uncertainty.
- Item 6 is descriptive with n = 10.
- PSUIM6/7 are two animals, and the fast-response results rest on 93 and 266 control trials at 100% coherence.
- Mice are not split by rig.

## Open questions and next steps
- [ ] Figure 4D caption/Results (author to approve wording). Suggested: "A bounded accumulator without leak produced a readout τ of about 0.8 s on the same trials, and leak up to 2 /s shortened it only to about 0.5 s, all within the data interval; the exponential therefore summarizes the readout and does not estimate a leak."
- [ ] Candidate fit family (needs author approval, simulator change, new task table): evidence-reading guesses with a free readout lag, or a free informed/blind guess share, per mouse. Check recovery and the control guardrail first.
- [ ] The 1–5 s pulse effect stays under-predicted in every variant (PSUIM7 about 3 vs 8 pp).
- [ ] Transient-channel fits pending (plans/2026-11-20-transient-channel.md).
