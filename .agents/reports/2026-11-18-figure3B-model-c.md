# Report: model C only in Figure 3B
Date: 2026-11-18   Agent: Codex   Commit: 294cddc (base; update uncommitted)
Plan: plans/2026-10-26-paper-accumulation-variant.md, R

## Question
Author requests psychometric and chronometric full-control fits for current best candidate C; pulse deferred.

## Summary
B now contains two side-by-side axes for C alone, replacing the five-model preview for current review. Held-out scores assess unseen-control prediction in A; full-control fits supply parameters and curves in B. No new simulations, fits or scores.

## Findings
- VERIFIED: all five exported C/data source tables exactly equal the corresponding subsets of the verified preceding B tables (pandas assert_frame_equal); source compiles, PNG visually inspected.
- VERIFIED: source directory figure3B_control_fits_2026-11-18; output figure3B_model_C_2026-11-18, both under dissemination/paper_accumulation/draft_2026-11-15. Tables/caption/hash manifest and PNG/PDF/SVG retained. C full-control source fits_resp_final, as prior report; no CV-fit substitution.
- AUTHOR DECISION: focus on C fitted psychometric/chronometric curves; pulse deferred. “Normative” interpreted from context as chronometric, matching previous requested mean RT plots; C is not claimed to be an optimal normative model.

## What didn't work
No failed scientific checks. Font subsetting generated verbose logging without affecting exports.

## How to reproduce
```bash
.venv/bin/python -m scripts.paper.figure3B_model_c --input dissemination/paper_accumulation/draft_2026-11-15/figure3B_control_fits_2026-11-18 --output dissemination/paper_accumulation/draft_2026-11-15/figure3B_model_C_FRESH
```
Base source provenance/verification: reports/2026-11-18-figure3B-control-fits.md. Renderer hashes in output manifest.json.

## Caveats
In-sample curves do not independently validate unseen-control prediction. Shading is data SEM, not parameter uncertainty. Same observed RT cell eligibility and documented one-trial Fig1 population difference retained. Connections between tested coherences are visual guides, no additional psychometric fit/smoothing. No pulse analysis or universal model optimality claim.

## Open questions and next steps
- [ ] Author assess model C-only B.
- [ ] Continue recovery C after B is settled; A alternative choice remains deferred.

## Full-control optimization provenance verified — 2026-11-18
Author asks whether C parameters were actually fitted on all controls rather than only evaluated there. Read all10 actual C fit pickles listed in B fit_inventory.csv: split=control, success=True, n_train equals every modeled responded control for that mouse. Counts DBM12 785, DBM13 347, DBM14 396, DBM15 514, DBM5 1213, DBM6 1502, PSUIM10 259, PSUIM5 1337, PSUIM6 3566, PSUIM7 4095 (total14014). Parameters in B come from these independently optimized full-control fits, not CV estimates averaged or applied to all controls. Fit metadata includes optimizer iterations/training objective. No new optimization was performed for figure rendering because these full-control fits already exist. Author convention: model comparison on held-out controls; full-control estimates for parameters/fitted curves. Whole data here means all eligible controls per mouse, with pulse explicitly deferred.

## Four-parameter psychometric curves — 2026-11-18
Author requests smooth four-parameter psychometric curves instead of joined coherence segments. Current output figure3B_model_C_logit4_2026-11-18 under draft directory. Exact src/utils/pmf_utils.py logit_4 helper/default bounds, same as Figure1, fitted separately to equal-mouse data and C-predicted proportions (unweighted least squares). Data dashed gray, C solid black; raw data points visible. This is descriptive logistic approximation to simulated C probabilities, not direct DDM predictions on a new coherence grid. Coefficients/dense curves exported in psychometric_logit4_parameters.csv / psychometric_logit4_curves.csv. VERIFIED all original tables including RT match preceding C-only B exactly; recomputed every dense curve from exported coefficients with scipy.special.expit; both401-point curves bounded/monotone. Script compiles; PNG inspected. Initial caption concatenation syntax error corrected before rendering. No DDM optimization/simulation or pulse work. Reproduce prior C-only rendering command with --psychometric logit4 and fresh --output. Next author assess smooth-curve B.
