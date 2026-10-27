<!-- np-contract
stage: S1 ; section: spine_response ; agent: np-architect ; version: v1
thesis: "In mice performing a reaction-time random-dot motion task, a bounded accumulator with drift variability and fast guesses predicted held-out control-trial choices and response times better than a tested rapid-forgetting model, in a comparison not yet shown to identify rapid forgetting, whereas brief motion pulses moved choices far more than either control-fitted model predicted, which left the temporal weighting of evidence unresolved."
claims: C001, C003, C004, C005, C006, C007, C008, C009, C010, C011, C012, C013, C014
numbers: N016, N017, N020, N021, N026, N029, N030, N033, N042, N043, N047, N063, N064, N065, N066, N071, N073, N079, N082, N083, N097, N098, N110, N112, N113, N114, N115, N116, N117, N118
sources: stine2020differentiating, hyafil2023temporal, brunton2013rats
-->
# Response to the spine challenge (S1, one revision round)

Spine v2 is at `np/spine.md`; claims updated in `np/ledger/claims.csv` (all still `proposed`; new C013, C014).
No analysis was run or assumed. Every NEEDS-ANALYSIS item states the exact analysis, where it runs, and how the
spine changes under each outcome. Proposed decision bounds must be fixed by the authors **before** an analysis runs.

Labels: **ADDRESSED-TEXT** (fixed in spine v2 wording), **NEEDS-ANALYSIS**, **DISAGREE** (with evidence).
Several points have parts with different labels.

Compute legend: *local* = rescoring of saved fits or behavioral data on the workstation (the amendment 7
noise rescoring ran locally, log 5.13); *cluster* = new model fits (Hyak). Fit counts below are design counts, not
runtime estimates.

---

## Summary table
| Point | Label | Accepted / contested | Tier |
|---|---|---|---|
| F1.1 / F1a no comparison recovery for E | ADDRESSED-TEXT + NEEDS-ANALYSIS (cluster) | Accepted | 1 (decides thesis) |
| F1.2 near-constant control input | ADDRESSED-TEXT + NEEDS-ANALYSIS F1c (cluster) | Accepted | 2 |
| F1.3 / F1d within-trial tests | ADDRESSED-TEXT; DISAGREE in part | Accepted (reporting); contested (reading) | — |
| F1b score decomposition | NEEDS-ANALYSIS (local) | Accepted | 1 |
| M1 both models fail on pulses | ADDRESSED-TEXT; optional NEEDS-ANALYSIS (local) | Accepted | 3 |
| M2 amendment 7 front end | ADDRESSED-TEXT + NEEDS-ANALYSIS (cluster); DISAGREE in part | Accepted | 2 |
| M3 free-leak identifiability | ADDRESSED-TEXT + NEEDS-ANALYSIS (cluster; one local check) | Accepted | 3 |
| M4 C006 contradicts ledger | ADDRESSED-TEXT; optional NEEDS-ANALYSIS | Accepted | 3 |
| M5 fast-guess / lapse account | ADDRESSED-TEXT + NEEDS-ANALYSIS (local and cluster) | Accepted | 2 |
| M6 point 3 is an absence | ADDRESSED-TEXT; DISAGREE in part; optional NEEDS-ANALYSIS | Partly accepted | 3 |
| M7 38 mislabeled trials | ADDRESSED-TEXT + NEEDS-ANALYSIS (local bound, cluster refit) | Accepted | 2 |
| P1-1 counts at MC noise edge | ADDRESSED-TEXT + NEEDS-ANALYSIS | Accepted | 2 |
| P1-2 sv as engagement/history | ADDRESSED-TEXT; optional NEEDS-ANALYSIS | Accepted | 3 |
| P1-3 sz untested | ADDRESSED-TEXT; optional NEEDS-ANALYSIS (cluster) | Accepted | 3 |
| P1-4 Figure 2 relevance | ADDRESSED-TEXT (conditional on F1c) | Accepted | — |
| P1-5 filter as hidden DoF | ADDRESSED-TEXT; optional NEEDS-ANALYSIS (cluster) | Accepted | 3 |
| P1-6 novelty | ADDRESSED-TEXT (S2 to verify) | Accepted | — |
| P1-7 H1/H2 table | ADDRESSED-TEXT | Accepted | — |
| P1-8 pulses as "evidence" | ADDRESSED-TEXT | Accepted | — |

---

## FATAL

### F1. Comparison identifiability and within-trial tests

