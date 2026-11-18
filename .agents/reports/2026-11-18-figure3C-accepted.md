# Report: Figure3C accepted
Date: 2026-11-18   Agent: Codex   Commit: 294cddc (base; approval update uncommitted)
Plan: plans/2026-10-26-paper-accumulation-variant.md, R

## Question
Author approves recovery matrix C.

## Summary
Recorded C approval and exported standalone C without D for later Figure3 A–C assembly. Both A alternatives remain accepted with final choice deferred; B approved; former D text-only. No result changes.

## Findings
- AUTHOR DECISION: C is fine/approved.
- VERIFIED: source matrix CSV byte-identical to reviewed figure3_control_results_2026-11-17/source_data/fig3_C_recovery.csv; row totals20 checked. Standalone export inspected; script compiles. Caption/acceptance metadata and source hashes in figure3C_final_2026-11-18/ under draft directory.
- VERIFIED: C-only renderer option changes layout only, retains all25 entries and original fraction color scale. D excluded from artwork. Accepted canonical files figure3C.png/pdf/svg.

## What didn't work
No failed operations; no new recovery simulations or inference.

## How to reproduce
```bash
.venv/bin/python -m scripts.paper.figure3_recovery_preview --input dissemination/paper_accumulation/draft_2026-11-15/figure3_control_results_2026-11-17 --output <fresh-directory> --only-c
```
Canonical C copies duplicate the renderer's figure3_CD outputs. Source/script hashes in manifest.json; approval/source integrity in acceptance.json.

## Caveats
Recovery conditional on tested candidates/parameters/schedules. Historical packets retain older numbering/layouts until combined figure assembly. No commits/pushes.

## Open questions and next steps
- [ ] Assemble Figure3 A–C, retaining both A alternatives until author chooses.
- [ ] Continue figure-led paper review with pulse figure when author resumes pulse work.
