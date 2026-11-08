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
- [ ] 3c. Nominal-coherence refits of C, E, ES (D003; code --nominal_matched, smoke-tested PSUIM10 ccv0: PSUIM10 test
      NLL ~31 like the motion-energy fits, small folds drop the RT term). Author runs (after git pull on Hyak):
        sbatch --array=0-49 --export=ALL,JOB_OFFSET=0,MODULE=scripts.ddm.fit_mouse_ddm,EXTRA_ARGS="--responded_only --guess_model fast_only --nominal_input --nominal_matched --variants L0U0V1Z0G1 --splits ccv0 ccv1 ccv2 ccv3 ccv4 --out_dir ddm/fits_resp_nominal_matched_C" --time=16:00:00 scripts/slurm/fit_mouse_ddm.slurm
        sbatch --array=0-49 --export=ALL,JOB_OFFSET=0,MODULE=scripts.ddm.fit_mouse_ddm,EXTRA_ARGS="--responded_only --guess_model fast_only --nominal_input --nominal_matched --variants L1U0V1Z0G1 --splits ccv0 ccv1 ccv2 ccv3 ccv4 --leak_bounds 20 200 --out_dir ddm/fits_resp_nominal_matched_E" --time=16:00:00 scripts/slurm/fit_mouse_ddm.slurm
        sbatch --array=0-49 --export=ALL,JOB_OFFSET=0,MODULE=scripts.ddm.fit_mouse_ddm,EXTRA_ARGS="--responded_only --guess_model fast_only --nominal_input --nominal_matched --variants L0U0V1Z0G1 --splits ccv0 ccv1 ccv2 ccv3 ccv4 --extrema_samples --out_dir ddm/fits_resp_nominal_matched_ES" --time=16:00:00 scripts/slurm/fit_mouse_ddm.slurm
      Comparison rule fixed now: per model, (NLL_nominal - NLL_ME) per 1,000 control trials, mice as unit, t and
      Wilcoxon, Holm over 3; > 0 means the motion-energy input predicts better. Also C_nom vs E_nom / ES_nom ranking.
      Scored with scripts/ddm/control_heldout.py (to add the _nom models).
- [x] 3d. Held-out recomputation (scripts/ddm/control_heldout.py) reproduces heldout_per_trial_2026-10-28 exactly;
      leave-one-mouse-out: all alternatives keep mean > 0 and max uncorrected p_t <= 0.037 (Wilcoxon <= 0.074).
- [ ] 3b. Recovery analysis at the group-test level (D002 item 2) and motion-energy ablation (D002 item 3): definitions
      to be fixed here before any run.
      **Definitions fixed 2026-10-30 after G1 (D004), before any recovery likelihood is read:**
      Input: recovery_full_cpu_resp/*.pkl (validity checked: 320, paired, datasets_dir set). Per dataset (mouse,
      generator, replicate) and alternative X in {E, ES, DDMx, ESx}: d = (test_nll_X - test_nll_C) / n_test * 1000
      (> 0: C predicts better; one held-out split per dataset, unlike the 5-fold real data). Cohorts: all 2^10 = 1,024
      choices of one replicate per mouse (enumerated, not sampled). Per cohort: one-sample t over the 10 mice per X,
      Holm over the 4 alternatives; reproduces for X if mean d_X > 0 and Holm p_X < 0.05. X separated if
      P(reproduce | X-generated) <= 0.10 and P(reproduce | C-generated) >= 0.50. Decisive: E and ES -> variant A
      (both), I_E / I_ES (one), B (neither). Secondary: per-dataset counts d * n_test / 1000 > 10 NLL (C favored) with
      Clopper-Pearson 95% CIs; full confusion of best-fitting candidate per dataset.
      While ES fits are missing: Holm over the 4 is not computable. Provisional E result reported under Bonferroni x4
      (p_E * 4 < 0.05; conservative, always >= Holm-4) and under Holm over the 3 available (anti-conservative);
      decision only if both give the same verdict, else wait for ES. Final verdict only with all 4.
      Script: scripts/ddm/recovery_cohorts.py; tables dissemination/paper_control/tables/recovery_*_2026-10-30.csv.
- [ ] 5. Seed np/ledger/numbers.csv with control-only rows (source file per row).
- [ ] 6. [S1 + G1 done 2026-10-30, D004] S1 spine -> G1; S2 targeted lit search (Stine-style integration vs non-integration, mouse RDK) -> G2;
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
- 2026-10-29: shuffled-ME ablation dropped before running: likelihood pools per coherence, shuffle within coherence = seed noise (reports/2026-10-29-likelihood-ignores-trial-me.md). D002 item 3 needs re-decision (choice/RT split local; nominal refits optional).
- 2026-10-29: D003 recorded; nominal_matched code + control_heldout.py; held-out table provenance restored (exact reproduction).
- 2026-10-30: G1 approved (D004, "approve"); spine locked; S2. 3b definitions fixed, then recovery_cohorts.py on 42579825: valid; E separated (Holm-3 and Bonferroni-4 agree), provisional until ES cells (reports/2026-10-30-paired-recovery-cohorts.md). Next: author submits ES cells + nominal refits; S2 literature.
- 2026-10-30: author submitted ES recovery cells (Slurm 42590287, 180, out_dir ddm/recovery_full_cpu_resp) and nominal_matched refits C/E/ES (42590292, 42590294, 42590301; 50 each). Next: sync pull, rerun recovery_cohorts.py (final A vs I_E), score _nom models in control_heldout.py.
- 2026-10-30: synced. Recovery 400/500: ES-generated jobs (42590287 idx 40-89,130-179) missing. E separated with Holm-4 (final); ES pending. Nominal refits scored: ME not better than nominal (C +0.96, Holm 0.60); C > E, ES on nominal input. reports/2026-10-30-es-recovery-partial-and-nominal-refits.md. Next: resubmit the 100 ES-generated jobs.
- 2026-10-30: author resubmitted the 100 ES-generated recovery jobs (Slurm 42620010, idx 40-89,130-179). Next: sync pull, rerun recovery_cohorts --suffix _v3 -> final A vs I_E.
- 2026-10-30: 42620010 failed (all 100, ~20 s each): KeyError in load_dataset, manifest.json had 80 entries, no ES. Cause (SUSPECTED): a sync pull replaced the local 100-entry manifest with the older Hyak copy (mtime 2026-10-29 20:03, before the ES run). Fix: ES datasets regenerated on CPU into scratch, all 20 byte-identical (sha256) to the existing files; manifest now 100 entries (80 unchanged), all hashes verified; old one kept as manifest_80_before-es_2026-10-29.json. Local job 40 now loads and fits. Next: rsync the folder to Hyak, resubmit indices 40-89,130-179.
- 2026-10-30: author resubmitted the 100 ES-generated recovery jobs after the manifest fix: Slurm 42623537 (idx 40-89,130-179). Next: sync pull, rerun recovery_cohorts --suffix _v3 -> final A vs I_E.
