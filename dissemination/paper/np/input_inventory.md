# S0 input inventory

Checked: 2026-10-24 by Codex. Paths are relative to `/src/dissemination/paper/` unless absolute.
This is an inventory, not scientific approval. Raw data were not modified or reanalysed.

## Current manuscript and planning inputs

- `manuscript_2026-10-23.md`: current 193-word-abstract working draft; 94 evidence-linked claim markers. It is an input to neuropaper, not approved prose.
- `outline.md`, `story_and_figures_2026-10-23.md`, `figure_captions_story_2026-10-23.md`: current story, five-figure plan and draft legends.
- `/src/.agents/plans/2026-10-20-paper-writeup.md` and `/src/.agents/reports/2026-10-23-manuscript-story-integration.md`: active writing plan and latest drafting audit.
- `/src/dissemination/poster/SfN Poster - 2025.pdf`: historical framing only; its accumulation/primacy claims and session denominator are superseded as documented in the poster-review report.

## Evidence and traceability inputs

- `consistency_2026-10-23-v2.json`: 66 numeric facts plus five methods and five result consistency records. This is the source for the initial neuropaper number ledger.
- `claims_2026-10-23-v2.csv`: 94 claim hashes linked to evidence IDs; verification status remains human-unverified.
- `sources_2026-10-23.json`: 29 public and restricted evidence records with exact locators. This is the migration map, not yet the neuropaper literature ledger.
- `parameters_common_model_2026-10-23.csv`: final all-trial common-model parameter summary.
- `pulse_followup_results_2026-10-23.md`: behavioural pulse results and model-diagnostic narrative.

## Result-to-source map

| Result expected in paper | Authoritative evidence locator |
|---|---|
| Dataset, rigs, sessions and task | E003, E006, E008 and E024 in `sources_2026-10-23.json` |
| Motion-energy reconstruction and hidden coherence | E004 and E009 |
| Common-model selection, integration-vs-extrema comparison and recovery | E019 and E023 |
| Failed predictive gates and low strategy-test sensitivity | E020, E021 and E022 |
| Randomized directional pulse effect | E024 and E025 |
| Pulse-aligned response time course | E026 |
| Stimulus/replay audit | E027 |
| Choice-versus-response-time model conflict | E028 |
| Estimator calibration | E029 |

The evidence IDs above resolve to exact files, notebook cells, scripts and commands in `sources_2026-10-23.json`.

## Figures confirmed present

- Main-figure drafts: `figures/fig1_behaviour_2026-10-20.{pdf,png}` and `figures/fig2_motion_energy_2026-10-20.{pdf,png}`.
- Pulse follow-up panels: 17 current PNG files in `figures/pulse_followup/20261023T191030Z_fa8de8b/`, covering behaviour, response time, stimulus audit, model diagnostics and estimator validation.
- Remaining publication figures are not assembled. Figure source assignments are in `story_and_figures_2026-10-23.md`.

## Exclusions and warnings

- Do not use `figures/pulse_followup/20261023T191030Z_fa8de8b/superseded_diagnostics_attempt1/`.
- Do not promote the `tau_p` pilot into formal claims until the planned independent post-run check is complete.
- Do not describe the failed-gate timing analysis as a null primacy result; the confirmatory timing test was not run and its calibrated power was inadequate.
- Do not infer accumulation uniquely: control trials favour the tested accumulator over the tested rapid-forgetting/extrema alternative, while pulse diagnostics expose model inadequacy.
- Forty-eight UCLA no-response pulse trials were historically labelled as controls in DDM inputs; a versioned corrected input recovered 43, while original inputs remain unchanged.
- Animal/training/ethics details, final authorship, declarations and release statements remain missing.

## Inventory metrics

- 66 numeric facts in the audited consistency registry.
- 94 claim records in the current claim registry.
- 29 evidence records in the current source manifest.
- 2 assembled main-figure drafts and 17 current pulse-follow-up panel images.
- 10 mice, 50 mouse-sessions and 30,045 accepted behavioural trials are represented in the current audited records; analysis-specific denominators differ and must remain explicit.
