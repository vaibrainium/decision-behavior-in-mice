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

- 2026-11-18: Author requests Figure4A remove control and fit psychometrics for left/right pulses only. Retain observed group means/SEM, exact author logit_4 helper with equal-coherence fit to equal-mouse means (as Fig1), fit each direction separately and restrict dense curves to its observed coherence range. Export points/coefs/curves, verify source identities and B–D untouched; inspect fresh full-figure revision. No pulse decision-model fitting or new inference.

- 2026-11-18: Figure4A revision completed as v2: control omitted, left/right group points/SEM and exact author logit_4 curves, no coherence extrapolation. All original source tables equal, B–D/caption unchanged; curves verified and render inspected. Report ../reports/2026-11-18-figure4A-pulse-psychometrics.md. Next author assess A.

- 2026-11-18: Author requests full-range pulse fit lines. Completed v3 with --extend-pulse-curves; exact parameters and all data/B–D unchanged, curves verified across−100/+100 and render inspected. Caption/Methods disclose extrapolation. Report ../reports/2026-11-18-figure4A-pulse-psychometrics.md updated.

### Figure4 paired pulse psychometric parameters — 2026-11-18
Author requests an additional paired α/β panel to assess pulse use. Clarification requested on labels: provisional α=author logit_4 mean (horizontal dynamic-range midpoint), β=var (logistic slope coefficient), with width alternative offered. Independent work can fit native mean/var without this label decision. Steps: audit per-mouse direction/coherence counts; fit exact4-param helper separately per mouse/direction using trial-count WLS as individual Fig1; inspect boundary/covariance/fit support issues; export paired parameter values and differences, exploratory two-sided paired tests with Holm across2 contrasts only if interpretable; plot connected subject pairs in an added panel, retaining A and existing temporal panels. Do not interpret β null as no pulse use or α midpoint as exactly P(right)=.5 with asymmetric asymptotes. Original decision-model fits unaffected.

- 2026-11-18: Added paired B using same individual4-param form as A/author helper. Free fits expose instability; checked shared-control asymptotes as separate sensitivity, still midpoint-boundary issue. Kept all mice/original fits, explicit α=midpoint β=coefficient assumption after optional clarification. Exact paired sign-flip+Holm gives pα=.0703,pβ=.7031; exploratory, not definitive pulse-use proof. Full/focused renders inspected, all A and prior temporal sources equal, label B–D→C–E only. Report ../reports/2026-11-18-figure4-paired-psychometrics.md. Next author assess new B and fit adequacy.

- 2026-11-18: Author challenges pairedα significance. Audit before interpretation: independently reproduce raw/adjusted tests; audit per-mouse fits with multiple starting points under exactly same4-param equation, trial weights and bounds, selecting only by WLS objective; compare coefficient stability and coherence support, no animal exclusions or p-driven fit selection. Preserve v4 and do not change correction family post hoc. User has now confirmed α=midpoint β=coefficient. Document whether arithmetic, optimization or identifiability explains result; do not force significance.

- 2026-11-18: Audit found actual missed WLS solutions in2 single-start pulse curves. Same equation, weights, bounds, all10 mice,19 starts/curve selected by objective: corrected Holmαp=.01171875, βp=.13671875. Updated v5 paired/full figure; A and C–E unchanged. v4 paired results explicitly superseded. Numericalnear-minimumα inference stable in500 checks, no param-uncertainty claim. Report ../reports/2026-11-18-paired-psychometric-optimization-audit.md. User α/β definition confirmed. Next author review corrected B.

- 2026-11-18: Author adopts corrected paired B/result. v5 marked current with acceptance.json and Results paragraph read directly from source tests; caption/Methods aligned, fit caveats retained. Report ../reports/2026-11-18-figure4-paired-update.md. Next temporal C review, then D/E. No new calculations or commits.

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

- 2026-11-18: User returns to Figure4 after committing Figure3. Restored latest v5 preview and caption; resume C temporal influence, then D/E. A and corrected B retained; no numerical or artwork edits.

