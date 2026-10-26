SIMULATED DECISION: MAJOR REVISION

Reason: the paper is unusually candid and internally well audited, but the causal pulse claim lacks session-pinned assignment provenance, required animal/ethics records are absent, and the central model-limit framing remains more definite than the historical stimulus and model-input records permit. These are panel recommendations, not an eLife editorial decision.

<!-- np-contract
stage: S6 ; section: panel ; agent: np-devils-advocate ; version: v1
thesis: "Joint held-out prediction on control trials favoured the tested accumulator over a rapid-forgetting implementation, but randomized motion pulses exposed a failure of the tested model-and-input pipelines to generalize to transient strong evidence."
claims: C001, C003, C004, C005, C006, C007, C008, C009
numbers: N016, N051, N052, N053, N059, N063, N064, N065, N066, N095, N098, N105, N106, N107, N108, N109
sources:
-->

# S6 devil's-advocate panel review

Criteria commitment: `np/panel/criteria_devils_advocate.md` (written before reading the manuscript, spine, ledgers, audits, figures, source tables, or core reports).

# Comments to authors

## Scope and limits

This is a working draft for a simulated journal panel. It is not an independently submitted peer review and does not impersonate an eLife reviewer or editor. I reviewed the rendered `manuscript.md`, locked `np/spine.md`, claim and number ledgers, integrity audit and recheck, selected Figures 1–5 and S6 with adjacent source tables, and the central control-model, pulse-data, stimulus, behaviour, response-time, validation and diagnostic reports. I did not rerun raw-data analyses or model fits, inspect collection hardware, or verify historical task-code versions beyond the project records. The accountable human must verify every location and judgment.

## Neutral assessment and strengths

The study compares two fully specified control-trial pipelines, shows that their joint held-out predictions favour the no-leak accumulator within this cohort, establishes a mouse-level signed-pulse association, and then subjects the control-selected pipelines to a strong out-of-condition stress test. Its best feature is epistemic discipline: the manuscript separates the behavioural pulse effect from mechanism, reports failed gates and low sensitivity, keeps the confirmatory timing test unrun, shows mouse-level heterogeneity, and treats replay, model and response mapping as a pipeline. The source tables and S5 audits support the reported numbers and denominators. The concerns below arise precisely because the negative transfer result is promoted to the paper's organizing claim.

## Numbered issues

### 1. P0 — “Randomized” and causal pulse wording are not secured to the code that generated these sessions

**Location.** Title/Abstract and Introduction (`manuscript.md:7`, `:21`); Results (`:31`, `:59–69`); Methods (`:204–218`); C001/C005 in `np/ledger/claims.csv`.

**Evidence/criterion.** The manuscript states that task-code inspection indicated pre-outcome randomization but explicitly says the inspected repositories were “current snapshots rather than session-pinned collection versions” (`manuscript.md:204`). The source audit reports moderate—not high—confidence for code-version match; UCLA has no per-session configuration, while the balance checks are descriptive and cannot prove the assignment mechanism (`.agents/reports/2026-10-23-pulse-data-20261023T191030Z_fa8de8b.md`). Randomization is the basis for causal language and for calling the directional shift a perturbation effect rather than an adjusted association.

**Why it matters.** If collection-era code differed in repeat-trial handling, block construction, or assignment probabilities, common-support adjustment does not by itself restore randomization. This does not make the observed contrast disappear, but it changes the estimand and the permissible verb.

**Strongest counterargument.** The audited HEAD implementations specify pre-outcome, unannounced assignment; UW session configurations match that implementation; signs are balanced within supported strata; and sign is nearly unrelated to prior choice, outcome, or session half. The estimate is also stable across several existing-data checks.

**Bounded remedy.** Supply collection-era commit hashes, archived code, run metadata, or logs that bind the assignment implementation to the analysed sessions. If that is unavailable, replace “randomized”/causal wording with “pre-outcome scheduled assignment” and describe the result as a covariate-balanced within-stratum association, with the version-provenance limitation in the Abstract and Figure 4 legend. No reanalysis is required for the narrowing option.

### 2. P0 — The manuscript is not ethically or descriptively appraisable as an animal study