**F1.1 / F1a: no recovery of the control comparison with a rapid-forgetting (E) generator.**
*Accepted; factually right (orchestrator verified).* Recovery (N083) used five nested accumulator generators only.

- **ADDRESSED-TEXT.** THESIS, C001 and C004 now say the comparison is "not yet shown to identify rapid forgetting" and
  that recovery did not include a rapid-forgetting generator. The Key control has an explicit "Missing control" line.
  H5 (first-passage-time family / censoring / guess allocation) is added to the hypothesis table as undecided. Scope
  forbids "identify the mouse's algorithm" and "mice accumulate". C004 note records E's bound separation 0.52–1.02
  and 4/60 fits at leak 20/s (log 5.8; ledger ids missing, see change requests).
- **NEEDS-ANALYSIS (cluster).** For each of the 10 mice, simulate control-trial datasets from (a) E's control-only
  fitted parameters and (b) the accumulator's control-only fitted parameters, using that mouse's actual control-trial
  motion-energy inputs and trial counts, 2 replicates each. Fit both candidates (L0U0V1Z0G1 and the leak 20–200/s
  model, guess bias free, fast-only guesses) with the same five-fold control-only CV, 15 repetitions, no warm starts,
  and score with the same censored QMLE settings including the empty-prediction penalty (N079), so the procedure
  matches N016/N110 exactly. Design: 10 mice × 2 generators × 2 replicates × 2 candidates × 5 folds = 400 fits.
  Report the confusion matrix (E→E, E→I, E→neither; I→I, I→E, I→neither) at the >10 rule; preferably also rescore
  at 10 seeds (N082). The E-generated datasets from the fluctuation-kernel power work may be reusable as generator
  data only if they were simulated from the same E control fits and trial set; the v2 sets exclude the 38 mislabeled
  trials (N117 note), so they differ slightly from the N016 input. Check before reuse; do not assume.
- **Key quantity:** how often E-generated data are scored as favoring the accumulator by >10. Only that rate tells
  whether the observed 6/10 accumulator wins carry information against E.
- **Spine under each outcome** (proposed bounds; authors fix before running):
  - E→I in ≤ 2/20 mouse-replicates and I→E rare, with F1b spread over choice and RT terms: replace the
    identifiability clause with "in a comparison that recovered both generating models in simulation"; H1/H2 rows
    become decidable by Figure 3; F1 drops to MAJOR as the challenge itself proposes.
  - E→neither common but E→I rare: same as above, plus a sentence that the comparison has low sensitivity to E in
    mice with fewer trials (the four non-distinguishing mice are uninformative).
  - E→I in 3–4/20: keep the current THESIS; report the confusion matrix in Figure 3D.
  - E→I in ≥ 5/20: **fallback THESIS** (below); C004 becomes descriptive ("described ... better"); Figure 3 claim
    becomes "the control comparison ranks the models but cannot identify rapid forgetting"; title must drop any
    accumulation assertion.

**Fallback THESIS** (E-recovery shows the comparison cannot identify E):
"In mice performing a reaction-time random-dot motion task, a bounded accumulator with drift variability and fast
guesses described control-trial choices and response times better than a tested rapid-forgetting model, but neither
this comparison, which could not identify rapid forgetting in simulation, nor brief motion pulses, which moved choices
far more than either model predicted, determined how mice use evidence over time."

**F1.2: control input is near-constant, so the comparison may only compare RT-distribution families.**
*Accepted.* The stimulus-aligned fluctuation sensitivity is small (0.1–0.4 % coh; amendment 8 report caveat) and the
hidden-coherence analysis is excluded.
- **ADDRESSED-TEXT.** Scope now forbids describing the control comparison as a test of how momentary evidence is used
  over time; H5 states this alternative and its predictions; the Opening keeps stine2020differentiating's point that
  choice and RT curves alone cannot separate the strategies.
- **NEEDS-ANALYSIS F1c (cluster).** Refit both models with drift driven by nominal signed coherence (constant over the
  trial, same onset and filter delay handling as far as the code allows) instead of motion energy, same control-only
  five-fold CV and scoring. Design: 10 mice × 2 models × 5 folds = 100 fits. Report (i) E − I under nominal input vs
  under motion energy, per mouse; (ii) accumulator with motion energy vs with nominal input (answers P1-4).
  - E − I similar under nominal input: the comparison concerns first-passage-time families given coherence. THESIS
    takes the "response-time distributions were better described" variant (spine conditional table, row 3); C004
    adds "independent of within-trial fluctuations"; Figure 2 leaves the main text.
  - E − I shrinks markedly under nominal input, and motion energy beats nominal input held out: within-trial
    fluctuations contribute to the ranking; Figure 2 stays main; C003 gains a behavioral consequence.