### Shared psychometric helper multistart — 2026-11-18
User authorizes updating the helper after the individual-fit optimization audit. Preserve logistic equations, bounds, weighted least-squares objective, sklearn/public coefficient API and covariance. Add deterministic multistart default with original single-start candidate retained, select by residual error among finite successful fits, allow multistart=False for historical behavior, and export optimization/boundary diagnostics. Validate input/counts and numerical stability without changing the scientific model. Regression checks cover two affected pulse curves, all three logistic forms/custom bounds, exact legacy opt-out, weighted selection, convergence failure handling and sklearn cloning. Do not rerun preprocessing, change trial inclusion or regenerate accepted figures.
- [x] Update helper and meaningful regression tests.
- [x] Run checks including real affected fits; save fresh verification output.
- [x] Document API, limitations and provenance; update handoff.

- 2026-11-18: Shared-helper subtask complete; report ../reports/2026-11-18-psychometric-helper-multistart.md. Five regression tests pass and all20 pulse curves no worse than legacy; exact opt-out verified. Retained original logistic numerical evaluation after expit changed weakly identified coefficients in legacy mode. Saved verification/source hashes, no existing outputs replaced, no preprocessing/figure reruns or commit.

- 2026-11-18: User requests committing the shared-helper update. Verified persisted source/test hashes match tested files; focused commit includes helper, regression tests, verification exports and related handoff only. No new fits or existing figure/data changes.

### Pulse-time psychometric parameters — 2026-11-18
User requests timing × physical-direction α/β plots like notebook examples. Audit notebook cell5/15–17: α is additive evidence offset (opposite current midpoint), plots are pulse-minus-control coefficients, linear stage dependence imposed, and SE formula omits shared-time term/covariances and adds SEs. New exploratory plots retain current α=midpoint and β=slope coefficient; plot within-mouse pulse-minus-control changes, summarize mice with SEM, no significance claims. Source audited trial table, scheduled signs/times, symmetric cells, modeled responses after actual/virtual offset and ≥0.1s after onset, as Figure4 except restoring late stratum for this requested exploratory comparison. Primary all-three-times view uses same6 UW mice; companion early/middle uses all10 mice. Audit timing metadata; do not reuse inaccurate notebook millisecond windows. Fit independently by time/direction with updated helper, retain failed/boundary diagnostics and observed support; inspect whether free4-parameter fits remain interpretable after splitting. Shared-control-asymptote sensitivity only if identification issues arise; clearly separate assumptions. Existing Figure4 unchanged.
- [x] Audit selection/timing and notebook definitions; export subject/coherence counts.
- [x] Fit timing-specific curves, derive paired control-relative estimates and diagnostics.
- [x] Verify arithmetic/selection, inspect figures and document scientific limits.

- 2026-11-18: Timing preview subtask complete; report ../reports/2026-11-18-pulse-psychometric-timing.md. Independent fits unstable; fixed-asymptote sensitivity changes trends. Author clarifies α absolute: v2 applies without refitting; β remains control-relative. Summaries/selection independently checked, renders inspected, Figure4 unchanged.

- 2026-11-18: Author selects all10-mouse early/middle preview as primary; matched6-mouse three-time view retained separately. Existing v2 artifacts reused; all10 contribute to both directions/times and α/Δβ means/SEM independently rechecked. Added selection.json and primary_caption.md, updated pointers, no refits or Figure4 integration.

### Audit misleading early-pulse coefficient averages — 2026-11-18
Author challenges similar negative early α for both physical directions. Trace coding to physical pulse coherence and existing Figure4 source cells; compare observed equal-mouse choice curves with per-mouse midpoint estimates. Quantify boundary/weak-fit influence, without excluding mice. If confirmed, withdraw average-coefficient plot as a population psychometric summary and fit the same4-parameter equation directly to equal-mouse choice proportions (consistent Figure4A), independently by time/direction; label changed estimand explicitly. Preview observed curves before timing parameters, retain all mice. Bootstrap whole mice for population-curve coefficients if identifiable; no imposed timing trend or p-driven fit selection. Preserve prior outputs and existing Figure4. Document cause and superseded status.
- 2026-11-18: Audit confirms physical pulse coding, observed directional separation, and a −100-bound early-left individual α influencing the average. Population free-asymptote fits also expose α versus P=.5 criterion mismatch. Add explicitly labeled joint per-time population-curve sensitivity with asymptotes shared across control/left/right, free midpoint/slope for each curve, no forced direction or time trend. Use same equal-mouse observed proportions as Figure4A; whole-mouse bootstrap keeps contrast covariance. Compare observed curves/free4 fits/shared fits, report any remaining instability and changed estimand. Do not claim a corrected individual-average statistic or alter existing Figure4.

