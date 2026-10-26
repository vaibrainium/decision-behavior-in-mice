# S4 midpoint: Methods, Results and figure legends passed

Date: 2026-10-25
Stage: S4 drafting midpoint (required author check; not a gate)

## Passed sections

- `np/drafts/methods/v3.md`: 3,361/3,400 canonical words; readable snapshot `np/checkpoints/S4_midpoint_methods.md`.
- `np/drafts/results/v3.md`: 2,763/2,850 canonical words; readable snapshot `np/checkpoints/S4_midpoint_results.md`.
- `np/drafts/figure_legends/v3.md`: 1,450/1,650 canonical words; readable snapshot `np/checkpoints/S4_midpoint_figure_legends.md`.

All three sections are `passed` in neuropaper state. Methods and Results received independent section and statistics review. After three rounds, the author approved three exact direct edits and waived a fourth formal review (D006); human-resolution PASS records document that exception.

## Results story for author verification

1. Ten mice and 50 mouse-sessions contributed choice, response-time and no-response constraints in the reaction-time random-dot-motion task.
2. Reconstructed motion energy makes the fitted input explicit but is not a frame-perfect display record or neural-latency measurement.
3. Joint held-out control prediction favoured the tested accumulator over the specified rapid-forgetting approximation by 345.7 NLL units; this is a relative model comparison, not unique proof of accumulation.
4. Randomized signed pulse assignment shifted response direction by 5.84 percentage points (95% CI 1.80–9.89; Holm-adjusted p=0.019), with cumulative response-associated divergence emerging mainly 0.5–2 s after logged onset.
5. The tested model-and-input pipelines predicted a different temporal pulse-response profile. The choice-versus-remaining-objective gain tradeoff is restricted to PSUIM6 and PSUIM7.
6. The original and gain-revised primary and secondary predictive gates failed; simulations had low strategy/timing sensitivity; the confirmatory timing test was not run. This is not a null result for primacy, recency or flat weighting.

## Methods boundaries for author verification

- Mouse is the group-inference unit; trial/cell/session counts are descriptive or within-mouse units.
- Scheduled assignment, pre-onset responses and no-response outcomes are retained for the pulse estimand.
- The legacy model-input exclusions/mislabels remain disclosed and unchanged; overlays use common rows.
- The primary tested accumulator and supplementary `L1U1V1Z0G1` gate baseline are defined separately and receive no unsupported mechanistic interpretation.
- Unknown animal, ethics, hardware, blinding, final software lock and repository facts remain `[MISSING]` rather than guessed.

## Automated checks

- Contracts: PASS.
- Claims and citations: 0 errors, 0 warnings.
- Number tokens: 0 errors, 0 warnings.
- Lint: 0 errors; expected `[MISSING]` warnings in Methods and provisional legends.
- Locked spine: PASS.
- Whitespace: PASS.

## Author question

Are the passed Results and Methods scientifically accurate representations of the experiment and analyses? Please identify any factual correction now. On confirmation, S4 continues to Discussion, then Introduction, then Title/Abstract.

