# Plan for testing pulse dynamics with the existing fitted models

Status: done
Date: November 13, 2026

## Goal

Determine which aspects of the observed pulse persistence and late decline are explained by the existing fitted accumulators, using the same correctness and dilution estimators for data and simulations. Produce a figure and evidence-matched point-three narrative. All analyses are exploratory, use existing experimental data, and keep fitted parameters fixed.

## Model comparisons

Use the control-trained linear accumulator, the joint linear accumulator with and without drift variability, the best joint power-law leak/urgency and normalization/leak fits, the best pulse-only BIC and held-out families, and a fixed-parameter sv-zero counterfactual. Model selection follows the completed-results tables rather than these new plots.

## Steps

- [x] Reproduce the historical pooled dilution and directional/shared estimates with a computationally efficient grouped-binomial estimator and exact trial selection.
- [x] Simulate the existing finalist fits on the same stimulus schedules, retaining trial and repetition identity and censoring metadata; benchmark before the full run.
- [x] Apply identical selection, binning, correctness, directional/shared, and dilution estimators to data and simulations.
- [x] Check a second simulation seed and a low-coherence sensitivity; distinguish simulation sampling variation from fitted-parameter uncertainty.
- [x] Produce source tables and a standalone figure; decide which point-three claims survive bounded selection and which remain unidentified.
- [x] Record provenance, numerical checks, results, limitations, and the proposed manuscript statement.

## Scope

No new experiments, model refits, package installations, cluster jobs, or changes to raw data. Historical output files remain intact. Primary analyses reproduce the existing response-conditioned estimand; they do not turn it into a direct measurement of latent memory. Fitted-parameter uncertainty is not estimated by repeated simulations at fixed fitted parameters.

## Log

- November 13: No suitable raw simulation cache was found in the inspected repository, processed outputs, or temporary directory. Existing fitted parameters and the public simulator will be reused.

- November 13: Historical trial identities and both regression readouts reproduce to numerical precision (maximum gamma-times-T difference below 1.3e-13). The readout includes 19,313 trials from 19,579 eligible schedules after response-based restrictions. Both GPUs are already occupied, so simulation is benchmarked and run conservatively on one device.

- November 13: Eight existing finalist/ablation parameter sets were simulated for all ten mice with 30 repetitions at each of two seeds. The first seed shows a late decline even in the fitted no-leak, no-sv integrator, so gamma-times-T decline cannot uniquely identify forgetting. Independent-seed readouts and low-coherence sensitivity are being checked before interpretation.

- November 13: Added the two already-fitted onset-specific pulse-weight families to avoid omitting the strongest flexible-pulse alternatives from the new readout. No parameters were refitted. Added a 600-resample mouse bootstrap for early/late summaries; the low-coherence point estimates closely match the all-coherence data.

- November 13: Completed ten configurations, two seeds, thirty simulated datasets per seed, six hundred mouse-bootstrap resamples per scope, and the baseline-coherence sensitivity. All 8,400 replicate-bin readouts succeeded. Fixed-parameter checks and source reproduction passed; results and proposed manuscript wording are in RESULTS.md. The declining readout is not specific to forgetting.
