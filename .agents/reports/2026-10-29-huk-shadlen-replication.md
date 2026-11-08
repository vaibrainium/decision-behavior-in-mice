# Report: Huk & Shadlen 2005 behavioural pulse analyses replicated on the mouse data
Date: 2026-10-29   Agent: Claude (Opus 5.5)   Commit: 57a47c0 (scripts uncommitted at writing)
Plan: plans/2026-10-29-huk-shadlen-replication.md

## Question
Author: "Look at this paper which also does pulse. Understand and see if we can replicate this." Huk AC, Shadlen MN
2005, J Neurosci 25:10420 (doi 10.1523/JNEUROSCI.4684-04.2005), read via PMC6725829 (Methods and behavioural Results
verbatim; Eqs 4-10 are images there and were not read; Discussion not read).

## Summary
Both of their behavioural analyses run on our data and give the same qualitative picture: a pulse shifts the
psychometric function by a fixed coherence equivalent, with no separate effect on RT, and it affects choices made from
about 0.3 s after pulse onset onward, not earlier. Differences: the shift is much larger in coherence units (12% vs
1.6%), the effect lasts to about 1.2-1.8 s after the pulse and then fades, and pulses change the RT distribution shape
slightly (KS p < .001, D 0.03-0.04) where theirs did not. The diffusion fit to mean RT is poor in mice, so per-mouse
k, A and t_nd are not interpretable; gamma is carried by the choices.

## Paper (VERIFIED from the PMC text, via a fetch agent)
- 2 monkeys, RT task, coherences 0, 3.2-51.2%; 100 ms motion pulse in a dim background texture at 100/150/211/287/392
  ms; 1/3 positive, 1/3 negative, 1/3 no pulse. Responses before or during the pulse excluded (~3%); RT 100-1650 ms.
- Joint choice + mean RT fit (Eqs 6-7): pulse = equivalent coherence gamma for choices, gamma + delta for RT.
  Table 2 combined: gamma 1.60% (SE 0.08), delta -0.05% (0.13), LR p 0.70; k 0.426, A 22.8, t_nd 417 ms.
- Fig 4: 75 ms bins of RT - pulse onset, logistic with pulse indicators, effects b2/b1, b3/b1 (% coherence);
  "responses initiated from 300 to 900 ms after pulse onset showed a clear effect"; none earlier.
- KS on standardized RT distributions: all p > 0.6.
- Unreconciled in the paper: Table 1 (model simulation) lists "effective pulse strength 10% motion coherence".

## Our implementation
`python -m scripts.behavior.huk_shadlen_replication --date 2026-10-29` (about 3 min). Tables
`dissemination/paper_accumulation/tables/huk_shadlen_replication_2026-10-29_{joint_fits,timecourse_fine,timecourse_per_mouse,timecourse_tests,ks}.csv`;
figure `dissemination/paper_accumulation/figures/qc/huk_shadlen_replication_2026-10-29.png`.
- Trials: trial_table (pulse_followup 20261023T191030Z_fa8de8b), responded, symmetric cells, control / positive /
  negative (null pulses excluded); 22,437 trials, 408 removed for responding before the end of the (virtual) pulse;
  22,029 kept. Pulse = right (+1) / left (-1). Virtual onsets for controls: control_onset_s; virtual duration = rig
  median pulse duration.
- Diffusion form ASSUMED (equations are images): Palmer et al. 2005 proportional-rate diffusion,
  P = 1/(1+exp(-2kAC)), mean decision time A/(kC) tanh(kAC), C as a fraction, time in ms; t_nd >= 0. "huk" has no
  bias (as in the paper); "bias" adds a coherence offset. Nelder-Mead + Powell from several starts, nested fits warm
  started; SE from a numerical Hessian.

## Findings (VERIFIED unless marked)
- Pooled, Huk model: gamma 11.9% coherence (SE 1.0); delta -0.5% (4.2), LR p 0.90. With bias: gamma 12.1% (1.0),
  delta 1.4% (3.8), p 0.72. k 0.029, A 37.2, t_nd 291 ms.
