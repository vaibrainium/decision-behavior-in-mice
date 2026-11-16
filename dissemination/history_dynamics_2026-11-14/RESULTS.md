# History, persistent bias and the pulse story

**Choices contain predictable serial bias beyond first-order history. That is a useful model constraint, but it has not solved the joint choice/RT/pulse problem or identified attention.** Continuous drift is at least a serious alternative to literal discrete choice states. The filtering audit materially limits the population and timescale interpretation.

## 1. Selection and chronology

The main population is the existing 25,493 responded DDM trials from ten mice and fifty accepted sessions. Every accepted session was compared with its original trial CSV: row counts, counter order and choices agree in all fifty. The broader saved sequence contains 30,146 records: 25,508 eligible responses, 4,102 late responses, 435 no-choice records and 101 correction records. Fifteen otherwise eligible responses are absent from the DDM input; these are preserved in sequence but not scored. Sources: `raw_session_alignment.csv`, `selection_audit.json`, `valid_responses_absent_from_ddm.csv`.

The compilation removes subjects with fewer than two recorded sessions. The later preprocessing removes correction trials and ineligible response times, and selects sessions using trial count and fitted control performance. The inspected thresholds are at least 300 eligible responses, RT 0.15–5 s, lapse/guess each <0.25, absolute PMF mean <25, and PMF variance parameter <0.5. These describe the implemented data selection; this analysis did not change those historical inputs. Notebook/source hashes are in `selection_audit.json`.

Previous outcomes are reconstructed from the original saved-row order, not the next retained analysis trial. Counter duplicates mean the counter is not a unique record ID. Compressing the retained rows would change 1,536 previous-choice assignments **where both previous-choice definitions are available** (`chronology_by_mouse.csv`). The audited previous-choice/outcome coding agrees exactly with the existing follow-up table.

This verifies logged order, not completeness of all events that may have occurred in the task. Dynamics are conditional on accepted sessions and the responded subset. Missing records advance the latent state without a choice emission. Masking does **not** establish noninformative missingness. Timescales are in saved-record steps, not elapsed seconds or proven distinct stimulus presentations.

## 2. History and residual persistence

Matched regressions account for current condition, session, within-session position, previous coherence, missing/correction/late flags, then previous rewarded/unrewarded choice and previous log RT. Choice uses Bernoulli regression; conditional log RT additionally adjusts for current choice and its coherence interaction. Five contiguous within-session blocks supply residual predictions. Those diagnostic regressions can train on blocks on either side; they are not prospective/new-session tests.

Four group endpoints were fixed before inference. Group tests use mice, with Holm correction over these four endpoints. Within-mouse pointwise uncertainty uses fifty-record blocks.

| Endpoint | Mouse mean [95% t interval] | Holm p | Direction |
|---|---:|---:|---|
| Rewarded-history log-odds contrast change, RT q80−q20 | −0.057 [−1.117, 1.004] | 1.000 | Mixed |
| Error-history contrast change | −0.101 [−0.561, 0.359] | 1.000 | Mixed |
| Choice residual correlation, mean over lags 2–10 | **0.0726 [0.0480, 0.0972]** | **0.00036** | Positive in every mouse |
| Log-RT residual correlation, mean over lags 2–10 | **0.0506 [0.0133, 0.0878]** | **0.0399** | Positive in every mouse |

Sources: `group_inference.csv`, `mouse_summary.csv`, `residual_acf.csv`. The RT-history curves are descriptive conditioning on current response time; their mixed directions cannot classify drift bias versus starting-point bias by eye. Control-only and clean-previous sensitivities are retained in `history_bias_curves.csv`/regression caches. Frozen-predictor Bernoulli and residual-permutation references are explicitly **not** a full refitted sequential null calibration.

## 3. Future-choice prediction

Three candidates use the same evidence/session/history covariates: a static GLM, continuous AR(1) additive log-odds bias, and a two-state bias-only GLM-HMM. The continuous process is approximated by a Rouwenhorst grid with the specified stationary variance and lag correlation; it is not PsyTrack or a fully unconstrained strategy model. The HMM varies side bias, not pulse sensitivity.

Fit the first 40/60/80% of each session's saved rows; predict the following 20% and update state only after an observed choice. All models share 14,854 outer test trials. Parameters pool early prefixes from the retained sessions; this is future portions of those sessions, **not** an unseen-session/day forecast. The current state distribution never uses current choice/RT or future outcomes.

| Comparison | Mean gain, bits/test trial [95% t interval] | Holm p, five endpoints |
|---|---:|---:|
| Continuous bias vs static | **0.0426 [0.0194, 0.0659]** | **0.0124** |
| Two-state bias vs static | **0.0291 [0.0096, 0.0485]** | **0.0324** |
| Two-state minus continuous | −0.0136 [−0.0264, −0.0007] | 0.1228 |

