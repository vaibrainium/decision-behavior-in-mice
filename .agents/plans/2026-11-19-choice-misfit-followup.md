# Plan: Follow up the held-out choice misfit
Status: active
Created: 2026-11-19 by Claude (Opus 5.5)
Related reports: reports/2026-11-19-choice-rt-weighting.md, reports/2026-11-19-choice-g2-all-families.md

## Goal
Know whether the choice excess is pulse-specific, structural (sv, front end, lapse) or mouse-driven, and rescore all families on bins that give RT a fair out-of-sample test.

## Context
The likelihood is correct. Held-out pulse choice excess is 287–506 G² across families. sv is the main driver. The power front end fixes the mean slope but not the excess. Only 34% of held-out pulse trials get an RT term at nbins=9.

## Assumptions
- Saved CV fit pickles and the processed NPZ (SHA in the 11-17 audit) are current.

## Steps
- [x] 1. G² test on all 22 pulse-only families, with and without PSUIM7 (saved cells; report choice-g2-all-families).
- [ ] 2. Same test on control held-out folds and on training (full) fits at an independent seed. Needs a control version of scripts/paper/audit_pulse_choice_rt_score.py. CPU, minutes.
- [ ] 3. guess_lapse on norm UGM no sv: needs new pulse CV fits on Hyak. Author approval required.
- [ ] 4. Decompose the excess (per-mouse × |coh| slope, pulse direction, fold).
- [ ] 5. Adaptive bins (5 if n ≥ 25, 2 if 8–24, otherwise count only). Rescore all families together at ≥3 seeds. Re-simulation, CPU/GPU.
- [ ] 6. Verify: reproduce native totals (atol 1e-8) before applying new bins. Seed SD reported next to every ranking difference.

## Out of scope
Refitting existing families; changing rt_nllh_weight for final fits.

## Log
- 2026-11-19: The power front end was tested from saved all_candidates cells, without new fits. The GLM-HMM for PSUIM7 already exists (2026-11-15 pilot), so it is not repeated.
