# Plan: motion-energy filter comparison (current mouse filter vs Okazawa et al. 2018) and fit to mouse behaviour
Status: active
Created: 2026-10-29 by Claude (Opus 5.5)
Related reports: reports/2026-10-27-pulse-me-old-vs-new-filter.md; dissemination/reports/motion-energy-methods.md

## Goal
Author request: "test it against original motion filter used by Okazawa and also compare it to mice". Done = for each
filter, (1) its response to our pulses (peak, area, delay) and to coherence (linearity, direction selectivity), and
(2) how well its motion energy predicts mouse choices beyond nominal coherence, compared across filters with mice as
the unit.

## Context
- Okazawa, Sha, Purcell & Kiani 2018 (Nat Commun 9:3479, doi 10.1038/s41467-018-05797-y), Methods, read in full
  text (Europe PMC PMC6113286): Adelson-Bergen filters, spatial f = cos^4(a) cos/sin(4a) exp(-y^2 / 2 wg^2) with
  a = atan(x / 0.35), wg = 0.05; temporal g_n = (60t)^n exp(-60t) [1/n! - (60t)^2/(n+2)!], n = 3, 5. Tuned to MT and
  to their 5 deg/s dots; ME lags the stimulus by ~50 ms. Same equations and constants as Kiani et al. 2008
  (methods report table), which also gives sigma_c 0.35 deg, k 60 /s.
- Current mouse filter (methods report 3.1): sigma_c 6 deg, sigma_g 3 deg, k 34 /s, 0.5 deg grid; 0.080 c/deg,
  2.4 Hz, 30 deg/s (dot speed ~30 deg/s on both rigs). Pulse response: peak 0.27 (UCLA) / 0.42 (UW) per unit change,
  area 0.045 / 0.074 s.
- Okazawa's filter literally applied: preferred speed ~3.2 deg/s and SF ~1.36 c/deg (methods report 2.1 table),
  i.e. 9x slower than our dots and above mouse acuity (~0.48 c/deg, Umino et al. 2008). Expect weak direction
  selectivity on our stimulus. Its temporal filter (k 60) is ~1.8x faster than ours, so its pulse peak is higher and
  earlier; for a linear integrator the area, not the peak, matters.
- Hidden coherence (methods report 5.1): stimulus noise is mostly a fixed per-trial bias, so choice prediction tests
  spatial/speed tuning more than temporal filtering. Pulse timing is the temporal test.
- GPU not available now (NVML error); CPU only, 32 cores.

## Filters
- F0: current mouse filter (existing ME; no recompute).
- F1: Okazawa literal: sigma_c 0.35 deg, wg 0.05 deg, k 60 /s. Needs a fine grid (0.1 deg; wg below one sample is
  treated as a single row). Temporal window to < 1% of peak.
- F2: Okazawa temporal filter (k 60) with spatial filter rescaled to keep the dot speed (sigma_c ~3.3 deg,
  sigma_g = sigma_c / 2; exact values from SF ~ 0.477 / sigma_c, TF ~ 0.071 k). Isolates the temporal constant.

## Assumptions
- scripts/motion_energy.py functions accept alternative parameter dicts (check; if not, add a params argument, no
  change to the default).
- Per-rig calibration to % coherence (assemble_motion_energy.py) applies unchanged to new filters.
- CPU time (estimate, not measured): F2 at 0.5 deg ~0.4 h on 32 cores for all trials; F1 at 0.1 deg several hours
  for all trials, so F1 on a subset unless approved otherwise.

## Steps
- [x] 1. Timing pilot: 50 trials per rig with F1 and F2; report s/trial and projected totals. Check F0 reproduces the
      stored ME exactly (same code path).
- [ ] 2. Compute F2 for all responded trials; F1 for the subset agreed with the author (default: all pulse trials +
      control trials at 0% and +-9% coherence, all mice). Outputs to new directories
      <processed>/motion_energy_mouse_okazawa_{literal,temporal}/; nothing existing overwritten.
- [ ] 3. Per-rig calibration and sanity checks per filter: mean ME vs coherence (slope, linearity), mean at 0%,
      direction selectivity (mean at +-100% over SD at 0%).
- [ ] 4. Pulse response per filter and rig (method of build_ddm_inputs.pulse_response): peak, time to peak, area;
      step response; figure overlaying F0/F1/F2 with the nominal pulse.
- [ ] 5. Mice, choices: per mouse, 5-fold CV logistic regression of choice on nominal coherence (categorical) +
      residual ME (trial ME minus mean ME for the coherence and rig, averaged from 0.1 s to the RT); compare held-out
      log-likelihood gain over coherence-only across filters. Mouse as unit: paired Wilcoxon across mice, Holm over
      the filter pairs, effect size; responded trials only.
- [ ] 6. Mice, filter tuning: table of each filter's SF / TF / speed against the mouse V1 and behavioural values in
      the methods report (Niell & Stryker 2008; Andermann et al. 2011; Umino et al. 2008), and against dot speed.
- [ ] 7. Verify: F0 numbers match the stored DDM inputs (pulse kernel area 0.0449 / 0.0738 s); F2 pulse area within
      ~10% of F0 (area should be filter-independent after calibration); report anything else as a finding.
- [ ] 8. Report, STATUS; dashboard only if the author asks.

## Out of scope
Refitting the DDM with a new filter (would follow only if a filter predicts choices clearly better); adaptation
front end (separate plan); per-site interpretation (rig is a covariate only).

## Log
- 2026-10-29: plan written at the author's request; awaiting approval because of CPU cost.
- 2026-10-29: author approved running on Hyak ("write code, push it, pull it there and run on hyak"); both filters on all
  trials. Pilot (6 trials, local CPU): compute_mouse_me now filters time in blocks of y rows (max_elements; identical
  output, max diff 0); mouse filter reproduces stored pipeline ME (max rel diff 3e-7); okazawa literal ~16 s/trial on
  CPU (first unblocked try was OOM-killed), okazawa_temporal ~1 s/trial. Job script scripts/slurm/motion_energy_filter.slurm.
- 2026-10-29: pushed (5c4e4fd, 4e1c231); Hyak session asked to run. Blocked: valid_data.csv not on Hyak
  (CLUSTER_DATA_PATH/processed has only ddm/); author to copy it (no ssh to Hyak from this machine). Analysis script
  scripts/me_filter_comparison.py tested on the mouse filter alone: reproduces pulse area 0.0448 / 0.0734 per unit
  (UCLA / UW) and hidden-coherence correlation 0.875 / 0.974. Next: steps 2-8 once the Hyak shards are synced back.
- 2026-10-29: Hyak container lacks cv2; author chose a side-install on gscratch (opencv-python-headless 4.11.0.86,
  --no-deps, PYTHONPATH /mnt/data/pylib). Shard resume added (a0261ef). Local check, 12 non-pulse trials at +-100%
  (3 per rig x sign; scratchpad me_alias): okazawa literal reports the motion REVERSED on both rigs (raw mean ME at
  +100% negative, at -100% positive; consistent across trials); okazawa_temporal and mouse have the right sign.
  SUSPECTED cause: spatial aliasing (dots jump ~0.48-0.5 deg/frame, ~2/3 of the filter's 0.74 deg period). The
  per-rig calibration divides by the (negative) slope and would hide this; the analysis now reports raw slopes.