**F1.3 / F1d: the within-trial tests do not support the integrator and are absent from the Resolution.**
- **ADDRESSED-TEXT (accepted).** Both prespecified results are now in the Resolution and placed beside Figure 3:
  - Response-aligned kernel (amendment 8): new claim C013, "neither model fits", Figure 3—figure supplement 1. This
    conflicts with D001 item 4 ("add it if it pans out"); flagged for an author decision at G1. My recommendation is to
    report it, because omitting a prespecified negative from an accumulation-first paper is selective reporting.
  - Pulse strategy statistic (N029, z = 2.97, 8/10 same sign toward E): C011 moved to the Figure 3 Results text with
    its 1/20 and 0/20 sensitivity (N024, N025, N097).
- **DISAGREE in part (reading, not reporting).**
  - The kernel test rejected *both* models, and E more clearly: S_I = 11.44 vs its q95 11.22, S_E = 14.74 vs 13.21
    (amendment 8 report). It is evidence that neither pipeline captures fluctuation use, not evidence for E. Its
    references come from 20 datasets each and in-sample predictions, so "adequately powered" overstates it for the
    integrator side (I-generated data: 14/20 classified accumulation, 5/20 not distinguished, 1/20 neither). The spine
    reports it as "neither model fits" with no lean either way, and forbids "near-support".
  - The pulse statistic leaned toward E because E predicted a slightly larger pulse effect (~0.04 vs ~0.03 logit)
    against an observed ~0.3 (log 5.10); the larger prediction is less wrong, so E gains more likelihood. That says the
    pulse sensitivity was under-predicted, not that mice forget rapidly (orchestrator verified). C011 states this.

**F1b: decompose the E − I difference.** *Accepted.*
- **NEEDS-ANALYSIS (local).** Re-score the saved held-out fold fits (`ddm/fits_guess_fast_only/*_ccv*.pkl` and
  `ddm/fits_guess_fast_only_leak20-200/*_ccv*.pkl`) with the likelihood calculator returning per-term contributions:
  choice, conditional RT, censoring P(RT > 5 s), and empty-prediction penalty (N079), per mouse and coherence. Needs a
  small change to `src/ddm/likelihood_calculator_censored.py` to expose terms (no refit). 15 repetitions × ideally 10
  seeds. Also report the per-trial-normalized difference (P1-1).
  - Advantage spread over choice and RT terms, penalty negligible: C004 unchanged (or strengthened per F1a).
  - Advantage mainly in the censoring term: C004 rewritten as "better predicted the rate of responses after 5 s and
    the response-time distribution"; THESIS row 3 variant; Discussion links this to the suspected delayed-engagement
    pattern (log 5.6), which is neither model's mechanism.
  - Advantage mainly in the empty-prediction penalty: the ranking is a scoring artifact of E's tiny bounds; C004 is
    withdrawn as strategy evidence and the fallback THESIS applies regardless of F1a.

---

## P0 / MAJOR

### M1. Both models fail out of sample on pulses; point 2 depends on a misspecified model.
*Accepted.*
- **ADDRESSED-TEXT.** The Resolution says the comparison "ranks two models that both misfit parts of the data"; C012
  now says the ranking does not identify the algorithm and that neither model predicts pulse responses; Discussion
  promise D4 added (error RTs faster than predicted at 36–100%, P(RT > 5 s) underpredicted at 100% in three mice,
  pulse excess). The predicted-vs-observed pulse effect is now main Figure 6A (C010 promoted), not a supplement.
  Placing it next to Figure 3 instead was considered; it stays in Figure 6 so each figure keeps one claim, and the
  Figure 3 text cross-references it.
- **Optional NEEDS-ANALYSIS (local, simulation from saved fits).** Extend the existing pulse likelihood decomposition
  (pulse diagnostics, N063–N066; done only for PSUIM6/PSUIM7) to all mice. Outcome only changes the explanatory text
  of C010 (which terms fail); the spine is unchanged either way.