- 2026-11-18: Timing-summary audit complete; report ../reports/2026-11-18-pulse-timing-summary-audit.md. Verified coding, observed directional separation, −100-bound alpha influence and free-asymptote midpoint ambiguity. Withdrew prior population interpretation; saved data-first display and changed-estimand joint shared-asymptote sensitivity with120 whole-mouse resamples. Independent objectives/means checked, renders inspected; no exclusions or existing Figure4 changes.

### Show per-mouse timing fit and boundary example — 2026-11-18
Author requests the actual individual estimates and−100 mouse fit. Clarify the original plot did use per-mouse fitting then mean/SEM; population-curve sensitivity is a distinct estimand, not a replacement for subject-level inference. Plot all10 early left/right α pairs and DBM12 early-left observed fractions/counts with its saved fitted curve, marking α lower bound and observed coherence support. No refitting, exclusions, population substitution or new tests. Verify against saved cells/coefficients; document/preview.

- 2026-11-18: Individual-fit display complete. Showed all10 early pairs and DBM12 early-left105 trial observations/boundary curve, saved squared residual reconstructed and render inspected. No refit/exclusions; clarified original per-mouse mean/SEM versus separate population sensitivity. Report ../reports/2026-11-18-pulse-timing-summary-audit.md updated.

### Exact notebook population-fit reproduction — 2026-11-18
Author reiterates screenshot is population fit; prior alternate analyses do not reproduce its model. Reproduce notebook cell5 fitting function on current valid_data without edits, reconstruct screenshot curves from saved cell14 coefficient output, and compare current fit to saved coefficients. Map additive-offset alpha versus midpoint and baseline-term omission exactly. Then hold equation/weights fixed while changing selection to scheduled labels and current Figure4 early/middle eligibility, isolating data/model/parameter-transform differences. Preserve full covariance for correct contrast SE; no new significance claims. Deliver direct comparison and acknowledge implementation mismatch rather than attributing original discrepancy solely to one mouse. No raw/notebook edits or existing-figure replacements.

- 2026-11-18: Exact-reproduction subtask complete; report ../reports/2026-11-18-pulse-time-exact-reproduction.md. Same25,508-row data, original equation/start/bounds/weights reproduce all10 saved coefficients and screenshot alpha means. Independently checked offset/midpoint/baseline and full covariance transforms; same-model current-selection comparison also exported. Corrected assistant specification mismatch; individual-bound issue is separate. Render inspected; no existing figures changed.

### Per-mouse exact joint pulse-time model — 2026-11-18
User requests the reproduced notebook joint population model fitted separately per mouse. Primary uses original valid_data rows/response-coded labels for exact method comparability; separately labeled sensitivity uses current scheduled-label/post-offset eligibility. Each mouse jointly fits all its observed pulse stages plus controls, using notebook equation,10 coefficient bounds, pooled coherence-cell trial-count WLS, and shared asymptotes across conditions. Preserve original additive-offset α convention; export full α, original plotted baseline-omitted α, native midpoint, and β changes separately. Retain native single-start fits as diagnostic; multistart under same objective/bounds selected solely by WLS, with no animal or direction-based exclusions. Record boundary contacts, covariance/conditioning, actual-stage slope signs, fit adequacy and native-versus-best stability. Early/middle summaries use10 mice; late only6, with same6 three-time companion.
Exploratory group tests fixed before fitting: exact two-sided subject-level sign-flip tests of right-minus-left α and β at each of3 stages, Holm across6 contrasts. Direction×time changes middle-minus-early for α and β are a separate2-test Holm family, all10 mice. Report paired mean effects, unadjusted95% t intervals and dz plus corrected p values; tests condition on fitted coefficients and do not propagate individual uncertainty. Do not infer no effect from a null, and do not treat linear model lines as independent proof of timing trends. Check unchanged model/aggregation on pooled reproduction and all selected objectives, render per-mouse and group figures; report primary/sensitivity, no existing-figure replacement.
- [x] Fit original joint model per mouse and record fit diagnostics/native comparisons.
- [x] Derive subject-level stage effects, prespecified exploratory contrasts and figures.
- [x] Verify mapping/arithmetic/tests, assess stability, document and preview.

