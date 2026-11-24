# Plan: informed fast guesses (Molano-Mazón action initiation) on norm UGM no sv
Status: active
Created: 2026-11-24 by Claude (Opus 5.5)
Related reports: reports/2026-11-24-lit-followups-results.md, reports/2026-11-24-lit-brunton-piet-molano.md

## Goal
Test whether fast guesses that report the decision variable (DV) explain the PSUIM6/7 fast-window pulse effect and fast control accuracy in a fitted model. Stages 1–2 are local. Stage 3 (Hyak) needs the author's go-ahead.

## Context
- Counterfactual (fixed parameters): a 0.1 s readout lag takes PSUIM7 early pulses 11.4 → 21.3 pp (data 25.1), and fast 100% control accuracy to 79.0% (data 78.9). It overshoots the evidence-blind mice. A lag equal to ndt barely helps.
- The likelihood is a quantile likelihood on simulated outcomes (src/ddm/ddm.py). Guesses are applied after simulation (apply_guesses) with common-random-number draws (n, 3).

## Model
- Guess trials as now: probability p_guess, RT = guess_t0 + Exp(guess_tau).
- With probability w a guess is informed: choice = side of the DV relative to the bound midpoint, at step (guess RT − read_lag)/dt. If the DV hit a bound earlier, that committed choice is used.
- Otherwise the guess is blind: choice 1 with probability guess_bias.
- Draw reuse keeps w = 0 identical to the current model: informed iff u1 < w; the blind choice uses (u1 − w)/(1 − w) < guess_bias. This is exact at w = 0 and independent of the informed draw.
- New parameters: w ∈ [0, 1], read_lag ∈ [0.05, 0.5] s.

## Assumptions
- The midpoint readout keeps the start-point bias (readout_mid).
- read_lag is independent of ndt. A read_lag ≥ ndt-like value returns the near-null case.

## Steps
- [x] 1. Implement in the numba and torch backends (optional per-trial read_step → read choice), apply_guesses (w), and the MouseDDM simulate paths. Add a fit-script option (guess model "informed") and the make_model mapping.
- [x] 2. Tests:
  - w = 0 reproduces the stored NLL of pulse_norm_ugm_no_sv fits exactly.
  - numba == torch (CPU) for the read choice.
  - The informed-guess choice equals the counterfactual script at matched draws.
  - Existing tests still pass.
