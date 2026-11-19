# Report: Figure 4C ordinal pulse timing
Date: 2026-11-19   Agent: Codex   Commit: ed2d38d (assembly changes uncommitted)
Plan: plans/2026-10-26-paper-accumulation-variant.md

## Question
Place author-selected earlier single directional-influence curve in Figure 4C; keep direction interaction as backup.

## Summary
VERIFIED: v6 assembles saved estimates without fitting or trial changes. A/B/D/E source tables are byte-identical. Former C is a supplementary draft; interaction display is backup. Full layout inspected.

## Findings
- VERIFIED: new C reads all_available_10/WLS curves directly from pulse_time_ordinal_2026-11-18/influence_curves.csv. Caption preserves cohort-support and matched-cohort sensitivity caveats; no new scientific inference.
- VERIFIED: source equality and image comparison recorded in figure4_revision_2026-11-19_v6/verification.json. No source statistics changed.
- VERIFIED: PNG/PDF/SVG exported; source data, caption, acceptance metadata and provenance retained. Manuscript review pointers updated.

## What didn't work
No fit was attempted; existing optimizer/helper defaults therefore cannot alter accepted estimates.

## How to reproduce
From /src: `.venv/bin/python -m scripts.paper.assemble_figure4_timing --previous dissemination/paper_accumulation/draft_2026-11-15/figure4_revision_2026-11-18_v5 --timing dissemination/paper_accumulation/draft_2026-11-15/pulse_time_ordinal_2026-11-18 --interaction dissemination/paper_accumulation/draft_2026-11-15/pulse_time_direction_interaction_2026-11-18 --output <fresh-output-directory>`.
Inputs and code hashes are in the new figure_manifest.json. Supplementary and backup outputs are subdirectories of v6. No packages changed.

## Caveats
Ordinal timing and shared-effect assumptions remain. New C presents model estimates and pointwise cluster intervals, not raw trial means. Figure arrangement remains provisional. Earlier manuscript passages/numbering may still reflect historical versions; the v6 caption and review notice are current.

## Open questions and next steps
- [ ] Continue author review of Figure 4 layout and remaining panels.