**Location.** Author placeholder (`manuscript.md:3`); Animals and oversight (`:112–116`); task details (`:120`); end matter (`:265–275`).

**Evidence/criterion.** Strain, sex, age, provenance, housing, water restriction/welfare monitoring, sample-size rationale, ethics bodies/protocol identifiers, blinding, training/session criteria, complete rig details, funding, conflicts, contributions, data/code availability and author information are explicitly missing. The S5 audit treats these honestly as author-supplied placeholders, but an eLife/ARRIVE review cannot assess welfare, sampling, exclusions, or reproducibility without them.

**Why it matters.** This is a submission blocker independent of whether the statistical conclusions are correct. In particular, sex/age/strain and session acceptance could affect external validity, and the ethics approval cannot be inferred.

**Strongest counterargument.** The placeholders are visible rather than invented, and the scientific draft was intentionally allowed to enter simulated panel review before final production facts were supplied.

**Bounded remedy.** Authors must supply the records and complete the ARRIVE/MDAR mapping. No scientifically honest remedy exists within the current files; omission or boilerplate substitution is not acceptable.

### 3. P1 — The headline converts a failure of a model-and-input pipeline into a limitation of “an evidence-accumulation model”

**Location.** Title (`manuscript.md:1`), impact statement (`:11`), Results subheading and conclusion (`:75–81`, `:94`), Discussion (`:98`, `:108`). Compare the narrower spine scope and `manuscript.md:41–43`, `:81`, `:102–104`.

**Evidence/criterion.** The tested object includes reconstructed frames, a motion-energy filter, calibration, pulse-component decomposition, an approximate likelihood and response mapping. UCLA acquisition frame rate, dot lifetime, monitor refresh, vertical synchronization and screen geometry are unresolved (`manuscript.md:132–148`). The stimulus report finds plausible UCLA pulse-energy alternatives 1.28–1.40 times the stored replay and incomplete seed-level fidelity. Figure 2 makes these caveats visible, but the title names the model alone.

**Why it matters.** A reader can reasonably infer that the accumulator's dynamics failed, whereas the paper has shown only that one historical end-to-end implementation failed. That distinction is the principal logical boundary of the study.

**Strongest counterargument.** The title says “limits,” not falsification; the Abstract concludes with the unresolved sensory/decision/response locus; and the body repeatedly uses “model-and-input pipeline.” Amplitude alternatives also appear too small to explain the reported magnitude mismatch by themselves.

**Bounded remedy.** Put “model-and-input pipeline” or “control-fitted decision pipeline” in the title and impact statement, and reserve “model failure” for explicitly defined shorthand. If the authors keep the current title, they should provide a sensitivity refit under the plausible input conventions; otherwise the stronger model-specific implication is not earned.

### 4. P1 — The claimed temporal-profile failure is descriptive, post-gate exploratory, and not tested as a paired model-minus-data contrast

**Location.** Abstract (`manuscript.md:7`); Results subheading and assertions (`:75–83`); Figure 5 legend (`:344–358`); Discussion (`:98`, `:102`).

**Evidence/criterion.** The text says the models predicted the “wrong temporal profile” and “failed to generalize,” but also concedes that Figure 5 intervals are separate between-mouse summaries, not intervals for paired differences (`manuscript.md:81`). Source table `figures/fig5_model_mismatch_2026-10-26_v3_source_windows.csv` shows overlap in early/middle windows, while the clearest late separation is a diagnostic developed after gate failure. The dense-mouse tradeoff uses one main Monte Carlo seed per informative mouse and is demonstrated only for PSUIM6/7 (`.agents/reports/2026-10-23-pulse-diagnostics-20261023T191030Z_fa8de8b.md`).

**Why it matters.** The gates establish broad inadequacy of choice/RT/censoring predictions; they do not by themselves establish that temporal shape is the statistically localized failure. The narrative promotes the exploratory localization above its inferential status.

**Strongest counterargument.** The observed/model overlays use identical common rows and weights, both accumulator and leak-plus-urgency implementations show the same qualitative early-rise/late-decline pattern, and the manuscript labels the comparison descriptive in the Abstract and Results.

