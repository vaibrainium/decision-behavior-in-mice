# Completed evidence for the mouse motion decision paper

Date: November 13, 2026. Repository: `b63c9d919edc85e48446be48a8399ba6304b8df0`.

Follow-up: the proposed model-to-dilution comparison is now complete. See [What the pulse trials establish about accumulation dynamics](../pulse_dynamics_2026-11-13/RESULTS.md) and its figure. A no-leak integrator also produces a late decline under the historical readout, so that decline cannot uniquely identify forgetting. The comparison sharpens the joint constraint from pulse effects and RT predictions.

The completed results support the proposed paper structure: mice perform the task; control behavior favors accumulation over the tested nonaccumulation alternatives; pulses then constrain the dynamics and expose limits of the fitted accounts. The control-model identification is further advanced than the earlier review stated. The pulse-model work is also extensive: the question is how to interpret those completed comparisons, not whether to begin fitting pulse trials.

## Corrections to the earlier assessment

The statement that matched-extrema recovery was incomplete was wrong. The October 30 report described incomplete outputs, but the later `recovery_*_2026-10-30_v3.csv` tables contain the completed analysis. All 500 underlying fit files are present. They reference 100 fixed CPU-generated datasets whose SHA-256 hashes match the manifest; training and test response counts agree across all candidates for each dataset. The v3 cohort rates and confusion matrix reproduce from those files.

The updated timing tables also supersede parts of the prose report. In `huk_shadlen_replication_2026-10-29_timecourse_tests.csv`, the mouse-level directional contrast at 0.9–1.2 s after pulse onset has Wilcoxon p = 0.0078125, Holm p = 0.046875. The earlier prose saying that no bin survives correction is stale for that table. Its estimates include different numbers of estimable mice across bins.

Several previously suggested analyses are already complete: nominal-input controls, joint control/pulse fitting, pulse-only fitting, power-law and normalization mappings, pulse weights shared or specific to onset, urgency-gating fits, drift-variability counterfactuals, and data/model pulse uncertainty comparisons. They should be interpreted together.

The audit script in this directory catalogs 236 result CSVs and 75 reports containing Summary sections. It reproduces control comparisons from 400 saved fold-fit files, checks the completed recovery, and recomputes the reported late dilution contrasts' Holm adjustment. It runs no new model fits or simulations. See `completed_results_audit.json` and the adjacent inventories for source-level detail.

## Part one Mice perform the task

The accepted responded dataset contains 25,508 trials from 10 mice and 50 mouse-sessions. The broader compiled dataset contains 134,537 trials, 14 mice, and 298 mouse-sessions. The audited assignment table contains 30,045 trials in the accepted sessions, including 4,537 without a response by 5 s. The model input set has 25,493 responded trials because 15 trials with problematic pulse duration were excluded.

Individual psychometric functions, chronometry, conditional accuracy, fast-response behavior, session variation, and history effects have already been explored. The appropriate first result is that choices depend on the motion stimulus, with substantial variation across mice and task implementations. The control chronometric trend is in the expected direction but does not quite survive its three-test Holm family; it should not be presented as the decisive evidence for accumulation.

High-coherence fast errors and the 0.3 s response boundary matter for the response model. The component comparison supports fast guesses: removing them costs 430.5 summed held-out NLL, with a mean cost of 24.9 per 1,000 trials; corrected t p = 0.001 and Wilcoxon p = 0.023. Ordinary control behavior gives much less clear population evidence for leak and urgency. This is useful model construction, not an unfinished descriptive task.

Sources: `../paper_accumulation/tables/behavior_exploration_2026-10-29_{provenance,psychometric,chronometric,rt_summary,tests}.csv`; `components_group_2026-10-28.csv`; `../../.agents/reports/2026-10-29-control-descriptives.md`; prior independent counts in `../reviewer_2026-11-12/independent_audit.json`.

## Part two Control behavior favors the tested accumulators

### Held out model comparisons are complete

