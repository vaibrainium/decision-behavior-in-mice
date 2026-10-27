# Plan: responded-only refits of control-trial models, then E-generated strategy recovery (F1a)
Status: active
Created: 2026-10-26 by Claude (Opus 5.5)
Related: plans/2026-10-26-paper-accumulation-variant.md; dissemination/paper_accumulation/np/decisions.md D002;
np/reviews/spine_challenge.md F1; reports/2026-10-23-pulse-data-20261023T191030Z_fa8de8b.md (mislabel)

## Goal
All control-trial numbers of the accumulation-first paper (model variant selection, accumulator vs rapid forgetting,
free-leak fit, final parameters) recomputed on corrected inputs, and a recovery test of whether the control-trial
comparison identifies rapid-forgetting (E) data.

## Context
- v1 inputs `ddm/ddm_inputs_global.npz` label 38 genuine UCLA no-response pulses as controls (replayed without pulse)
  and 5 unknown-direction pulses as controls. Corrected inputs already exist and are NOT modified:
  `pulse_followup/20261023T191030Z_fa8de8b/models/inputs_v2/ddm_inputs_global_v2.npz`
  (sha256 8b111911237dbae2c213fb28b7da6264b88f6a17bf3aa36445bce6468b1387ba; built at 84fedd7).
- `scripts/ddm/model_recovery.py --strategy` (added 2026-10-26, uncommitted): generators/candidates L0U0V1Z0G1 and
  L1U0V1Z0G1 with leak 20-200/s; control trials only; generating params from each model's control fit; 80 jobs.
  Smoke-tested locally (2 iterations, PSUIM10, existing v1 fits; scratchpad only).

## Decision rule for F1a (fixed 2026-10-26, before any job runs; D002)
Per (mouse, replicate) with E as generator: "scored as accumulator" if test NLL(E fit) - test NLL(I fit) > 10.
Count over 10 mice x 2 replicates = 20.
- <= 2/20: the comparison identifies E -> thesis may say the comparison recovered both models in simulation.
- >= 5/20: fails -> fallback thesis (spine_response.md).
- 3-4/20: partial; report the rate, keep the identifiability caveat.
Also reported: I-generated scored as E by > 10 (false E rate), and both "within 10" rates. Single test-set evaluation
at 15 reps (as the existing recovery); per-mouse Monte Carlo SD 6.5-12.8 NLL is a known limit.

## Assumptions
- The v2 file is synced to CLUSTER_DATA_PATH at the same relative path (user to rsync before submitting).
- Warm starts from the corresponding v1 fit folders are acceptable (applied equally to all variants).

