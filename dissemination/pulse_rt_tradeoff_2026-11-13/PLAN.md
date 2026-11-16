# Diagnose the pulse and response time tradeoff

Status: done
Date: November 13, 2026

## Goal

Locate the response-time features that favor the power-law leak/urgency model over the onset-specific pulse-weight model without drift variability. Use the result to choose one targeted modeling hypothesis while preserving the joint choice/RT objective.

## Steps

- [x] Reproduce held-out scores for both models on the original five folds, with the original simulation seed and repetitions.
- [x] Decompose scores by mouse, baseline coherence, scheduled pulse, correctness and RT quantile, checking exact reconstruction of the objective.
- [x] Check dependence on dominant mice and simulation noise in the largest contributions.
- [x] Produce a diagnostic figure and an evidence-based proposal for the next model comparison.

## Scope

Existing data and fitted parameters only. No model refits, new experiments, package changes, cluster jobs or modification of earlier outputs. These diagnostics are exploratory and cannot by themselves identify the biological source of a model's predictive advantage.

- November 13: Added the matched onset-weight pair with/without sv to separate that component from changes in input mapping, leak and urgency. The PSUIM7 cv0 pilot exactly reproduces all three stored test likelihoods.

- November 13: All 150 original held-out scores reproduced exactly. The matched sv gap is concentrated in PSUIM7, correct high-coherence responses, and central RT quantiles; its direction survives the second seed in PSUIM7. Completed report and targeted model hypotheses are in RESULTS_AND_NEXT_MODEL.md. No model refits were launched.
