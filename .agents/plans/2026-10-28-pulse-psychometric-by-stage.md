# Plan: pulse psychometric functions by pulse stage
Status: done
Created: 2026-10-28 by Claude (Opus 5.5)
Related reports: reports/2026-10-27-pulse-contrast-responders-only.md, reports/2026-10-27-pulse-asymmetry-lapse-checks.md

## Goal
Replace the dashboard's "pulse direction shifts choices" dot plot with observed psychometric functions (author request):
(1) control, right pulse, left pulse; (2) control, congruent, incongruent pulse; each per pulse stage (early, middle, late).

## Context
- Responded trials only (D003). Pulse stage = |sched_pulse_type|: 1 early, 2 middle, 3 late (onsets: UCLA ~17-117 /
  200-300 ms for stages 1-2 and no stage 3; UW 50 / 233 / 417 ms). Late stage has fewer mice (design, not a rig split).
- At ±100% a pulse can only point against the motion; 0% pulses are neither congruent nor incongruent.
- Asymmetric UW cells (one sign scheduled) excluded via signs_scheduled_symmetric, as in the asymmetry report.
- Helpers: scripts/ddm/pulse_psychometric.py (trial_table, cells).

## Steps
- [x] 1. Script scripts/ddm/pulse_psychometric_stage.py: per mouse P(right) per coherence x category x stage; mean ± SEM
      over mice; CSV + figure (dissemination/paper_accumulation/figures/qc).
- [x] 2. Check counts per cell and n mice per point; report trials dropped by the symmetry rule.
- [x] 3. Dashboard: replace the per-mouse dot panel with the two psychometric panels.
- [x] 4. Verify: stage-pooled curves reproduce the sign of the 7.52 pp contrast; numbers in the CSV match the figure.

## Out of scope
Model predictions on these curves; new statistics.

## Log
- 2026-10-28: plan written.
- 2026-10-28: author asked for stages (early/middle/late) and fitted curves instead of joined lines. Mouse sets matched per
  panel and coherence (pooled control vs 2-mouse late points was misleading); points need >= 3 mice. 2,264 trials in
  asymmetric cells dropped. Fits: logistic with lapses on group means weighted by mice; free 4-parameter fits on pulse
  curves were unconstrained at the missing +-100% end (right pulse to 0.95), so pulse curves share control lapses.
- 2026-10-28: verify: early/middle right-pulse curves sit left of control and left-pulse right of it, matching the sign of
  the 7.52 pp contrast. Outputs dissemination/paper_accumulation/figures/qc/pulse_psychometric_stage_2026-10-28*;
  dashboard version 10. No new report (descriptive display; no new tested result).
