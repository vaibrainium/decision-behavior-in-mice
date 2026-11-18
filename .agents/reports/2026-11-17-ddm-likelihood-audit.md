# Report: DDM fitting likelihood audit
Date: 2026-11-17 (client date)   Agent: Codex   Commit: 294cddc (base)
Plan: [Figure 3 likelihood audit](../plans/2026-10-26-paper-accumulation-variant.md#figure-3-likelihood-audit-2026-11-17-client-date)

## Question
Does the DDM fitting implementation compute the intended likelihood, and do the current Figure 3A alternatives reflect that calculation?

## Summary
The choice and conditional RT terms implement the intended response-conditioned, simulation-based quantile objective. An independent count calculation matched the implementation, and sampled training and test scores reproduced from saved parameters. Figure 3A's transformations match the archives. The main reporting limitation is that the held-out quantile score defines RT bins from each test fold and drops its RT term for sparse condition-by-choice cells.

## Findings

- **VERIFIED — Objective.** Within mouse and condition, the simulated choice probability uses the count of each choice among responses by 5 s, with 0.5 pseudocounts per choice. The conditional RT probability uses the histogram for that choice and the same smoothing per RT bin. Multiplying these probabilities gives the joint probability of choice and RT bin, so adding their negative logs is appropriate. The first and last bins cover both tails. Simulated trials without a response by the deadline are excluded from the conditional denominator, and a condition with zero simulated responses costs 20 units per observed trial. Training additionally rejects parameter vectors with more than 50% simulated nonresponses overall. The held-out scoring function uses the calculator without that training guard. Hand-count checks covered censoring, conditional scoring, empty cells, and sparse cells. Sources: src/ddm/likelihood_calculator_censored.py, scripts/ddm/fit_mouse_ddm.py, src/ddm/ddm.py, and the accompanying audit script. For background on diffusion-model RT quantiles, see [Ratcliff and Tuerlinckx (2002)](https://pmc.ncbi.nlm.nih.gov/articles/PMC2474747/).
- **VERIFIED — Data and bins.** The processed input had consistent response markers and no collisions between condition IDs and coherence × scheduled pulse pairs. Across 14,014 held-out control trials, 1,990 (14.2%) contributed choice only because their condition-by-choice cell had fewer than nine observed test RTs. For the pooled full-control scoring population, the corresponding count was 48 (0.34%). No duplicate interior RT cut points occurred in these full-control or test cells. Each test fold defines its own RT quantiles and eligibility. These are shared across candidate models. Source: audit script's cell counts from the processed NPZ and original fold assignment.
- **VERIFIED — Score reproduction.** Read back all 250 saved CV fit objects and matched their settings, trial counts, and test scores to the archive. At fixed parameters and the archived repetitions and seeds, an independent count-based calculation and the production scorer agreed in both fold-0 checks (DBM12 and PSUIM7, all five candidates), in a DBM12 C independent full-control training rescore, and in a DBM12 C fold-0 original training score at seed 42. The original training objective was also called directly at those fitted parameters. All sampled archive agreements were within 1e-8 NLL units with CUDA. Sources: accompanying script, control_fold_inventory.csv, full_control_fit_inventory.csv, independent_training_scores.csv, and source fit pickles.
- **VERIFIED — Figure 3A.** Test LL is the sign flip of summed test NLL per mouse, averaged equally across mice. Joint bits/trial divides each mouse's test LL by its trial count and by ln(2) before averaging equally across mice. This is an absolute grouped log score in base 2. The right axis uses the BIC formula with independent full-control NLL at saved parameters and the archived free-parameter count. It is a QMLE-based BIC approximation. Verified all 100 BIC input rows and 50 archived full-control fit hashes. Sources: the selected-artwork source CSV, both fit inventories and independent_training_scores.csv.

## What didn't work
The first read-back assumed all historical fit pickles store the nominal-input flag explicitly. The audit now defaults missing flags to false, consistent with the older motion-energy fits. The first rescore repeated forward simulation after obtaining the score. The final script captures the actual scored simulation rows for its independent recomputation.

## How to reproduce
From the repository root at base commit 294cddc and with the same archived score tables and processed inputs:

```bash
PYTHONPATH=/src .venv/bin/python .agents/reports/2026-11-17-ddm-likelihood-audit.py
```

Input is /mnt/data/processed/ddm/ddm_inputs_global.npz, SHA-256 1a6c88ecf5da258e18435ceab600c799b3e413f0a0adc464d70b6115e1d69980. Tables and fit paths are in the script. Reproduced in the project .venv with the CUDA simulator. The script uses the CPU backend on hosts without CUDA and prints archive differences there.

## Caveats
- The objective pools simulated outcomes within condition, so it evaluates the marginal choice and RT distributions across the inputs within that condition. It does not score the association between an individual trial's observed outcome and its own motion-energy trace.
- Training folds supply fitted parameters and a fresh seed supplies simulation draws. The outcome bins and sparse-cell mask depend on the test fold. The resulting quantity is a held-out quantile log score, distinct from a log score for prespecified RT categories or a continuous RT density. Absolute bits/trial also depend on the binning and contain no subtraction of a null score.
- The audit checks score calculation and provenance. It does not establish parameter identifiability, a global optimum, or ranking stability under different bins or seeds. The code represents success as a finite objective below the failure penalty. Original fitting, artwork, and score tables were not modified.

## Open questions and next steps
- [ ] For manuscript wording, describe the test-fold RT quantiles and sparse-cell rule when reporting held-out scores.
- [ ] If a fixed-category prediction metric is needed, compare candidates on common bins defined on training data or fixed in advance and check Monte Carlo sensitivity. The bounded audit printed examples under training-defined cuts, without estimating a cohort ranking under those cuts.
