# Plan: literature follow-ups (Brunton/Piet/Molano), items 1, 5, 6
Status: done
Created: 2026-11-24 by Claude (Opus 5.5)
Related reports: reports/2026-11-24-lit-brunton-piet-molano.md, reports/2026-11-24-lit-followups-results.md

## Goal
(1) Narrow the Brunton citation in the locked spine. (5) Calibrate the descriptive Figure 4D exponential (τ = 1.11 s) against simulated accumulators with known leak, so the paper can say what τ does or doesn't tell us about leak. (6) Quantify how much early-pulse gain the fitted divisive front end produces at early, middle and late pulse onsets, per mouse, and compare it descriptively with the observed per-mouse stage pattern.

## Context
- Figure 4D readout: scripts/ddm/pulse_dynamics_bridge.py (frame/aggregate/readout, exact historical selection; cache/metadata.pkl). Exponential: scripts/paper/preview_pulse_exponential.py fit_exp, fixed observed bin coordinates (pulse_exponential_preview_2026-11-18/observations.csv).
- The zero-leak no-sv joint integrator already gives a declining γT (early 7.51, late 2.14; pulse_dynamics RESULTS.md).
- Norm front end: x' = x / (1 + fe_beta·p), p a causal LP of |x| starting at 0 (src/ddm/simulator.py front_end_numpy). Fits: pulse_norm_ugm_no_sv.

## Assumptions
- Fixing every other parameter and changing only leak_rate is a fair "known-leak agent" (Piet 2018, Fig. 3c–d). Accuracy changes with leak; the γ = D/slope normalization partly absorbs this.
- One readout per simulated rep has the same trial count as the real data, so the spread across reps approximates readout sampling variability at data size. It does not include mouse resampling.

## Steps
- [x] 1. Spine reworded, D011 logged, lock-spine re-run (hash b3630df9343a6a67), check-spine OK.
- [x] 2. Script scripts/paper/leak_readout_calibration.py. Bases 'no_sv' and 'primary' (joint fits). leak_rate ∈ {0, 0.5, 1, 2, 5, 10, 20} /s. 10 mice × 30 reps × seeds 0, 1. Exact bridge readout plus fit_exp on pooled and per-rep γT. New output dir dissemination/paper_accumulation/draft_2026-11-15/leak_readout_calibration_2026-11-24/.
- [x] 3. Checks: the leak = 0 no_sv pooled readout reproduces the existing bridge readout (within simulation seeds). The leak override reaches the simulator (accuracy changes).
- [x] 4. Script scripts/paper/front_end_onset_gain.py. Per mouse and pulse stage, the gain 1/(1 + fe_beta·p) just before pulse onset, from pulse_norm_ugm_no_sv fit parameters on that mouse's actual inputs. Join with the observed per-mouse early/middle effects from pulse_onset_diagnosis mouse.csv. Spearman correlation across mice, descriptive only.
- [x] 4b. Guess-readout counterfactual (author "yes" 2026-11-24): scripts/paper/guess_readout_counterfactual.py. Fixed fits (pulse_norm_ugm_no_sv, no_sv, primary); guess trials keep their RTs but report the DV side at guess time (midpoint / start-point versions) instead of a coin flip; paired draws; per-mouse pulse effects by RT window, fast control accuracy guardrail, gammaT readout. Output guess_readout_counterfactual_2026-11-24/.
- [x] 5. Report and STATUS update.

## Out of scope
Refits, Hyak jobs, figure changes, manuscript text changes beyond the spine.

## Log
- 2026-11-24: Author "yes" to items 1, 5, 6 of the lit report.
- 2026-11-24: Item 6 done (front_end_onset_gain_2026-11-24). First output measured gain at the logged onset, which lies before the filter-delayed pulse motion energy (gain exactly 1); deleted unreported and replaced by a pulse-ME-weighted gain. Early/middle gain ratio 1.05-1.57; PSUIM6/7 deficit is amplitude at both stages.
- 2026-11-24: Author asked which modeling from the papers is usable; guess-readout (Molano action initiation) counterfactual added as step 4b. Smoke test (2 reps): exact kernel equality passed; PSUIM7 coin model already matches data at 0.6-1.0 s, so RT windows split further.
- 2026-11-24: 4b done (guess_readout_counterfactual_2026-11-24, plus _lag0.1s/_lag0.2s with --read-lag, pulse_norm_ugm_no_sv only). Reading DV at guess RT - ndt adds little (PSUIM7 early all-RT 11.4 -> 14.8 vs data 25.1). With a 0.1 s readout lag (Molano structure) PSUIM7 early reaches 21.3 (fast window 27.7 vs data 25.1) and fast 100%-coherence control accuracy 79.0 vs data 78.9, but intermediate coherences overshoot (62-68 vs 48-57). PSUIM6 gains less (7.9 vs 17.5; p_guess 0.13). Other mice: fast responses evidence-blind in data, readout overshoots equal-mouse fast accuracy and fast pulse effect. 1-5 s window gap unchanged. Fixed parameters fitted under coin-flip guesses: existence demonstration, not a model test; a fit family needs author approval.
- 2026-11-24: Item 5 done (leak_readout_calibration_2026-11-24). Zero-leak no_sv reproduces bridge within seeds. Leak 0-2 /s gives readout tau 0.80-0.50 s, all compatible with the data interval; leak >= 5 /s at fixed parameters collapses responding (>= 73% non-response), not calibratable without refits. Plan closed; report reports/2026-11-24-lit-followups-results.md.
