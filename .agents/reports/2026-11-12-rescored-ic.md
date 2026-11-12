# Report: AIC / BIC from fitted NLL rescored at independent seeds
Date: 2026-11-12   Agent: Claude (Opus 5.5)   Commit: 487407b (+ this report's commit)
Plan: plans/2026-11-12-rescore-fitted-nll.md

## Question
reports/2026-11-12-likelihood-check.md found the stored fitted NLL optimistic (fit's own noise draw). With every
full-data fit rescored at independent seeds, which models win by AIC / BIC, and does that agree with held-out NLL?

## Summary
- All-trial fits (38): rescored AIC and BIC both pick power law + leak + urgency, the held-out winner too.
  Normalization + leak is 2.6 behind (within Monte Carlo noise); next power law + leak (BIC +43). With stored values
  BIC had picked normalization + leak (+29 ahead). VERIFIED.
- Pulse-only fits (22): BIC still picks linear leak; then power-law integrator (+35), power-law leak (+50). No-sv models
  remain 190-500 behind their sv versions by BIC. Held-out best (norm UGM no sv) is 16th by BIC. VERIFIED.
- Control-only (3): BIC power law, then normalization (+39).
- Optimism of stored NLL: per family 53-233 (median per mouse 16; range -11 to 45), so it was model-dependent but
  smaller than most gaps; rankings beyond the top 2-3 changed little (Spearman BIC vs held-out: joint 0.93 both ways;
  pulse-only 0.75 rescored vs 0.68 stored).

## Findings
- rescored_nll_2026-11-12.csv (630 fits x 2 seeds, 30 reps; choice and RT terms), model_ic_summary_2026-11-12_rescored.csv
  (d_aic, d_bic, d_heldout, d_bic_stored, ranks, optimism, seed_sd), model_ic_per_mouse_2026-11-12_rescored.csv.
- Monte Carlo noise of a family's summed NLL (SD across the 2 seeds): median 13, range 1-52; UGM and ES families are
  the noisiest (27-52). Differences below ~20-30 are not resolved.
- Fit browser data v6 (fit_browser_2026-11-12_v6.json = v5 with fitted_nll rescored, stored kept as
  stored_fitted_nll); artifact version 9 (Fitted / AIC / BIC views use rescored; "Fitted, as stored" view).

## What didn't work
- Process pool: forked workers cannot use CUDA (container now has 2 GPUs); ran one sequential shard per GPU.
- A page edit introduced unescaped quotes in a JS string; caught by a syntax check before publishing.

## How to reproduce
`CUDA_VISIBLE_DEVICES=0 python -m scripts.ddm.rescore_fits --cache C --shard 0/2` and the same with 1 / `1/2`, then
`python -m scripts.ddm.rescore_fits --cache C` (collects); `python -m scripts.ddm.compare_ic --rescored
dissemination/figures/qc/rescored_nll_2026-11-12.csv`. ~35 min on 2 x RTX 4090.

## Caveats
- Two seeds only: seed SD is a rough noise estimate.
- Each mouse fitted separately; rescoring does not refit (parameters are the stored optima).

## Open questions and next steps
- [ ] Which criterion for the paper (author).
- [ ] PSUIM7's RTs and sv (reports/2026-11-12-likelihood-check.md).
