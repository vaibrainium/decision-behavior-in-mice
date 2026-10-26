# Report: Main Figures 3–5 assembled
Date: 2026-10-26   Agent: Codex   Commit: uncommitted atop 0b76e80
Plan: plans/2026-10-20-paper-writeup.md (AB1–AB4)

## Question
Can the three central model/pulse figures be assembled now from audited saved results, before further manuscript prose?

## Summary
Figures 3–5 are assembled as versioned PDF, SVG and 300-dpi PNG files with adjacent source-data CSVs. Figure 3 keeps
held-out model comparisons separate from descriptive in-sample fit quality. Figures 4–5 make the randomized behavioural
pulse effect and the model's temporal mismatch the visual centre of the paper. No fitting or cluster work was run.

## Findings
- VERIFIED: Figure 3 reproduces summed extrema-minus-accumulator held-out NLL = 345.741 and 6/10 mice above the
  working 10-NLL threshold. Source: selected `fig3_*_source_strategy.csv`; script
  `scripts/paper/fig3_control_models.py`; command `.venv/bin/python -m scripts.paper.fig3_control_models`.
- VERIFIED: Figure 3 component sums are remove `sv` +1017.779, remove fast guesses +858.111, add leak −21.350,
  add urgency +25.773 and add both −33.266 NLL. Source: selected `fig3_*_source_components.csv`; same script/command.
- VERIFIED: Figure 4 reproduces 5.844356 pp [1.799491, 9.889221], raw p = 0.009705 and Holm p = 0.019410, with
  10,281 trials, 717 supported cells, 118 pre-onset responses and 1,709 no-response trials. Source: selected
  `fig4_*_source_{group_estimates,coverage}.csv`; script `scripts/paper/fig4_pulse_behaviour.py`.
- VERIFIED: Figure 5 reproduces observed window increments 0.388, 3.210, 2.125 and 0.118 pp versus choice-gain model
  increments 2.997, 4.723, 0.249 and −2.977 pp. PSUIM6/7 held-out choice benefits are 10.400/10.005 NLL and remaining
  objective costs 96.010/106.609. Source: selected `fig5_*_source_{windows,heldout_tradeoff}.csv`; script
  `scripts/paper/fig5_model_mismatch.py`.

## What didn't work
- Constrained layout collapsed the nested Figure 3 axes. The selected v4 uses an explicit GridSpec; earlier same-day
  versions are retained but superseded as layout drafts.
- A four-axis nested objective display made Figure 5C unreadable. The selected v3 normalizes each objective profile
  within its displayed gain range; held-out NLL magnitudes remain explicit in Figure 5D.

## How to reproduce
```bash
.venv/bin/python -m scripts.paper.fig3_control_models
.venv/bin/python -m scripts.paper.fig4_pulse_behaviour
.venv/bin/python -m scripts.paper.fig5_model_mismatch
```
Scripts never overwrite: reruns add a version suffix. Figure 3 reuses the newest adjacent deterministic fit-quality
source CSV when available; otherwise it simulates 20 fixed-seed repetitions per control trial from `ddm/fits_final`.

## Caveats
Figure 3D is in-sample/descriptive and its simulated repetitions are not animals. Figure 5A–B is descriptive, Figure
5C is in-sample and only PSUIM6/7 strongly constrain the gain tradeoff. Figures 1–2 retain unresolved denominator/replay
display audits and are not locked.

## Open questions and next steps
- [ ] Close Figure 1 mask/denominator audit and rebuild it with the shared colour semantics.
- [ ] Close Figure 2 denominator/replay mapping and rebuild it.
- [ ] Reconcile the approved neuropaper legend against the selected artwork after Figures 1–2 are locked.
