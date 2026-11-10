# Plan: fit the DDM families on pulse trials only
Status: active (step 2: waiting for the author to submit on Hyak)
Created: 2026-11-10 by Claude (Opus 5.5)
Related reports: reports/2026-11-09-pulse-effect-bootstrap.md, reports/2026-10-30-pulse-weight-joint.md,
reports/2026-10-31-pulse-time-weights.md, reports/2026-11-09-mapping-accumulator-exploratory.md

## Goal
Author 2026-11-10: "none of these are satisfactory for pulse. I am thinking of fitting these models only on pulse trials
(where pulse coherence is different than trial coherence)." Fit selected families on pulse trials only, then ask:
can the family reproduce the pulse behaviour when it is not also constrained by control trials? Exploratory.

## Context (checked 2026-11-10)
- Every responded pulse trial has pulse coherence (+-100%) different from the trial coherence: 11,479 of 11,479
  (no pulse at +100 in the rightward direction or at -100 leftward). So "pulse trials" = all 11,479 of 25,493.
- The current joint fits already see the pulse conditions: likelihood summed over cells of coherence x scheduled pulse
  condition (fit_mouse_ddm.py docstring). Pulse trials are 45% of the trials; RT quantiles dominate the objective.
- Earlier: a free pulse weight stays ~1 and per-pulse-time weights are flat in 8/10 mice (reports 2026-10-30,
  2026-10-31): fitted to choices and RTs, the likelihood does not ask for a stronger pulse.
- Existing split "control" (fit controls, test on pulse) is the mirror of what is proposed.

## Assumptions
- Same objective (censored quantile QMLE), same cells, same simulator; only the training trials change.

## Steps
- [x] 1. fit_mouse_ddm.py: add split "pulse" (train pulse trials, test control trials) and optionally "pcv0-pcv4"
      (5-fold CV within pulse trials), outside ALL_SPLITS so existing job ids are unchanged. Local smoke test.
- [x] 2a. Scope (author 2026-11-10): linear and power x primary and leak+urgency, each with and without sv
      (L0U0V1Z0G1, L0U0V0Z0G1, L1U1V1Z0G1, L1U1V0Z0G1); splits pcv0-pcv4 + pulse; checkpointing on. 480 tasks:
      scripts/slurm/tasks_2026-11-10_pulse.csv (make_task_table --pulse), out ddm/fits_pulse_{linear,power}_integrators.
- [ ] 2b. Author submits with autosubmit --tasks/--state (own state + lock file).
- [ ] 3. Sync; simulate the pulse-only fits; add a "Pulse-only fits" group to the fit browser.
- [ ] 4. Compare: pulse signatures vs data (psychometric shifts per condition, early/late window effect, per-mouse
      chi-square); parameters pulse-only vs all vs control-only; control-trial NLL out of sample.
- [ ] 5. Report.

## Interpretation, fixed before results
- Pulse-only fit still misses the pulse signatures -> the family cannot produce them with any parameters (structural).
- Pulse-only fit captures them but its parameters differ from the all-trial fit / predict controls badly -> tension
  between control and pulse trials under this family.
- Caveat: if RT quantiles dominate, even pulse-only fits may not prioritise the few-pp choice shifts.

## Out of scope
A new objective (e.g. extra weight on pulse-trial choices); decision rules.

## Log
- 2026-11-10: plan written; waiting for the author.
- 2026-11-10: author: "yes to both but also with and without sv", "also with checkpoint", 16 h only for fits that needed
  long before. Added splits pulse / pcv0-4 (fit_mouse_ddm.py; outside ALL_SPLITS). Smoke test (PSUIM10, power,
  L1U1V0Z0G1, 2 DE iterations, scratch output): pulse n_train 166 / n_test 259 (controls); pcv2 132 / 34; both saved.
  Checkpointing is built into run_job (resumes on requeue). Time limits: earlier joint fit of the same mouse, mapping
  and accumulator (with sv; slowest split) > 4 h -> 16 h (power leak+urgency, with and without sv: DBM6 6.6, PSUIM5
  4.1, PSUIM6 6.1, PSUIM7 4.7 h; 48 tasks); others limit(runtime) = 1-6.5 h. Task indices verified against
  build_grid. autosubmit.py: --tasks / --state (own lock), so this loop runs beside the old one.
