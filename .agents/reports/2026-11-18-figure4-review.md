# Report: begin Figure4 pulse-influence review
Date: 2026-11-18   Agent: Codex   Commit: 0f9ffc5 (base for next-figure review)
Plan: plans/2026-10-26-paper-accumulation-variant.md, R

## Question
Proceed after completed Figure3 panel review and requested checkpoint commits.

## Summary
Current next figure is pulse influence (proposed Figure4; earlier packet Figure3). Re-exported unchanged existing A–D results with new figure/table labels and matching caption. Panel-by-panel review starts at A; no redesign or new fitting performed.

## Findings
- VERIFIED: new figure4_pulse_review_2026-11-18/ under dissemination/paper_accumulation/draft_2026-11-15 contains psychometric pulse shifts A, directional/shared logistic coefficients versus response interval B, dilution-adjusted temporal readout C, and assignment-based directional contrast across mice D.
- VERIFIED: all5 exported source tables match corresponding figures_v5/source_data/fig3_* tables (pandas assert_frame_equal,1e-12 tolerances). Source hashes and definitions in figure_manifest.json; source-table equivalence in verification.json. PNG inspected; builder layout check recorded.
- VERIFIED: caption copied from existing pulse caption with figure/source-prefix relabeling; underlying estimates, uncertainty and corrected statistics unchanged. Historical manuscript/Word numbering not globally changed.
- CONTEXT: author retains Huk-style temporal pulse result centrally, including late decline. Figure3 model-control scores and Figure4 pulse observations have distinct populations/estimands; new pulse prediction fits not authorized by moving to artwork review alone.

## What didn't work
No new model fitting or pulse simulations attempted. One source-verification command used system pandas incompatibly, corrected with .venv; source equality then passed.

## How to reproduce
```bash
.venv/bin/python -m scripts.paper.review_pulse_results --output dissemination/paper_accumulation/draft_2026-11-15/figure4_pulse_review_FRESH
```
Renderer reuses build_paper_2026_11_15.figure3 through a label-changing Builder subclass; source/script hashes included. Caption adjacent.

## Caveats
This is an unchanged starting artwork, not final Figure4. A uses descriptive connected proportions, not the four-parameter logistic shown in Figure1/control Figure3B. B/C use discrete response-conditioned bins; D is a separate assignment-based estimand. Need author-led panel decisions before interpreting display changes as scientific changes.

## Open questions and next steps
- [ ] Begin A review: pulse/control psychometric display, population and curve convention.
- [ ] Then review B–D sequentially.
