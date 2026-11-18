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
  - [x] Figure 3 metric additions: joint test bits, training-only choice gain, independently rescored QMLE ΔBIC; arithmetic/seed checks and renders verified (2026-11-17).
  - [x] Figure 3A: both LL/BIC and joint-bits/BIC dual-axis alternatives author-finalized and included; author selection deferred (2026-11-17).
  - [x] Figure 3B: model C psychometric/chronometric with author logit_4 display curves approved, original full-control parameters retained (2026-11-18).
  - [x] Figure 3C recovery matrix approved; former D text only. Figure3 A–C panel review complete, final A selection and assembly pending (2026-11-18).

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

- 2026-11-17: Author redirects Figure 3A to absolute NLL rather than differences. Build one-panel preview with five-fold total held-out NLL for all five candidates, faceted by mouse because counts differ. Verify raw totals/counts against archived fold inventory and original comparison differences; preserve previous layouts. No per-trial normalization or new scores/fits.

- 2026-11-17: Completed raw-NLL A preview. All five candidates/10 mouse facets; exact five-fold totals and trial counts verified against fold inventory and original differences; render inspected. Caption/source exports included. No new fitting/scoring/statistics. Next: author assess A before other panels.

- 2026-11-17: Author requests raw NLL bar graph for A and comparison with Stine. Existing raw-score preview found in workspace; preserve it. Check Stine primary comparison display, convert only rendering to zero-baseline per-mouse bars with numerical values, retain all five candidates and raw five-fold totals; verify exact source identity and inspect new version. No new fits/scores/statistics.

- 2026-11-17: Completed direct-NLL horizontal bar A v2 after Stine Figure 7B check (source uses ΔBIC). Raw scores/fold exports identical to preceding preview; all bars zero-based with subject-specific axes and numeric labels. Inspected render after fixing clipped labels. Current A selected for discussion; next author assess before B.

- 2026-11-17: Author requests removing mouse breakdown. Aggregate verified raw five-fold NLLs into a single five-bar panel using equal-mouse mean and SEM; retain raw scores and no reference subtraction/per-trial normalization. Preserve per-mouse display via CLI option and earlier exports; verify aggregation and inspect.

- 2026-11-17: Completed single-panel A cohort display with means/SEM across 10 mice. Verified aggregate arithmetic and unchanged raw scores/folds; render inspected. Current selection figure3A_group_nll_2026-11-17; author assessment next.

- 2026-11-17: Author challenges raw-NLL SEM display. Confirmed SEM across uncentered subject totals does not represent uncertainty in paired model differences. Remove bars of uncertainty, preserve raw mean heights, export existing corrected paired tests separately with explicit per-trial estimand; do not put significance stars on raw means using a different estimand. Inspect new version.

- 2026-11-17: Corrected SEM presentation; current A figure3A_group_nll_no_sem_2026-11-17 keeps exact mean raw scores without error bars, alongside separately documented existing paired tests. Means/folds verified unchanged; render inspected. Paired normalized tests are distinct from raw mean bars; t/Wilcoxon robustness difference disclosed.

- 2026-11-17: Author requests points. Completed A points v2 with same means and numeric labels, no uncertainty bars and labeled tighter NLL limits; CSV identity verified and render inspected. Next: author assess A before B.

- 2026-11-17: Added author-requested connecting line to A; all source values/axes unchanged, render inspected. Current preview figure3A_group_nll_connected_2026-11-17; author assessment next.

- 2026-11-17: Author requests connected-point test bits/trial and ΔBIC panels. Closest “JLM 2021” reference identified as Ashwood GLM-HMM 2021 preprint/2022 publication, with choice-only gain over a train-set Bernoulli baseline. Plan: preserve A; derive a joint test-log-score bits/trial view and a distinctly labeled Ashwood-style choice-gain view from saved control CV scores and fold-specific training-only nulls; audit full-control fit counts/free parameters and benchmark independent training rescoring for valid QMLE ΔBIC (not CV BIC), with two independent seeds if bounded; export source tables/checks, inspect renders and explain metric distinctions. No fitting or new experimental data. Previous fixed-bin bits outputs are known noise-limited and will not be reused.

