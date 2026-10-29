# Report: can the pulse trials tell a leaky integrator from urgency?
Date: 2026-10-29   Agent: Claude (Fable 5.1)   Commit: 363aa3d (working tree; the files named below are not yet committed)
Plan: plans/2026-10-28-pulse-leak-vs-urgency-research.md
Companion: dissemination/reports/pulse-leak-vs-urgency-literature-2026-10-29.md (literature synthesis, 62 DOIs;
notes in .agents/research_notes/Pulse tests of leak vs urgency/)

## Question
Author: "what can we do to use pulse trials to tell if the DDM is leaky or urgency? Look at what we have tried so far
and how to get there." Leak = OU decay of the accumulated evidence toward the starting point (rate L, /s); urgency =
gain (1 + u t) on the accumulated evidence, equivalent to a bound collapsing as a / (1 + u t) (src/ddm/simulator.py).

## Summary
1. Nothing already in hand decides it. The three descriptive pulse results (no within-mouse change across onsets;
   effect present for responses within ~1.2 s of the pulse and absent later; toward-pulse choices faster) are what a
   fixed-bound integrator with bound depletion, non-decision time and drift variability produces; leak and urgency
   change them only per undecided trial, in the second-order structure. The literature report gives the sources.
2. The pulses do carry information at the project's trial counts: in the two dense mice a leak of 1 /s or more moves the
   pulse-to-response profile (S1) away from the leak-free model by 2 to 10 bootstrap SE in the 0.6 to 1.2 s bins, and
   urgency of 3 /s by 2 to 3.5 SE. Urgency of 0.3 /s (the control-fitted range) moves it by under 1.6 SE and is not
   resolvable; urgency of 1 /s is marginal (0.5 to 2.5 SE). Stop rule SR1 (feasibility) is therefore not triggered.
3. But no member of the family, with or without leak or urgency, reproduces the observed profile: the data hold a flat
   13 to 19 pp effect across 0.3 to 1.2 s and ~0 afterwards, whereas every variant peaks in the first bin, is near 0 by
   0.9 to 1.2 s (3.5 to 9 SE below the data in PSUIM7) and reverses to -8 to -24 pp after 1.2 s. Leak makes the
   mismatch worse; mild urgency does not repair it. Within the family the data sit on the "no leak" side of the
   leak-free model, so leak >= 1 /s is disfavoured, but only conditionally on a family that fails SR4 (falsification).
4. Route: the leak-versus-urgency answer has to come from a joint fit of (L, u, pulse gain w) with the non-decision
   time pinned, judged first by ex-post reproduction of S1 to S3 and only second by held-out likelihood, after a recovery
   grid on the real schedules. The illustration predicts the fit will fail SR4 before it reaches L versus u, so the
   first modelling target is the sustained-then-absent pulse response, not leak or urgency. Details in "Route" below.
All simulation numbers here are an exploratory illustration (parameters re-matched on a coarse grid, three mice), not a
fit and not a power analysis.

## Findings

### 1. What the repo had already tried (VERIFIED from the cited files)
- Control trials neither need nor identify leak or urgency. Responded-only component table, mice as unit, per 1,000
  trials: add leak median -0.0 (Holm 1.0), add urgency -0.0 (Holm 1.0)
  (dissemination/paper_accumulation/tables/components_group_2026-10-28.csv). Fitted values in the secondary model
  L1U1V1Z0G1: leak 0.07 to 2.7 /s, urgency -0.08 to +0.14 /s (reports/2026-10-22-leak-urgency-diagnosis.md; the
  all-trial gains were the > 5 s response rate, now excluded under D003). Old all-trial recovery: leak 35 % hits,
  urgency 45 % hits, 15 % false alarms (reports/2026-10-22-arriving-results.md).
