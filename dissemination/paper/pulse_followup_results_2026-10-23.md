# Pulse follow-up: behavioural Results package (draft, exploratory)

Status: DRAFT, 2026-10-23. Run `20261023T191030Z_fa8de8b`, contract config v2, commit fa8de8b (dirty tree; new code untracked and hashed in each stage manifest).
Every analysis here is **exploratory**. It was added after the original primacy procedure failed its adequacy gates; that procedure stays closed under amendment 6 item 8, and nothing here reopens or replaces it.
Outputs: `/mnt/data/processed/pulse_followup/20261023T191030Z_fa8de8b/<stage>/` (written `<run>/…` below). Figures: `dissemination/paper/figures/pulse_followup/20261023T191030Z_fa8de8b/`.
Section E (observed versus predicted under the existing model) added from package E.

---

## Results

### Pulse assignment and trial set

Pulse assignment was randomized within each coherence and was not announced to the mouse, in both task implementations. The UW task drew one of nine pulse/sham categories independently on each trial. The UCLA task assigned 12.5% of each coherence block to each of four pulse categories and shuffled the block.¹ We analysed the 30,030 trials retained as DDM inputs, including 4,537 trials with no response by 5 s. Unresponded trials were kept and treated as unresponded at the deadline, never as responses.² Pulse condition was the *scheduled* one. Trials on which the mouse responded before the pulse began were kept, because this analysis estimates the effect of being assigned a pulse.

Comparisons used trials whose base coherence was at most 36%. Rightward (positive) and leftward (negative) pulses were compared within cells defined by mouse, session, coherence and onset category. Each cell was weighted by the smaller of its two arm counts, and every mouse contributed equally. In each UW session, one coherence level was scheduled with rightward pulses only. Those cells have no leftward arm and were excluded from the signed and control comparisons.³

### Pulses shifted responses toward the pulse direction

Across mice, a rightward rather than a leftward scheduled pulse increased the probability of responding toward the pulse direction. The symmetric directional contrast was **Δdirection = +5.84 percentage points** (95% t interval 1.80 to 9.89; 10 mice; d_z = 1.03; Holm-adjusted p = 0.019 within the declared family of three comparisons). Nine of 10 mice showed a positive contrast; the range was −3.5 to +15.7 pp (Fig. P1A).⁴ Most of the effect was redirection:

| Component (positive − negative) | Estimate (pp) | 95% t interval |
|---|---|---|
| Right responses, ΔR | +4.81 | 0.47 to 9.16 |
| Left responses, ΔL | −6.88 | −10.97 to −2.78 |
| No response by 5 s, Δunresponded | +2.07 | −0.36 to 4.49 |

The three components sum to zero in every mouse, as they must. There was no clear change in the probability of responding at all.

The estimate was stable across checks:
- Dropping one mouse at a time gave 4.75 to 6.88 pp, and every interval stayed above zero.
- Earlier and later sessions gave 6.66 pp [0.46, 12.86] and 7.97 pp [1.74, 14.21] (7 mice estimable).
- The first and second halves of each session gave 5.13 and 5.89 pp.
- At 0% nominal coherence the estimate was larger but imprecise: 10.93 pp [−0.19, 22.04].
- Among responders only, the contrast was 7.26 pp [2.49, 12.02], or 0.39 log-odds [0.14, 0.65]. This analysis conditions on a response that the pulse itself can affect, so it is secondary.⁵

Pulses on identical stimulus seeds could be compared in only 3 mice: 8.94 pp, with an interval spanning zero. This is a methods check, not independent replication.

### Relation to trials without a pulse

Control trials were aligned to sham onsets. UW recorded scheduled sham onsets. UCLA controls received a pseudo-onset drawn from the same session's pulse onsets with a fixed seed, using no outcome information.⁶

- Rightward pulses versus controls: Δdirection = +4.86 pp [2.43, 7.29], Holm p = 0.004.
- Controls versus leftward pulses: +1.40 pp [−2.13, 4.92], Holm p = 0.39.

The two comparisons cover different matched cells. Their difference (+3.46 pp [−0.78, 7.71]) was computed after seeing them and is not evidence of an asymmetry between pulse directions. Five alternative pseudo-onset seeds changed these estimates by at most 0.2 pp.

