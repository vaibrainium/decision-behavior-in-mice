# Variable response delay does not resolve the pulse/RT tradeoff in this pilot

Date: 2026-11-14. Repository baseline: `b63c9d9` (see `integrity_audit.json` for the full checked commit). New code and outputs are uncommitted. Exploratory, existing data only.

## Scientific conclusion

Replacing persistent additive drift variability with an independent, mean-preserving lognormal postdecision delay did not materially improve prediction. The fitted delay spread is essentially zero in both full-data fits and almost all CV fits. A broader training-only search also returned near-zero spread. The new model retains the no-sv model's substantial PSUIM7 RT disadvantage and continues to underpredict the early pulse effect in both selected mice.

This result does not establish that response timing is fixed, nor that persistent drift variability is the correct mechanism. It shows that this particular timing alternative, under the tested bounds and bounded optimization, does not reconcile the constraints. The point-3 modeling problem remains open.

[Diagnostic comparison](response_delay_pilot.pdf). [Model, design and commands](README.md).

## What was implemented

`src/ddm/response_delay.py` adds `D = ndt * exp(ndt_sigma * Z - ndt_sigma**2 / 2)` after bound crossing. `ndt` remains the mean in seconds; `ndt_sigma` is the log standard deviation, bounded [0, 1.5]. It replaces sv; all other components and common bounds follow the existing onset-weighted linear-input integrator. Guesses retain their existing timing distribution. The new delay does not alter preselection decision choices; the deadline can alter observed response/choice proportions.

The matched drift and delay models each have 11 free parameters for these mice; the fixed-delay no-sv model has 10. Common parameters were refitted separately on the full data and each original training fold. Existing fixed/sv fits initialize only their corresponding split. No held-out score or pulse summary selects parameters or starts.

Twelve new fits were completed: full data and five CV folds for each mouse. Full-data training sizes are 5,843 trials in PSUIM6 and 6,835 in PSUIM7. Independent broader-search checks were run on the full-data training sets only, with separate output files. The first search is a bounded multistart local pilot; the broader check is also finite and does not certify global optimality. Details and numerical convergence status are preserved in each fit.

Sources: `fit_parameters_and_provenance.csv`; new fits and `_search_check.pkl` files under `/mnt/data/processed/ddm/fits_response_delay_2026-11-14/`; `fit_PSUIM*.log`, `search_PSUIM*.log`, and manifests here.

## Held-out prediction

Each original held-out fold was scored with 60 simulation repetitions at seeds 12345, 23456 and 34567. The table sums the five folds per mouse and averages the seed-specific differences. Positive values mean worse prediction than the matched drift-variability model.

| Mouse | Fixed delay: total NLL difference | Variable delay: total difference | Variable delay: choice term | Variable delay: RT term |
|---|---:|---:|---:|---:|
| PSUIM6 | +9.12 | +6.22 | −14.69 | +20.92 |
| PSUIM7 | +256.10 | +255.85 | −20.15 | +276.00 |

Relative to the fixed-delay no-sv model, variable delay improves mean held-out NLL by only 2.89 units in PSUIM6 and 0.25 in PSUIM7. PSUIM6's delay-versus-drift total ranges from −12.00 to +18.14 across simulation seeds: its small ranking difference remains numerically unresolved. PSUIM7's disadvantage is stable, ranging from +247.20 to +266.23. These ranges measure simulation noise, not biological uncertainty or confidence intervals for model preference.

The full-data delay spread is about 0.00000024 s in PSUIM6 and zero in PSUIM7. The largest CV delay SD is about 0.028 s, in PSUIM6 cv0; every PSUIM7 CV delay SD is below 0.0001 s. The near-zero solutions explain why the new and fixed-delay prediction curves overlap.

Sources: `heldout_scores_by_seed.csv`, `heldout_differences_from_drift.csv`, `heldout_difference_summary.csv`, `fit_parameters_and_provenance.csv`. Reproduce with the scoring and collection commands in README.

## Pulse predictions remain inadequate

The estimator matches each pulse-sign/coherence cell to controls, then averages using pulse counts. All model values below come from **out-of-fold** predictions on symmetric cells with baseline coherence magnitude at most 36%. The early window is 0.3–1.2 s after actual or pseudo-onset. Data intervals are pointwise within-mouse 95% intervals from 500 resamples of blocks of 50 modeled responded trials within sessions; they are not corrected population tests.

