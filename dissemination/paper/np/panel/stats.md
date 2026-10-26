SIMULATED DECISION: MAJOR REVISION

<!-- np-contract
stage: S6 ; section: panel-stats ; agent: np-stats-reviewer ; version: v1
thesis: "Joint held-out prediction on control trials favoured the tested accumulator over a rapid-forgetting implementation, but randomized motion pulses exposed a failure of the tested model-and-input pipelines to generalize to transient strong evidence."
claims: C001, C004, C005, C006, C007, C008
numbers:
sources:
-->

# Statistical panel review

Reviewer: `np-stats-reviewer` (mode: panel)  
Criteria: `np/panel/criteria_stats.md`  
Manuscript reviewed: `manuscript.md` and `np/integrity/manuscript_marked_s5.md`  
Decision basis: 0 P0, 6 P1, 2 P2

## Overall assessment

The paper is statistically more disciplined than most model-transfer studies. Mice, not trials or cells, are the unit of group inference for the randomized pulse contrast; the three-test Holm family is declared; no-response outcomes and pre-onset responses are retained; control-model fitting is separated from pulse transfer; the failure-prompted pulse-gain revision is explicitly exploratory and cross-validated; and the stopped, insensitive timing test is not converted into evidence for a null temporal-weighting result. The ledgers, integrity audit and recheck, selected figures, and adjacent source records agree on the reported values and denominators.

Major revision is recommended because the paper's most prominent temporal-profile conclusion is stronger than its explicitly descriptive comparison, and because the central control-model score, small-sample pulse inference, legacy-input bias, and reproducibility record require clearer statistical qualification. These concerns are remediable without changing the locked thesis if the strongest temporal language is bounded. There is no P0 or evidence-integrity blocker.

## Criterion summary

| Criterion | Result | Panel finding |
|---|---|---|
| K1 Estimand and claim type | Partly met | The assignment contrast is well defined; the temporal-profile claim sometimes shifts from descriptive comparison to definitive failure language. |
| K2 Independent unit and dependence | Met | Mouse-level group inference is explicit; simulations, cells and trials are not treated as biological replicates. |
| K3 Missingness, censoring and exclusions | Partly met | Censoring is well defined, but the known legacy label/exclusion bias is not quantitatively connected to the predictive-gate interpretation. |
| K4 Direct tests and multiplicity | Partly met | The Holm family is explicit, but the headline confidence interval is unadjusted while displayed beside a Holm-adjusted p value. |
| K5 Magnitude and uncertainty | Partly met | The pulse effect has a mouse-level interval; the control-model comparison and model–data temporal difference lack corresponding sampling uncertainty. |
| K6 Null/equivalence/calibration language | Met | Failed gates and low sensitivity are not interpreted as equivalence or absence of primacy/recency. |
| K7 Power and sensitivity | Partly met | Timing-test calibration is strong; the primary behavioural effect's modest power and absent sample-size rationale are not prominent enough. |
| K8 Model comparison and CV | Partly met | Train/test separation is clear, but the central summed score is conditional on one within-session fold construction and is repeatedly called NLL despite being an uncalibrated simulation-based objective. |
| K9 Adequacy, identification and recovery | Met with limitations disclosed | Recovery, false positives, bounds and absolute misfit are reported and component-level claims are limited. |
| K10 Confirmatory versus adaptive work | Met | The original gate, failure-prompted gain revision, later diagnostics and stopped timing procedure are distinguished. |
| K11 Controls and transport | Met | Randomized scheduled assignment, common support, site/rig confounding and replay limitations are disclosed. |
| K12 Traceability and reproducibility | Partly met | Quantitative traceability passes, but key time units and the final software/data record remain incomplete. |
| K13 Descriptive/inferential boundary | Partly met | Figure 4 timing is appropriately descriptive; Figure 5's descriptive status is not maintained consistently in headings and conclusions. |
| K14 Conclusions follow | Partly met | Relative control-model support and the directional pulse effect follow; the temporal-shape conclusion needs either narrower language or direct uncertainty on the paired discrepancy. |

## P0 — must fix

None.

## P1 — should fix

### P1.1 The central temporal-profile claim outruns the analysis used to establish it

**Locations:** Abstract, `manuscript.md:7`; Results heading and text, `:75-81`; Discussion, `:98` and `:108`; Figure 5 legend, `:344-358`.

**Evidence:** Results state that the pipelines “failed to generalize the temporal profile” and the heading says they predicted the “wrong temporal profile.” Yet `manuscript.md:81` and the Figure 5 legend explicitly say that the group overlays are descriptive, that intervals are for each observed or predicted series rather than their paired difference, that simulation uncertainty is added, and that parameter uncertainty and legacy-input repair are absent. Figure 5A–B visually supports a discrepancy, but it is not a calibrated test or interval for the model-minus-observed temporal contrast. The formal gates support inadequate pulse prediction, but they do not by themselves estimate the displayed temporal-shape difference.

