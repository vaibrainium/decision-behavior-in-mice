# Report: Gain-decay and signed-leak pulse-only fits scored against pre-registered criteria A / A2
Date: 2026-11-20   Agent: Claude (Opus 5.5)   Commit: 0772cff (criteria A2 + scripts, committed before any output was read) + this report's commit
Plan: plans/2026-11-19-choice-misfit-followup.md (step 4h; criteria A pre-registered in 57f7c72, tier A2 in 0772cff)

## Question
Does primacy (a time-decaying evidence weight, or a self-exciting accumulator with negative leak) absorb the held-out early low-coherence pulse residual, especially in PSUIM6/7, without harming the control-trial choice fit?

## Summary
No. Neither tier passes for any of the four pairs. Within the tested range (gain_decay ≤ 3/s, leak ≥ −1/s), primacy does not account for the residual: ruled out for the cohort and for PSUIM6. For PSUIM7 it partly helps the pulse trials, at a clear cost on control trials. The next step is pulse weighting (4h2). One exploratory observation stands out: PSUIM7 without sv improves strongly with near-maximal gain decay (ΔNLL −94), but its control-trial choice excess doubles and its residual shrinks only 40%. Signed leak changes nothing: no mouse improves, and fitted leak rates are mostly positive.

## Findings
All numbers: held-out pulse-only NLL (pcv0–4, nbins 9), 5 seeds (12345 … 56789), CPU backend. ΔNLL = new − constant-gain, summed over folds, then mean ± SD over seeds. Source: `dissemination/paper_accumulation/draft_2026-11-15/pw_scores_{gain,leak}_2026-11-20/criteria_{summary,per_mouse}.csv`.

- VERIFIED: **Reproduction.** At seed 12345 the recomputed held-out NLL matches the stored test NLL per fold: exactly for the gain-decay run (all 4 families); within 0.17 for the signed-leak run (CPU vs CUDA, as documented before). So the stored gain_decay and negative leak_rate are applied in simulation. The other seeds differ by up to 29 per fold, which is simulation noise.
- VERIFIED: **Confirmatory tier A**:

  | rule | gain, sv | gain, no sv | signed leak, sv | signed leak, no sv |
  |---|---|---|---|---|
  | total ΔNLL (10 mice) | −26 | −86 | +0.6 | +1.0 |
  | 1 improved mice | 1/10 (DBM13) | 2/10 (DBM13, PSUIM7) | 0/10 | 0/10 |
  | 2 cohort (8): median ΔNLL, Wilcoxon p | +0.08, 0.64 → no cohort benefit | +0.51, 0.15 → no cohort benefit | −1.13, 0.95 → no cohort benefit | +0.12, 0.84 → no cohort benefit |
  | 3 PSUIM6 and 7 both fixed | fail | fail | fail | fail |
  | 4 mechanism in improvers | fail (DBM13 gain_decay −0.07) | pass (DBM13 1.1, PSUIM7 2.9) | n/a (no improvers) | n/a |
  | 5 control excess (new vs const, const seed range) | pass (229 vs 238, 24) | **fail** (202 vs 153, 16) | **fail** (200 vs 173, 12) | pass (159 vs 145, 18) |

- VERIFIED: **Exploratory tier A2.** No pair passes.
  - Loose improvers: gain sv 3/10 (DBM13, DBM14, PSUIM6); gain no-sv 2/10 (DBM13, PSUIM7); signed leak 0/10 for both.
  - Of the 8 other mice, the number with ΔNLL below 0, and the median ΔNLL [mouse-bootstrap 95% CI]:

    | | improved | median ΔNLL |
    |---|---|---|
    | gain, sv | 4/8 | 0.08 [−4.61, 2.01] |
    | gain, no sv | 1/8 | 0.51 [0.03, 4.36] |
    | signed leak, sv | 5/8 | −1.13 [−1.83, 2.43] |
    | signed leak, no sv | 4/8 | 0.12 [−2.19, 2.73] |

  - The residual-shrink rule (25% in both PSUIM6 and PSUIM7) fails everywhere.
  - The control-trial flag (worse by more than 2× the seed range) is raised for gain no-sv (+48.7) and signed leak sv (+26.7).
