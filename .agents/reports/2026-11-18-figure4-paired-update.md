# Report: corrected paired panel adopted
Date: 2026-11-18   Agent: Codex   Commit: eef364b (base; update uncommitted)
Plan: plans/2026-10-26-paper-accumulation-variant.md, R

## Question
Author accepts the corrected paired α/β result and requests updating the working paper.

## Summary
Current Figure4 is v5 with corrected multi-start individual fits. Added adoption metadata and evidence-linked Results paragraph, kept matching caption/Methods. Paired B adopted; temporal panels remain for minor review. No computations rerun or values changed.

## Findings
- AUTHOR DECISION: corrected paired panel/result adopted, α=midpoint, β=coefficient confirmed.
- VERIFIED: adopted p values read directly from v5/source_data/fig4_B_paired_tests.csv; α Holm=.01171875, β Holm=.13671875; meanα−22.28180943 coherence-percentage units,9/10 expected direction. Source test SHA256 in v5/acceptance.json; Results paragraph exported alongside figure.
- VERIFIED: caption already describes19-start selection by WLS, same equation/bounds/data/mice and corrected contrasts. Methods describes same procedure. Results now explicitly marks coefficient tests exploratory and retains fit-identification limitations. v4 superseded notice preserved.

## What didn't work
No failed operations. Historical figure/Word packets not silently replaced; workspace HTML is an old Figure1 viewer and is not used as current Figure4 artwork.

## How to reproduce
Read v5/acceptance.json, results_paragraph.md and source tests; prior numerical audit report/check script reproduces fits/statistics. This adoption requires only metadata/prose edits.

## Caveats
Adoption of B does not approve every remaining temporal-panel detail or establish a new mechanism. No new fits, trials, commits/pushes or global renumbering.

## Open questions and next steps
- [ ] Continue current Figure4C temporal-panel review, then D/E.
