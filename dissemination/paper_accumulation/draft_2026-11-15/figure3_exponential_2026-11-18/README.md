# Figure3D exponential overlay — candidate

Main preview: figure3D_exponential.png/pdf/svg. Original data-only candidate remains unchanged. Diagnostic: exponential_bootstrap_diagnostic.png/pdf/svg (pointwise 95% curve intervals from 200 whole-mouse resamples, not data SEM).

Equation: p(t)=p0+(p_inf-p0)(1-exp(-(t-0.3)/tau)), for t in [0.3,5] seconds. Starting accuracy is free; p_inf>=p0. Tau constrained to 0.01–20s. Four coherence-specific fits use individual Bernoulli outcomes, inverse mouse/coherence trial-count weights, and multistart optimization. Every mouse contributes equally within a coherence, while trials within a mouse are equally weighted. Zero coherence uses a weighted constant. The common curve does not model between-mouse differences in RT dependence. Bootstrap resamples entire mice with a common draw across coherence, seed89123. No formal tests or model-selection claims.

The strongest-coherence curves describe the rise and plateau reasonably. Weak-coherence time constants are less identifiable: 11/200 9% resamples and 1/200 18% resamples hit a tau bound; none do at 36% or 100%. The 9% tau interval reaches the imposed 20-s upper limit and its upper asymptote interval reaches 1. Do not report this as a precise integration time or compare coherence time constants mechanistically.

Tables: trials.csv, parameters.csv, bootstrap_parameters.csv, parameter_intervals.csv (second column is percentile), curves.csv. Checks and input hashes: manifest.json and checks.json. Curve bands are pointwise descriptive percentile intervals with only 10 mice and 200 draws.

Reproduce from repo root, using a new output directory:
`.venv/bin/python -m scripts.paper.control_accuracy_exponential --output <new-directory>`
