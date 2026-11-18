# Report: Figure3 assembled preview
Date: 2026-11-18   Agent: Codex   Commit: 5944a68 (base; composition uncommitted)
Plan: plans/2026-10-26-paper-accumulation-variant.md

## Question
Show the current Figure3 with newly approved D.

## Summary
Combined the accepted A/B/C and exponential D in two review previews, retaining both A alternatives. No changes to plotted data or fits. Preview typography is inherited from the individual approved panels.

## Findings
- VERIFIED: input paths and SHA256 hashes recorded in figure3_assembled_2026-11-18/manifest.json. PNG layout inspected; all panels visible without cropping. Both SVG files preserve nested source vector panels.

## What didn't work
No vector-to-raster conversion package was available. PNG previews compose existing saved PNGs; separate SVG composition retains vectors.

## How to reproduce
`.venv/bin/python -m scripts.paper.assemble_figure3 --output <fresh-directory>`
Existing environment. Output: dissemination/paper_accumulation/draft_2026-11-15/figure3_assembled_2026-11-18/.

## Caveats
Review assembly retains panel-specific type sizes and historical review annotations. It is not a final journal-formatted plate.

## Open questions and next steps
- [ ] Final choice of A1 versus A2 and typography/layout review.

## Approved working-order update — 18 November 2026
Author chose oldD→oldA→oldB→oldC. New previews in figure3_story_order_2026-11-18/ relabel A conditional accuracy/B comparison/C fits/D recovery. Both comparison alternatives retained. Source hashes verified unchanged; SVG IDs unique; raster inspected. Reproduce with --behavior-first option. Header labels only changed; obsolete recovery approval annotation removed. Layout remains provisional, manuscript-wide cross-reference harmonization pending final selection. No fits or commit.

## Commit checkpoint — 18 November 2026
User approved the reordered preview and requests all Figure3 changes committed. Both assemblies passed source-hash, PNG-dimension and SVG-structure/unique-ID checks (figure3_story_order_2026-11-18/verification.json). Captions saved in current order; Methods conditional-accuracy label updated to A. Script compilation checked. Figure3-only shared-document hunks staged; unrelated Figure4 content left uncommitted. No numerical analyses rerun.
