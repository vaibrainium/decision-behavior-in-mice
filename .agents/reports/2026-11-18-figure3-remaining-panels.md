# Report: remaining Figure 3 panel review
Date: 2026-11-18   Agent: Codex   Commit: 294cddc (base; uncommitted review notes)
Plan: plans/2026-10-26-paper-accumulation-variant.md, step R

## Question
Resume remaining panels after both A alternatives were finalized.

## Summary
Existing B decomposes held-out score advantages into choice and conditional RT; C is fixed-data model recovery; D is cohort recombination. Recommend start with B, retain recovery C, consider D supplementary. This is a proposal, not an author-approved rearrangement. A alternatives remain intact and selection pending.

## Findings
- VERIFIED: B source per-mouse means (NLL advantage per 1,000 trials): E choice 2.5463479401, RT 10.2101159573; ES choice 1.2166813821, RT 17.5282818109. Ten mice per component. Independently averaged via stdlib CSV from dissemination/paper_accumulation/draft_2026-11-15/figure3_control_results_2026-11-17/source_data/fig3_AB_control_differences.csv; match adjacent group statistics. Components are choice and RT conditional on choice, not independent fits. E component total is minutely different from original saved total; existing rescored_total agrees with decomposition, as archived; do not force exact equality to original total.
- VERIFIED: recovery source fig3_C_recovery.csv rows sum to 20. C-generated: C wins19/20, ES1/20. E-generated: C2, E10, ES6, ESx2; ES-generated: E10, ES10. Recovery supports stronger C discrimination than E-versus-ES separation. Conditional on the tested models/parameters/schedules.
- VERIFIED: D source fig3_D_recombined_cohorts.csv summarizes 1,024 recombinations of reused replicates, not independent simulations. Matched E/ES comparisons produce the same all/none group pattern already stated in the caption.
- JUDGMENT: B should answer where A's predictive advantage originates, preferably show choice/RT separately instead of stacked totals. C should show identifiability limits openly. D may be redundant in the main figure; supplementary placement is proposed. Observed/predicted control behavior could be more informative than D but matched all-candidate predictions remain unaudited (see earlier Figure 3 review); no new overlays invented.

## What didn't work
No new plot attempted. Legacy data/common/E chronometry alone cannot provide matched five-candidate held-out behavioral overlays.

## How to reproduce
Read current figure3_control_results_2026-11-17/figure3.png, caption.md and adjacent source CSVs. For decomposition average per_1000 by model/part in fig3_AB_control_differences.csv. Builder: scripts/paper/build_paper_2026_11_15.py, figure2; wrapper scripts/paper/review_control_results.py.

## Caveats
No new inference, fits, simulations or artwork changes. User preferences remain one panel at a time; no mouse-facet crowding. No claims of temporal integration strength or pulse mechanism from control score decomposition alone.

## Open questions and next steps
- [ ] Discuss B choice/RT decomposition and agree rendering.
- [ ] Review recovery C, then decide placement of D.
- [ ] Audit matched saved predictions before adding observed/predicted behavior panels.

## C/D preview — 2026-11-18
After approving B, author requests viewing remaining panels. Rendered existing C/D alone into figure3_CD_review_2026-11-18/ under draft directory with scripts.paper.figure3_recovery_preview. Source CSV copies byte-identical, matrix rows verified20, PNG inspected; no new results or simulations. Manifest records source/script hashes. Reproduce with --input <draft>/figure3_control_results_2026-11-17 --output <fresh-directory>. C recovery and D placement remain pending review; A/B unchanged.
