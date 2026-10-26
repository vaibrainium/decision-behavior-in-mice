<!-- np-contract
stage: S4 ; section: methods ; agent: np-stats-reviewer ; version: r3
thesis: "Joint held-out prediction on control trials favoured the tested accumulator over a rapid-forgetting implementation, but randomized motion pulses exposed a failure of the tested model-and-input pipelines to generalize to transient strong evidence."
claims: C016, C017, C018
numbers: N001, N004, N005, N006, N009, N010, N016, N018, N022, N023, N027, N034, N036, N051, N052, N053, N054, N055, N056, N057, N058, N059, N060, N061, N062, N063, N064, N065, N066
sources: adelson1985spatiotemporal, bogacz2006physics, luken2025parameter, palmer2005effect, ratcliff2008diffusion, wiecki2013hddm
-->
# Final statistics criteria commitment: methods round 3

Sources used: locked spine, amended v3 outline/Methods brief, `np/reviews/methods/r2_stats.md`, `np/reviews/results/r2_stats.md`, decision D005 and `review-rubrics.md` (no v3 draft seen).

This is the human-authorized final bounded review. It adds no statistical criterion and permits no new analysis or claim. Methods passed round 2; every passed S1–S11 finding remains binding. Review only the D005 correction and regressions caused by it.

| ID | Frozen final criterion | PASS requires | REVISE/P0 if |
|---|---|---|---|
| F-M1 | Minimal reproducible secondary baseline | Define the supplementary `L1U1V1Z0G1` baseline as leak plus urgency with drift variability, no starting-point variability and the same fast-only guess form; state that it was fitted on controls under the documented input/objective/censoring/CV framework, then received the documented cross-validated mouse-specific pulse-gain revision with control parameters fixed. Identify it as supplementary and supporting only C007's original/revised gate record, not Figure 3 selection, C006's headline or a new mechanism claim. Existing implementation/settings may be cross-referenced rather than duplicated. | REVISE if a reader cannot identify the model, fitting population, shared/different components, gain revision or C007-only role. P0 if it becomes a newly selected model, independent confirmation or new claim. |
| F-M2 | Remove/recast incomplete hidden-coherence inference | Remove the two Wilcoxon inferential procedures and missing-W placeholder from the reported Methods path, or clearly recast the remaining hidden-coherence material as descriptive input characterization only. A retained pooled ratio must keep the historical-control-label, shared-model and scheduled-control-sensitivity caveats. Do not compute/export W, add a test, or imply population support. | REVISE if incomplete Wilcoxon reporting or a W placeholder remains. P0 if new inference is introduced or N011 is promoted to a population-wide conclusion. |
| F-M3 | Preserve the round-2 statistical pass | Preserve mouse-level group inference; nesting; scheduled assignment; supported-cell/equal-mouse weights; retained pre-onset/no-response outcomes; cutoff/censoring distinctions; held-out control comparison; recovery; pulse-gain split/seed limits; descriptive common-row timing; C009's two-mouse scope; Holm/pointwise language; stopping record; honest figure-level provenance/placeholders; and approved claim/source scope. | Apply the original r2 severity: P0 for pseudoreplication, leakage, outcome-conditioned primary inference, invented model–data test, uncorrected central multiplicity, false null/equivalence or fabricated provenance; P1 for incomplete reporting/reproducibility. |
| F-M4 | Token provenance and canonical counts | Every hard value is an existing ledger token used with its registered population/unit. N027/N034/N036 may enter only as registered secondary-gate outcomes. Budget compliance uses the canonical neuropaper body count, not shell whitespace counts; trimming must not remove statistical definitions or caveats. | P0 for invented/hard-coded values or new analysis. REVISE if the final count method is noncanonical or trimming causes a statistical regression. |

## Final decision rule

- PASS only if F-M1–F-M4 are fully met with no new P0/P1/P2 issue.
- REVISE for a correctable D005 or reporting regression using existing evidence.
- BLOCK only for an evidence conflict or genuinely unavoidable new human analysis. D005 explicitly authorizes removal/recast of the incomplete Wilcoxon inference, so rerunning it is out of scope.

