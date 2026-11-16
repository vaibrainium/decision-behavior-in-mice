# Independent scientific review and publication strategy

Date: November 12, 2026 (America/Los_Angeles). Reviewer: Codex.
Repository inspected at `b63c9d919edc85e48446be48a8399ba6304b8df0`.

Update November 13, 2026: completed `_v3` recovery tables and all 500 paired fits confirm that matched sample-extrema recovery is complete and supports separation from C. The earlier statement below that this coverage was incomplete has been corrected. The fuller [completed-results synthesis](../reviewer_2026-11-13/COMPLETED_RESULTS.md) also incorporates the dilution analysis, updated timing tables, and later model comparisons into the author's three-part accumulation-first story. It supersedes the narrower recommendation here to make decision variability the primary framing.

This review uses independent scientific judgment. Earlier author-imposed model-selection thresholds, frozen narrative choices, approval gates, and prohibitions on examining particular data subsets are not adopted as scientific requirements. Historical analysis decisions remain relevant to provenance and to distinguishing exploratory development from validation.

## Assessment

There is a credible behavioral result and a potentially interesting model challenge here. **The current analysis package does not yet justify a Neuron-level mechanistic claim.** My recommendation is to develop one focused paper about the constraints that transient evidence places on accounts of decision variability. Treat integration-versus-extrema comparisons as supporting context rather than the principal advance.

The strongest candidate story is:

> Models selected by ordinary choice and response-time distributions can assign variability to the wrong process. Transient evidence reveals additional constraints on those accounts that ordinary trials do not provide.

The first sentence is a hypothesis to establish in this dataset, not a completed finding. Present evidence shows a tension between RT fit and pulse-choice predictions in the tested models. It does not yet show whether the missing process is sensory dynamics, persistent engagement/history states, decision variability, or response execution.

An evidence-matched working title today is **“Transient motion evidence constrains models of perceptual decisions in mice.”** A stronger title about misidentifying the source of variability requires the additional analyses below. I would not submit the current manuscript to Neuron unchanged. Better prose cannot resolve these inferential issues.

## What I actually checked

I inspected the current manuscript and alternative paper outlines, preprocessing notebook cells, the censored quantile likelihood, model simulation and fitting code, cross-validation construction, pulse estimators, recovery and recent model-diagnostic reports, and their saved source tables. I accessed the processed aggregate, accepted-trial, and audited pulse trial tables. I independently recomputed the main signed assignment contrast, an exploratory late-choice sensitivity, cohort summaries, and the contribution of choices versus RTs to the saved control-model comparisons. I also checked the likelihood's pooling behavior with a small synthetic example.

I did **not** refit the model grid, rerun the stimulus rendering, validate acquisition against displayed frames, reproduce every historical report, or inspect every notebook output. Full-data pulse fits and foldwise predictions remain inherited computations. Their numerical provenance is identified below rather than represented as newly reproduced fits. No raw inputs, existing results, manuscript text, or historical plans were changed.

Reproduction of the new checks:

```bash
cd /src
.venv/bin/python dissemination/reviewer_2026-11-12/audit_existing_data.py
```

The script records source hashes and repository commit in `independent_audit.json`. Outputs are local to this review directory. `reviewer_diagnostics.pdf` and `.png` visualize the new checks. Restoring late choices changes the endpoint; it is a labeled sensitivity, not a replacement for the original endpoint or an extension of the stimulus replay.

## Evidence ledger