- Per mouse (huk): gamma -2.4 (DBM12) to 24.7% (PSUIM10); 9/10 positive, mean 9.4%, Wilcoxon p 0.006 (computed
  from _joint_fits.csv, inline command in this session). delta n.s. in 9/10 (DBM5 p 0.044 uncorrected, 10 tests).
- Fit quality: choices well described; mean RT poorly (pooled RTs 1.25-1.9 s, noisy across coherences); t_nd at the
  0 bound in DBM12, DBM13 (bias), DBM15 (bias), PSUIM7 and PSUIM10 (bias), 1.4 s in DBM14. Per-mouse k, A, t_nd are
  not interpretable.
- Time course, pooled 75 ms bins: right pulses +10-46% coherence and left pulses -7 to -29% in bins from 0.38 to
  1.2 s after onset; near 0 (within SE) after about 1.25 s; bins before 0.3 s unstable (few trials, small b1).
  Right-pulse shifts are larger than left (same asymmetry as reports/2026-10-28-pulse-psychometric-parameter-bootstrap.md;
  SUSPECTED, not tested).
- Time course per mouse (right - left logit; Wilcoxon, Holm over 6 bins): 0-0.3 s -0.08 (3/9 positive, Holm 1.0);
  0.3-0.6 s +0.44 (8/10, p .037, Holm .22); 0.6-0.9 s +0.70 (8/10, p .037, Holm .22); 0.9-1.2 s +0.56 (8/10, Holm .34);
  1.2-1.8 s +0.39 (7/10, Holm .48); 1.8-5 s -0.02 (6/10, Holm 1.0). Shape as in the paper; no bin survives Holm with
  10 mice.
- KS (standardized RT within mouse x coherence): pulse vs none D 0.030 p 1e-4; right vs left D 0.042 p 3e-4; right vs
  none D 0.044 p < 1e-4; left vs none D 0.022 p 0.069. Unlike the paper, pulses change the RT distribution slightly.
- SUSPECTED, back-of-envelope (not computed from data): our pulse adds about (100 - |C|)% x 0.05-0.067 s, about 0.05
  coherence x s; spread over a ~1 s decision this is ~5% coherence, below the 12% measured. This is the same gap as the
  DDM underprediction (reports/2026-10-29-joint-control-pulse-refits.md).

## What didn't work
- L-BFGS-B with raw parameters: t_nd did not move from its start and Hessian SEs were meaningless; replaced by scaled
  Nelder-Mead/Powell with a numerical Hessian.
- A column named C clashed with patsy's C(); renamed.

## Caveats
- Equation forms ASSUMED from the prose (Palmer 2005); Table 2 magnitudes are consistent with it.
- Their pulse is a weak texture motion; ours is 100% coherent dots for 50-67 ms. Coherence-equivalent sizes are not
  comparable as stimuli, only as behavioural effects.
- Pooled time-course fits use mouse intercepts but a common coherence slope; PSUIM6/7 dominate pooled bins.
- Mean RT includes correct and error trials (as in the paper); mouse RT distributions are long-tailed (to 5 s).

## Open questions and next steps
- [ ] Read the paper's Discussion and Figs 8-10 (model of pulse vs time) if the comparison goes into the paper.
- [ ] Decide whether the Huk-style gamma (equivalent coherence) is the pulse effect size to report; it is easy to
      compare with the primate literature.
- [ ] Test the right/left asymmetry directly (gamma_right vs gamma_left).