## Steps (user submits; bash on Hyak; check each EXTRA_ARGS is non-empty)
REVISED 2026-10-27: responded-only (author rule: no trial without a response by 5 s in any analysis). Original inputs
`ddm/ddm_inputs_global.npz` + `--responded_only` (drops choice -1; likelihood conditional on a response by 5 s). Verified:
responded rows of v1 and v2 inputs are identical in every field (25,493 trials; 14,014 controls), so v2 is not needed.
Sync the code (fit_mouse_ddm.py, model_recovery.py, src/ddm/likelihood_calculator_censored.py) before submitting.
```
C="--responded_only --guess_model fast_only"
CCV="--splits ccv0 ccv1 ccv2 ccv3 ccv4"
# R1 common model, control-only CV (50)
env EXTRA_ARGS="$C --variants L0U0V1Z0G1 $CCV --warm_start_from ddm/fits_guess_fast_only --out_dir ddm/fits_resp_fast_only" sbatch --array=0-49 --time=16:00:00 scripts/slurm/fit_mouse_ddm.slurm
# R2 variant selection, control-only CV (250)
env EXTRA_ARGS="$C --variants L0U0V0Z0G1 L0U0V1Z0G0 L1U0V1Z0G1 L0U1V1Z0G1 L1U1V1Z0G1 $CCV --warm_start_from ddm/fits_guess_fast_only --out_dir ddm/fits_resp_fast_only" sbatch --array=0-249 --time=16:00:00 scripts/slurm/fit_mouse_ddm.slurm
# R3 guess bias fixed, control-only CV (50)
env EXTRA_ARGS="$C --variants L0U0V1Z0G1 $CCV --fixed_guess_bias --warm_start_from ddm/fits_guess_fast_only_FB --out_dir ddm/fits_resp_fast_only_FB" sbatch --array=0-49 --time=16:00:00 scripts/slurm/fit_mouse_ddm.slurm
# R4 rapid forgetting E, control-only CV + control (60)
env EXTRA_ARGS="$C --variants L1U0V1Z0G1 $CCV control --leak_bounds 20 200 --warm_start_from ddm/fits_guess_fast_only_leak20-200 --out_dir ddm/fits_resp_fast_only_leak20-200" sbatch --array=0-59 --time=16:00:00 scripts/slurm/fit_mouse_ddm.slurm
# R5 descriptive free leak 0-200, control (10)
env EXTRA_ARGS="$C --variants L1U0V1Z0G1 --splits control --leak_bounds 0 200 --warm_start_from ddm/fits_guess_fast_only_leak0-200 --out_dir ddm/fits_resp_fast_only_leak0-200" sbatch --array=0-9 --time=16:00:00 scripts/slurm/fit_mouse_ddm.slurm
# R6 final 50-rep fits, control + all (40)
env EXTRA_ARGS="$C --variants L0U0V1Z0G1 L1U1V1Z0G1 --splits control all --n_reps 50 --warm_start_from ddm/fits_final --out_dir ddm/fits_resp_final" sbatch --array=0-39 --time=16:00:00 scripts/slurm/fit_mouse_ddm.slurm
# AFTER R4 and R6 finish: F1a strategy recovery (80)
sbatch --array=0-79 --export=ALL,JOB_OFFSET=0,MODULE=scripts.ddm.model_recovery,EXTRA_ARGS="--responded_only --strategy --fits_dir ddm/fits_resp_final ddm/fits_resp_fast_only_leak20-200 --out_dir ddm/recovery_strategy_resp" --time=16:00:00 scripts/slurm/fit_mouse_ddm.slurm
```
- [x] 0. Code (--strategy, --responded_only, conditional likelihood), unit test, smoke tests, decision rule, commands.
- [ ] 1. User syncs code to Hyak; submits R1-R6 (460 fits).
- [ ] 2. Local: compare_strategy / control-only selection / guess-bias / free-leak / parameter table on fits_resp_*; new ledger rows replacing N014-N017, N045-N050, N110-N116, N118 for this paper (check the comparison scripts read test_nll only, not censored counts).
- [ ] 3. User submits F1a (80); local summary with the fixed rule; report.
- [ ] 4. Verify: responded-only vs earlier numbers side by side; G1 thesis wording chosen from the F1a outcome.

