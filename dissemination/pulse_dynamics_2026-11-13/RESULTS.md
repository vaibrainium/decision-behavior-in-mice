# What the pulse trials establish about accumulation dynamics

Date: November 13, 2026. Source repository commit: `b63c9d919edc85e48446be48a8399ba6304b8df0`; new scripts and outputs are uncommitted.

The pulse results support a sustained directional influence followed by a later reduction. They also distinguish the predictions of existing fitted accumulators: the best joint choice/RT model predicts a weaker early influence and a late reversal, while models without persistent drift variability avoid much of the reversal and approach the behavioral summaries more closely. The apparent late loss does not uniquely identify forgetting, because a bounded accumulator with zero leakage also produces a decline under the same analysis.

This makes point three a quantitative test of accumulation models. It does not yet identify one intrinsic memory time constant or one complete account of decision dynamics.

## The comparison figure

[View the standalone figure](pulse_dynamics_comparison.pdf).

- **Panel A:** The historical directional/shared correctness estimator, applied to data and model simulations. The directional component measures influence toward the pulse, controlling for baseline coherence and mouse. Black intervals are the existing mouse-bootstrap intervals; model curves show two independent simulation seeds.
- **Panel B:** The coherence-equivalent pulse effect multiplied by mean RT, using the historical dilution estimator. The pre-effect 0.1–0.3 s bin is omitted here because its coherence slope is unstable in finite simulated datasets. It remains visible as a directional coefficient in panel A.
- **Panel C:** Early and late influence summaries for every finalist. Data intervals come from a new 600-resample mouse bootstrap. Model points are fixed-parameter predictions averaged across two seeds; they are not parameter confidence intervals.
- **Panel D:** Late/early ratios with and without baseline coherences above 36%. The short horizontal ranges show changes between simulation seeds. Ratios describe the readout; a ratio below one is not uniquely a leakage signature.

## The same estimator now connects behavior and model predictions

The grouped-binomial implementation reproduces the historical trial identities and regression estimates. Maximum absolute differences are below 1.3e-13 for gamma times T, and below 9e-15 for the directional/shared coefficients. The readout uses 19,313 observed trials from 19,579 eligible schedules after the historical response-related restrictions.

The simulation reuses the fitted decision-model parameters, reconstructed motion energy, and logged pulse schedules. There are nine fitted configurations and one fixed-parameter sv-zero ablation, each evaluated in all ten mice with 30 repetitions at each of two seeds. This produces 60 simulated cohort datasets per configuration. Independent mouse seeds avoid sharing the same noise sequence between animals. Simulated censoring, response floors, fast guesses, and post-pulse response selection are retained. No decision-model parameters were refitted; the descriptive readout regressions were fitted identically to observed and simulated responses.

The historical analysis conditions on responding, excludes late pulse-onset strata, uses symmetric scheduled cells, and removes responses before the actual or virtual pulse ends. Those conventions are reproduced to make the comparison exact. They are not a new endorsement of every historical exclusion. The simulation input pool consists of empirical responded trials, as in the existing fits; this analysis does not model the experimental population excluded by that conditioning.

Sources: `preparation_checks.json`, `data_readouts.csv`, `all_readouts.csv`, `coverage_*_r30.csv`, and the cache fingerprints. Fitted-model and input paths are recorded in each cache record. The simulation implementation is unchanged in `src/ddm/`.

## Observed influence persists across the early bins and then declines

Let gamma denote the pulse's effect in equivalent baseline-coherence units, and T the mean RT from motion onset. The historical simple-retention benchmark predicts an approximately constant gamma times T if continued stimulus evidence merely dilutes a fixed pulse contribution.

The observed early summary K is the unweighted mean of gamma times T in the 0.3–0.6, 0.6–0.9, and 0.9–1.2 s pulse-to-response bins. The late summary is the unweighted mean in the 1.2–1.5, 1.5–2.1, and 2.1–5 s bins. These are averages of bin estimates, not time-integrated quantities or trial-count-weighted window effects.

