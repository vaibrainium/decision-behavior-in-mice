# Report: paper direction after the pulse and state analyses
Date: 2026-11-15   Agent: Codex   Commit: b63c9d9 (base; review/recent analyses uncommitted)
Plan: plans/2026-11-15-paper-direction.md

## Question
What paper should be built from the accumulated evidence, given the original accumulation-first argument, Neuron ambition and no further experiments?

## Summary
RECOMMENDATION: preserve task → control-model discrimination → pulse constraints. Completed matched recovery strengthens the control result and belongs in the main paper. Pulses constrain tested accumulation accounts; an exact accumulation mechanism, attention mechanism and population-wide requirement for drift variability remain unresolved. Assemble the manuscript around the existing results. A resolved mechanistic Neuron story is not established yet. This is author-directed scientific advice, not an editorial decision or a new manual gate.

## Findings
Evidence identifiers resolve to files in `dissemination/paper_direction_2026-11-15/evidence_index.json`. VERIFIED below means checked against existing audited outputs; no model fits or biological statistics were rerun this turn.

- VERIFIED — task/scope: principal cohort is 10 mice / 50 accepted sessions, with 25,493 model-input trials. Conclusions condition on selected trained animals/sessions and responded trials. Original chronology and excluded-row gaps are now audited. Sources: E01 `COMPLETED_RESULTS.md`, E10 `selection_audit.json`; original extraction/audit commands and data provenance linked there.
- VERIFIED — point 2: matched control fits favor accumulation over rapid-forgetting and extrema candidates, mainly through RT predictions. Completed paired recovery covers 500 fits on 100 fixed synthetic train/test datasets and separates relevant generating strategies at the recombined-cohort level within the tested parameter range. It is not missing; earlier review language is superseded. Recombined cohorts are not independent simulations. Source: E01 matched-control/recovery sections and linked tables/manifests.
- VERIFIED — directional perturbation: scheduled signed response contrast is 5.84 percentage points, mouse-level interval [1.80, 9.89], Holm-adjusted p = .0194. Responded-only contrasts estimate a different quantity. Source: E02 `independent_audit.json` / `independent_signed_effects.csv`, E10 for selection. Causal interpretation is bounded to eligible randomized cells and the stated selected-session outcome.
- VERIFIED — temporal interpretation: applying the same dilution/readout estimator to a no-leak bounded model also produces a late decline. This counters inferring intrinsic forgetting from the decline alone; it does not establish that mice have no leak. Source: E03 `RESULTS.md`, `data_bootstrap_summary.csv`, `summary_across_seeds.csv` and the simulation/estimator commands linked there.
- VERIFIED — no universal pulse-amplitude failure: several cohort-average model effects lie within data intervals. The sharper constraints are individual amplitudes and time courses, especially PSUIM6/7. Onset comparisons do not establish cohort primacy. Sources: E01, E03, E05 and linked bootstrap/onset tables.
- VERIFIED — choice/RT tradeoff is concentrated: in the matched onset-weight comparison, removing persistent additive drift variability improves held-out choice NLL by 49.29 but worsens RT NLL by 360.22, total cost 310.93. PSUIM7 supplies 280.17, about 90%, of that cost. This is not evidence that every mouse needs this variability. Source: E04 `RESULTS_AND_NEXT_MODEL.md`, `diagnostic_summary.json`, per-mouse and independent-seed tables. The older unmatched comparison changes additional components.
- VERIFIED — followups do not resolve the mechanism: variable postdecision delay does not solve the joint discrepancy; positive gain is a limited full-training feasibility result; baseline/history states improve future choices but state-specific pulse coefficients do not help consistently. External RT checks do not give a consistent attention interpretation. Sources: E06–E09, especially E09 final `assessment_v2`. These are two-mouse diagnostic pilots, not group mechanism evidence. Pilot mice have no late-pulse trials.

## Recommended argument and figures
Working title: **Transient motion pulses constrain models of evidence accumulation in mice.**

Central claim: **Control choices and response times favor accumulation over matched nonintegration alternatives; transient motion perturbations impose additional constraints on the temporal influence of evidence and reveal limitations of the best-scoring tested accounts.**

Preserve the author's three steps:
1. Mice perform the task: establish stimulus-guided choices, timing and analyzed population.
2. Accumulation is favored: show matched held-out control comparisons and completed recovery, with relative support bounded to the tested candidate set.
3. Pulses test the dynamics: directional effects and quantitative forward predictions constrain the accounts; they do not uniquely identify a memory time constant or establish attention/gain.

Proposed main figure argument:
- Figure 1: task, pulse assignment, selection/filter flow and individual choice/RT behavior.
- Figure 2: matched control-model predictions, held-out choice/RT decomposition and paired recovery.
- Figure 3: signed pulse effects and individual time courses with identical data/model estimators. Distinguish scheduled-response and response-conditioned estimands.
- Figure 4: what pulses add: matched variability ablations, joint choice/RT adequacy, the no-leak readout counterexample and full-cohort/dominant-mouse context. Label PSUIM6/7 as diagnostic examples, not the cohort.

