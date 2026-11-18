# Report: model C shallow psychometric slope
Date: 2026-11-18   Agent: Codex   Commit: 294cddc (base; assessment uncommitted)
Plan: plans/2026-10-26-paper-accumulation-variant.md, R

## Question
What could improve model C control fits given its shallower psychometric curve?

## Summary
Shallow slope exists in raw simulated probabilities, not solely logistic display smoothing. Deficits concentrate at intermediate coherence with endpoints approximately matched. Existing fit parameters suggest sensitivity/variability/guess tradeoffs to profile; mechanism and best modification are not established. Recommend optimize/check current model first, then a tightly scoped nonlinear sensory mapping comparison using held-out controls.

## Findings
- VERIFIED: displayed four-parameter maximum derivative is0.00683574336 per coherence percentage point for data and0.00493474385 for C (about28% shallower); formula(1−lapse−guess)*var/4. Source display_curve_slopes.csv in control_psychometric_slope_diagnostic_2026-11-18 under dissemination/paper_accumulation/draft_2026-11-15. These are descriptive group curve parameters, not DDM parameters or inferential estimates.
- VERIFIED: raw C P(right) at+18%=0.5998587 versus data0.6417060; +36%=0.6763386 versus0.7424142. At−18%, C0.4259318 versus0.3669346. Endpoints −100%: C0.1747480 versus0.1685484; +100%: C0.8349232 versus0.8437462. Source group_choice_residuals.csv, original psychometric_group.csv.
- VERIFIED: signed intermediate-coherence deficit ((data−C)*sign(coherence), averaged across±18/±36 within mouse) positive in9/10 mice. Source intermediate_coherence_deficit_per_mouse.csv. Descriptive only; no new tests.
- VERIFIED: saved C parameters include drift variability sv, fast-guess mixture and linear drift gain. p_guess ranges0.09447–0.32065; all optimizations stop before max_iterations1000, but finite success/early stop does not establish global optimum. Exact values/paths in control_C_parameter_audit.csv. Effects of joint changes must be checked against RT, not diagnosed from slope alone.
- EXISTING EVIDENCE: reports/2026-11-09-mapping-accumulator-exploratory.md reports modest improvements for nonlinear mappings using JOINT control+pulse fits and a different input version; these do not establish improvement for current control-only model. Do not rerun old campaigns blindly or substitute joint estimates in current B.
- HYPOTHESES: gain/variability/guess compromise, optimization noise/local solutions, or incorrect linear sensory mapping could yield intermediate-coherence underprediction. A compressive mapping is a plausible candidate given matched endpoints, not a proven fix. Behavioral-state extensions require separate joint choice/RT evidence; no generic attention interpretation supported by slope alone.

## What didn't work
No new fit attempted. Display logistic coefficients cannot be used to identify which DDM parameter is wrong. Different asymptotes mean raw var coefficients alone overstate slope difference; use actual derivative and raw residuals.

## How to reproduce
Sources: figure3B_model_C_logit4_2026-11-18/{psychometric_logit4_parameters,psychometric_group,psychometric_mouse,fit_inventory}.csv. Calculate derivative as above; pivot raw probabilities and compare by coherence. For mouse check select abs(coh) in[18,36], pivot model, compute(data−C)*sign(coh), then average within mouse. Read parameters and optimization metadata from fit_inventory paths. Tables and hashes exported to control_psychometric_slope_diagnostic_2026-11-18/.

## Caveats
Finite simulation draws, fitted parameter uncertainty unquantified, group descriptive fit not an individual mechanistic slope. Literature reference checked: Ratcliff and McKoon2008, https://pmc.ncbi.nlm.nih.gov/articles/PMC2474742/; sensitivity/boundary/drift variability affect coupled choice and RT predictions. No new group significance or adequacy claim. No simulation, optimization or pulse analysis executed for this assessment.

## Open questions and next steps
- [ ] Profile gain, sv and fast-guess terms jointly against choice and RT at independent seeds; first determine whether the existing model can improve under the same objective.
- [ ] If underfit persists, compare a minimal nonlinear evidence-to-drift mapping on matched held-out controls, then refit all controls only after candidate selection.
- [ ] Preserve accepted figures/likelihood definition and report the joint choice/RT tradeoff; do not tune to the plotted slope alone.
