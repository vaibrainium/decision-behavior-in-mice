# Report: What to adopt from the supplied pulse PDF
Date: 2026-11-19   Agent: Codex   Commit: ed2d38d (review notes uncommitted)
Plan: plans/2026-10-26-paper-accumulation-variant.md

## Question
What can be adopted from the author's supplied Huk–Shadlen replication PDF for the current manuscript?

## Summary
Author clarified that the goal is reuse and scientific presentation, not another correctness audit. All PDF page text and page artwork were read. The main reusable contribution is persistence after the pulse, complementary to the onset-stage dependence in current Figure 4C. Recommend the standard response-latency directional curve and its dilution-adjusted companion together; keep detailed congruency/individual/ROC views as supporting material. No figure changes authorized or made this turn.

## Findings
- VERIFIED: PDF page 4 right-hand plot presents a Huk-style pulse-to-response time course. Page 8 separates directional and shared effects. Their source scripts are scripts/behavior/huk_shadlen_replication.py and scripts/behavior/pulse_decomposition.py; artwork/source tables live in dissemination/paper_accumulation/figures/qc and tables. Former Figure 4C already preserves the page-8 directional/shared estimates in figure4_revision_2026-11-19_v6/supplementary_drafts/.
- VERIFIED: PDF page 9 dilution-adjusted time course is already represented in current Figure 4D, with later bootstrap intervals from dissemination/pulse_dynamics_2026-11-13. It is a companion to the ordinary directional curve, not a replacement for pulse-onset primacy.
- VERIFIED: PDF pages 5–6 offer per-mouse and model-free support; page 7 ROC is supporting detail. Page 4 joint choice/mean-RT fit is a distinct historical fit, not the selected control model now used in Figure 3.
- VERIFIED: current Figure 4C uses pulse-onset stage; PDF temporal curves use response latency measured from pulse onset. These are different independent variables. The narrative can connect directional use, onset dependence, persistence, and late attenuation without treating them as independent replications.
- VERIFIED: primary Huk/Shadlen text read at https://pmc.ncbi.nlm.nih.gov/articles/PMC6725829/ (behavioral Figure 4 and Discussion). Persistent choice effects support temporal integration; the paper distinguishes apparent persistence from an intrinsic integration time constant.

## What didn't work
No installed PDF reader or system PDF executable was available. The supplied PDF has a Unicode text layer and full-page images, so these were extracted locally with Python standard library and installed Pillow; no installation required. Temporary extractor: /tmp/read_supplied_pulse_pdf.py. Derived pages and extracted_text.md: dissemination/pdf_review_2026-11-19/.

## How to reproduce
Read /src/Mouse pulse effects Huk & Shadlen replication.pdf and dissemination/pdf_review_2026-11-19/extracted_text.md; compare scripts/behavior/{huk_shadlen_replication,pulse_decomposition,pulse_dilution,congruency_roc}.py and current Figure 4 caption. No fits, simulation, exclusions or tests were rerun. A read-only loader/table check was performed; its numerical details are not new inferential results and are not needed for adoption decisions.

## Caveats
Panel placement below is a recommendation, not author approval. Keep the positive persistence/late-reduction result central. Do not describe nonsignificant asymmetry as demonstrated equivalence, or finite apparent persistence as a direct intrinsic memory constant. Avoid duplicating pulse psychometrics or introducing a second diffusion-fit story without a specific reason.

## Open questions and next steps
- [ ] Author decide whether to restore a simplified directional response-latency panel alongside the existing dilution-adjusted panel.
- [ ] If requested, render that panel from saved estimates and assess the full Figure 4 layout before moving assignment-based support.
