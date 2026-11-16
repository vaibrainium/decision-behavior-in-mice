# NHP-fork pulse-state pilot

**The installed fork works, and state models predict choices better than a static GLM. Allowing pulse weights themselves to change between states adds no consistent predictive benefit in this two-mouse pilot.** This does not resolve the original joint pulse/RT mismatch or establish attention.

## Completed setup and model

The user authorized installation. SSM is installed at `/mnt/data/venvs/nhp-glmhmm-2026-11-15`, Python 3.10.12, from `vaibrainium/ssm` commit `a109af369797d852904fd9496f3532524de8f15a`. Exact resolved dependencies are in `environment_freeze.txt`. The original DDM environment remains on NumPy 1.26.4.

The system Python lacked `ensurepip`; its isolated interpreter was usable, and the existing `uv` installed the pinned packages without a system-package installation. The fork built successfully. Installed-runtime checks passed for Git provenance, masks, class-weight sign, log-transition parameters, pre-current-choice state filtering and the EM interface (`ssm_smoke.log`).

Per the latest user selection, the **primary inputs are six physical pulse direction × onset-stage indicators**, with controls as reference. Congruency is a nonzero-coherence accuracy view. Zero-coherence trials remain in model fitting. The pilot uses PSUIM6/7 and the original selected/responded population, preserving excluded logged rows as masked observations.

Three models share the same nominal-coherence, previous-choice/outcome/RT and nuisance inputs:

| Model | Baseline/history coefficients | Pulse coefficients |
|---|---|---|
| Static GLM | One set | One set |
| Shared-pulse HMM | Two state-specific sets | Shared across states |
| Free-pulse HMM | Two state-specific sets | State-specific |

Session offsets and within-session position terms are shared across states. The NHP fork supplies input-driven likelihoods, masking, forward/backward and EM. A tested observation subclass adds exact parameter-sharing constraints and a Gaussian prior on unique parameters; it also provides a stricter binary M-step for both HMM candidates. No fork source was patched. Numerical gradient/Hessian, independent-optimizer, sharing and masking checks passed (`emission_tests.log`). Stored SSM weights favor class 0; reported coefficients convert to right-choice log odds.

PSUIM6/7 have **no late-stage pulses** under the existing onset strata. Their early/middle scored counts are 580/563/582/552 and 702/672/668/698 for left-early/right-early/left-middle/right-middle. The six-type template is retained, but late coefficients are **not estimable**, shown as missing rather than inferred zero.

## Predictive design and optimization

First 20% of each session trains inner fits; next 20% selects each model's prior SD from 1, 2, 5. That choice is frozen. Outer fits train the first 40/60/80% and sequentially predict the following 20%, updating state only after the observed choice. This is later portions of the **same sessions**, with parameter fitting pooled over early session prefixes; it is not prediction of unseen sessions/days.

The initial 108 prescribed fits all converged. Four bias-oriented starts per HMM revealed local optima, so a training-only check added two coherence-sensitivity-oriented starts to each of twelve selected outer HMMs. All 24 additional fits converged. Better PSUIM6 middle-prefix modes were found; final results use `selected_models_v2.pkl` / `heldout_predictions_v2.csv`. Priors were unchanged and no held-out score selected an optimizer solution. First-pass results are preserved.

Selected prior SDs: PSUIM6 static 2/shared 1/free 1; PSUIM7 static 1/shared 2/free 1. Sources: `prior_selection.csv`, `fit_audit.csv`, `search_check.csv`. Starts are selected using actual post-update model log probability. The fork's displayed EM progress combines an older E-step likelihood with an updated prior, so that trace was not used as a fitted likelihood.

## Held-out results

Every model is scored on identical choices: 3,461 in PSUIM6 and 4,020 in PSUIM7. All eighteen selected outer models converged with no failed observation M-step. The assessment independently verified source/input hashes, trial identity, fold labels and Bernoulli likelihood values (`assessment_v2/assessment_audit.json`).

Gain in bits per test trial (positive favors the first model):

| Comparison | PSUIM6 [conditional 95% interval] | PSUIM7 [conditional 95% interval] |
|---|---:|---:|
| Shared-pulse HMM − static | **0.03757 [0.02165, 0.05350]** | **0.01483 [0.00336, 0.02703]** |
| Free-pulse HMM − static | 0.03461 [0.01880, 0.05082] | 0.01548 [0.00325, 0.02888] |
| Free-pulse − shared-pulse HMM | **−0.00296 [−0.00461, −0.00127]** | **0.00065 [−0.00436, 0.00570]** |