## Addendum 2026-10-30: per mouse, and congruent vs incongruent (author requests)
Same script and command; new tables `_timecourse_mouse_150ms.csv`, `_congruency_pooled.csv`, `_congruency_mouse_150ms.csv`;
figures `huk_shadlen_replication_2026-10-29_per_mouse.png` and `_congruency.png`.
- Per mouse: psychometric and chronometric curves with the joint fit (bias model), plus the time course in 150 ms
  bins (75 ms bins hold too few trials per mouse). Deviation from the paper: per-mouse effects are converted to %
  coherence with the mouse's overall b1, not the per-bin b1 (unstable at these counts). Bins need >= 8 trials of each
  pulse type; PSUIM10 has 1 bin, DBM13 4, DBM14 5.
- Per mouse, VERIFIED (figure): PSUIM6 and PSUIM7 show right and left pulses separating from about 0.3 to 1.2 s;
  DBM6 and PSUIM5 show it less consistently; DBM12-15 and DBM5 are noisy with no clear pattern.
- Congruency: regressors signed by pulse direction (positive = toward the pulse); 0% pulse trials dropped; responses
  < 100 ms after pulse onset blocked (author). Pooled 0.32-0.92 s: congruent +17.7 to +44.1% coherence, incongruent
  +16.5 to +31.5%, both toward the pulse, congruent mostly larger; both near 0 after about 1.25 s. Bins 0.10-0.32 s
  are unstable (76-184 trials per type, small per-bin b1; e.g. incongruent -116.6 at 0.10 s). PSUIM10 has too few
  trials for any per-mouse bin. Per mouse the congruent-incongruent difference is visible only in PSUIM7 (congruent
  larger 0.45-1.25 s); other mice are within noise. No test run on the congruency difference (descriptive).
- Per-mouse overlay (author request; `_overlay_per_mouse.csv`, `_overlay_summary.csv`, figure `_mouse_overlay.png`):
  shared bins 0.1-0.3-0.6-0.9-1.2-1.5-2.1 s, first 100 ms blocked, mouse b1, >= 8 trials per pulse type, mean +- SEM
  over mice, Wilcoxon on logits, Holm within each set (24 tests over both sets; 12 each). VERIFIED: right pulses +17.5%
  (0.3-0.6 s, 7/9 mice, p .039) and +25.1% (0.6-0.9 s, 8/10, p .027), Holm .43 / .33; left pulses -3 to -12%, mostly
  within noise (0.9-1.2 s: 8/10 toward left, p .084). Congruent +16.1% at 0.3-0.6 s (8/9, p .012, Holm .14);
  incongruent +12 to +15% at 0.3-0.9 s (n.s.); congruent and incongruent overlap in every bin. Nothing survives Holm.
  The pooled figure's larger effects come mostly from PSUIM6/7 (about 55% of trials).

## Correction 2026-10-30: congruency time courses (supersedes the congruency and overlay numbers above)
- BUG (VERIFIED): time-course fits were logistic in linear coherence including +-100%. Mice lapse at 100% (P correct
  ~0.85), which the linear term cannot follow, and only incongruent pulses occur at 100% (1,498 trials; congruent 0),
  so the misfit loaded on the incongruent term and reversed the congruency ordering. Pooled 0.3-1.2 s, logit toward
  pulse: linear with +-100% cong +0.54 / incong +0.40; linear without +-100% +0.34 / +0.57; categorical coherence,
  all trials +0.31 / +0.55 (inline check, this session). Model-free (pulse minus matched controls, same coherence and
  bin): incong >= cong from 0.6 s.