**Consequence:** The general statement that the registered pipelines failed their pulse predictive gates is supported; the more specific, headline-level assertion that a delayed/sustained temporal profile was demonstrated as different is less secure than the prose implies.

**Bounded remedy:** Choose one route at G5. Either (a) keep the existing analyses and consistently say that the observed and predicted temporal profiles *descriptively differed*, anchoring definitive “failed” language to the registered multicomponent gates; or (b) add a prespecified paired mouse-level observed-minus-predicted temporal contrast with simultaneous or otherwise multiplicity-aware uncertainty, Monte Carlo uncertainty, and a stated treatment of fitted-parameter uncertainty. Route (a) requires prose/heading edits only and preserves the thesis.

### P1.2 The control-model preference is conditional on an uncalibrated, trial-weighted score but is presented through a single precise aggregate

**Locations:** Abstract, `manuscript.md:7`; Results, `:47-55`; Methods, `:180-192`; Figure 3 legend, `:312-327`.

**Evidence:** Methods call the censored-quantile objective a simulation-based comparison score “not a calibrated likelihood” (`:182`), construct one condition-stratified five-fold partition within the same mice and sessions (`:188-190`), and sum scores without normalizing for mouse trial count (`:190`). The 345.7-unit aggregate therefore weights mice by available held-out trials and has no population interval. The selected Figure 3 and source record show the useful subject-level fact that 6/10 mice exceed the approximate +10 working threshold and none exceed −10 in the opposite direction; the main Results report only the sum. Monte Carlo rescoring addresses simulation noise, not sampling variability, fold-partition sensitivity, session drift, or transport to new mice.

**Consequence:** “Favoured among the tested implementations on held-out trials from these mice and sessions” is defensible. The exact aggregate should not read like a calibrated likelihood-ratio magnitude or population effect.

**Bounded remedy:** In the Abstract and Results, call 345.7 the difference in the registered held-out simulation-based objective (or clearly define “NLL score units”), report 6/10 above +10 and none below −10, and retain the within-mice/sessions scope. Do not imply a population test. If broader generalization is desired, add repeated split/session-blocked or leave-session-out sensitivity; it is not required if the current conditional scope is maintained.

### P1.3 The known legacy-input errors are disclosed but their quantified direction is not integrated into the gate claim

**Locations:** Results, `manuscript.md:69`, `:81`, and `:87-94`; Discussion, `:102`; Methods, `:124-128` and `:226-246`.

**Evidence:** The manuscript reports 15 invalid-duration exclusions and 48 historically control-labelled UCLA no-response pulse trials, with model overlays restricted to the unchanged common intersection. The underlying data and diagnostic reports quantify the consequence: affected pulse censoring is biased downward by as much as 1.7 percentage points in one mouse and control censoring upward by as much as 1.2 points, weakly favouring the old censoring gate; the temporal overlay omits the recovered rows. Source: `.agents/reports/2026-10-23-pulse-data-20261023T191030Z_fa8de8b.md` and `.agents/reports/2026-10-23-pulse-diagnostics-20261023T191030Z_fa8de8b.md`. The assignment-based behavioural effect uses corrected scheduled labels and is not affected in the same way.

**Consequence:** The errors do not plausibly manufacture the reported behavioural pulse effect and appear conservative for one gate component, but exact predictive-gate values remain conditional on a known defective historical input.

**Bounded remedy:** Add the direction and maximum quantified size of the censoring bias where the gates are interpreted, state explicitly that it weakly favours rather than causes gate failure, and keep the assignment-based effect separate. Either label corrected-input refitting as future work, as already proposed, or perform one versioned corrected-input sensitivity only if the authors want exact gate values to be treated as final.

### P1.4 The headline interval and Holm-adjusted p value do not belong to the same familywise confidence procedure

**Locations:** Abstract, `manuscript.md:7`; Results, `:61-67`; Methods, `:214-216`; Figure 4 legend, `:329-342`.

**Evidence:** The effect is reported with an ordinary 95% Student-t interval and a Holm-adjusted p value from a family of three. Methods correctly disclose that no additional correction was applied to the interval (`:216`), but the Abstract, Results and legend pair the two without calling the interval unadjusted.

**Consequence:** Readers can reasonably infer that the interval and adjusted p value express the same familywise error control, although they do not.

**Bounded remedy:** Label the interval “unadjusted 95% Student-t CI” wherever paired with the Holm p value. Alternatively, provide a multiplicity-compatible interval. The former is a reporting-only fix.

### P1.5 Small-sample uncertainty and the absence of a sample-size rationale need to qualify “reliably”

**Locations:** Results heading and text, `manuscript.md:59-71`; Discussion, `:98`; Methods placeholder, `:114`; estimator validation, `:220-224`; Figure 4A.

