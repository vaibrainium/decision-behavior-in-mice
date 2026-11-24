# Report: Current main-figure compilation
Date: 2026-11-24   Agent: Codex   Commit: WORKTREE on e026778
Plan: plans/2026-10-26-paper-accumulation-variant.md

## Question
Compile the current manuscript figures for review without silently resolving the open Figure 3 metric choice.

## Summary
Two six-page review PDFs were compiled from the existing 300-dpi PNG exports. They differ only on Figure 3: LL+BIC versus bits/trial+BIC. Figures 1, 2 and 4 use the current checkpointed/approved artwork; Figures 5 and 6 remain explicitly provisional. No analysis, fitting, simulation or source figure changed.

## Findings
- VERIFIED: both PDFs contain 6 page objects, valid `%PDF-1.4` headers and terminal EOF markers, and their SHA-256 hashes match the manifest. Source: `figure_compilation_2026-11-24/verification.json`; command below.
- VERIFIED: all 7 source PNGs report approximately 300 dpi; page order is Figure 1 through Figure 6; the only variant key is page 3. Source: `manifest.json` and `verification.json`.
- VERIFIED: all source pages, including both Figure 3 alternatives, were visually inspected at native export resolution with no clipping or missing panels. Figures 5 and 6 are still labeled opening/tentative in their artwork.

## What didn't work
- No system PDF merger or PDF parsing library was installed. The existing Pillow environment therefore produced review-only raster PDFs from the high-resolution PNG exports. Vector source PDFs/SVGs remain authoritative for submission.

## How to reproduce
```bash
.venv/bin/python -m scripts.paper.compile_current_figures \
  --draft-root dissemination/paper_accumulation/draft_2026-11-15 \
  --output dissemination/paper_accumulation/draft_2026-11-15/<fresh-output-directory>
```
Inputs and output hashes: `dissemination/paper_accumulation/draft_2026-11-15/figure_compilation_2026-11-24/manifest.json`. Validation logic and results: adjacent `verification.json`. Base repository commit was `e026778`; compiler and packet are included in the focused commit that contains this report.

## Caveats
These are raster review packets, not Neuron submission masters. Figure 3 layout and metric remain open; Figure 5 and Figure 6 await panel-by-panel review. Compilation does not establish current Cell Press submission compliance.

## Open questions and next steps
- [ ] Author selects the Figure 3 comparison version when ready.
- [ ] Continue Figure 5 and Figure 6 review before creating a vector submission packet.