- 2026-11-17: Completed metric additions under step R; 100 independent fixed-parameter training evaluations, no refits. Main B/C preview and separate choice-only companion inspected, all numerical checks pass. Report: ../reports/2026-11-17-figure3-bits-bic.md. Next author assess B/C and select bits definition; overall figure review remains active.

- 2026-11-17: Author requests normal absolute IC plot after BIC/ΔBIC discussion. Rendering-only continuation of R: average existing seed-averaged per-mouse BIC equally across mice, verify differences reproduce prior ΔBIC, preserve old outputs, inspect new connected-point preview and report. No rescoring/refits.

- 2026-11-17: Absolute BIC rendering completed; matched subject coverage, source values and identity with prior ΔBIC checked; render inspected, source compiles. Report: ../reports/2026-11-17-figure3-absolute-bic.md. Next: author assess preview.

- 2026-11-17: Author requests two panel-A alternatives: held-out NLL left axis / training BIC right axis, and joint test bits left / BIC separate right panel (literal requested right panel). Rendering only from approved source tables; export fresh outputs, verify identities and inspect both. Dual-axis ranges stay independently labeled and are not tuned for curve alignment.

- 2026-11-17: Both A alternatives completed; source means/checks verified, renders inspected and script compiles. Report: ../reports/2026-11-17-figure3A-metric-alternatives.md. Next author select layout; R remains active.

- 2026-11-17: Requested LL sign change completed in fresh A1 output; exact sign/unchanged BIC/bits checks, compile and visual inspection pass. Report updated: ../reports/2026-11-17-figure3A-metric-alternatives.md.

- 2026-11-17: Author clarifies both A alternatives require dual axes. Completed rendering-only LL/BIC and bits/BIC with identical source values, checked exports and inspected both; report ../reports/2026-11-17-figure3A-metric-alternatives.md updated. Previous separate-right-panel interpretation superseded. Next author select A.

- 2026-11-17: Author finalizes both A alternatives, will choose later. Added immutable copies with source/captions/hashes and pending-selection record; linked both in working packet. Report: ../reports/2026-11-17-figure3A-final-alternatives.md. Next review panel B; do not block on A selection.

- 2026-11-18: Resume R after finalized A alternatives. Reviewed existing B/C/D and source values. Next B: explain choice/conditional-RT score contribution and discuss rendering, then C recovery. D supplementary placement proposed only; behavioral overlays require matched prediction audit. Report: ../reports/2026-11-18-figure3-remaining-panels.md. No new artwork/scores/fits.

- 2026-11-18: Author rejects decomposition B; replaces it with control model fits on data, psychometric and choice-conditioned mean RT as Figure 1. Steps: audit response/control membership and 50 saved full-control fits; produce bounded fixed-parameter predictions (20 repetitions/input), cache aggregate counts/RT sums to fresh outputs; match observed subject/coherence and RT choice-cell eligibility to Figure 1; plot five model columns (psychometric above, left/right-choice mean RT below), inspect and document. Descriptive in-sample predictions, no refitting; A alternatives preserved. Existing caches lack choice-specific RT and cannot substitute.

- 2026-11-18: B preview completed from50 saved full-control fits,20 repetitions/input, no refits. Exact Fig1 membership assumption failed by one missing-pulse-duration PSUIM7 control; B uses14,014 modeled controls and documents difference. Independent aggregation/raw-data checks pass; render inspected. Report: ../reports/2026-11-18-figure3B-control-fits.md. Next author assess B. Rejected decomposition B remains historical only.

### Figure 3 likelihood audit (2026-11-17 client date)

- [x] Locate current Figure 3 score provenance, earlier audits and fitting entry point.
- [x] Trace observed and simulated responses through training and scoring. Check normalization, RT binning, response conditioning and sparse cells against the intended objective.
- [x] Verify with bounded checks on synthetic counts and processed inputs and trace archived Figure 3A arithmetic.
- [x] Record findings and limitations in a [linked report](../reports/2026-11-17-ddm-likelihood-audit.md) and STATUS.

Audit scope is the current response-conditioned control fits and their reported scores. Historical branches are checked where shared code affects the interpretation. No refits are needed for this audit.

