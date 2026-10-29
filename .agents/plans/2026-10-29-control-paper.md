# Plan: control-trial-only paper on mouse RDK decisions (neuropaper, third project)
Status: active
Created: 2026-10-29 by Claude (Opus 5.5)
Related reports: reports/2026-10-28-stine-exact-models.md, reports/2026-10-28-recovery-synthetic-data-mismatch.md,
reports/2026-10-23-control-only-selection.md, reports/2026-10-26-fluctuation-kernel-observed.md

## Goal
A full neuropaper manuscript in `dissemination/paper_control/` on how mice make visual decisions about dynamic
random-dot motion, using control trials only, modeled on Stine et al. 2020 (eLife 9:e55365): behavior (psychometric,
chronometric, RT distributions), motion-energy kernels, integration vs non-integration model comparison, and paired
model recovery.

## Context
- Author choices 2026-10-29: new third project folder (paper and paper_accumulation untouched); plan the recovery rerun;
  add psychophysical kernels and chronometric/RT-distribution analyses.
- Existing control-trial evidence: held-out comparison and components (paper_accumulation D006/D008 tables),
  control-split parameters, paper-exact Stine models.
- Fixed rules: no trials without a response by 5 s; rig is a covariate only; sv model set; no free-leak fits.

## Assumptions
- Control-trial held-out comparisons (heldout_*/components_* 2026-10-28) are on responded control trials only and are
  unaffected by the recovery bug (stated in the bug report; re-check provenance at S0 inventory).
- Fig 1 v2 psychometric/RT panels already use responded control trials (fig1_behaviour.py docstring); verify per panel.
- Kernels are descriptive: Stine 2020 shows kernels do not separate integration from non-integration.

## Steps
- [x] 1. np init in dissemination/paper_control; config.md; 44 verified sources and notes copied; G0 checkpoint.
- [x] 2. G0 approval (D001, "you choose").
- [ ] 3. Recovery rerun [code + datasets DONE 4dbef52; author to run the commands below] (needs author OK for the cluster job): implement CPU pre-generation of synthetic control
      datasets with sha256 and `model_recovery --datasets`; check determinism and pairing locally; write the sbatch
      command for the author to submit (C, E, DDMx, ESx; 16 cells x 20 datasets = 320 fits).
