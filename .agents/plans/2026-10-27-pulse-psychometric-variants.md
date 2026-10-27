# Plan: psychometric functions for congruent, incongruent and control trials, data vs every responded-only variant
Status: done (report: reports/2026-10-27-pulse-psychometric-variants.md)
Created: 2026-10-27 by Claude Opus 5.5
Related reports: reports/2026-10-27-pulse-contrast-responders-only.md; refit plan plans/2026-10-26-v2-refits-and-strategy-recovery.md

## Goal
One figure: P(right | response) vs signed coherence for control, congruent (pulse toward the coherence) and
incongruent pulses, observed vs each responded-only model variant (control-trial fits), plus the pulse effect per coherence.

## Context
Saved frozen pulse predictions (responded-only, 200 reps, seed 0): primacy_resp/{primary, secondary, extrema_samples},
primacy_revised_resp/{primary, secondary} (cross-validated pulse gain). Missing: control-trial predictions for all,
and pulse predictions for E (leak 20-200, cap) and free leak 0-200 (cap).

## Design
- Trials: responded only (inputs + responded_only). Pulse direction = sign(sched_pulse_type); congruent = sign equals
  sign(coherence), incongruent = opposite; 0% pulses not on either curve. All scheduled pulse trials (UW asymmetric
  sessions included; data and model use identical trials).
- Model P(right | response) per trial from p_hat (pulse direction) or simulated control trials with primacy.predict_mouse
  (same function, 200 reps, seed 0). Pulse-gain variants: saved pulse predictions; their control trials = base variant.
- Mouse is the unit: per mouse cell means, then mean +- SEM over mice.
- Variants: primary L0U0V1Z0G1, secondary L1U1V1Z0G1, primary + pulse gain, secondary + pulse gain, E L1U0V1Z0G1
  leak 20-200 (cap), ES (cap), free leak 0-200 (cap). Not plotted: R2 cross-validation-only variants (no control fit),
  nosv set (withdrawn, D005), all-trial fits (author rule).

## Steps
- [x] 1. scripts/ddm/pulse_psychometric.py: simulate missing predictions -> processed/ddm/pulse_psychometric_resp/ (cache).
- [x] 2. Figure -> dissemination/figures/qc/pulse_psychometric_variants_<date>.{png,pdf} + source table csv.
- [x] 3. Verify: saved primary pulse p_hat vs fresh simulation of the same trials agree (same seed); data cell counts.
- [x] 4. Report + STATUS.

## Out of scope
New fits; statistics beyond descriptive SEM.

## Log
- 2026-10-27: done. Check: fresh CPU simulation vs saved (Hyak) primary predictions, PSUIM10 166 pulse trials: corr 0.975, mean diff 0.004, mean predicted effect 0.55 vs 0.58 pp (Monte Carlo/backend noise).