- Fix: all time-course analyses use |C| <= 36% (the paper's range ends at 51.2%), so congruent and incongruent share
  coherences 9/18/36. The joint fit (analysis 1) is unchanged. Per-mouse overlay bins now need >= 20 trials per pulse
  type (at 8, bins of ~10 trials dominated the mean, e.g. PSUIM10 -109%).
- Corrected overlay (5-8 mice per bin; `_overlay_summary.csv`): congruent and incongruent both toward the pulse at
  0.3-1.2 s (cong +19.2 / +5.0 / +15.0%, incong +7.6 / +21.7 / +15.2% in 0.3-0.6 / 0.6-0.9 / 0.9-1.2 s), no consistent
  ordering, nothing survives Holm. Direction: right pulses +24.8 / +24.9 / +16.8% (8/8, 6/7, 6/7 mice); left pulses
  +8.1 / -2.9 / -10.9%.
- Pooled 75 ms congruency bins remain unstable before ~0.4 s (per-bin b1 small); from 0.4-1.0 s incongruent +18 to
  +24%, congruent -0.5 to +19%.
- Also changed by the restriction: the coarse per-mouse direction test (`_timecourse_tests.csv`) is now weaker
  (0.3-1.2 s bins 6-7/10 mice positive, Holm >= 0.79); the pooled and per-mouse direction figures use |C| <= 36%.

## Revision 2026-10-30 (author): all coherences, no late pulses (supersedes the correction above and all earlier numbers)
- Late pulses dropped everywhere (trial_table onset_stratum == "late", pulse and matched controls: 2,858 trials);
  19,560 trials kept (19 responded before the pulse ended). +-100% kept (author). Pulse terms now come from logit
  P(right) ~ C(coherence) + pulse terms (+ mouse), which absorbs the 100% lapses; b1 for % coherence from a linear fit
  to |C| <= 36%. Pooled 75 ms bins use one b1 for all bins (per-bin b1 near 0 before 0.4 s; ratios kept as
  *_pct_bin_b1). Deviations from the paper: categorical coherence and one b1.
- Joint fit (huk, pooled): gamma 13.0% (SE 1.0), delta +1.2% (3.9), LR p 0.76. Per mouse 10/10 positive (0.9 to
  24.7%), Wilcoxon p 0.002.
- Pooled direction, 0.4-1.2 s: right +14 to +40%, left -7 to -24% coherence; KS pulse vs none D 0.035 (p < 1e-4).
- Pooled congruency, 0.3-0.9 s: congruent +12 to +19% (one bin -2.4), incongruent +7 to +37%; both toward the pulse,
  incongruent >= congruent from ~0.5 s.
- Per-mouse overlay: only 6 mice reach >= 20 trials per pulse type in a bin (DBM12, DBM5, DBM6, PSUIM5/6/7). Right
  +18 to +21% at 0.1-0.9 s (0.6-0.9 s 6/6, p .031, Holm .38); left -20 to -24% at 0.6-1.2 s (5/6, 6/6). Congruent
  and incongruent overlap except 0.6-0.9 s (incong +34.0, 6/6, p .031, Holm .25; cong +0.5). Nothing survives Holm.
- Sign convention changed (author 2026-10-30, "why is incongruent pulse pushing choice to congruent direction"): the
  earlier "toward the pulse" sign made incongruent effects positive although they cause errors (pooled P(correct)
  incongruent 0.51 / 0.55 / 0.71 vs no pulse 0.58 / 0.68 / 0.77 at 9 / 18 / 36%). Congruency effects are now
  "toward the correct side": congruent > 0, incongruent < 0. Data unchanged, only the incongruent sign. Pooled overlay
  bins: congruent +13.5 / +11.3 / +7.4%, incongruent -12.2 / -26.1 / -14.8% at 0.3-0.6 / 0.6-0.9 / 0.9-1.2 s (z p
  < .01 except congruent 0.9-1.2 s, p .085). Numbers above that give incongruent as positive refer to the old sign.
- Per-mouse congruency figure (author request; `huk_shadlen_replication_2026-10-29_per_mouse_congruency.png`): per mouse
  P(correct) and mean RT vs |C| for no pulse / congruent / incongruent (curves from the mouse's direction fit with bias,
  averaged over right and left), and 150 ms time courses toward the correct side (>= 8 trials per type). The earlier
  per-mouse congruency panels had the old sign; regenerated. VERIFIED (figure): PSUIM6 and PSUIM7 show congruent > 0
  and incongruent < 0 from ~0.3 to ~1.3 s; PSUIM5 from ~0.6 s; DBM6 incongruent dips at 0.6-0.8 s; DBM5 and DBM12-15
  and PSUIM10 too sparse (0-9 bins). Some coherence cells are missing in UW mice (e.g. DBM12 36%) because the
  symmetric-cell filter drops whole cells.

## Addendum 2026-10-30: non-parametric congruent vs incongruent comparison (author request)
`python -m scripts.behavior.congruency_roc --date 2026-10-30`; tables
`dissemination/paper_accumulation/tables/congruency_roc_2026-10-30_{per_mouse,summary}.csv`.
Score per pulse trial = choice toward the pulse (0/1) minus P(that choice) on no-pulse trials of the same mouse,
coherence and RT - onset bin; AUC (Mann-Whitney) congruent vs incongruent (0.5 = equal, < 0.5 = incongruent
larger). |C| 9-36% only, no late pulses, first 100 ms blocked. Equivalence margin +-0.05 AUC (my default; the author
did not set one), 90% mouse-bootstrap CI.
- All responses >= 0.1 s after onset: mean AUC 0.512, 95% CI [0.494, 0.531], 90% CI [0.497, 0.528] inside the margin
  (equivalent); 5/10 mice > 0.5, Wilcoxon p 0.38; pooled 0.488 [0.465, 0.531]. Diluted by responses outside the
  window where either pulse acts.
- 0.3-1.2 s (window chosen after seeing the time courses, post hoc): mean AUC 0.466 [0.441, 0.495], 90% CI
  [0.445, 0.490], not equivalent; 8/10 mice < 0.5, Wilcoxon p 0.064; pooled 0.442 [0.417, 0.491]. Mean effect toward
  the pulse: congruent +2.6 pp, incongruent +8.2 pp (mouse means). PSUIM6 and PSUIM7 individually p < .001.
- Interpretation (SUSPECTED): within the window incongruent pulses move choices more. Part of this is ceiling
  (congruent pulses fall on trials that are mostly correct already); the logit-scale estimates (pooled overlay bins,
  incongruent larger at 0.6-1.2 s) suggest it is not only ceiling. Not tested directly.
- ROC caveat (VERIFIED by simulation, `congruency_roc.py` null_auc, 200 draws): choices are 0/1, so the scores take
  baseline-dependent values (congruent baseline P(toward) ~0.66, incongruent ~0.35) and the ROC curves are step-shaped
  by that structure. If the pulse had no effect, the mean-over-mice AUC would be 0.509 [0.485, 0.532] (all) and
  0.503 [0.476, 0.539] (0.3-1.2 s), close to 0.5 here but not guaranteed. The AUC does not have a clean null for
  "equal effects"; the direct test is the per-mouse difference in mean effect: 0.3-1.2 s congruent 2.6 vs incongruent
  8.2 pp, difference -5.7 pp, 7/10 mice incongruent larger, Wilcoxon p 0.131 (all >= 0.1 s: +1.1 pp, p 0.695). The
  incongruent > congruent asymmetry is therefore suggestive, not established. Figure: per-mouse ROC curves (thin),
  pooled (bold), `congruency_roc_2026-10-30.png`.
- ROC on panel 4 (author suggestion; `congruency_roc.py` panel4_roc, table `congruency_roc_2026-10-30_panel4.csv`,
  figure `congruency_roc_panel4_2026-10-30.png`): per-mouse x bin logit effects toward the pulse (congruent vs
  sign-flipped incongruent; 54 points, 10 mice; separated fits dropped). Paired label-swap permutation, Holm over 6
  bins. All bins: AUC 0.556, p 0.35, incongruent larger in 23/54 (Wilcoxon p 0.30): no detectable asymmetry. By bin:
  0.1-0.3 s 0.80 (p .11), 0.3-0.6 s 0.77 (p .056), 0.6-0.9 s 0.15 (p .030), 0.9-1.2 s 0.33, 1.2-1.8 s 0.69,
  1.8-5 s 0.64; none survives Holm (min 0.18). SUSPECTED: congruent larger early, incongruent larger at 0.6-0.9 s
  (a timing difference rather than a size difference); could be noise. Bins within a mouse are not independent.
- Panel-4 ROC from 250 ms after pulse onset (author request; bins 0.25-0.55-0.85-1.15-1.45-1.8-5 s; table
  `congruency_roc_2026-10-30_panel4_from250ms.csv`, effects `_panel4_from250ms_effects.csv`, figure
  `congruency_roc_panel4_from250ms_2026-10-30.png`): all bins AUC 0.460, permutation p 0.52, incongruent larger in
  27/53 (Wilcoxon p 0.43): no detectable asymmetry. By bin: 0.25-0.55 s 0.72 (p .17); 0.55-0.85 s 0.14 (p .008,
  8/9 mice incongruent larger, Holm .051); later bins 0.36-0.64, n.s. Same pattern as from 100 ms: no overall size
  difference, incongruent larger around 0.55-0.85 s (borderline after Holm).
- Model-free effect of each pulse type on choice (author request; `congruency_roc.py` choice_effects; tables
  `congruency_choice_effect_2026-10-30_{per_mouse,summary}.csv`, figure `congruency_choice_effect_2026-10-30.png`):
  change in P(correct) vs matched no-pulse trials (same mouse, coherence 9-36%, RT - onset bin), pp, >= 10 trials per
  mouse x bin. Congruent +17.1 / +14.5 / -2.3 / +4.2 / +2.4 / -3.7; incongruent +6.6 / -4.2 / -15.3 / -7.0 / -4.2 /
  -6.0 at 0.1-0.3 / 0.3-0.6 / 0.6-0.9 / 0.9-1.2 / 1.2-1.5 / 1.5-2.1 s (5-9 mice per point; nothing survives Holm
  over 12; best congruent 0.3-0.6 s 8/9 mice p .020, incongruent 0.6-0.9 s p .039).
- Decomposition (inline, this session, mice with both types per bin): directional part (cong - incong)/2 is steady
  at +5 to +8 pp from 0.1 to 1.2 s (0.9-1.2 s 6/7 mice, p .031); shared part (cong + incong)/2 is +11.8 at 0.1-0.3 s
  and -7.0 at 0.6-0.9 s (0/7 mice > 0, p .016). SUSPECTED: the apparent congruent/incongruent asymmetry over time is
  a non-directional pulse effect on accuracy (any pulse raises accuracy for fast responses and lowers it around
  0.6-0.9 s) added to a constant directional effect. Uncorrected, 5-7 mice per bin; needs confirmation.

## Addendum 2026-10-30: directional vs non-directional pulse effects, pooled (author: pooled only)
`python -m scripts.behavior.pulse_decomposition --date 2026-10-30 --n_boot 300`; tables
`pulse_decomposition_2026-10-30_{bins,tests}.csv`, figure `pulse_decomposition_2026-10-30.png`.
Model: logit P(right) ~ C(coherence) x C(bin) + C(mouse) + D_b * pulse + S_b * sign(C) * any pulse, bins of RT -
onset (0.1-0.3-0.6-0.9-1.2-1.5-2.1-5 s); all coherences, no late pulses. Inference: 300 mouse-bootstrap refits,
two-sided bootstrap p, Holm over 7 bins per term. Cluster-robust Wald tests (10 clusters) reported but unreliable.
- VERIFIED: directional D (toward the pulse) 0.04 / 0.43 / 0.66 / 0.43 / 0.19 / 0.12 / -0.03 logit; Holm 0.023 at
  0.3-0.6, 0.6-0.9 and 0.9-1.2 s; n.s. elsewhere.
- VERIFIED: shared S (toward the correct side, any pulse) +0.22 / +0.01 / -0.23 / -0.10 / -0.08 / -0.27 / +0.07;
  only 0.6-0.9 s has a CI excluding 0 (bootstrap p .017, Holm .117); 2.1-5 s p .030 (Holm .18). No bin survives Holm.
- Conclusion: the pulse acts directionally; a non-directional component (accuracy drop at ~0.6-0.9 s for any pulse)
  is suggestive but not established on pooled data. The earlier per-mouse decomposition (shared -7 pp, 0/7 mice)
  points the same way.
- Does the pulse effect vanish or only get diluted? (author 2026-10-30; inline, this session; same design as
  pulse_decomposition, per bin: D from logit ~ C(coherence) + C(mouse) + pulse, b1 from |C| <= 36%, T = mean RT from
  motion onset; 100 mouse-bootstrap refits.) Benchmark: if the pulse adds fixed evidence that is kept (no loss), its
  coherence equivalent gamma = D/b1 scales as 1/T, so gamma*T is constant. gamma*T (%coh x s): 0.3-0.6 s 14.0
  [11.2, 22.9], 0.6-0.9 s 16.6 [11.1, 22.0], 0.9-1.2 s 14.8 [8.5, 19.1]; then 1.2-1.5 s 4.3 [-1.8, 10.7], 1.5-2.1 s
  5.4 [-0.5, 14.5], 2.1-5 s -2.8 [-13.3, 3.6]. SUSPECTED: up to ~1.2 s after the pulse the decline of gamma is
  dilution by further dot evidence (pulse kept); after ~1.2 s the effect drops faster than dilution, i.e. the pulse's
  contribution is lost. Caveats: benchmark ignores bound selection and disengagement on slow trials; not run in a
  script yet. Plateau ~15 %coh x s = 0.15 coherence x s, about 3x the pulse's nominal stimulus (~0.05 coherence x s;
  rough, my arithmetic).

