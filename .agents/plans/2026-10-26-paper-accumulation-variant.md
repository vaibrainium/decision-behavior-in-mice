# Plan: accumulation-first paper variant (neuropaper, separate folder)
Status: active
Created: 2026-10-26 by Claude (Opus 5.5)
Related reports: ../reports/2026-11-16-figures-first-draft.md; reports/2026-10-26-neuropaper-s5-s6.md (first version), reports/2026-10-23-control-only-selection.md

## Goal
Current authorized pass (2026-11-15): write a complete accumulation-first working manuscript for a Neuron research-article audience in `dissemination/paper_accumulation/draft_2026-11-15/`, retaining sustained pulse influence as a central result and using completed corrected recovery. Original variants/results remain intact.

Historical goal (superseded where it conflicts with the current author request):
A second full neuropaper manuscript in `dissemination/paper_accumulation/` framed as: (1) mice perform/learn the task;
(2) control trials favor accumulation over the tested extrema-like model, with the needed model variant; (3) primacy vs
recency not determinable from pulses. The first version (`dissemination/paper/`) stays untouched for comparison.

## Context
Same analyses as the first version; numbers and verified sources copied, new rows N110-N117 added.

## Assumptions
- Current author authorization supersedes old manually imposed scientific gates; no external submission or human verification is inferred. Drafting proceeds now, with missing author facts and pending human source review explicitly recorded.
- No new model fits, package changes, cluster submissions, commits or external uploads of unpublished content in this writing pass.
- No new analyses unless the author approves them at G0 (learning curves; real-data fluctuation kernel).

## Steps
- [x] 1. np init, config, ledgers copied, G0 checkpoint written.
- [x] 2. G0 approval (D001): targeted lit search; 'perform' only; eLife; kernel only if it passes; V. Thakur approves.
- [x] 2b. Amendment 8 kernel on recorded choices: neither model fits -> not supporting evidence (reports/2026-10-26-fluctuation-kernel-observed.md).
- [x] 3. Historical neuropaper workflow (superseded by current authorized writing pass below; not a remaining approval requirement).
- [x] 4. Historical gated stages (superseded by current authorized writing pass below).
- [x] 5. Historical variant comparison (superseded by evidence-linked current draft; old manuscripts preserved).


### Current authorized writing pass — 2026-11-15
- [x] A. Orient to evidence and author corrections; read writing/citation/venue/figure skills and the prior active plan.
- [x] B. FIGURES: assemble and visually inspect a current main-figure set with panel source tables and provenance, using completed results only.
- [x] C. CAPTIONS: write legends matched to the assembled figures and exact populations/uncertainty.
- [x] D. METHODS: write performed procedures from code/provenance; leave genuinely missing author facts explicit.
- [x] E. RESULTS: write figure-led Results from the assembled evidence, keeping sustained pulse influence central.
- [x] F. Verify source/numeric consistency, provide an editable reading copy, report and update STATUS.

- [ ] G. Next phase: write Introduction, Discussion, Summary and final title from the figure-led argument; incorporate supporting analyses and author facts as appropriate.

The figures/captions/Methods/Results packet is complete; the overall manuscript plan remains active for the next phase.

## Out of scope
Changes to the first version's files.

## Log
- 2026-10-26: started at author request ("start working on this paper in a separate folder").
- 2026-10-26: G0 approved; amendment 8 run, verdict 'neither'; whether to mention it goes to G1. Next: S1 architect.

- 2026-11-15: Resumed this existing active plan rather than opening another manuscript plan. Author explicitly requests using repository skills and starting the paper after approving retention of the Huk-style persistence analysis. Current pass replaces the obsolete gated sequence; old spine/manuscripts/results untouched. Use agent-inspected evidence for a clearly labeled draft; do not impersonate human verification or submission approval. Current Neuron author page returned 403; exact format limits remain unverified, so use a provisional research-article structure. ARRIVE official guidance was accessible.
- 2026-11-15: Author steered the order explicitly to figures → captions → Methods → Results → remaining sections. No manuscript prose existed at interruption. Following this order now; no preliminary Introduction/Discussion/Summary drafting. Four main figures are provisional scientific organization, not an asserted Neuron figure limit.
- 2026-11-15: Figure stage complete: figures_v4 contains four main figures in PDF/SVG/300-dpi PNG, a combined PDF, 22 source tables and SHA-256 provenance. Earlier layout versions retained. New plotting-only build uses saved tables and does not fit/simulate. Old shared-style import made lazy to avoid an unavailable OpenCV libGL dependency; scientific behavior unchanged. Canvas text and basic embedded-font checks passed; main layouts inspected visually.
- 2026-11-15: Captions completed after figure selection in draft_2026-11-15/figure_captions.md. Explicitly distinguish descriptive controls (14,015) from model controls (14,014), the 19,313 response-conditioned temporal observations from assignment endpoints, 300- versus 600-mouse-bootstrap intervals, and dependent recovery recombinations. Next: Methods from performed code/provenance.
- 2026-11-15: Methods draft completed after captions in methods.md, based on inspected implementations and read-back settings from 400 saved control fits. Animal/ethics/apparatus/authorship facts remain explicit author-detail fields. Historical filtering reports the var parameter correctly as logistic slope. Public-reference metadata retrieved from Crossref with stdlib because the optional citation CLI lacks requests; no installation. Next: figure-led Results.
- 2026-11-16: Caption/Methods review motivated one figure refinement before Results: add the existing hierarchical cohort interval to Figure 4C so average compatibility and individual discrepancies are visible together. Rebuild as figures_v5; earlier artwork remains unchanged. Caption source links updated.
- 2026-11-16: Author additionally requests matching the language and structure of comparable decision-making papers. Before drafting Results, inspect primary full texts (Huk 2005, Stine 2020/2023, Odoemene 2018, Roy 2021), record structural/style lessons and apply them in original prose. Preserve figures → captions → Methods → Results order; no change to evidence or model fitting.
- 2026-11-16: Figure-led Results completed after Methods, using comparable-paper structure: specific question, brief comparison, figure-linked finding, bounded inference. Five primary-paper comparators inspected for rhetoric/organization, with access limitations recorded. No Introduction/Discussion/Summary drafted. Next: evidence mapping, numeric/reference checks, editable reading copy and report.
- 2026-11-16: Completed first writing packet; report ../reports/2026-11-16-figures-first-draft.md. Selected figures_v5, working_draft_v3.docx/Markdown, 23 source tables and 77 mapped claims. Final structural/reference/declared-consistency checks pass; human verification and publication-policy records intentionally remain open. Introduction/Discussion/Summary are the next unchecked current-phase step. No new fits, simulations, installs or submission.
- 2026-11-16: Historical steps 3–5 marked dispositioned as superseded, not as executed; current step G is now the first unchecked action for a cold continuation.
