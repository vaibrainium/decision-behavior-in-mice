# Report: Joint pulse-weight fits scored against criteria A/A2 (A3 mapping); PSUIM6/7 residual closed as a mouse-specific deviation
Date: 2026-11-20   Agent: Claude (Opus 5.5)   Commit: 29ce31c (A3 criteria, before scoring) + this report's commit
Plan: plans/2026-11-19-choice-misfit-followup.md (step 4h2; criteria A, A2, A3)

## Question
Does a free weight on the pulse channel, fitted jointly on control and pulse trials, absorb the held-out early low-coherence pulse residual (PSUIM6/7) without hurting control trials? With w = 1 the model is the joint fit. A free w also tests whether the motion-energy input understates the pulse by a scalar factor (the scale part of the rig check).

## Summary
No. Neither tier passes, with or without sv. The fitted weight stays at 1.000 in PSUIM6 and PSUIM7 (all-trial and fold-median fits), and their residuals do not move (PSUIM6 9.4 → 8.9 pp, PSUIM7 14.5 → 14.5 pp, sv). This confirms the 2026-10-30 total-NLL result at 5 seeds and extends it to the residual and control-trial checks. The pulse is not under-scaled in the input as far as these mice's choices and RTs are concerned. Under the author's stopping rule (2026-11-20), PSUIM6/7 are reported as a stable mouse-specific deviation that the tested models do not capture. The rig check is the one condition still open; see the last section.