- 2026-11-18: Per-mouse joint subtask complete; report ../reports/2026-11-18-pulse-time-per-mouse-joint.md. Original-mask α early/middle survive Holm6, timing interaction Holm2; β/late inconclusive. Scheduled eligibility sensitivity not corrected-significant, with unstable DBM12. All fits retained,580 attempts converged, independent objective/transform/exact-test/Holm checks passed and renders inspected. No existing outputs changed; original significance not used to pick final mask.

### Trial-selection accounting — 2026-11-18
User requests exact trial differences between notebook and current joint-model sensitivity. Join original valid_data IDs to audited trial table and current eligible IDs; reconstruct newer mask in explicit sequential order, report mutually exclusive removal counts plus independent rule failures, original versus scheduled label changes, and per-mouse counts. Identify null/no-change pulse removal and virtual-control timing gates separately; do not describe bundled sensitivity as only pulse-label correction. No fits, data changes or final mask choice.

- 2026-11-18: Trial-accounting subtask complete; report ../reports/2026-11-18-pulse-timing-trial-accounting.md. Reconstructed retained IDs exactly and no retained labels differ. Detailed3,783 exclusions and virtual-control gates exported. Corrected earlier interpretation of sensitivity as relabeling; no refits or final mask decision.

### Restricted-trial joint-model preview — 2026-11-18
User asks to see the joint per-mouse model on the restricted21,725-trial set. Render saved scheduled_eligible_sensitivity coefficients in the same full additive-alpha/delta-beta convention,10 mice early/middle, matching6-mouse all-time companion. Verify summary arithmetic and copy existing corrected tests; no refits or new exclusions. Save a fresh display version and clarify all trials derive from author's filtered data.

- 2026-11-18: Restricted-trial preview complete from saved per-mouse joint fits. Group means/SEM rechecked, tests copied unchanged, early/middle10-mouse and same6 all-time displays saved and main render inspected. Existing per-mouse report updated; no fitting, exclusion or statistical changes.

### Joint pulse-time model with categorical mouse fixed offsets — 2026-11-18
User requests a joint regression with mouse ID. Preserve notebook probability equation and additive-offset sign; replace global alpha1 with10 categorical mouse baseline offsets, share alpha2/alpha3/alpha4, beta1–4 and asymptotes. Primary early/middle restricted dataset19,313 trials (late excluded for common10-mouse support); original-label early/middle/control sensitivity23,684 trials. Explain that a shared pulse effect differs from averaging individual effects and weights trials through objective. Primary objective remains notebook trial-count WLS on mouse/condition/coherence cells; separately labeled binomial-deviance sensitivity keeps probability equation. Use multistart, same coefficient bounds, inspect adequacy/gradient/boundaries/actual slopes. Mouse-cluster sandwich covariance with CR1 finite correction and t9/F(2,9) reference;10 clusters means approximate inference. Leave-one-mouse cluster jackknife covariance/influence for WLS as sensitivity, not permanent exclusions. Main hypotheses fixed before fits: alpha directional block(alpha2,alpha4)=0 and beta directional block(beta2,beta4)=0, Holm across2 omnibus tests. Early/middle directional alpha contrasts are exploratory follow-ups, Holm across2. No significance-based model/objective/mask selection; retain all results and uncertainty-method discrepancies. Export curves/coefficients/covariances/tests and verify independently. Do not silently substitute ordinary logistic regression or change lapse structure.
- [x] Fit mouse-offset joint WLS and binomial sensitivity on both datasets.
- [x] Cluster inference, jackknife checks and plots; inspect adequacy/identification.
- [x] Verify derivatives/objectives/tests, report and preview with limitations.
- 2026-11-18: Initial Gauss–Newton/Fisher sandwich checked against statsmodels linearization. Full nonlinear score-Hessian check yields same scientific conclusion; use full observed score curvature as final M-estimator sandwich, retaining initial approximation separately. Restricted WLS Holm alpha≈3.20e-5,beta≈.100. This changes covariance postprocessing only, not model/data/fit or test family. Save fresh inference subdirectory; compare finite-difference step stability and jackknife.

