# Plan: replicate the behavioural pulse analyses of Huk & Shadlen 2005 on the mouse data
Status: done
Created: 2026-10-29 by Claude (Opus 5.5)
Related reports: reports/2026-10-29-behavior-exploration.md; reports/2026-10-29-pulse-descriptive-package.md

## Goal
Author request: "Look at this paper which also does pulse. Understand and see if we can replicate this" (Huk AC,
Shadlen MN 2005, J Neurosci 25:10420, doi 10.1523/JNEUROSCI.4684-04.2005; read via PMC6725829). Done = their two
behavioural pulse analyses run on our responded trials, per mouse and pooled, with their numbers next to ours.

## Context (from the paper, Methods/Results; equations are images in PMC, so forms below follow the prose)
- RT task, 2 monkeys; 100 ms background-texture pulse at 100-392 ms; 1/3 positive, 1/3 negative, 1/3 no pulse.
- Analysis 1 (Eqs 6-7, Table 2): joint fit of P(choice) and mean RT (correct + error) per coherence x pulse with a
  proportional-rate diffusion; the pulse adds gamma (% coherence) to C for choices and gamma + delta for RT; binomial
  choices, normal mean RT with measured SE; result gamma 1.60% (0.08), delta -0.05% (0.13), LR p 0.70.
- Analysis 2 (Eq 8, Fig 4): 75 ms bins of RT - pulse onset; per bin logistic in C with positive- and negative-pulse
  indicators; effects beta2/beta1 and beta3/beta1 in % coherence; no-pulse trials get virtual onsets matched to the
  pulse onset distribution. Result: effect for responses ~300-900 ms after pulse onset, none earlier.
- Exclusions: responses before or during the pulse removed (pulse and virtual).
- Check: KS test of standardized RT distributions (pulse vs none, positive vs negative), all p > 0.6.

## Assumptions
- The diffusion form is Palmer, Huk & Shadlen 2005 (P = 1/(1+exp(-2kAC)), mean decision time A/(kC) tanh(kAC),
  C as a fraction, time in ms) since Eqs 6-7 are images; the text's parameter list (k, gamma, delta, t_nd, A) and
  Table 2 magnitudes (A 22.8, k 0.426) fit this form.
- Our pulse coding: trial_table pulse_sign (+1 right), categories control/positive/negative; null pulses and unknown
  excluded; symmetric cells only; onsets recorded (UCLA) / scheduled (UW); virtual onsets control_onset_s.

## Steps
- [x] 1. Script scripts/behavior/huk_shadlen_replication.py: trial selection and exclusions.
- [x] 2. Analysis 1 per mouse and pooled: Huk-exact (no bias) and with a bias term (mice have side biases); LR test
      for delta.
- [x] 3. Analysis 2: 75 ms relative-RT bins pooled (mouse intercepts), and coarse bins per mouse with mouse as unit
      (Wilcoxon, Holm).
- [x] 4. KS check on standardized RT distributions.
- [x] 5. Verify: model fits plotted against data; pooled bins reproduce the sign of the existing RT-split pulse effect.
- [x] 6. Report, STATUS.

## Out of scope
The LIP analyses; refitting our DDMs.

## Log
- 2026-10-29: written; cheap local analysis, started.
- 2026-10-29: done; optimizer changed to scaled Nelder-Mead/Powell (L-BFGS-B stuck); t_nd constrained >= 0. Report:
  reports/2026-10-29-huk-shadlen-replication.md.
- 2026-10-30: author follow-ups done in the same script: per mouse, congruency, overlay, all coherences with
  categorical coherence, no late pulses, sign toward correct side; plus scripts/behavior/congruency_roc.py (AUC,
  margin +-0.05 by default). Pending (offered, not run): spline time-course fits and window tests; pulse x |C|.
- 2026-10-30: added scripts/behavior/pulse_decomposition.py (pooled directional vs shared terms, mouse bootstrap) at
  the author's request; report addendum.
- 2026-10-30: added scripts/behavior/pulse_dilution.py (kept vs lost benchmark, 300 mouse bootstraps); report
  result section; STATUS updated.
