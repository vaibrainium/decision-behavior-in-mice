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
- [x] 2a. Scope (author 2026-11-10): linear and power x primary, leak, urgency and leak+urgency, each with and without
      sv; splits pcv0-pcv4 + pulse; checkpointing on. Two tables (out ddm/fits_pulse_{linear,power}_integrators):
      tasks_2026-11-10_pulse.csv (PO_*, primary + leak+urgency, 480, submitted; state autosubmit_state_pulse.json) and
      tasks_2026-11-10_pulse_lu.csv (PLU_*, leak only + urgency only, 480; state autosubmit_state_pulse_lu.json).
- [x] 2b. PO table submitted by the author (loop in tmux 'pulse'; 21 done at 2026-11-09 16:58 Hyak time).
- [x] 2c. PLU loop started by the author (tmux 'pulse_lu'; dry run 2026-11-09 17:09 Hyak time: 480 pending, queue 431/500).
      Both loops share the 500 limit; an sbatch refused by the QOS limit leaves its tasks pending for the next pass.
- [x] 3a. Fits finished and synced (2026-11-11).
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
- 2026-11-10: author added leak only and urgency only (linear and power); with and without sv as for the others
  (assumed, stated to the author). Table regenerated before any submission (indices changed; the 480-task version was
  never pushed or submitted): 960 tasks, 16 h for 60 (adds power leak PSUIM6, before 4.8 h, with and without sv).
- 2026-11-10: CORRECTION: the 480-task table had already been pulled and submitted (tmux "pulse"), so regenerating it
  as 960 tasks (6e05c24) changed indices under a running batch. No harm done (the running loop keeps the table it
  loaded; the author's --dry_run with the new file changes nothing), but a restart would have mismatched state and
  table. Fixed: tasks_2026-11-10_pulse.csv restored (regenerated byte-identical to 153d06d's); leak only and urgency
  only moved to a separate table/batch (PLU_*) with its own state. Lesson: never change a task table once pulled.
- 2026-11-10: author: start the long-running jobs first. PO 16 h tasks (48; power leak+urgency DBM6/PSUIM5/PSUIM6/
  PSUIM7, with/without sv) are queued in their own 16 h arrays: scontrol top (fallback: Nice=100 on the other pending
  arrays). PLU 16 h tasks (12; power leak-only PSUIM6) not yet submitted: autosubmit --to_lab
  scripts/slurm/to_lab_pulse_lu_long_2026-11-10.txt (lab tasks are submitted first, LAB_LIMIT 8 at a time).
- 2026-11-10: the 48 PO 16 h tasks were already submitted (job 43085922) and RUNNING: ckpt-all shows their limit as
  9:05:00 (partition cap; same as seen 2026-11-07), so filtering squeue on 16:00:00 found nothing. scontrol top not
  needed. Past the cap a task ends (requeue or TIMEOUT); autosubmit resubmits and the fit resumes from its checkpoint.
- 2026-11-10: author ran --to_lab for the 12 PLU 16 h tasks: 4 were pending on ckpt-all (43088811_8/_18,
  43089137_48/_58) and were cancelled; all 12 now pending for gpu-a100 (submitted by the pulse_lu loop, 8 at a time).
- 2026-11-10: the lab array 43089435 waited on "ReqNodeNotAvail, Reserved for maintenance" (16 h limit overlaps a
  gpu-a100 maintenance reservation). Author: submit them on the shared partition (fits checkpoint). Added autosubmit
  --now FILE: cancels still-PENDING submissions of the listed tasks, clears the lab flag, sbatches them at once on the
  default partition (ahead of table order). Tested with stub squeue/sbatch/scancel on a copy of the state: 8 cancelled,
  12 submitted in one array (--time=960, no -p), state submitted / attempts 1 / no partition; dry run changed nothing.
- 2026-11-10: author ran --now: 8 lab copies cancelled, all 12 PLU 16 h tasks submitted on the shared partition as job 43089560.
- 2026-11-11: after the Hyak restart the author synced: all 960 pulse-only fits present (PO 480, PLU 480), all load,
  name = content (mouse, variant, split, front end), finite train/test NLL, n_test of the pulse split = controls;
  25 resumed from a checkpoint; fit time median 0.3-0.4 h, max 3.7 h (none above its limit). No .ckpt/.tmp left.
  Nothing to resume. Next: step 3 (simulate, fit browser group).