| Quantity | All baseline coherences | Baseline coherence magnitude at most 36% |
|---|---:|---:|
| Early K, percentage coherence seconds | 15.15 | 15.60 |
| Mouse-bootstrap 95% interval for K | 11.78–17.75 | 9.23–17.79 |
| Late summary, percentage coherence seconds | 2.29 | 2.33 |
| Mouse-bootstrap 95% interval for late summary | -4.01–8.23 | -4.15–8.41 |
| Late minus early | -12.86 | -13.27 |
| Mouse-bootstrap 95% interval for that difference | -19.78 to -4.08 | -18.57 to -2.12 |
| Late/early point ratio | 0.151 | 0.149 |

Thus, the later reduction survives removal of the ±100% baseline trials. Pulses themselves remain strong; this sensitivity changes baseline coherence, not pulse strength. The late effect is imprecise and is not established as positive. The three early point estimates are approximately flat, but their flatness is not proven: the bootstrap interval for the last-minus-first early bin spans -15.47 to 6.01 percentage coherence seconds. Do not turn that plateau description into an equivalence claim.

The new intervals use 600 successful resamples of mice and a different random seed from the historical 300-resample analysis. They therefore differ from the earlier reported intervals. All slopes used in these early/late summaries were positive in every successful data bootstrap. The low-coherence analysis provides a sensitivity check rather than a second independent discovery.

Sources: `data_readouts{,_low_coherence}.csv`, `data_bootstrap_intervals.csv`, `data_bootstrap_summary.csv`, `data_bootstrap_readouts.csv`. These intervals are exploratory percentile intervals; no new family of significance tests is claimed.

## Existing model configurations make substantially different predictions

Values below average the pooled readouts over the two simulation seeds. All entries are percentage coherence seconds except the ratio. They are conditional on the existing fitted parameters.

| Configuration | Early K | Late summary | Late/early ratio |
|---|---:|---:|---:|
| Observed data | 15.15 | 2.29 | 0.15 |
| Control-trained integrator | 5.63 | -5.14 | -0.91 |
| Joint integrator with sv | 5.89 | -6.00 | -1.02 |
| Joint integrator without sv | 7.51 | 2.14 | 0.29 |
| Power input plus leak and urgency | 6.05 | -10.53 | -1.74 |
| Normalized input plus leak | 7.17 | -5.74 | -0.80 |
| Pulse-only linear leak | 7.60 | -9.31 | -1.22 |
| Pulse-only normalized urgency gating without sv | 9.96 | -0.38 | -0.04 |
| Joint integrator with sv set to zero, other parameters fixed | 7.32 | 4.16 | 0.57 |
| Onset-specific pulse weights with sv | 7.40 | -6.20 | -0.84 |
| Onset-specific pulse weights without sv | 11.69 | 3.40 | 0.29 |

The best joint-likelihood model—power input plus leak and urgency—does not reproduce the sustained observed readout at its fitted parameters. For example, the observed gamma times T at 0.9–1.2 s is 14.81; that model predicts about -0.46. The onset-specific no-sv weight model predicts about 7.00, closer but still lower. The data's new mouse-bootstrap interval for that bin is 8.89–18.66 in the all-coherence analysis and 7.45–18.73 in the restricted analysis. These are descriptive predictive discrepancies, not calibrated model-rejection tests.

Free onset weights without sv come closer to the early and late aggregate summaries. They must not be described as failing every pulse statistic. Their early K is near the lower end of the observed interval, with seed estimates 11.48 and 11.91; their late summary is inside the data interval. Conversely, they retain a less sustained time course and do not explain the individual-mouse heterogeneity documented in the earlier results. Aggregate compatibility does not settle full model adequacy.

Sources: `summary_across_seeds.csv`, `all_readouts.csv`, `conditional_prediction_intervals.csv`, and the earlier per-mouse outputs `dissemination/figures/qc/pulse_joint_signatures_2026-11-12_pw_windows.csv` and `pulse_effect_bootstrap_2026-11-12_pw_data.csv`.

## The late decline does not measure an intrinsic forgetting time

The fitted no-sv integrator has zero leak, zero urgency slope, and zero drift variability in every mouse. Its evidence accumulator retains all input increments until bound crossing. Nevertheless, gamma times T falls from an early summary of 7.51 to a late summary of 2.14. The corresponding ratio, 0.29, is inside the data bootstrap ratio interval of -0.27 to 0.65.