The following are means over mice of held-out NLL differences per 1,000 control trials; positive values favor the common accumulator C. C and the matched alternatives include drift variability and fast-response components. DDMx/ESx are simpler paper-exact nominal-input baselines.

| Alternative | Total advantage for C | Choice component | RT component | Holm t p for total | Holm Wilcoxon p for total |
|---|---:|---:|---:|---:|---:|
| Rapid forgetting E | 12.76 | 2.55 | 10.21 | 0.037 | 0.059 |
| Matched sample extrema ES | 18.74 | 1.22 | 17.53 | 0.023 | 0.055 |
| Paper-exact integration DDMx | 28.20 | 3.64 | 24.56 | 0.037 | 0.059 |
| Paper-exact extrema ESx | 30.24 | 0.12 | 30.11 | 0.037 | 0.059 |

The advantage is principally an RT-distribution result. That is informative: the full response distribution can constrain a strategy. The evidence is stronger against matched alternatives than a comparison with simpler models missing important response components. The population t and Wilcoxon tests differ near their conventional thresholds; report both rather than selecting whichever is favorable. Leave-one-mouse-out mean advantages remain positive.

The stored fold likelihoods and test counts reproduce the existing comparison tables. Five-fold scoring covers 14,014 control trials. The audit checks matched test counts across models; it does not rerun model simulations at new seeds.

Sources: `../paper_control/tables/heldout_{group,diff_per_mouse,lomo}_2026-10-29.csv`; `control_fold_inventory.csv` and `control_differences_reproduced.csv` in this directory.

### Completed paired recovery strengthens this inference

The complete recovery includes five generators and five fitted candidates, 10 mice and two replicates per mouse: 500 fits on 100 synthetic train/test dataset pairs. For the matched candidates, the existing group-test exercise gives:

| Generating strategy | Recombined cohorts reproducing C better than E | Recombined cohorts reproducing C better than ES |
|---|---:|---:|
| Accumulation C | 1,024 of 1,024 | 1,024 of 1,024 |
| Rapid forgetting E | 0 of 1,024 | 0 of 1,024 |
| Sample extrema ES | 0 of 1,024 | 0 of 1,024 |

This supports the claim that, within the tested candidates and generating-parameter range, the real-data preference for C can distinguish it from both matched nonaccumulation accounts. It is not a universal proof against all nonintegration strategies.

The 1,024 cohorts recombine the same two replicates per mouse; they are not independent new simulations or biological experiments. Recovery uses one independent train/test dataset pair per replicate, whereas the observed comparison uses five-fold CV. At the individual-dataset level E and ES often confuse with one another; that does not negate their group-level separation from C. On ES-generated datasets, C is never the best candidate in the five-model comparison; E and ES each win 10 of 20.

Sources: `../paper_control/tables/recovery_{cohort_rates,confusion,per_dataset}_2026-10-30_v3.csv`; the reproduced tables and `recovery_fit_inventory.csv` in this directory; `/mnt/data/processed/ddm/recovery_full_cpu_resp/` and `recovery_datasets_cpu_2026-10-29/manifest.json`.

### The conclusion survives an input sensitivity

On matched nominal-coherence control inputs, C retains an advantage of 15.64 NLL per 1,000 trials over E and 10.27 over ES. The corrected t p values are 0.0061 and 0.0481; the corresponding Wilcoxon p values are 0.0117 and 0.0645. There is no clear advantage of motion-energy input over nominal coherence in that control comparison.

Later joint fits extend the relative accumulator preference across linear motion energy, power-law and divisive-normalization mappings, and nominal input. Summed held-out advantages over the extrema candidates range approximately 241–593 NLL units across these comparisons. Those large exploratory grids support robustness of relative ranking; each entry is not a separate confirmed group finding.

Sources: `../paper_control/tables/heldout_nominal_group_2026-10-30.csv`; `../figures/qc/mapping_accumulator_{ranking,integrator_vs_extrema,nominal}_2026-11-09_final.csv`.

### Auxiliary evidence does not independently settle strategy

