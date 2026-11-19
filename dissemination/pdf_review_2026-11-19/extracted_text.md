
## PDF page 1
Mouse motion discrimination · pulse experiments
A brief motion pulse is signed
evidence, kept for about a
second
Huk & Shadlen (2005) pulse analyses applied to 10 mice: equal and opposite effects of
congruent and incongruent pulses, retained ~1.2 s, then lost
10 mice · 19,560 responded trials · all coherences, early and middle pulses (late pulses excluded)

## PDF page 2
Approach: the Huk & Shadlen analyses on mouse data
Huk & Shadlen 2005 (monkeys)
This dataset (mice)
Subjects
2 monkeys
10 mice, 19,560 trials
Pulse
100 ms background-texture motion
50–67 ms of 100% coherent dots
Pulse onset
100–392 ms after motion onset
early and middle pulses
RTs analysed
100–1650 ms
0.3–5 s, responded trials
Pulse effect
equivalent coherence shift
same, plus per mouse and by congruency
Time course: trials binned by
RT − pulse onset
; no-pulse trials get a matched virtual onset. Coherence enters as categories,
so lapses at 100% cannot leak into the pulse terms.
Huk AC, Shadlen MN (2005) J Neurosci 25:10420 · scripts/behavior/huk_shadlen_replication.py

## PDF page 3
How to read the plots
Congruent / incongruent
The pulse moves in the same / opposite
direction as the dots. Pulses on 0%
coherence trials are neither and are
left out.
RT − pulse onset
Time from the pulse to the response. No-
pulse trials get a matched virtual onset, so
both are binned the same way.
Effect toward the correct side
Pulse trials vs no-pulse trials at the same
coherence and time. Helps = above 0
(congruent should be), hurts = below
0 (incongruent).
% coherence equivalent
Effect divided by how much 1% coherence
moves the choice (slope at 9–36%).
“Worth 13% coherence” = shifts choices
like 13% more dots.
Pooled vs per mouse
Pooled fits use all trials with one intercept
per mouse; their CIs come from resampling
whole mice. Per-mouse plots: thin lines.
Trials used
Responses within 5 s; early and middle
pulses (late removed); responses in the
first 100 ms after the pulse blocked.
Log-odds = logit of P(choice); effects in log-odds avoid the ceiling on trials the mice already get right

## PDF page 4
Congruent pulses help, incongruent pulses hurt
Plotted.
 Pooled trials. ① P(correct) and ② mean RT vs |coherence|: no pulse (black), congruent (blue), incongruent (red); lines = diffusion fit. ③ Effect per
75 ms bin of RT − pulse onset, in % coherence toward the correct side.
Meaning.
 Congruent pulses raise accuracy, incongruent pulses lower it (9%: 0.63 / 0.58 / 0.51). Joint fit: the pulse is worth 13% coherence (SE 1.0),
positive in 10/10 mice; no separate RT effect (p .76).
Read it as.
 ③ is Huk & Shadlen’s Fig 4: no effect before ~0.3 s, congruent above and incongruent below zero until ~1.2 s, then both near zero. Bins before
0.3 s are noisy.
Pooled, mouse intercepts · huk_shadlen_replication_2026-10-29_pooled_congruency.png

## PDF page 5
The same pattern mouse by mouse
Plotted.
 Congruent (blue) and incongruent (red) effects in % coherence
toward the correct side, per bin of RT − pulse onset. Thin lines = mice;
bold = mean ± SEM. Numbers at the bottom = mice per point (≥ 20 pulse
trials of each type in that bin).
Meaning.
 In individual mice, congruent pulses push choices toward the
correct side and incongruent pulses away from it, mostly 0.3–1.2 s after
the pulse (0.6–0.9 s: incongruent −34% in 6/6 mice).
Read it as.
 A check that the pooled result is not one mouse. Only 3–6
mice per bin, so no bin survives correction; the next analyses pool trials
and resample mice.
Mouse as the unit · huk_shadlen_replication_2026-10-29_mouse_overlay_congruency.png

