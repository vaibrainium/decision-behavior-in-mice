# Report: Choice G² across all pulse-only families, with and without PSUIM7
Date: 2026-11-19   Agent: Claude (Opus 5.5)   Commit: 3b55eca (+ untracked audit outputs)
Plan: plans/2026-11-19-choice-misfit-followup.md

## Question
Does a power front end reduce the held-out choice misfit, as the linear-too-shallow / UGM-too-steep pattern suggests? Does the ranking hold without PSUIM7?

## Summary
The power front end removes most of the low-coherence slope bias. It does not reduce the choice excess: power is equal to or worse than linear within each sv/no-sv pairing. The main driver of choice excess is sv. All 11 no-sv families (excess 322–418) beat all 11 sv families (423–506). Excess remains in every family without PSUIM7 (z ≥ 4.3), so the misfit is not only a slope miss and not only PSUIM7. Norm UGM no-sv ranks first on choice with and without PSUIM7, but its margin over linear no-sv (about 11 to 28 G²) is within Monte Carlo seed noise (about 30).

## Findings
- VERIFIED: Choice excess G² by family, 22 families, 11,479 held-out pulse trials, seed 12345:
  - norm UGM no sv: 322
  - linear no sv: 350
  - power no sv: 357
  - other no-sv families: 359–418
  - all sv families: 423–506. Linear leak 441 vs power leak 489. Linear leak + urgency 489 vs power leak + urgency 506.

  Source: `dissemination/paper_accumulation/draft_2026-11-15/choice_g2_2026-11-19/summary_all.csv`.
- VERIFIED: Slope residual, (observed − model) P(choice toward coherence), at 9 / 18 / 36% coherence:
  - Linear leak: +1.8 / +1.4 / +2.9 pp. Power leak: +0.1 / −0.4 / +2.1 pp. The power front end fixes the mean slope at low coherence.
  - Norm UGM no sv: −2.2 / −3.0 / +0.8 pp, and +4.9 pp at 100%.
  - sv families are consistently too shallow at 36% (+2.0 to +4.4 pp).

  Source: `slope_residual_by_abs_coh.csv`.
- VERIFIED: Without PSUIM7 (8,739 trials):
  - Choice-excess rank 1 is still norm UGM no sv (249), followed by linear no sv (260).
  - The total held-out NLL top 3 becomes power UGM (10,409.7), norm UGM no sv (10,414.1) and linear leak (10,414.7). These are within about 5 NLL, smaller than the about 50 NLL seed range for finalists (2026-11-19 score audit), so the order is unresolved.

  Source: `summary_no_PSUIM7.csv`.
- SUSPECTED: Mean slope residuals are ≤ 5 pp, while the excess persists after the power front end removes them. Most of the excess is therefore spread across cells, for example in the pulse-direction effect (see the pulse-onset diagnosis, PSUIM6/7) or in session-to-session drift. It is not in the mean psychometric curve. Not decomposed.
- VERIFIED (existing): An HMM on PSUIM7 was already run in reports/2026-11-15-nhp-pulse-hmm-pilot.md. A shared-pulse HMM improves held-out choice by 0.0148 [0.0034, 0.0270] bits/trial over static. This is choice-only, with no late pulse trials.

## What didn't work
- Nothing failed. The guess_lapse variant was not tested: no pulse-only CV fits exist with guess_model=guess_lapse (all audited fits use fast_only).

## How to reproduce
`.venv/bin/python scripts/paper/choice_g2_all_candidates.py dissemination/paper_accumulation/draft_2026-11-15/pulse_score_audit_2026-11-19/all_candidates/cells.csv.gz dissemination/paper_accumulation/draft_2026-11-15/choice_g2_2026-11-19` (seconds, CPU).

## Caveats
- One seed for all 22 families. Only the 3 finalists have 3 seeds.
- Pulse-only held-out trials only. Control trials and training fits were not checked yet.

## Open questions and next steps
- [ ] Control-trial and training-fit G² (plan step 2).
- [ ] guess_lapse on norm UGM no sv needs new pulse CV fits (author decision).
- [ ] Decompose the excess into slope, pulse-direction and fold/session parts.
