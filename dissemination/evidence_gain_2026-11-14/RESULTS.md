# Positive evidence-gain feasibility pilot

This candidate partly improves the joint fit but **does not explain the early pulse amplitude**. It is more informative than the previous variable-response-delay alternative, and is not yet a validated replacement for drift variability.

## Target and implementation

Two mice, PSUIM6/PSUIM7, were selected because they dominate the existing pulse/RT diagnosis. All existing responded trials and common parameters were used. The positive mean-one trial gain is `G = exp(sigma Z - sigma²/2)`. It scales the complete mapped evidence stream, including every pulse channel, **after** the sensory transform. Directional drift offset, diffusion noise, guesses, deadline and floor keep their existing definitions. Additive `sv` is disabled when gain spread is active.

`src/ddm/evidence_gain.py` is separate from the legacy simulator. CPU/CUDA tests independently verify channel combination and transform placement, unscaled bias/diffusion, common-draw equivalence, positive gain moments and an exact zero-spread legacy limit. No existing fitted results or raw inputs were overwritten.

The bounded local multistart pilot refit all common parameters using three-repetition screening and fifteen-repetition refinement. Gain SD bounds were 0–1.5 in log units. Fits are `/mnt/data/processed/ddm/fits_evidence_gain_2026-11-14/*_gain_all.pkl`. They are **full-training fits**, with no certified global optimum. Held-out folds have not been fitted.

## Independent simulation checks

Each of three families was evaluated at two fresh seeds and sixty repetitions per empirical schedule, giving twelve scores and 4,564,080 outcomes. `assessment_audit.json` verifies schedule identity/counts, fitted-file hashes and likelihood decomposition. Fresh seeds assess Monte Carlo noise; they do not provide held-out generalization or biological replication.

Mean NLL difference from additive drift variability (negative favors the alternative):

| Mouse | Candidate | Choice | RT | Total |
|---|---|---:|---:|---:|
| PSUIM6 | No trial variability | −5.84 | +16.39 | +10.55 |
| PSUIM6 | Positive gain | −25.32 | −26.03 | **−51.35** |
| PSUIM7 | No trial variability | −21.97 | +269.38 | +247.41 |
| PSUIM7 | Positive gain | −41.88 | +73.06 | **+31.18** |

Source: `training_differences_from_drift.csv`, averaged over evaluation seeds. Gain total differences are −47.18/−55.52 for PSUIM6 and +42.06/+20.30 for PSUIM7. These scores cannot be substituted for the earlier out-of-fold comparison. The optimized gain log SDs are 0.657 and 1.036 (`parameters.csv`).

The early coherence-matched signed pulse effect, averaged over both signs, remains too small:

| Mouse | Observed effect, pp [pointwise block interval] | Additive drift | No trial variability | Positive gain |
|---|---:|---:|---:|---:|
| PSUIM6 | 15.50 [12.46, 18.77] | 7.38 | 7.41 | **7.54** |
| PSUIM7 | 13.48 [11.17, 15.59] | 3.80 | 6.48 | **8.44** |

Early means 0.3–1.2 s after (pseudo-)onset using the established response-conditioned estimator. Intervals use 400 within-session blocks of fifty **original saved records**. Point estimates exactly match the earlier estimator; interval resampling now preserves the audited chronology. These are exploratory pointwise intervals conditional on the retained population, not group tests or causal temporal kernels. Sources: `data_pulse_window.csv`, `model_pulse_window.csv`.

For PSUIM7 the late pooled prediction moves from −4.81 pp with additive drift variability to −0.14 pp with gain (observed −0.95 [−4.26, 2.47]). Thus gain largely removes that late reversal while retaining much of the RT advantage. The positive-pulse early residual remains particularly large: observed 15.26 pp versus gain 8.02 in PSUIM7, and 18.10 versus 6.93 in PSUIM6. Both signs are shown separately in [the revised figure](gain_feasibility_v2.pdf), with the full observed interval range. The original fixed-range figure is retained as v1.

## Interpretation and limits

This establishes a plausible route for positive gain to improve the **late-response/RT tradeoff**, rather than resolving the whole mechanism. It does not establish attention, recover an integration memory constant, explain serial choice bias or reproduce the early pulse amplitude. No full-cohort expansion is justified merely by the better PSUIM6 training score. A fixed-parameter failure was not used to reject the candidate: shared parameters were refitted, but a broader search and held-out evaluation would still be required before model ranking.

The immediate complementary question is whether pulse sensitivity changes with pretrial behavioral regime, beyond directional bias and baseline sensitivity. The requested NHP pulse-input GLM-HMM adapter and its limits are documented in `../history_dynamics_2026-11-14/NHP_GLM_HMM_ADAPTATION.md`.

## Reproduction/provenance

Base commit `b63c9d9`; new code/results are uncommitted. Exact source and input hashes: `manifest.json`, `assessment_audit.json`. Commands executed from `/src` with existing `.venv`, no installations:

```bash
OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 NUMBA_NUM_THREADS=1 .venv/bin/python -m tests.test_evidence_gain
CUDA_VISIBLE_DEVICES=0 OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 NUMBA_NUM_THREADS=1 .venv/bin/python -m scripts.ddm.evidence_gain_feasibility
OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 .venv/bin/python -m scripts.ddm.assess_evidence_gain
OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 .venv/bin/python -m scripts.ddm.plot_evidence_gain_v2
```

These document completed executions. Preserve this output directory; use a new version for any rerun. The initial assessment attempt preceded the last cache file and stopped without summary outputs; the completed collection is logged in `assessment_run_v2.log`.
