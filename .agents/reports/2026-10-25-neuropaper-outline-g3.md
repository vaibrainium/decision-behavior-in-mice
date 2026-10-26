# Report: neuropaper S3 outline and G3 handoff
Date: 2026-10-25   Agent: Codex   Commit: 67df63a (working tree; neuropaper files uncommitted)
Plan: plans/2026-10-20-paper-writeup.md

## Question
Can the approved spine and literature base be converted into a draftable eLife paper architecture without overstating the mouse novelty, pulse mechanism, or inconclusive timing analysis?

## Summary
VERIFIED: yes. The revised outline assigns all 21 approved claims exactly once, gives each main figure one headline, mirrors Results and Methods, and budgets 4,980 words for the eLife main text. An independent reviewer precommitted 12 criteria, requested three bounded revisions, and passed the revised package with no remaining P0/P1/P2 issues. G3 now awaits author approval.

## Findings

- VERIFIED: Main-text targets are Introduction 700, Results 2,850, Discussion 1,200, and title/abstract/impact 230 words (total 4,980); Methods and legends are separately budgeted at 3,400 and 1,650 words. Source: `dissemination/paper/np/outline.md`, `np.py status`.
- VERIFIED: all claims C001–C021 have one primary location; the five main figures follow task, input reconstruction, control-model comparison, randomized pulse behaviour, and pipeline mismatch. Source: `dissemination/paper/np/outline.md`, Primary claim placement audit.
- VERIFIED: Supplementary Figure S6 remains a named main-text Results subsection reporting failed gates, inadequate sensitivity, and the withheld timing test. Source: `dissemination/paper/np/outline.md`; `np/briefs/results.md`.
- VERIFIED: the final review verdict is PASS with all K1–K12 met and no remaining issues. Source: `dissemination/paper/np/reviews/outline/r2.md`.
- VERIFIED: contracts, spine hash, claim/number lint, and whitespace checks pass. Commands: `np.py check-contract ...`, `np.py check-spine`, `np.py check-all`, `git diff --check` from `/src/dissemination/paper`.

## What didn't work

- The first review found three P1 issues: C009 appeared co-equal with C006 in Figure 5, a secondary leak/urgency method lacked a Results destination, and blinding/AI/end-matter placeholders were incomplete. One bounded architect revision resolved all three; the unchanged reviewer criteria then passed.

## How to reproduce

```bash
cd /src/dissemination/paper
python3 /root/.claude/plugins/cache/neuropaper/neuropaper/0.1.0/skills/neuropaper/scripts/np.py status
python3 /root/.claude/plugins/cache/neuropaper/neuropaper/0.1.0/skills/neuropaper/scripts/np.py check-spine
python3 /root/.claude/plugins/cache/neuropaper/neuropaper/0.1.0/skills/neuropaper/scripts/np.py check-all
git -C /src diff --check
```

## Caveats

The outline does not supply missing animal, ethics, hardware, blinding, authorship, funding, repository, or disclosure facts. Figure composites are not yet assembled, so final panel letters and legends will require reconciliation. G3 approval is required before prose drafting.

## Open questions and next steps

- [ ] Author approves or edits G3, including the indicative title and the recommendation not to demote the failed-gate material.
- [ ] After approval, draft Methods and Results/Figure legends in parallel under separate writer/reviewer roles.
- [ ] Pause at the neuropaper midpoint for author verification of Results and Methods before later sections.