| Mouse | Observed early pulse effect, pp [block CI] | Drift model | Fixed-delay no-sv model | Variable-delay model |
|---|---:|---:|---:|---:|
| PSUIM6 | 15.50 [12.61, 18.20] | 6.01 | 7.16 | 7.15 |
| PSUIM7 | 13.48 [11.45, 15.59] | 3.67 | 4.82 | 4.84 |

Variable delay does not restore the sustained early pulse response. Positive- and negative-pulse profiles are shown separately in the figure; coherence-specific pulse/control probabilities are saved as source tables. Both early observed signs are positive in the pointwise block intervals, but this is not a corrected test of multiple time bins or a causal interpretation of response-conditioned subgroups.

Out-of-fold values differ from earlier full-data signatures. For example, PSUIM7's fixed-delay full-data early pulse weight is 2.11, whereas its CV weights range from about 1.00 to 1.65. Thus the earlier full-fit prediction around 6.5 pp and the present out-of-fold prediction of 4.82 pp have different parameter/generalization targets. Do not substitute one for the other.

Sources: `data_pulse_window.csv`, `data_pulse_profile.csv`, `model_pulse_window.csv`, `model_pulse_profile.csv`, `data_pulse_coherence_cells.csv`, `model_pulse_coherence_cells.csv`; fold weights in `fit_parameters_and_provenance.csv`.

## Verification and limits

Verified: CPU/CUDA scientific contract tests; exact zero-spread reproduction of the original stored cv0 likelihood in each mouse; unchanged preselection decision choices and contaminant guesses; valid floor/deadline mapping; deterministic draws; positive delay and correct distribution moments; original fitting checkpoint tests. The pulse estimator matches the historical implementation, and weighted bootstrap contrasts were independently checked against literal trial resampling.

The final audit checks all 90 score records, containing 6,846,120 simulated outcomes. Every outcome is aligned to its held-out input and condition; fit/scoring source hashes match the current code; no fitted delay model lost its nested fixed-delay training solution; drift/delay parameter counts match. Choice plus RT terms reconstruct NLL to a maximum error of approximately 2.3e-12. The audit records hashes for source tables and figure exports.

These checks establish implementation integrity, not model adequacy. The two mice were selected because they are informative diagnostic cases. No group test, full-cohort claim, recovery study, or fitted-parameter interval is supplied. Cross-validation holds out trials from the same sessions, not sessions or new animals. Simulated nonresponses are recorded but the likelihood remains conditional on a response, matching the existing comparison. Models do not explain the observed frequency of nonresponses from a complete unselected trial population.

This independent trial-delay model does not test session-specific timing, variable sensory-onset latency, or dependencies between response delay and decision state. Existing descriptive high-coherence session timing shifts remain relevant, but do not identify motor latency; their source table is `../pulse_rt_tradeoff_2026-11-13/high_coherence_correct_rt_by_session.csv`.

What needed correction: an initial pulse validation used a similarly named reference estimator with fraction rather than percentage-point units; the validation import was corrected and numerical agreement verified. The incomplete table is preserved with a `validation_pending` suffix. The first assessment collection also dropped a needed row identifier when indexing metadata; this was repaired before any final score/prediction tables were written. Neither issue changed fitted parameters or likelihood scores. The errors and successful reruns are retained in the logs.

## Next modeling decision

Do not expand this delay model to the full cohort or interpret its near-zero spread as proof of fixed motor time. The next focused comparison should replace additive signed drift variation with **positive evidence-gain variability**:

`drift(t) = drift_gain * G * evidence(t) + drift_offset`, with positive mean-one G and one spread parameter.

This varies sensitivity to the whole evidence stream, including pulses, while preserving the direction of its contribution. It could produce different coherence/RT/pulse relationships from a persistent signed offset; this is a hypothesis, not a demonstrated explanation. Keep the same matched components and parameter count, refit common parameters on training folds only, and require improvement in absolute RT and signed pulse prediction. Test session dependence/history and establish recovery/parameter uncertainty before mechanistic interpretation. No gain-variability fits were launched in this pilot.
