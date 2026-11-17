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

- [ ] R. Author-led figure-by-figure review: discuss Figure 1 and resolve revisions before proceeding sequentially.

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

- 2026-11-17: Author steers to figure-by-figure review before remaining prose. Figure 1 inspected against caption/source CSVs; recommendations await author discussion. No artwork/data changed. See ../reports/2026-11-17-figure1-review.md.

- 2026-11-17: Author requests explicit physical-direction pulse wording. Updated legend/caption and exported figure1_revision_2026-11-17; inspected rendered result. Other Figure 1 recommendations remain pending.

- 2026-11-17: Author requests in-conversation figure previews for subsequent edits. Created figure_review/figure-workspace.html from the actual latest Figure 1 SVG, with full/B focus selection. Continue displaying revisions inline; preserve static scientific exports.

- 2026-11-17: Author requests C/D controls only, observed points and their existing four-parameter psychometric fit. Verify archived scheduled-control selection; fit per-mouse and equal-mouse group curves using src/utils/pmf_utils.py; show RT data without a psychometric fit; export fresh revision, inspect and show inline. This author request authorizes these small descriptive fits; no decision-model fits.

- 2026-11-17: Completed requested C/D control-only presentation: points and author logit_4 fits in C, observed RT points in D. Exported v2, verified source-table identity and curve predictions; inspected render. Caption/Methods updated; discuss current Figure 1 next.

- 2026-11-17: Author approves C and requests Basso mean-RT figure precedents before revising D. Focused search and primary caption/render inspection completed for Jun et al. 2021 Figures 2 and 5; recommendation in ../reports/2026-11-17-basso-rt-display.md. C remains selected; D not yet changed.

- 2026-11-17: Author authorizes trying mean-RT D redesign. Recompute signed-coherence control means from valid_data.csv, verify control counts against accepted C, retain the existing minimum of 10 trials per mouse/coherence/outcome cell and disclose varying error-cell mouse counts. Export fresh v3, inspect, update caption/Methods, show in chat.

- 2026-11-17: Mean-RT D trial completed as v3. Verified original scheduled-control membership, unchanged approved C, equal-mouse means/SEM, and disclosed 7–10 mice for signed error cells. Figure inspected; caption/Methods/Results aligned. Next: author assess D preview.

- 2026-11-17: Author requests left/right choice RT grouping. Completed v4: orange right-choice circles/solid line and blue left-choice squares/dashed line; zero coherence included in both series. Verified raw choice means and subject SEM; C unchanged. Caption/Methods/Results aligned; inspected render; next author assess D.

- 2026-11-17: Author requests both RT traces solid and shaded SEM rather than error bars. Completed v5 with alpha 0.18 pointwise ±SEM bands; all source CSVs identical to v4, render inspected and caption/Methods updated. Next: continue author figure discussion.

- 2026-11-17: Author requests removing E. Completed v6 with compact 2×2 A–D layout, revised title/caption and removal of obsolete Results panel reference. Exclusion details retained in Methods and population source CSV. Verified all source values unchanged from v5 and visually inspected export.

- 2026-11-17: Author requests commits and progression to Figure 2. Figure 1 implementation/artifacts/text committed as 9f21e7f; no push. Initial Figure 2 walkthrough recorded in ../reports/2026-11-17-figure2-review.md. Current review step R continues with Figure 2; no Figure 2 edits yet. Scoped Python/Markdown whitespace and compile checks pass; generated SVG whitespace retained.

- 2026-11-17: Author requests full Figure 2 redesign, starting only with A introducing tested models, inspired by Stine et al. 2020 (inferred from “stein”). Plan: inspect primary Figure 1 and local C/E/ES rules; draw original labeled illustrative traces/bounds with exported schematic coordinates and parameters; verify dynamics and inspect rendering; show in chat. Preserve existing full Figure 2 and defer remaining panels.

- 2026-11-17: Completed A schematic draft v3 with source-linked C/E/ES rules, identical illustrative increments, thresholds and first crossings; caption states illustrative status and omitted shared components. Convolution/first-crossing checks pass; render inspected after correcting a clipped illustrative marker. Full Figure 2 untouched. Next: author review A, then B onward.

- 2026-11-17: Author approves adding DDMx/ESx within the accumulation/extrema columns. Completed A v4 with all five labels and input/response-component notes; schematic coordinates unchanged; caption updated and render inspected. Next: assess A, then B.

- 2026-11-17: Author approves separating model introduction from results. Build standalone Figure 2 with decision-rule schematics (A) and compact five-implementation table (B); export existing control results separately as provisional Figure 3, with linked source/caption and clearly pending redesign. Preserve earlier figures/manuscript numbering while this figure-led review proceeds; document proposed downstream numbering. Verify source identities and renders, then show model figure in chat.

- 2026-11-17: Completed approved split: standalone Figure 2 (rules + implementation table), separate provisional Figure 3 (existing control scores/recovery), index mapping proposed five-figure organization. Verified unchanged schematic coordinates and control-result values; inspected renders. Captions adjacent; global manuscript numbering deliberately pending artwork selection. Next: assess model figure, then redo results Figure 3 including existing observed/predicted behavior.

- 2026-11-17: Author accepts model Figure 2 and requests commit/move on. Figure/artifacts/split committed as a20629e; no push. Current focus Figure 3 opening observed/predicted behavior panels, then scores/recovery. Initial source check finds legacy chronometry only C/E with differing fit sources, so audit matched saved predictions before new overlays. See ../reports/2026-11-17-figure3-review.md.
