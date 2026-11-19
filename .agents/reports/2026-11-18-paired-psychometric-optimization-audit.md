# Report: corrected paired psychometric fit optimization
Date: 2026-11-18   Agent: Codex   Commit: eef364b (base; audit/correction uncommitted)
Plan: plans/2026-10-26-paper-accumulation-variant.md, paired psychometric audit subsection

## Question
Author challenges why pairedα is not significant; audit arithmetic, optimization and identifiability.

## Summary
Found actual optimizer problem: the author helper’s single start missed lower-WLS fits for DBM12/DBM13 left-pulse curves. Original p arithmetic was correct for those suboptimal coefficients. Same equation/bounds/weights/mice with19 starts per curve yields corrected Holm pα0.01171875, pβ0.13671875. Updated B/full figure as v5. No exclusions, correction changes or p-driven fit selection. Remaining fit-identification caveats retained.

## Findings
- VERIFIED:380 starting-point fits (20 curves×19). Native solution plus18 predetermined starts. Minimum WLS selected before statistics. DBM12 left weighted-SSE improvement0.0305505907, α−36.25449→−19.40663; DBM13 left improvement0.5339242336, α−28.27322→−5.78199. Source pulse_psychometric_pair_audit_2026-11-18_v2/fit_audit.csv and all_starts.csv under draft directory. Several other coefficients, particularlyβ, vary with negligible SSE changes; not all parameter estimates are well identified.
- VERIFIED: correctedα mean paired right−left−22.281809, median−16.384243, dz−1.0785, unadjusted t95% CI[−37.061031,−7.502588];9/10 negative. Raw exact sign-flip p6/1024=.005859375; Holm overα/β=.01171875. Paired-t sensitivity rawp=.007743, Holm≈.015486. Source v5/source_data/fig4_B_paired_tests.csv. No point-estimate exclusion or alternative test selected for significance.
- VERIFIED: β mean paired difference−1.010929, median−.021009, dz−.4812; raw/adjusted exactp=.13671875. Some steep fitted β values remain weakly constrained. Same source.
- VERIFIED: coefficient/curve/WLS checks against independent audit pass; all1024 sign patterns and unchanged Holm family independently reproduced. All20 curves retained, same subject alignment.500 combinations of near-minimum-SSE optimizer solutions (within1e-5 SSE, numerical tolerance only) give the sameα rawp=.005859375. This is numerical robustness, not biological/parameter uncertainty. Source v5/verification.json and saved independent audit-check script.
- VERIFIED: group A multi-start audit improves unweighted SSE by<1e-10 for either direction; A curves/data unchanged. Original temporal/assignment C–E source tables unchanged. Figure v5 focused B inspected, scripts compile. v4 paired panel marked superseded; original files preserved.

## What didn't work
The original single-start helper can return a finite curve-fit solution at a local minimum, so trusting its coefficients for paired inference was insufficient. The first audit run hit tiny floating-point bound mismatch when reconstructing guess_rate=1−upper_asymptote; initial seeds now clipped to the unchanged bounds. Failed empty output preserved; successful audit uses fresh _v2 directory. Shared-asymptote fitting does not resolve every parameter-identification concern and was not substituted to obtain significance.

## How to reproduce
```bash
.venv/bin/python -m scripts.paper.audit_pulse_psychometric_pairs --input dissemination/paper_accumulation/draft_2026-11-15/figure4_revision_2026-11-18_v4 --output <fresh-audit-directory>
.venv/bin/python -m scripts.paper.review_pulse_results --output <fresh-figure-directory> --fit-pulse-psychometric --extend-pulse-curves --paired-psychometric --multistart-paired
.venv/bin/python .agents/reports/2026-11-18-paired-psychometric-audit-check.py
```
Actual outputs: pulse_psychometric_pair_audit_2026-11-18_v2/ and figure4_revision_2026-11-18_v5/ under dissemination/paper_accumulation/draft_2026-11-15. All start solutions, source/script hashes, revised coefs/tests/curves and independent checks retained. Source scripts audit_pulse_psychometric_pairs.py, pulse_paired_psychometrics.py, review_pulse_results.py.

## Caveats
Multi-start numerical improvement is not proof of global optimum or parameter identifiability. Tests condition on point estimates, without propagating curve uncertainty; asymmetric/sparse coherence ranges persist. Significant correctedα supports an exploratory pulse-dependent horizontal shift, not a new accumulation/attention mechanism. β non-significance does not establish equal slopes or failure to use pulses. No raw data/model-C parameters/temporal or assignment statistics changed; no commits/pushes.

## Open questions and next steps
- [ ] Author review corrected paired B; retain explicit fitting/uncertainty limitations.
- [ ] Continue Figure4 temporal-panel edits after B settles.