Source: `assessment_v2/heldout_differences.csv`. Freeing pulse weights costs 7.11 held-out NLL in PSUIM6 and saves 1.82 in PSUIM7. The latter is unresolved. Intervals use 600 within-session blocks of fifty **original saved records**, conditional on fitted models. They are pointwise descriptive intervals without a multiplicity adjustment; no formal population tests were performed. They do not refit the whole training procedure, and are not a population test from two mice.

The original four-start comparison gave PSUIM6 free-minus-shared −0.00088 bits/trial with an interval spanning zero. The training-only optimization check strengthened the shared-pulse account rather than revealing a free-pulse advantage. This sensitivity is documented rather than hidden; all original artifacts remain available.

## External RT and pulse checks

Current RT was not used to fit/infer the current state. Previous RT remains an explicit history covariate. State labels use the larger predicted choice contrast between +36% and −36% coherence; this is not an attention label.

Conditional log-RT slopes for the pre-choice probability of the higher-contrast state:

| Mouse | Shared-pulse HMM | Free-pulse HMM |
|---|---:|---:|
| PSUIM6 | 0.0044 [−0.0777, 0.0765] | −0.0011 [−0.0863, 0.0702] |
| PSUIM7 | 0.0897 [0.0228, 0.1537] | 0.0243 [−0.0277, 0.0761] |

Source: `assessment_v2/rt_external_validation.csv`. The PSUIM7 shared model associates higher baseline choice contrast with **slower**, not faster, conditional responses; this association is not robust to the free-pulse model. These are descriptive regressions adjusted for current evidence/choice, session, position and history, with fitted state probabilities held fixed. They do not supply a generative RT prediction or establish a common attention state.

Nonzero-coherence congruency summaries match each pulse cell with controls at the same signed coherence, pooling retained response times. They show remaining calibration differences, including the early incongruent effect: observed −14.88 / −15.36 pp versus shared-HMM −6.86 / −10.92 in PSUIM6/7. Freeing pulse weights does not resolve these discrepancies (−6.76 / −9.85). Source: `assessment_v2/pulse_congruency_validation.csv`.

These marginal contrasts are **not** the earlier 0.3–1.2 s post-pulse response-conditioned estimator. A choice-only GLM-HMM cannot predict that joint RT/pulse curve. It therefore cannot be presented as having solved paper point 3 even if its marginal choice calibration improves.

[Final figure](pulse_hmm_pilot_final.pdf): choice gains, pulse coefficients, unused-RT associations and marginal pulse contrasts. E/M/L denote early/middle/late; C/I congruent/incongruent; coefficient ranges show variation across fitted training prefixes, not sampling confidence intervals.

## Decision

Keep **shared pulse weights** as the simpler state-model benchmark. This pilot does not motivate a large campaign of state-specific pulse coefficients. It does not rule out smaller state effects, additional states, continuous histories or context-dependent sensory mechanisms; none was recovered/identified here.

This pilot does not compare discrete states against continuous dynamics. The preceding history analysis already showed that extended history can represent much of the serial benefit in these two mice; a predictive HMM win is not proof of discrete psychological states.

The publication-relevant constraint is that predictable baseline/history states improve serial choice predictions while the additional pulse-specific state freedom provides little benefit. A joint choice/RT accumulator with constrained baseline-state variability is a possible next mechanism comparison. It would still need to reproduce both signed early pulse effects and RT distributions, and to pass held-out/recovery checks. The current analyses do not establish attention or a unique accumulation-memory constant.

## Provenance/reproduction

Base commit `b63c9d9`; new work uncommitted. Input/source hashes: `pilot_manifest.json`, `search_manifest.json`, assessment audit. Exact install logs, environment freeze, runtime and emission tests are adjacent. Author-approved installation uses only the separate environment.

Commands executed from `/src`, with single-thread BLAS:

```bash
OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 NUMBA_NUM_THREADS=1 /mnt/data/venvs/nhp-glmhmm-2026-11-15/bin/python -m scripts.behavior.check_nhp_ssm_install
OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 /mnt/data/venvs/nhp-glmhmm-2026-11-15/bin/python -m tests.test_nhp_pulse_observations
OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 /mnt/data/venvs/nhp-glmhmm-2026-11-15/bin/python -m scripts.behavior.fit_nhp_pulse_pilot
OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 /mnt/data/venvs/nhp-glmhmm-2026-11-15/bin/python -m scripts.behavior.check_nhp_pulse_search
OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 /mnt/data/venvs/nhp-glmhmm-2026-11-15/bin/python -m scripts.behavior.assess_nhp_pulse_pilot --version 2
OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 .venv/bin/python -m scripts.behavior.plot_nhp_pulse_pilot
```

Use new versioned outputs for reruns. Cached starts verify matching source/input signatures; do not remove these checks to reuse incompatible fits. No raw data or existing DDM fit files were modified.
