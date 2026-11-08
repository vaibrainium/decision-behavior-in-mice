# Plan: input mapping x accumulator (is the accumulator conclusion robust to how motion maps to drift?)
Status: active
Created: 2026-11-06 by Claude (Opus 5.5)
Related: plans/2026-10-30-normalization-pulse-prediction.md (norm, control-only prediction);
plans/2026-11-06-nominal-coherence-joint-fits.md (nominal input); reports/2026-10-29-joint-control-pulse-refits.md
(linear joint fits, the "linear" arm here); plans/2026-10-25-amendment-7-normalization.md (F1/F2 defined; old fits
include no-response trials, not used)

## Goal
Author 2026-11-06 (after a colleague's question about nonlinear coherence-to-drift mappings, e.g. log/exponential in a
bird DDM paper): (1) refit the static power-law mapping under the no-response rule; (2) find out whether the choice of
accumulator (integrator variants vs extrema detection) depends on the input mapping. Done = held-out comparison of 3
mappings x 6 accumulators on the same joint folds, plus a frozen control-only pulse prediction for the power law.

## Context
- Mappings (applied to the drift input before the gain, all model paths, both simulator backends):
  linear (none); power F1: x' = sign(x)|x|^fe_gamma, fe_gamma 0.3-3 (Stevens-type; a signed log is undefined at 0%);
  norm F2: x' = x / (1 + fe_beta p(t)), p = causal exponential low-pass of |x| (fe_tau 0.02-1 s), fe_beta 0-20.
- Old F1 (2026-10-25, control-only ccv, with no-response trials): beat linear by -64.0 summed (2 SD MC noise 28.9);
  fe_gamma 0.62-0.77 in PSUIM5/6/7/10, DBM6, ~1 elsewhere.