### M2. The selected compressive front end (amendment 7) is missing.
*Accepted.*
- **ADDRESSED-TEXT.** Action step 2, Key control (i), C004 and C006 now say every comparison used the linear front end.
  New claim C014 reports amendment 7 (summed −62.7 against a two-SD margin of 28.9, mainly PSUIM6 and PSUIM7) as an
  exploratory comparison stopped on 2026-10-25 and not propagated; Figure 4—figure supplement 1; glossary terms added.
  Scope forbids claiming robustness to the front end.
- **DISAGREE in part.** "The input assumption was rejected on control trials" overstates it: the improvement passed
  the summed rule but came from two mice; γ ≈ 1.0 in five mice, and every mouse other than PSUIM6, PSUIM7 and DBM14
  was within ±3 (log 5.13). The amendment was stopped by the author and is exploratory. It is a real gap, worded as
  "not propagated", not as "the selected model".
- **NEEDS-ANALYSIS (cluster).** Refit E with the power-law front end, control-only five-fold CV (10 × 5 = 50 fits);
  the accumulator F1 CV fits already exist in `ddm/fits_guess_fast_only_fe-power`. Refit the free-leak model with F1
  on all control trials (10 fits). Score as N016/N110.
  - Ranking and counts hold: C004 adds "with either front end"; the scope line on front-end robustness is removed.
  - Ranking weakens or flips: C004 is reported per front end; THESIS takes the hedged or fallback variant depending
    on size; M1 note that compression shrinks the predicted pulse effect enters Discussion.

### M3. Free-leak time constant lacks identifiability; 2–20/s never compared under CV.
*Accepted.*
- **ADDRESSED-TEXT.** C005 now says in-sample, descriptive, and "cannot exclude leak of a few per second", citing
  leak recovery hits (0.5/0/0.5/1.0 at 4.1/0.8/0.6/0.4 per s; 35% overall; log 5.8). Key control (iii) relabeled as
  an optimizer check. The time constant is no longer in the THESIS. H2 prediction rewritten (P1-7). Scope forbids
  using the fit to exclude time constants of a few hundred ms. C007 now includes the leak hit rate.
- **NEEDS-ANALYSIS (cluster), M3a.** Held-out profile at fixed leak 1, 2, 5, 10, 50/s (0/s exists as the accumulator
  CV fits; E covers 20–200/s), control-only five-fold CV: 5 × 10 × 5 = 250 fits.
  - Profile minimum at 0–2/s with ≥ 5/s worse beyond noise in most mice: C005 becomes a cross-validated statement
    ("held-out prediction worsened for leak of 5/s and above").
  - Flat to ~5–10/s: C005 states the range the data cannot distinguish; Discussion notes that moderate leaky
    integration (τ 0.1–0.5 s) remains open, against hyafil2023temporal and brunton2013rats.
- **NEEDS-ANALYSIS (cluster), M3b.** Parameter recovery of the free-leak model at generating leak 1, 2, 5, 10, 20/s per
  mouse, 2 replicates, control trials: 100 fits. Output fixes the resolution wording in C005.
- **NEEDS-ANALYSIS (local), M3c.** Compare DBM15's all-trial L1 generator fit (leak 4.1/s) with its control-only
  free-leak fit from the saved pickles (trial set, other parameters, likelihood surface). The record already shows
  all-trial leak/urgency gains partly came from pulse trials (log 5.6 step 3.3), which is a candidate explanation but
  is not verified for DBM15. Outcome changes only the Methods note.

### M4. C006 contradicts the ledger.
*Accepted; orchestrator verified.* Negative = better, so leak (−21.3, N113) and leak + urgency (−33.3) improved the
summed held-out score, within noise.
- **ADDRESSED-TEXT.** C006 now reads "improved the summed held-out score only within Monte Carlo noise ... not needed
  under the parsimony rule"; urgency alone +25.8 (N114) worsened it; beyond 10 units only in PSUIM6. Note that the
  summed SD 22–54 was measured on other comparisons (log 5.6), and that CV fits had no warm starts, which disfavors
  larger models. Scope bans "did not improve". The −33.3 has no ledger id yet (change request).
- **Optional NEEDS-ANALYSIS.** Rescore the saved ccv fits at 10 seeds × 50 repetitions (GPU; ran on the cluster
  before, log 5.6), and warm-started CV refits (cluster, 300 fits for the component set).
  - Leak improvement stays within 2 SD: wording unchanged.
  - Leak improvement exceeds 2 SD summed but stays confined to one or two mice: C006 becomes "leak improved the summed
    score, driven by PSUIM6, but was not needed in most mice"; THESIS unchanged (it does not mention leak).

