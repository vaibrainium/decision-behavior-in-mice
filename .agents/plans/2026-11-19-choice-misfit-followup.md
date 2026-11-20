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
- [x] 4e. Gain-decay / signed-leak pulse-only CV fits: table tasks_2026-11-19_pulse_w.csv generated (240 tasks); SUBMITTED 2026-11-19 14:55 (Hyak time) by author, all 10 mice, state slurm-logs/autosubmit_state_pulse_w.json; then rerun the cell split and residual bootstrap on them.
- [x] 4g. RT hazard aligned to pulse onset at 100% coherence (criteria B).
- [x] 4h. Score PW fits against criteria A once all 240 tasks are done.
- [ ] 4h2. Conditional on 4h: if gain decay / signed leak does not absorb the PSUIM6/7 early low-coherence residual, run the same cell split and residual bootstrap on the existing pulse-weight fits (fits_joint_unfreeze_pulse_weight; scripts/slurm/submit_pulse_weight.sh, scripts/ddm/compare_pulse_weight.py) before building anything new. Note: these are JOINT fits (cv0-4 on all trials, L0U0V1Z0G1 and L0U0V0Z0G1), not pulse-only pcv fits; score their pulse cells within the joint held-out folds and compare with the matching joint constant-gain fits.
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

### A2. Exploratory tier for the PW fits (author, added 2026-11-20 BEFORE any PW scoring output was seen; does NOT replace A)
A (strict, confirmatory) alone supports claims in the paper. A2 decides what to try next.
Continuous effect sizes are reported for everything, plus these looser flags:
1. Mouse improved (loose): seed-mean dNLL < 0 AND |dNLL| > 1 x that mouse's seed SD.
2. Cohort (8 mice): per-mouse dNLL, sign count out of 8, median with a bootstrap 95% interval (resample mice). No p-value cutoff.
3. Residual (loose): early low-coherence residual shrinks by >= 25% in absolute size (|new| <= 0.75 |old|).
4. Parameter direction (loose): median over the 5 pcv folds on the primacy side.
5. Control guardrail (loose): change in control excess reported as an effect size; flag only if worse by > 2 x the constant fit's seed range.
Decision: A and A2 pass = result. Only A2 passes = direction worth one more round (pulse-weight fits or more seeds), not a claim. Neither = primacy ruled out for the PSUIM6/7 residual; move to pulse weighting (step 4h2).
Pinned strict-tier details (author): rule 3 compares absolute sizes, |new| <= 0.5 |old| (an overshoot of the other sign can count); rule 4 = >= 3 of 5 pcv folds; rule 5 = seed max - min over 5 seeds.