- Frozen control-fit predictions underpredict the pulse effect about tenfold (0.028 logit primary, 0.024 leak +
  urgency, versus about 0.3 logit observed; dissemination/reports/mouse-ddm-analysis-log.md section 5.9;
  reports/2026-10-27-pulse-contrast-responders-only.md: 7.52 pp [2.73, 12.30], Holm 0.012, 10 mice).
- With a free pulse gain the choice-best gain (4 to 7 in PSUIM6/7) is 2 to 3 times the joint choice + RT optimum; the
  model places the effect early and reverses it late (2 to 4.58 s window -1.4 to -3 pp; data +0.1 pp); the leak +
  urgency baseline has the same shape; the tau_p (300 ms filter) pilot failed P2/P3 and modelling stopped
  (reports/2026-10-23-pulse-diagnostics-20261023T191030Z_fa8de8b.md; reports/2026-10-23-pulse-tau-pilot-20261023T191030Z_fa8de8b.md).
- RT split: data effect by control-RT quintile 4.9, 4.3, 6.2, -0.2, -0.4 pp versus model 1.7, 3.2, 1.8, -0.4, -1.6;
  toward-pulse choices faster in data and model (reports/2026-10-27-pulse-readout-model-rt-split.md).
- No within-mouse change across onsets: early - middle 0.14 log-odds [-0.08, 0.37] (10 mice), middle - late 0.04
  [-0.31, 0.37] (6 mice) (reports/2026-10-28-pulse-time-comparison.md).
- The direction effect accrues 0.5 to 2 s after onset with no common latency effect (-0.5 pp [-2.1, 1.1]);
  readout-bias (slow-trial) account rejected (reports/2026-10-23-pulse-response_time-...md; reports/2026-10-27-pulse-readout-bias-checks.md).

### 2. What the literature says (VERIFIED against the four research notes; locators in the literature report)
- Every bounded-integrator class predicts the same first-order pulse signatures (a decline of the window effect with
  onset by thresholding, persistence for responses within about a second, toward-pulse choices faster). Zhou et al.
  2009 reproduce the primate data with a fixed bound once bound depletion and NDT are included; Okazawa et al. 2018
  show a 300 ms "integration window" in fixed-duration tasks arises from bounded integration without leak.
- Leak raises the per-undecided-trial effect of later pulses (Wong et al. 2007); urgency on accumulated evidence equals a
  collapsing bound and leaves the onset profile flat before thresholding (Murphy et al. 2016; Smith and Ratcliff 2022).
  Both are second-order and interact with depletion, so raw shapes cannot be read off; simulations fix the reading.
- Identifiability: leak is recoverable only when L is above about 1 /s, the evidence changes early relative to the
  decision, and NDT is pinned elsewhere (Trueblood et al. 2021; Stine et al. 2020; Murrow and Holmes 2024). Collapse
  trades off with bound and with sv (Evans et al. 2017; Hawkins et al. 2015). This design has three onsets inside the
  first 420 ms and a 100 % coherence condition, so the ingredients exist; the pulse-antipulse ratio (Zhou et al. 2009)
  and the policy manipulation (Carland et al. 2016) are not available.
- No study in any species has jointly fitted leak and urgency to pulsed RT data; no mouse RT pulse study exists.
  The literature's answer to "leaky or urgency?" is a region of the (L, u) plane, with L bounded above about 1 /s.