**Bounded remedy.** Either (a) report a predeclared paired mouse-level observed-minus-predicted window contrast with simulation uncertainty and a small multiplicity family, or (b) consistently change “wrong temporal profile” to “descriptively different profile” in the subheading, Discussion, title-facing text and conclusion. Keep the PSUIM6/7 diagnostic explicitly illustrative.

### 5. P1 — The central pulse-transfer comparison uses known-corrupted legacy inputs without a corrected refit

**Location.** Results (`manuscript.md:69`, `:81`); Methods (`:124–128`, `:234`, `:240`); Figure 5 legend (`:356–358`).

**Evidence/criterion.** Legacy inputs mislabel 48 UCLA no-response pulse trials as controls; 43 directions are recoverable, 38 are genuine non-null pulses, and five zero-coherence directions are unknowable. Fifteen late-stratum UCLA pulse trials were excluded because responding during the pulse left duration unknown—an outcome-dependent exclusion. The diagnostic report estimates that mislabelling biases observed pulse censoring down by as much as 1.7 percentage points and control censoring up by as much as 1.2, weakly favouring the old gate (`.agents/reports/2026-10-23-pulse-diagnostics-20261023T191030Z_fa8de8b.md`). The manuscript discloses the problem but makes the unchanged common-row overlay central.

**Why it matters.** Disclosure does not establish robustness. Known outcome-linked classification errors are most concerning when the model is judged jointly on response occurrence and timing.

**Strongest counterargument.** The affected counts are small relative to the full data; the direction effect uses corrected scheduled labels and is unaffected; model–data curves use an explicit intersection; and the estimated censoring bias would make the original gate look better, not manufacture failure.

**Bounded remedy.** Build a versioned corrected input, refit the control models, and repeat only the frozen transfer/gate and Figure 5 overlay as a sensitivity analysis. If the authors will not refit, downgrade the temporal/localization claim and state that the current comparison is a historical-pipeline audit rather than the best estimate obtainable from the present records.

### 6. P1 — “Held-out” does not mean independent confirmation after adaptive model construction on the same control dataset

**Location.** Abstract (`manuscript.md:7`); Results (`:47–57`); Methods (`:180–200`); Figure 3 (`:312–327`).

**Evidence/criterion.** Five-fold control-only CV separates fitting from fold scoring, but the same cohort and control dataset were repeatedly used to choose the common-model components, guess form and bias, set the rapid-forgetting comparison, inspect fit quality, and settle the final narrative. Methods acknowledge within-cohort generalization and trial-count weighting (`manuscript.md:188–192`), but the front matter does not convey the adaptive model-development context. Figure 3B is strongly influenced by PSUIM6/7, although all ten mouse differences are positive and six exceed the approximate +10 threshold.

**Why it matters.** Ordinary CV estimates performance of a fixed workflow; reusing its scores for model development and final comparison is optimistically biased unless model selection is nested or a reserved set remains untouched. It also does not provide a population-level uncertainty statement.

**Strongest counterargument.** The claim is deliberately relative, all ten per-mouse differences favour the accumulator, the aggregate is 345.7 NLL units, and the paper explicitly denies new-animal or population-significance generalization.

**Bounded remedy.** Label the control comparison exploratory/model-development evidence and foreground the per-mouse distribution. A nested-CV or untouched-session analysis would strengthen it, but is not necessary if the claim is narrowed to “within this adaptively developed cohort comparison.” Do not call it independent confirmation.

### 7. P1 — The rapid-forgetting candidate is a useful stress test, not a sufficient alternative class

**Location.** Introduction (`manuscript.md:15`, `:21`); Results (`:49`, `:57`); Methods (`:172–178`); Figure 3A (`:314–318`).

**Evidence/criterion.** The comparator restricts leak to 20–200 s⁻¹ (5–50 ms nominal time constants) after a sensory filter. It is explicitly not an exact extrema detector. An all-control free-leak fit explored 0–200 s⁻¹ and returned <2 s⁻¹ in every mouse, but that result is descriptive and is not the headline cross-validated comparison. Other non-integrating strategies, state-dependent policies, alternative sensory transformations and response rules remain outside the candidate set.

**Why it matters.** “Evidence retention” versus this very-fast-forgetting implementation is not a general integration-versus-non-integration test. A skeptical reader may view the comparator as deliberately extreme.