The stimulus-aligned motion-energy kernel is small and uncertain. The response-aligned fluctuation-kernel check did not produce an adequate fit from either tested candidate under that procedure. The paper-exact Stine-style models, without the response components needed here, discriminate weakly and fit worse than the common model. These results belong in the supplement and qualify the evidence; they do not erase the matched-model recovery result.

Sources: `../paper_control/tables/control_tests_2026-10-29.csv`; `../../.agents/reports/2026-10-26-fluctuation-kernel-observed.md`, `2026-10-28-stine-exact-models.md`. Earlier unpaired recovery is superseded by the completed paired CPU analysis.

## Part three Pulses constrain accumulation dynamics

### The directional effect is established

The assignment-based positive-minus-negative directional response contrast is 5.84 percentage points, with a 95% mouse-level t interval of 1.80–9.89 and Holm p = 0.0194. This reproduces independently. Restoring recorded choices after 5 s yields an exploratory endpoint sensitivity of 6.52 points, with interval 2.70–10.34.

The psychometric parameter analysis predominantly suggests a horizontal directional shift. The early right-minus-left bias shift is -17.05 percentage-coherence units, with bootstrap interval -32.11 to -4.41; its post hoc six-test Holm p is 0.0468. There is no detectable slope difference. This supports a directional biasing effect, without establishing identical sensory sensitivity under every pulse condition.

Sources: `../reviewer_2026-11-12/independent_audit.json`; `../paper_accumulation/tables/pulse_direction_by_time_2026-10-28.csv`.

### Correctness after the pulse has been analyzed extensively

The monkey-style analysis includes congruent/incongruent psychometric and chronometric curves, time from pulse to response, per-mouse overlays, direct comparisons, and decomposition of directional and shared effects.

The updated pooled logistic decomposition has positive directional coefficients of approximately 0.43, 0.66, and 0.43 log-odds in the 0.3–0.6, 0.6–0.9, and 0.9–1.2 s bins. All three have mouse-bootstrap Holm p approximately 0.023. A shared component—an effect of any pulse toward the correct side—does not survive per-bin correction. Thus the data support a directional influence after the pulse. They do not establish a separate nondirectional accuracy mechanism or a robust congruent/incongruent magnitude asymmetry. One updated mouse-level timecourse bin, 0.9–1.2 s, also survives Holm, as described above.

Pooled curves and per-mouse summaries answer related but different questions: pooled regressions have common slopes and unequal trial information, while mouse-level summaries can lose sparse bins. The directly reported congruent-versus-incongruent average effects do not show a reliable difference. AUC analyses should not be the principal asymmetry evidence because baseline correctness affects the score distribution.

Sources: `../paper_accumulation/tables/pulse_decomposition_2026-10-30_bins.csv`; `huk_shadlen_replication_2026-10-29_{timecourse_tests,overlay_summary,congruency_mouse_150ms}.csv`; `pulse_congruency_tests_2026-10-28.csv`; `congruency_choice_effect_2026-10-30_summary.csv`; `../../.agents/reports/2026-10-29-huk-shadlen-replication.md` and its later addenda. The global cluster-Wald results are not used to strengthen these claims.

### The dilution analysis already addresses persistence

The coherence-equivalent pulse effect gamma decreases as responses get later. The completed analysis tests a simple retention benchmark: gamma should scale approximately as 1/T if the pulse supplies a fixed contribution diluted by continued evidence, where T is RT from motion onset. Consequently gamma times T should remain approximately constant.

| Time from pulse to response | gamma times T in percentage coherence seconds |
|---|---:|
| 0.3–0.6 s | 14.03 |
| 0.6–0.9 s | 16.62 |
| 0.9–1.2 s | 14.81 |
| 1.2–1.5 s | 4.27 |
| 1.5–2.1 s | 5.39 |
| 2.1–5.0 s | -2.77 |

The fitted plateau is 15.15 percentage coherence seconds, with mouse-bootstrap interval 12.71–17.54. The three later contrasts fall below it under the reported one-sided bootstrap exercise; Holm-adjusted tail probabilities are 0.020, 0.0267, and 0.010. These reproduce from the saved table. The benchmark interval and plateau window were developed within the existing exploratory analyses.