## Point 3 full re-run (amendment 9; author: "let's do full re-run", 2026-10-27)
Code (uncommitted, smoke-tested on PSUIM10 with tiny settings): `--responded_only` in primacy.py, fit_pulse_gain.py,
primacy_calibration.py, check_strategy_test.py; fits with the old likelihood are refused; gate 3 (censored fraction)
dropped. Pulse diagnostics (scripts/pulse_followup: ~10x excess, PSUIM6/7 gain trade-off) not yet adapted (local, later).
```
# P1-P2 AFTER R4 and R6: frozen pulse predictions (30)
env EXTRA_ARGS="--predict --responded_only --baselines primary secondary --fits_dir ddm/fits_resp_final --out_dir ddm/primacy_resp" sbatch --array=0-19 --export=ALL,JOB_OFFSET=0,MODULE=scripts.ddm.primacy --time=16:00:00 scripts/slurm/fit_mouse_ddm.slurm
env EXTRA_ARGS="--predict --responded_only --baselines extrema --fits_dir ddm/fits_resp_fast_only_leak20-200 --out_dir ddm/primacy_resp" sbatch --array=0-9 --export=ALL,JOB_OFFSET=0,MODULE=scripts.ddm.primacy --time=16:00:00 scripts/slurm/fit_mouse_ddm.slurm
# P3 AFTER R6: cross-validated pulse gain (20)
sbatch --array=0-19 --export=ALL,JOB_OFFSET=0,MODULE=scripts.ddm.fit_pulse_gain,EXTRA_ARGS="--responded_only --fits_dir ddm/fits_resp_final --out_dir ddm/primacy_revised_resp" --time=16:00:00 scripts/slurm/fit_mouse_ddm.slurm
# P4 AFTER P3: calibration and power (800)
for off in 0 400; do sbatch --array=0-399 --export=ALL,JOB_OFFSET=$off,MODULE=scripts.ddm.primacy_calibration,EXTRA_ARGS="--responded_only --fits_dir ddm/fits_resp_final --gain_dir ddm/primacy_revised_resp --out_dir ddm/primacy_calibration_resp" --time=16:00:00 scripts/slurm/fit_mouse_ddm.slurm; done
```
Before P2: amendment 5 rule: if E's drift_gain binds at 20 in the R4 fits, refit E with --drift_gain_max 200 first.
Local, in order: original gates (`primacy --analyze --gate_only --responded_only --unblind --out_dir ddm/primacy_resp --baseline primary|secondary`);
strategy test (`--strategy_test --responded_only --unblind --out_dir ddm/primacy_resp`); its power
(`check_strategy_test --power --responded_only --pred_dir ddm/primacy_resp`); revised gate (`primacy --analyze --gate_only
--responded_only --unblind --out_dir ddm/primacy_revised_resp`); calibration (`primacy_calibration --summarize --out_dir
ddm/primacy_calibration_resp`); timing test only if the revised gate passes (amendment 6 item 8); pulse diagnostics after adaptation.
- [ ] 5. P1-P4 submitted and finished; local steps above; report original vs responded-only side by side.

## Discrete-sample extrema detection, ES (amendment 10; author: "lets do both", 2026-10-27)
Simulator rule `extrema_bound` (both backends identical; zero-drift decision time matches theory), `--extrema_samples`
in fit_mouse_ddm, model_recovery (--strategy --extrema_samples, label ES), primacy (--baselines extrema_samples,
--strategy_model extrema_samples), check_strategy_test (--strategy_model extrema_samples). No warm start (new parameter).
```
# ES1 control-only CV + control (60)
ES1=$(env EXTRA_ARGS="--responded_only --guess_model fast_only --extrema_samples --variants L0U0V1Z0G1 --splits ccv0 ccv1 ccv2 ccv3 ccv4 control --out_dir ddm/fits_resp_fast_only_es" sbatch --parsable --array=0-59 --time=16:00:00 scripts/slurm/fit_mouse_ddm.slurm)
# ES3 pulse predictions (10), after ES1
sbatch --dependency=afterok:$ES1 --array=0-9 --export=ALL,JOB_OFFSET=0,MODULE=scripts.ddm.primacy,EXTRA_ARGS="--predict --responded_only --baselines extrema_samples --fits_dir ddm/fits_resp_fast_only_es --out_dir ddm/primacy_resp" --time=16:00:00 scripts/slurm/fit_mouse_ddm.slurm
# ES2 recovery (80), after ES1 and R6
sbatch --dependency=afterok:$ES1:$R6 --array=0-79 --export=ALL,JOB_OFFSET=0,MODULE=scripts.ddm.model_recovery,EXTRA_ARGS="--responded_only --strategy --extrema_samples --fits_dir ddm/fits_resp_final ddm/fits_resp_fast_only_es --out_dir ddm/recovery_strategy_es_resp" --time=16:00:00 scripts/slurm/fit_mouse_ddm.slurm
```
Local after: ES vs accumulator control CV (>10 rule), bound checks (b at 2 or 5, drift_gain at 200), strategy test
`primacy --strategy_test --strategy_model extrema_samples --responded_only --unblind --out_dir ddm/primacy_resp`, its power.
- [ ] 6. ES1-ES3 submitted; local comparison and report.

## Out of scope
No change to v1 inputs or v1 fits; the first paper version is unaffected.

