# Paper configuration

Filled at S0 (intake) by the orchestrator with the human. Every later agent reads this file.
Unknown facts remain explicitly marked as missing; never guess a value.

This is the **control-trial-only** paper, started 2026-10-29 at the author's request ("using only control trials
from our data, can we write up a paper on how mice do visual decision making in dynamic stimuli (RDK)"), modeled on
Stine, Zylberberg, Ditterich & Shadlen 2020 (eLife 9:e55365, `stine2020differentiating`). It is a third, separate
project; `/src/dissemination/paper/` and `/src/dissemination/paper_accumulation/` are left untouched.

## Paper
- Working title: How mice decide about dynamic random-dot motion: control-trial evidence (placeholder; settled at G1)
- Article type: Research Article
- Target venue: eLife (provisional; same venue as the model paper) 
- Backup venues: [MISSING: authors to choose]
- Venue rules checked on (date) and source URL: 2026-10-24 (first project); https://elife-rp.msubmit.net/html/elife-rp_author_instructions.html and https://elifesciences.org/about/submit-your-research. Recheck before S8.
- Word / figure / reference limits: eLife suggests no more than 5,000 main-text words excluding Methods, References and Figure legends; no display-item limit. Abstract normally 150–200 words; title up to 120 characters.
- Required front matter: title, 150–200-word abstract, impact statement, funding, author contributions, competing interests, data and software availability; acknowledgments and references.
- Section order for this venue: Introduction; Results; Discussion; Materials and Methods; Acknowledgments; References; figures and legends.
- Reporting checklist: ARRIVE 2.0 and eLife MDAR checklist.

## Science
- Species / preparation: mice (10), head-fixed behavior; sex/age/strain, training and ethics identifiers [MISSING: author records]
- Task / paradigm: reaction-time random-dot motion (RDK) direction discrimination on two rigs. **Control trials only**: pulse trials are not analyzed, modeled or mentioned as results (they may appear in Methods only as trials that were excluded).
- Techniques: behavioral psychophysics (psychometric, chronometric, RT distributions); stimulus replay and motion-energy filtering; psychophysical (motion-energy) kernels; bounded accumulation and non-integration models (rapid forgetting E, extrema samples ES, paper-exact DDMx/ESx); cross-validated model comparison; model recovery.
- Units of analysis: mice for group inference (10); sessions and trials only for labeled within-mouse descriptive estimates.
- Pre-registration or analysis plan: not preregistered. Model-comparison rules (parsimony rules, > 10 held-out NLL rule, group tests per 1,000 trials) fixed in earlier decisions (paper_accumulation D006, D008). New kernel and RT analyses are exploratory unless criteria are fixed before they are run.

## Fixed analysis rules (author, carried into this project)
- Trials without a response by 5 s (no RT, or RT > 5 s) enter no analysis; model likelihoods are conditional on a response by 5 s.
- Rig/site (UCLA vs UW) is a covariate only; results are never split or interpreted by site.
- Common model: L0U0V1Z0G1 (drift variability sv, fast guesses, free guess bias), responded-only, 50% non-response cap (paper_accumulation D004/D005). The no-sv model is not discussed beyond one Methods sentence without numbers (D003): the sv model set was chosen after the no-sv comparison was seen, and the ranking depends on sv.
- Group claims use per-1,000-trial held-out differences with mice as the unit (t and Wilcoxon, Holm, dz); summed totals secondary (D006, D008). Removing sv is not significant at group level; the text must not claim sv is needed (D008).
- Free-leak fits not used (D009). Parameters come from **control-split** fits, not all-trial fits.
- No claim that mice integrate rather than detect extrema unless the rerun recovery supports it (D007 condition b).

## Intended story (author request + G0 answers 2026-10-29; formalized at S1)
1. Mice perform reaction-time RDK discrimination: choice and RT depend on coherence (psychometric, chronometric, RT distributions, correct vs error RTs).
2. Choices depend on the moment-to-moment motion energy within a trial (psychophysical kernels, stimulus- and response-aligned) [NEW ANALYSIS].
3. Following Stine et al. 2020: integration and non-integration models can mimic each other's choice/RT signatures; on held-out control trials the common bounded-accumulator model predicts choices and RTs better than every tested non-integration alternative.
4. Whether that comparison can tell the strategies apart is measured by paired model recovery [PENDING: rerun on fixed CPU datasets].

## Inputs the human supplies (paths)
Agents only report results from these files. Inventory with status in `np/input_inventory.md`.
- Held-out model comparison, control trials, responded: `/src/dissemination/paper_accumulation/tables/heldout_group_2026-10-28.csv`, `heldout_per_trial_2026-10-28.csv`.
- Component comparison: `/src/dissemination/paper_accumulation/tables/components_group_2026-10-28.csv`, `components_per_trial_2026-10-28.csv`.
- Control-split parameters: `/src/dissemination/paper_accumulation/tables/parameters_common_model_control_2026-10-28.{csv,md}`.
- Paper-exact Stine models: `/src/.agents/reports/2026-10-28-stine-exact-models.md`.
- Control-only selection: `/src/.agents/reports/2026-10-23-control-only-selection.md`.
- Motion energy: `/src/dissemination/reports/motion-energy-methods.md`; Fig 2 A–C of `/src/dissemination/paper/figures/fig2_stimulus_reconstruction_2026-10-26_v6.*`.
- Behavior figure: `/src/dissemination/paper/figures/fig1_task_behaviour_2026-10-26_v2.*` [needs rebuild on responded control trials only].
- Model recovery: [PENDING: paired rerun, plan `/src/.agents/plans/2026-10-29-control-paper.md` step 3].
- Kernels and RT distributions: [PENDING: new analyses, same plan].
- Methods notes: [MISSING: animal/training protocol, ethics/IACUC details].
- Key papers: stine2020differentiating (model paper). Author-supplied 2026-10-29: Kirkpatrick, Turner & Sederberg 2021, Psychological Review 128(6):1051-1087, doi 10.1037/rev0000284 (accumulator dependency: DDM/FFI vs LCA vs race/LBA; equal-evidence RDK); verify and add at S2. 44 verified sources copied from paper_accumulation (`np/ledger/sources.csv`, notes in `np/lit/notes/`, prior searches in `np/lit/prior_project/`).
- Zotero library or folder: [MISSING: none identified]

## People and policy
- Authors (order, roles) and corresponding author: [MISSING]
- Who approves gates: V. Thakur through this project chat 
- Confidentiality: no unpublished text, data or figures to external AI services without explicit author approval; public scholarly APIs allowed for citation checks 
- AI-use disclosure: transparent drafting-assistance disclosure; check eLife policy before submission.

## Run settings
- Mode: full  <!-- full | lit-only | section:<name> | review-only | revise -->
- Max review rounds per section: 2
- Minimum verified sources for the literature review: 25
- Citation style / reference manager: eLife author-date; Markdown/Pandoc source of truth.
- Spelling: American English in manuscript-facing text.
