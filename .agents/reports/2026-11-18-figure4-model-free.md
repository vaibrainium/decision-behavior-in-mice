# Report: Model-free Figure 4E
Date: 2026-11-18   Agent: Codex   Commit: ed2d38d (uncommitted)
Plan: plans/2026-10-26-paper-accumulation-variant.md

## Question
Add model-free accuracy changes alongside compensated pulse influence.

## Summary
VERIFIED v11 adds E from saved per-mouse and summary CSVs. A–C artwork unchanged; compensated D estimates retained with narrower placement. Individual traces, equal-mouse mean/SEM, gaps and original eligibility retained. No new tests or fits.

## Findings
- VERIFIED means, SEM and animal counts recomputed from saved individual observations match exported summary; v11/verification.json.
- VERIFIED existing Holm family has 12 tests, none significant; caption reports this. Source: source_data/fig4_E_model_free_summary.csv. No inferential test rerun.
- VERIFIED full layout inspected, manuscript notes updated, ROC excluded.

## What didn't work
No failed analysis. This is an additional display of the same experiment, not independent replication.

## How to reproduce
Run scripts.paper.assemble_figure4_timing with v5 previous, ordinal timing and interaction sources, fresh output and --persistence-sequence --dilution-only --model-free. Source hashes in v11/figure_manifest.json; finishing checks in /tmp/finalize_model_free.py.

## Caveats
Model-free means no decision-model fit; control matching, filtering and available-mouse aggregation still apply. Response-conditioned comparisons, restricted coherence range and changing bin support remain explicit.

## Open questions and next steps
- [ ] Author review E and panel ordering.