| Finding | Evidence and assessment |
|---|---|
| Signed pulses redirect behavior | **Independently reproduced:** positive-minus-negative directional response contrast by 5 s = **5.84 percentage points**, mouse-level 95% t CI **1.80–9.89**, 10 mice. The statistic is `(Delta_R - Delta_L)/2`, with nonresponses contributing zero directional response, using within-session/coherence/onset common-support cells. It is not the same estimand as pulse-versus-control effects restricted to RT windows. |
| The directional result survives restoring recorded late choices | **New exploratory check:** restoring **4,102** recorded choices after 5 s in the same trial table gives **6.52 pp**, 95% mouse-level t CI **2.70–10.34**. This supports robustness of redirection to that endpoint change. It says nothing by itself about the temporal retention of a pulse. |
| Cohort differences are substantial | **New descriptive check:** the same by-5-s assignment estimator averages **11.12 pp** in UCLA (**4 mice**) versus **2.33 pp** in UW (**6 mice**). These are confounded apparatus/cohort comparisons, not an experiment on a biological group difference. Do not infer a between-cohort difference by comparing separate significance tests. |
| The overall signed effect is not solely a result of the two most discussed mice | **New post hoc sensitivity:** excluding PSUIM6/7 leaves **4.00 pp**, 95% t CI **0.27–7.72**, 8 mice. This is not multiplicity-adjusted evidence for a newly selected subgroup and does not establish generality across rigs. |
| Control fits favor the tested integration implementations | **Saved scores independently aggregated:** C's advantage over rapid forgetting E averages **12.76 NLL/1,000 control trials**, with **2.55** from choice and **10.21** from RT. Against sample extrema ES the values are **18.74 total**, **1.22 choice**, **17.53 RT**. Most of this comparison's discrimination is in RT distributions. |
| “The models miss the average pulse magnitude” is too broad | **Audited saved results:** response-conditioned early-window data mean **5.48 pp**; fixed-cohort trial-bootstrap CI **3.17–7.87**, whereas the mouse-plus-trial interval is **0.88–9.92**. Many motion-energy integrator means are inside the former interval. The better-supported discrepancy is the per-mouse pattern, particularly in densely sampled UCLA animals. |
| Strong late reversal is a problem for particular fits | **Audited saved results:** the fitted drift-variability term is necessary for the reversal in the reported fixed-parameter counterfactuals; leak/urgency amplify it. Some plain integrator predictions remain within late-window data uncertainty. No-sv variants can eliminate reversal and improve pulse-choice fit while losing combined choice/RT score. This is a targeted constraint, not a refutation of accumulation. |
| The analysis population is restricted | **Independently recounted:** aggregate **134,537 trials, 14 mice, 298 mouse-sessions**; accepted responded set **25,508 trials, 10 mice, 50 mouse-sessions**. The audited table adds **4,537** trials without a response by 5 s, totaling **30,045**. Denominators change across manuscripts and model generations. |

Sources for new findings: `audit_existing_data.py`, `independent_audit.json`, `independent_signed_effects.csv`, and `independent_score_components.csv` in this directory. The original main contrast's raw mouse-level t-test p is 0.009705; the previously specified three-contrast Holm analysis reports adjusted p = 0.019410. The new sensitivities use unadjusted intervals and are not additional confirmatory endpoints.

Sources for inherited pulse diagnostics: `../figures/qc/pulse_effect_bootstrap_2026-11-09_{data,models,heterogeneity}.csv`; `pulse_effect_bootstrap_2026-11-11_ugm_models.csv`; `pulse_effect_bootstrap_2026-11-12_pw_{data,models}.csv`; corresponding `../../.agents/reports/2026-11-09-pulse-effect-bootstrap.md` and `2026-11-13-pulse-weight-signatures.md`. Control score source: `../paper_control/tables/heldout_diff_per_mouse_2026-10-29.csv`. These filenames use the repository's recorded dates, including UTC-dated November 13 artifacts.

## Major reviewer concerns

### 1. The proposed advance needs to be a computational finding

“Mice accumulate visual evidence,” “pulses affect choices,” and “a DDM fits better than a particular extrema model” are not sufficient novelty claims in the present literature. Nor is failure of one sensory-to-response pipeline an identification of a new decision mechanism. The manuscript is conscientious about limitations but frequently makes the analysis procedure—failed gates, revisions, unrun tests—the subject of the scientific story.

Reorganize around a concrete observation and competing explanations. The useful question is **which aspects of ordinary behavior are insufficient to determine how an animal responds to transient evidence, and why?** A strong answer would connect a specific source of variability to several independently predicted behavioral signatures.

### 2. The current objective does not validate use of each trial's stimulus fluctuations

`src/ddm/likelihood_calculator_censored.py` pools simulated outcomes by condition. `scripts/ddm/fit_mouse_ddm.py:select` supplies trial-specific motion energy, but the objective does not score the observed choice and RT conditional on its own motion-energy trajectory. It compares marginal distributions after pooling those trajectories.