### 3. Feasibility illustration (VERIFIED as simulation output; interpretation EXPLORATORY)
Script scripts/ddm/pulse_leak_urgency_signatures.py (new); outputs
dissemination/figures/qc/pulse_leak_urgency_signatures_2026-10-29.{png,pdf} and _profile/_stage/_rtshift/_match/_grid.csv.
Setup: responded trials, symmetric cells, |coherence| <= 36 %, onset = scheduled (UW) or recorded (UCLA); S1 = P(choice
= pulse direction | pulse) - P(same choice | control) in bins of time from pulse onset to response (0.3-0.6, 0.6-0.9,
0.9-1.2, 1.2-1.6, 1.6-2.2, 2.2-3.0, 3.0-5.0 s), controls given the stage's median onset; bootstrap SE over 300 trial
resamples. Models: the primary control-split fit (fits_resp_final, L0U0V1Z0G1_control) simulated in the L1U1 simulator
with imposed leak (1, 3, 10 /s) or urgency (0.3, 1, 3 /s); bound and drift gain re-matched to the control trials on a
grid (a x 0.3-2.2, gain x 0.7-5, refined x 0.85-1.18, 6 repetitions, a <= 10, non-response <= 0.3), other parameters
held; pulse gain w = 1 (about the fitted value) and w = 4 (about the choice-matched value, Package E); 60 repetitions
of each mouse's real schedule. Simulated bins with fewer than 100 pulse trials are not drawn.

Window effects, data (stage CSV): PSUIM7 early 12.4 pp (n 1,182), middle 6.0 (1,207); PSUIM6 8.9 (979), 5.7 (958);
DBM6 1.2 (333), 3.5 (346), 2.8 (387). Responded pulse trials per S1 bin (profile CSV): PSUIM7 early 336, 309, 170,
100, 55, 61, 88; PSUIM6 early 112, 164, 107, 113, 124, 111, 226; DBM6 29 to 62 per bin. Base model at w = 4: PSUIM7 2.9 / 3.3; PSUIM6 4.6 / 4.0; DBM6 4.5 / 4.1 / 4.6;
at w = 1: 0.5 to 1.7 pp. Leak 10 /s at w = 4: 11.6 / 10.7; 19.7 / 17.1; 39.1 / 36.9 / 34.3. The window effect by onset is
flat for every variant (leak and urgency included), so the "no change across onsets" result bounds neither L nor u.

S1, PSUIM7, early pulse, w = 4 (pp; profile CSV; data +- bootstrap SE):
| bin (s) | data | base | leak 1/s | leak 3/s | leak 10/s | urg 0.3/s | urg 1/s | urg 3/s |
|---|---|---|---|---|---|---|---|---|
| 0.3-0.6 | 15.4 +- 2.5 | 16.2 | 22.4 | 20.4 | 29.9 | 19.0 | 18.8 | 13.8 |
| 0.6-0.9 | 16.5 +- 2.4 | 10.5 | 6.7 | -3.6 | -13.6 | 14.4 | 16.4 | 3.3 |
| 0.9-1.2 | 13.9 +- 3.5 | 1.4 | -5.2 | -12.4 | -18.2 | 1.7 | 0.4 | -7.3 |
| 1.2-1.6 | -4.6 +- 4.8 | -7.8 | -12.5 | -16.5 | -20.3 | -8.6 | -11.4 | -11.5 |
| 1.6-2.2 | 6.8 +- 5.8 | -12.1 | -18.4 | -18.7 | -22.9 | -15.1 | -16.3 | -11.8 |
| 2.2-3.0 | -4.0 +- 7.4 | -14.3 | -19.2 | -17.5 | -23.9 | -17.5 | -20.6 | -10.2 |
| 3.0-5.0 | 1.3 +- 5.0 | -16.1 | -18.9 | -14.6 | -21.6 | -19.5 | -17.5 | (n < 100) |
At w = 1 the base model gives 4.1, 2.1, 0.5, -2.0, -2.2, -4.2, -3.3: a quarter of the observed early effect.

S1, PSUIM6, early pulse, w = 4: data 19.0 +- 4.1, 19.1 +- 3.2, 10.7 +- 4.4, 0.8 +- 4.2, 5.3 +- 3.9, -1.3 +- 4.5,
1.3 +- 3.0; base 12.8, 11.6, 9.1, 5.7, 0.7, -2.0, -3.7; leak 3/s 16.2, 0.6, -3.3, -5.0, -4.8, -5.6, -5.5; urgency 1/s
10.9, 11.9, 8.9, 4.1, -0.9, -2.9, -3.9. DBM6 (SE 6 to 10 pp per bin) does not resolve the variants.

