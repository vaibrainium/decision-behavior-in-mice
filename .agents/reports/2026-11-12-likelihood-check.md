# Report: is the likelihood calculation correct? (choice vs RT terms; optimism of fitted NLL)
Date: 2026-11-12   Agent: Claude (Opus 5.5)   Commit: d36f3da (+ this report's commit)
Plan: none (author question 2026-11-12, after sv vs no-sv overlays: no sv looks better on pulse-trial choices)

## Question
Is the likelihood wrong, given that no-sv fits look better on pulse-trial choices but sv wins on likelihood?

## Summary
- No bug found. src/ddm/likelihood_calculator_censored.py is a standard censored quantile likelihood (binomial over
  choices + per-choice multinomial over 9 data-quantile RT bins, per cell). Cells = signed coherence x scheduled pulse
  (sign x stage 1-3), unique per condition code (checked on the inputs). Rescoring reproduces the stored values up
  to the noise seed (below). VERIFIED.
- sv's advantage on pulse trials is all in the RT term; the choice term favours no sv. The RT term is ~77% of the
  objective (23.5k of 30.6k per family). VERIFIED for 3 pairs.
- One mouse carries it: PSUIM7 gives 109-133 of the 125-232 no-sv deficit. Without PSUIM7: linear integrator no-sv
  -7 (better), linear leak+urgency +19, power leak +99. VERIFIED.
- The stored fitted NLL (train_nll; used for "fitted", AIC, BIC) is optimistic: the fit's own noise draw. Rescored at
  an independent seed it is 4-47 higher per mouse, 194-250 per family, and the optimism differs by family by up to 56.
  So AIC/BIC from stored values carry a model-dependent bias of the size of the top-model gaps. Held-out NLL
  (scored at EVAL_SEED on unseen trials) is not affected. VERIFIED (6 families); other families SUSPECTED same.

## Findings (rescore_nll_terms_2026-11-12.csv; scripts/ddm/rescore_nll_terms.py; split "pulse" fits, pulse trials)
| no sv minus sv (sum, 10 mice) | stored | rescored | choice term | RT term | PSUIM7 (rescored) |
|---|---|---|---|---|---|
| linear leak + urgency | +164 | +141 | -34 | +174 | +122 |
| power leak | +197 | +232 | -1 | +233 | +133 |
| linear integrator | +119 | +125 | -23 | +148 | +133 |
Optimism (rescored - stored) per mouse: median 16-24, range 4-47; per family 194 (linear integrator) to 250 (linear L+U).

## What didn't work
- Nothing failed.

## How to reproduce
`python -m scripts.ddm.rescore_nll_terms` (needs /mnt/data; ~10 min CPU).

## Caveats
- One independent seed; rescored values have Monte Carlo noise of their own (15 reps).
- Choice term here (cells, 15 reps) differs from choice_binomial_nll_2026-11-12.csv (30 reps, browser cells): both
  favour no sv, by 1-34 here vs 26-60 there.

## Open questions and next steps
- [ ] Recompute fitted NLL / AIC / BIC for all families at an independent seed (more reps) before reporting AIC/BIC.
- [ ] What in PSUIM7's RTs needs sv (look at its RT distributions with the sv / no-sv overlay).
- [ ] Whether to weight choices vs RTs differently is a modelling choice (rt_nllh_weight != 1 is no longer a likelihood).