### A3. Criteria for the pulse-weight joint fits, step 4h2 (author, fixed 2026-11-20 BEFORE this scoring ran)
The two tiers A (confirmatory) and A2 (exploratory) apply unchanged to these fits, with the same five rules, thresholds and decision table. Mapping to joint fits:
- Pairs: fits_joint_unfreeze_pulse_weight L0U0V1Z0G1 vs fits_joint_unfreeze_integrators L0U0V1Z0G1 (sv); L0U0V0Z0G1 vs L0U0V0Z0G1 (no sv). Joint folds cv0-4 over all responded trials; 5 seeds (12345, 23456, 34567, 45678, 56789); same audit cell scorer (nbins 9).
- Rule 1/2 dNLL: held-out NLL over all trials in the joint folds (the fits' own objective). The pulse-trial and control-trial parts are reported separately as well.
- Rule 3: early low-coherence residual on held-out pulse cells within the joint folds; |new| <= 0.5 |old| (A2: 0.75).
- Rule 4: pulse weight (stored as parameter `noise_weight`) > 1 in the "all" fit and in >= 3 of 5 cv folds (A2: fold median > 1).
- Rule 5: choice excess G² on held-out CONTROL trials within the joint folds; fail if worse by more than the constant fit's seed range (A2 flag: > 2x).
- Disclosure: NOT blind for total NLL. Total held-out NLL at seed 12345 and the fitted weights were already reported on 2026-10-30 (reports/2026-10-30-pulse-weight-joint.md: w ~ 1, no mouse better by 10, PSUIM7 NLL worse at w = 2). Rules 1, 2 and 4 are therefore largely known in advance. New and unseen: the 5-seed values, the residual (rule 3) and the control excess (rule 5).

### B. RT alignment to pulse onset at 100% coherence (hazard)
- Pulse trials: 100% coherence, incongruent pulses (all timings pooled, primary; by timing, secondary). Error = choice against coherence (= following the pulse).
- Control: 100% control trials of the same mouse, each assigned 20 pseudo-onsets drawn from that mouse's 100% pulse-onset distribution.
- Time since (pseudo-)onset τ; at risk = still undecided (RT ≥ onset + τ_start); the RT floor applies equally to both.
- Primary statistic: window error hazard = errors with RT − onset in [150, 400) ms / trials undecided at onset + 150 ms; ratio pulse/control, counts pooled across mice.
- Clustering = ratio > 1 with 95% bootstrap CI excluding 1 (2,000 resamples: mice, then trials within mouse). A roughly flat ratio over time (the 50 ms-bin profile 0-1500 ms and the out-of-window ratio [400, 1500) ms) = lapse-like. Both reported.
- CORRECTED READING (2026-11-19, AFTER the test ran; NOT pre-registered): lapses occur on control trials too and cancel in the pulse/control ratio, so 'flat = lapse-like' was wrong. Corrected: ratio ~1 at all times = pulse has no effect on errors; peak in 150-400 ms = pulse triggers responses; ratio > 1 spread over later times = pulse integrated, decision at an ordinary RT. The clustering criterion itself is unchanged; only the reading of non-clustered patterns changed (author-approved).
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
- 2026-11-19: Criterion B reading corrected after the test (see criteria B). Settled: no pulse-triggered responses; the 100%-coherence pulse effect comes with ordinary-latency errors, so the pulse passes through the accumulator. Open: models under-weight the pulse, mostly PSUIM6/7 (primacy vs pulse salience). Methods sentence added (100% baseline has only incongruent pulses).
- 2026-11-19: Status pass at 19:39 on Hyak: PW_signed_leak 120/120 done; PW_gain 118/120, with the 2 missing fits resubmitted by autosubmit as job 43407656 (2 x 2 h). Scoring waits for those 2 and the sync. The two fits timed out at 1 h (estimated 0.4 h): PW_gain:18 PSUIM6 L0U0V1Z0G1 pcv0 and PW_gain:115 DBM6 L0U0V1Z0G1 pulse; 43407656 pending on ckpt-all.
- 2026-11-20: All 240 PW fits synced to /mnt/data/processed/ddm (verified against the task table). Scoring: scripts/paper/score_pw_fits.py (registers the new folders, runs the committed audit + control scorer unchanged, 5 seeds, CPU since GPU still down) -> pw_scores_{gain,leak}_2026-11-20; criteria via scripts/paper/score_pw_criteria.py. Operationalised (not in the pre-registration text): rule 3 'halves' = new residual <= 0.5 x constant residual (signed); rule 5 'beyond seed range' = mean increase > constant fit's seed max-min; rule 4 'majority of pcv folds' = >= 3 of 5.
- 2026-11-20 04:59 UTC: Exploratory tier A2 added (author) and rule 3 changed to absolute sizes (|new| <= 0.5 |old|), committed while pw_scores_{gain,leak}_2026-11-20 runs were still in progress and before any of their output was read. A2 does not replace A.
- 2026-11-20: 4h done (report pw-fits-criteria-a): neither A nor A2 passes for any of the 4 pairs; primacy ruled out for the PSUIM6/7 residual per the decision rule. PSUIM7 no-sv gain decay -94 NLL (gain_decay 2.9) but control excess 33->64 and residual -40%. Signed leak: no improvers, leak mostly positive. Next: 4h2 (pulse-weight joint fits).
- 2026-11-20 05:55 UTC: Criteria A3 (tiers A and A2 applied unchanged to the pulse-weight joint fits) committed before any 4h2 scoring ran; prior 2026-10-30 total-NLL result disclosed.