- 2026-11-18: Author narrows B to model C psychometric/chronometric full-control fit; pulse explicitly deferred. Rendering-only subset completed with exact source checks and visual inspection. Report: ../reports/2026-11-18-figure3B-model-c.md. Unseen-control prediction remains assessed with held-out A scores; parameters/curves use full-control fits. Next author assess B.

- 2026-11-18: Clarified actual optimization provenance for B: read all10 C control-fit pickles, n_train equals full eligible controls per mouse. Existing full-control optimization already supplies B parameters; no need to optimize again just for plotting. Report ../reports/2026-11-18-figure3B-model-c.md updated.

- 2026-11-18: Author requests four-parameter psychometric curves instead of joined coherence segments. Use exact author logit_4 helper as Fig1; fit equal-mouse observed and C-predicted proportions separately, export coefficients/dense curves and raw source values. Retain raw data points, label descriptive smoothing clearly, leave RT values/layout intact, verify bounds/monotonicity/source identities and inspect. No DDM refits or pulse work.

- 2026-11-18: Four-parameter psychometric revision completed with exact author helper; separate observed/predicted group fits, source tables/RT unchanged, coefficients-to-curves independently verified and render inspected. Report ../reports/2026-11-18-figure3B-model-c.md updated. Next author assess revised B.

- 2026-11-18: Author questions E/ES visual fit versus C LL. Bounded check confirms E/ES lower group mean-RT RMSE, but not choice-proportion RMSE, than C. This differs from CV quantile log score in summary/weighting and fit parameters; exact RT-bin source of advantage not diagnosed. Report: ../reports/2026-11-18-figure3B-mean-versus-score.md. No artwork altered or new group inference.

- 2026-11-18: Author authorizes held-out RT diagnostic to explain C versus E/ES despite mean RT overlays. Steps: capture actual scored simulations using original CV parameters/seeds/repetitions for C/E/ES, all mice/folds; reproduce archived choice+RT scores exactly; export observed/predicted conditional RT quantiles and exact score contributions by mouse/fold/coherence/choice/RT bin; aggregate within mouse before group summaries; inspect distribution/score-contribution plots and identify gains/losses without new inferential tests. Sparse cells, smoothing and test-derived bins retained and disclosed. No refitting, pulse work or changes to accepted figures.

- 2026-11-18: Held-out diagnostic completed: all150 scores and exact bin contributions reproduced, conditional quantile absolute-error checks passed, final v2 render inspected. C gains middle bins, alternatives slowest bins; C wins net. Tiny old E component discrepancy recorded rather than altering archived totals. Report ../reports/2026-11-18-control-rt-score-diagnostic.md. No accepted artwork changes/refits/pulse work. Next author review diagnostic and placement.

- 2026-11-18: Author selects held-out RT diagnostic for supplement, with further work pending. Saved byte-identical draft artwork, caption, source tables and provenance plus proposed revision checklist; number deliberately unassigned. Report ../reports/2026-11-18-control-rt-supplement.md. Main figures unchanged; next continue main review and revisit supplement later.

- 2026-11-18: Author asks how to improve shallow psychometric slope. Bounded existing-source assessment confirms raw intermediate-coherence underfit (not just smoothing), descriptive max slope~28% shallower;9/10 mice same deficit direction. Recommendations documented, no refits/simulations run. Report ../reports/2026-11-18-control-psychometric-slope.md. Next if authorized: bounded current-model optimization/sensitivity audit before new sensory mapping.

### Authorized control-C sensitivity and optimization pilot — 2026-11-18
- [x] Map all10 mice over gain×sv×p_guess (3 levels each), with common draws at15 repetitions/input and original bounds/objective. Track choice, conditional-RT, joint scores, intermediate-coherence residuals and RT quantiles.
- [x] Bounded derivative-free restarts on DBM13 (little slope deficit), DBM12 (moderate), PSUIM10 (largest deficit/small sample; updated after benchmark); allow all existing9 free parameters, retain original bounds. Compare original, joint-best and choice-improved starts.
- [x] Independently evaluate original/new solutions using separate simulation seeds and higher repetitions; keep selection draws separate from confirmation draws.
- [x] Assessed conditional CV expansion: not run because selected refits lack a useful consistent independent gain. If useful/reproducible, assess the same restart procedure within original control CV folds using training-only starts/selection; report pilot scope and do not replace manuscript scores before matched comparison.
- [x] Verify arithmetic, parameters/bounds and resume checkpoints; export plots and report. Preserve old fits/artwork/raw inputs, pulse deferred.

