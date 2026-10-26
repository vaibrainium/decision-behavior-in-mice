# Report: neuropaper S4 complete and ready for G4
Date: 2026-10-26   Agent: Codex   Commit: 8933afd
Plan: plans/2026-10-20-paper-writeup.md (task AA, S4)

## Question
Are all manuscript sections drafted, independently reviewed and ready for the author’s G4 assembly decision?

## Summary
VERIFIED: all six neuropaper sections are `passed`. Introduction v2 and title/abstract v2 each passed independent round-2 review after bounded revisions, and the full deterministic check has zero errors. G4 is written but not approved. Three Methods reproducibility-table placeholders became stale when the selected Figure 1–3 audits were completed; G4 proposes an exact evidence-only N105–N107 patch before assembly rather than silently carrying those placeholders forward.

## Findings
- VERIFIED: `np.py status` reports Methods, Results, figure legends, Discussion, Introduction and title/abstract passed, with 18 review round-trips. Source: `/src/.venv/bin/python .../scripts/np.py status` from `/src/dissemination/paper`.
- VERIFIED: Introduction v2 states pre-outcome pulse-direction assignment directly, uses each declared claim marker once and preserves the four-paragraph bounded mouse/predictive-transfer argument. Source: `np/drafts/introduction/v2.md`; reviews `np/reviews/introduction/r1.md` and `r2.md`.
- VERIFIED: title/abstract v2 uses the 75-character title, retains all seven registered number tokens and C001 only, labels the group temporal comparison descriptive, reports failed gates and says the confirmatory timing test was not run. Source: `np/drafts/title_abstract/v2.md`; reviews `np/reviews/title_abstract/r1.md` and `r2.md`.
- VERIFIED: `np.py check-all` reports zero errors. Its two number warnings are regex matches to `±100% coherence` and the `±10` working threshold; its lint warnings are the explicit Methods `[MISSING]` fields and the already-reviewed legend length.
- VERIFIED: N105, N107 and N106 now contain the final Figure 1, Figure 2 and Figure 3 panel denominator/uncertainty mappings. Source: `np/ledger/numbers.csv`; reports `2026-10-26-main-figures-1-2.md` and `2026-10-26-main-figures-3-5.md`.

## What didn't work
- The neuropaper state schema retains section `version: 1` even when later draft files pass; selected latest versions are therefore identified explicitly in G4 and must be checked during assembly.
- A clean G4 assembly cannot honestly retain the three now-resolved Figure 1–3 Methods placeholders. Because Methods already used author-approved review waivers, the correction is held for explicit human authorization at G4.

## How to reproduce
From `/src/dissemination/paper`:

```bash
/src/.venv/bin/python /root/.claude/plugins/marketplaces/neuropaper/skills/neuropaper/scripts/np.py status
/src/.venv/bin/python /root/.claude/plugins/marketplaces/neuropaper/skills/neuropaper/scripts/np.py check-all
/src/.venv/bin/python /root/.claude/plugins/marketplaces/neuropaper/skills/neuropaper/scripts/np.py check-spine
```

## Caveats
- Human-supplied animal, ethics, training, blinding, authorship, funding, availability and disclosure facts remain missing.
- Supplementary Figure S6 artwork remains to be built before simulated panel review.
- G4 has not been approved; manuscript assembly and stage advance are not authorized yet.

## Open questions and next steps
- [ ] Human approves or edits the four decisions in `np/checkpoints/G4.md`.
- [ ] On approval, apply the exact N105–N107 Methods provenance patch, rerun checks, record the quoted G4 approval and advance to S5.
- [ ] Assemble and audit the manuscript, then build S6 before simulated panel review.