Consequently, shuffling the association of stimulus trajectories and observed responses **within the same scored condition** cannot establish whether those trajectories explain the actual trial's behavior. My synthetic check re-pairs predicted rows within condition and gets an exactly unchanged score. The existing report `2026-10-29-likelihood-ignores-trial-me.md` reaches the same substantive conclusion using the pipeline.

This does not make the likelihood wrong, or mean motion energy has no value: stimulus variability can change the model's marginal RT and choice distributions. It means that “we reconstructed trial-specific input” and “we validated trial-specific evidence use” are different claims. A stimulus-conditional evaluation would be particularly valuable because hidden coherence is temporally persistent and cannot be treated as independent framewise evidence.

### 3. A response-conditioned pulse curve is not a memory curve

`pulse_descriptive_package.effect` and `pulse_leak_urgency_signatures.with_bins` compare choices inside bins of **observed RT minus pulse onset**. A pulse can move trials into or out of those bins. Thus, even with randomized assignment, the pulse and control trials occupying a later bin can differ in latent drift, engagement, starting state, and decision survival.

A reversal of the conditional choice contrast can occur without an individual decision variable literally reversing the pulse's contribution. Conversely, a persistent conditional contrast does not measure an intrinsic integration time constant. These summaries remain legitimate posterior-predictive diagnostics when simulated and observed data are processed identically. Their mechanistic interpretation requires a full generative model and selection-aware simulation.

Use signed scheduled-assignment contrasts in cumulative right/left response probabilities as the principal behavioral display. Define the at-risk population from information available before pulse delivery. Keep response-conditioned curves as secondary diagnostics and display both for every candidate. The existing assignment-based response-time module is an appropriate starting point; much of this infrastructure already exists.

### 4. The variability term may be absorbing omitted structure

The simulator uses a persistent per-trial drift offset for `sv`. It is a computational parameter, not a direct measurement of sensory noise. Existing reports document substantial history effects, fast responses, session-position changes in response probability, parameter bounds, and differential RT behavior. A stationary mixture plus independent drift variability may absorb these features.

The fact that sv helps RT fit is not itself suspicious: RT is valid scientific evidence. The interesting issue is that the same parameterization can worsen pulse-choice predictions. Test whether structured history or slow state variation explains both datasets with fewer contradictions. Do not declare that an HMM, delayed engagement, motor gate, or sensory transient is the answer before fitting it. Persistent states can themselves produce response-selection effects and need the same falsification checks.

`src/glm_hmm/` contains infrastructure with human clinical metadata assumptions; its presence is not evidence that a mouse state model has already been validated. Adaptation would require a task-specific data contract and held-out checks.

### 5. The five-second analysis boundary and the response gate need a coherent account

The task often continued past 5 s. A recorded choice after that point is neither an absent response nor necessarily a guess. The late-choice sensitivity strengthens the directional behavioral result, so removing all those trials is not scientifically mandatory merely because it was an earlier author rule.

For a bounded analysis window, retain genuine nonresponses and late responses as right-censored observations. For a full-RT analysis, extend the stimulus representation first and distinguish actual trial termination from administrative censoring. Do not feed a late RT into a five-second stimulus replay.

The responded-only objective conditions on responding, while `MAX_NO_RESPONSE = 0.5` adds a hard constraint on simulated response occurrence. Such a constraint can stabilize optimization but is not a fitted explanation for the observed response rate. Compare the resulting model with the censored objective on common data before interpreting leak or variability mechanistically.

The notebook adds 0.3 s to UW response times; UCLA RT is imported directly. The current simulator floors early simulated RTs at 0.3 s. Resolve, from acquisition code, whether evidence can be accumulated, committed, or updated during the minimum viewing interval and how queued licks are registered. A floor can reproduce a pileup without reproducing the behavior that generated it. A critical risk concerns the RT-dependent model ranking.

### 6. Selection and cohort differences require sensitivities

Only 50 of 298 mouse-sessions enter the accepted set. Restricting analysis to competent performance can be defensible, but generalization must match that population. A null test of session heterogeneity with very few retained sessions is not evidence of stability.

