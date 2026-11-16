# Plan: decide the publication direction from the accumulated evidence
Status: done
Created: 2026-11-15 by Codex
Related reports: ../reports/2026-11-15-paper-direction.md; ../reports/2026-11-15-nhp-pulse-hmm-pilot.md; ../reports/2026-11-14-history-state-gain.md

## Goal
Give the author a clear paper recommendation, preserving the original three-part logic where supported. Identify a defensible current central claim, its novelty/Neuron limitations, a figure-level argument and only the remaining analyses needed to support that argument.

## Context
User wants an existing-data Neuron submission, no additional experiments and no inherited manual scientific gates. Extensive control/pulse model fits, paired recovery, predictive checks, literature review, delay/gain and serial-state analyses already exist. Latest pulse-state pilot supports changing baseline/history but not state-specific pulse weights consistently.

## Assumptions
- This is author-requested strategy/critical appraisal of their own work, not an assigned confidential journal review or an editorial decision.
- Preserve completed results and distinguish group evidence from two-mouse diagnostic pilots, and response-conditioned descriptions from causal temporal kernels.
- No new fits, installations, submissions, uploads of unpublished material or changes to old manuscript/protocol files during this decision review.

## Steps
- [x] 1. Review the completed-result inventory, central comparisons/recovery and recent pilots; inspect the current reviewer figure.
- [x] 2. Reconcile the original three claims with current evidence, close primary literature comparators and current Neuron scope/author guidance.
- [x] 3. Choose a paper direction, figure argument, claim limits and a short publication-relevant remaining-work list; record alternatives not selected.
- [x] 4. Save a factual decision report, update STATUS and explain the recommendation clearly to the author.

## Out of scope
Another broad model search, new experiments, journal submission, or treating author-directed strategy advice as an actual peer-review/editorial verdict.

## Log
- 2026-11-15: Recommendation: keep the author's accumulation-first three-step logic; make pulse constraints the main mechanistic test, with the exact mechanism unresolved. Attention/HMM/gain are diagnostic/supporting material. Retain completed control recovery as main evidence. Current cohort-average compatibility and the PSUIM7-dominated RT gap preclude universal failure/noise claims. Neuron readiness is an advisory scientific judgment, not a formal editorial criterion or requirement for new recordings.
- 2026-11-15: Checked primary comparators (Stine 2020 humans; Chakravarty 2025 cross-species reviewed preprint) and publisher scope/author-AI guidance using public-only queries. Cell/ScienceDirect direct scope pages returned 403; publisher's Neuron description was accessible. No unpublished material sent to search services. Formal assigned-review intake is outside this author-owned strategy task; using critical-appraisal/claim-evidence guidance without implying a journal invitation or editorial verdict.
- 2026-11-15: Evidence review confirms completed matched recovery (500 fits/100 fixed datasets), relative accumulation support and a robust signed pulse influence. It also confirms that a no-leak model can produce late readout decay, several cohort-average pulse predictions are compatible with data, and about 90% of one matched RT-score tradeoff is PSUIM7. Thus no universal model-failure or uniquely identified forgetting/attention claim. Author-directed strategy advice uses critical-thinking/claim-evidence guidance; no assigned-journal review, editor report or formal editorial verdict is being produced.
- 2026-11-15: User requested a conversation-wide publication decision after the completed NHP pulse-HMM pilot. Reading evidence and reviewer/critical-thinking guidance; no new analysis/model fitting planned in this turn.
- 2026-11-15: Completed report ../reports/2026-11-15-paper-direction.md, evidence index and claim map. Local schema validation v2 passes with explicitly recorded unsupported claims; cross-references checked. No new model fits or statistical results. Recommendation awaits author adoption; old plans/gates not reactivated. System python was unavailable; used existing .venv/bin/python.