### Time course after pulse onset

Cumulative probabilities of right responses, left responses and no response, aligned to pulse or sham onset (Fig. P2), reproduced the directional effect:
- On trials still unresponded at onset: +5.85 pp [1.93, 9.77] at onset + 4.58 s.
- On all scheduled trials: +5.80 pp [1.82, 9.78].

The directional difference was near zero in the first 0.5 s after onset (+0.2 pp). It accumulated mainly between 0.5 and 2 s: +3.24 pp [−0.01, 6.50] between 0.5 and 1 s, and +2.09 pp [0.47, 3.72] between 1 and 2 s. Little was added later (pointwise 95% intervals across mice, uncorrected).⁷ Most responses also occur in this window. The curve therefore shows when pulse-related responses were *emitted*. It does not show when pulse evidence entered the decision, and late cumulative differences carry earlier effects forward.

Neither pulse direction had a clear common effect, relative to controls, on whether or when mice responded:
- Responded by onset + 4.58 s: −0.51 pp [−2.10, 1.09].
- Restricted mean time unresponded: −0.017 s [−0.082, 0.048].

Early pulses of either sign may have sped responding slightly (−0.070 s [−0.140, −0.0003]), but this is one of many uncorrected quantities. Averaged over both signs and compared with controls, pulses also reduced left responses by 2.3 pp [0.7, 3.9] (all scheduled trials, at onset + 4.58 s). This is the positive–negative asymmetry above seen from a different angle, is likewise uncorrected, and we do not interpret it.

### Stimulus validation

Paired replays of 184 trials were rendered twice from the same initial seed, once with the scheduled pulse and once with it physically omitted. Their motion energy was identical before the pulse. The filter did not spread any difference to before the physical onset.

When the pulse ends, the task assigns the background dots new random directions. This added trial-specific noise (unsigned difference ≈ 7.8% coherence). It produced no detectable bias toward the pulse direction: the pulse-aligned noise change over all pulses was −0.004 [−0.09, 0.08] (UCLA task) and 0.06 [−0.11, 0.23] (UW task).

One deterministic exception exists. A rounding asymmetry in the task code changes one coherent dot toward the pulse direction for the rest of the trial, in specific coherence × sign cells: +0.2% to +0.66% coherence, or about 0.1% averaged over all pulses. This is small next to the 50–67 ms change of up to 100% coherence. A long-lasting stimulus bias therefore cannot explain the behavioural effect.⁸

The motion-energy pulse template used in the DDM inputs matched the physical replay's mean, within 10% over the first 333 ms. If the UCLA display never skipped a dot step at the pulse edges, its pulse energy is understated by a factor of 1.28 to 1.40. The display-loop rate and dot lifetime used during acquisition are not recorded, so this remains a labelled alternative.

### Sensitivity of the behavioural design

We kept the real trial design, schedules and censoring and replaced only the outcomes with simulated ones (200 datasets per scenario).⁹
- The primary estimator was unbiased (|bias| ≤ 0.17 pp).
- The t interval covered the true value in 93 to 97.5% of datasets.
- Under no effect, the primary test rejected in 2.5% of datasets [0.8, 5.7].
- Power was 0.64 [0.57, 0.71] for a true 6 pp effect and 0.21 for 3 pp.
- The mouse bootstrap covered too rarely (85 to 93%), so it is reported only as a sensitivity.

With 10 mice, a real effect of the observed size would fail the corrected test about one time in three, and effects near 3 pp cannot be detected reliably. Non-significant secondary contrasts, such as controls versus leftward pulses, must not be read as absence of an effect.

### Observed versus predicted behaviour under the existing model

The existing model's misfit on pulse trials concerned the timing of the directional effect more than its size. We used the fitted control parameters and the per-mouse pulse gain of the revised baselines, and simulated each mouse's pulse trials on the same cells and weights as the behavioural curves.¹⁰ At every gain we examined, the model placed the directional effect within the first second and then partly reversed it. The mice showed a delayed, sustained effect:

