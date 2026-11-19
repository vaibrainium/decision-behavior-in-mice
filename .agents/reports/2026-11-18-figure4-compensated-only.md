# Report: Keep only compensated pulse time course
Date: 2026-11-18   Agent: Codex   Commit: ed2d38d (changes uncommitted)
Plan: plans/2026-10-26-paper-accumulation-variant.md

## Question
Author requests removal of redundant separate directional panel; retains dilution-adjusted curve. Congruency ROC omitted.

## Summary
VERIFIED v10 preserves A–C artwork and retains former E as new D, widened across the remaining lower row. Historical results retained. No refits or numerical changes.

## Findings
- VERIFIED A–C pixel equality and compensated source byte equality against v8; v10/verification.json.
- VERIFIED main artwork inspected; source_data/fig4_D_dilution_adjustment.csv unchanged. Caption and current manuscript pointers updated. ROC not selected.

## What didn't work
An incomplete prior omit-dilution option reflected the opposite panel choice; latest author instruction supersedes it. It is not used for v10.

## How to reproduce
Use scripts.paper.assemble_figure4_timing with v5 previous, ordinal timing and interaction directories, fresh output and --persistence-sequence --dilution-only. Exact input paths and hashes in v10/figure_manifest.json. Final documentation/verification: /tmp/finalize_dilution_only.py.

## Caveats
Dilution adjustment is a behavioral readout, not a unique forgetting estimate. Existing selection and uncertainty apply. Historical manuscript mapping outside this section remains provisional.

## Open questions and next steps
- [ ] Continue author review of retained compensated panel.
