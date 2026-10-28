# Report: pulse effects split into congruent and incongruent, responded trials
Date: 2026-10-28   Agent: Claude (Opus 5.5)   Commit: (this commit; parent 67ac4ab)
Plan: plans/2026-10-28-pulse-congruency-tests.md

## Question
Author chose the congruent/incongruent framing for the pulse analysis. Are the congruent and incongruent effects, each
against control, significant with mice as the unit?

## Summary
Not after correction. Pooled over stages, congruent pulses shift choices toward the pulse by 3.0 pp [0.3, 5.8]
(8/10 mice, dz 0.80, Holm p 0.096) and incongruent by 3.6 pp [-2.2, 9.4] (7/10, Holm p 0.39); they do not differ
(-0.5 pp, p 0.87). Each is roughly half of the positive-vs-negative contrast (7.52 pp, Holm 0.012), which pools both
directions and does not subtract the noisier control cells. Per-stage tests are all non-significant (late: 6 mice).

## Findings (VERIFIED; scripts/ddm/pulse_congruency_tests.py; tables
dissemination/paper_accumulation/tables/pulse_congruency_{per_mouse,tests}_2026-10-28.csv)
- Spec written before computing (plan): responded, symmetric cells, |c| 9-36%, per-mouse mean over coherences,
  t and Wilcoxon, Holm over 3 (pooled) and over 9 (per stage).
- Pooled: congruent 3.04 pp [0.33, 5.76], t 2.53, Holm p 0.096 (Wilcoxon 0.146); incongruent 3.58 [-2.21, 9.38],
  Holm 0.39; congruent - incongruent -0.54 [-7.83, 6.75], Holm 0.87.
- Per stage (Holm over 9, all >= 0.66): early congruent 4.07, incongruent 2.73; middle 4.23, 3.33; late -0.42, 0.14 pp.
- Check: congruent - incongruent = -0.54 equals minus the asymmetry report's observed A = 0.54 (same definition).
- Between-mouse spread is large for incongruent (DBM15 +18.4, DBM14 -8.9 pp).

## Per pulse time, hierarchical bootstrap (author request; VERIFIED; pulse_congruency_bootstrap_2026-10-28.csv)
Resample mice, then trials within each mouse x category x coherence cell (binomial), 10,000, seed 0; Holm over 9.
| Pulse time | Mice | Congruent (pp) | Incongruent (pp) | Difference (pp) |
|---|---|---|---|---|
| early | 10 | 4.07 [-1.92, 9.94], p 0.17 | 2.72 [-3.85, 8.72], p 0.39 | 1.35 [-8.15, 11.80], p 0.83 |
| middle | 10 | 4.24 [-1.29, 9.67], p 0.13 | 3.33 [-3.86, 10.10], p 0.34 | 0.91 [-6.87, 9.39], p 0.84 |
| late | 6 | -0.42 [-8.01, 6.56], p 0.92 | 0.13 [-9.36, 11.77], p 0.98 | -0.55 [-17.35, 13.37], p 0.98 |
All Holm p = 1.0. Bootstrap CIs are wider than the t intervals because they add trial-level noise.

## What didn't work
- Nothing failed; the framing splits one effect into two smaller tests, each underpowered with 10 mice.

## Caveats
- The positive-vs-negative contrast uses matched cells (mouse x session x coherence x onset) and |c| <= 36 including 0%;
  this uses coherence cells with control as reference. Not the same weighting, so 3.0 + 3.6 is only roughly 7.5.
- Any combined congruency statistic chosen now would be chosen after seeing these results.

## Open questions and next steps
- [ ] Author: which test the paper reports (see session 2026-10-28): keep positive-vs-negative as the tested pulse
      effect with congruent/incongruent psychometric curves as the display, or report the congruency tests as they are.