SR1 check (bins in 0.3 to 1.2 s where |variant - base| >= 1 data SE, out of 3; max |variant - base| / SE over all bins;
w = 4; from the profile CSV):
| variant | PSUIM7 early / middle | PSUIM6 early / middle | DBM6 early / middle / late |
|---|---|---|---|
| leak 1/s | 3 / 2 (2.5, 2.6) | 2 / 2 (1.8, 1.9) | 3 / 2 / 2 (1.6, 1.9, 1.6) |
| leak 3/s | 3 / 3 (6.0, 3.5) | 2 / 3 (3.5, 2.7) | 3 / 3 / 3 (3.3, 3.0, 2.6) |
| leak 10/s | 3 / 3 (10.2, 7.2) | 3 / 2 (5.4, 4.2) | 3 / 2 / 2 (2.6, 3.0, 2.8) |
| urgency 0.3/s | 2 / 1 (1.6, 1.2) | 1 / 1 (1.3, 1.2) | 0 / 0 / 0 (0.8, 1.0, 0.8) |
| urgency 1/s | 2 / 1 (2.5, 1.5) | 0 / 0 (0.5, 0.8) | 0 / 0 / 1 (0.9, 1.3, 1.1) |
| urgency 3/s | 2 / 2 (3.1, 3.5) | 1 / 2 (2.1, 2.3) | 2 / 2 / 3 (1.7, 2.3, 2.3) |
Reading: leak >= 1 /s is separable from the leak-free model by S1 in the dense mice; urgency is separable only at 3 /s,
and 0.3 /s (the control-fitted range) is not. SR1 is not triggered, so the pulses are informative in principle.

Model minus data in SE units, w = 4 (0.6-0.9 bin / 0.9-1.2 bin / worst bin after 1.2 s):
- PSUIM7 early: base -2.5 / -3.6 / -3.5; leak 1/s -4.1 / -5.4 / -4.4; leak 3/s -8.5 / -7.5 / -4.4; leak 10/s -12.7 /
  -9.2 / -5.2; urgency 0.3/s -0.9 / -3.5 / -4.2; urgency 1/s -0.1 / -3.9 / -4.0; urgency 3/s -5.6 / -6.1 / -3.2.
- PSUIM7 middle: base -3.5 / -3.5 / -3.0; leak 1/s -4.1 / -5.0 / -4.6; urgency 1/s -3.0 / -4.1 / -3.6 (others similar
  or worse; the first bin is over-predicted by 3.7 to 11.9 SE by every variant: data 7.4 pp, models 16 to 36 pp).
- PSUIM6 early: base -2.3 / -0.4 / -1.7; leak 1/s -3.1 / -1.6 / -2.8; leak 3/s -5.8 / -3.2 / -2.6; urgency 0.3/s -1.1
  / +0.5 / -2.5; urgency 1/s -2.3 / -0.4 / -1.8. PSUIM6 middle: base -1.0 / -0.5 / -1.5; leak 3/s -3.6 / -3.0 / -3.0.
Reading: in PSUIM7 every variant fails the 0.9-1.2 s bin by >= 3.5 SE and at least two late bins by 2 to 5 SE
(urgency 3/s, rejected by the control trials, fails one late bin); in PSUIM6 the base and urgency <= 1 /s variants
stay within 2.5 SE everywhere except the 0.6-0.9 bin, while leak >= 1 /s fails two or more late bins. The data are
less front-loaded and show less late reversal than any variant; leak moves the model away from the data.

