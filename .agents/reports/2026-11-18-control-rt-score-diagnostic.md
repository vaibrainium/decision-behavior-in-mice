# Report: matched held-out RT quantiles and exact score contributions
Date: 2026-11-18   Agent: Codex   Commit: 294cddc (base; diagnostic uncommitted)
Plan: plans/2026-10-26-paper-accumulation-variant.md, R

## Question
Why can E/ES match displayed mean RT better while C wins held-out likelihood?

## Summary
All150 original C/E/ES CV scores reproduced from saved fit parameters, seeds and simulation repetitions. Exact score decomposition locates C's net RT advantage mainly in middle bins; E/ES win slowest bins. C has lower observed-cell-weighted absolute conditional-quantile error at30/50/70/90th percentiles, slightly higher at10th. Full-control mean RT fit need not rank the same as held-out distribution score.

## Findings
| Comparison | Choice advantage | RT advantage | Total |
|---|---:|---:|---:|
| C versus E | 2.5463 | 10.2103 | 12.7566 |
| C versus ES | 1.2167 | 17.5283 | 18.7450 |

| RT percentile | C | E | ES |
|---|---:|---:|---:|
| 10 | 161.6 | 147.7 | 153.7 |
| 30 | 150.9 | 209.2 | 215.6 |
| 50 | 199.6 | 263.6 | 306.2 |
| 70 | 313.3 | 401.2 | 438.3 |
| 90 | 588.6 | 629.0 | 636.2 |

- VERIFIED tables above: control_rt_score_diagnostic_2026-11-18_v2/score_group_components.csv and quantile_absolute_error_group.csv, under dissemination/paper_accumulation/draft_2026-11-15. Quantile errors in ms; score advantages in NLL/1000 controls. These are descriptive group summaries, not new tests.
- VERIFIED: bins3–6 sum17.61532845 (E),29.68126992 (ES); bins8–9 sum−13.86443000 (E),−14.62989325 (ES). Source score_by_rt_bin.csv. Contributions add to exact RT advantage; negative means alternative better. This is not an assertion that C fits all tails better.
- VERIFIED: largest coherence contribution is −100%:4.1037 (E),9.3006 (ES), from score_by_coherence.csv. RT advantage positive in9/10 mice versus E and10/10 versus ES; DBM14 favors E. Source score_by_mouse_component.csv. No group significance added.
- VERIFIED: all150 scores and bin sums match original archived test NLL within1e-8. Original C CV source fits_resp_fast_only; E/ES original CV paths from reviewer_2026-11-13/control_fold_inventory.csv. Captured actual simulation rows used by heldout_nll; no separate draws used to explain scores. Per-fold cache stores counts/probabilities, cutpoints, quantiles and fit/input hashes, not new fitted parameters. Exact settings in fold_score_verification.csv.
- VERIFIED: RT summaries include12024 controls in original cells with >=9 observed RTs;1990 choice-only controls do not contribute RT terms. Quantile diagnostics use identical observed cells and weights for all candidates, retain original conditioning and test-defined cuts. Per-mouse normalization uses all14014 control trials across mice; group equally weights mice. All absolute errors checked directly, avoiding signed cancellation.

## What didn't work
An initial check against the old separately rescored component table failed only for E RT: exact mean differs by+0.00015548 NLL/1000, confined to PSUIM7 (+0.00155484). Exact decomposed totals match all original saved scores and archived total differences; use those as reference. Older table discrepancy cause not established. Export historical_component_comparison.csv rather than silently relaxing a check. First diagnostic visualized signed quantile bias; added absolute-error view because signed errors can cancel, preserving first version. Final v2 reuses original verified fold caches; no repeat simulations needed.

## How to reproduce
From /src, existing .venv/CUDA:
```bash
.venv/bin/python -m scripts.paper.control_rt_score_diagnostic --output dissemination/paper_accumulation/draft_2026-11-15/control_rt_score_diagnostic_FRESH
```
Source script scripts/paper/control_rt_score_diagnostic.py. Original NPZ input,150 fit hashes, inventory/script hashes in manifest.json, dependency_hashes.json. All checks in verification.json. Reuse a copied fold_cache using --resume for rendering/aggregation; fit/input hashes checked. Source compiles, final PNG visually inspected. Source arithmetic independently checked for all bins and group sums; exact quantile observations matched across models.

## Caveats
Original QMLE uses test-defined RT quantile cuts and choice-only sparse cells; not a continuous RT density. Finite original simulation seed/repetitions, no parameter uncertainty or new seed robustness here. Quantiles estimate distribution shape in finite cells; high-percentile errors remain substantial for all candidates. Absolute quantile error and bin log score differ, so C can have smaller90th-percentile error yet worse slowest-bin probability contribution. This diagnostic explains the archived ranking; it does not prove global optimality or isolate causally why full-control mean curves differ. Existing A/B artwork unchanged; pulse deferred.

## Open questions and next steps
- [ ] Author review diagnostic and choose whether an RT-distribution panel belongs in main figure or supplement.
- [ ] Continue Figure3 assembly, keeping visible mean-fit discrepancies and scoring limitations.