| Window after onset | Observed (pp) | Model at choice-best gain (pp) |
|---|---|---|
| 0–0.5 s | +0.39 | +3.0 |
| 0.5–1 s | +3.21 | +4.7 |
| 1–2 s | +2.12 [0.48, 3.77] | +0.25 |
| 2–4.58 s | +0.12 [−1.26, 1.50] | −2.98 [−4.21, −1.75] |

The baseline with leak and urgency reversed in the same way (−3.25 pp late).

The fitted objective splits exactly into three terms: whether the mouse responded, which side, and the response-time bins (the terms sum to the original within 1e-11). In the two mice with the most response-time data, the gain that best fits choices (4–7) was well above the joint optimum (1.4–2.45). It improved the choice term by about 9–10 NLL on held-out folds and cost about 100 NLL in the response-time term. In 6–7 of the other mice the choice term was nearly flat, so a tradeoff is only suspected there; in one it was not supported. Choices needed 2–7 times more pulse input than the model receives. The stimulus audit allows at most a 1.4-fold error in that input.

Two earlier observations had other explanations. The model predicted no common response burst at the gains that fit, and the data showed none, so a shared latency effect is not indicated. The coherence-slope excess on pulse trials (0.156 logit) equals the control fit's own coherence misfit (0.158 logit), so most of the "with versus against coherence" asymmetry noted under amendment 6 is a known control misfit. The pulse-specific remainder is about 0.1 logit.

In short, the existing accumulator family does not reproduce a pulse effect that emerges 0.5–2 s after onset without a later reversal. This is a predictive limitation of the fitted models. It does not establish any particular mechanism, nor the absence of accumulation or of primacy.

---

## Methods (additions)

**Trial table and assignment audit.** A single read-only table was built by joining `valid_data.csv`, `censored_trials.csv`, `aggregate_data.csv` and the retained DDM inputs by unique trial identity. Raw UCLA burst signs were joined by mouse, session, trial and attempt number. Pulse direction was taken from the scheduled pulse field: for UCLA, sign(BurstCoh × coherence); for UW, the sign of the scheduled pulse coherence. A trial counted as pulsed only if the pulse changed the stimulus coherence. Same-sign 100% pulses on 100% stimuli are null events.

Assignment rules were verified by reading the task source code:
- UW: NeuRPi `protocols/random_dot_motion/rt_pulse/session_manager.py`, commit fcfb603.
- UCLA: RDK-Task `Burst_Experiment.py`, commit 6fb3878.

Balance was checked against variables fixed before the pulse: coherence sign, previous choice and outcome, and position in the session. The code read is each repository's latest version, which may postdate data collection.

**Estimands.** For each mouse, ΔR, ΔL and Δunresponded are standardized differences in the probability of each outcome by 5 s between scheduled positive and negative pulses, using the weighting described in Results. Δdirection = (ΔR − ΔL)/2, in percentage points. Group estimates are unweighted means over mice, with two-sided 95% Student-t intervals (df = 9). The Holm family contains the primary contrast and the two pulse-versus-control contrasts. Nothing was adjusted for realised response time or for post-pulse motion energy.

**Response-time curves.** Cumulative incidence of right and left responses and the probability of no response were computed on a grid from onset to onset + 4.58 s, which lies inside every trial's follow-up. A left response is a competing event for a right response, never a censoring event. The onset-eligible summary includes trials unresponded immediately before onset. Weighting followed the same rules within each comparison.

**Stimulus replay audit.** Same-seed replays with and without the pulse event used the project's existing renderer and motion-energy filter. Coupling of the random number streams holds only until the pulse branch consumes different draws.

**Simulation check.** The real design was kept and outcomes were drawn from each mouse × coherence's control-trial outcome distribution. A known directional effect was introduced with between-mouse spread matched to the observed spread. The estimators used were the analysis code itself.

---

## Figure captions (draft)

**Fig. P1 — Directional effect of scheduled pulses.** (A) Per-mouse Δdirection, ΔR, ΔL and Δunresponded (positive − negative scheduled pulse; base coherence ≤ 36%) with the group mean and 95% t interval across mice (n = 10). (B) Pulse versus timing-matched control. (C) Robustness: leave-one-mouse-out, session halves, 0% coherence, responders only. Files: `behaviour_primary_components.png`, `behaviour_pulse_vs_control.png`, `behaviour_robustness_forest.png`.

