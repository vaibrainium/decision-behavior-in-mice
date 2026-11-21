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
- [ ] 1. Implement fe_h / fe_tau_h in front_end_numpy and front_end_torch (src/ddm/simulator.py). Add a fit-script option (scripts/ddm/fit_mouse_ddm.py `--front_end norm_transient`) and the make_model mapping. Unit checks: fe_h = 0 reproduces norm exactly; numpy == torch; a step input gives the expected overshoot.
- [ ] 2. Pre-fit profile (CPU, minutes): PSUIM6, PSUIM7 and two other mice. Held-out pcv NLL of the norm UGM no sv fits with fe_h on a grid (0, 1, 3, 10) × fe_tau_h (0.05, 0.15), other parameters fixed. If no improvement anywhere, report that and ask whether fitting is still worth it.
- [ ] 3. Write the criteria before fitting: tiers A and A2 unchanged. Pair: transient vs pulse_norm_ugm_no_sv. Rule 4: fe_h > 0 in the full fit and ≥ 3/5 folds (A2: fold median). Rule 5: control-trial choice excess of the full fit. Commit.
- [ ] 4. New task table (new file + state; committed tables are never changed): 10 mice × (pcv0–4, pulse) = 60 fits; time limits from the norm UGM no sv fit times (16 h only where those took > 4 h). Author submits on Hyak.
- [ ] 5. Score with the committed machinery (5 seeds, held-out + control), then evaluate criteria A/A2.
- [ ] 6. Pick the winner by the decision table. Update the Figure 6 model-vs-data panels for the winner (psychometric, RT quantiles, pulse effect by time × coherence).
- [ ] 7. Verify: fe_h = 0 reproduction check passes in scoring; report written.

## Out of scope
Widening the fe_beta bound alone; joint (control + pulse) refits; other transient forms.

## Log
- 2026-11-20: Plan written. PSUIM7 fe_beta at bound noted; widening it is a cheaper partial test and can be added as a second family if the author wants.