## Findings
Held-out NLL over all trials in the joint folds cv0–4, nbins 9, 5 seeds (12345 … 56789), CPU. ΔNLL = pulse weight − joint constant, summed over folds, then mean ± SD over seeds. Source: `dissemination/paper_accumulation/draft_2026-11-15/pulse_weight_joint_scores_2026-11-20/criteria_{summary,per_mouse}.csv`.
- VERIFIED: **Reproduction.** At seed 12345, recomputed fold NLL equals the stored test NLL within 0.001 for all 4 families.
- VERIFIED: **Confirmatory tier A:**

  | rule | with sv (vs joint primary) | no sv (vs joint no sv) |
  |---|---|---|
  | total ΔNLL (10 mice); pulse part, control part | −2.5; −13.1, +10.6 | +12.1; +4.1, +8.0 |
  | 1 improved mice | 0/10 | 0/10 |
  | 2 cohort (8): median ΔNLL, Wilcoxon p | +0.67, 0.11 → no cohort benefit | +0.28, 0.31 → no cohort benefit |
  | 3 PSUIM6 and PSUIM7 both fixed | fail | fail |
  | 4 mechanism (w > 1 in improvers) | n/a (no improvers) | n/a |
  | 5 control excess, new vs constant (constant's seed range) | pass: 177 vs 187 (16) | pass: 154 vs 155 (19) |

- VERIFIED: **Exploratory tier A2:** no pass.
  - Loose improvers: with sv, 1/10 (PSUIM6, −9.3 ± 8.7); without sv, 0/10.
  - Cohort of 8: 1/8 improved with sv, median +0.67 [0.10, 1.82]; 4/8 without sv, median +0.28 [−0.14, 3.36].
  - The residual rule (25% shrink in both mice) fails.
  - No control-trial flag (the change is −9.8 with sv, −0.9 without).
  - The A2 mechanism count "1/1 with fold-median w > 1" for PSUIM6 is a tolerance artefact: w_all = 1.000 and the fold median = 1.000 (above 1 by less than 0.001). PSUIM6's loose improvement therefore comes with essentially unchanged parameters and is read as seed noise.
- VERIFIED: **Fitted w.** It departs from 1 by more than 0.05 only in DBM13 (sv, all-trial fit 1.33; fold median 1.00), PSUIM10 (sv fold median 5.3; no-sv 4.5 / 2.8) and PSUIM5 (no sv, all-trial 1.64, fold median 1.50) and PSUIM6 (no sv, all-trial 1.34, fold median 1.00). PSUIM7: 1.000 (sv); no sv 1.04 all-trial, fold median 1.09. Same pattern as the 2026-10-30 report.
- VERIFIED: **Residual under the constant joint fits, sv** (early pulses, |coh| 0/9/18, observed − model P(follow)):

  | mouse | residual (pp) |
  |---|---|
  | PSUIM7 | 14.5 |
  | PSUIM10 | 10.4 (166 pulse trials) |
  | PSUIM6 | 9.4 |
  | DBM5 | 6.2 |
  | PSUIM5 | 5.8 |
  | other 5 mice | −6.4 to 2.2 |

  So the deviation is heterogeneous across mice and strongest in PSUIM6/7; it is not confined to them.

## Evidence for the closing statement on PSUIM6/7 (author's stopping rule)
1. **Residual.** Mice follow early low-coherence pulses more than every tested model predicts. It is largest in PSUIM7 (≈14.5 pp) and PSUIM6 (≈9 pp). Stable across pulse-only and joint fits, sv and no-sv, and 5 seeds (this report; reports/2026-11-19-top4-multiseed-pulse-effect.md).
2. **Primacy fails within the tested range** (gain_decay ≤ 3/s, leak ≥ −1/s). Ruled out for the cohort and PSUIM6. For PSUIM7 it partly helps pulse trials at a clear cost on control trials (reports/2026-11-20-pw-fits-criteria-a.md).
3. **A free pulse weight fails.** w stays at 1, and neither the residual nor NLL moves (this report). It is fitted jointly, so control trials constrain it.
4. **No session or stage confound.** Every session has both trial types, randomly interleaved and evenly placed (plan log 2026-11-20; `pulse_session_structure_2026-11-20/`). The deviation is within-trial and stimulus-driven.
5. **Not pulse-triggered.** There is no error clustering 150–400 ms after incongruent 100% pulses (reports/2026-11-19-pulse-onset-error-hazard.md).
6. **HMM pilot** (reports/2026-11-15-nhp-pulse-hmm-pilot.md). A shared-pulse state model improves future-choice prediction in PSUIM6/7. State-specific pulse coefficients give no consistent benefit. Choice-only, two mice.

## Rig check (condition of the stopping rule): status
- VERIFIED (earlier reports 2026-10-23 pulse-stimulus and 2026-10-29 ucla-pulse-me-nofreeze):
  - Both rigs run at about 60 Hz. Pulses last 3 frames on UCLA and 4 on UW, and the same coherence-update code applies them.
  - The inputs used here have the UCLA replay freeze removed. The remaining convention uncertainty is bounded at 1.13–1.20×.
  - The UW/UCLA pulse ME ratio is 1.45, against 1.33 expected from duration.
  - Control inputs are matched across rigs.
- VERIFIED (this report): a scalar understatement of the pulse ME of any size is exactly what w tests, and w stays at 1 in PSUIM6/7.
- NOT DONE: a per-mouse check of pulse ME against nominal coherence. Not covered: pulse shape or timing errors that leave the area unchanged. For an integrator without leak these should not change choices.
- Rig is a covariate only. 4 UCLA mice (PSUIM5/6/7/10) vs 6 UW; PSUIM6/7 hold 83% of UCLA trials. Mouse and rig cannot be separated, so nothing here is a rig effect.

## What didn't work
- Nothing failed.

## How to reproduce
- `PYTHONPATH=/src .venv/bin/python -W ignore -m scripts.paper.score_pulse_weight_joint --output dissemination/paper_accumulation/draft_2026-11-15/pulse_weight_joint_scores_2026-11-20` (CPU)
- `PYTHONPATH=/src .venv/bin/python -W ignore -m scripts.paper.score_pulse_weight_criteria <that dir>`
- `PYTHONPATH=/src .venv/bin/python -m scripts.paper.pulse_session_structure --output dissemination/paper_accumulation/draft_2026-11-15/pulse_session_structure_2026-11-20`

## Caveats
- NOT BLIND for total NLL and the fitted w: both were reported on 2026-10-30 (disclosed in A3 before scoring). Rules 3 and 5 and the 5-seed values are new.
- 10 mice; 8 in the cohort test. PSUIM10's w is unstable (166 pulse trials).
- The pulse-weight model scales the whole pulse channel. A transient (high-pass ME) channel is a different hypothesis and was not tested; it is parked by the author.

## Open questions and next steps
- [ ] Author: accept the existing stimulus reports plus w ≈ 1 as the rig check, or ask for the per-mouse pulse-ME check. Then close the PSUIM6/7 thread per the stopping rule.
- [ ] Step 4i: random-effects model comparison across mice.
- [ ] Step 5: adaptive bins, once the GPU is back.
