# Continuous recorded-onset pulse influence

Current inference/preview: inference_v2_trial_count/. Source fit coefficients/cells/diagnostics here remain unchanged. Earlier inference counted grouped cells in a finite correction; v2 uses underlying trials and is invariant to frequency grouping. Initial source snapshots preserved.

Primary: recorded onset in seconds, early/middle restricted19,313 responses, same10 mice. Model keeps notebook probability equation and categorical mouse biases. P marks pulse presence, x=(onset-.15)/.2 for pulses (0 for controls): A=u_mouse+aP*P+aT*P*x+d*(w0+wT*x); B=b0+bP*P+bT*P*x+d*(v0+vT*x). Common presence terms are nuisance additions allowing centering without constraining common pulse bias/slope at time0.21 parameters, compared with19 in the prior ordinal model. Directional influence w(onset)=w0+wT*x is half the right-minus-left additive offset. Its physical slope is wT/.2 per second. This is distinct from common aT and beta slope.

One exploratory primary two-sided test of wT=0, no correction for stage-wise tests because none are primary here. The hypothesis was chosen after prior exploration, not confirmatory. Full observed score-Hessian mouse-cluster CR1, t9; WLS cluster jackknife and binomial/original-selection sensitivities retained. WLS uses trial-count weights on exact time/coherence cells, controls pooled within mouse/coherence; binomial sensitivity explicitly separate. Shared pulse, sensitivity and asymptote assumptions remain. All mice retained; leave-one fits only estimate uncertainty.

Fits:4 datasets/objectives×10 starts all converged, no bounds and positive actual coherence slopes. Near-optimum primary slope range<0.00013 coherence units per100ms. All omitted-mouse fits have negative slopes, but PSUIM7 affects magnitude. Recorded UW earlier onsets are2 exact times; UCLA timing spread does not make the design uniformly continuous. Primacy interpretation remains conditional on selection/model, not a forgetting constant or direct bound test.

Reproduce fit, fresh output:
`OPENBLAS_NUM_THREADS=1 .venv/bin/python -m scripts.paper.pulse_time_continuous --eligible dissemination/paper_accumulation/draft_2026-11-15/pulse_psychometric_timing_2026-11-18/eligible_trials.csv --previous dissemination/paper_accumulation/draft_2026-11-15/pulse_time_mouse_fixed_effects_2026-11-18 --output <new-directory>`
Then run scripts.paper.refine_continuous_time_inference as in current v2 README.
Tests: `.venv/bin/python -m unittest tests.test_pulse_time_continuous tests.test_pulse_time_mouse_fixed_effects -v` (13 pass).