**Evidence:** The primary estimate uses 10 mice. The figure shows one negative mouse and marked between-mouse spread. The underlying behavioural report gives SD about 5.7 percentage points, 9/10 positive mice, and a wide 1.80–9.89 percentage-point t interval. The validation report estimates only 0.64 Holm-adjusted power for a 6-point effect under its generator and notes that its acceptable t-interval coverage assumes normal between-mouse heterogeneity and no session drift. The manuscript reports the validation design in Methods but leaves the sample-size rationale explicitly missing and does not carry this effect-specific sensitivity into the Results or Discussion.

**Consequence:** The directional assignment effect is supported, but its magnitude is imprecise and replication at the same n may miss an effect of this size. “Reliably redirected” overstates precision for an exploratory ten-mouse result.

**Bounded remedy:** Supply the actual sample-size rationale, or state that no prospective power calculation determined n. Add one concise sentence in Results or Discussion giving the observed between-mouse spread and the design-based 6-point Holm power, with its generator dependence. Prefer “shifted response direction” over “reliably redirected” unless reliability is explicitly defined.

### P1.6 Statistical reproducibility remains incomplete at two exact Methods locations

**Locations:** Rapid-forgetting implementation, `manuscript.md:172-178`; reproducibility and availability, `:250-273`.

**Evidence:** The leak is specified as 20–200 s⁻¹, but “nominal time constants 5-50” and “Euler dt=1” have no units; dimensional consistency implies milliseconds, but a reader should not infer this. The manuscript also retains `[MISSING: final manuscript-wide software lock; final Figure 1–5/S6 run commits and executable provenance; data/code repository identifiers, access conditions and release timing]` at `:273`. The integrity audit correctly treats this as an author/final-production omission rather than a fabricated fact.

**Consequence:** The rapid-forgetting candidate cannot be reproduced unambiguously from the paper, and the current manuscript is not independently executable from its availability statement.

**Bounded remedy:** Add the verified time units for the time constants and Euler step without guessing; then supply the final software lock, selected-run commits, repository identifiers, access conditions and release timing. If data cannot yet be public, state the concrete staged-release condition rather than leaving a generic placeholder.

## P2 — polish

### P2.1 Report Monte Carlo uncertainty or resolution with the sensitivity proportions

**Locations:** Results, `manuscript.md:91`; Methods, `:228` and `:246`; Supplementary Figure S6 legend, `:368-373`.

**Evidence:** Strategy and timing calibration use only 20 full-cohort datasets per generator/level. Counts such as 0/20 and 1/20 are correctly reported, but no binomial Monte Carlo interval or explicit 1/20 resolution appears in the manuscript. The underlying S5 report already notes this resolution.

**Bounded remedy:** Add a short statement that empirical resolution is 0.05 and give binomial Monte Carlo intervals (or an explicit qualitative bound) for the main 0/20 and 1/20 sensitivity estimates. This will preserve the correct conclusion that sensitivity is poor without implying exact zero power.

### P2.2 Round display values to scientific precision while preserving ledger exactness

**Locations:** Abstract, `manuscript.md:7`; Results, `:61`, `:69`, `:71`, `:83`, and `:87`; Methods and legends where the same values recur.

**Evidence:** Values such as 5.844356 percentage points, 0.01941029, and 0.295968634567205 logit exceed the precision supported by 10 mice, simulation error, and model-input uncertainty. The figure-manifest captions already demonstrate readable rounding (for example, 5.84 and 0.019) without breaking source traceability.

**Bounded remedy:** Use consistent publication rounding in prose and legends, retaining full machine precision in `numbers.csv` and source tables.

## Conclusions that are supported now

- Within the specified candidate set and score, held-out control trials from the same mice and sessions preferred the tested accumulator over the rapid-forgetting approximation.
- Randomized scheduled pulse direction shifted the mouse-level directional response contrast; the estimate is about 5.8 percentage points with substantial uncertainty across 10 mice.
- The original and failure-prompted gain-revised prediction pipelines failed their registered adequacy gates.
- The planned timing procedure had poor sensitivity under the tested generators and was appropriately not run; the data do not establish primacy, recency, flat weighting, or equivalence of strategies.
- The mechanism of pulse-transfer failure is unresolved across stimulus reconstruction, sensory transformation, decision dynamics, and response mapping.

## Conclusions requiring revision or additional analysis

- A statistically demonstrated difference in temporal *shape* between observed and predicted curves is not established by the current descriptive overlay.
- The 345.7 score difference is not a population effect or calibrated likelihood-ratio magnitude.
- Exact predictive-gate values are conditional on known legacy pulse-label and exclusion errors until corrected-input sensitivity/refitting is performed.

## Blockers and scope

- **Blocker to acceptance as written:** resolution of P1.1 by bounded language or direct paired inference.
- **Blockers to a submission-ready statistical record:** the missing sample-size rationale and the final software/data/code availability record (P1.5–P1.6).
- **Not blockers:** the integrity audit is PASS; no number mismatch, pseudoreplication, uncorrected central test family, false equivalence claim, or hidden execution of the stopped timing test was found.
- This report does not edit manuscript prose or ledgers, does not modify state, and does not approve or cross G5.
