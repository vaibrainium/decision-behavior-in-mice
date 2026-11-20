# Pulse-only models versus Figure 4C onset-stage influence

All22 pulse-only candidates were evaluated with fixed saved parameters, two independent simulation seeds and30 repetitions per input. The same ordinal readout and outcome-eligibility rules were applied to generated choices/RTs. Observed21,725 selection and regression cells reproduced exactly before analysis. No decision-model parameters refitted.

The normalized UGM without drift variability has the smallest all-available three-stage curve RMSE and slope error in both seeds. Mean predicted slope−0.72579 coherence-percentage units/stage versus observed−5.40068. Predicted early/middle/late influence is4.85793/4.13214/3.40635, versus observed12.10521/6.70452/1.30384. It is the only candidate with a negative average slope across the two seeds; other candidates' seed-specific slopes can change sign. This does not establish a population-level recency effect in the others.

The linear-leak BIC winner predicts mean slope+0.44413/stage. Best all-available does not imply an adequate fit to the observed early amplitude or onset slope. No calibrated rejection test was performed.

Matched-six sensitivity changes the descriptive curve ranking: linear integrator with drift variability is closest on mean curve RMSE; its ordering versus nearby models changes between seeds. Observed matched-six slope−1.71722 has a broad interval including zero. Thus cohort support is material; do not claim one identified accumulation mechanism from the pooled primacy result.

Files: model_primacy_ranking{,_matched6}.csv, model_readout{,_matched6}_by_seed.csv, model_stage_readouts.csv, caption.md and verification.json. Each of440 simulation-cell files has fit hash, seed, repetitions, selected counts and nonresponse metadata. Per-readout JSONs retain coefficients/diagnostics. Coherence-equivalent offsets here are not the percentage-point pulse effect in the earlier amplitude ranking.

Reproduce from /src, choosing a fresh output directory:

```bash
OPENBLAS_NUM_THREADS=1 .venv/bin/python -m scripts.paper.pulse_model_primacy --phase prepare --output <output>
OPENBLAS_NUM_THREADS=1 .venv/bin/python -m scripts.paper.pulse_model_primacy --phase simulate --output <output>
OPENBLAS_NUM_THREADS=1 .venv/bin/python -m scripts.paper.pulse_model_primacy --phase analyze --output <output>
OPENBLAS_NUM_THREADS=1 .venv/bin/python -m scripts.paper.pulse_model_primacy --phase analyze --comparison matched_6 --output <output>
OPENBLAS_NUM_THREADS=1 .venv/bin/python -m scripts.paper.plot_pulse_model_primacy --source <output>
```

These are exploratory conditional model checks using an already fitted response-selected stimulus pool. Model bands show simulation-seed range only. No new biological significance tests, no multiple-comparison-adjusted claim of model superiority, and no parameter uncertainty. All regressions use the same estimator; model response eligibility and resulting cell weights can differ from observed data as predictions of the fixed model.
