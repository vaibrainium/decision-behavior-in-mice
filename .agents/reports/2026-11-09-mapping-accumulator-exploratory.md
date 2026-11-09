# Report: input mapping x accumulator and nominal-coherence joint fits (exploratory, all 1,260 fits)
Date: 2026-11-09   Agent: Claude (Opus 5.5)   Commit: e432946 (+ this report's commit)
Plans: plans/2026-11-06-input-mapping-x-accumulator.md, plans/2026-11-06-nominal-coherence-joint-fits.md

## Question
Does a nonlinear coherence-to-drift mapping (static power law, divisive normalization) or the nominal coherence sequence
instead of motion energy (ME) change (a) which accumulator predicts held-out choices and RTs best, (b) whether
integrators beat extrema models, and (c) whether any family reproduces the pulse effect (data 5.48 pp, 0.3-1.2 s)?

STATUS OF THE ANALYSIS: EXPLORATORY (author decision 2026-11-08). The plans' decision rules are suspended; everything
below is descriptive (sums, medians, mice beyond 10 NLL, uncorrected p as descriptives only). No claim is confirmed.

## Summary
- Both nonlinear mappings fit slightly better than linear ME for every accumulator (power -39 to -123, norm -54 to -197
  summed held-out NLL over 10 mice), carried by 2-4 mice; the fitted power exponent is compressive in most mice (median
  0.70-0.89).
- Integrators beat E and ES under all four inputs/mappings (-241 to -593); leak+urgency is best under linear, power and
  norm, leak under the nominal sequence. The mapping does not change the accumulator ranking.
- No family reproduces the pulse effect per mouse (RMSE 5.3-6.9 pp for all 32 families). Integrator means range from
  2.3 (nominal) to 5.3 pp (norm leak); every integrator predicts a late (1.2-5 s) reversal the data do not show.
- Nominal coherence instead of ME: mixed (primary +117 worse, no_sv -164 better); adding a power law to the nominal
  sequence recovers the ME-linear fit (-10) but not ME-power (+29).

## Findings
Held-out NLL = sum over cv0-cv4 per mouse, then summed over 10 mice; negative = first model better.
Source: `python -m scripts.ddm.compare_mapping_accumulator --tag _final` ->
dissemination/figures/qc/mapping_accumulator_{audit,heldout_nll,mapping_vs_linear,ranking,integrator_vs_extrema,nominal,params}_2026-11-09_final.csv.
Fits: ddm/fits_joint_{unfreeze,power,norm,nominal}_* and fits_joint_nominal_power, inputs ddm_inputs_global_ucla_nofreeze.npz
(md5 f18e0e6b...), responded trials only (RT < 5 s), control + pulse, identical folds.

1. Audit (VERIFIED): 1,260/1,260 new fits + 420 linear reference; 0 optimizer failures, 0 at the iteration cap.
   Recurrent bounds: guess_tau at its upper bound in most families (also in the linear reference); fe_beta at 0 (= no
   normalization) in 5-11 of 60 fits per norm family; drift_offset at its upper bound in ES fits (10-11 of 60).
2. Mapping minus linear (VERIFIED, mapping_vs_linear_*_final.csv):
   | accumulator | power - linear | norm - linear |
   |---|---|---|
   | primary | -39 (2 better >10 / 1 worse) | -54 (2 / 1) |
   | leak | -98 (3 / 0) | -87 (3 / 1) |
   | urgency | -109 (4 / 0) | -88 (2 / 1) |
   | leak+urgency | -123 (3 / 0) | -85 (2 / 0) |
   | E | -95 (3 / 2) | -123 (2 / 1) |
   | ES | -119 (3 / 1) | -197 (3 / 1) |
   Medians -1.7 to -5.9 per mouse; uncorrected p 0.05-0.49. Small and concentrated in a few mice.
3. Fitted mapping parameters, "all" fits (VERIFIED, params_*_final.csv): power fe_gamma median 0.70 (E) to 0.89 (leak),
   range 0.42-1.68; < 1 in 7-10 of 10 mice per family; DBM13 is expansive (1.2-1.7) in the integrators. Norm fe_beta median
   0.68-1.26 (max up to 15.7 in ES), fe_tau median 0.15-0.53 s. Nominal + power fe_gamma median 0.77 (0.49-1.37).
4. Ranking within each mapping, minus that mapping's primary (VERIFIED, ranking_*_final.csv):
   linear: leak+urgency -72, leak -15, urgency +18, no_sv +317, E +328, ES +518.
   power: leak+urgency -156 (5 better / 0 worse), leak -75, urgency -53, E +272, ES +438.
   norm: leak+urgency -104, leak -49, urgency -17, E +258, ES +374.
   nominal: leak -140, leak+urgency -120, urgency -60, no_sv +36, E +241, ES +342.
5. Integrator minus extrema (VERIFIED, integrator_vs_extrema_*_final.csv): every integrator beats E and ES under every
   mapping, -241 to -593; 4-7 mice better by >10, 0-2 worse. (The partial-data impression that norm shrank this gap was
   due to 3 missing mice; with all 10 the norm gap is -258 to -478.)
6. Nominal coherence minus ME, same family (VERIFIED, nominal_*_final.csv): primary +117 (0 better / 4 worse;
   +3.6 per 1,000 trials), leak+urgency +69, urgency +39, E +30, leak -7, ES -59, no_sv -164 (2 / 0). Nominal + power
   vs nominal primary -127 (3 / 0); vs ME-linear primary -10; vs ME-power primary +29.
7. Pulse effect of the "all" fits (VERIFIED; pulse_joint_signatures, 30 reps, seed 0; data 5.48 pp at 0.3-1.2 s,
   +1.22 pp at 1.2-5 s with 3 mice < 0). Sources: pulse_joint_signatures_2026-11-08_explore_partial_*,
   _2026-11-09_explore_norm_*, _2026-11-09_explore_norm_lu_* (summary and windows CSVs in dissemination/figures/qc/).
   | families | 0.3-1.2 s mean (pp) | 1.2-5 s mean | mice < 0 late | per-mouse RMSE | r with data across mice |
   |---|---|---|---|---|---|
   | linear integrators (4) | 3.08-3.85 | -1.07 to -2.14 | 8-10 | 5.87-6.25 | 0.39-0.64 |
   | power integrators (4) | 3.70-4.20 | -1.38 to -2.80 | 8-10 | 5.34-5.85 | 0.52-0.78 |
   | norm integrators (4) | 4.26-5.33 | -1.19 to -2.90 | 6-10 | 5.58-6.05 | 0.36-0.59 |
   | nominal integrators (5) | 2.35-3.55 | +0.76 to -1.88 | 0-10 | 6.14-6.52 | 0.24-0.68 |
   | nominal + power | 2.33 | -0.76 | 8 | 6.90 | 0.16 |
   | extrema E/ES (all inputs, 8) | 4.03-6.29 | +0.25 to -1.50 | 2-9 | 5.36-6.43 | 0.07-0.70 |
   | P1: power, control-only fit | 3.72 (linear control-only 3.25) | -1.46 | 8 | 5.61 | 0.68 |
   Per mouse the data range from -4.2 to 15.5 pp; no family's prediction tracks this spread (RMSE >= 5.3 everywhere).
   Extrema families that reach the mean (power E 6.10, norm ES 6.29) are the ones that lose most held-out NLL.

## What didn't work
- Rule B of the mapping plan (pre-set 2026-11-07) was too strict: even linear fails it (Holm). Moot while exploratory;
  kept for the rules discussion.
- Partial comparisons (1,235 fits) misled on the norm integrator-vs-extrema gap; only compare complete mouse sets.
- ckpt-all requeues jobs at ~8 h (VERIFIED pattern: 8 jobs started together all REQUEUED at 08:02 elapsed); norm fits
  need > 8 h, so before checkpointing (c902211, 84a4b0b) some never finished; 373.5 h were lost to restarts in this batch.

## How to reproduce
Fits: scripts/slurm/tasks_2026-11-06.csv via scripts/slurm/autosubmit.py (Hyak). Sync: `bash scripts/sync_ddm_data.sh pull`.
Comparison: `.venv/bin/python -m scripts.ddm.compare_mapping_accumulator --tag _final`.
Pulse signatures: `.venv/bin/python -m scripts.ddm.pulse_joint_signatures --cache <dir> --fe_power --tag _explore_partial
--families <22 families>` (see mapping plan log 2026-11-08 for the list); `--tag _explore_norm --families primary
norm_primary norm_leak norm_urgency norm_extrema_E_leak20-200`; `--tag _explore_norm_lu --families primary norm_leak_urgency`.
Reference families reproduce exactly across runs (primary 3.43, norm_primary 4.49).

## Caveats
- 10 mice; differences are summed over mice and dominated by 2-4 of them; uncorrected p values are descriptive only.
- Many comparisons (4 mappings x 7 accumulators x pulse windows); any single "best" is not a confirmed finding.
- guess_tau at its upper bound in many fits, fe_beta at 0 in some: the parameter boxes may shape the fits.
- Simulation statistics use 30 reps; per-mouse simulation noise not quantified here.
- Rig enters only as a covariate (min_rt per site); results are not and should not be split by site.

## Open questions and next steps
- [ ] Rules discussion with the author now that all results are in (which comparisons, which correction, rule B).
- [ ] The late-window reversal (all integrators negative at 1.2-5 s; data +1.2) is the most consistent misfit; decide
      whether to examine it (e.g. RT-conditioned pulse effect in data vs model).
- [ ] Per-mouse pulse spread (-4.2 to 15.5 pp) is not captured by any mapping or accumulator: check whether it relates
      to per-mouse fitted parameters (guess rate, bound, fe_gamma) or is sampling noise (bootstrap the data effect).
- [ ] Whether the compressive mapping (power/norm) should become the default front end for the paper(s).
