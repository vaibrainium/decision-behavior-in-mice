# Report: neuropaper S4 first-wave review
Date: 2026-10-25   Agent: Codex   Commit: cf6add0 (working tree; neuropaper files uncommitted)
Plan: plans/2026-10-20-paper-writeup.md

## Question
Did the first Methods, Results and figure-legend drafts pass independent scientific and statistical review within the configured two rounds?

## Summary
PARTLY. Figure legends passed, and Methods passed statistical review, but Methods and Results did not both receive full PASS after two rounds. No new analysis is required. One approved-claim inconsistency must be corrected: C007 requires secondary-pipeline gate outcomes that the Methods brief did not define. Human authorization is required before a narrowly scoped third review round.

## Findings

- VERIFIED: canonical neuropaper body counts are Methods 3,381/3,400, Results 2,785/2,850 and legends 1,404/1,650. Source: `np.py status` after round-2 review.
- VERIFIED: 38 source-mapped reproducibility settings N067–N104 resolved the round-1 tokenization P0; five unavailable final-artwork/export fields remain explicit. Source: `dissemination/paper/np/integrity/wave1_number_audit.md`; `numbers.csv`.
- VERIFIED: figure legends passed round 2; Methods statistical review passed with no P0/P1; Methods section review retained only a disputed word-count P1. Source: `np/reviews/figure_legends/r2.md`, `methods/r2_stats.md`, `methods/r2.md`.
- VERIFIED: C007 and the approved outline require N027, N034 and N036, while the Methods brief omitted ownership of the secondary-pipeline definition. Source: `np/ledger/claims.csv` C007; `np/outline.md` S6; `np/briefs/results.md`; `np/briefs/methods.md`.
- VERIFIED: hidden-coherence p values are stored, but Wilcoxon W statistics are not. Source: `np/integrity/wave1_number_audit.md`, missing item N108.

## What didn't work

- Removing the undefined secondary pipeline across v2 resolved the section review but violated the numerical scope of approved C007. The correct fix is a minimal definition plus restoration of its registered negative gate outcomes.
- Reviewer word counts included metadata differently from the neuropaper state machine. The canonical body counts are within budget.

## How to reproduce

```bash
cd /src/dissemination/paper
python3 /root/.claude/plugins/cache/neuropaper/neuropaper/0.1.0/skills/neuropaper/scripts/np.py status
rg -n '^C007,' np/ledger/claims.csv
rg -n 'N027|N034|N036' np/outline.md np/briefs/results.md np/ledger/numbers.csv
```

## Caveats

Final figure composites and their exact panel-level source tables remain unresolved. The proposed correction does not solve those artwork tasks and does not add a mechanism claim.

## Open questions and next steps

- [x] Author authorized the bounded v3 correction and one final review round (D005).
- [x] After round 3 left three P1 wording misses, author approved their direct patch and waived a fourth formal review (D006); automated checks passed and human-resolution records marked all three sections passed.
- [ ] Author verifies the rendered Results and Methods at `dissemination/paper/np/checkpoints/S4_midpoint.md` before Discussion drafting.