Extensive model grids, HMM/history checks and delay/gain pilots are supporting material unless needed for a specific main claim. Organize the Results around the scientific argument rather than the sequence of models tried.

## Literature and Neuron assessment
- VERIFIED literature context: Stine et al. (2020), *Differentiating between integration and non-integration strategies in perceptual decision making*, studied humans and motivates matched alternatives/recovery. https://pubmed.ncbi.nlm.nih.gov/32338595/ ; https://doi.org/10.7554/eLife.55365 . It is not a mouse precedent.
- VERIFIED literature context: Chakravarty et al. (2025), *A cross-species framework for investigating perceptual evidence accumulation*, is a recent mouse/rat/human task comparator. Accessible record is an eLife reviewed preprint: https://doi.org/10.7554/eLife.105116 . Mouse performance/accumulation alone is insufficient novelty relative to this literature.
- Earlier verified pulse and serial-state references, including Huk/Shadlen and Ashwood, are indexed in E11. Pulse sensitivity or choice-state prediction alone does not establish a novel mechanism.
- JUDGMENT: the promising general question is whether a model's explanation of endogenous behavioral variability predicts sensitivity to controlled input perturbations. The present observations motivate this question; mismatch does not identify its biological solution. Population concentration and aggregate compatibility must remain visible.
- JUDGMENT: retain Neuron as the ambition, but current evidence has not established a resolved Neuron-level mechanism story. A compact validated explanation or a calibrated general constraint would strengthen the case. This does not imply that Neuron requires new recordings or that the experiment must be repeated. Publisher description checked: https://shop.elsevier.com/journals/neuron/0896-6273 . Direct Cell/ScienceDirect scope pages were inaccessible; no acceptance probability inferred.

## What did not work / directions not selected
- Attention/state switching as the headline: inconsistent mechanistic validation.
- Universal accumulator failure, universal drift variability, exact forgetting cutoff or robust primacy: contradicted or insufficiently supported.
- Repeating generic fits/recovery as if missing: extensive fits and corrected recovery already exist.
- Explaining the no-variability disadvantage as a slow-tail problem: the existing decomposition instead identifies central/fast correct RTs.
- Treating finite model failures as proof of structural nonidentifiability: not established.
- System `python` was absent when writing this report; used the existing `.venv/bin/python`, with no package changes.

## How to reproduce
No new model analysis was run. Follow E01–E11 in `dissemination/paper_direction_2026-11-15/evidence_index.json`. Original reports/manifests retain exact analysis commands, input hashes, fitted versions and environments. Base commit is given above; recent scripts/results remain uncommitted and should be archived together before submission.

Claim map: `dissemination/paper_direction_2026-11-15/claim_evidence.csv`. Structural validation:

```bash
.venv/bin/python .claude/skills/peer-review/scripts/validate_claim_evidence.py dissemination/paper_direction_2026-11-15/claim_evidence.csv --output dissemination/paper_direction_2026-11-15/claim_evidence_validation_v2.json
```

Validation checks declared structure/alignment, not evidence truth or manuscript merit. Initial validation retained; v2 more clearly marks the unvalidated gain-mechanism headline unsupported. All evidence IDs resolve locally. Inspected `reviewer_2026-11-12/reviewer_diagnostics.png` corresponding to the open PDF; the newer completed-results inventory supersedes older conclusions.

Procedural acknowledgement: repository peer-review and scientific-critical-thinking guidance informed this appraisal. Scientific Agent Skills citation verified: Kassis et al. (2026), arXiv preprint, https://doi.org/10.48550/arXiv.2609.00065 . Workflow attribution only, not neuroscience evidence. No unpublished content was placed in public web queries or sent to another external AI service.

## Caveats
This recommendation is not author adoption or locked manuscript scope. Most fits score pooled condition distributions rather than the exact pairing of each trial's motion energy and choice. Marginal prediction comparisons remain meaningful, but do not validate a trialwise neural algorithm. Fixed-model discrepancies are not calibrated class-wide rejections. Selection, nonresponse, schedules, diagnostic-mouse choice and simulation resolution limit inference. Newest exploratory mechanisms lack formal recovery.

## Open questions and concrete next steps
- [ ] Assemble the main figures and Results skeleton from completed outputs before expanding model search.
- [ ] If pursuing a stronger rejection/tradeoff claim, perform a focused uncertainty-aware adequacy comparison for a few existing finalists, retaining per-mouse and dominant-mouse sensitivity. A comprehensive near-optimal-parameter uncertainty analysis was not found among audited outputs; avoid repeating completed fits blindly.
- [ ] Keep a joint serial-bias/shared-pulse accumulator as an optional specific hypothesis. Choice-only HMM gains do not establish that it will solve the joint discrepancy.
- [ ] Reassess the Neuron advance from the assembled argument. Manuscript completion should not depend on another exploratory family giving a favorable result or on unavailable experiments.
