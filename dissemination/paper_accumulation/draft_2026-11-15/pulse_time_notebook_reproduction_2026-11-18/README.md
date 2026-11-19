# Exact original pulse-time population model reproduction

The reference screenshot is reproduced by the original notebook joint population model. This resolves an implementation/specification mismatch introduced by the assistant: separate per-mouse fits, equal-mouse population fits, independent stage parameters and midpoint sign convention are different analyses. The DBM12 boundary example does not explain failure to reproduce this original model.

Script extracts and runs the3 original fitting functions from reviewed notebook cell5 without changing equation, initialization, bounds, or pooled trial-count WLS weights. All10 fitted coefficients agree with saved cell14 values to the notebook's6-decimal rounding. Source valid_data has25,508 trials. No original notebook/helper/results changed.

Original alpha offset A=alpha1+alpha2*d+alpha3*t+alpha4*d*t, logistic uses coh+A. Native helper midpoint mu=-A. The original display omits alpha1 and plots A-alpha1: left[-10.113690,-3.115907,3.881876], right[13.560653,10.009833,6.459013]. Full-offset/native-midpoint values are also exported. No sign convention should be mixed silently.

The original model fits one shared lower and upper asymptote across all conditions, with linear ordinal-stage terms and direction×stage interaction in both offset and slope. It pools trials across mice rather than equally weighting mice or averaging individual fitted coefficients. Trial selection uses response-coded pulse_type. Separate same-model fits on current scheduled-label/response-eligible data isolate selection effects, and still recover direction-separated offsets. They are diagnostic, not adopted paper fits.

Plots notebook_original_display and notebook_full_offset preserve the fitted means. Their error bars are corrected ±1SE using c.T@Cov@c; the notebook's SE2+t*SE4 formula is retained in display_values.csv for audit only. These are conditional nonlinear-WLS covariance errors, not mouse-level population uncertainty or final paper inferential intervals. Stage trend is imposed and late includes only UW mice; do not treat it as a separately established timing trend. Pointwise physical timing windows differ by site.

Tables: parameters.csv; display_values.csv (all conventions and old/corrected SE); *_cells.csv; *_covariance.npy; manifest.json; verification.json. Original model is appropriate to reproduce first, before comparing scientifically motivated variants.

Reproduce in a fresh output directory:
`.venv/bin/python -m scripts.paper.reproduce_pulse_time_notebook --eligible dissemination/paper_accumulation/draft_2026-11-15/pulse_psychometric_timing_2026-11-18/eligible_trials.csv --output <fresh-directory>`
