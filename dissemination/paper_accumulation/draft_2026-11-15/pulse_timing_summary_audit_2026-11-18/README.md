# Audit: early timing coefficient plot

The earlier mean-of-individual-alpha plot is unsuitable as a population-curve summary. See ../pulse_psychometric_timing_2026-11-18_v2/SUMMARY_INTERPRETATION_WITHDRAWN.md. Current observed_curves.png/pdf/svg shows actual equal-mouse choice proportions with SEM, alongside a population-curve sensitivity fit.

The audit verifies physical pulse directions against raw pulse_coherence_pct. The observed early zero-coherence right-minus-left choice difference averages0.132762 across the10 mice. Averages of weakly identified individual midpoints obscure this behavior; DBM12 early-left midpoint hits−100. Absolute midpoint also does not itself measure a pulse-induced change, and with different asymptotes it does not refer to the same choice probability.

Population sensitivity: jointly fit control/left/right equal-mouse group points separately within each time; each curve has its own midpoint and slope, with common lower/upper asymptotes within time. These asymptotes are estimated jointly, not fixed to the control estimate. Main fit tries18 starts including both shift directions and no shift, selected only by squared error. Bootstrap uses120 whole-mouse resamples, identical draws across stages/directions, with2 starts per resample (warm fit and a neutral fit). Intervals are exploratory pointwise95% percentiles. No animal exclusions, direction signs or timing trends imposed; no hypothesis test or mechanistic time constant claimed. Changed estimand versus individual-coefficient means is explicit. Individual Figure4 paired panel is not automatically replaced.

population_parameters.png/pdf/svg plots absolute population midpoints and slope changes from control. Full/independent fit parameters, observed group points, predictions, bootstrap draws and intervals are exported. Independent free-asymptote population fits retained in independent_population_fits.csv show why free midpoint and P=.5 crossing differ. Checks/provenance: manifest.json and verification.json. No coefficient bound contacts in bootstrap, but uncertainty/model assumptions still limit interpretation.

Reproduce in a new directory:
`.venv/bin/python -m scripts.paper.audit_pulse_timing_summary --source dissemination/paper_accumulation/draft_2026-11-15/pulse_psychometric_timing_2026-11-18 --output <fresh-directory>`