Control-matching cost (match CSV; responded-only control NLL after re-matching a and drift gain, minus base; 6
repetitions, so upper bounds on a full refit): PSUIM6 leak 1/3/10 /s +124 / +619 / +1,747, urgency 0.3/1/3 /s +63 /
+385 / +3,231; PSUIM7 +39 / +296 / +553 and +2 / +131 / +1,420; DBM6 +20 / +80 / +304 and +11 / +43 / +466. Urgency
>= 1 /s drives the bound to the simulator's limit (a = 9.0 to 9.4 of 10) and lowers 36 % accuracy (PSUIM6 0.70 versus
0.77 base); leak shortens the median 0 % RT (PSUIM6 1.83 s base, 1.42 s at 1 /s, 0.83 s at 10 /s). DBM6 leak 10 /s
did not meet the non-response cap (0.41; flagged cap_ok False) and is unreliable. Strong leak or urgency is not a
free addition to the control fit; the mild variants (leak 1 /s, urgency 0.3 /s) nearly are, consistent with the
component table.

RT shifts (rtshift CSV, pulse minus control quantiles): data PSUIM7 toward-pulse choices -13, -99, -231, -619 ms at
quantiles 0.3 to 0.9, against-pulse -32, -56, +103, +244; base model at w = 4 -54, -167, -326, -581 and +82, +198,
+308, +384. Every variant has the same sign pattern; leak >= 3 /s overshoots the slow toward-pulse quantile (-1,057
to -1,572 ms). S3's quantile part constrains the gain w, not L versus u, in this regime.

### 4. What this means for "leaky or urgency?" (SUSPECTED; inference from 1 to 3)
- Taken inside the family, the S1 profiles say: no evidence for leak of 1 /s or more (it would fade the effect by
  0.6-0.9 s; the data hold it to 1.2 s), and urgency below about 1 /s is invisible. That is the same verdict as the
  control trials, now from the pulses.
