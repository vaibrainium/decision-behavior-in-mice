# S4 wave-1 review-limit checkpoint

Date: 2026-10-25
Stage: S4 drafting
Decision: APPROVED by V. Thakur — “Approve this bounded v3 correction and one final review round”

## Produced

- `np/drafts/methods/v2.md`: canonical neuropaper count 3,381/3,400 words; statistical review PASS; section review REVISE.
- `np/drafts/results/v2.md`: canonical neuropaper count 2,785/2,850 words; section/statistical reviews REVISE.
- `np/drafts/figure_legends/v2.md`: 1,404/1,650 words; section review PASS.
- `np/integrity/wave1_number_audit.md`: audited every first-wave numerical setting; 38 source-mapped rows N067–N104 were added to `numbers.csv`; five unavailable final-artwork/export fields remain explicit.
- Round-1 and round-2 criteria/reports for all three sections, including independent statistics review for Methods and Results.

## What passed

- Figure legends passed all committed round-2 criteria.
- Methods passed the independent statistical review with every round-1 issue resolved.
- Claims, number tokens, contracts and the locked spine pass automated checks.
- No reviewer requested a new scientific analysis.
- Undefined secondary-pipeline references were removed consistently in v2, but this exposed an approved-claim inconsistency described below.

## Human resolutions needed

1. **Review-round limit:** Methods and Results have used the configured two rounds without both receiving PASS. Authorize one final, narrowly scoped revision/re-review, or stop those sections as `needs_human`.
2. **Canonical word count:** the section reviewer counted contract/metadata text and reported 3,403 Methods words and 3,005 Results words. The neuropaper state machine reports the manuscript body at 3,381/3,400 and 2,785/2,850. Recommendation: accept the canonical counts and dismiss both budget findings.
3. **Secondary predictive-gate record:** approved claim C007 and the approved outline explicitly require N027, N034 and N036 for the secondary pipeline, but the Methods brief failed to assign its definition. Round 1 therefore removed it as undefined; the statistics reviewer correctly flagged its absence in v2 as a locked-scope regression. Recommendation: restore the three registered gate outcomes and add only the minimal secondary-pipeline definition/provenance to Methods/S6, without promoting it to a headline or mechanistic claim.
4. **Supplementary hidden-coherence tests:** their p values were saved but their Wilcoxon W statistics were not. Recommendation: remove the two inferential test sentences from Results and retain only the conditional descriptive ratio/caveat, rather than rerunning/exporting statistics for a non-central unresolved supplement.

## Proposed bounded correction

- Methods v3: add a concise definition of the secondary leak/urgency baseline used only for the registered S6 gate outcomes; retain the canonical budget.
- Results v3: restore N027, N034 and N036 with explicit secondary/exploratory labels; remove the two incomplete Wilcoxon inferential sentences; preserve all central results and the canonical budget.
- Figure legends remain passed unless the restored S6 values require a minimal synchronized legend patch.
- One final review verifies only these corrections and regressions; no new criteria, claims, numbers or analyses.

## Approved resolution

The proposed bounded correction and one final review round are approved. This resolves an internal G3 brief inconsistency while preserving the locked C007 negative-result record and avoids spending time on a non-central hidden-coherence statistic export.

## Final-review outcome

The bounded v3 drafts restored C007 and passed all canonical budgets, but each section retained one P1 literal-scope miss; there were no P0 issues or requests for analysis. Neuropaper therefore marked Methods, Results and Figure Legends `needs_human` after round 3.

Recommended direct editorial resolution, without another formal review round:

1. Methods: delete the stale N085/N086 Wilcoxon procedure and missing-W placeholder; remove those tokens from its contract.
2. Results: add that the retained descriptive N011 ratio lacked a scheduled-control-label sensitivity analysis; add the exact secondary identifier `L1U1V1Z0G1` at its first S6 mention.
3. Figure Legends: add `L1U1V1Z0G1` at the first S6 secondary-baseline mention.
4. Run contract, claim, number, lint, spine and whitespace checks, then record the author's waiver of a fourth review and present the corrected Methods/Results midpoint package.