Author's “do it” authorizes these bounded analyses/refits; no cluster jobs/installations/pushes. This exploratory optimization pilot is not a new family comparison. Choice residuals are diagnostics, never a modified likelihood objective.

- 2026-11-18: Pilot mouse refinement after benchmark: use DBM13 (little deficit), DBM12 (moderate), PSUIM10 (largest deficit, small sample) instead of PSUIM6. This spans the observed slope discrepancy and bounds restart runtime; all10 mice still receive sensitivity maps. Local restarts capped at200 objective evaluations/start,3 starts/mouse, same9 parameters/bounds. These are exploratory local pilots, not global optimization claims.

- 2026-11-18: Implementation bug found before interpretation: name original for a local restart collided with archived-fit comparison baseline. Sensitivity and optimization outputs unaffected; original independent_evaluation.json files explicitly invalidated, executed source preserved, corrected comparisons in validation_v2. Independent 30-rep selection gains failed first60-rep confirmation. Resolve simulation sensitivity with already selected parameters fixed at3 new100-rep seeds (123456/234567/345678); no new parameter selection on confirmation draws. CV remains conditional on useful reproducible gains.

- 2026-11-18: Authorized sensitivity/local pilot complete;270 profiles,9 capped restarts, corrected baseline comparisons and100-rep independent confirmation. No useful consistent joint gain, so conditional CV expansion not run; no manuscript fit replacements. Report ../reports/2026-11-18-control-C-optimization-pilot.md. Next author review findings; structural mapping or higher-precision optimization remains a separate next decision.

- 2026-11-18: Author accepts B after optimization pilot. Approved artwork copied with source/captions/hashes to figure3B_final_2026-11-18; no parameter/artwork changes. Report ../reports/2026-11-18-figure3B-accepted.md. Next panel C recovery; A final selection and supplement refinement deferred.

- 2026-11-18: Showed existing C/D recovery panels alone at author request; source values unchanged/verified and render inspected. Preview figure3_CD_review_2026-11-18/figure3_CD.png. Next author review C and decide D placement.

- 2026-11-18: Author requests more intuitive D. Rendering-only redesign: replace overlapping dot axes with generator→group-conclusion rows, direct percentages/counts, explicit identical C-vs-E/C-vs-ES outcomes and reused-cohort caveat. Confirm group decision rule from recovery_cohorts.py; source values unchanged, inspect, document. C/A/B unchanged; D placement still undecided.

- 2026-11-18: Intuitive D draft completed: generator→group-preference rows, exact percentages/counts, identical comparison rates verified; source rule/footnote caveats retained. Render inspected, source compiles. Report ../reports/2026-11-18-figure3D-intuitive.md. Next author assess D; placement undecided.

- 2026-11-18: Author chooses cohort-recovery D in text only. Updated Results paragraph, removed obsolete D reference/current caption and made A–C layout explicit. Preserved historical artwork/source/caption. Report ../reports/2026-11-18-cohort-recovery-text-only.md. Next review C matrix; no D figure remains planned.

- 2026-11-18: Author accepts C. Saved standalone unchanged matrix, caption and acceptance/source record in figure3C_final_2026-11-18. Report ../reports/2026-11-18-figure3C-accepted.md. Next combined A–C assembly retaining both A alternatives; pulse work remains deferred.

- 2026-11-18: Author requests commits and next figure. Four focused topic commits7f80063/316c8af/fd2ee9c/0f9ffc5 saved Figure3 work locally; final handoff/next-figure commit follows, no push. Pulse artwork review resumes as Figure4; existing A–D re-exported with5 source tables unchanged, caption matched/render inspected. Reports ../reports/2026-11-18-figure3-commits.md and ../reports/2026-11-18-figure4-review.md. Next A discussion, then B onward.

