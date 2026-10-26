# Paper configuration

Filled at S0 (intake) by the orchestrator with the human. Every later agent reads this file.
Unknown facts remain explicitly marked as missing; never guess a value.

## Paper
- Working title: Brief motion pulses constrain models of evidence accumulation in mice
- Article type: Research Article
- Target venue: eLife (provisional); the thesis chapter will retain expanded methodological and negative-result detail
- Backup venues: [MISSING: authors to choose]
- Venue rules checked on (date) and source URL: 2026-10-24; https://elife-rp.msubmit.net/html/elife-rp_author_instructions.html and https://elifesciences.org/about/submit-your-research
- Word / figure / reference limits: Research Articles have no maximum length, but eLife suggests no more than 5,000 words in the main text, excluding Methods, References, and Figure legends; no display-item limit. Abstract normally 150–200 words; title suggested up to 120 characters. No fixed reference limit identified.
- Required front matter: title, 150–200-word abstract, 15–30-word third-person impact statement, funding information and funder role, author information/contributions, competing interests, data and software availability; acknowledgements and references. Exact submission/VOR requirements to be rechecked before submission.
- Section order for this venue: Introduction; Results; Discussion; Materials and Methods; Acknowledgements; References; figures and legends; tables. A Methods/Model section may follow the Introduction when justified.
- Reporting checklist: ARRIVE 2.0 for animal research and eLife MDAR checklist; final VOR checklist if applicable.

## Science
- Species / preparation: mice; behavioural preparation details, sex/age/strain and ethics identifiers remain [MISSING: author records]
- Task / paradigm: reaction-time random-dot motion direction discrimination on two rigs, with control trials and brief signed motion-pulse trials
- Techniques: behavioural psychophysics; stimulus replay and motion-energy filtering; drift-diffusion and extrema-detection modelling; cross-validation, predictive checks, simulation calibration and model diagnostics
- Units of analysis: mice for group inference (10 total); mouse-sessions, scheduled cells and trials for descriptive or within-mouse estimates as explicitly labelled
- Pre-registration or analysis plan: a confirmatory primacy plan was locked before the relevant outcome inspection and subsequently amended in a versioned audit trail; the final timing test was not run after predictive gates failed. Later pulse diagnostics are explicitly exploratory. The plan was not externally preregistered.

## Inputs the human supplies (paths)
Agents only report results that come from these files.
- Analysis outputs / statistics tables: `consistency_2026-10-23-v2.json`; `claims_2026-10-23-v2.csv`; `sources_2026-10-23.json`; `parameters_common_model_2026-10-23.csv`; `pulse_followup_results_2026-10-23.md`; `/src/dissemination/reports/mouse-ddm-analysis-log.md`; relevant `/src/.agents/reports/2026-10-23-pulse-*.md`. Detailed mapping: `np/input_inventory.md`.
- Figures (drafts or finals): `figures/fig1_behaviour_2026-10-20.{pdf,png}`; `figures/fig2_motion_energy_2026-10-20.{pdf,png}`; `figures/pulse_followup/20261023T191030Z_fa8de8b/` excluding its `superseded_diagnostics_attempt1/` subfolder. Remaining main figures are not yet assembled.
- Methods notes / protocols / IACUC numbers: `/src/dissemination/reports/motion-energy-methods.md`; `/src/dissemination/reports/primacy-analysis-plan.md`; analysis scripts/notebooks linked from `sources_2026-10-23.json`; [MISSING: animal/training protocol and ethics/IACUC details].
- Prior drafts, talks, grant text: `manuscript_2026-10-23.md`; `outline.md`; `story_and_figures_2026-10-23.md`; `figure_captions_story_2026-10-23.md`; `/src/dissemination/poster/SfN Poster - 2025.pdf`.
- Key papers the authors consider essential: current public literature records in `sources_2026-10-23.json`, including Stine et al. (2020); authors must identify any additional must-cite papers at G2.
- Zotero library or folder to seed the literature review: [MISSING: no Zotero library/folder or credentials identified]

## People and policy
- Authors (order, roles) and corresponding author: [MISSING: authors, order, roles, affiliations and corresponding author]
- Who approves gates (human-in-the-loop): V. Thakur through this project chat, unless the author designates another approver
- Confidentiality: no unpublished text, data or figures may be sent to external AI services without explicit author approval. Public scholarly APIs may be used for citation verification.
- AI-use disclosure required by venue: prepare a transparent drafting-assistance disclosure; exact eLife policy and final wording must be checked before submission. Scientific Agent Skills citation is already present in the working draft.

## Run settings
- Mode: full  <!-- full | lit-only | section:<name> | review-only | revise -->
- Max review rounds per section: 2
- Minimum verified sources for the literature review: 25
- Citation style / reference manager: eLife author-date style; Markdown/Pandoc source of truth. Zotero/pyzotero may be adopted after the author identifies the library.
