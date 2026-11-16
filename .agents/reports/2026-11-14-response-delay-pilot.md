# Report: response-delay variability pilot
Date: 2026-11-14   Agent: Codex   Commit: b63c9d9 (new code and outputs uncommitted; hashes in integrity audit)
Plan: plans/2026-11-14-response-delay-pilot.md

## Question
Can mean-preserving postdecision delay variation replace persistent additive drift variability and explain both RT distributions and the sustained pulse response?

## Summary
VERIFIED within this exploratory bounded pilot: no material improvement over the fixed-delay no-sv model. Full-data fits and independent broader searches favor near-zero delay spread. The PSUIM7 RT disadvantage and both mice's early pulse underprediction remain. This does not reject all timing accounts or identify the biological source of variability.

## Findings
- VERIFIED: 12 new fits (PSUIM6/7, full data plus original five folds), plus two separate broader full-data search checks. All common parameters refitted; CV warm starts use corresponding training fits only. Sources: `/mnt/data/processed/ddm/fits_response_delay_2026-11-14/`; `dissemination/response_delay_2026-11-14/fit_parameters_and_provenance.csv`.
- VERIFIED: delay minus matched drift-model held-out NLL, averaged over three independent seeds at 60 repetitions: PSUIM6 +6.22 (choice −14.69, RT +20.92); PSUIM7 +255.85 (choice −20.15, RT +276.00). Delay improves on fixed no-sv by only 2.89 / 0.25. PSUIM6's total ranking changes across simulation seeds; not numerically resolved. Sources: `heldout_scores_by_seed.csv`, `heldout_difference_summary.csv` in the output folder.
- VERIFIED: early pulse effect (pp, 0.3–1.2 s), observed versus out-of-fold delay prediction: PSUIM6 15.50 [12.61,18.20] vs 7.15; PSUIM7 13.48 [11.45,15.59] vs 4.84. Data intervals: 500 within-session 50-trial-block resamples, pointwise within mouse, not corrected group tests. Both signed profiles and coherence cells are saved. Sources: `data_pulse_window.csv`, `model_pulse_window.csv`, associated profile/coherence tables.
- VERIFIED: CPU/CUDA contract tests, real-data zero-spread stored-likelihood equality, historical pulse-estimator reproduction, literal-resampling validation and existing checkpoint tests. Final audit checks 90 scores / 6,846,120 outcomes, equal drift/delay parameter counts and trial/condition/source alignment. Maximum NLL decomposition error <3e-12. Source: `integrity_audit.json`, `real_data_zero_spread_checks.json`, `pulse_estimator_checks.json`; code/commands below.
- HYPOTHESIS: positive mean-one evidence-gain variation is the next focused alternative. No gain model was fitted. Do not interpret this pilot as evidence for a motor mechanism or unique accumulation dynamics.

## What didn't work
- Local optimization approached the nested zero-spread boundary. A separate training-only DE exploration also returned near-zero spread; finite searches do not establish the global optimum.
- A pulse validation initially compared pp to a fraction-valued reference. Corrected the reference import and verified agreement; incomplete output retained with `validation_pending` suffix.
- Assessment indexing initially dropped its row identifier. Fixed before final prediction tables/figure; no fits or likelihood scores changed. Failed/successful logs retained.

## How to reproduce
Use the existing `/src/.venv`, processed responded-only nofreeze inputs and original onset-weighted benchmark fits. From `/src`, set `OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1`:
```
CUDA_VISIBLE_DEVICES=0 .venv/bin/python -m scripts.ddm.fit_response_delay --fit --mice PSUIM6
CUDA_VISIBLE_DEVICES=1 .venv/bin/python -m scripts.ddm.fit_response_delay --fit --mice PSUIM7
CUDA_VISIBLE_DEVICES=0 .venv/bin/python -m scripts.ddm.check_response_delay_search --mouse PSUIM6
CUDA_VISIBLE_DEVICES=1 .venv/bin/python -m scripts.ddm.check_response_delay_search --mouse PSUIM7
.venv/bin/python -m scripts.ddm.assess_response_delay --prepare
CUDA_VISIBLE_DEVICES=0 .venv/bin/python -m scripts.ddm.fit_response_delay --score --mice PSUIM6
CUDA_VISIBLE_DEVICES=1 .venv/bin/python -m scripts.ddm.fit_response_delay --score --mice PSUIM7
.venv/bin/python -m scripts.ddm.assess_response_delay --collect --plot
.venv/bin/python -m scripts.ddm.audit_response_delay
NUMBA_NUM_THREADS=1 .venv/bin/python -m tests.test_response_delay
.venv/bin/python -m tests.test_fit_checkpoint
```
Detailed interpretation/implementation: `dissemination/response_delay_2026-11-14/RESULTS.md` and README. Data/source hashes and environment versions in manifests and integrity audit; figure `response_delay_pilot.pdf` visually inspected. All prior inputs/results preserved.

## Caveats
Two selected diagnostic mice, trial holdout within sessions; no population inference, recovery or fitted-parameter intervals. Numerical seed spread is not a biological CI. Bounded local/global pilots are not global optimum certificates. Response-conditioned likelihood and pulse subgroups retain survival/selection limitations. Pure independent postdecision lognormal delay does not test sensory-onset or session-level timing variation.

## Open questions and next steps
- [ ] Test a matched positive-gain-variability model using the same training folds, seeds, RT and signed pulse checks; do not expand this unhelpful delay candidate to the full cohort.
- [ ] If a candidate fits both constraints, perform recovery, parameter-uncertainty and session/history sensitivity checks before mechanism claims or full-cohort publication interpretation.
