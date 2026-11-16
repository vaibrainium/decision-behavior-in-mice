# Ranked next analyses using the existing data

These are proposed exploratory analyses, not results or revived historical decision rules. Their purpose is to choose one compact explanation of the joint RT/pulse mismatch. The literature assessment is in [REVIEW.md](REVIEW.md).

## 1. Start with history and trial chronology

The next concrete analysis should be **history-conditioned choice bias and RT structure**, using the already documented history effect rather than repeating a generic history regression.

Inputs available now:

- Aligned pulse trial table: `/mnt/data/processed/pulse_followup/20261023T191030Z_fa8de8b/data/trial_table.csv`. It contains previous choice/outcome, session identifiers, position, schedule, response and RT.
- Broader chronology and task metadata: `/mnt/data/processed/aggregate_data.csv` and `valid_data.csv`. The existing `scripts/behavior/explore_behavior.py` documents selection and history construction.
- Existing fitted benchmarks and simulations in `fits_joint_unfreeze_pulse_time_weights` and `dissemination/response_delay_2026-11-14/`.

First audit previous-trial definitions, correction trials, session boundaries, and the reported target anti-repetition. Do not concatenate the next retained trial as if omitted/late trials never occurred. Use a unique mouse/session key; session strings can repeat between animals. Preserve the original responded-only comparison as a matched target and distinguish any broader sensitivity analysis.

Produce per-mouse estimates of:

1. Choice repetition bias as a function of current RT, separately after rewarded and unrewarded choices, with current coherence, scheduled pulse and session accounted for.
2. Residual choice runs and residual RT autocorrelation after accounting for evidence, first-order history, session and position. Examine more than a single lag so a persistent regime is distinguishable from an immediate history effect.
3. Pulse effect versus **pretrial** history or predicted behavioral regime, standardized to a common coherence/schedule composition. Reuse the existing signed pulse estimators and the all-scheduled cumulative-response analyses; do not label a new RT-conditioned curve a causal attention effect.

The first two distinguish predictable directional bias from unstructured sensitivity variation. They do not prove that history causes the average randomized pulse effect. The third asks whether state composition could explain the mismatch between aggregate RT fits and conditional pulse profiles.

Use within-session blocks for trial uncertainty and mice for population statements. Report effect sizes and uncertainty. If several diagnostic endpoints are formally tested, declare that family and correct it, for example with Holm; do not count bins, sessions or simulation seeds as independent mice. A weak serial effect is not proof of independence without adequate sensitivity.

**Deliverable:** one chronology audit and a per-mouse figure linking history-conditioned bias, residual persistence and existing pulse/RT misfit. This is the most informative inexpensive next step.

## 2. Compare the location of the history effect

The first new fitted comparison should be motivated by the preceding conditional RT pattern. Candidate forms are:

| Candidate | Changed component | What distinguishes it |
|---|---|---|
| Static benchmark | Current independent drift variability | Baseline for absolute choice/RT and pulse prediction |
| History in drift bias | `b_t = b0 + h_win * previous_choice * previous_reward + h_loss * previous_choice * previous_error` | Persistent directional accumulation bias; conditional repetition-versus-RT pattern |
| History in starting point | The same history predictors through a bounded starting-point link | A different effect on the leading edge and conditional choice bias |

The coding above is schematic: choice must have a signed definition; reward/error and previous-trial eligibility must be explicit. Preserve the existing starting-point bounds through the link. Compare equal history-predictor complexity, refit common parameters, and retain a residual sv term initially so that a decline in unexplained variability can be assessed rather than forced.