- But the verdict is conditional on a family that fails the data where the discrimination lives (0.9-1.2 s and the
  late window, PSUIM7). The reversal after 1.2 s is bound depletion: pulse-favoured trials finish early, so the late
  pool is enriched for the other choice. The data lack it. Candidates that would remove or dilute it have not been
  tested: a late pulse-insensitive process (the coherence-flat late responses of reports/2026-10-22-leak-urgency-
  diagnosis.md), a pulse acting partly outside the accumulator, or a sensory stage that spreads the pulse later than
  the ME template. The tau_p pilot (a 300 ms filter) did not remove it. Which of these is right is a separate question
  from leak versus urgency and must be settled first, or the (L, u) fit will report whichever distortion best mimics
  the missing component (the literature's warning on mimics).

## What didn't work
- Imposing leak 3 /s on the fitted parameters without re-matching stalls the accumulator (responded fraction 0.42);
  hence the control re-matching grid. The grid proposed a = 11.65 for PSUIM6 urgency 1 /s and crashed the first full
  run (simulator limit a < 10); fixed by skipping such grid points and caching matched parameters per (mouse, variant).
- Re-matching only (a, drift gain) cannot hold the control behaviour fixed for strong leak or urgency (NLL costs above);
  a full refit per variant would be needed for a cleaner illustration, which is the joint fit of the route anyway.
- The 10-mouse per-bin counts computed in session from pulse_psychometric_stage.load_trials were not saved; the
  profile CSV holds the counts for the three mice (added to the data rows in the re-render).

## How to reproduce
```
NUMBA_NUM_THREADS=16 PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -B -W ignore -m scripts.ddm.pulse_leak_urgency_signatures \
  --mice PSUIM6 PSUIM7 DBM6 --cache <scratch>/cache --out dissemination/figures/qc
```
About 2 h on 16 CPU threads for the matching and simulations (three mice x seven settings; cache files timestamped
00:07 to 01:52 UTC, one crash and a cached rerun in between); seed 0; inputs
/mnt/data/processed/ddm/ddm_inputs_global.npz (responded only) and fits_resp_final control-split fits.
`--quick` runs a smoke test. The literature report was produced by four research subagents (notes in
.agents/research_notes/Pulse tests of leak vs urgency/) and a report writer; no data left the machine.

## Caveats
- Illustration only: three mice, coarse re-matching, parameters other than a and drift gain held at the base fit,
  no likelihood fit to pulse trials, no recovery. Per-bin SEs are trial bootstraps within mouse, not a power analysis.
- The data profile pools coherences 0 to 36 % and both pulse signs; the model-data residuals are in units of the
  data's SE and ignore simulation noise (60 repetitions, so small) and the match uncertainty (not small).
- DBM6 is too sparse (SE 6 to 10 pp) to constrain anything; the 10-mouse picture needs the other seven mice.
- Rig enters only through each mouse's own schedule (memory rule: no site split).

## Route: how to get there (proposed; thresholds marked ‡ for the author to fix before any pulse-trial fit)
1. Descriptive package on all 10 mice, local CPU (days): S1 per onset (this script, extended to 10 mice), S2 log-odds
   effect per onset within |coherence| 0 / 9 / 18 / 36 % (extends scripts/ddm/pulse_time_comparison.py), S3 mean and
   SD of RT for positive versus negative pulses by onset plus the quantile shifts. Same code paths on data and
   simulations. This is the empirical contribution whatever the modelling returns.
2. SR2, NDT pinning, local: a per-mouse interval for the non-decision time from the +-100 % trials and the ME latency
   (profile over NDT with the other parameters at the control fit). Point estimates are 0.02 to 0.46 s (median 0.16;
   dissemination/paper_accumulation/tables/parameters_common_model_resp_2026-10-27.md); if the interval is wider than
   the onset spacing (about 180 ms‡), leak and urgency estimates are declared uninterpretable and the route stops.
3. Decide the pulse-response misfit before (L, u): fit the candidates that could remove the late reversal (late
   pulse-insensitive mixture; pulse component outside the accumulator; later sensory spread) one at a time, judged by
   S1 on PSUIM6/7 (effect within 1.2 s, none later, no reversal, within 2 SE‡). Only a candidate that passes carries
   on. If none passes, report "the family's pulse response is mis-specified; leak versus urgency not decidable" and
   stop with the descriptive package.
4. SR3, recovery on the real schedules, cluster (after the synthetic-data pairing bug in
   reports/2026-10-28-recovery-synthetic-data-mismatch.md is fixed): generating grid L in {0, 1, 3, 10} /s x u in
   {0, 0.3, 1, 3} /s, w matched to the observed 0.3 log-odds, >= 20 datasets per cell, refit with the same pipeline;
   report bias and R^2 for L, u, w, NDT, the confusion and inversion matrices for {neither, leak, urgency, both}, and
   null false-positive rates with binomial intervals. Stop if the inversion diagonal is below 0.8‡ or the null
   false-positive upper bound exceeds 0.10‡.
5. Joint fits, cluster: per mouse, (L, u, w) free with NDT pinned (step 2), control + pulse trials, responded-only
   likelihood, five-fold CV; nested L = 0, u = 0, L = u = 0. Primary decision: each fitted model simulated on the real
   schedules must reproduce S1 to S3 within the data's bootstrap uncertainty (SR4); held-out NLL secondary. Result
   stated as the region of the (L, u) plane consistent with the data per mouse; group claim only if >= 6 of 10 mice‡
   agree after Holm (SR5). Nothing else freed at the same time.
Expected outcome from this report: steps 1 and 2 are cheap and worth doing now; step 3 is the real obstacle; the
honest end state is "L below about 1 /s, u below about 1 /s, or undecidable", not a named winner.

## Open questions and next steps
- [ ] Author: fix the ‡ thresholds and confirm the order (descriptive package and NDT check before any cluster fit).
- [ ] Extend the S1 script to all 10 mice and add S2 and S3-by-onset (local; no new fits).
- [ ] NDT profile per mouse from the +-100 % trials (local).
- [ ] Which candidate for the missing late reversal to test first (step 3); not decided here.
- [ ] Recovery grid depends on the paired-synthetic-data fix (plans/2026-10-28-full-recovery-matrix.md, on hold).
