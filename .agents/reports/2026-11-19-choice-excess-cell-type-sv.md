# Report: Where the held-out pulse choice excess sits, and how big sv is relative to motion-energy drift spread
Date: 2026-11-19   Agent: Claude (Opus 5.5)   Commit: af74b35 (+ this report's commit)
Plan: plans/2026-11-19-choice-misfit-followup.md (steps 3, 4; step 2 in its own section below)

## Question
1. Is the held-out pulse choice excess concentrated in the 100% coherence cells, which would point to lapses and guess_lapse? Or in incongruent or late-pulse cells, which would point to pulse integration?
2. Is the fitted sv large compared with the trial-to-trial drift spread that motion energy already supplies?

## Summary
The choice misfit is not specific to pulses. Every family also shows excess on control trials it never saw, and in-sample on its own pulse training trials. The sv penalty appears on pulse trials, both held-out and in-sample, but not on controls. The excess is not concentrated at 100% coherence or in incongruent or late cells. It is largest in early pulses and in zero- and low-coherence cells, where the mice follow the pulse more than every model predicts. The extra excess from sv is confined to congruent cells. guess_lapse is a side issue and is not queued. The fitted sv is 5 to 35 times the within-cell motion-energy drift spread, depending on the window. sv supplies almost all of the across-trial drift variability rather than duplicating the input.

## Findings
- VERIFIED: Mean excess G² per family, held-out pulse trials:

  | trial type | trials | no-sv families | sv families |
  |---|---|---|---|
  | congruent | 4,312 | 162 | 242 |
  | incongruent | 5,779 | 146 | 145 |
  | zero coherence | 1,388 | 61 | 79 |

  sv adds excess only in congruent cells. Source: `choice_g2_by_cell_type_2026-11-19/by_direction.csv`.
- VERIFIED: Excess per 100 trials:
  - By timing (no-sv / sv): early 3.7 / 5.0, middle 2.5 / 3.0, late 3.7 / 4.7. Late cells are not disproportionate (2,146 trials).
  - At 100% coherence (all incongruent): 2.6 / 3.1, below the overall average of about 3.9.
  - Source: `by_timing.csv`, `by_abs_coh.csv`.
- VERIFIED: norm UGM no sv at 100% coherence has excess 35 (11% of its total, z = 1.6). PSUIM7 contributes 21.7 of that. Its +4.9 pp mean miss at 100% is not a reliable lapse signal.
- VERIFIED: Pulse-follow residual is (observed − model) P(choice in the pulse direction). It is positive in early cells (+4.4 pp no-sv, +5.9 pp sv) and in zero-coherence cells (+5.1 / +6.5 pp; early zero-coherence +8.3 / +9.8 pp). At 36 to 100% incongruent it is about −1 pp. Source: `by_direction_timing.csv`, `by_direction_abs_coh.csv`.
- SUSPECTED: All models underpredict the effect of early pulses when the baseline evidence is weak, and overpredict it slightly at high coherence. A pulse effect that shrinks with coherence would fit this. It agrees with the pulse-onset diagnosis (excess directional sensitivity, PSUIM6/7). Not tested with a model.
- VERIFIED: Without PSUIM7, incongruent excess falls from 146 to 94 (no-sv) and from 145 to 90 (sv). Congruent falls less (162 to 146, 242 to 193).
- VERIFIED: Linear sv pulse-only families, medians over mice: sv is 1.9 to 2.6 drift units. Within-cell SD of drift_gain × mean ME is 0.05 to 0.06 over 0.25 s, 0.09 to 0.12 over 0.5 s and 0.33 to 0.44 over each trial's decision time. The sv/spread ratio is 33 to 35, 18 and 5.2 to 5.8. Per mouse (decision time) the ratio is 3.3 (PSUIM7) to 9.3. The exception is PSUIM10 at 0.05, where sv ≈ 0. Source: `sv_vs_me_spread_2026-11-19/sv_vs_me_spread.csv`, `scripts/paper/sv_vs_me_drift_spread.py`.
- SUSPECTED: The motion-energy spread grows with window length, which white noise would not produce. The ME onset ramp and pulse timing within a cell probably inflate the longer windows, so the decision-time ratio is a lower bound. The premise that ME already supplies the drift variability is weak. sv dominates trial-to-trial drift variability. Its cost on choice is in congruent cells, where it pulls predictions toward 0.5.

## Step 2: control trials and training fits
Full pulse-only fits (split "pulse", all 22 families) were scored at seeds 12345 and 23456; the fits used seed 42. They were scored on their own pulse training trials (11,479 trials, 392 cells) and on control trials they never saw (14,014 trials, 90 cells). Source: `choice_g2_control_training_2026-11-19/{cells.csv.gz,summary.csv}`, `scripts/paper/choice_g2_control_training.py`.
- VERIFIED: **Pulse training trials (in-sample):** excess per family ranges from 130 to 247 (z 4.4 to 8.4).
  - no-sv families: 1.1 to 1.4 per 100 trials. sv families: 1.4 to 2.2.
  - sv costs choice fit in-sample too, so this is a fitting trade-off with RT, not overfitting.
  - norm UGM no sv (135) is mid-pack among the no-sv families. Its held-out lead is not reproduced in-sample.
  - The two seeds differ by 10 to 48 per family.
- VERIFIED: **Control trials (out of sample):** excess per family ranges from 115 to 277 (z 8.5 to 20); the seeds differ by at most 13.
  - The misfit is NOT specific to pulse trials.
  - The sv difference disappears: 1.18 per 100 trials (no-sv) vs 1.23 (sv).
  - PSUIM6 and PSUIM7 carry 57 and 58 of the roughly 165 mean. The other mice range from −2 to 12.
- VERIFIED: **norm UGM no sv is the worst family on controls (277).** At 9 / 18 / 36 / 100% coherence it misses by −4.6 / −1.6 / +0.9 / +6.1 pp: too steep at low coherence and too flat at 100%. Linear and power families miss at 100% by 0.4 to 1.7 pp only. The compression shape of the normalizing front end fits controls poorly. This is not a lapse pattern shared by all models.
- SUSPECTED: Control excess combines accumulator misfit with the failure of pulse-fit parameters to transfer to controls. Separating the two needs control-trained fits scored on held-out controls (Figure 3 ccv candidates; C has sv, so there is no matched no-sv control fit).

## What didn't work
- Nothing failed.

## How to reproduce
- `PYTHONPATH=/src .venv/bin/python -m scripts.paper.choice_g2_control_training --output dissemination/paper_accumulation/draft_2026-11-15/choice_g2_control_training_2026-11-19` (about 25 min, CUDA); then `.venv/bin/python scripts/paper/choice_g2_control_training_summary.py dissemination/paper_accumulation/draft_2026-11-15/choice_g2_control_training_2026-11-19`.
- `.venv/bin/python scripts/paper/choice_g2_by_cell_type.py dissemination/paper_accumulation/draft_2026-11-15/pulse_score_audit_2026-11-19/all_candidates/cells.csv.gz dissemination/paper_accumulation/draft_2026-11-15/choice_g2_by_cell_type_2026-11-19`
- `PYTHONPATH=/src .venv/bin/python -m scripts.paper.sv_vs_me_drift_spread --output dissemination/paper_accumulation/draft_2026-11-15/sv_vs_me_spread_2026-11-19`

## Caveats
- One seed. Cell-type excesses are sums over small cells, and the families are not independent, so the per-family z values are descriptive.
- 100% coherence pulses are all incongruent, so lapses and incongruent pulses cannot be separated there.
- The sv comparison covers linear front-end families only. With power or norm front ends the drift units differ.

## Open questions and next steps
- [ ] Test a pulse effect that shrinks with baseline coherence. This needs a model change, not a refit of existing families.
