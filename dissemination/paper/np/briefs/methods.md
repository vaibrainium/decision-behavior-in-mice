<!-- np-contract
stage: S3 ; section: methods ; agent: np-architect ; version: v3
thesis: "Joint held-out prediction on control trials favoured the tested accumulator over a rapid-forgetting implementation, but randomized motion pulses exposed a failure of the tested model-and-input pipelines to generalize to transient strong evidence."
claims: C016, C017, C018
numbers: N001, N004, N005, N006, N009, N010, N016, N018, N022, N023, N027, N034, N036, N051, N052, N053, N054, N055, N056, N057, N058, N059, N060, N061, N062, N063, N064, N065, N066
sources: adelson1985spatiotemporal, bogacz2006physics, luken2025parameter, palmer2005effect, ratcliff2008diffusion, wiecki2013hddm
-->
# Brief: methods

Purpose (one sentence): Make every Results analysis reproducible in the same order while preserving explicit gaps in animal, ethics, hardware and release records.

Venue constraints: words 3,400, excluded from eLife's suggested 5,000-word main-text scope; past tense; subsections mirror Results/Figures 1–5 and S6 after an animals/ethics subsection; equations and operational rules included; ARRIVE 2.0/MDAR items explicit; unknown facts remain `[MISSING: ...]`.

Reader question this section answers: Could another lab reconstruct the task, model inputs, comparisons, behavioural estimands and stopping decisions without guessing any unreported detail?

Paragraph plan:

| # | Move (from section-specs) | Content | Claims | Numbers | Sources | Figure |
|---|---|---|---|---|---|---|
| 1 | Subjects and ethics | Species/cohorts and all required animal-care/reporting facts, with unresolved records visibly marked. | — | N001, N004 | — | 1 |
| 2 | M1 apparatus/task | Head fixation, RDK, lick responses, reward/error contingencies, minimum viewing, rig clocks and pulse schedules. | — | N009, N010 | — | 1A–B |
| 3 | M1 analysis sets | Valid-response/censored construction, scheduled versus historical labels, exclusions and outcome definitions. | — | N005, N006 | — | 1C–E; S1 |
| 4 | M2 replay | Seed-based rig implementations, frame sampling, documented replay/acquisition uncertainty and no-pulse counterfactual. | — | — | — | 2A, 2E; S2 |
| 5 | M2 motion energy | Oriented filters, quadrature energy, opponent subtraction, causal support, calibration and units; precedent does not validate replay fidelity. | C017 | — | adelson1985spatiotemporal | 2B–D |
| 6 | M3 model rationale/equations | Bounded diffusion, reconstructed input, fast-response mixture, nondecision/censoring mapping and the rapid-forgetting implementation used in the approved control comparison. | C016 | — | ratcliff2008diffusion; palmer2005effect; bogacz2006physics | 3A |
| 7 | M3 likelihood/fitting | Choice-response multinomial, conditional RT bins, smoothing, optimization, simulation repetitions and parameter bounds. | — | N023 | — | 3 |
| 8 | M3 comparison/recovery | Five-fold control-only CV, score sign, Monte Carlo working threshold, fit-quality separation and recovery/identifiability rationale. | C018 | N016, N018 | wiecki2013hddm; luken2025parameter | 3B–D; S3 |
| 9 | M4 assignment and estimand | Assignment audit, supported cells/weights, directional contrast, control pseudo-onsets/shams and retained pre-onset/no-response trials. | — | N055, N056, N057, N058 | — | 4A–C; S4 |
| 10 | M4 time course/statistics | Competing cumulative outcomes, shared endpoint, subject-level t intervals, Holm family, robustness and estimator simulations. | — | N051, N052, N053, N054, N059, N060, N061, N062 | — | 4D; S4 |
| 11 | M5 frozen predictions | Frozen control parameters, prediction files/repetitions, pulse-gain CV, original/revised/choice-optimal predictions and legacy-input common-row restriction. | — | N022, N023 | — | 5A–B |
| 12 | M5 diagnostics | Exact objective decomposition, RT-term inclusion rule, gain profiles, held-out choice and remaining-objective changes, exploratory designation. | — | N063, N064, N065, N066 | — | 5C–D; S5 |
| 13 | M6 gates and sensitivity | Define the primary strict baseline and the secondary `L1U1V1Z0G1` leak-plus-urgency baseline, both control-fitted with fast-only guesses and later pulse-gain revision; report original/revised gate rules, strategy generator/scoring, temporal-decay calibration and the rule that withheld the timing model. The secondary baseline is supplementary and supports only C007. | — | N027, N034, N036 | — | S6 |
| 14 | Reproducibility and availability | Unit of inference, software/environment/commit, source data, repository/access, reporting checklist and recorded blinding status. Hand off the unresolved data/software and AI-disclosure wording to the end-matter plan. | — | — | — | all |

Promises this section creates: None beyond faithful reproducibility; any method not already supporting an approved result must be omitted or labelled as an unused exploratory procedure.

Promises it must deliver: A one-to-one method path for every Results paragraph; exact analysis populations and units; transparent randomization, multiplicity and stopping rules; distinctions among task deadline, analysis cutoff and pulse-aligned endpoint.

Must include: `[MISSING: mouse strain, sex, age, provenance, housing, water restriction/welfare monitoring, sample-size rationale, ethics bodies and protocol IDs]`; `[MISSING: training stages/criteria, session rules and complete rig/display hardware]`; `[MISSING: whether blinding was performed and at which stages]`; `[MISSING: final software lock/run commits and data/code repository, identifiers, access conditions and release timing]`; `[MISSING: final AI-use disclosure wording after eLife policy recheck]`; primary-claim treatments for C016–C018 with verified sources.

Must not include: Invented IACUC language, equipment, versions or exclusion rules; claims that generic DDM or motion-energy precedents validate this implementation; the unreviewed tau-p pilot; a timing-model result that was never run; raw-data modifications.

Known risks / reviewer bait: Historical and scheduled pulse labels differ; recovered pulse trials are absent from legacy model inputs; UCLA replay is approximate; RT likelihood coverage varies by mouse; quantile objective is not a standard calibrated likelihood; some parameters are near bounds or poorly recovered.

Acceptance criteria (the reviewer instantiates these at commit time):

- Subsections mirror Figure 1, Figure 2, Figure 3, Figure 4, Figure 5 and S6 in order.
- C016, C017 and C018 each appear once as primary claims with their verified sources.
- Every Results analysis has enough detail to identify inputs, exclusions, nesting, statistic and uncertainty.
- All missing animal, ethics, hardware and release facts remain explicit rather than silently omitted.
- The reader can reproduce why the timing test was not run.