## Log
- 2026-10-26: plan written after G1 answers (D002).
- 2026-10-27: switched from v2 inputs to responded-only (author: no-response and >5 s trials excluded from all analyses). Commands rewritten; outputs ddm/fits_resp_*, ddm/recovery_strategy_resp. Peer session src-46 handles responders-only pulse contrast and behavioural summaries (read-only).
- 2026-10-27: full point-3 re-run added (amendment 9, plan SHA prefix 2e1e22b0 at 02:12Z); code smoke-tested.
- 2026-10-27: amendment 10 (ES, Stine et al. 2020 sample rule) added; code smoke-tested; commands ES1-ES3.
- 2026-10-27: first Stage-1 submission (jobs 42415371-42415379, Hyak 19:20 PDT) ran with empty $C/$CCV (default single
  guess model, all-trial CV, no --responded_only); cancelled; its outputs moved on Hyak to
  ddm/archive/invalid_2026-10-27_empty-args/ (fits_resp_fast_only, fits_resp_fast_only_FB). Resubmitted with literal
  arguments; R1 log verified (ccv0, include_censored False). Job ids: R1 42422239, R2 42422438, R3 42422506,
  R4 42422510, R5 42422512, R6 42422579, P1 42422581 (after R6), P3 42422586 (after R6), P4 first half 42422652
  (after P3). P4 second half (JOB_OFFSET=400) refused by QOSMaxSubmitJobPerUserLimit; resubmit when the queue drains.
  Not yet submitted: P4 second half; ES1-ES3; after R4 + bound check: P2, F1a.
- 2026-10-27: ES submitted: ES1 42424538, ES3 42424540 (after ES1), ES2 42424542 (after ES1 and R6). Still pending:
  P4 second half (when queue < ~600), P2 + F1a (after R4 rsync and drift-gain bound check).
- 2026-10-27: P4 second half submitted: 42433981 (after P3). Remaining: P2 + F1a after R4 rsync and bound check.
- 2026-10-27: R4 bound check (local, rsynced fits): drift_gain max 5.05 (control) / 15.5 (ccv), none near 20 -> no
  amendment-5 refit; leak at lower bound 20/s in 2/50 ccv fits (caveat). P1/P3/ES2 released from the R6 dependency
  (all 20 R6 control fits present; only all-trial fits still running). P2 submitted: 42450548. F1a refused by
  QOSMaxSubmitJobPerUserLimit (~935 queued); resubmit when the queue drains.
- 2026-10-27: F1a submitted: 42451102 (16 h). All batches now queued; next: rsync processed/ddm/ when done, then local analysis.
- 2026-10-27: R6_35 preempted after > 5 h; R6_35, ES2 (42424542) and F1a (42451102) switched to Partition=gpu-a100,ckpt-all.
- 2026-10-27: R6_39 also preempted after > 5 h. R6_35 and R6_39 moved to gpu-a100 with Account=gpu-a100-walkerlab QOS=normal (ckpt account/QOS had kept them pending). ES2/F1a back on ckpt-all (ES2 tasks 1-4 had started under the mixed setting).
- 2026-10-27: degenerate responded-only fits found (conditional likelihood leaves response rate free; ~98% simulated
  non-responses in DBM13/PSUIM10 E, ES, R2 leak variant, R5 free leak). Amendment 11 (cap 50%) adopted and coded
  (4a06b1e); audit: all other fit sets <= 38%. F1a (42451102) and ES2 (42424542) cancelled; old P2/ES3 predictions
  moved to ddm/archive/precap_2026-10-27/ on Hyak and NAS. Refits with the cap: E 42454391 (fits_resp_fast_only_leak20-200_cap),
  ES 42454463 (fits_resp_fast_only_es_cap), R2 leak variant 42454549 (fits_resp_fast_only_cap), R5 free leak 42454615
  (fits_resp_fast_only_leak0-200_cap). Downstream: ES3 42454650 (after ES refit, -> primacy_resp), ES2 42454671 (after
  ES refit, -> recovery_strategy_es_resp_cap). P2 and F1a wait for the E refit and its drift-gain check.
  Pending audit: the 4 remaining R6 all-trial fits.