### M5. Fast guesses (median 21%) may decide both the comparison and the pulse effect.
*Accepted as an open alternative.*
- **ADDRESSED-TEXT.** Glossary defines the fast-guess component as stimulus-independent *by construction*; H5 lists
  "changes when fast guesses are removed" as a prediction; Discussion D4 carries the bias-like reading of the pulse
  gain tradeoff (N063–N066) as an alternative, without stage attribution.
- **NEEDS-ANALYSIS (local), M5a.** Conditional accuracy functions: accuracy by RT bin and coherence, observed vs both
  models simulated from the saved control fits. If responses < 0.6 s are above chance and rise with coherence, the
  guess component is misspecified; C006 adds that caveat and H5 gains weight.
- **NEEDS-ANALYSIS (cluster), M5b.** E vs I with p_guess = 0: the accumulator no-guess CV fits exist (L0U0V1Z0G0 ccv);
  E without guesses needs 50 fits. A guess component restricted below a fixed latency needs a code change and 100 fits.
  - Ranking holds without guesses: C004 adds "not dependent on the fast-guess mixture".
  - Ranking vanishes or flips: C004 conditioned on the guess component; THESIS takes the hedged variant. Note that
    both no-guess models misfit badly (removing guesses costs +858, N015), so this is diagnostic only.
- **NEEDS-ANALYSIS (local), M5c.** Directional contrast excluding responses within 300 ms of pulse onset, plus pulse
  effect on RT, with `scripts/pulse_followup/behaviour.py` masks. Conditioning on response time is post-outcome
  selection, so it is a sensitivity analysis only.
  - Contrast persists: C008 note records it; the reflexive-response account weakens.
  - Contrast concentrated in fast responses: C008 and C010 add that the pulse effect sits in early responses;
    Discussion gives the transient/reflexive account more weight.

### M6. Point 3 is an absence; its positive content is buried.
- **ADDRESSED-TEXT (accepted).** Point 3 is reframed as a reported negative with its reason in front: C010 (pulse
  excess about tenfold, present at 0% coherence, mouse-varying gains, choice/RT gain conflict in two mice) is now main
  Figure 6A and in the THESIS ("moved choices far more than either control-fitted model predicted"). C009 notes that
  the low expected sensitivity was identified before pulse outcomes were read (log 5.7 states no pulse outcome was
  read). Discussion D5 stays qualitative unless a design simulation is run.
- **DISAGREE in part.**
  - "Derived after data collection" is true but incomplete: it was derived before unblinding, and the plan's response
    (gate 1 first, option 2, log 5.7) was chosen then. That is a documented prespecified path, not a lab-notebook
    outcome, and the spine says so.
  - Route (i), making the pulse excess a headline discovery, is not adopted: it is exploratory, post hoc, the gain
    revision failed to absorb it, and the UCLA replay likely underestimates pulse energy by ~25–35% (log 5.10, suspected, not measured), so its
    magnitude partly depends on the input pipeline. Per orchestrator instruction it is a reported negative, not a
    discovery. Route (ii) (drop temporal weighting from title and abstract) remains an option at G1; it is listed as
    a framing alternative in the return summary.
- **Optional NEEDS-ANALYSIS (cluster).** Forward design simulation under the gain-revised model: pulse strength,
  duration and trial count for 80% detection of 20% decay. If run, D5 gives numbers; if not, D5 names only the
  quantities that would need calibrating before data collection.

### M7. 38 genuine pulse trials remain in the control fits.
*Accepted.*
- **ADDRESSED-TEXT.** Key control (ii) now reads "control trials as labeled in the analysis input ... except that 38
  genuine pulse trials, all without a response by 5 s and mislabeled as controls, remain in these fits (Methods)";
  glossary "control trial" notes it; C004 note; Methods promise added. They can affect only the censoring term.
- **NEEDS-ANALYSIS (local bound).** Re-evaluate the saved held-out fold fits with those 38 trials removed from the test
  sets (no refit). Bounds their effect on N016/N110/N115/N116/N113/N114 through scoring.
- **NEEDS-ANALYSIS (cluster refit).** Refit I and E ccv (100 fits) and the component variants (200 more) on corrected
  labels. Changes in counts or sums: reported numbers are replaced by the corrected ones and the key-control caveat is
  removed; a changed ranking would move the THESIS to the hedged variant.

---

## P1 / MINOR

