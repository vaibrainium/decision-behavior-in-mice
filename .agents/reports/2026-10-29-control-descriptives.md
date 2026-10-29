# Report: control-trial descriptives (kernels, chronometry) and paired recovery datasets
Date: 2026-10-29   Agent: Claude (Opus 5.5)   Commit: 4dbef52 (+ script commit below)
Plan: plans/2026-10-29-control-paper.md (steps 3-4)

## Question
For the control-only paper (Stine et al. 2020 framing): do choices depend on within-trial motion energy (kernels), how
do RT and errors depend on coherence, and do the common model and rapid forgetting (E) reproduce these? Also: fix the
unpaired recovery so that it can be rerun.

## Summary
On 14,014 responded control trials from 10 mice, RT falls weakly with coherence and errors are faster than correct
responses. The motion-energy kernel is small (about 0.1-0.3% coherence) and, with these trial counts, cannot be
distinguished from 0 or from either model. Within-mouse simulation SD (0.2-1.1) is as large as the predicted kernel
(about 0.3-0.5), so the kernel analysis is underpowered. The common model under-predicts fast errors (exploratory).
Paired recovery datasets now exist (80, CPU, sha256); the 320-fit rerun awaits submission by the author.

## Findings
Source: `python -m scripts.ddm.control_descriptives --n_reps 20` (definitions fixed in the plan before the run);
tables in `dissemination/paper_control/tables/control_{tests,per_mouse,kernels,chronometry}_2026-10-29.csv`.
Mice are the unit. Two-sided tests, Holm over the 3 pre-specified tests.
- VERIFIED. K1 (stimulus-aligned kernel 0.1-0.5 s, |coh| <= 36%): mean 0.14% coh, 95% CI [-0.36, 0.63], t p 0.55
  (Holm 0.55), Wilcoxon 0.28, dz 0.19. Not different from 0. Likely underpowered (see below).
- VERIFIED. T1 chronometric rho(|coh|, median correct RT): mean -0.49 [-0.88, -0.10], t p 0.020 (Holm 0.061),
  Wilcoxon 0.029 (Holm 0.088), dz -0.89. Group median correct RT 1.35 s at 9% and 1.16 s at 100% (0%: 1.44 s, all
  trials). The trend is in the expected direction, but it does not survive Holm.
- VERIFIED. T2 error minus correct mean RT (9/18/36% cells with >= 10 errors): -0.118 s [-0.214, -0.022], t p 0.022
  (Holm 0.061), Wilcoxon 0.065 (Holm 0.129), dz -0.88. Errors are faster in 9/10 mice (DBM13 +0.20 s).
- VERIFIED, descriptive. Model kernels (20 sims per mouse, same stimuli): stimulus-aligned, both models rise to about
  0.4-0.55% coh from 0.3 s; data about 0.1-0.2. Response-aligned: E peaks about 1.0 at -0.7 to -0.5 s, the common
  model about 1.0 at -0.4 to -0.3 s, and the data are flat at about 0.25-0.5. The kernel is driven by the per-trial
  mean of the noise: the fluctuation-only kernel is about 0.
- EXPLORATORY (not pre-specified). Data minus model per mouse: K1 common -0.18 [-0.67, 0.31] (p 0.43), E -0.22
  (p 0.38). Response-kernel mean: common -0.37 (p 0.16), E -0.34 (p 0.17). Fast errors: data minus common
  -0.071 s [-0.139, -0.003] (t p 0.042, Wilcoxon 0.084), data minus E -0.044 (p 0.20). Inline script in this
  session; reproduce from control_per_mouse and control_kernels tables.
- VERIFIED. Model accuracy matches the data at 9% (0.54 vs 0.54) and is slightly low at 18-36% (common 0.59/0.67 vs
  data 0.64/0.71).
- VERIFIED. Recovery fix: CPU synthesis gives identical hashes in two processes. 80 datasets are in
  `/mnt/data/processed/ddm/recovery_datasets_cpu_2026-10-29/` (manifest sha256 all match). In the smoke test (PSUIM10,
  C-generated rep0; candidates C, E, DDMx; 2 iterations), all three loaded the same file and had n_train = n_test = 206.

## What didn't work
- The kernel as a test of evidence use: per-mouse noise is as large as the effect, so it cannot separate the models,
  and with 10 mice it cannot separate 0 either. Stine et al. 2020 show that kernels are uninformative about strategy
  even with power.

## How to reproduce
`cd /src && .venv/bin/python -m scripts.ddm.control_descriptives --n_reps 20` (CPU, about 10 min). Inputs:
`processed/ddm/ddm_inputs_global.npz`; fits: `fits_resp_final` (L0U0V1Z0G1 control) and
`fits_resp_fast_only_leak20-200_cap` (L1U0V1Z0G1 control).
Datasets: `python -m scripts.ddm.model_recovery --strategy --full --responded_only --fits_dir ddm/fits_resp_final
ddm/fits_resp_fast_only_leak20-200_cap ddm/fits_resp_nominal_ddm_g001 ddm/fits_resp_nominal_es --make_datasets
--datasets ddm/recovery_datasets_cpu_2026-10-29`.

## Caveats
- Kernels use the reconstructed motion-energy noise N(t). The earlier hidden-coherence analysis (k = 0.50) suggests
  that mice use only part of it. Screen geometry is not corrected.
- 0% coherence trials enter the chronometric curve with all responses. 100% errors are shown, not tested.
- The model references use the fitted parameters, with no refit per simulation.

## Open questions and next steps
- [ ] Author: push the datasets to Hyak, sync the code, submit the 320 fits (commands in the plan, step 3).
- [ ] Power for a pooled kernel (all mice, mixed model), if the kernel is to be kept beyond a supplement.
- [ ] Fast errors under-predicted by the common model: check against the known high-coherence error misfit (sv absorbs it).
- [ ] S1 spine for the control paper.