This is evidence that later pulse-response contrasts decline faster than this simple dilution account predicts. It does not uniquely show that the internal memory is retained for exactly 1.2 s and then erased. The benchmark omits selection due to decision bounds, response-time conditioning, variable sensory and motor delays, and changing engagement. A bounded perfect integrator must be simulated and passed through the same estimator before treating the late decline as identified forgetting. The approximate comparison of the plateau with nominal pulse area also does not establish a threefold neural gain.

Source: `../paper_accumulation/tables/pulse_dilution_2026-10-30.csv`, `../../scripts/behavior/pulse_dilution.py`, and `dilution_late_contrasts_with_holm.csv` in this directory.

### Pulse onset effects have been tested directly

Per-mouse paired contrasts, a hierarchical Bayesian model, RT-eligible sensitivities, and fitted onset-specific pulse weights are already available. They do not establish early greater than middle greater than late weighting across the cohort. The Bayesian early-minus-middle contrast is 0.144 log-odds with 95% HDI -0.081 to 0.371. Comparing all early/middle mice with the six late-pulse mice creates a misleading impression of a decline because the mouse populations differ.

Onset-specific weights improve summed held-out score by only about 2 NLL units with sv and 8.4 without it relative to the corresponding joint fits, with no corrected group support. PSUIM6 has a clear exploratory early-weight effect around three versus a middle weight around one; PSUIM7 shows a related hint in the no-sv formulation. Those are individual-mouse findings, not a cohort-wide primacy result. Earlier poor power calibration applies to the original frozen modeling procedure; it does not prove that every possible analysis of the dataset lacks information.

Sources: `../paper_accumulation/tables/pulse_time_comparison_{tests,bayes}_2026-10-28.csv`; `../figures/qc/pulse_time_weights_{summary,parameters}_2026-10-31.csv`; `../../.agents/reports/2026-10-30-pulse-time-weight-profile.md`, `2026-10-23-amendment-6-result.md`.

### The model work already covers many possible repairs

| Completed analysis | What it establishes for the story |
|---|---|
| Joint control and pulse fits | Adding pulses to fitting preserves the broad relative ranking. It does not reliably reproduce all individual pulse patterns. |
| Pulse-only fits | Removing control constraints does not resolve the full discrepancy; this is more specific than a failure to transfer control parameters. |
| Nonlinear input mappings | They improve some likelihoods and bring several average pulse predictions closer to the data. They do not uniformly explain individual-mouse effects. |
| Free shared pulse weight | Little held-out benefit in the tested linear-input families; a larger pulse amplitude is not a demonstrated sufficient repair. |
| Pulse weight specific to onset | Some individual-mouse improvement; no robust cohort ordering or general repair of large pulse effects. |
| Added pulse-response time constant | A two-mouse pilot improves fit at its grid edge but leaves the choice/RT tension and late reversal. It is not evidence against all sensory dynamics. |
| Fixed-parameter sv set to zero | The reported late reversal disappears. This isolates an important consequence of the fitted drift-variability term within those models. Other predictions deteriorate, so this counterfactual is not a replacement fitted model. |
| Refit without sv | Pulse choices and some mean temporal signatures can improve while joint choice/RT likelihood worsens; on pulse-only pairs the held-out cost is about 25–68 NLL. |
| Urgency-gating parameter region | Free optima mostly avoid the strongly leaky, strong-urgency corner; no-sv versions improve some pulse summaries but generally lose joint fit. Avoidance by free optimization is weaker than a full profile ruling out that corner. |
| Race and LCA illustrations | Coarse control-matched examples in three mice do not solve pulse amplitude; these are not comprehensive fitted architecture comparisons. |
| Input/replay corrections | The UCLA freeze correction changes pulse magnitude modestly and does not resolve the whole mismatch. Display fidelity and geometry still limit a unique sensory interpretation. |
| Independent likelihood rescoring | Model-dependent optimum-score optimism was diagnosed and corrected for information criteria. |
| Bits per trial | Fine-bin held-out evaluation is simulation-noise limited; it is not a new reliable ranking or an independent information-theoretic discovery. |