### Conditional accuracy versus RT for Figure3 — 2026-11-18
Author asks to add notebook bounded-accumulation plot to previous control-model figure. Steps: trace notebook cells5/7/10/12 (pulse_type0, pooled outcome,400ms bins); audit scheduled-control contamination, trial counts and zero-coherence correctness; reproduce original summary separately, derive subject-level conditional accuracy on same14,014 controls as Figure3; retain bin counts/available mice and SEM, verify group arithmetic. Preview new D without replacing A–C; title descriptive, not a standalone bound claim. If useful, compare existing C/E/ES fixed-fit conditional accuracy with same input/readout to assess specificity, no refits. Keep Figure4 correction intact.

- 2026-11-18: Conditional-accuracy candidate D complete: notebook audit, corrected scheduled controls, mouse-balanced means/SEM, fixed-fit C/E/ES comparison, independent arithmetic/coverage checks and inspected renders. All steps complete for this subtask; panel review/assembly pending. Report ../reports/2026-11-18-control-conditional-accuracy.md. No model refits; all prior artwork preserved.

### Exponential overlay for conditional accuracy — 2026-11-18
User authorizes trying descriptive saturation fits. Use the same scheduled-control inputs and original points/SEM; fit trial-level Bernoulli outcomes separately for four nonzero coherences with equal total weight per mouse within coherence. Estimate starting accuracy and monotonic asymptote, anchor time at the 300-ms analysis limit, constrain tau to 0.01–20s for numerical stability and report bound contacts. At zero coherence use a constant. Bootstrap whole mice (200 resamples, fixed seed) for descriptive uncertainty; inspect convergence/boundaries and visual adequacy. Export a new version, source coefficients/curves/diagnostics/caption without replacing existing figures. No hypothesis tests or mechanistic tau interpretation.
- [x] Fit and export exponential/constant overlays with subject bootstrap.
- [x] Independently verify objective/derivatives/counts and inspect rendering/limitations.
- [x] Document findings, update handoff and preview in chat.

- 2026-11-18: Exponential subtask completed, report ../reports/2026-11-18-control-accuracy-exponential.md. Visually inspected main overlay; all fits converged and data counts exactly matched. Weak-coherence bootstrap tau boundary contacts disclosed. Original figures unchanged; author selection pending.

- 2026-11-18: Author approved exponential Figure3D and requested a focused commit. Adopted D, added acceptance record and current caption/Methods pointers. Commit includes only conditional-accuracy/exponential scripts, outputs and related handoff; unrelated Figure4 edits remain in working tree. No new fits or push.

### Combined Figure3 preview — 2026-11-18
User requests current full figure. Assemble accepted A/B/C and approved exponential D from saved artwork, retaining both A alternatives. No analysis, refitting, cropping or changes to plotted values. Save reproducible composition script, PNG chat previews and vector SVG composites in a new directory; inspect layout and record source hashes.

- 2026-11-18: Combined Figure3 preview completed with both A alternatives, accepted B/C and approved D. PNG layout inspected, SVG source vectors retained, hashes recorded. Report ../reports/2026-11-18-figure3-assembled-preview.md. No refits or plotted-value edits; final A choice/typography pending.

### Figure3 story order — 2026-11-18
Author approves working order oldD→oldA→oldB→oldC: newA conditional accuracy, newB model comparison, newC model fits, newD recovery. Update both comparison alternatives in a fresh preview directory and relabel headers only, preserving plotted data and source files. Save the mapping and revised caption order; layout remains provisional, no new fits or commit requested.

- 2026-11-18: Story-order update complete: both previews relabeled A conditional accuracy/B comparison/C fits/D recovery; source hashes unchanged, SVG IDs unique, main raster inspected. Selection mapping and README saved; index/caption order pointers updated. Layout remains provisional; manuscript-wide cross-reference harmonization deferred until final layout.

- 2026-11-18: User requests all Figure3 work committed. Verified both assemblies against source hashes, PNG dimensions and SVG structure; saved reordered captions and selection mapping. Stage Figure3-only code/artwork/docs; preserve unrelated Figure4 edits. Both comparison alternatives and provisional layout status retained.