- [x] 3. Fixed-parameter profile: PSUIM6, PSUIM7 and two other mice. Held-out pcv NLL on a grid w ∈ {0, .25, .5, 1} × read_lag ∈ {0.1, 0.2, 0.3}; other parameters fixed. Report total, choice/RT split and fast-window effects.
- [x] 4. Recovery check: simulate PSUIM7-like data (truths changed to (0.5, 0.12), (0.25, 0.2), (0, 0.1), 2 datasets each), then fit w and read_lag only (other parameters at their true values) from a few starts. Check whether w and read_lag are identifiable.
- [x] 5. Write criteria (A/A2; mechanism w > 0.05 in PSUIM6/7 in ≥ 3/5 folds; guardrail on control choice excess and fast control accuracy), draft the task table (not submitted), and report.
- [ ] 6. (Stage 3, author's go-ahead needed) Author submits scripts/slurm/tasks_2026-11-24_informed.csv on Hyak (60 fits, batch IG_norm_ugm, warm start from fits_pulse_norm_ugm). Then score with the committed machinery (5 seeds, held-out + control) and evaluate the criteria below.

## Criteria (written 2026-11-24, after the fixed-parameter profile and recovery, before any fit)
Tiers A (confirmatory) and A2 (exploratory) exactly as in plans/2026-11-19-choice-misfit-followup.md and as applied in
plans/2026-11-20-transient-channel.md (scripts/paper/score_pw_criteria.py machinery):
- Pair: pulse_norm_ugm_informed_no_sv (fits_pulse_norm_ugm_informed, L1U1V0Z0G1, guess model informed) vs
  pulse_norm_ugm_no_sv (fits_pulse_norm_ugm, L1U1V0Z0G1).
- ΔNLL: held-out pcv0-4 pulse-trial NLL, nbins 9, summed over folds, 5 seeds (12345, 23456, 34567, 45678, 56789), CPU.
- Rules 1-3 unchanged (rule 3: PSUIM6 and PSUIM7 improve and |resid_new| <= 0.5 |resid_old|; A2: 0.75).
- Rule 4 (mechanism): guess_w > 0.05 in the full "pulse" fit and in >= 3 of 5 pcv folds, in both PSUIM6 and PSUIM7
  (A2: fold median > 0.05). The recovery check put w_hat at 0.009 and 0.034 when the truth was 0, so 0.05 separates
  a real informed fraction from the lower-bound noise. read_lag is not interpreted (weakly identified, see recovery).
- Rule 5 (guardrail): control-trial choice excess of the full "pulse" fit scored on control trials, new vs constant;
  fail if worse by more than the constant's seed range (A2: flag at 2x).
- Rule 6 (descriptive, not pass/fail): fast (< 0.6 s) control accuracy by |coherence|, model vs data, per mouse.
  Reported so an overshoot at intermediate coherences (seen in the profile at w = 1) is visible.
- Decision: A passes -> informed guesses join the best pulse model. Only A2 passes -> report as suggestive, norm UGM
  no sv stays. Neither -> norm UGM no sv stays; the fast-window pulse effect in PSUIM6/7 is a stated limitation.
- If both this family and the transient family pass A, they are compared on held-out ΔNLL with the same seeds; a
  combined model is a separate plan.
- The profile and recovery decide only whether fitting is worth it; they are not evidence for the criteria.

## Out of scope
Hyak submission without the author's go-ahead; control-model (Figure 2/3) refits; combining with the transient channel.

## Log
- 2026-11-24: Author "yes" to stages 1–2 (local).
- 2026-11-24: Step 1 done: src/ddm/simulator.py (numba kernel read_step arg + read output; numba/torch backends; DriftDiffusionSimulator read_choice column), src/ddm/ddm.py (informed_read_steps, apply_guesses guess_w with draw reuse, both simulate paths; MouseDDM.simulate keeps the original random order when guess_w = 0), scripts/ddm/fit_mouse_ddm.py GUESS_MODELS["informed"]. Counterfactual script updated for the 3-output kernel.
- 2026-11-24: Step 2 done: tests/test_informed_guesses.py passes (readout agreement 1.0000 both backends, 3 settings; exact counterfactual equality; w = 0 exact in apply_guesses and MouseDDM.simulate). Existing tests pass (normalized_urgency, evidence_gain, response_delay, fit_checkpoint, pulse_feature_encoding). Profile at w = 0 reproduces stored PSUIM7 test NLL exactly (max diff 0.0).
- 2026-11-24: Single-seed PSUIM7 preview: w 0.25-0.5, lag 0.1 improves held-out NLL by about 10-12 (mostly RT); w = 1, lag 0.1 matches the fast early-pulse effect (27.3 vs 26.7 pp) but costs +62 (choice). Full profile (4 mice x 2 seeds) and recovery (3 truths x 2 datasets, PSUIM7) running.
- 2026-11-24: Step 3 done (profile, 4 mice x 2 seeds): ΔNLL summed over folds, mean of 2 seeds. PSUIM7 w .5/lag .1 −8.3 ± 2.7, w .25/lag .1 −5.8 ± 8.0, w 1/lag .1 +66 (choice). PSUIM6 w .5/lag .1 −9.3 ± 8.6. DBM5 about 0. DBM12 worse (+2.5 to +45). Guardrail (fast 100% control accuracy, data/w0/w.5): PSUIM7 .77/.53/.67, PSUIM6 .74/.51/.60. Output: draft_2026-11-15/informed_guess_profile_2026-11-24/.
- 2026-11-24: Step 4 done (recovery, PSUIM7, 6 synthetic datasets): w_hat 0.45/0.42 (truth 0.5), 0.29/0.35 (0.25), 0.009/0.034 (0). read_lag not identified (0.07-0.33 across truths 0.10-0.20). nll_hat <= nll_truth everywhere (optimizer fine). Truths deviate from the plan's (0.7, 0.12): chosen to bracket the profile optimum and include the null.
- 2026-11-24: Step 5: criteria written above; draft table scripts/slurm/tasks_2026-11-24_informed.csv generated (60 tasks, 303.5 h requested, est 157.5 h), not committed, not submitted. Report: reports/2026-11-24-informed-guess-profile.md. Next: author decision on stage 3 (step 6).
