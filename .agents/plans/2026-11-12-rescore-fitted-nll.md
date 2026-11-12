# Plan: rescore every full-data fit at independent noise seeds; AIC/BIC from rescored NLL
Status: done (report reports/2026-11-12-rescored-ic.md)
Created: 2026-11-12 by Claude (Opus 5.5)
Related reports: reports/2026-11-12-likelihood-check.md, reports/2026-11-11-model-ic.md

## Goal
For every family in the fit browser (joint, pulse-only, control-only; 63 x 10 mice), the fitted-data NLL evaluated at
independent seeds (not the fit's own noise draw), split into choice and RT terms; AIC/BIC recomputed from it; the
browser shows the rescored values. Author approved 2026-11-12 ("ok").

## Assumptions
- 2 independent seeds x 30 reps per fit (seed difference = Monte Carlo noise estimate); local CPU, parallel processes.
- make_model + OPTIONS reproduce each family's model (checked before: test NLL reproduced to <= 0.08).

## Steps
- [x] 1. scripts/ddm/rescore_fits.py: per (family, mouse) rescore the full-data fit on its training trials; asserts
      likelihood settings / guess form match; per-row cache (restartable). Check: 15 reps at EVAL_SEED reproduces
      rescore_nll_terms_2026-11-12.csv for those pairs.
- [x] 2. Run all families (parallel).
- [x] 3. compare_ic.py: AIC/BIC from rescored NLL (stored kept for comparison); new CSVs.
- [x] 4. Browser: rescored fitted NLL / AIC / BIC in the NLL tab; publish.
- [x] 5. Report; STATUS.

## Out of scope
Refitting; held-out NLL (unaffected).

## Log
- 2026-11-12: plan written.
- 2026-11-12: step 1 done; 15 reps at EVAL_SEED reproduces rescore_nll_terms_2026-11-12.csv (60 fits, diff 0). Container now has 2 RTX 4090: CUDA backend, sequential shards per GPU (forked workers cannot use CUDA) instead of a process pool.
- 2026-11-12: steps 2-5 done (1,260 rescorings, ~35 min on 2 GPUs); artifact version 9.
