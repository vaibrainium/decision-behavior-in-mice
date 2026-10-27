# Paper configuration

Filled at S0 (intake) by the orchestrator with the human. Every later agent reads this file.
Unknown facts remain explicitly marked as missing; never guess a value.

This is the **accumulation-first variant** of the mouse pulse paper, started 2026-10-26 at the author's request so that
it can be compared later with the pulse-generalization version in `/src/dissemination/paper/np/` (left untouched).
Both versions draw on the same analyses; only the framing, emphasis and figure plan differ.

## Paper
- Working title: Mice accumulate continuous motion evidence, but motion pulses cannot resolve its temporal weighting (placeholder; settled at G1)
- Article type: Research Article
- Target venue: eLife (provisional, carried over from the first version; to be confirmed at G0 because the novelty argument changes)
- Backup venues: [MISSING: authors to choose]
- Venue rules checked on (date) and source URL: 2026-10-24 (first version); https://elife-rp.msubmit.net/html/elife-rp_author_instructions.html and https://elifesciences.org/about/submit-your-research. Recheck before S8.
- Word / figure / reference limits: eLife suggests no more than 5,000 main-text words excluding Methods, References and Figure legends; no display-item limit. Abstract normally 150–200 words; title suggested up to 120 characters. No fixed reference limit identified.
- Required front matter: title, 150–200-word abstract, 15–30-word third-person impact statement, funding and funder role, author contributions, competing interests, data and software availability; acknowledgments and references.
- Section order for this venue: Introduction; Results; Discussion; Materials and Methods; Acknowledgments; References; figures and legends; tables.
- Reporting checklist: ARRIVE 2.0 and eLife MDAR checklist.

## Science
- Species / preparation: mice, head-fixed behavior; sex/age/strain, training and ethics identifiers remain [MISSING: author records]
- Task / paradigm: reaction-time random-dot motion direction discrimination on two rigs (rig is a covariate only; no site-level interpretation), with control trials and brief signed motion-pulse trials
- Techniques: behavioral psychophysics; stimulus replay and motion-energy filtering; drift-diffusion and rapid-forgetting (extrema-like) modeling; cross-validated model selection; model recovery; predictive checks and simulation power/calibration
- Units of analysis: mice for group inference (10 total); mouse-sessions, cells and trials only for labeled descriptive or within-mouse estimates
- Pre-registration or analysis plan: confirmatory primacy plan locked before outcome inspection (commit aeb0a22) and amended in a versioned audit trail; the timing test was not run after predictive gates failed. Pulse diagnostics are exploratory. Not externally preregistered.

## Intended story (author, 2026-10-26; to be formalized at S1)
1. Mice can learn/perform the reaction-time random-dot task (scope of "learn" pending: see G0 question 2).
2. Control trials favor evidence accumulation over the tested extrema-like (rapid-forgetting) model, and identify which model variant is needed (strict L0U0V1Z0G1: drift variability, fast guesses, free guess bias; leak and urgency not needed).
3. Primacy versus recency could not be determined from the pulses: pulses shift choices, but the control-fitted model does not predict their time course, the predictive gates failed and calibration showed no sensitivity.

## Inputs the human supplies (paths)
Agents only report results that come from these files. Paths relative to `/src/dissemination/paper/` unless absolute.
- Number ledger: `np/ledger/numbers.csv`, copied from the first version (N001–N109, same provenance) plus N110–N117 added for this framing (sources in each row).
- Analysis outputs / statistics: `/src/dissemination/reports/mouse-ddm-analysis-log.md` (sections 5.6–5.13); `/src/.agents/reports/2026-10-23-control-only-selection.md`; `/src/.agents/reports/2026-10-22-arriving-results.md`; `/src/.agents/reports/2026-10-23-amendment-6-result.md`; `/src/.agents/reports/2026-10-22-primacy-power.md`; `/src/.agents/reports/2026-10-25-fluctuation-kernel-power.md`; `/src/.agents/reports/2026-10-23-pulse-*.md`; `parameters_common_model_2026-10-23.csv`; `pulse_followup_results_2026-10-23.md`. Evidence map: `/src/dissemination/paper/np/input_inventory.md`.
- Figures: selected main figures and S6 indexed in `figures/figure_build_2026-10-26.md`; `figures/fig1_behaviour_2026-10-20.*`; `figures/fig2_motion_energy_2026-10-20.*`; `/src/dissemination/figures/ddm_fit_quality_L0U0V1Z0G1_fits_guess_fast_only.png`; `figures/pulse_followup/20261023T191030Z_fa8de8b/` (excluding `superseded_diagnostics_attempt1/`). Figure plan for this version is set at S1.
- Methods notes: `/src/dissemination/reports/motion-energy-methods.md`; `/src/dissemination/reports/primacy-analysis-plan.md`; [MISSING: animal/training protocol, training-stage criteria, ethics/IACUC details].
- Prior drafts: the first version's approved sections in `/src/dissemination/paper/np/drafts/` and `manuscript.md` (reusable material, not approved for this version), and its S6 panel roadmap `/src/dissemination/paper/np/panel/roadmap.md` (author-supplied facts it lists apply to both versions).
- Literature: 44 verified sources copied into `np/ledger/sources.csv` from the first version (verified 2026-10-24/25); prior search logs, notes and shards in `np/lit/prior_project/`. S2 re-runs only the gap/counter search the new framing needs.
- Zotero library or folder: [MISSING: none identified]

## People and policy
- Authors (order, roles) and corresponding author: [MISSING: authors, order, roles, affiliations and corresponding author]
- Who approves gates: V. Thakur through this project chat
- Confidentiality: no unpublished text, data or figures may go to external AI services without explicit author approval. Public scholarly APIs may be used for citation verification.
- AI-use disclosure: transparent drafting-assistance disclosure; check exact eLife policy before submission.

## Run settings
- Mode: full  <!-- full | lit-only | section:<name> | review-only | revise -->
- Max review rounds per section: 2
- Minimum verified sources for the literature review: 25
- Citation style / reference manager: eLife author-date style; Markdown/Pandoc source of truth.
- Spelling: American English throughout manuscript-facing text.
- Exploratory input (2026-10-26): amendment 8 fluctuation-kernel result, `/src/.agents/reports/2026-10-26-fluctuation-kernel-observed.md` (verdict: neither model fits; not supporting evidence).
