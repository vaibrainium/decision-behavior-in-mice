# Report: pulse-aligned motion energy, old (master, nb 2.11) vs new mouse filter
Date: 2026-10-27   Agent: Claude Opus 5.5   Commit: 85d4f8d (+ uncommitted scripts below)

## Question
Author suspected the pulse-aligned ME in the DDM inputs is wrong, because notebook 2.11 on master shows sharp, undelayed pulses.

## Summary
Not a calculation bug. The difference is the filter change of 2026-10-13 (dissemination/reports/motion-energy-methods.md §2.2-2.3, §3.1-3.2).
Stimulus replay and pulse placement are identical on master and this branch. The old filter is non-causal (centred padding,
unflipped kernels, 6-frame temporal window), so its pulse response starts about 1 frame before onset and peaks at about 0-17 ms with
height close to the nominal change. The new causal mouse filter (k 34 /s, 0.55 s) delays the response (rise ~50 ms, peak ~120 ms) and spreads it over ~300 ms
(peak about 1/3 of nominal, area ratio 0.99; see refit plan log).

## Findings
- VERIFIED: master `get_stimulus_array_ucla` and branch `render_stimulus_deg` switch coherence at the same frame (`i == onset_frame - 1`).
- VERIFIED: current `motion_energies_normalized/me_global.pkl` (25,508 trials, written 2026-10-14) is the new-filter output; nb 2.11's saved
  outputs (113,874 entries) came from an earlier version of that file, which has since been overwritten.
- VERIFIED (figure): old filter's pulse-minus-control signal peaks at the pulse and ≈ ±(pulse − baseline) % coh; new peaks ~120 ms later at ~1/3 height.
  Source: scripts/ddm/pulse_energy_old_vs_new.py -> dissemination/figures/qc/pulse_motion_energy_old_vs_new_2026-10-27.png.
- VERIFIED: nb 2.11 x tick labels use frames/60*100, so "100 msec" there is 60 frames = 1 s.

## How to reproduce
`.venv/bin/python -m scripts.ddm.pulse_energy_old_vs_new`; `.venv/bin/python -m scripts.ddm.pulse_energy_by_coherence`.

## Caveats
Old ME is cut at the RT, so late frames of the window use fewer trials. Old units are rescaled by a per-rig control slope here (nb 2.11 used session max).

## Open questions and next steps
- [ ] Author: keep the new filter (all fits use it), or ask for a sensitivity check with a faster temporal filter. Changing it would invalidate the existing fits.
- [ ] For display only, ME may be plotted against t − ~100 ms (methods report §3.2), stated in the caption.
