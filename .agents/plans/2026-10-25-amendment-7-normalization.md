# Plan: primacy plan amendment 7 (normalization front end), exploratory
Status: active
Created: 2026-10-25 by Claude (Opus 5.5)
Related reports: dissemination/reports/primacy-analysis-plan.md (amendment 7, adopted 2026-10-25); analysis log 5.10–5.11

## Goal
Front ends F1 (power law) and F2 (temporal divisive normalization) fitted on control trials, one selected by the
pre-specified rule, its frozen pulse predictions gated; only if the gate passes: fair strategy comparison, calibration,
then timing analyses. One round, then stop.

## Assumptions
- The transform acts on the 1 ms simulator input (60 Hz frames held), i.e. on x(t) = S + N, inside the simulator.
- F2's pool p is a causal exponential low-pass of |x| on the 1 ms grid; p starts at 0 at stimulus onset.

## Steps
- [x] 1. (a6aefe7) Implement F1/F2 in both simulator backends (params fe_gamma; fe_beta, fe_tau); defaults reproduce F0 exactly;
      backends agree; check F2 against a direct numpy reference.
- [x] 2. (88e6cd0) `fit_mouse_ddm.py --front_end {power,norm}`: adds the parameters with the amendment's bounds; output folder suffix.
- [ ] 3. Hyak: ccv0-4 (15 reps) + control (50 reps) for F1 and F2 (120 jobs).
- [ ] 4. Selection (item 3) on control CV; record before any pulse prediction.
- [ ] 5. Frozen predictions (commit + SHA-256), then gate (item 4). Stop if it fails.
- [ ] 6. (only if gate passes) E refit with the same front end; strategy test + power; calibration; timing analyses (a)-(c).
- [ ] 7. Report.

## Out of scope
Full normalization inside the motion-energy computation; any candidate beyond F1/F2; location-level analyses.

## Log
- 2026-10-25: amendment 7 adopted (V. Thakur).
- 2026-10-25: front ends implemented and checked (backends agree, defaults exact, normalization = direct loop); fit
  option smoke-tested for both. Next: 120 Hyak jobs (analysis log 8.4f).