- [x] 4. New descriptive analyses (fix definitions in this plan before running on real data): (a) stimulus- and
      response-aligned motion-energy kernels on responded control trials, per mouse, group with mice as unit;
      (b) chronometric curves, RT quantiles per |coherence|, correct vs error RTs, per mouse and group.
      **Definitions fixed 2026-10-29 before any real-data run (D001 item 4):**
      Trials: `ddm_inputs_global.npz`, sched_pulse_type == 0, choice >= 0 (response at 0.3-5 s); 14,014 trials,
      10 mice (count checked; no outcome looked at). Mice are the unit; per-mouse values, then group mean with t 95% CI,
      one-sample t and Wilcoxon, Holm over the family of confirmatory tests below (3 tests), dz. Rig is not a factor.
      (a) Kernels. Signal: noise array N(t) (motion energy minus the expected signal component, % coherence), frames
          before the response only. Trials with |coh| <= 36%. Per mouse and signed coherence: mean N for right minus
          left choices; averaged over signed coherences weighted by trial count (cells need >= 5 trials of each
          choice). Bins of 100 ms: stimulus-aligned 0-1.0 s; response-aligned -1.0-0 s.
          Test K1: per-mouse mean stimulus-aligned kernel over 0.1-0.5 s > 0 (choices depend on within-trial motion
          energy). Shape is descriptive only. Model reference (descriptive, no selection): the same kernels computed on
          choices/RTs simulated (CPU, 20 reps, fixed seeds) from each mouse's control fit of the common model
          (fits_resp_final, L0U0V1Z0G1) and of rapid forgetting E (fits_resp_fast_only_leak20-200_cap); reported as
          overlay with the per-mouse SD over reps. A trial-mean-removed (fluctuation-only) kernel is a supplement.
      (b) Chronometry. Per mouse and |coh|: median RT of correct trials (all trials at 0%); RT quantiles 0.1/0.3/0.5/
          0.7/0.9 for correct and error trials. Test T1: per-mouse Spearman rho between |coh| and median correct RT < 0.
          Test T2: per-mouse error minus correct mean RT, averaged over |coh| in {9, 18, 36}% cells with >= 10 errors
          (weighted by error count); sign tested against 0 (two-sided). 100% coherence errors shown, not tested.
          Model reference: quantiles from the same common-model and E simulations (descriptive).
      Outputs: tables in dissemination/paper_control/tables/*_2026-10-29.csv; per-trial intermediates under
      /mnt/data/processed/ddm/control_paper/. Script: scripts/ddm/control_descriptives.py.
      Result: reports/2026-10-29-control-descriptives.md.
      Hyak commands for step 3 (author runs):
        rsync -a /mnt/data/processed/ddm/recovery_datasets_cpu_2026-10-29/ vthakur@klone.hyak.uw.edu:/gscratch/walkerlab/vaibhav/mouse-pulse-data/processed/ddm/recovery_datasets_cpu_2026-10-29/
        (on Hyak: git pull to >= 4dbef52)
        sbatch --array=0-319 --export=ALL,JOB_OFFSET=0,MODULE=scripts.ddm.model_recovery,EXTRA_ARGS="--strategy --full --responded_only --fits_dir ddm/fits_resp_final ddm/fits_resp_fast_only_leak20-200_cap ddm/fits_resp_nominal_ddm_g001 ddm/fits_resp_nominal_es --datasets ddm/recovery_datasets_cpu_2026-10-29 --out_dir ddm/recovery_full_cpu_resp" --time=16:00:00 scripts/slurm/fit_mouse_ddm.slurm
        then: bash scripts/sync_ddm_data.sh pull; check every output has datasets_dir set and equal n_train/n_test per dataset.
      ES extension (D002 item 1): 20 ES datasets added to the same folder (manifest now 100, all sha256 OK; ES CPU
      synthesis deterministic, PSUIM10 two processes). Commands (author runs):
        rsync -a /mnt/data/processed/ddm/recovery_datasets_cpu_2026-10-29/ vthakur@klone.hyak.uw.edu:/gscratch/walkerlab/vaibhav/mouse-pulse-data/processed/ddm/recovery_datasets_cpu_2026-10-29/
        (on Hyak: git pull to the ES-cells commit)
        sbatch --array=0-179 --export=ALL,JOB_OFFSET=0,MODULE=scripts.ddm.model_recovery,EXTRA_ARGS="--strategy --full --es_cells --responded_only --fits_dir ddm/fits_resp_final ddm/fits_resp_fast_only_leak20-200_cap ddm/fits_resp_nominal_ddm_g001 ddm/fits_resp_nominal_es ddm/fits_resp_fast_only_es_cap --datasets ddm/recovery_datasets_cpu_2026-10-29 --out_dir ddm/recovery_full_cpu_resp" --time=16:00:00 scripts/slurm/fit_mouse_ddm.slurm
- [ ] 3b. Recovery analysis at the group-test level (D002 item 2) and motion-energy ablation (D002 item 3): definitions
      to be fixed here before any run.
- [ ] 5. Seed np/ledger/numbers.csv with control-only rows (source file per row).
- [ ] 6. S1 spine -> G1; S2 targeted lit search (Stine-style integration vs non-integration, mouse RDK) -> G2;
      S3 -> G3; S4-S8 per neuropaper workflow.
- [ ] 7. Verify: integrity audit PASS; every number traces to a control-only, responded-only source.

## Out of scope
Pulse trials (effects, primacy, pulse gain); no-response trials; site comparisons; free-leak fits; edits to the
other two paper projects.

## Log
- 2026-10-29: started at author request; S0 written; waiting at G0.
- 2026-10-29: G0 approved (D001). Step 3 code: model_recovery --make_datasets/--datasets/--full; CPU synthesis
  deterministic across two processes (PSUIM10, 4 generators, identical hashes; scratchpad det.py). 80 datasets being
  written to /mnt/data/processed/ddm/recovery_datasets_cpu_2026-10-29 (manifest.json with sha256).
- 2026-10-29: step 4 script scripts/ddm/control_descriptives.py. Real-data-only run done first (definitions unchanged
  after it); sign check: signal tracks signed coherence, pooled right-left N ~0.3% coh, fluctuation-only ~0.
- 2026-10-29: descriptives done; kernel K1 null and underpowered (sim SD ~ effect); fast errors under-predicted by the common model (exploratory). Report written.
- 2026-10-29: author submitted the 320-fit paired recovery: Slurm job 42579825 (out_dir ddm/recovery_full_cpu_resp). Next: pull, validity check (320 outputs, datasets_dir set, equal n_train/n_test per dataset), confusion matrix, THESIS rule.
- 2026-10-29: D002 (author "ok"): ES added to recovery (180 jobs, same out_dir), group-level calibration, ME ablation. ES code + datasets done.
