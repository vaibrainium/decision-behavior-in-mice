# Plan: replace persistent drift variability with variable response delay
Status: done
Created: 2026-11-14 by Codex
Related reports: ../../dissemination/pulse_rt_tradeoff_2026-11-13/RESULTS_AND_NEXT_MODEL.md
Completed report: ../reports/2026-11-14-response-delay-pilot.md

## Goal
Implement and validate a mean-preserving lognormal postdecision response delay, then run an exploratory PSUIM6/PSUIM7 pilot with refitted common parameters, matched held-out scoring, and pulse prediction checks.

## Context
The matched onset-weighted sv/no-sv comparison loses 310.93 held-out NLL without sv, 90% from PSUIM7. Its central correct-response RTs motivate checking timing assumptions. The user authorized implementation of the proposed plan. Historical manuscript gates do not govern this newly authorized exploratory analysis; retain their records and do not alter prior outputs.

## Assumptions
- Use the original responded-only input, five condition-stratified folds, floor at 0.3 s and censoring at 5 s for a matched comparison; record simulated nonresponse fractions.
- Delay is postdecision, independent of evidence and direction: D = ndt * exp(ndt_sigma * Z - ndt_sigma**2 / 2). ndt is the mean in seconds; ndt_sigma is dimensionless, bounded [0, 1.5]. sigma=0 must recover the fixed-delay model exactly.
- Replace sv with ndt_sigma, keeping pulse weights and other parameter bounds unchanged. The same standard-normal draw can serve the alternative variability parameters because they are mutually exclusive.
- No new experiments, external data transfer, package installation, cluster submission, or changes to historical fits.

## Steps
- [x] 1. Implement an isolated simulator/model and pilot fitting/assessment entry point; capture code/input hashes, seeds, environment and split-specific warm starts.
- [x] 2. Verify zero-spread equivalence, positivity and mean of delay, unchanged decision choices before response selection, guess handling, censoring/flooring, deterministic draws and CPU/GPU consistency. Benchmark the real objective before choosing a bounded pilot budget.
- [x] 3. Refit both pilot mice (full data and original five CV folds), preserving checkpoints and separating exploratory optimization limits from convergence. Score matched drift, fixed and delay models at common independent seeds and higher simulation precision.
- [x] 4. Compare per-mouse absolute RT fit, choice/RT likelihood terms and signed pulse profiles with existing models and observed data. Check session timing and report remaining uncertainty.
- [x] 5. Verify result integrity, write a reproducible report and update STATUS. If delay is inadequate, specify the gain-variability follow-up rather than infer a mechanism from the pilot.

## Out of scope
Full-cohort mechanism claims, exhaustive recovery, changes to likelihood weights, adding a second likelihood for the same pulse outcomes, or removing difficult mice. Recovery and parameter uncertainty are necessary before publication-level mechanism interpretation; this pilot determines whether further work is justified.

## Log
- 2026-11-14: User approved implementation. Read repository status, relevant prior diagnostic/reports, simulator, optimizer and statistical/GPU skills. Existing historical plans concern different frozen analyses; this is a new exploratory pilot. Shared GPUs are busy, so benchmark before selecting local fit budget.
- 2026-11-14: `tests.test_response_delay` passed on CPU/CUDA including exact zero-spread regression. PSUIM7 full-data objective benchmark: ~0.06 s/evaluation at 3 reps, ~0.30 s at 15 reps after warmup. Budget fixed before fitting: two selected starts per stage, max 350 evaluations/start at 3 reps followed by 600/start at 15 reps, all common parameters refitted; original seed 42. This is an explicitly bounded multistart local pilot rather than the historical long global DE search. Started both mice locally on separate shared GPUs, full data then cv0–cv4. Fits/checkpoints: `/mnt/data/processed/ddm/fits_response_delay_2026-11-14/`; logs/manifests: `dissemination/response_delay_2026-11-14/`.
- 2026-11-14: Full-data local solutions favor near-zero spread. Added an independent training-only broader-search check (48 candidates x 20 DE generations at 3 reps, then two 450-evaluation NM refinements at 15 reps), storing separate `_search_check` results; no held-out scores inspected. This checks whether coupled timing/accumulation changes were missed by local boundary convergence.
- 2026-11-14: Pulse bootstrap preparation initially failed its independent estimator check because a reference function returns fractions whereas its similarly named counterpart returns percentage points. Fixed the validation import; independent profile/window estimators now match to <4e-15 pp. Preserved the incomplete output as `data_pulse_profile_validation_pending.csv`; no historic output changed. Existing fitting checkpoint regression tests also passed.
- 2026-11-14: Finished all 12 fits, both separate training-only search checks and 90 higher-precision held-out scores. Near-zero spread persists; PSUIM7 delay minus drift NLL +255.85, PSUIM6 +6.22 with unresolved seed variation. Both early pulse effects remain underpredicted. No full-cohort delay expansion or gain fits. Assessment indexing repair affected no fitted parameters/scores. All 6,846,120 simulated outcomes passed integrity checks; final PDF/PNG visually inspected. See completed report and `dissemination/response_delay_2026-11-14/RESULTS.md`.
