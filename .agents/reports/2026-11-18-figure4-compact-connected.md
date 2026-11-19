# Report: Compact compensated panel with connected observations
Date: 2026-11-18   Agent: Codex   Commit: ed2d38d (uncommitted)
Plan: plans/2026-10-26-paper-accumulation-variant.md

## Question
Try narrower compensated panel and connect the data points.

## Summary
VERIFIED v13 reduces D width from .46 to .32 of canvas; connects observations with black straight segments. Exponential overlay, intervals and A–C retained. All v12 source files byte-identical; artwork inspected. Caption explains connecting segments as a visual guide.

## Findings
- VERIFIED visual-only change; source equality in v13/verification.json.

## What didn't work
None.

## How to reproduce
Use scripts.paper.assemble_figure4_timing with previous v5, ordinal/interaction sources and --persistence-sequence --dilution-only --exponential-overlay <pulse_exponential_preview_2026-11-18> --compact-connected --output <fresh-directory>. No fits or tests.

## Caveats
Layout preview; line segments are not an additional fitted model.

## Open questions and next steps
- [ ] Author assess compact connected layout.
