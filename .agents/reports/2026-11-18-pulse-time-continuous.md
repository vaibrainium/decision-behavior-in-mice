# Report: Continuous onset-time slope of directional pulse influence
Date: 2026-11-18   Agent: Codex   Commit: ed2d38d (base; uncommitted)
Plan: plans/2026-10-26-paper-accumulation-variant.md

## Question
Does pulse influence decrease with actual onset time, using one primary slope test and categorical mouse baselines?

## Summary
Estimated influence decreases by2.93 coherence units per100ms delay. Primary cluster-t9 p≈.0493, but cluster jackknife p≈.0903 and its interval spans zero. Negative slopes persist across objectives/selections and every omitted-mouse fit; evidence remains suggestive, not robust proof of primacy. Added common pulse-presence nuisances to separate directional influence and keep time centering invariant. No existing figure adopted/replaced.

## Findings
- VERIFIED:21-parameter model, restricted19,313 and original23,684 earlier-time/control trials,10 mice;40/40 multistart fits converged, no bounds, all observed coherence slopes positive. Source: parent fit_diagnostics.csv and optimizer_starts.json.
- VERIFIED primary restricted WLS:−2.931574 per100ms,95% cluster CI[−5.851405,−.011743],two-sided t9 p.049261856. Same point estimate jackknife CI[−6.427223,+.564075],p.090302. Source: inference_v2_trial_count/primary_slope_tests.csv.
- VERIFIED sensitivities: restricted binomial−2.877438,p.047442;original WLS−3.249952,p.047126;original jackknife p.089953. All omitted-mouse slopes negative, PSUIM7 omission reduces restricted magnitude to−1.448881. Sources: final tests and leave_one_mouse_slopes.csv.
- VERIFIED:continuous time vs ordinal in otherwise same21-parameter model changes p.053213→.049262. Earlier19-parameter model lacked common pulse-presence offset/slope terms. This is not a pure continuous-versus-categorical discovery. Source: specification_comparison.json and parent specification_diagnostic/.
- VERIFIED:13 relevant unit tests pass, including time-center invariance, correct control coding, half-direction-difference slope, analytic derivatives, Hessian expected information and frequency-aggregation covariance invariance. Independent primary p/CI/unit checks pass, saved costs reproduced, full Hessian covariance stable to10x step change<7.3e-8 relative. Near-optimum slope range<.00013 per100ms. Source: tests/test_pulse_time_continuous.py, tests/test_pulse_time_mouse_fixed_effects.py, final verification/manifest/stability files.

## What didn't work
Initial finite correction counted grouped cells, producing aggregation-dependent clustered covariance. Corrected to underlying trial counts; original source/results preserved, new inference_v2_trial_count/ is current. Earlier19-parameter ordinal mouse-ID covariance also recomputed in observed_hessian_inference_v2_trial_count/ without refitting; see separate correction report. Statistical conclusion unchanged. Borderline primary p is not robust to jackknife uncertainty.

## How to reproduce
Fit and final refinement commands are in parent README and inference_v2_trial_count/README.md. Script: scripts/paper/pulse_time_continuous.py; refinement: scripts/paper/refine_continuous_time_inference.py. Inputs/hashes exported. Existing .venv; no installs.
Tests: `.venv/bin/python -m unittest tests.test_pulse_time_continuous tests.test_pulse_time_mouse_fixed_effects -v`.
Actual output: dissemination/paper_accumulation/draft_2026-11-15/pulse_time_continuous_2026-11-18/, current inference in inference_v2_trial_count/.

## Caveats
Single primary hypothesis was selected after earlier exploration, not confirmatory.10 clusters, common pulse/sensitivity/asymptote assumptions and unequal animal trial counts. Timing mostly occupies2 windows, UW only2 exact earlier onsets; line assumes linear behavior across gap. Post-offset eligibility can change time-conditioned populations. No intrinsic integration/leak constant estimated. Current plots display model estimates/pointwise uncertainty, not independent time-bin observations.

## Open questions and next steps
- [ ] Author assess suggested directional timing dependence while retaining jackknife uncertainty.
- [ ] Before publication primacy claim, resolve model/sampling assumptions and mouse heterogeneity; retain directional pulse effect separately from its timing trend.
