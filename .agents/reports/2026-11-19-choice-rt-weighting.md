# Report: Is choice under-weighted relative to RT in the DDM likelihood?
Date: 2026-11-19   Agent: Claude (Opus 5.5)   Commit: 3b55eca (+ untracked pulse_score_audit_2026-11-19 outputs)
Plan: none (author question: fits match RTs but miss choice proportions; suspected weight imbalance)

## Question
Does CensoredQMLE (nbins=9, rt_nllh_weight=1) give the choice term too little weight compared with the RT quantile term? Is the choice misfit real?

## Summary
There is no weighting bug. Per cell, the objective is a multinomial over choices, using trial counts so it scales with N, plus p(RT bin | choice). Together these give the joint (choice × bin) multinomial, so choice is counted once. This confirms reports 2026-11-12-likelihood-check and 2026-11-17-ddm-likelihood-audit. Out of fold, on pulse-only trials, the choice misfit is real but small. Its excess deviance over binomial noise is 0.013 to 0.021 nats per trial. It is systematic in psychometric slope and concentrated in PSUIM7. The likely cause is model misspecification, not weighting.

## Findings
- VERIFIED: `src/ddm/likelihood_calculator_censored.py` computes the outcome term as −Σ n_k log p_k from the counts, and the RT term from each choice's own simulated RTs (conditional, not defective). No separate binomial is added. Choice is not double-counted, and its weight scales with N.
- VERIFIED: Choice G² on held-out pulse trials, 10 mice × 5 folds, 1,907 cells, 11,479 trials, at stored out-of-fold parameters. The expected G² under the model is computed exactly per cell from Binomial(n, p_model).

  | family | G² (3 seeds) | E[G² \| model] | excess | z |
  |---|---|---|---|---|
  | norm UGM, no sv | 2557–2588 | ~2265 | 287–322 | 4.7–5.3 |
  | linear leak | 2666–2689 | ~2240 | 431–444 | 7.1–7.3 |
  | linear leak + urgency | 2701–2737 | ~2248 | 455–489 | 7.5–8.1 |

  Monte Carlo seed spread is about 30 G² units, much smaller than the excess. Source: `pulse_score_audit_2026-11-19/cells.csv.gz`, `scripts/paper/choice_g2_vs_binomial.py`.
- VERIFIED: The misfit is systematic. For the linear models, the data are steeper than the model at 9 to 36% coherence by 1.4 to 3.8 pp toward the coherence direction. For normalized UGM, the model is too steep at 9 to 18% (−2.2 to −3.0 pp) and too shallow at 100% (+4.9 pp).
- VERIFIED: PSUIM7 contributes the largest excess in every family (74 to 140 of 287 to 489). DBM15 is second (68 to 77). DBM12 shows no excess.
- VERIFIED: Held-out cells are small. The median is 4 trials per cell (IQR 2 to 7), and the median training cell-side has 7 trials. With nbins=9, only 3,886 of 11,479 held-out pulse trials (34%) get an RT term. In training, 82.6% of trials are in cell-sides with at least 9 trials. Held-out pulse scores are therefore mostly choice scores.
- SUSPECTED: Lowering rt_nllh_weight would buy a few pp of psychometric fit at the cost of RT shape. It would not fix the slope pattern, which looks structural (the models disagree in opposite directions). Not tested.

## What didn't work
- Nothing was attempted beyond rescoring saved cells. No refits.

## How to reproduce
`.venv/bin/python scripts/paper/choice_g2_vs_binomial.py dissemination/paper_accumulation/draft_2026-11-15/pulse_score_audit_2026-11-19/cells.csv.gz`
(seconds, CPU). Collapses rows to cells, computes G² = 2(choice_nll − saturated) and its exact mean and variance under Binomial(n, p_side).

## Caveats
- Pulse-only held-out trials, 3 finalist families. Control trials and full-fit (training) choice G² were not checked.
- The saturated model is per cell. With n ≈ 4, the exact expectation (not χ²(df)) is required, and that is what was used.

## Open questions and next steps
- [ ] The same G² vs E[G²] check on control trials and training fits. Is the slope misfit pulse-specific?
- [ ] If RT is reweighted for diagnosis, keep held-out scoring at weight 1 and use CV, not AIC/BIC.
- [ ] Consider adaptive bins (for example 5 bins if n ≥ 25, 2 if 8 to 24, count-only below). This is data-only, so models stay comparable. It would let more held-out cells contribute RT.