- 2026-11-18: Mouse-ID regression subtask complete; report ../reports/2026-11-18-pulse-time-mouse-fixed-effects.md. Final observed score-Hessian covariance;6 tests and numerical/linearization/Holm checks pass. Restricted alpha direction effect across sensitivities, beta/timing decline inconclusive. Shared-effect/unequal-weight distinction explicit; figures inspected, no existing-figure replacement or commit.

### Continuous actual-onset slope as primary pulse-influence test — 2026-11-18
User approves actual pulse-onset time and one primary slope of directional influence. Fit early/middle10-mouse joint nonlinear model, preserving notebook probability equation and categorical mouse baselines. Use x=(recorded_onset_s−.15)/.2 on pulse trials only; controls x=0,P=0,d=0. A=u_m+aP*P+aT*P*x+d*(w0+wT*x), B=b0+bP*P+bT*P*x+d*(v0+vT*x); shared asymptotes. Presence intercepts are explicit nuisance additions so centering time does not constrain common pulse bias/slope at time0; no sign/time trend forced. wT/.2 is directional-influence time slope per second (half right-minus-left offset), distinct from common aT. Primary restricted19,313 trials, original23,684 sensitivity; WLS primary and binomial sensitivity,21 parameters, same scaled coefficient bounds, multistart. One exploratory primary two-sided cluster-t9 test wT=0, report slope/CI per100ms, no stage-wise correction; all other coefficient tests descriptive. Full observed score-Hessian cluster CR1 covariance, WLS cluster jackknife check. Continuous recorded onset is not a continuous uniform timing experiment; six UW mice have2 exact earlier onsets, UCLA has timing spread. Export actual-time support, fit adequacy, derivatives/stability, and original-model sensitivity. Existing figures untouched.
- [x] Prepare actual onset data and fit continuous-time models.
- [x] Primary slope inference/jackknife and timing-curve plots.
- [x] Independent checks, interpretation, report and handoff.

- 2026-11-18: Continuous-time subtask complete; reports ../reports/2026-11-18-pulse-time-continuous.md and ../reports/2026-11-18-cluster-frequency-correction.md. Primary−2.93/100ms,p.0493; jackknife p.0903.40 starts, common-pulse nuisance specification and ordinal comparison,13 tests, gradient/curvature/unit/stability checks complete. Fixed aggregation-dependent finite correction in covariance and versioned continuous/earlier ordinal inference without refitting. Plots inspected, existing Figure4 unchanged; no firm primacy claim.

### Ordinal1/2/3 time slope with same pulse-influence model — 2026-11-18
User requests same slope analysis using stage1/2/3 instead of actual onset values. Keep current21-parameter structure for10 mice (or17 for6), common pulse-presence/time nuisance terms and notebook probability equation. x=stage−2 for pulses; controls P=d=x=0, so directional w(stage)=w0+wT*(stage−2). wT is per-stage effect (not per100ms). Primary exploratory display: all available restricted21,725 trials,10 mouse baselines with late support6. Companion: matched6 acrossall3 times; retain same10 early/middle-only case to isolate timing coding from late inclusion. WLS primary, binomial sensitivity, corrected underlying-trial CR1/t(G−1), cluster jackknife sensitivity. No exclusions based on fit or significance; one slope test per stated comparison, no claim of independent confirmatory analyses. Late interpretation conditional on common-effect assumptions and6-cluster matched inference approximate. Save new outputs, verify stage mapping/objectives/gradients/center invariance and reproduce prior21-parameter two-stage diagnostic p≈.0532. Existing figures unchanged.
- [x] Fit ordinal stage-slope comparisons with same model and uncertainty methods.
- [x] Verify stage coding/units, contrast tests and prior early/middle result.
- [x] Preview three-stage and matched-cohort comparisons; document/report.

