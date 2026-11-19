# Report: Figure 4 compensated exponential overlay
Date: 2026-11-18   Agent: Codex   Commit: ed2d38d (uncommitted)
Plan: plans/2026-10-26-paper-accumulation-variant.md

## Question
Overlay standalone exponential on compensated pulse panel (author calls it E; current layout D).

## Summary
VERIFIED v12 preserves A–C pixels and original dilution source. Adds saved exponential and pointwise band using physical mean pulse-to-response latency. No refits or new tests.

## Findings
- VERIFIED source equality and artwork in v12/verification.json; full PNG inspected.
- VERIFIED exponential source curves copied exactly; source_data/fig4_D_exponential_* and exponential_fit_manifest.json retain provenance.
- VERIFIED caption and review pointers explain historical E/current D and updated physical time axis.

## What didn't work
Ordinal bin coordinates cannot be used for a physical-time exponential. Original categorical positions were replaced by the saved physical mean-delay coordinates; outcomes and intervals unchanged.

## How to reproduce
scripts.paper.assemble_figure4_timing with v5 previous, ordinal and interaction sources, fresh output, --persistence-sequence --dilution-only --exponential-overlay dissemination/paper_accumulation/draft_2026-11-15/pulse_exponential_preview_2026-11-18. Final checks /tmp/finish_exponential_overlay.py. Hashes in v12/figure_manifest.json.

## Caveats
Descriptive curve, fixed zero asymptote, uncertainty conditional on observed time coordinates; not an intrinsic forgetting constant. Existing bootstrap limitations retained.

## Open questions and next steps
- [ ] Author review overlay and final panel labels.