- **P1-1 (accepted).** ADDRESSED-TEXT: glossary and C004 call the 10-unit threshold "roughly one per-mouse Monte Carlo
  SD" at 15 reps (log 5.6; not calibrated for N016, N082). NEEDS-ANALYSIS: rescore N016/N110 and N115/N116 at
  10 seeds × 50 reps (GPU; cluster as before); per-trial-normalized differences (local, from per-mouse deltas and
  trial counts). If counts fall (e.g. 6/10 to fewer), C004 and the Resolution report the rescored counts; the THESIS
  wording ("predicted ... better") holds unless the summed difference falls within noise.
- **P1-2 (accepted).** ADDRESSED-TEXT: sv defined as "across-trial variability not explained by the stimulus"; scope
  bars a mechanism reading. Optional NEEDS-ANALYSIS (cluster): previous choice/outcome in drift offset or starting
  point; if sv need shrinks, C006 adds that sv partly absorbs history.
- **P1-3 (accepted).** ADDRESSED-TEXT: C006 note and scope say sz was tested only in an earlier generation (N118:
  all-trial CV, L1U1 base, split 2/2). Optional NEEDS-ANALYSIS (cluster): L0U0V1Z1G1 control CV, 50 fits. If sz is
  needed in most mice, C006 adds sz and Figure 4 changes; fast errors would then be partly explained.
- **P1-4 (accepted).** ADDRESSED-TEXT: Figure 2's main-text status is conditional on F1c; C003 note says no analysis
  yet shows behavior uses the fluctuations.
- **P1-5 (accepted).** ADDRESSED-TEXT: rapid-forgetting model defined as leak on *filtered* motion energy (N073,
  temporal support 0.55 s); Methods promise to state how filter parameters were chosen ([MISSING: provenance; ask
  authors whether behavior informed them]); UCLA pulse-energy replay bias kept as an input caveat, rig as covariate.
  Optional NEEDS-ANALYSIS (cluster): recompute motion energy with a shorter temporal filter and rerun E vs I (100 fits).
- **P1-6 (accepted).** ADDRESSED-TEXT: Opening states the narrow contribution and the rat precedent. Odoemene et al.
  2018 and Pinto et al. 2018 are not cited until S2 verifies them; S2 should search for mouse RDK reaction-time DDM work.
- **P1-7 (accepted).** ADDRESSED-TEXT: H1 and H2 rows now conditional on comparison recovery; H2 no longer relies on the
  free-leak fit.
- **P1-8 (accepted).** ADDRESSED-TEXT: glossary "motion pulse" (not "evidence pulse"); scope bars calling pulses
  evidence. The THESIS says "brief motion pulses moved choices" and keeps "evidence" only for "temporal weighting of
  evidence", the question the pulses failed to answer.

---

## Suggested analysis order
1. Local, cheap, high value: F1b decomposition; M7 local bound; M5a; M5c; M3c; P1-1 per-trial normalization.
2. Cluster, decides the THESIS: F1a (400 fits). Fix the decision bounds first.
3. Cluster, robustness of C004: F1c (100), M5b (50–150), M2 (60), M7 refit (300), P1-1 rescoring (GPU).
4. Optional: M3a/b (350), M4 rescoring, P1-3 (50), P1-5 (100), P1-2, M6 design simulation.

## Change requests
- **Number ledger:** add ids for: leak + urgency −33.3 (log 5.6 step 3.3); E bound separation 0.52–1.02 and 4/60 at
  leak 20/s (log 5.8); leak recovery hit rate 35% and per-mouse hits (log 5.8); per-mouse MC SD 6.5–12.8 and summed
  22–54 at 15 reps (log 5.6); original frozen predicted pulse effects, integrator 0.028/0.029/0.027 and E (~0.04)
  (`primacy_predicted_pulse_effects_17511ca.csv`); 0% coherence observed 0.574 vs predicted 0.508 (log 5.10);
  amendment 7 −62.7, 2 SD 28.9, per-mouse PSUIM6 −37.3 and PSUIM7 −23.0, γ 0.62–0.77 (log 5.13); amendment 8 S_I,
  S_E, q95 values and operating characteristics (report 2026-10-26). C004, C006, C007, C010, C013, C014 carry
  `[MISSING]` until then.
- **decisions.md / G1:** C013 reporting conflicts with D001 item 4; needs an author decision.
- **config.md:** working title asserts accumulation; replace at G1 (THESIS no longer supports it).
