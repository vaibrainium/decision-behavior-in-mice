# Exploratory response-delay pilot

This analysis tests whether variation in response timing can reconcile joint choice/RT prediction with the sustained directional pulse effect. It uses existing data only and leaves historical fits and analyses intact.

## Model

For genuine decision-process trials, `RT = bound-crossing time + D`, with

`D = ndt * exp(ndt_sigma * Z - ndt_sigma**2 / 2)`, `Z ~ Normal(0,1)`.

`ndt` is the mean postdecision delay in seconds; `ndt_sigma` is the dimensionless log standard deviation, bounded from zero to 1.5. The standard deviation in seconds is `ndt * sqrt(exp(ndt_sigma**2) - 1)`. Zero spread gives the existing fixed-delay model exactly. The new model fixes persistent additive drift variability `sv` to zero; replacing `sv` with `ndt_sigma` keeps complexity equal to the matched drift-variability model. If `ndt` is zero, the spread parameter is unidentifiable.

Evidence mapping, pulse-stage weights, diffusion variance, bound, starting point, drift bias, fast guesses and all common parameter bounds follow the existing onset-weighted models. All common free parameters are refitted on the relevant training partition. The spread applies to genuine DDM responses; contaminant guesses retain their existing timing distribution. The minimum response floor (0.3 s), deadline (5 s), response-conditioned QMLE, nine RT bins, smoothing, and response-fraction guard are preserved. Consequently this is a matched timing-assumption comparison, not a test of a new sensory latency kernel.

The existing independent `unit_sv` normal draws are reused for the mutually exclusive delay-variability alternative. They are independent of diffusion and contaminant draws. The simulator rejects using the same draw for simultaneous nonzero drift and delay variability. Legacy source modules are unchanged.

## Design and optimization

PSUIM6 and PSUIM7, full data plus the original five stratified trial folds. A CV fit starts only from the corresponding CV training fits; full-data fits never initialize CV fits. Held-out outcomes and pulse summaries do not enter optimization or start selection.

The bounded multistart pilot screens at three simulation repetitions and refines at the original fifteen repetitions, using simulation seed 42. Both stages freely refit all common parameters. Each stage selects two separated starts and uses at most 350/600 Nelder–Mead evaluations per start. Numerical simplex convergence on a discretized simulation objective is not evidence of a global optimum. A separate, training-only broader-search check explores coupled timing and accumulation changes using 48 candidates and 20 differential-evolution generations at three repetitions, followed by two local refinements at fifteen repetitions. It preserves the first pilot fits.

Final scoring uses three independent simulation seeds and sixty repetitions per trial on the original held-out folds. The fixed and drift benchmarks are existing fits, rescored at the same seeds and precision. Comparisons generalize to trials within the same mice/sessions; they do not establish generalization to new sessions or mice. Simulation-seed variation quantifies numerical uncertainty, not biological or parameter uncertainty.

Pulse profiles use the out-of-fold simulated outcomes and the same coherence-matched, pulse-count-weighted estimators as the earlier pulse analyses. Positive and negative signs are shown separately. Observed-data intervals are pointwise 95% percentile intervals from 500 resamples of blocks of 50 modeled responded trials within each mouse/session. These are exploratory within-mouse intervals, not multiplicity-corrected group tests. No independent pulse likelihood is added to the choice/RT objective.

## Reproduction

From `/src`, using the existing `.venv` and processed inputs under `/mnt/data/processed/ddm`. Set `OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1` for the following commands. GPU IDs can be changed to suit availability.

```bash
CUDA_VISIBLE_DEVICES=0 .venv/bin/python -m scripts.ddm.fit_response_delay --fit --mice PSUIM6
CUDA_VISIBLE_DEVICES=1 .venv/bin/python -m scripts.ddm.fit_response_delay --fit --mice PSUIM7
CUDA_VISIBLE_DEVICES=0 .venv/bin/python -m scripts.ddm.check_response_delay_search --mouse PSUIM6
CUDA_VISIBLE_DEVICES=1 .venv/bin/python -m scripts.ddm.check_response_delay_search --mouse PSUIM7
.venv/bin/python -m scripts.ddm.assess_response_delay --prepare
CUDA_VISIBLE_DEVICES=0 .venv/bin/python -m scripts.ddm.fit_response_delay --score --mice PSUIM6
CUDA_VISIBLE_DEVICES=1 .venv/bin/python -m scripts.ddm.fit_response_delay --score --mice PSUIM7
.venv/bin/python -m scripts.ddm.assess_response_delay --collect --plot
```

Contract checks:

```bash
NUMBA_NUM_THREADS=1 .venv/bin/python -m tests.test_response_delay
.venv/bin/python -m tests.test_fit_checkpoint
```

Fits and resumable best-point/stage checkpoints: `/mnt/data/processed/ddm/fits_response_delay_2026-11-14/`. Checkpoints preserve completed stages and the best evaluated candidate; an interrupted local stage restarts around that candidate rather than restoring the exact simplex trajectory. Source/input hashes, package versions and optimizer settings are saved in the manifests. Independent-search results carry `_search_check` suffixes. Existing files are not overwritten by compatible reruns.

## Interpretation limits

This pilot cannot uniquely identify a motor, sensory, decision or engagement mechanism. Response-conditioned pulse profiles are descriptive and affected by survival/selection. Model recovery, fitted-parameter uncertainty, optimization robustness, and full-cohort validation would be required before a publication-level mechanistic conclusion. A failed delay pilot motivates a separately evaluated positive-gain-variability account; it does not establish that gain variability is correct.