## Result 2026-10-30: the pulse is kept (only diluted) until ~1.2 s after onset, then lost (supersedes the inline check above)
`python -m scripts.behavior.pulse_dilution --date 2026-10-30 --n_boot 300` (~12 min, CPU); table
`dissemination/paper_accumulation/tables/pulse_dilution_2026-10-30.csv`; figure
`dissemination/paper_accumulation/figures/qc/pulse_dilution_2026-10-30.png`. Method in the script docstring (pooled
trials, all coherences, no late pulses; gamma = D / b1; T = mean RT from motion onset; K = mean gamma x T over 0.3-1.2
s; 300 mouse-bootstrap refits; one-sided bootstrap p for gamma x T below K).
- VERIFIED: plateau K = 15.2 % coherence x s [12.7, 17.5]. gamma x T: 0.3-0.6 s 14.0 [11.1, 23.0], 0.6-0.9 s 16.6
  [9.9, 21.6], 0.9-1.2 s 14.8 [9.1, 19.1] (flat: the decline of gamma from 23.3 to 12.6 % coherence matches dilution
  by later dot evidence).
- VERIFIED: after 1.2 s gamma x T falls below K: 1.2-1.5 s 4.3 [-3.8, 12.0] (p .010), 1.5-2.1 s 5.4 [-1.8, 14.5]
  (p .027), 2.1-5 s -2.8 [-13.6, 5.1] (p .003); Holm over these 3 bins: .020, .027, .009. 0.1-0.3 s is also low
  (0.7, before the pulse acts; Huk & Shadlen saw no effect before ~300 ms).
- Interpretation (SUSPECTED): the pulse is integrated and retained for ~1.2 s, then its contribution to the choice is
  lost faster than dilution predicts. Alternatives not excluded: bound selection and disengagement on slow trials
  (late-after-pulse responses are slow trials), which would also lower gamma x T without forgetting.
- K = 0.15 coherence x s vs the pulse's nominal ~0.05 coherence x s (about 91% coherence for 50-67 ms; rough, my
  arithmetic): while retained, the pulse counts ~3x its stimulus value.
