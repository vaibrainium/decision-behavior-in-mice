# Plan: Transient (change-sensitive) input channel on top of norm UGM no sv
Status: active
Created: 2026-11-20 by Claude (Opus 5.5)
Related reports: reports/2026-11-20-pw-fits-criteria-a.md, reports/2026-11-20-pulse-weight-joint-criteria.md, reports/2026-11-19-top4-multiseed-pulse-effect.md

## Goal
Find the model that best explains the pulse effect with RT, as close to the data as possible (author, 2026-11-20). Current best is norm UGM without sv (pulse_norm_ugm_no_sv). Test one more model aimed at the remaining pulse gap: the same model plus a transient channel. If it passes the criteria it becomes the best model; otherwise norm UGM no sv stays, and the remaining pulse gap is a stated limitation.

## Context
- norm UGM no sv: best held-out total at 5/5 seeds, lead mostly PSUIM6/7 (top4 multiseed report). Worst family on control trials scored out of sample (choice excess 277; too steep at low coherence, too flat at 100%; step-2 report). Model-vs-data plots exist: dissemination/paper_accumulation/draft_2026-11-15/figure6_pulse_fits_2026-11-18/.
- Its front end already favours change: x' = x / (1 + fe_beta · LP_fe_tau(|x|)), plus leak ≈ 2/s (UGM corner). Fitted fe_beta for PSUIM7 is 19.93, at the bound of 20 (fe_tau 0.75 s). PSUIM6 has 4.4 (0.80 s). Source: fits_pulse_norm_ugm/*_L1U1V0Z0G1_pulse.pkl.
- Primacy (gain decay, signed leak) and a scalar pulse weight failed criteria A/A2.

## Model
Signed high-pass term added after the existing front end: x'' = x' + fe_h · (x' − LP_fe_tau_h(x')), with LP the same causal exponential low-pass as the norm front end. Two new free parameters: fe_h in [0, 20] and fe_tau_h in [0.02, 0.5] s. fe_h = 0 gives back norm UGM no sv exactly. The term also responds at stimulus onset on every trial, so control trials constrain it in the guardrail.

## Assumptions
- A high-pass of the existing input is a fair "transient" channel. Alternatives (|dME/dt|, a pulse-onset kernel) are not tested.
- Pulse-only fits (pcv0–4 + pulse) are the comparison set, as for the other pulse-only families.

## Steps
- [x] 1. Implement fe_h / fe_tau_h in front_end_numpy and front_end_torch (src/ddm/simulator.py). Add a fit-script option (scripts/ddm/fit_mouse_ddm.py `--front_end norm_transient`) and the make_model mapping. Unit checks: fe_h = 0 reproduces norm exactly; numpy == torch; a step input gives the expected overshoot.
- [x] 2. Pre-fit profile (CPU, minutes): PSUIM6, PSUIM7 and two other mice. Held-out pcv NLL of the norm UGM no sv fits with fe_h on a grid (0, 1, 3, 10) × fe_tau_h (0.05, 0.15), other parameters fixed. If no improvement anywhere, report that and ask whether fitting is still worth it.
- [ ] 3. Write the criteria before fitting: tiers A and A2 unchanged. Pair: transient vs pulse_norm_ugm_no_sv. Rule 4: fe_h > 0 in the full fit and ≥ 3/5 folds (A2: fold median). Rule 5: control-trial choice excess of the full fit. Commit.
- [ ] 4. New task table (new file + state; committed tables are never changed): 10 mice × (pcv0–4, pulse) = 60 fits; time limits from the norm UGM no sv fit times (16 h only where those took > 4 h). Author submits on Hyak.
- [ ] 5. Score with the committed machinery (5 seeds, held-out + control), then evaluate criteria A/A2.
- [ ] 6. Pick the winner by the decision table. Update the Figure 6 model-vs-data panels for the winner (psychometric, RT quantiles, pulse effect by time × coherence).
- [ ] 7. Verify: fe_h = 0 reproduction check passes in scoring; report written.

## Criteria (written 2026-11-21, before the profile results and before any fit)
Tiers A (confirmatory) and A2 (exploratory) exactly as in plans/2026-11-19-choice-misfit-followup.md, applied to the
pulse-only fits as for the PW families (scripts/paper/score_pw_criteria.py machinery):
- Pair: pulse_norm_transient_no_sv (fits_pulse_norm_transient_ugm, L1U1V0Z0G1) vs pulse_norm_ugm_no_sv (fits_pulse_norm_ugm, L1U1V0Z0G1).
- ΔNLL: held-out pcv0-4 pulse-trial NLL, nbins 9, summed over folds, 5 seeds (12345, 23456, 34567, 45678, 56789), CPU.
- Rules 1-3 unchanged (rule 3: PSUIM6 and PSUIM7 improve and |resid_new| <= 0.5 |resid_old|; A2: 0.75).
- Rule 4 (mechanism): fe_h > 0.05 in the full "pulse" fit and in >= 3 of 5 pcv folds (A2: fold median > 0.05). The
  threshold 0.05 stops a value pinned at the lower bound 0 from counting (cf. the w = 1.000 tolerance artefact).
- Rule 5 (guardrail): control-trial choice excess of the full "pulse" fit scored on control trials, new vs constant;
  fail if worse by more than the constant's seed range (A2: flag at 2x).
- Decision: A passes -> transient model replaces norm UGM no sv as the best pulse model. Only A2 passes -> report as
  suggestive, norm UGM no sv stays the best model. Neither -> norm UGM no sv is the best model; the early low-coherence
  pulse residual is reported as a limitation.
- The pre-fit profile (step 2) only decides whether fitting is worth it; it is not evidence for the criteria.

## Out of scope
Widening the fe_beta bound alone; joint (control + pulse) refits; other transient forms.

## Log
- 2026-11-21: Author approved the plan ("ok"); the fe_beta-widening family not added. Step 1 done: fe_h/fe_tau_h in front_end_numpy/torch, `--front_end norm_transient`, and fe_h switched off in evidence_gain's second pass. Checks: fe_h = 0 identical to norm (array_equal); numpy == torch (max diff 0.0 at float32); unit step gives 1 + h(1-k) at onset, decaying with tau_h (matches closed form). Fits will warm-start from fits_pulse_norm_ugm, so each starts at the base model.
- 2026-11-20: Plan written. PSUIM7 fe_beta at bound noted; widening it is a cheaper partial test and can be added as a second family if the author wants.
- 2026-11-21: Step 2 done (`scripts/paper/transient_profile.py`, output dissemination/paper_accumulation/draft_2026-11-15/transient_profile_2026-11-21/profile.csv; seeds 12345, 23456; commit e4bdc8d). fe_h = 0 reproduces stored test NLL exactly (max diff 0.0). With all other parameters fixed, no grid point improves held-out NLL beyond noise (best: PSUIM6 h=1, tau_h=0.05, -1.7 +/- 2.8). NLL worsens steeply with h, most in PSUIM6/7 (h=3, tau_h=0.15: +212 and +480). The early low-coherence residual does shrink with h (PSUIM7 9.8 -> 4.7 pp at h=3/0.15; sign flips at h=10). Reading: the term moves the pulse effect the right way, but with drift gain, bound etc. fixed it distorts everything else; a fixed-parameter profile cannot show whether a refit compensates. Stopped before step 4, as the plan says; asked the author.