- Arithmetic (2026-11-06): a static compressive mapping shrinks a pulse relative to low-coherence evidence (gamma 0.7 at
  9%: pulse push ~0.5x the linear model's after the gain refits), so F1 is expected to predict a SMALLER pulse effect;
  F2 raised it (3.19 -> 4.65 pp, 9 mice) by letting gain rise and sv/bound fall.
- Linear joint fits exist for all 6 accumulators (fits_joint_unfreeze_*), same inputs and folds (cv0-cv4 stratified by
  coherence x pulse condition, identical across families), so all held-out NLLs are paired.
- Why all trials for selection: pulse trials are randomized, valid data and 39-54% of each mouse's trials; using them
  in CV costs nothing and adds information. Why control-only for the pulse prediction: fitting pulses makes any pulse
  prediction circular. So: selection on joint CV (this plan), mechanism test on control-only fits (P1 here, norm plan).
- Limitation known in advance: adding pulses barely changed the linear ranking (joint report) and a free pulse weight
  leaves the likelihood flat up to w ~2-3, so the pulses add little likelihood information about the accumulator.

## Steps
- [ ] 1. Submit script scripts/slurm/submit_mapping_accumulator.sh (input md5 checks, new folders only):
      M1 power and M2 norm, joint (responded, cv0-cv4 + all, 15 reps, nofreeze inputs), each with primary L0U0V1Z0G1,
      leak L1U0V1Z0G1, urgency L0U1V1Z0G1, leak+urgency L1U1V1Z0G1 (240), E L1U0V1Z0G1 leak 20-200 (60),
      ES L0U0V1Z0G1 --extrema_samples (60): 720 fits.
      P1 power, control-only (responded, ccv0-ccv4 15 reps + control 50 reps), primary: 60 fits.
      N4 (nominal plan) nominal input + power, joint, primary: 60 fits. Total 840. Author submits.
- [ ] 2. Audit: counts, front_end and flags per folder, n_train, parameters at bounds, iteration cap.
- [ ] 3. Analysis code: compare_joint_refits families for the two mappings; pulse_joint_signatures for P1.
- [ ] 4. Comparison (rules fixed here, 2026-11-06, before any fit exists):
      A. Mapping, per accumulator: held-out NLL (sum cv0-cv4) of power - linear and norm - linear per mouse; t test
         and Wilcoxon over 10 mice, Holm over the 12 tests. A mapping "fits better" for a family if the summed
         difference is < -30 (above the measured 2 SD MC noise of 28.9) AND Holm p < 0.05.
      B. Accumulator robustness: within each mapping, ranking by summed held-out NLL minus primary; mice beyond 10
         either way. "The accumulator conclusion does not depend on the mapping" if in all 3 mappings (i) every
         integrator variant beats E and ES (paired Wilcoxon over mice, Holm within mapping) and (ii) the best family
         is the same; otherwise report the mapping-dependence as the result.
      C. Pulse signatures of each joint "all" fit: descriptive only (fitted on pulses).
      D. P1 (power, control-only): frozen pulse prediction, committed before comparing; same rule as the norm plan
         (per-mouse |error| vs the linear reference, paired Wilcoxon; mean toward the data).
- [ ] 5. Report; STATUS.

## Out of scope
Primacy or timing claims (procedure closed; would need its own amendment); log mapping (undefined at signed 0%);
per-site interpretation (rig is a covariate only).

## Log
- 2026-11-06: plan written ("yes, amend them"). Code check: make_params accepts power/norm with every accumulator,
  E leak bounds, extrema samples and nominal_matched; the simulator applies the front end before all model paths.
- 2026-11-06: author submitted (Hyak, at efdd33a): M_power_integrators 43010287 (240), M_power_leak20-200 43010288,
  M_power_es 43010289, M_norm_leak20-200 43010290, M_norm_es 43010291, P1_power_control 43010292 (10). Refused by
  QOSMaxSubmitJobPerUserLimit (~500 queued tasks): M_norm_integrators, P1_power_ccv, N4. Do not rerun
  submit_mapping_accumulator.sh (P1 folder will exist); use scripts/slurm/submit_remaining_2026-11-06.sh (queue-aware,
  each batch once).
- 2026-11-06: P1_power_ccv submitted (43013411). N4, M_norm_integrators and N1-N3 waiting (459 queued). Script now
  submits M_norm_integrators (240) and N1 (300) in 60-task chunks (same grid; indices unchanged).
- 2026-11-06: author asked for slot-based auto-submission with time limits from expected runtimes and retries with
  more time. scripts/slurm/make_task_table.py -> tasks_2026-11-06.csv (1,260 tasks; limits from finished fits of the
  same mouse and variant, x p90 slowdown: norm 8.3, nominal 1.77-2.26, power assumed 2.0; x1.5 + 15 min; 1-16 h).
  scripts/slurm/autosubmit.py (stdlib; tmux --watch): fills LIMIT - queued slots in priority order, rounds limits up to
  1/2/3/4/6/8/12/16/24/32/48 h, retries failures (TIMEOUT doubles the limit, max 48 h, 3 attempts), imports the jobs
  submitted earlier. Tested with stub squeue/sacct/sbatch: slot filling, timeout retry, just-submitted tasks counted,
  squeue failure survives --watch. submit_remaining_2026-11-06.sh superseded.
- 2026-11-07: step 3 code: scripts/ddm/compare_mapping_accumulator.py (audit, rules A, B, nominal 5a; partial data
  reported as such); pulse_joint_signatures: EXTRA_FAMILIES (power/norm/nominal joint "all" fits) and --fe_power (P1);
  primacy.make_model(nominal_matched=). Tested on the real linear fits plus fake mapping folders (scratch output only):
  the linear ranking reproduces the 2026-10-29 report exactly; rule A detects a planted -50/mouse shift.
- 2026-11-07: ISSUE for the author (rule not changed): on the existing linear fits, rule B's test (each integrator vs
  E and ES, paired Wilcoxon, Holm within mapping) already fails: summed differences -300 to -590 favour the integrators
  but rest on 4-6 mice (Holm p 0.06-0.92). So rule B would say "mapping-dependent" even if every mapping agreed with
  linear. Also the code compared no_sv too, which is not in this plan's integrator list (no power/norm no_sv fits).
  Options to decide BEFORE the power/norm results are synced: keep B; or B' = robustness as agreement with linear
  (same best family; each integrator-vs-extrema summed difference keeps its sign and stays beyond 10 NLL in the same
  number of mice +-1); or use the control paper's paired-cohort rule (D004) for C > E per mapping.
- 2026-11-08: AUTHOR DECISION: exploratory analysis; no decision rules for now (the comparison rules written above are
  suspended, not applied). Rules to be discussed once all results are in. compare_mapping_accumulator.py reports
  descriptives only (sums, medians, mice beyond 10 NLL, uncorrected p as descriptives; no verdicts, no Holm). The
  rule-B issue logged 2026-11-07 is moot for now; keep it for the rules discussion.
- 2026-11-08: author: see which running tasks were restarted (preempted on ckpt-all) and move long ones to the lab
  GPUs. Added scripts/slurm/task_report.py (read-only: restarts from scontrol, hours lost from sacct --duplicates,
  expected hours from the task table; writes candidates) and autosubmit.py --to_lab FILE (cancels listed queued tasks,
  resubmits them on gpu-a100 / walkerlab, LAB_LIMIT 8 at a time, longest expected first; RUNNING tasks only with
  --include_running; state re-read under a lock every pass, so it is safe while --watch runs). Tested with stub Slurm
  commands (report, dry run, move, lab cap with another lab job present, ordering).