There is also a concrete weakness in the claim that session selection used outcome-independent controls. Preprocessing notebook `0.1`, cell 9, sets `pulse_type = 0` when the response precedes pulse offset; cell 12 then uses those labels for the psychometric acceptance fit. In the audited accepted-session table, **362** genuine scheduled signed-pulse rows carry legacy label zero, including **324 responded rows**. These counts do not quantify how many sessions would change acceptance. They show that the selection-control definition was not wholly independent of response timing. Recompute acceptance using scheduled controls and assess stability under a broader, transparent quality range.

Show apparatus/cohort-stratified estimates. The direction, duration, onset schedule, screen/replay characteristics, training, and animals are not crossed factors; no statistical adjustment can fully identify their separate contributions. In particular, strong effects in several UCLA mice cannot establish uniform mouse generality or explain the source of the cross-cohort contrast.

### 7. Numerical comparison is not the same as decisive model identification

The inspected likelihood decomposes sensibly into outcome and conditional RT-bin terms. I found no basis to call it a simple choice/RT weighting bug. Arbitrarily increasing the choice weight would create a different objective, not solve the biological discrepancy.

However, sparse condition/choice cells drop the RT term when they contain fewer than nine observed RTs. Test quantiles are also constructed from the scored data. The score is a useful binned comparison on fixed folds, but it does not evaluate every mouse or every endpoint at equal temporal resolution. Report scored RT coverage and fixed-bin/density sensitivity. Use common evaluation partitions and compare models on the same trial population. AIC/BIC computed from this binned objective should be supporting approximations; they are not automatic evidence for a unique process.

Stored optimum NLL was optimistic under the fit's simulation draw. Independently rescored tables are the appropriate existing source. In the joint-fit table, power + leak + urgency is first by BIC; normalization + leak is only **2.63 BIC units** behind. The inspected table gives seed SDs of **5.25** and **2.03 NLL units**, respectively. The precise BIC order of these fits is unresolved at that simulation resolution. They also differ more in held-out prediction, so avoid collapsing every criterion into one “winner.” Source: `../figures/qc/model_ic_summary_2026-11-12_rescored.csv`.

The newer fixed-100-ms bits score is simulation-noise limited, as its own second-seed check shows. Bits are log-score units here, not a demonstrated neural information rate or sensory mutual information. Return to a reliable predictive score before using them to rank families.

### 8. Recovery and rejection need calibration

Use the later paired CPU recovery, not the earlier recovery in which competitors were fit to different synthetic datasets. The completed v3 study supports discrimination against both the tested rapid-forgetting and matched sample-extrema models. All 500 fits and 100 hashed CPU datasets were checked in the November 13 follow-up. Recombining two simulated datasets per mouse into many cohorts does not create many independent simulated experiments.

Similarly, the pulse goodness-of-fit calculation uses bootstrap SEs, assumes simulation variance proportional to data variance divided by simulation repetitions, and compares a sum of squared residuals to a nominal chi-square distribution. It does not propagate parameter estimation or calibrate the full fit-and-check operation. Particularly for models already fit to pulse trials, this reference distribution is not established. Use those statistics as discrepancy measures. A parametric bootstrap that simulates, refits, and rechecks the complete procedure is the appropriate basis for a calibrated rejection claim.

### 9. Discovery, model rescue, and genuine transfer have become mixed

The original control-trained pulse prediction is a valid historical transfer test if its construction preceded inspection of the outcome. Later joint fits, pulse-only fits, pulse-weight changes, and candidate selection after examining pulse residuals are exploratory model development. They cannot be described collectively as predictions of untouched perturbation data.

A new blocked or session-level split can assess robustness and out-of-sample fitting within the existing cohort. Because the dataset and signatures have already informed model design, that split does not retrospectively recreate pristine confirmatory validation. Be explicit about that limitation. Report the development trajectory briefly in the supplement rather than make it the main Results narrative.

## A focused route using existing data

