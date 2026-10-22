# Figure captions (draft)

Each caption lists the script that makes the figure; every number in a caption comes from that script's printed
output (run on commit `e37cc56` + uncommitted `scripts/paper/`, 2026-10-20). Rerun the script and update the caption
together. Sample sizes: 10 mice (UCLA 4, UW 6); the mouse is the unit for every error bar.

---

## Figure 1. Mice perform a reaction-time motion discrimination task on two rigs

Script: `python -m scripts.paper.fig1_behaviour` → `figures/fig1_behaviour_<date>.pdf`. Layout follows the SfN 2025
poster (Figs 1, 2A, 3A).
Status: data panels done; panel A (mouse/rig illustration) to be drawn from the poster.

**(A)** Head-fixed mouse viewing random-dot motion and reporting its direction by licking the left or right port.
[Illustration to be added.]
**(B)** Trial structure. After a period without licking, random-dot motion appeared; a lick could register only after
a minimum viewing time of 0.3 s. Correct choices were rewarded and errors followed by a time-out before the
inter-trial interval. Trials without a response by 5 s are treated as no response in all analyses. [Durations differ
by rig; to state them, see the note below.]
**(C)** Coherence over time on control trials (grey; 18% base coherence shown as an example) and on pulse trials,
where a brief pulse of ±100% coherence replaced the base coherence early, in the middle or late in the trial. Timing
shown for the UW rig: onsets 50, 233 and 417 ms, 67 ms long. On the UCLA rig onsets were drawn per trial around 61 ms
(early) and 241 ms (middle), SD 15 ms, 51 ms long; UCLA had no late pulses. Red bar, minimum viewing time. Scale bar,
100% coherence.
**(D)** Psychometric function on control trials (no scheduled pulse), all mice. Symbols, mean ± SEM across mice
(10 mice, 50 sessions, 14,015 responded control trials); curve, logistic function with lapse and guess rates fitted to
the mouse-averaged proportions.
**(E)** Median reaction time of correct trials (all responded trials at 0% coherence) per rig. Thin lines, individual
mice (a mouse contributes a point where it has ≥ 10 trials); symbols, mean ± SEM across mice (UCLA circles, 4 mice;
UW squares, 6 mice). On UCLA, median RT fell from 1.72 s at 0% to 0.99–1.45 s at 100% coherence; on UW it depended
little on coherence (1.25 s at 0%, 0.98–1.38 s at 100%).
**(F)** Fraction of control trials with no response by 5 s, same conventions (UCLA 0.165, range 0.088–0.218 across
mice; UW 0.133, 0.080–0.231).
**(G)** Accuracy as a function of reaction time, by |coherence|, both rigs (RT bin edges 0.3, 0.45, 0.6, 0.8, 1.0,
1.3, 1.6, 2.0, 2.5, 3.0, 4.0, 5.0 s; points at the median RT of each bin; shown where ≥ 3 mice have ≥ 10 trials;
mean ± SEM across mice). At 100% coherence, responses faster than 0.6 s were 58% correct, slower responses 88% (mean
of mice).
**(H)** Reaction-time distributions of responded control trials (50 ms bins, mean of per-mouse densities). Responses
faster than 0.6 s made up 12% (UCLA; range 5–26% across mice) and 21% (UW; 14–35%) of responses.

Data: UCLA 32 sessions (1–15 per mouse), 15,302 responded and 2,933 no-response trials; UW 18 sessions (1–6 per
mouse), 10,206 responded and 1,604 no-response trials. Scheduled pulse trials per mouse (incl. no-response): UCLA
early 102–1,475, middle 94–1,493; UW early 98–480, middle 157–706, late 165–798. Reaction time is measured from
motion onset on both rigs.

Notes for authors (not caption text):
- Trial timing in the data (5th/50th/95th percentiles, responded trials), to confirm what each column means before
  the caption gives durations: `fixation_duration` UCLA 1.0 s always, UW 0.51/0.56/1.84 s; `reinforcement_duration`
  UCLA 0.5 s correct, 1.5 s error, UW 0 (not recorded?); `intertrial_delay` correct UCLA 0.25 s, UW 0.5 s, error UCLA
  0.25/0.61/6.71 s, UW 1.0/4.5/20.3 s. The poster's 0.5 s withholding / 0.5 s reward / 1 s time-out match neither rig
  exactly.
- The SfN 2025 poster reported "26 sessions". That number came from `data['session_id'].nunique()`, which counts
  session labels (e.g. "6_1") shared across mice. The data contain 50 mouse-sessions.
- The fit in D is descriptive (least squares in `src/utils/pmf_utils`); its parameters are not interpreted.
- The 15 trials with invalid pulse durations (dropped from the DDM inputs) are included here: 14 UCLA middle-pulse
  trials (affect only the pulse counts) and 1 UCLA control trial (in D–H).

---

## Figure 2. Motion energy of the replayed stimulus

Script: `python -m scripts.paper.fig2_motion_energy` → `figures/fig2_motion_energy_<date>.pdf`. Status: draft done.

**(A)** Space–time profile of a rightward-tuned motion-energy filter (sum of the quadrature pair f1·g1 + f2·g2;
Adelson & Bergen 1985, as in Kiani et al. 2008), with parameters set for mice: σc = 6°, σg = 3°, k = 34 s⁻¹ (preferred
0.08 cycles/deg, 2.4 Hz, ~30°/s). Dashed line, the dot speed (30°/s). Red and blue, positive and negative weights.
**(B, C)** Mean motion energy over time on control trials for each coherence, UCLA (B; 9,258 trials) and UW (C;
4,757 trials). Each trial's stimulus was regenerated from its random seed with the rig's own code and filtered over
the full 5 s (not cut at the response); motion energy is spatially averaged over the screen and calibrated per rig
to equivalent % coherence.
**(D)** Motion energy averaged over 0.33–5 s against programmed coherence (mean ± SD across trials; UCLA filled
circles, UW open squares; dotted line, identity). Fits: UCLA 1.013 × coherence + 0.09 (r = 0.998); UW 1.012 ×
coherence − 0.10 (r = 0.997). The trial-to-trial SD at 0% coherence (3.7% UCLA, 6.3% UW) is analysed in Fig 3.
**(E)** Change in motion energy caused by a pulse, per 100% change in coherence, aligned to pulse onset (pulse trials
minus the mean of control trials at the same coherence and rig; mean ± SEM across trials; UCLA 3,094 and UW 4,100
pulse trials). On both rigs the response reached half its peak 83 ms and peaked 117 ms after pulse onset. UW
pulses are longer than UCLA pulses (67 vs 51 ms), which likely accounts for at least part of the larger UW response.

Notes for authors (not caption text):
- Calibration slopes (raw ME units per % coherence, global pooling): UCLA 1.18, UW 4.93 (`me_calibrated.npz`).
- Trials, not mice, are the unit here: these are properties of the stimulus and filters, not of behaviour.
- The x–t orientation in A was checked numerically (energy ratio rightward/leftward at 30°/s = 6.2); worth a second
  look by eye before submission.
- References in A to verify (outline §6).

---

## Figure 3. Stimulus noise is a fixed bias per trial, and mice discount it

Script: `scripts/paper/fig3_hidden_coherence.py`. Status: not started.
