# Report: Figure 3 test bits and QMLE ΔBIC
Date: 2026-11-17   Agent: Codex   Commit: 294cddc (base; this work uncommitted)
Plan: plans/2026-10-26-paper-accumulation-variant.md, step R

## Question
Add test bits/trial and ΔBIC in the author's connected-point style while preserving approved raw-NLL A.

## Summary
Verified three distinct metrics: joint held-out choice/RT quantile log score converted to bits/trial; Ashwood-style choice-only gain over a training-only bias null; and independently rescored, full-control QMLE-based ΔBIC. Main preview combines joint test bits (B) and ΔBIC (C). C leads both; both independent training-score seeds give the same group ranking. These are descriptive means without error bars or new hypothesis tests.

## Findings
VERIFIED values below come from `dissemination/paper_accumulation/draft_2026-11-15/figure3_information_metrics_2026-11-17/group_metrics.csv`:

| Model | Joint test bits/trial | Choice gain bits/trial | Mean ΔBIC vs C |
|---|---:|---:|---:|
| C | -2.899003 | 0.157420 | 0.000000 |
| E | -2.917407 | 0.153746 | 71.254805 |
| ES | -2.926047 | 0.155665 | 75.985762 |
| DDMx | -2.939689 | 0.152167 | 132.173157 |
| ESx | -2.942624 | 0.157245 | 143.039519 |

- VERIFIED: joint test score = −saved_test_NLL/(n_test ln2), summed across folds within mouse then averaged equally across mice. This is a quantile log score, not continuous RT density or baseline-normalized information gain.
- VERIFIED: choice gain = (LL_choice,test − LL_null,test)/(n_test ln2). Each fold's null uses only its training right-choice fraction. Original stratified folds and archived test counts matched. Sources: test_bits_per_mouse.csv, training_only_choice_nulls.csv, metric_manifest.json.
- VERIFIED: BIC = 2 independently evaluated training NLL + k ln(n_training). Full-control parameters held fixed; 30 repetitions per input, seeds 12345/23456. Actual saved k: C9, E10, ES8, DDMx4, ESx4. All 50 saved full-control fits have success=True and correct control counts. Sources: full_control_fit_inventory.csv, independent_training_scores.csv, training_score_cache/.
- VERIFIED: 10 mice, 14,014 control responses, 250 CV fold records; 100 new fixed-parameter fit/seed evaluations. All BIC arithmetic, matched counts, within-mouse/seed reference subtraction, archived held-out score differences and seed rank stability passed independent checks (verification.json). Both seed group rankings: C, E, ES, DDMx, ESx. Exact seed results: delta_bic_group_by_seed.csv.
- VERIFIED: main and separate companion renders visually inspected; source scripts compile. Approved A unchanged. New plots are connected categorical means with no uncertainty bars/stars.
- REFERENCE: Ashwood et al., Eq22, DOI10.1038/s41593-021-01007-z (2021 preprint/2022 publication); Stine et al., Eq17, DOI10.7554/eLife.55365. Primary sources checked. Exact Ashwood convention is choice-only; joint score must be labeled distinctly.

## What didn't work
Stored fitting scores are optimistic with respect to their original simulation draws; prior independent IC exports cover a different candidate set. Neither was substituted for the requested five-candidate training comparison. Earlier fixed-RT-bin held-out bits outputs are noise-limited and were not reused. PDF font subsetting produced verbose INFO output without affecting artifacts.

## How to reproduce
From /src, use existing .venv and existing processed inputs; no installations needed. The scoring command performs no optimization/refits and must target a fresh output directory:

```bash
.venv/bin/python -m scripts.paper.figure3_information_metrics --output /src/dissemination/paper_accumulation/draft_2026-11-15/figure3_information_metrics_FRESH --seeds 12345 23456 --n-reps 30
.venv/bin/python -m scripts.paper.compose_information_metric_panels --input /src/dissemination/paper_accumulation/draft_2026-11-15/figure3_information_metrics_2026-11-17 --output /src/dissemination/paper_accumulation/draft_2026-11-15/figure3_information_metrics_panels_FRESH
```

Actual completed outputs: figure3_information_metrics_2026-11-17/ and figure3_information_metrics_panels_2026-11-17/ under the draft directory. Data: /mnt/data/processed/ddm/ddm_inputs_global.npz; archived CV totals: dissemination/paper_control/tables/heldout_nll_per_mouse_2026-10-29.csv; fold inventory: dissemination/reviewer_2026-11-13/control_fold_inventory.csv. Exact source/fit/input hashes and formulas: metric_manifest.json and per-fit caches. Source hashes at completion:

- `scripts/paper/figure3_information_metrics.py`: SHA256 `054cd6015c608d67795ebeab406f2e71a83292a8d4cc37ede20fd3263516abc8`.
- `scripts/paper/compose_information_metric_panels.py`: SHA256 `f7054225fdc564cd1a0888069384aa0fbe66785b6bad6c1af6704fa20ade6715`.

## Caveats
ΔBIC is a QMLE-based approximation at saved parameters, not exact Bayesian evidence. Independent fixed-parameter scoring reduces original simulation-draw optimism but does not measure all parameter or Monte Carlo uncertainty. Group rank stability across two seeds is not a group significance test. C all-control fits come from fits_resp_final; C CV fits come from fits_resp_fast_only, as recorded. Equal-mouse per-trial means differ from panel A's mean raw total NLL. Choice gain makes C/ESx close; no equivalence claim. No raw data changed, packages installed, cluster jobs submitted, commits or pushes made.

## Open questions and next steps
- [ ] Author review B/C previews and choose joint versus choice-only bits for final artwork.
- [ ] Continue Figure 3 panel review; assemble only approved panels and align global manuscript numbering afterward.
