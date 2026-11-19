# Corrected paired-parameter panel: single-start optimization issue

The original v4 paired p values are superseded. Their arithmetic and Holm correction were correct for the estimates used, but the single-start psychometric helper missed lower-WLS solutions for two individual left-pulse curves (DBM12/DBM13). User confirmed α=midpoint and β=slope coefficient.

v5 uses the same equation, trial counts, bounds, data and all10 mouse pairs. Each curve has19 starts (the original solution plus18 predetermined starts); fits are selected solely by weighted residual sum of squares. Parameter tests are computed afterward. No animals were dropped, correction family was not changed, and a favorable p value was not a fit-selection criterion. The group curves in A were separately audited and their residual sums of squares match best multi-start values to numerical tolerance, so A remains unchanged.

Corrected exact paired sign-flip pα=0.005859375, pβ=0.13671875; Holm across the same2 contrasts gives0.01171875 and0.13671875. Paired-t sensitivity with the same2-test correction gives approximately0.01549 and0.16245. Nine mice have the expected α direction. Mean α(right−left)=−22.2818 coherence-percentage units. All primary/difference/test CSVs and individual curves are exported.

This fixes an optimization problem, not all parameter-identification limitations. Some β values describe near-step curves with poor Jacobian conditioning. Conditional coefficient tests do not propagate individual curve uncertainty, and left/right curves have different observed coherence support. A sampling check among numerically equivalent optimizer solutions (500 combinations, not new animals or bootstraps) leaves the rawα p value unchanged; this is an optimizer-stability check, not an uncertainty interval.

The earlier control-derived shared-asymptote sensitivity remains separate. Changing asymptote assumptions can change fitted midpoints, so no robust-to-all-assumptions or mechanistic claim is made. Original v4 outputs remain archived with an explicit superseded notice. No decision-model parameters, temporal coefficients, assignment-effect estimates or raw data were changed.

Reproduce corrected figure:
```bash
.venv/bin/python -m scripts.paper.review_pulse_results --output <fresh-directory> --fit-pulse-psychometric --extend-pulse-curves --paired-psychometric --multistart-paired
```
Independent fit audit: scripts.paper.audit_pulse_psychometric_pairs. Independent arithmetic/source/numerical checks: .agents/reports/2026-11-18-paired-psychometric-audit-check.py. See pulse_psychometric_pair_audit_2026-11-18_v2/ for all380 starting-point solutions and original-versus-best objective comparisons.