**Strongest counterargument.** The manuscript consistently says “among the tested implementations,” calls the comparator an “approximation,” and explicitly refuses unique identification.

**Bounded remedy.** Retain the result but make the operational question explicit in the Abstract: no leak versus 20–200 s⁻¹ rapid forgetting under one shared response model. Add the free-leak descriptive result and its non-cross-validated status to the main Figure 3 narrative, or explain why it is not part of the primary comparison.

### 8. P1 — Pulse magnitude and timing are entangled with rig/cohort, and the largest effects occur where replay uncertainty is greatest

**Location.** Results (`manuscript.md:27–33`, `:61–73`); Discussion (`:102`, `:104`); Figure 4A/D (`:329–342`).

**Evidence/criterion.** Rig, site and cohort are fully confounded. Figure 4 source data show the four UCLA mice have directional effects of about 7.3–15.7 pp, whereas five of six UW mice are about −3.5 to 4.6 pp and one is 6.7 pp (`figures/fig4_pulse_behaviour_2026-10-26_v2_source_mouse_estimates.csv`). The diagnostic report explicitly notes that the four largest pulse effects are the same cohort. UCLA is also the rig with unresolved display-loop settings, possible replay freezes, and 1.28–1.40 pulse-energy alternatives.

**Why it matters.** The equal-mouse mean is valid for the sampled mice, but the apparent cohort concentration undermines a generic “mice” statement and makes the central transfer mismatch inseparable from hardware/input differences.

**Strongest counterargument.** Assignment is within mouse, both rigs mostly show the same direction, rig is never interpreted biologically, and leave-one-mouse-out estimates remain positive. A stronger delivered pulse in UCLA cannot by itself explain why the tested pipeline misses temporal shape.

**Bounded remedy.** Show rig-stratified effect estimates and model-minus-data curves descriptively, without a biological rig test, and state in the Abstract that the pooled effect is heterogeneous and concentrated in one confounded rig/cohort. A new crossed-rig replication is the clean remedy; no reweighting of this dataset can unconfound rig, site and cohort.

### 9. P1 — “Physical omission” is not a stable no-pulse counterfactual, and a known persistent stimulus artefact was not directly conditioned out

**Location.** Results (`manuscript.md:41`); Methods (`:132–148`); Figure 2D legend (`:303–310`).

**Evidence/criterion.** Pulse-present and omitted branches are identical before onset but consume different random draws after pulse offset; unsigned late motion-energy differences remain large even when their sign-aligned mean is near zero. The task also creates a deterministic pulse-direction-aligned rounding shift of about 0.07–0.16% coherence on average (up to 0.66% in specified cells) that lasts for the remainder of the trial. The stimulus report lists a cell-level behavioural check as an open question (`.agents/reports/2026-10-23-pulse-stimulus-20261023T191030Z_fa8de8b.md`).

**Why it matters.** A long weak signed tail is precisely the boring explanation for a delayed, sustained behavioural contrast. The diagnostic scaling estimate suggests it is too small (roughly 0.03–0.3 pp), but that estimate is not the registered behavioural analysis and the phrase “physical omission” overstates counterfactual control after offset.

**Strongest counterargument.** The artefact is tiny relative to the 5.8-pp effect; its expected sign and size were audited over all genuine pulses; the manuscript explicitly describes stream divergence; and the replay is used to define a pipeline, not to claim frame-perfect omission.

**Bounded remedy.** Rename the panel “branched replay with pulse command omitted.” Add the already proposed stratified/covariate sensitivity using affected versus unaffected rounding cells, or provide a direct upper-bound calculation in the manuscript. If neither is done, state that persistent physical bias was bounded but not behaviourally excluded.

### 10. P1 — The gate/calibration package is over-weighted relative to what it can identify

**Location.** Abstract (`manuscript.md:7`); Results (`:85–94`); Methods (`:242–248`); Figure S6 (`:360–373`).