This is a constructive counterexample to identifying forgetting from the readout alone. The complete model includes absorbing decision bounds, a response-time mapping, and fast guesses; selection of responses can produce a declining conditional pulse contrast while the accumulator itself has no leakage. This example does not establish that mice use this particular model, which underpredicts early influence and scores worse overall.

Similarly, setting sv to zero at fixed joint-fit parameters reduces the reversal without changing the leakage term. Together with the earlier counterfactual analysis, this localizes the reversal to the consequences of persistent drift variability within the tested pipelines. It does not establish that biological trial-to-trial variability is absent.

## The strongest point three result is a joint constraint

Models that approach the pulse behavior need to explain ordinary choices and response times as well. In the existing rescored joint comparison, the onset-specific no-sv weight model costs 503.71 held-out NLL and 907.10 BIC relative to power plus leak and urgency. The full-data rescored decomposition gives it a slightly better choice term—14,838.77 versus 14,848.22—but a worse RT term—55,511.76 versus 54,995.66. Those terms concern the combined trial population; the pulse-specific choice/RT tradeoff is also documented in the earlier analyses. The new readout does not introduce arbitrary reweighting of choices versus RTs.

The evidence therefore constrains the combination of transient evidence sensitivity, its temporal expression, and the source of RT variability. It does not currently select a unique leak rate, urgency process, or memory time constant. A history/state account or temporally evolving variability account remains a possible future explanation, not an inferred result of this comparison.

Source for score differences: `dissemination/figures/qc/model_ic_summary_2026-11-12_rescored.csv`. Those are existing predictive comparisons; the new pooled readout is an additional characterization of their predictions, not independent validation data.

## Proposed Results paragraph

Brief motion pulses exerted a directional influence on choices extending through responses made 0.3–1.2 s after pulse onset. A coherence-equivalent readout adjusted for dilution declined in later responses, and this pattern persisted when high baseline coherences were excluded. Applying identical analyses to existing fitted models revealed a tension between joint predictive fit and the temporal influence of transient evidence: the best joint choice/RT models predicted weaker early influence and a late reversal, whereas some variants without persistent drift variability approached the pulse summaries but incurred poorer RT fit in matched joint comparisons. A bounded integrator with no leakage also produced a declining dilution-adjusted readout, demonstrating that the behavioral decline does not uniquely identify forgetting. These results constrain accounts of accumulation dynamics beyond relative control-trial model support, while leaving the precise source of the discrepancy unresolved.

## Reproduction and limitations

Run from `/src`, with the existing environment. Commands write only into this dated output directory and its ignored cache.

```bash
OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 .venv/bin/python -m scripts.ddm.pulse_dynamics_bridge --prepare
CUDA_VISIBLE_DEVICES=0 OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 .venv/bin/python -m scripts.ddm.pulse_dynamics_bridge --simulate --seed 0
CUDA_VISIBLE_DEVICES=0 OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 .venv/bin/python -m scripts.ddm.pulse_dynamics_bridge --simulate --seed 1
CUDA_VISIBLE_DEVICES=0 OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 .venv/bin/python -m scripts.ddm.pulse_dynamics_sensitivity --simulate-extra --seed 0
CUDA_VISIBLE_DEVICES=0 OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 .venv/bin/python -m scripts.ddm.pulse_dynamics_sensitivity --simulate-extra --seed 1
OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 .venv/bin/python -m scripts.ddm.pulse_dynamics_sensitivity --analyze-extra
OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 .venv/bin/python -m scripts.ddm.pulse_dynamics_sensitivity --bootstrap 600
OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 .venv/bin/python -m scripts.ddm.plot_pulse_dynamics_bridge
```

Model parameters and experimental data were not changed. Model uncertainty intervals in `conditional_prediction_intervals.csv` describe finite simulated datasets at fixed parameters; they do not propagate fitting uncertainty. Sixty simulated datasets per configuration provide approximate predictive quantiles. The new data intervals resample mice but do not redo session selection or refit decision models. Pulse-trained configurations are evaluated retrospectively on the stimulus population used for fitting. The pooled estimator has mouse intercepts and common readout coefficients; it does not give each mouse equal influence. Apparatus, cohort, and pulse schedule remain confounded.

The next scientific choice is whether to pursue one compact explanation that reconciles the pulse and RT constraints, or report these constraints as the endpoint of point three. The current results support neither an exact 1.2 s memory cutoff nor a general rejection of accumulation.
