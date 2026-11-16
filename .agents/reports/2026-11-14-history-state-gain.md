# Report: chronology, persistent bias and gain feasibility
Date: 2026-11-14   Agent: Codex   Commit: b63c9d9 (base; new work uncommitted)
Plan: plans/2026-11-14-history-state-diagnostics.md

## Question
Which literature-motivated account can strengthen the joint pulse/choice/RT story using existing data, without labeling generic variability attention?

## Summary
History-adjusted choice and RT residuals remain serially correlated. A continuous bias model predicts future portions of the retained sessions better than a static history GLM; long history explains much of that benefit in the main pulse mice. A new positive evidence-gain pilot partly improves the RT/late-pulse tradeoff but still misses early pulse amplitude. Neither result establishes attention or an integration time constant. The requested NHP pulse-HMM input contract is prepared, but that exact fitter has not run.

## Findings
- VERIFIED: all 50 accepted sessions match original trial CSV counts, order/counters and choices. Saved sequence: 30,146 records; main DDM choices: 25,493. Session/per-response filters remain relevant. Source: `scripts/behavior/audit_history_selection.py`, `dissemination/history_dynamics_2026-11-14/selection_audit.json` and `raw_session_alignment.csv`.
- VERIFIED: after first-order history, mouse-mean residual correlations at saved-record lags 2–10 are 0.07259 for choice and 0.05056 for log RT; Holm p over four declared endpoints 0.00036 / 0.03992. Both positive in every mouse. History-versus-current-RT changes have no resolved group direction. Source: `scripts/behavior/history_dynamics.py`, `group_inference.csv` in the same output folder.
- VERIFIED: continuous / two-state bias models gain 0.04264 / 0.02908 bits per outer test trial over matched static history; Holm p over five declared endpoints 0.01236 / 0.03245. All models share 14,854 prefix-held-out choices. No corrected distinction between discrete/continuous accounts; current-RT validation has no resolved group direction. Source: `predictive_bias_states.py`, `refine_discrete_bias_states.py`, `states_v2_grid15_*`. Use v2, not initial nonconverged two-state fits.
- VERIFIED: nested training-only penalty sensitivity still supports predictive continuous bias, but its advantage over ten-record history is only 0.009984 / 0.001123 bits in PSUIM6/7. A richer history process remains a viable representation. Source: `check_state_regularization.py`, `state_regularization_sensitivity.csv`.
- VERIFIED: bounded full-training gain fits plus twelve fresh-seed evaluations (4,564,080 outcomes) give total NLL changes versus additive drift variability −51.35 in PSUIM6 and +31.18 in PSUIM7. Gain improves choice in both; its PSUIM7 RT loss is +73.06, smaller than the no-variability +269.38. Early pulse predictions 7.54 / 8.44 pp remain below observed 15.50 / 13.48. Source: `scripts/ddm/evidence_gain_feasibility.py`, `assess_evidence_gain.py`, `dissemination/evidence_gain_2026-11-14/*csv`. Full-training feasibility only; no held-out gain ranking.
- VERIFIED: the author's requested repository is `vaibrainium/prior-encoding-in-nhp-sc`, read at b42fb00ed243ace8dc831a6c72caca7c7494d8d2. Its fitter requires absent `ssm`/`autograd`; no installations performed. Six independent physical pulse indicators are exported (left/right × stage; control reference), original rows retained with masks. Source: `make_nhp_pulse_inputs.py`, `nhp_pulse6_input_manifest.json`, `NHP_GLM_HMM_ADAPTATION.md`.
- VERIFIED: the suggested congruent/incongruent alternative encounters zero-coherence pulse trials in every mouse. Baseline-motion congruency is undefined there. A clarification is pending; six physical-direction types remain valid. No trials were silently dropped or assigned a false congruency.
- INTERPRETATION: serial directional bias is a relevant nuisance/mechanistic candidate. Neither a choice-only state win nor better gain training scores establish attention, a discrete biological state or a unique accumulation memory.

## What didn't work
- Direct self-transition optimization left many two-state fits unconverged; preserved outputs, reoptimized identical model in logit coordinates. All revised selected fits converged; training-only selection.
- Unregularized/weakly regularized longer-history expansion overfits some short datasets. Added nested penalty selection, without selecting on outer test outcomes.
- Positive iid gain does not close the early pulse deficit even after shared-parameter refitting. Do not infer family impossibility from a bounded local pilot.
- Exact NHP GLM-HMM could not run with current dependencies; prepared source audit/inputs instead of installing packages or claiming a fit.

## How to reproduce
Commands executed from `/src`, existing `.venv`, single-thread BLAS. Full module list, exact file paths and source/input hashes: `dissemination/history_dynamics_2026-11-14/RESULTS.md`, adjacent manifests; gain commands/hashes: `dissemination/evidence_gain_2026-11-14/RESULTS.md` and manifests. Scientific checks passed: `tests.test_history_dynamics`, `tests.test_predictive_bias_states`, `tests.test_evidence_gain`, `tests.test_pulse_feature_encoding`. Use new versioned output paths for reruns, not these result directories.

## Caveats
Same-session prefix prediction pools early prefixes across sessions, not unseen-session/day prediction. Original logged records cannot establish completeness of unlogged events. Masking does not model outcome-dependent missingness. Current-RT-conditioned curves and RT validation are descriptive. Frozen-predictor serial null references are not whole-procedure calibration. Gain fits are two-mouse full-training local pilots; simulation seeds are not biological replicates. See detailed results for interval and correction definitions.

## Open questions and next steps
- [ ] Clarify baseline-motion versus task-assigned-target congruency and zero-coherence handling before fitting that alternative.
- [ ] Use the NHP input/mask contract for a small pulse-coefficient-tied versus state-specific pulse comparison when exact fitter dependencies are available; no extra experiments needed.
- [ ] Require joint choice/RT and signed early-pulse adequacy before expanding a candidate. Positive gain helps the late tradeoff but is incomplete.
- [ ] If a compact candidate succeeds, run held-out comparisons and matched synthetic recovery before interpreting mechanism for publication.