Sources: `../../.agents/reports/2026-10-29-joint-control-pulse-refits.md`; `2026-11-11-pulse-only-fits.md`; `2026-11-09-mapping-accumulator-exploratory.md`; `2026-10-30-pulse-weight-joint.md`; `2026-10-31-pulse-time-weights.md`; `2026-10-23-pulse-tau-pilot-20261023T191030Z_fa8de8b.md`; `2026-11-09-pulse-effect-bootstrap.md` including its sv-zero addendum; `2026-11-11-ugm-corner.md`; `2026-10-29-pulse-race-lca-illustration.md`; `2026-10-29-ucla-pulse-me-nofreeze.md`; `2026-11-12-{likelihood-check,rescored-ic}.md`; `2026-11-13-{pulse-weight-signatures,bits-per-trial}.md`. Exact output-table paths are recorded in the associated reports and local inventories.

### The latest rankings have an important qualification

The rescored summary contains 42 joint, 22 pulse-only, and three control-only family entries. Among joint fits, power-law input plus leak and urgency ranks first by summed held-out NLL and rescored AIC/BIC. Normalization plus leak is only 2.63 BIC units behind, within the measured simulation uncertainty of that fine ordering. The held-out ranking separates those two more strongly. Among pulse-only fits, linear leak ranks first by rescored BIC, while normalized no-sv urgency gating has the best held-out sum by a small margin. There is no unique dynamics verdict shared by all these comparisons.

The observed 0.3–1.2 s pulse-versus-control effect averages 5.48 pp. Its trial-bootstrap interval for this fixed cohort is 3.17–7.87; the mouse-plus-trial interval is wider, 0.88–9.92. Many fitted accumulator means lie within the former interval. Therefore a universal mean pulse-amplitude failure is unsupported. The clearer unresolved issue is the individual-mouse pattern and its timing: PSUIM6 and PSUIM7 have early-window effects around 15.5 and 13.5 pp, which the tested free linear pulse weights still underpredict.

Existing diagnostic chi-square summaries are useful discrepancy measures, but omit fitted-parameter uncertainty and a full calibration of the fit-and-check procedure. They do not justify declaring every tested accumulator definitively falsified. Similarly, per-mouse differences are confounded with apparatus and schedule and should not be assigned a biological cohort cause.

Sources: `../figures/qc/model_ic_summary_2026-11-12_rescored.csv`; `pulse_effect_bootstrap_2026-11-09_{data,heterogeneity,models}.csv`; `pulse_effect_bootstrap_2026-11-12_pw_data.csv`; `pulse_joint_signatures_2026-11-12_pw_windows.csv`.

## The story supported by the completed results

**Mice use motion evidence to make decisions. Their control choices and response times favor accumulation over matched rapid-forgetting and extrema alternatives, with completed paired recovery supporting that discrimination. Brief pulses then reveal directional influences over an extended pulse-to-response interval. Extensive model comparisons constrain how that influence can arise, but the current rankings and individual pulse predictions do not identify a unique accumulation dynamics.**

This retains all three parts of the proposed paper. The third part is currently strongest as quantitative constraints and a specific unresolved model tension. It should not be reduced to an uninformative null, nor presented as an exact measurement of a memory time constant.

The most targeted missing comparison at the time of this inventory was the exact correctness, directional/shared, and dilution estimators applied to existing finalist simulations. The follow-up linked above now completes it on matched schedules, with two simulation seeds, a low-coherence sensitivity, and mouse-bootstrap uncertainty. It demonstrates that the simple dilution interpretation does not uniquely survive bounded-decision selection, while exposing a quantitative tension between the best joint models and the pulse time course. No new broad fit grid or experiment was required.

A history/state model remains one possible explanation if that comparison exposes an unresolved contradiction. It is not a prerequisite for acknowledging the completed accumulation-versus-nonaccumulation result, and it should not replace the original paper question before the existing results are assembled coherently.
