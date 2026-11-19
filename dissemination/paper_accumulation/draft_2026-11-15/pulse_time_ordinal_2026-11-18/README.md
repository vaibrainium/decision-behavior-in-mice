# Ordinal1/2/3 pulse-influence time slope

Same21-parameter joint model as continuous-onset analysis (17 parameters for6 mice): categorical mouse baselines; shared pulse, time, slope and asymptote terms; pulse-presence nuisance intercepts retained. Only time input changes to x=stage−2 for pulses. ControlsP=d=x=0. Directional influence w(stage)=w0+wT*(stage−2); wT is coherence units per stage, not per100ms. Lines/markers are model estimates, not independently fitted stage observations.

Restricted input only,3 support comparisons:
- All available:21,725 responses,10 mice with late observed in6; slope−5.400683/stage,95% cluster-t9 CI[−9.846765,−.954601],p.022556; jackknife p.044027. Common-effect assumptions permit incomplete stage support but do not remove cohort-dependent pulse heterogeneity.
- Matched6 across3 times:7,434 responses; slope−1.717220,CI[−7.254332,3.819891],cluster-t5 p.461490,jackknife p.495277.
- Same10 early/middle:19,313 responses; slope−5.510359,CI[−11.115196,.094479],cluster-t9 p.053213,jackknife p.100785. Reproduces previous ordinal diagnostic.

Binomial sensitivity follows same pattern; all60 multistart attempts converged, no coefficient-bound contacts, observed coherence slopes positive. WLS main, full observed-Hessian cluster sandwich with aggregation-invariant trial-count CR1, t(G−1); leave-one-mouse jackknife sensitivity. No sign constraints or p-driven exclusions; unadjusted exploratory single slope tests per stated comparison, not independent confirmatory discoveries. Timing ordinal imposes linear equal stage steps. Stronger all-available result reflects inclusion of late as well as coding; matched6 check remains uncertain. Do not claim different cohorts have significantly different slopes without a formal comparison.

Figures: cohort_comparison.png/pdf/svg uses identical axes; individual all_available_10, matched_6, early_middle_10 previews retained. Tables/diagnostics/starts/full covariance/provenance exported. Stage coding/probability algebra, objective, units/tests and prior two-stage result independently verified. Existing Figure4 unchanged.

Reproduce in a fresh directory:
`OPENBLAS_NUM_THREADS=1 .venv/bin/python -m scripts.paper.pulse_time_ordinal --eligible dissemination/paper_accumulation/draft_2026-11-15/pulse_psychometric_timing_2026-11-18/eligible_trials.csv --previous dissemination/paper_accumulation/draft_2026-11-15/pulse_time_continuous_2026-11-18 --output <new-directory>`

## Author preference
Author selected the left/all-available plot as the preferred timing-panel candidate. See selection.json and selected_caption.md. The matched6 analysis stays separate as a sensitivity check. Late-six support must remain explicit; full Figure4 placement is pending. No data, fits or tests changed.
