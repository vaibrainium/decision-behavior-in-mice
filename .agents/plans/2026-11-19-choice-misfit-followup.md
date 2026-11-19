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
(author order 2026-11-19: 2, cell-type split (4), sv vs ME spread, guess_lapse decision (3), multi-seed top 3, then adaptive bins (5))
- [x] 1. G² test on all 22 pulse-only families, with and without PSUIM7 (saved cells; report choice-g2-all-families).
- [x] 2. Same test on control held-out folds and on training (full) fits at an independent seed. Needs a control version of scripts/paper/audit_pulse_choice_rt_score.py. CPU, minutes.
- [x] 3. guess_lapse on norm UGM no sv: needs new pulse CV fits on Hyak. NOT queued: 100% cells carry no disproportionate excess (report choice-excess-cell-type-sv).
- [x] 4. Decompose the excess (per-mouse × |coh| slope, pulse direction, fold).
- [x] 4b. Fitted sv vs within-cell ME drift spread (sv 5-35x larger).
- [x] 4c. Rescore the top 3 by total held-out NLL (with and without PSUIM7: power UGM, norm UGM no sv, linear leak, linear leak + urgency) at >= 3 seeds before treating any ordering as a result.
- [x] 4d. Data-only pulse effect vs coherence x timing with hierarchical bootstrap; residual bootstrap (early zero/low coherence) with and without PSUIM6/7.
- [ ] 4e. Gain-decay / signed-leak pulse-only CV fits: table tasks_2026-11-19_pulse_w.csv generated (240 tasks); SUBMITTED 2026-11-19 14:55 (Hyak time) by author, all 10 mice, state slurm-logs/autosubmit_state_pulse_w.json; then rerun the cell split and residual bootstrap on them.
- [x] 4g. RT hazard aligned to pulse onset at 100% coherence (criteria B).
- [ ] 4h. Score PW fits against criteria A once all 240 tasks are done.
- [ ] 4i. Random-effects model comparison across mice.
- [ ] 4f. Control-trained no-sv fits only if the pulse-to-control transfer question still matters after 4e.
- [ ] 5. Adaptive bins (5 if n ≥ 25, 2 if 8–24, otherwise count only). Rescore all families together at ≥3 seeds. Re-simulation, CPU/GPU.
- [ ] 6. Verify: reproduce native totals (atol 1e-8) before applying new bins. Seed SD reported next to every ranking difference.

## Pre-registered criteria (author, 2026-11-19; written before any PW fit or RT-alignment result was seen)

### A. Scoring the PW fits (gain decay, signed leak) against their constant-gain counterparts
Pairs: PW_gain L0U0V0Z0G1 vs pulse_linear_no_sv; L0U0V1Z0G1 vs pulse_linear_primary. PW_signed_leak L1U0V0Z0G1 vs pulse_linear_leak_no_sv; L1U0V1Z0G1 vs pulse_linear_leak. Held-out pulse-only NLL (pcv folds, nbins 9), 5 seeds (12345, 23456, 34567, 45678, 56789), via the committed score audit.
1. Mouse improved: mean over seeds of ΔNLL (new − constant) < −2 × (seed SD of ΔNLL for that mouse) AND < −2 NLL.
2. Cohort (8 mice excluding PSUIM6/7): two-sided Wilcoxon signed-rank on per-mouse seed-mean ΔNLL, p < 0.05 AND median improvement > 0. Otherwise report "no cohort benefit" (never "trend").
3. Mouse-specific: PSUIM6 AND PSUIM7 both improved by rule 1, AND each one's early low-coherence residual (early pulses, |coh| 0/9/18; observed − model P(follow pulse)) at least halves relative to the constant-gain fit.
4. Mechanism: in the mice that improve, fitted gain_decay > 0 or signed leak_rate < 0 (pulse full fit and majority of pcv folds). An improvement with parameters not on the primacy side does not count as support.
5. Guardrail: choice excess G² on control trials (full pulse fit scored out of sample, as choice_g2_control_training) must not increase versus the constant-gain counterpart, beyond its seed range.
All five are reported, including failures.

### B. RT alignment to pulse onset at 100% coherence (hazard)
- Pulse trials: 100% coherence, incongruent pulses (all timings pooled, primary; by timing, secondary). Error = choice against coherence (= following the pulse).
- Control: 100% control trials of the same mouse, each assigned 20 pseudo-onsets drawn from that mouse's 100% pulse-onset distribution.
- Time since (pseudo-)onset τ; at risk = still undecided (RT ≥ onset + τ_start); the RT floor applies equally to both.
- Primary statistic: window error hazard = errors with RT − onset in [150, 400) ms / trials undecided at onset + 150 ms; ratio pulse/control, counts pooled across mice.
- Clustering = ratio > 1 with 95% bootstrap CI excluding 1 (2,000 resamples: mice, then trials within mouse). A roughly flat ratio over time (the 50 ms-bin profile 0-1500 ms and the out-of-window ratio [400, 1500) ms) = lapse-like. Both reported.
- Groups: all mice; PSUIM6/7; other 8 mice.
- Deviation (data): there are no congruent pulses at 100% coherence (all 1,538 are incongruent), so the congruent check uses 36% congruent pulses vs 36% controls (expect ratio ≤ 1).

## Out of scope
Refitting existing families; changing rt_nllh_weight for final fits.

## Log
- 2026-11-19: The power front end was tested from saved all_candidates cells, without new fits. The GLM-HMM for PSUIM7 already exists (2026-11-15 pilot), so it is not repeated.
- 2026-11-19: Control excess is not zero, so the misfit is not pulse-specific; PSUIM6/7 dominate the control excess. guess_lapse not queued. Next: step 4c.
- 2026-11-19: Score audit committed (144107c) before rescore, per author. Top-4 rescore ran on CPU (GPU lost mid-session); <=0.55 NLL vs CUDA. Early-pulse residual mostly PSUIM6/7; data pulse effect does not shrink with coherence. Next: author decision on PW fits (all mice or PSUIM6/7).
- 2026-11-19: Branch pushed (af74b35..e253c1f). PW table submitted by author: PW_gain jobs 43398729 (108 x 1 h), 43398730 (12 x 2 h); PW_signed_leak 43398731 (65 x 1 h), 43398732 (52 x 2 h), 43398733 (3 x 3 h). Outputs ddm/fits_pulse_linear_{gain_decay,signed_leak}. Pending from author: scoring criteria for PW fits and definition of the RT-to-pulse-onset alignment at 100% coherence.
- 2026-11-19: Criteria A and B pre-registered (author's thresholds) before any PW or hazard result.
- 2026-11-19: Criteria B result: no clustering in 150-400 ms (all CIs include 1); excess after 400 ms in other 8 mice. Flagged: lapses cancel in the pulse/control ratio, so 'flat = lapses' is not a valid reading (report pulse-onset-error-hazard).