**Evidence/criterion.** Gates are adequacy screens with chosen 80% coverage and relative-choice thresholds, not equivalence tests. Calibration uses only 20 full-cohort datasets per level, fixes fitted control parameters, and does not propagate their uncertainty. As imposed decay grows, gate pass rates collapse from 19/20 to 1/20; the core report says this occurs partly by construction because the decay changes pulse RTs while control parameters remain fixed and that those rates “say little about the real data” (`dissemination/reports/mouse-ddm-analysis-log.md`, §5.11). Yet Figure S6 and the narrative present the falling green curve alongside detection failure as one calibration story.

**Why it matters.** The workflow can stop because the alternative generator makes the baseline inadequate before the timing test is reached. That is a valid safeguard but not a conventional power analysis of the scientific hypothesis. Repeated negative checks risk becoming rhetorical evidence for the paper rather than limits of the procedure.

**Strongest counterargument.** The manuscript repeatedly states that low sensitivity is not evidence against primacy/recency, keeps strategy and timing calibration separate, and correctly withholds the confirmatory test.

**Bounded remedy.** In Figure S6E and the Results, explicitly say that gate attrition under decay is partly structural and is not evidence about the real data. Compress the negative procedural record in the main narrative, retain full detail in S6, and separate “pipeline inadequacy” from “timing-test sensitivity” in the Abstract.

### 11. P1 — Reproduction of the choice gate and final package is still incomplete

**Location.** Methods (`manuscript.md:182–192`, `:228–248`, `:250–263`); availability placeholder (`:273`).

**Evidence/criterion.** The manuscript specifies many simulation and optimizer settings but does not fully define the statistical model producing the choice-departure estimate and “95% posterior interval” displayed in the S6 source table. It also lacks the final manuscript-wide software lock, release identifiers and access conditions. The objective is explicitly a simulation-based score, not a calibrated likelihood, while some post-gate thresholds use likelihood-like quantities.

**Why it matters.** A reader can reproduce neither the central gate nor the complete paper package from the manuscript alone. Dense parameter listings do not substitute for one executable, versioned analysis path and a definition of each estimand.

**Strongest counterargument.** Commands, commits, hashes and environments exist across the project reports; deterministic assembly and source reconciliation passed; the final repository release was intentionally deferred.

**Bounded remedy.** Add the exact choice-gate model, priors/interval construction, pooling unit and computation to Methods; provide a versioned code/data release or a justified controlled-access plan; and cite one frozen environment/commit manifest rather than dispersing provenance across prose.

### 12. P1 — The paper's significance currently rests more on diagnostic failure than on a positive, generalizable advance

**Location.** Title/Impact (`manuscript.md:1`, `:11`); Results sequence (`:75–94`); Discussion opening/conclusion (`:98`, `:108`); full Figure S6.

**Evidence/criterion.** The positive findings are a relative two-implementation control comparison and a heterogeneous signed-pulse effect. The most novel result—the delayed/sustained mismatch—is descriptive, depends on uncertain historical inputs, and is followed by several insensitive or failed procedures. Roughly half of the conceptual payoff is built from what the selected pipelines and tests could not do.

**Why it matters.** Negative model checks can be valuable, but an eLife editor may ask whether the paper discovers a principle or mainly documents that one bespoke model/input reconstruction did not transfer. The present rhetoric sometimes treats procedural stopping itself as biological information.

**Strongest counterargument.** Honest out-of-condition failure is the intended contribution; the paper gives a concrete successor-experiment design and does not disguise failed tests as null biological findings.

**Bounded remedy.** Reframe the advance as a methodological demonstration with a specific empirical payload: joint response distributions under pre-outcome signed pulses reveal a reproducible constraint that control-fit ranking misses. Reduce prominence of repeated gate-failure statements, and make the durable deliverable the benchmark dataset/analysis contract rather than a model-specific negative result. If eLife breadth is retained, the corrected-input sensitivity and crossed-rig replication become much more important.

### 13. P2 — Numerical precision exceeds the biological and Monte Carlo precision

**Location.** Abstract (`manuscript.md:7`); Results (`:61`, `:71`, `:83`, `:87`, `:91`); legends (`:331–370`).

**Evidence/criterion.** Estimates are printed to six or more decimals (for example, 5.844356 pp and P = 0.01941029) despite ten biological units, simulation noise, and broad intervals. The exact ledger values are appropriate for audit trails, not narrative prose.

