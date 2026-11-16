# Pulse inputs for the author's NHP GLM-HMM

**2026-11-15 update:** The author selected task-assigned correct side. The target-relative six-category export is complete, including zero-coherence pulses; use `../nhp_ssm_2026-11-15/target_inputs_v2/`. The exact SSM fork/revision is now verified from NHP requirements and lockfile. Current setup, target provenance and verification are in [the continuation README](../nhp_ssm_2026-11-15/README.md). Earlier baseline-congruency questions below are historical context, not a pending author decision.

The requested repository is [vaibrainium/prior-encoding-in-nhp-sc](https://github.com/vaibrainium/prior-encoding-in-nhp-sc), inspected at commit `b42fb00ed243ace8dc831a6c72caca7c7494d8d2`. The fitting utilities and newer feature/mask notebook were read; exact snapshots and their GitHub blob hashes are available locally under `cache/nhp_sc/`. This audit did not execute or modify the NHP project.

The useful reusable contract is the list of session-wise **observations, inputs and masks**, and its input-driven Bernoulli emissions. The current environment lacks `ssm` and `autograd`, so the exact NHP fitter has **not** run. No packages were installed. The small bias-only HMM reported elsewhere in this folder is an independently checked diagnostic implementation, not an output of the NHP fitter.

## What is ready

`scripts/behavior/make_nhp_pulse_inputs.py` exports `cache/nhp_pulse6_inputs.pkl`, with one dictionary per mouse. Each contains `observations`, `inputs`, `masks`, `aggregate_rows`, `session_ids` and `feature_names`. Use Bernoulli `C=2` explicitly. Current features include flexible coherence indicators, **six separate pulse-type indicators** (left/right × three onset stages), and the matched first-order history covariates. Control trials have all six pulse indicators zero. Left/right coefficients are independent. Every saved row in an accepted session remains in sequence. Masks select exactly the existing DDM responded population. The adjacent `nhp_pulse6_input_*` manifest and per-session audit give counts and provenance. The superseded signed-three-feature export is preserved separately.

The pulse indicators encode **scheduled direction and onset stage**. The old preprocessing `pulse_type` is set to control for responses before pulse completion; using it here would put current response timing into a supposed stimulus predictor. The adapter uses the corrected follow-up schedule instead. Current RT, current outcome/target and realized pulse exposure are excluded from choice predictors.

The author also proposed early/middle/late × congruent/incongruent. For **right-versus-left** outcomes, baseline-motion congruency indicators must carry baseline sign (equivalently interact with baseline direction). Plain unsigned congruency indicators are appropriate only after a corresponding outcome/covariate transformation to correctness. The mathematical equivalence is tested in `tests/test_pulse_feature_encoding.py`.

However, the retained population includes **zero-coherence pulse trials in every mouse**, so baseline-motion congruency is undefined there. The adapter intentionally raises rather than silently allocating or excluding those trials. The six physical-direction inputs remain the complete usable export while this alternative is clarified. Defining congruency relative to a task-assigned correct side is a different choice and requires verifying that assignment at zero coherence; it must not be inferred casually from the mouse's current response/reward. Another explicit option is a separate zero-coherence pulse component. Neither alternative has been silently substituted into the existing export.

## Small comparison worth doing

Fit the same features in a one-state GLM and a two-state GLM-HMM. First tie pulse coefficients between states while allowing bias and baseline coherence sensitivity to change; then release just the pulse coefficients. This asks whether pulse sensitivity adds predictive information beyond changing side bias or baseline sensitivity. A third state should require a clear predictive benefit before interpreting it. Keep a continuous-bias/history comparator; the current evidence does not favor literal discrete states over continuous drift.

Use training-only starts/regularization and the existing prefix test blocks for the first pilot. Estimate the current state from **past outcomes only**. Current choice, current RT and future trials may not define an independent pretrial state label. The NHP cross-validation helper uses multiple disconnected train/test segments with separate initial conditions; that is a different prediction target and should not be silently substituted for next-choice forecasting.

The newer NHP feature notebook retrieves previous valid trials. The mouse adapter deliberately shifts the original saved-record sequence and flags missing/late/correction history instead. Preserve this explicit convention. Audit the NHP/installed-`ssm` transition-parameter convention before reusing its initialization; probability matrices and unconstrained/log transition parameters are not interchangeable.

## Filtering limit

The accepted sessions were selected using performance criteria; the observed emissions further condition on response eligibility. Preserving masked rows avoids falsely treating the next retained choice as the immediately following logged event. It does **not** recover unlogged events, make missingness independent of state, or establish arousal/attention. All state dwell parameters must therefore be described in saved-record steps, conditional on the selected sessions and response population.

A pulse-input choice GLM-HMM can reveal changing sensitivity. It still does not identify accumulation memory or provide a joint choice/RT likelihood. To address paper point 3, validate current RT without using it to define state, and then test the successful account against the signed pulse profiles and joint RT/choice constraints.