- 2026-11-18: Ordinal subtask complete; report ../reports/2026-11-18-pulse-time-ordinal.md. Same21/17-parameter model/time-only coding change; all-available10,matched6,and early/middle10 compared.60 starts success, coding/objective/test/prior-result checks complete; render inspected. All-available slope−5.40,p.0226,matched6−1.72,p.4615; existing Figure4 unchanged.

- 2026-11-18: Author prefers left all-available ordinal plot. Recorded preferred timing-panel candidate, caption and selection metadata; keep matched6 sensitivity and late-six support explicit. No fitting/statistics changes; full Figure4 placement pending.

### Show direction×ordinal-time interaction — 2026-11-18
Author requests direction interaction in selected all-available model. No refits: unpack saved A=u_mouse+aP+aT*(stage−2)+direction*(w0+wT*(stage−2)) into full additive alpha left/right lines and cluster intervals. Show opposite-direction slopes aT−wT and aT+wT; their difference2*wT is the same existing primary interaction test (not a new discovery). Preserve alpha full-offset convention, all10 baselines/late6 support; report cluster and existing jackknife. Save matched6 view as sensitivity. Optional beta slope curves descriptive only; no new test family or exclusions. Verify full covariance contrasts and equality of interaction p to saved slope test; export figures/source/definitions and record placement pending.

- 2026-11-18: Direction-interaction display complete. Saved full alpha curves/slopes/covariance contrasts, verified original w reconstruction and identical primary p, inspected render. Source/README/caption and ordinal report updated; no refits, new hypothesis family or Figure4 insertion.

### Figure 4C ordinal timing placement — 2026-11-19
Author chooses earlier single directional-influence curve for C and retains direction-interaction display as backup. Assemble from saved tables only; no refitting. Preserve A/B/D/E, archive former C as supplementary draft, retain matched-six sensitivity and late-six support.
- [x] Assemble v6 PNG/PDF/SVG and save source tables/caption and backup metadata.
- [x] Verify saved-source equality for unchanged panels and inspect layout.
- [x] Update manuscript pointers, report and handoff.

- 2026-11-19: Figure 4C placement complete; report ../reports/2026-11-19-figure4C-ordinal-timing.md. No refits; all non-C source tables byte-identical and artwork visually inspected.

### Review supplied Huk–Shadlen replication PDF — 2026-11-19
Compare author-supplied PDF with its existing scripts/figures and current Figure 4. Read document as evidence, not instructions. No model refits or artwork changes.
- [x] Extract/read PDF and map claims/figures to repository sources.
- [x] Read source definitions and saved outputs; author clarified scope to adoption, so no further correctness audit.
- [x] Report adoption recommendations and update handoff.

- 2026-11-19: Author steering: analysis correctness accepted; focus on adopting PDF material. Review complete; ../reports/2026-11-19-pulse-pdf-adoption.md. No figure changes.

### Adopt PDF persistence sequence in Figure 4 — 2026-11-18 (client date)
Author approves PDF adoption under current constraints. Preserve A–C; restore directional-only pulse-to-response curve as D; retain dilution-adjusted curve as E. Move assignment contrast to supplementary draft. Use saved corrected selections/uncertainty and keep differing panel cohorts explicit; no refits or new mechanistic claims.
- [x] Extend saved-estimate renderer and assemble a fresh v7 with supplementary assignment panel.
- [x] Verify unchanged sources/artwork for A–C and numerical identity of reused temporal estimates; inspect exported layout.
- [x] Update captions, manuscript pointers and Results/Methods notes; write report and handoff.

