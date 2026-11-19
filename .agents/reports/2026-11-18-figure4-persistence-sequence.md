# Report: Figure 4 adopts the PDF persistence sequence
Date: 2026-11-18 (client date)   Agent: Codex   Commit: ed2d38d (changes uncommitted)
Plan: plans/2026-10-26-paper-accumulation-variant.md

## Question
Adopt the supplied PDF's persistence analysis alongside approved onset-stage C, under current scientific constraints.

## Summary
VERIFIED: v8 preserves A–C pixel-for-pixel, restores a simplified directional persistence curve as D, and moves the unchanged dilution-adjusted estimates to E. The assignment analysis is exported as supplementary PNG/PDF/SVG with its original caption/source. Full decomposition, PDF supporting candidates and interaction backup are retained. No refits, new tests or exclusions.

## Findings
- VERIFIED: Figure4 D copies the saved directional/shared table and displays D only, with original mouse-bootstrap intervals and Holm indicators. Source: v8/source_data/fig4_D_persistence.csv, byte-identical to v6 supplementary former-C table.
- VERIFIED: dilution and assignment tables are byte-identical to v6, with new roles. A–C preserved pixel-for-pixel. Sources: v8/verification.json and source_data/.
- VERIFIED: figure-specific caption, working Results/Methods and current review pointers describe the different onset-stage and response-latency analyses and differing cohort support. No equivalence or intrinsic forgetting-time conclusion added.
- VERIFIED: all main/supplementary figure formats rendered locally; main and assignment layouts inspected. First assembly v7 exposed an overlong rightmost x label; v8 shortens D/E x labels while caption states discrete bin spacing. v7 retained as intermediate.

## What didn't work
Long historical x label extended beyond the right canvas when dilution moved to the last column. Corrected in fresh v8 output. No failed fitting or statistical work.

## How to reproduce
`.venv/bin/python -m scripts.paper.assemble_figure4_timing --previous dissemination/paper_accumulation/draft_2026-11-15/figure4_revision_2026-11-18_v5 --timing dissemination/paper_accumulation/draft_2026-11-15/pulse_time_ordinal_2026-11-18 --interaction dissemination/paper_accumulation/draft_2026-11-15/pulse_time_direction_interaction_2026-11-18 --output <fresh-output-directory> --persistence-sequence`

Final artwork: dissemination/paper_accumulation/draft_2026-11-15/figure4_revision_2026-11-18_v8/. Saved coefficients and intervals only; existing .venv. Additional copied support and documentation finalized by /tmp/finish_persistence_sequence.py; figure/source provenance in figure_manifest.json and supplementary_drafts/pdf_support/manifest.json.

## Caveats
Panel C has late data from a subset and common-effect assumptions; D/E retain early/middle response selection. Estimates share data and are not independent replications. Supplementary numbering and historical global manuscript numbering outside this section remain provisional. No journal submission/export compliance claim.

## Open questions and next steps
- [ ] Author review the new persistence panel and overall Figure 4 flow.
- [ ] Refine supplementary layout/numbering with the remaining manuscript figures.
