# Held-out RT diagnostic

All150 archived held-out C/E/ES scores reproduced within1e-8 NLL; exact count-based choice/RT decomposition and aggregation checks passed. No model fitting or pulse analysis.

C gains mainly in middle RT bins (3–6), while alternatives score better in slowest bins8–9. Summed middle-bin advantages:17.6153 against E,29.6813 against ES; slowest-bin contributions:−13.8644 and−14.6299, respectively, in NLL/1000 controls. C retains a net held-out advantage.

| Comparison | Choice advantage | RT advantage | Total |
|---|---:|---:|---:|
| C versus E | 2.5463 | 10.2103 | 12.7566 |
| C versus ES | 1.2167 | 17.5283 | 18.7450 |

Mean absolute conditional-quantile error (ms), weighted by observed cell count within mouse, then equal-mouse mean:

| RT percentile | C | E | ES |
|---|---:|---:|---:|
| 10 | 161.6 | 147.7 | 153.7 |
| 30 | 150.9 | 209.2 | 215.6 |
| 50 | 199.6 | 263.6 | 306.2 |
| 70 | 313.3 | 401.2 | 438.3 |
| 90 | 588.6 | 629.0 | 636.2 |

RT advantage is positive in9/10 mice against E and10/10 against ES, without a new significance claim. Largest coherence contribution is −100%:4.1037 versus E and9.3006 versus ES. These are contributions on the all-control denominator, not separate per-condition fit-quality scores. Full detail in CSVs; scoring definitions and limitations in caption.md.

The older separately rescored E component table differs by0.00015548 NLL/1000 in group RT advantage (PSUIM7); this exact decomposition instead matches the original archived total. No earlier results overwritten; cause of the older component discrepancy not established here.

Reproduce: `.venv/bin/python -m scripts.paper.control_rt_score_diagnostic --output <fresh-output-directory>`. Rendering/refinement can reuse copied fold_cache/ using --resume, which checks fit/input hashes. Source code, input and fit hashes in manifest.json/dependency_hashes.json; verification.json records independent checks. Both signed and absolute quantile errors exported. Earlier first diagnostic preserved; v2 uses absolute error to avoid signed cancellation.
