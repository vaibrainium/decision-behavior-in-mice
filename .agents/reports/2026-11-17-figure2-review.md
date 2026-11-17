# Report: Figure 2 initial walkthrough
Date: 2026-11-17   Agent: Codex   Commit: 9f21e7f
Plan: plans/2026-10-26-paper-accumulation-variant.md

## Question
After checkpointing Figure 1, begin author review of Figure 2.

## Summary
VERIFIED: inspected figures_v5/figure2.png, current caption, build code and cohort source CSV. Figure concerns matched control-model discrimination and completed paired recovery. No Figure 2 edits or new inference performed. Recommendation: explain model operations before presenting likelihood comparisons; retain RT score decomposition and recovery.

## Findings
- VERIFIED: A shows normalized held-out differences against the accumulator; positive favors accumulation. B splits those differences into choice/RT components. Source: figures_v5/source_data/fig2_AB_* and scripts/paper/build_paper_2026_11_15.py figure2.
- VERIFIED: C shows fixed-dataset recovery across five candidates, whereas D shows dependent cohort recombinations, not independent simulations. Source: fig2_C_recovery.csv and fig2_D_recombined_cohorts.csv; current caption. Original correction implementation is documented in scripts/ddm/recovery_cohorts.py (rep columns apply Holm).
- JUDGMENT: add a compact conceptual model schematic and clearer model names to orient readers before scores. Exact layout not yet chosen by author. Interpretation stays relative to tested models.

## What didn't work
No Figure 2 build was attempted; existing artwork is the current starting point.

## How to reproduce
View dissemination/paper_accumulation/draft_2026-11-15/figures_v5/figure2.png and read the Figure 2 caption and adjacent fig2_* source CSVs. Existing full builder can export to a fresh directory; no rerun required for this discussion.

## Caveats
Author-side initial review; no new statistical claims or journal-compliance certification. Recovery is conditional on tested candidates and parameters; recombined cohorts reuse simulated datasets.

## Open questions and next steps
- [ ] Review Figure 2 organization and model schematic with author.
- [ ] Implement chosen edits in a preserved new revision and show in chat.
