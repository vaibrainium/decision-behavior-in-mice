# Plan: DDM families fitted on the nominal coherence sequence (control + pulse trials)
Status: done
Created: 2026-11-06 by Claude (Opus 5.5)
Related reports: reports/2026-10-29-joint-control-pulse-refits.md (motion-energy joint fits);
reports/2026-10-30-es-recovery-partial-and-nominal-refits.md (nominal vs ME on control trials: no difference);
reports/2026-10-30-pulse-weight-joint.md; plans/2026-10-30-normalization-pulse-prediction.md

## Goal
Author request 2026-11-06: fit the DDM variants on the coherence shown on each frame (e.g. 9, 9, 9, 9, -100, -100, -100,
9, ...) instead of motion energy, on all responded trials (RT < 5 s, control + pulse). Done = held-out comparison with the
motion-energy joint fits of the same families on the same folds, and simulated pulse effects compared with the data.

## Context
- Input already implemented: fit_mouse_ddm --nominal_input --nominal_matched builds, per trial, the signed coherence held
  from stimulus onset and the scheduled pulse coherence (+-100%) over the logged pulse frames (pulse_timing_global.npz).
  Checked 2026-11-06 on a UCLA trial (9% with a -100% pulse, frames 4-6) and a UW trial (frames 3-6): exactly that sequence.
  No motion-energy filter, onset transient or frame noise.
- Measured 2026-11-06 (pulse trials with |pulse - coherence| > 0.5): the motion-energy pulse integral divided by the
  nominal pulse integral (coherence x s, after the ME coherence slope, 1.02 UCLA / 1.01 UW) is 1.00 (UCLA) and 1.09 (UW),
  IQR width ~0. So relative to coherence the pulse is the same size in both inputs; the nominal input differs by
  dropping the frame noise and filtering, not by a stronger pulse.
- Expectation (stated before fitting): the predicted pulse effect will not reach the data (5.48 pp, 0.3-1.2 s), because
  the motion-energy joint families predict 2.3-4.5 pp, the Stine nominal models 2.3-2.7 pp, and a free pulse weight stays ~1.
- Same inputs file and folds as the motion-energy joint fits (ddm_inputs_global_ucla_nofreeze.npz; cv0-cv4 stratified by
  coherence x pulse condition, identical across families), so held-out NLLs are paired.

## Assumptions
- Responded trials only (no-response rule); likelihood conditional on a response by 5 s (--responded_only).
- 15 reps for cv and "all" splits, as the motion-energy joint fits.

## Steps
- [x] 1. Smoke test locally: PSUIM10 cv0, primary variant, nominal_matched, 2 iterations (pulse trials + full model on
      nominal input has not run before).
- [x] 2. Submit script scripts/slurm/submit_joint_nominal.sh (input md5 checks, new folders only). Families
      (nominal_matched, guess fast_only): primary L0U0V1Z0G1, no sv L0U0V0Z0G1, leak L1U0V1Z0G1, urgency L0U1V1Z0G1,
      leak+urgency L1U1V1Z0G1 (one array, 300), E L1U0V1Z0G1 leak 20-200 (60), ES L0U0V1Z0G1 --extrema_samples (60).
      420 fits. Author submits on Hyak.
- [ ] 3. Audit: 420 fits, nominal_input and nominal_matched set, n_train = responded trials, bounds, iteration cap.
- [ ] 4. Analysis code: compare_joint_refits and pulse_joint_signatures accept the nominal families.
- [ ] 5. Comparison (rule fixed here, 2026-11-06, before any fit exists):
      a) Held-out NLL, nominal minus motion-energy, per family, summed over cv0-cv4, per 1,000 trials; mice as units;
         t test and Wilcoxon, Holm over the 7 families. < 0 = nominal predicts better.
      b) Ranking of the families on nominal input (same rules as the joint report: sum, mice beyond 10).
      c) Pulse effect of each nominal "all" fit (pulse_joint_signatures statistic, 30 reps, seed 0): mean over mice in the
         0.3-1.2 s window vs data 5.48 pp and vs the motion-energy family; per-mouse RMSE; 1.2-5 s window.
         "Nominal input captures the pulse better" only if a family's per-mouse error is lower than its motion-energy
         version (paired Wilcoxon, p < 0.05) AND its mean moves toward 5.48 pp.
- [ ] 6. Report, STATUS.

## Out of scope
Pulse-time or pulse weights on nominal input; primacy claims (the primacy procedure stays closed; any timing test needs
its own amendment); per-site interpretation (rig is a covariate only).

## Log
- 2026-11-06: plan written at the author's request.
- 2026-11-06: step 1 done: PSUIM10 cv0 primary (2 iterations, 2 reps) runs; n_train 327 + n_test 98 = 425 responded
  trials incl. pulse, n_train_censored 0, nominal_input and nominal_matched set. Step 2: submit_joint_nominal.sh written;
  local md5s of both inputs match the script; grids 300 / 60 / 60 (--list). Next: author git pull + submits on Hyak.
- 2026-11-06: added N4 (author "amend them"): nominal input + power-law mapping, primary model, joint, 60 fits; the
  bird-paper analogue (compressive coherence-to-drift mapping on the coherence sequence). Submitted from
  scripts/slurm/submit_mapping_accumulator.sh; compared under rule 5a (vs nominal linear primary) and with the
  mapping plan (plans/2026-11-06-input-mapping-x-accumulator.md).
- 2026-11-06: not yet submitted. N1-N3 moved into scripts/slurm/submit_remaining_2026-11-06.sh (queue-aware, after the
  mapping batches); do not also run submit_joint_nominal.sh.
- 2026-11-08: AUTHOR DECISION: exploratory analysis; no decision rules for now (the comparison rules written above are
  suspended, not applied). Rules to be discussed once all results are in. compare_mapping_accumulator.py reports
  descriptives only (sums, medians, mice beyond 10 NLL, uncorrected p as descriptives; no verdicts, no Holm). The
  rule-B issue logged 2026-11-07 is moot for now; keep it for the rules discussion.
- 2026-11-09: all 1,260 fits in; final descriptive comparison and pulse signatures done (exploratory, rules
  suspended). Report: reports/2026-11-09-mapping-accumulator-exploratory.md. Plan closed; rules discussion with the author is the next step.