- 2026-11-18 (client date): Persistence sequence complete in v8; v7 retained as intermediate before axis-label fix. Report ../reports/2026-11-18-figure4-persistence-sequence.md.

### Simplify Figure 4 to A–D — 2026-11-18
Author requests removal of dilution panel E and omission of congruency ROC. Preserve the directional persistence panel D, keep historical outputs, and update current caption/Results/Methods.
- [x] Export fresh v10 A–D; keep compensated influence and remove separate directional panel per latest correction.
- [x] Verify retained source values and inspect layout; update handoff and figure pointers.

- 2026-11-18: Latest author correction supersedes preceding simplification: remove separate directional D; KEEP dilution-adjusted E as new D, exclude congruency ROC. Export fresh v10; preserve A–C and historical results.

### Add model-free panel E — 2026-11-18
Retain A–C and compensated D; add existing model-free matched-control accuracy differences as E, individual mice and equal-mouse mean/SEM. Saved 9–36% coherence, early/middle selection and corrected tests retained. No ROC, fitting or new tests.
- [x] Render new panel and verify aggregation/source equality.
- [x] Inspect layout and update caption, review pointers and handoff.

### Separate exponential draft — 2026-11-18
- [x] Record author correction: model-free E was not intended; restore v10 as current Figure 4.
- [x] Preserve prior exponential artwork as reference in a separate draft; defer exact target and placement, no new fits.
- [x] Update manuscript pointers and handoff. Report: ../reports/2026-11-18-exponential-separate-draft.md.

### Standalone exponential pulse-influence preview — 2026-11-18
Assumption communicated: target is compensated Figure 4D; optional clarification pending. Keep Figure4 unchanged. Reuse saved mouse-bootstrap curves; fit descriptive zero-asymptote exponential to all six displayed bins, retain negative estimates, use observed physical mean pulse-to-response times (no ordinal bin coordinates). No decision-model refits or intrinsic forgetting claim.
- [x] Verify source alignment and physical time coordinates; render separate preview with explicit equation and uncertainty.
- [x] Check resample fits/profile identification; document limits and preserve source provenance.

- 2026-11-18: Separate exponential preview complete, report ../reports/2026-11-18-pulse-exponential-preview.md. Author specifies PDF; page-9 compensated readout used. Figure4 unchanged.

### Overlay saved exponential on Figure 4 compensated panel — 2026-11-18
User calls compensated panel E (historical name); current four-panel layout names it D. Overlay saved exponential and bootstrap band, use physical mean pulse-to-response coordinates, preserve A–C and data/intervals; no refits.
- [x] Export new revision and verify source equality and axis coordinates.
- [x] Inspect artwork and update caption/current pointers/handoff.

### Compact compensated panel — 2026-11-18
- [x] Reduce D width and connect observed points; preserve all data and fits.
- [x] Inspect fresh preview and update current pointers/handoff.

### Finalize Figure 4 and commit pending work — 2026-11-18
Author accepts compact connected v13 and requests all pending changes in logical commits. Preserve historical outputs and raw inputs, no push or package installation.
- [x] Verify regressions, paired-fit audit, source hashes and final artwork.
- [x] Commit psychometric and trial-selection work separately from joint timing regression and PDF/exponential work.
- [x] Create canonical final Figure 4, reconcile caption and current manuscript references, and commit assembly and handoff.
- [x] Verify final commit history and clean working tree.

- 2026-11-18: Latest v13 confirmed by author; exact artwork finalized in figure4_final_2026-11-18/. Regression and independent paired audit pass; reproduced PNG pixel-identical. Scientific work committed in separate chunks; final clean-tree check recorded in finalization report.

### Figure 5 scope: pulse-only fitted accumulation models — 2026-11-18
Author explicitly restricts Figure5 model introduction/comparison to pulse-only fitted candidates. Joint/control-only comparison is out of scope for this figure unless later requested. Existing rescored table has distinct held-out and BIC winners; do not label a single universal winner. No fits rerun.
- [x] Read pulse-only candidate scores and confirm scoring-population restriction.
- [x] Review candidate definitions and prepare model-introduction panel for author review.