**Fig. P2 — Pulse-aligned joint response distributions.** Standardized cumulative probability of right responses, left responses and no response after pulse or sham onset, by onset category and arm. Bottom row: positive − negative contrasts with pointwise 95% t intervals across mice (uncorrected; descriptive). Files: `response_time_joint_curves_onset_eligible.png`, `response_time_contrasts_onset_eligible.png` (all-scheduled versions alongside).

**Fig. P3 — Stimulus replay audit.** Paired same-seed replays with and without the pulse: signed and unsigned motion-energy differences around onset and offset, and the reset of background-dot directions at pulse offset. File: `stimulus_paired_difference_traces.png`, `stimulus_direction_reset.png`.

**Fig. S — Coverage and power of the behavioural estimators** on the observed design. File: `validation_g1_power_coverage.png`.

---

## Limitations
- The sample is 10 mice, so power is limited (Sensitivity section). All analyses are exploratory and were defined after earlier pulse results were known.
- The causal interpretation holds for scheduled-pulse assignment. It relies on the task code read here matching the code used to collect the data.
- Exclusions that depend on the outcome are small but non-zero. Fifteen UCLA trials in which the mouse responded during the pulse are missing from the DDM inputs. Five unresponded UCLA trials at 0% coherence have an unknowable pulse direction.
- UCLA control timing relies on pseudo-onsets. UCLA onset times are the times at which the pulse was applied, not the scheduled values.
- Rig is confounded with cohort and is used only to define onset schedules. No rig comparison is made or implied.
- The time course after onset describes when responses were emitted, not when evidence was integrated. No primacy or integration-window claim follows from it.
- The existing DDM inputs label 43 unresponded UCLA pulse trials as controls (38 genuine pulses). These analyses use corrected labels. The historical results were not recomputed.

## Notes (traceability)
1. `.agents/reports/2026-10-23-pulse-data-20261023T191030Z_fa8de8b.md`; `<run>/data/analysis_config.json` (`assignment_verdict`); `<run>/data/assignment_audit.json`.
2. `<run>/data/exclusion_ledger.csv`.
3. `<run>/data/support_summary.csv`; config `weighting.uw_asymmetric_schedule`.
4. `<run>/behaviour/group.csv`, `per_mouse.csv`. Command: `python -B -m scripts.pulse_followup.behaviour --run-id 20261023T191030Z_fa8de8b`. Independently recomputed by the coordinator (plan log).
5. `<run>/behaviour/robustness_*.csv`, `secondary_responder_only.csv`.
6. `<run>/response_time/d1_control_alignment.json`; `<run>/behaviour/c4_pseudo_onset_seed_sensitivity.csv`.
7. `<run>/response_time/contrast_table.csv`. Command: `python -B -m scripts.pulse_followup.response_time run --run-id 20261023T191030Z_fa8de8b`. Independent review: `.agents/reports/2026-10-23-pulse-review-D-20261023T191030Z_fa8de8b.md`.
8. `<run>/stimulus/summary.json`, `per_trial_replay_metrics.csv`, `dotstate_all_pulse_trials.csv`; `.agents/reports/2026-10-23-pulse-stimulus-20261023T191030Z_fa8de8b.md`. Rounding shift independently reproduced by the coordinator.
9. `<run>/validation/g1/`; `.agents/reports/2026-10-23-pulse-validation-g1-20261023T191030Z_fa8de8b.md`.
10. `<run>/diagnostics/` (`e3_optima.csv`, `e3_tradeoff_verdict.csv`, `e4_model_vs_D_summary.csv`, `e4_departure_decomposition.csv`, `e4_control_psychometric.csv`); `.agents/reports/2026-10-23-pulse-diagnostics-20261023T191030Z_fa8de8b.md`. Commands: `python -B -m scripts.pulse_followup.diagnostics simulate|analyze --run-id 20261023T191030Z_fa8de8b`. Uses the existing DDM inputs, which contain the 43-trial label bug (unresponded trials only).