[Urai et al.](https://doi.org/10.7554/eLife.46331) motivates the comparison, but the diagnostic predictions must be simulated with the actual evidence streams, floor, deadline and guesses. Their human conditional-bias pattern is not a universal classifier to apply by eye.

Do not start by fixing all control parameters and modifying one history coefficient. That counterfactual is useful for understanding model behavior but is not a fitted model comparison.

## 3. Examine persistent strategies only if supported

If residual serial structure remains, compare:

- a static history GLM;
- a continuously varying sensitivity/bias account;
- a small GLM-HMM with stimulus and the same history regressors.

This is a diagnostic comparison before a joint latent-state DDM. The repository contains general GLM-HMM utilities, but reviewed configuration/data-preparation code also serves a different human/color task. An aligned, audited mouse pulse/RT state fit was not located. Audit trial masks, features, session boundaries and output provenance before reuse.

Use held-out sessions where enough sessions and condition coverage exist. For mice with too few sessions, use clearly labeled held-out blocks/trials and report the narrower generalization target. Do not claim new-session generalization from the original random trial folds.

For pulse tests, infer the probability of the current state **from information preceding the current trial**. Smoothed state estimates using the current choice, current RT or future outcomes cannot serve as independent pretrial attention labels. A complementary masked-outcome analysis can test imputation, but it addresses a different target.

Validate with response timing or another outcome that was not used to infer the choice states. A state model winning choices alone does not solve the present joint RT/pulse problem. Compare continuous and discrete models before asserting literal discrete states. [Ashwood et al.](https://doi.org/10.1038/s41593-021-01007-z), [Roy et al.](https://doi.org/10.1016/j.neuron.2020.12.004), [Hulsey et al.](https://doi.org/10.1016/j.celrep.2024.113709).

If omissions are incorporated in a later sensitivity model, distinguish “no recorded response by five seconds” from absence of stimulus-guided processing. The repository documents accurate choices recorded later than that deadline. Missing observations and gaps must still propagate the state dynamics.

## 4. Keep positive gain as a minimal, testable alternative

Compare these computational assumptions:

`additive variability: drift(t) = k * e(t) + b + eta`

`gain variability: drift(t) = k * G * e(t) + b`, with `G > 0` and mean one.

Here `e(t)` includes the same baseline motion and pulse components as the existing models. A lognormal G is a proposed positive parameterization, not a literature-established attention distribution. Guesses, the sensory front end, pulse weights and response mapping should be matched.

There is a useful mathematical distinction for approximately constant nominal evidence C. Additive eta gives a coherence-independent between-trial drift variance, whereas gain gives a contribution proportional to `k² * C² * Var(G)`. Moreover, pulse sensitivity is coupled to the same G that scales baseline evidence. These are model consequences, not empirical findings; real motion-energy fluctuations, bias, bounds and response selection must be included in forward predictions.

First run a bounded simulation/profile study across plausible gain variation and common control parameters. Inspect:

- correct and error RT distributions at each coherence, especially the PSUIM7 conditions driving the score gap;
- baseline psychometric sensitivity and high-coherence errors;
- both signed pulse profiles, early amplitude and sustained influence;
- simulated response fractions and the existing all-scheduled response contrasts.

This establishes whether the candidate has a plausible route to explaining both constraints. A failure at one fixed parameter vector does not disprove it. If it looks viable, pilot a full common-parameter refit on the original folds before extending to the cohort.

Slow gain is a separate hypothesis from iid gain. For example, a stationary latent process could make `log(G_t)` correlated across trials. Its persistence needs serial observations or a sequential likelihood. It cannot be identified merely by observing that a correlated simulation fits aggregate condition-level RT histograms. [Goris et al.](https://doi.org/10.1038/nn.3711) motivates examining persistence; it does not validate a behavioral attention label.

## 5. Respect what the current scorer can identify

The existing likelihood pools simulated outcomes by coherence and scheduled pulse. It does not directly reward reproducing the actual ordering of history states or trial-by-trial motion-energy/choice associations. This was already audited in the repository. A model can match pooled distributions while getting temporal organization wrong.

Do not simply split every cell into many history/state categories while preserving nine independently estimated data-quantile RT bins: held-out cells can become too sparse and silently lose RT contributions. Any modified scoring scheme needs its own validation.

For a later joint state model, a principled target is a sequential predictive mixture:

`p(choice_t, RT_t | past, stimulus_t) = sum_s p(state_t=s | past) * p(choice_t, RT_t | state_t=s, stimulus_t)`.

One possible implementation uses training-defined response-time bins and state/condition emissions, integrating uncertainty through a forward filter. This is a design proposal, not implemented or validated here. Alternatives must preserve a fair common target for all models and explicitly retain choice/RT dependence.

Pulse summary checks should not be added as another independent likelihood for the same outcomes. Keep them as targeted predictive adequacy tests.

## 6. Reserve an encoder or onset model for a specific residual

Only pursue a new sensory encoder if the residual shows the predicted context, coherence or timing dependence. Already tested power/normalization models are not unfinished work. A new context-dependent mechanism must make a different prediction and account for sustained controls as well as transient pulses.

The 2026 macaque RDK adaptation study motivates this distinction but does not identify its exact algorithm. Cheadle's adaptive-gain account predicts a preference for context-consistent samples, not unrestricted pulse amplification. Decision-onset accounts differ from the already tested postdecision delay. [McGaughey and Gold](https://doi.org/10.7554/eLife.110685), [Cheadle et al.](https://doi.org/10.1016/j.neuron.2014.01.020), [Ueno et al.](https://doi.org/10.1007/s00221-024-06862-3).

Do not combine a free pulse-specific attention burst, onset delay, arbitrary temporal kernel, state-dependent bound and leak in the first extension. That combination could interpolate the observed curve while making the source of the effect less identifiable.

## Publication-level validation if a candidate succeeds

Keep the successful model compact and show improvement beyond the pulse residual used to motivate it. Demonstrate held-out choice/RT prediction, both pulse signs, coherence dependence and serial/state features where claimed. Report individual mice as well as the group.

Recovery must use fixed identical synthetic datasets for competing fits, match the actual stimulus/schedule and response selection, and refit every parameter fitted to real data. Include the nearby competitors that could be mistaken for the chosen mechanism. Propagate fitted-parameter uncertainty into pulse predictions. Good fit without recovery does not establish mechanism identification.

The desired contribution is that transient perturbations distinguish sources of decision variability otherwise confounded by ordinary behavior. A positive gain fit by itself, or rediscovering mouse state switching, is not that contribution. If the mechanisms remain indistinguishable, report the computational constraint and its limits rather than assigning attention or a precise memory time constant.