- VERIFIED: **PSUIM7, gain no-sv.**
  - ΔNLL −93.6 ± 15.6.
  - gain_decay 2.88 (full fit; pcv median 2.90; bound 3), so the evidence weight falls to about 5% after 1 s.
  - Early low-coherence residual 12.8 → 7.7 pp (−40%).
  - Control excess 33 → 64.
  - PSUIM7 accounts for −94 of the −86 total. The other 8 mice sum to +9.5.
- VERIFIED: **PSUIM6.**
  - Gain sv: ΔNLL −22.9 ± 15.5, but gain_decay is −0.23 (recency side), and the residual changes from 9.0 to 8.7 pp. Not primacy support.
  - Gain no-sv: −1.4 ± 8.7.
  - Signed leak: +4.3 (sv) and −1.2 (no sv).
- VERIFIED: **Fitted signed leak.** leak_rate is positive in most mice (full fit: 8/10 with sv, 6/10 without). It is negative in both variants only for DBM15 and PSUIM10; DBM13 and PSUIM7 are negative only without sv. The negative range is not being used.
- VERIFIED: **Early low-coherence residual.** In the 8 other mice it is already small under the constant-gain fits (group means −1.1 to 1.2 pp). Mean over PSUIM6/7: 11.9 → 11.6 (gain sv), 10.2 → 7.4 (gain no sv, almost all PSUIM7), 12.0 → 12.1 and 10.2 → 10.3 (signed leak).
- SUSPECTED: Large seed SDs (up to 15.5 per mouse) make rule 1 hard to meet for small effects. This does not affect the conclusion: outside PSUIM6/7 no seed-mean ΔNLL exceeds 8.4 in size.

## What didn't work
- Nothing failed technically. Two items of checkpoint and sync housekeeping:
  - Two gain-decay fits timed out at 1 h and were resumed from their checkpoints (PSUIM6 pcv0 resumed at generation 231).
  - Signed leak needed a second scp.

## How to reproduce
- `PYTHONPATH=/src .venv/bin/python -W ignore -m scripts.paper.score_pw_fits --which gain --output dissemination/paper_accumulation/draft_2026-11-15/pw_scores_gain_2026-11-20` (and `--which leak … pw_scores_leak_2026-11-20`). CPU; the two runs ran concurrently.
- `PYTHONPATH=/src .venv/bin/python -W ignore -m scripts.paper.score_pw_criteria <that dir>`
- Fits: `/mnt/data/processed/ddm/fits_pulse_linear_{gain_decay,signed_leak}` (task table `scripts/slurm/tasks_2026-11-19_pulse_w.csv`, all 240 present).

## Caveats
- PSUIM7's gain_decay (2.88; pcv median 2.90) sits at the upper bound of 3/s. At 3/s only about 5% of the evidence weight remains after 1 s, so widening the bound would mostly push PSUIM7 toward using only the first few hundred ms, which the extrema-detection models already cover. Not refitted (author decision 2026-11-20).
- PSUIM7's trade-off (better pulse fit, control excess doubled) means one parameter set cannot describe both trial types for that mouse. Whether pulse and control trials share sessions for PSUIM6/7 is being checked (possible session or engagement confound).
- CPU backend (GPU still unavailable). Differences of ≤0.17 NLL per fold are negligible relative to the effects.
- 10 mice. The cohort test has only 8.
- Single functional forms: exponential gain decay, and leak bounded at −1/s. Other primacy shapes (e.g. a step or an early integration window) were not tested.
- The rule-5 control check uses full pulse fits scored on controls, so it mixes accumulator misfit with transfer failure (as noted in the step-2 report).

## Open questions and next steps
- [ ] Step 4h2: cell split and residual bootstrap on the joint pulse-weight fits (fits_joint_unfreeze_pulse_weight) vs the matching joint constant-gain fits.
- [ ] PSUIM7 alone prefers strong primacy (no sv), but at a cost on controls. Revisit only if pulse weighting also leaves PSUIM7 unexplained.
- [ ] Step 4i: random-effects model comparison across mice (could include the PW families).