**Strongest counterargument.** Exact expansions guarantee that rendered values match the ledger and prevent silent rounding drift.

**Bounded remedy.** Keep exact values in source data/ledgers and round prose/figures to defensible precision (for example, 5.8 pp, 95% CI 1.8–9.9; adjusted P = 0.019).

### 14. P2 — Legends and reproducibility prose obscure the inferential hierarchy

**Location.** Figure legends (`manuscript.md:279–373`) and reproducibility table (`:250–263`).

**Evidence/criterion.** Legends contain long ledger-style count strings, optimizer grids and full run records. Figure S6's panel D label is visually crowded against “Coverage,” a nonblocking issue already noted by the integrity auditor. These details are auditable but make it harder to see which panels are confirmatory, exploratory, descriptive, or in-sample.

**Strongest counterargument.** Exact denominators and settings were deliberately kept visible to avoid ambiguity.

**Bounded remedy.** Keep n, unit, uncertainty and analysis status in each legend; move full vectors/grids/hashes to a source-data or reproducibility appendix. Reposition the S6 panel D label on the next export.

## What would sink the paper?

The clean falsifier is a versioned replication or reserved validation set with photodiode/frame-verified pulse delivery, corrected scheduled labels, and a prespecified model/input pipeline. The paper's central transfer claim would fail if the control-selected pipeline then reproduced the mouse-level pulse-associated joint direction/response-time/no-response distribution—including a paired temporal-shape criterion—without pulse-outcome tuning. Within the current data, a corrected-input refit under acquisition-supported UCLA settings that removes the Figure 5/S6 mismatch would likewise invalidate the present headline. No such decisive analysis exists in the reviewed record.

## Recommended editorial disposition

Major revision is proportionate. The paper should not be rejected for reporting failed predictions; that candour is a strength. It should, however, resolve or narrow the randomization claim, supply animal/ethics records, distinguish model failure from pipeline failure at title level, and either validate the central mismatch on corrected/plausible inputs or make its exploratory and rig-confounded status unmistakable. A new experiment is not strictly required for a narrower methods/benchmark paper; it may be required for the current broad eLife significance framing.

## Structured panel action summary

- Location: Title, Abstract, Results/Figures 4–5 and S6, Methods, and animal/ethics/end-matter fields; detailed locations are given in issues 1–14 above.
- Observation: Two submission-blocking records are absent, and the central pipeline-failure narrative is stronger than the historical assignment, stimulus, corrected-input and paired temporal evidence warrants.
- Evidence or criterion: Issues 1–14 trace each concern to the rendered manuscript, locked scope, source tables, audit trail, and core reports under the precommitted P0/P1/P2 rules.
- Why it matters: Without correction or narrowing, readers can mistake an association for a randomized causal effect and a historically specific pipeline failure for failure of an evidence-accumulation mechanism.
- Requested action: Resolve the two P0 items; then address the P1 items through the least burdensome combination of provenance, corrected-input sensitivity, explicit descriptive labels, claim narrowing, and reproducibility records.

## Counts and blockers

- P0: 2
- P1: 10
- P2: 2
- Total: 14
- Blockers within present files: session-pinned assignment provenance is unavailable; required animal/ethics/blinding records are unavailable; final data/code release identifiers are unavailable. These require author records or claim narrowing. No manuscript, spine, ledger, state or gate file was edited, and G5 was not crossed.

# Confidential comments to editor

## Reviewer disclosures

- This is an author-authorized, local-only simulated panel draft, not an actual commissioned review or editorial decision.
- No conflict information was supplied for this simulation. The review is limited to the available repository records; raw analyses and historical hardware/code were not independently reproduced.
- Assistance used: Codex plus the local neuropaper, peer-review and scientific-critical-thinking procedures. No manuscript content was sent to network, search, citation, image-generation or other external services.
- The project retains the manuscript and review artifacts in its authorized repository; the author controls later retention or deletion.

## Editorial-process or integrity concerns

No misconduct allegation is made. If this were a real submission, the absent animal/ethics records and uncertainty over session-pinned assignment provenance would require resolution before relying on the causal language. All ordinary scientific criticisms are stated in the author-facing channel above.