- 2026-11-18: Figure5 opening preview A model components/B pulse-only scores exported in figure5_opening_2026-11-18_v2; all22 source scores verified. Layout and candidate breadth await author review; no fitting.

### Tentative Figure 6 pulse-only psychometric/chronometric fits — 2026-11-18
Figure5 deferred for later discussion. Use existing full-pulse-fit predictions for predictive and BIC winners on pulse trials only. Show early/middle/late and physical left/right direction; equal-mouse observations/SEM with matched model summaries. No controls borrowed to anchor psychometrics, no decision-model refits or new simulations. Descriptive four-parameter display curves may be fitted to saved summaries; source/eligibility differences disclosed.
- [x] Inspect browser summaries and verify full-fit prediction provenance and matched mouse/coherence support.
- [x] Render tentative comparison with psychometric and mean-RT views and export source tables.
- [x] Verify aggregations, inspect artwork and document scope/limitations for author choice.

- 2026-11-18: Tentative Figure6 complete in figure6_pulse_fits_2026-11-18/. Both winners overlaid and individual previews exported; matched equal-mouse support/SEM verified. Figure5 deferred; no decision fits/simulations. Report ../reports/2026-11-18-figure6-pulse-fits.md.

### Pulse-only held-out bits per trial — 2026-11-18
Compute same metric as Figure3 for all22 pulse-only candidates: -heldout_NLL/(n_heldout ln2) within mouse, then equal-mouse mean. Keep pooled trial-weighted score separately, verify matched trial counts, no fits or null-baseline claim.
- [x] Export per-mouse and group scores, verify formula/ranking and document result.

### Pulse-only pulse-effect magnitude — 2026-11-18
- [x] Compare all22 saved pulse-only0.3–1.2s effects and verify shared observed reference; normalizedUGM/no sv largest, power+leak closest cohort mean. Report ../reports/2026-11-18-pulse-only-effect-magnitude.md. No fits/tests.

### Pulse-only model predictions of Figure4C onset-stage influence — 2026-11-18
User requests which model reproduces primacy. Existing response-time caches exclude late, so generate bounded fixed-parameter predictions on the same pre-response-selection schedules, not refit DDM parameters. All22 pulse-only candidates; start with30 reps/seed, use two independent seeds to assess simulation stability. Reproduce observed21725/10-mouse Figure4C cells/slope before ranking. Apply simulated response/offset/onset eligibility to outcomes; controls with virtual schedules included as predicted outcomes, not fitting data. Fit same21-parameter ordinal descriptive regression/WLS to model-generated choices, with per-cell simulation counts scaled by reps so simulation repetitions are not additional biological trials. Compare stage curve RMSE and slope error, not slope alone; report conditional predictions/identification and six-late-mouse caveat. Do not infer biological support from simulation p values.
- [x] Verify preselection/observed estimator and pilot fixed-parameter prediction.
- [x] Generate all22 candidates and apply identical regression; check optimizers and seed stability.
- [x] Compare slope/amplitude/curve discrepancy, inspect render, report and handoff.

- 2026-11-18: Model-primacy comparison complete. NormalizedUGM/no sv closest all-available but far shallower than data; matched6 ranking changes. Exact selection/cells verified;440 simulations/88 readout fits/880 successful starts. Report ../reports/2026-11-18-pulse-model-primacy.md.

### Review of the onset discrepancy — 2026-11-19
- [x] Audit the fitted objective, time weights, cohort schedules, simulations and previous tests.
- [x] Check whether the early deficit survives a comparison in observed choice probabilities within mouse and task implementation.
- [x] Synthesize primary research on stimulus encoding, commitment, attention and choice state. Report competing explanations, discriminating analyses and limitations.

- 2026-11-19. Onset-discrepancy review complete. Direct matched probability contrasts, reweighted ordinal fits, session checks, trial-sized simulation ranges and pulse-locked response timing are in the review. See ../reports/2026-11-19-pulse-onset-diagnosis.md.
