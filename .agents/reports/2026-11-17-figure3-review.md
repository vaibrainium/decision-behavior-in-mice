# Report: begin control-results Figure 3 review
Date: 2026-11-17   Agent: Codex   Commit: a20629e
Plan: plans/2026-10-26-paper-accumulation-variant.md

## Question
Move from accepted model-introduction Figure 2 to the control-results figure.

## Summary
Figure 2/split checkpointed at author request. Current Figure 3 remains the exported comparison/recovery starting layout. Recommend opening with observed and predicted choice/RT behavior, followed by held-out comparisons and recovery. No new predictions, fits or inference performed this turn.

## Findings
- VERIFIED: current Figure 3 panels are score differences, choice/RT score decomposition, dataset recovery and cohort recombinations. Sources: draft_2026-11-15/figure3_control_results_2026-11-17/figure3.png and adjacent caption/source tables; unchanged from prior audit.
- VERIFIED: dissemination/paper_control/tables/control_chronometry_2026-10-29.csv contains sources data/common/E and 10 mouse IDs, with absolute coherence/outcome summaries. It does not contain all five model predictions or signed-choice summaries needed for the proposed new overlays. Inspection command: pandas read_csv; inspect source.unique(), mouse.nunique(), columns.
- VERIFIED: scripts/ddm/control_descriptives.py documents common-model predictions from fits_resp_final and E from fits_resp_fast_only_leak20-200_cap; these are distinct fit sources. Do not present that export as a uniform held-out five-model comparison.
- JUDGMENT: new opening panels should show what models capture/miss in observed psychometric and choice-conditioned mean RT functions. Trial population, fitting split and prediction source must match the stated comparison. Source audit is next, not an assumed validation.

## What didn't work
No new build attempted. Legacy chronometry alone is insufficient for the proposed complete overlay; no substitution or fabricated ES/reference curves.

## How to reproduce
Read the current Figure 3 artwork/caption and the old chronometry CSV plus scripts/ddm/control_descriptives.py and control_heldout.py. Comparison/recovery extraction reproduces with `.venv/bin/python -m scripts.paper.review_control_results --output <fresh-directory>`.

## Caveats
Current Figure 3 is a starting layout. Model schematic is illustrative; observed/predicted results must use separately audited prediction sources. Old manuscript numbering remains pending figure selection. No push performed.

## Open questions and next steps
- [ ] Agree on opening choice/RT panels and overall Figure 3 arrangement.
- [ ] Audit saved prediction artifacts for matched fit splits and all five candidates before plotting.
- [ ] Build and inspect the agreed results revision, preserving old artwork.
