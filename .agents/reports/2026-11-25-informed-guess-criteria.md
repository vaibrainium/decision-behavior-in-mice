# Report: informed fast guesses — fitted family scored against the pre-written criteria
Date: 2026-11-25   Agent: Claude (Opus 5.5)   Commit: (this report's commit; fits from tasks_2026-11-24_informed.csv, 3438d1c)
Plan: plans/2026-11-24-informed-guess-family.md (step 6)

## Question
Does adding informed fast guesses (a fraction guess_w of fast guesses report the DV side at guess RT − read_lag) to
the best pulse model (pulse_norm_ugm_no_sv) pass criteria A or A2, so that it would replace that model?

## Summary
No. Criteria A fail (rules 1, 2, 3) and A2 fails (rule 3), so by the pre-written decision norm UGM no sv stays the
best pulse model and the PSUIM6/7 fast-window pulse effect is a stated limitation. The mechanism is real in the two
target mice (guess_w > 0.05 in the full fit and 5/5 folds in both), held-out NLL improves by about 10 in each
(only loosely, ~1-2 seed SD), and control-trial choice excess falls (282.7 → 203.8). But the early low-coherence
pulse residual shrinks by only 18-24%, against the required 50% (A) or 25% (A2). High confidence in the verdict.

## Findings (all VERIFIED; source: draft_2026-11-15/informed_scores_2026-11-25/, criteria_summary.csv, criteria_per_mouse.csv)
- Reproduction: at the fits' seed 12345, recomputed − stored held-out NLL ≤ 0.11 per fold (both families).
- Total held-out ΔNLL (informed − constant, summed over folds, mean of 5 seeds): −16.0.
  - PSUIM6 −10.3 ± 9.3 (choice −2.4, RT −7.9); PSUIM7 −10.5 ± 6.1 (choice −6.3, RT −4.1).
  - Other 8 mice: −0.8 to +1.9; median +0.24, Wilcoxon p = 0.25; 2/8 improved.
- Rule 1 (strict: < −2 SD and < −2): 0/10. Loose (A2): 2/10 (PSUIM6, PSUIM7).
- Rule 2: fail (median +0.24, p 0.25).
- Rule 3: fail at both tiers. Early low-coherence residual (pp): PSUIM6 5.70 → 4.70 (0.82×), PSUIM7 9.56 → 7.27 (0.76×).
- Rule 4 (mechanism): pass. guess_w full / folds > 0.05: PSUIM6 0.21 / 5 of 5 (fold median 0.55); PSUIM7 0.58 / 5 of 5
  (median 0.47). Other mice: full-fit w 0 to 0.15 except PSUIM5 (0.685, fold median 0) and PSUIM10 (0.095).
- Rule 5 (guardrail): pass. Control choice excess 203.8 vs 282.7 (constant seed range 13.1). Largest drops PSUIM7
  108.8 → 74.8 and DBM5 56.6 → 13.7.
- Rule 6 (descriptive): fast (< 0.6 s) control accuracy at 100% coherence, constant → informed (data):
  PSUIM7 0.53 → 0.68 (0.77); PSUIM6 0.51 → 0.56 (0.74); PSUIM5 0.48 → 0.69 (0.47, overshoot from the full fit's
  w 0.685, which its folds do not support). Source: fast_control_accuracy.csv.
- read_lag where w is clearly > 0: 0.05-0.15 s (not interpreted; weakly identified per the recovery report).

## What didn't work
- Informed guesses capture part of the PSUIM6/7 deviation (fast accuracy, part of the RT likelihood), not the
  early low-coherence pulse residual that rules 3 targets. As with primacy and the pulse weight, the bulk of that
  residual is not absorbed.

## How to reproduce
```
OPENBLAS_NUM_THREADS=1 .venv/bin/python -W ignore -m scripts.paper.score_informed_fits --output <new dir>
OPENBLAS_NUM_THREADS=1 .venv/bin/python -W ignore -m scripts.paper.score_informed_criteria <that dir>
```
Fits: /mnt/data/processed/ddm/fits_pulse_norm_ugm_informed (60, from Hyak jobs 43513803-43513810, 43534708-9).
CPU numba backend; seeds 12345, 23456, 34567, 45678, 56789.

## Caveats
- Rule 1's strict threshold is hard to meet with seed SDs of 6-9 per mouse; both target mice pass only the loose form.
- PSUIM5's full-fit w (0.685) is not supported by its folds (median 0); its fast control accuracy overshoots.
- Mechanism evidence (rule 4) is within-model; it does not show mice use informed guesses, only that the fit prefers them.

## Open questions and next steps
- [ ] Author: accept the "neither" verdict (norm UGM no sv stays; limitation stated). Optional sentence for the
      limitation: allowing a fraction of fast guesses to read the accumulated evidence improved PSUIM6/7 held-out
      fit and fast control accuracy but left most of the early-pulse residual.
- [ ] Transient-channel fits are scored the same way when synced (independent family).
