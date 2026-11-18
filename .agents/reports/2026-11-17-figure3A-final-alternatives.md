# Report: retain both finalized Figure 3A alternatives
Date: 2026-11-17   Agent: Codex   Commit: 294cddc (base; this update uncommitted)
Plan: plans/2026-10-26-paper-accumulation-variant.md, step R

## Question
Retain both finalized panel A alternatives, leaving the choice to the author later.

## Summary
Both LL/BIC and joint-bits/BIC dual-axis figures are registered as author-finalized alternatives for the same panel A. Neither selected over the other. Working draft README, figure index and caption packet link both.

## Findings
- VERIFIED: accepted PNG/PDF/SVG copied byte-for-byte from figure3A_both_dual_axes_2026-11-17 into figure3A_final_alternatives_2026-11-17, under dissemination/paper_accumulation/draft_2026-11-15/. All six artwork copies verified identical; SHA256 hashes in selection.json.
- VERIFIED: captions, source CSV and original score manifest preserved alongside accepted copies. selection.json explicitly leaves selected_alternative null.
- AUTHOR DECISION: both alternatives final; author will choose final A later. This supersedes earlier requests for author assessment of these two renders.

## What didn't work
No failed operations. No rerendering or score changes needed.

## How to reproduce
Copy listed assets from source to accepted directory; compare bytes and SHA256 against selection.json. Rendering remains reproducible with scripts.paper.figure3A_dual_axes, as documented in the prior metric-alternatives report.

## Caveats
Acceptance concerns artwork alternatives; it does not remove QMLE/dual-axis interpretation caveats. Historical combined manuscript figures retain their numbering until overall figure assembly is finalized. No commit or push.

## Open questions and next steps
- [ ] Author choose A1 or A2 later.
- [ ] Continue Figure 3 review with panel B.