## PDF page 6
Without a model: change in P(correct)
Plotted.
 P(correct) on pulse trials minus P(correct) on no-pulse trials of the
same mouse, coherence (9–36%) and time bin, in percentage points, against
RT − pulse onset. Thin lines = mice; bold = mean ± SEM.
Meaning.
 Congruent pulses raise accuracy (+14.5 points at 0.3–0.6 s, 8/9
mice); incongruent pulses lower it (−15.3 points at 0.6–0.9 s). After ~1.5 s
neither differs from no-pulse trials.
Read it as.
 The raw data, no fitting. Both curves rise early and dip together at
0.6–0.9 s, which raises the question of whether any pulse also has a non-
directional effect. 5–9 mice per point; nothing survives Holm.
Model-free, mouse as the unit · congruency_choice_effect_2026-10-30.png

## PDF page 7
Congruent and incongruent effects are the same size
Plotted.
 Per mouse × time bin (from 250 ms after the pulse): congruent and incongruent effects, both as log-odds toward the pulse. Left: ROC (thin = bins,
bold = all). Middle: congruent vs incongruent. Right: their difference over time.
Meaning.
 Equal effects give AUC 0.5 and points on the diagonal. All bins: AUC 0.46, permutation p .52; incongruent larger in 27 of 53 points.
Read it as.
 No detectable asymmetry. One bin (0.55–0.85 s) leans incongruent (8/9 mice, Holm p .051): a hint only. With 10 mice, “no difference found” is
not proof of equality.
Paired label-swap permutation, Holm over 6 bins · congruency_roc_panel4_from250ms_2026-10-30.png

## PDF page 8
One directional term explains both pulse types
Plotted.
 One pooled logistic fit, two pulse terms per time
bin. D (purple) pushes choices toward the pulse; S
(green) pushes toward the correct side for any pulse.
Bars: 95% CI from resampling mice. Right: implied
congruent (D + S) and incongruent (−D + S).
Meaning.
 D is large at 0.3–1.2 s (0.43 / 0.66 / 0.43 log-
odds, Holm p .023 each). S survives correction nowhere
(largest −0.23 at 0.6–0.9 s, Holm p .12).
Read it as.
 S ≈ 0 means congruent and incongruent
effects are equal and opposite: the pulse is signed
evidence, whatever the dots show.
Pooled logit, mouse intercepts, coherence × time-bin baseline · 300 mouse refits · pulse_decomposition_2026-10-30.png

## PDF page 9
The pulse is kept for ~1.2 s, then lost
Plotted.
 γ = pulse effect (D) in % coherence. Left: γ vs T,
the mean RT from motion onset per bin; green = 1/T
curve. Right: γ × T per bin of RT − pulse onset; green
band = plateau K over 0.3–1.2 s (95% CI).
Meaning.
 A pulse that is kept is only diluted by later dot
evidence: γ ∝ 1/T, so γ × T stays flat. It is flat at 15.2
%coh·s [12.7, 17.5] up to 1.2 s, then falls to 4.3, 5.4,
−2.8 (Holm p ≤ .027).
Read it as.
 Kept ~1.2 s, then lost. Caveat: late responses
are slow trials, where bounds or disengagement could
also weaken it.
Pooled, all coherences · 300 mouse refits · pulse_dilution_2026-10-30.png

## PDF page 10
Summary
Like added coherence
13% coherence equivalent, no separate RT effect, acts
from ~0.3 s: Huk & Shadlen’s picture
Equal and opposite
Congruent and incongruent pulses: one directional term;
the shared term is not significant
Kept ~1.2 s, then lost
Diluted only, then dropping below dilution: beyond what
Huk & Shadlen could measure
Open
Why the pulse counts ~3× its motion energy (pulse-weight
fits); slow-trial selection vs forgetting after 1.2 s
Report: .agents/reports/2026-10-29-huk-shadlen-replication.md · scripts/behavior/