Source: `states_v2_grid15_group_inference.csv`. Continuous improves ten mice; revised two-state fits improve nine. The continuous-versus-discrete difference does not survive the declared correction; do not claim a decisive discrete/continuous distinction. The other two endpoints assess current RT, which was unused in state inference: neither model's choice-alignment association has a resolved group direction (both Holm p=1). See `states_v2_grid15_mouse_summary.csv` for individual mice and the [overview figure](history_state_overview.pdf).

The original direct-transition optimizer did not converge in many two-state fits. Those v1 outputs are retained but superseded. Reoptimization in logit transition coordinates made all thirty selected two-state fits converge; all thirty continuous fits converged. Selection uses training likelihood only. Brute-force path enumeration and independent numerical derivatives check likelihoods and gradients; tests also verify gaps, boundaries and prediction before current choice.

## 4. Robustness and pulse checks

The longer fixed-history comparator explains much of the improvement in PSUIM6/7. Untuned extra coefficients can badly overfit short datasets; its raw check should not be treated as proof of latent states. Nested training-prefix penalty selection was therefore applied to static/continuous models on the same candidate penalties.

After matched tuning, continuous bias gains 0.0428 bits/trial on average over first-order static history (descriptive interval 0.0156–0.0699; positive in nine mice). Its advantage over tuned ten-record history is only **0.0100 and 0.0011 bits/trial** in PSUIM6/7, respectively (`state_regularization_sensitivity.csv`; use the exact stored values). Much of the predictable structure can thus be represented by extended history. These sensitivity intervals are uncorrected descriptive estimates, not an additional primary significance search. [Robustness figure](history_state_robustness.pdf).

Increasing the continuous grid from fifteen to thirty-one states on PSUIM6/7 changes mean predicted choice probability by less than 0.001 in every fold (`continuous_grid31_check.csv`). The frozen filtered-versus-stationary comparison in `state_sensitivities_by_mouse.csv` isolates the utility of past outcomes using otherwise identical emissions; it is not a separate mechanistic recovery exercise.

`pulse_by_pretrial_bias.csv` compares both pulse signs within near-neutral/biased pretrial regimes at common coherence/onset composition, without current-RT stratification. Threshold: absolute filtered latent bias 0.5 log-odds. These are exploratory responded-trial contrasts in the two main pulse mice, with conditional-on-state-fit block intervals. State parameter uncertainty is not propagated; opposite signed effects and unequal composition prevent assigning an attention interpretation. The standardization does not turn them into a causal temporal kernel.

## 5. Mechanistic consequence and requested NHP route

The complementary [positive-gain feasibility pilot](../evidence_gain_2026-11-14/RESULTS.md) partly improves the RT/late-pulse tradeoff but still underpredicts early pulse effects. It was not a held-out fit. Together these results support testing **which source of variability the pulse constrains**, rather than calling all fitted `sv` attention or inferring a unique forgetting time.

The author's [NHP GLM-HMM](https://github.com/vaibrainium/prior-encoding-in-nhp-sc) was inspected at a pinned commit. The exact fitter needs absent `ssm`/`autograd`; it has not run here. A masked session-list adapter now exports six independent physical pulse types (left/right × onset stage), with controls as reference. The proposed congruency alternative needs an explicit definition for zero-coherence pulses; it cannot silently label them congruent or drop them. See [adaptation notes](NHP_GLM_HMM_ADAPTATION.md), `nhp_source_audit.json` and pulse-input manifests for the current coding.

For the next targeted comparison, tie versus release state-specific pulse coefficients while keeping the same history/coherence covariates and pre-choice filtering. Compare against continuous/extended history, and validate current RT externally. A winning pulse-input choice HMM alone would still not identify accumulation memory or solve the joint choice/RT likelihood.

## Reproduction/provenance

Base commit `b63c9d9`; new work is uncommitted. Source/input hashes are recorded in manifests. The following modules were executed with `OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 .venv/bin/python -m`:

```text
scripts.behavior.history_dynamics --bootstrap 300
scripts.behavior.predictive_bias_states
scripts.behavior.refine_discrete_bias_states
scripts.behavior.check_bias_states
scripts.behavior.check_long_history_regularization
scripts.behavior.check_state_regularization
scripts.behavior.pulse_by_pretrial_bias
scripts.behavior.audit_history_selection
scripts.behavior.make_nhp_pulse_inputs
scripts.behavior.plot_history_dynamics
tests.test_history_dynamics
tests.test_predictive_bias_states
tests.test_pulse_feature_encoding
```

These document completed executions, not instructions to overwrite this directory. Use a new output version for reruns. The physical-six export's source is preserved under `cache/make_nhp_pulse_inputs_direction6_v2.py`; source changes for a subsequent alternative do not retroactively alter that exported dataset.
