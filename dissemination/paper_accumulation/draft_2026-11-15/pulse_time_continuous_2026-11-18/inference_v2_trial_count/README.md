# Current continuous-time inference

Slope:−2.931574 coherence units per100ms onset delay; pointwise95% cluster-t9 CI[−5.851405,−0.011743],two-sided p.049261856. Jackknife uses same point estimate,CI[−6.427223,+0.564075],p.090302. Restricted binomial slope−2.877438,p.047442. Original-selection WLS slope−3.249952,p.047126; jackknife p.089953. The negative slope is consistent across these checks, but inferential significance depends on uncertainty method. Evidence is suggestive, not firm primacy proof.

Primary19,313 restricted early/middle trials,10 mice. Actual onset time is used, with no late extrapolation. Model and primary exploratory hypothesis in parent README/manifest. Shading is pointwise model-based95% cluster uncertainty, not SEM or raw-data observations.

Finite correction now uses G/(G-1)*(N_trials-1)/(N_trials-K), verified against expanded individual Bernoulli trials. Earlier cell-count correction is preserved in parent; it changed the primary continuous-time p only slightly (.049464→.049262), but was not invariant to aggregation.

Specification check: holding21-parameter model/trials fixed and using only ordinal early/middle gives p.053213. Thus replacing ordinal with actual time is a modest change, not a qualitative discovery at the0.05 threshold. The earlier19-parameter model also lacked2 common pulse-presence nuisance terms. Specification comparison and original diagnostic files retain these distinctions.

Reproduce inference without refitting:
`OPENBLAS_NUM_THREADS=1 .venv/bin/python -m scripts.paper.refine_continuous_time_inference --source dissemination/paper_accumulation/draft_2026-11-15/pulse_time_continuous_2026-11-18 --output <new-directory>`
Outputs: primary_slope_tests.csv, pulse_influence_curves.csv, optimizer_stability.csv, covariance/Hessian files, manifest.json, verification.json, specification_comparison.json, figures.13 related regression tests passed; existing Figure4 unchanged.