| Priority | Analysis | What it would resolve |
|---|---|---|
| 1 | Unify the scheduled-assignment trial table, document acquisition timing, compare scheduled-control acceptance with existing acceptance, and retain a censored endpoint. Reuse the independent late-choice sensitivity and add a transparent quality-range sensitivity. | Whether the phenomenon and model comparison survive plausible preprocessing choices. |
| 2 | Display mouse-level signed cumulative response contrasts and common-support pulse effects, with cohort strata and uncertainty. Compare these with response-conditioned diagnostics. | Whether the apparent temporal contradiction survives an assignment-based estimand, and where it is concentrated. |
| 3 | Evaluate a small model set on common blocked folds with choice, RT, and censoring components. Include an empirical history/RT baseline. Develop stimulus-conditional scoring where tractable; otherwise explicitly restrict the claim to marginal distributions. | Whether the ranking depends on a particular RT readout, independent-trial assumption, or nuisance response process. |
| 4 | Contrast the current independent-drift-variability account with one parsimonious history/slow-state account and one justified sensory or response-dynamics account. Fit ordinary trials first; compare pulse predictions, RT serial dependence, high-coherence errors, and response occurrence. | A positive explanation for the present fit-versus-pulse tension. Each candidate must predict more than the statistic it was introduced to fix. |
| 5 | Simulate and recover those finalists at the actual sample sizes and schedules, including the competing data-generation mechanisms. Use common datasets, multiple starts and independent simulation seeds; quantify parameter and prediction uncertainty. | Whether the proposed distinction is identifiable and numerically reliable in these data. |
| 6 | If a general principle emerges, test its predictions on an already public decision dataset with available raw stimulus and RT information. | External support using existing data, particularly valuable for a broad journal claim. This is optional for a narrower paper, not already completed work. |

These are priorities, not inherited approval gates or chosen p-value thresholds. Start with the cheapest analyses that can change the interpretation. A limited model set is warranted because dozens of variations have already explored similar assumptions; another pulse-specific weight on every model is unlikely to clarify the mechanism. New computational fits are not experiments, but may take substantial compute. They were not run as part of this review.

## Manuscript architecture

1. **Task, analysis population, and robust pulse redirection.** Show individual mice, scheduled assignment, apparatus differences, and uncertainty before the models.
2. **Ordinary behavior constrains competing models, mainly through RT.** Include the source of the score difference, absolute fit, censoring, and appropriate paired recovery.
3. **Transient evidence exposes a specific predictive contradiction.** Distinguish control-trained transfer from joint-fit inadequacy. Show cumulative and conditional predictions together.
4. **A constrained account of variability explains additional behavior.** This is the missing result that could substantially strengthen the paper. If it fails, report the bounded negative result without claiming a new mechanism.
5. **Generality and identifiability.** Recovery and uncertainty are essential; external existing-data replication is a strong enhancement if feasible.

Move replay-validation detail, historical model grids, failed exploratory extensions, and superseded manuscript logic into a concise supplement. Remove unwarranted precision in prose: six decimal places of behavioral effect do not represent biological precision. The manuscript currently predates several important analyses; update its denominators and recovery claims before polishing its Discussion.

The manuscript also contains explicit missing-source placeholders at lines 114–120 for animal strain, sex, age, welfare and ethics records, sample-size rationale, blinding, training criteria, and display hardware. Lines 265–275 still lack author/funding/contribution declarations and final software/data-release provenance. These are actual submission gaps, not requests for new experiments. Recover the facts from study records; do not fill them by assumption. The draft's policy references also reflect its earlier journal target.

## Neuron judgment

This is an editorial assessment, not a journal requirement or an acceptance forecast. A behavior/computation paper can make a major neuroscience contribution; neural recordings are not logically required. The decisive issue is whether these data support a broadly informative, well-identified computational advance. The inspected publication pipeline currently supplies behavioral and model results, not a new validated neural mechanism. The README's mention of electrophysiology does not establish that usable neural analyses exist elsewhere.

My strongest Neuron-oriented route is a demonstrated **misattribution of decision variability**, with a compact alternative explaining both ordinary and perturbation behavior and, ideally, an independent existing-data test. A weaker but defensible route is a careful preparation-specific paper documenting robust pulse effects and the predictive limits of specified models. The latter should be framed and targeted honestly if the positive explanation cannot be established.

The literature review in `LITERATURE.md` explains why neither a first-in-mice claim nor an unrestricted rejection of accumulation is available. It also identifies concrete precedents for a more ambitious computational contribution. **There is a publication story here; a Neuron story remains a research hypothesis.**
