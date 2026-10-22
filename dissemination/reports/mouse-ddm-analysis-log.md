# Mouse pulse task: motion energy, kernels and DDM — analysis log

**Last updated:** 2026-10-20. **Branch:** `mouse-motion-energy`.

This log records what was tried, why, what worked and what did not, and how to reproduce each step, so any earlier
state can be recovered. The motion-energy method itself is described in
[`motion-energy-methods.md`](motion-energy-methods.md). Commit hashes refer to this branch.

Data paths below are relative to the processed data directory (`dir_config.data.processed`; `/mnt/data/processed` in
the container, `/gscratch/walkerlab/vaibhav/mouse-pulse-data/processed` on Hyak). Commands run from the repo root with
the project environment (`.venv`) or, on Hyak, inside the Singularity image (`scripts/slurm/fit_mouse_ddm.slurm`).

---

## Contents

1. [Current state at a glance](#1-current-state-at-a-glance)
2. [Motion energy](#2-motion-energy)
3. [Psychophysical kernels and hidden coherence](#3-psychophysical-kernels-and-hidden-coherence)
4. [DDM: inputs, model and likelihood](#4-ddm-inputs-model-and-likelihood)
5. [DDM fit generations](#5-ddm-fit-generations)
6. [Things that did not work, and why](#6-things-that-did-not-work-and-why)
   - [6b. Rig code check](#6b-rig-code-check-plan-step-0-2026-10-20)
7. [Open issues and next steps](#7-open-issues-and-next-steps)
8. [Replication commands](#8-replication-commands)
9. [Appendix: NHP DDM review](#9-appendix-nhp-ddm-review)

---

## 1. Current state at a glance

| Topic | State | Where |
|---|---|---|
| Motion energy (ME) | Recomputed with mouse-tuned causal filters, calibrated per rig to % coherence. **Done.** | `scripts/motion_energy.py`, `scripts/compute_motion_energy_full.py`, `scripts/assemble_motion_energy.py` |
| Psychophysical kernels | Fixed; noise kernels cannot resolve timing (noise is fixed per trial). **Done.** | `notebooks/2.14-psychophysical-kernel-analysis.ipynb` |
| Hidden coherence | Mice weight it about half as much as programmed coherence (k ≈ 0.50, 95% CI 0.15–0.90). **Done.** | 2.14 section 5, `processed/hidden_coherence.csv` |
| DDM pipeline | ME-driven DDM with censoring at 5 s, 0.3 s floor, scheduled-pulse conditions, censored QMLE, fast guesses. **Working.** | `scripts/ddm/`, `src/ddm/` |
| Current fits | 32-model grid with fast guesses, 2,239 / 2,240 fits (missing `PSUIM6_L1U1V1Z1G1_all`). | `ddm/fits_guess/` (commit `ddd497a`) |
| Leading model | Leak + urgency + sv + fast guesses, no sz (`L1U1V1Z0G1`). **Provisional.** | Section 5.4 |
| Warm starts, guess forms | Implemented; 223 + 120 jobs **submitted** (plan steps 1–2). | Section 5.5, `ddm/fits_guess_warm`, `ddm/fits_guess_<form>` |
| Rig code check | Replay matches the rigs. **Done** (plan step 0). | Section 6b |
| Model recovery | Script ready, **not run** (its common model is provisional). | `scripts/ddm/model_recovery.py` |
| Primacy test | **Not started.** | Section 7 |

---

## 2. Motion energy

### 2.1 Original pipeline (before this branch)
Computed in `scripts/compute_motion_energy_full.py` (old settings) and normalized in notebook 2.10. Problems found
(full list in `motion-energy-methods.md`, section 2):
- the filters were built on a 0.1° grid but the stimulus was resampled to 0.2°, doubling the filter size and
  preferred speed (to ~40°/s);
- the temporal window (100 ms) cut off most of the slow temporal filter;
- `F.conv3d` is cross-correlation and the padding was centred, so each output weighted *future* frames most;
- each session was divided by its largest |ME|, making scales differ between sessions and rigs.

### 2.2 What we did and why (commit `213e34f`)
- **Mouse-tuned filters:** σc = 6°, σg = 3°, k = 34 s⁻¹ → preferred 0.08 c/deg, 2.4 Hz, ~30°/s, matching the dot speed
  (Kiani et al. 2008's tuning rule) and close to mouse V1 medians (Andermann et al. 2011: 0.076 cpd, 3.0 Hz, 39.9°/s).
  Literature values were checked against the papers (commit `f299d89`).
- **Causal, separable computation** on a 0.5° grid; frames rendered at native resolution and area-averaged.
- **Per-rig calibration** to equivalent % coherence (slope of mean ME vs coherence; UCLA 1.18, UW 4.93 raw units per %).
  Per-session or per-mouse slopes differ by < 1%, so calibration is per rig.
- **Full 5 s replay** of every trial (beyond the RT) for the DDM; RT-cut copies for the kernel notebooks.

**Worked:** ME is linear in coherence on both rigs, pulses appear with the right sign and ~116 ms filter delay,
recomputation of all 25,508 trials takes ~6 min on two GPUs.

### 2.3 Analysis fixes (commits `1597c2a`, `036c102`)
Notebook 2.11: y-limits assumed the old ±1 normalization; time labels were 10× too small; a time-window average
sliced trials instead of frames.

---

## 3. Psychophysical kernels and hidden coherence

### 3.1 Kernel fixes (commit `e05c056`)
- 2.13 split trials by `outcome` on raw ME pooled over coherences, which mostly measures coherence. **Superseded** by
  2.14.
- Response-aligned kernels blanked sparse time bins *before* right-aligning, so long trials were aligned to the
  blanking cutoff. Fixed by aligning first.
- The residual kernel was attributed to Nienborg & Cumming (2009) / Okazawa et al. (2018); both use 0% coherence
  trials only. Citation removed; a 0% coherence kernel was added for comparison.

### 3.2 Control-trial definition: one wrong turn (commits `e05c056` → `6e7d9b5`)
- **Tried:** excluding 324 UW `pulse_type == 0` trials whose pulse coherence differed from the base coherence, thinking
  they contained a real pulse.
- **Why it was wrong:** preprocessing (notebook 0.1) sets `pulse_type = 0` when the response came before the pulse
  ended; 224 of those trials responded before pulse onset and 100 during it. UW's control condition is a faux pulse at
  the base coherence. `pulse_type == 0` is the correct control definition; restored in `6e7d9b5`.

### 3.3 Hidden coherence (commits `e2d1d1c`, `6e7d9b5`)
- In both rigs' RDK code, non-coherent dots keep their onset direction all trial, so each seed has a fixed net bias.
  SD at 0% coherence: 3.3% (UCLA), 5.9% (UW). It explains most ME noise (r = 0.87 / 0.97) and ME noise stays
  correlated for seconds.
- Mice weight it at about half of programmed coherence: shared ratio k ≈ 0.50 (95% CI 0.15–0.90), positive in 8 of 10
  mice (Wilcoxon p ≈ 0.02). The ME filters weight it like coherence (1.06 ME per 1%), so the discount is behavioural.
- **Robustness (2026-10-20, plan step 7):** the shared ratio k with per-mouse lapse terms is 0.45 (95% CI 0.15–0.85);
  with lapses and all coherences 0.50 (0.10–0.85); restricted to |coherence| ≤ 18% without lapses 0.35 (0.00–0.70).
  The CI excludes 1 in every version: mice discount the noise robustly, at about 0.35–0.50 of programmed coherence.
- **Consequence:** noise-based kernels cannot show *when* evidence is weighted (unlike Kiani et al. 2008's dynamic
  dots). Timing questions must use the pulses and the DDM.

---

## 4. DDM: inputs, model and likelihood

### 4.1 Inputs (`scripts/ddm/build_ddm_inputs.py`, `processed/ddm/ddm_inputs_global.npz`)
- Each trial's 5 s ME split into S (expected from programmed coherence) and N = ME − S. S uses the onset step response
  (control trials) plus a measured pulse response (pulse trials).
- Trials are labelled by **scheduled** pulse condition (preprocessing relabels pulse trials by RT, which would group
  trials by outcome).
- 25,493 responded trials (0.3–5 s) + 4,537 **censored** trials (no response by 5 s: RT > 5 s or none), 15 trials with
  invalid pulse durations dropped.

What did **not** work for the pulse part of S:
- the onset step response: ME responds ~50 ms faster to a change in an ongoing stimulus than at onset;
- deconvolving a mid-trial step response from 3–4-frame pulses: unstable (amplifies noise);
- measuring the pulse response with a constant baseline: early pulses arrive while the onset response is still rising.
  Fixed by subtracting the onset response first (pulse-locked residual 1.3% vs 33% pulse response).

### 4.2 Model (`src/ddm/`, `scripts/ddm/fit_mouse_ddm.py`)
Per 1 ms step: drift = drift_gain · ME(t) + drift_offset, noise variance 1. Optional mechanisms: leak, urgency
(`1 + t·time_constant`, kept > 0 over 5 s), sv, sz, fast guesses (with probability p_guess the response is a guess:
right with probability guess_bias, at 0.3 s + exponential delay with mean guess_tau). Common random numbers for all
noise and guess draws. Fit per mouse by differential evolution (pop 15, ≤ 1000 iterations, **absolute** stopping
tolerance atol = 1) + Nelder-Mead.

### 4.3 Recorded outcomes and how simulations are mapped onto them
| Data rule | Simulation rule | Why |
|---|---|---|
| No response by 5 s (4,537 trials, more at low coherence) | Censored outcome (rt = inf, choice = −1) | Slow decisions are informative; dropping them truncates the RT distribution |
| No response could register before 0.3 s on either rig (UCLA: next lick at 0.3 s; UW: raw times start at window opening, preprocessing adds 0.3 s) | Decisions before 0.3 s are **floored** at 0.3 s | Matches the rigs; nothing before 0.3 s was dropped from the data |

### 4.4 Likelihood (`src/ddm/likelihood_calculator_censored.py`)
Ratcliff quantile likelihood with a censored outcome, per cell of coherence × scheduled pulse condition: a multinomial
over {left, right, no response} plus, per choice, data-quantile RT bins (9). Smoothed probabilities; a cell with no
simulated trials costs 20 per data trial. Selected explicitly: `LIKELIHOOD_PARAMS = {"method": "qmle_censored", ...}`.

---

## 5. DDM fit generations

| Gen | Folder | Commit(s) | Grid | Outcome | Status |
|---|---|---|---|---|---|
| 0 | (`ddm/fits_test`, `fits_test_atol`; deleted 2026-10-20) | `072480a` + local edits | PSUIM5 timing tests | Exposed the empty-cell exploit and premature stopping | Test only, not kept |
| 1 | `ddm/archive/fits0_urgency_lowerbound` | `0c3de87` | L, U, V, Z, free k; urgency ≥ −0.5; UW **truncated** | UW invalid; UCLA valid | Archived |
| 2 | `ddm/archive/fits_no_guess` | `7ec9003`, `40858bd` (+ UCLA CV from gen 1) | L, U, V, Z, free k; urgency ≥ −0.15; floor on both rigs | Valid; error RTs misfit | Archived |
| — | `ddm/archive/fits_uw_truncated` | `0c3de87` / `7ec9003` | UW fits with truncation | Invalid | Archived |
| 3 | `ddm/fits_guess` | `ddd497a` | L, U, V, Z, **G (fast guesses)**; k fixed 1; single ME input | Current | **Active** |
| 3a | `ddm/fits_guess_warm` | `3a97ea6` | Warm-start refits of 223 under-optimized gen-3 fits (plan step 1) | Merged with gen 3 by `compare_models` | Submitted |
| 3b | `ddm/fits_guess_fast_only`, `ddm/fits_guess_guess_lapse` | `3a97ea6` | Leading model L1U1V1Z0G1 with two other guess forms (plan step 2), 5-fold CV + all | Compared with gen 3's single form | Submitted |

### 5.1 Generation 0: local timing tests
- First objective (plain QMLE) skipped cells with no predictions, and the then-used RT window dropped simulated trials,
  so a fit with a tiny bound "predicted nothing" and won (training NLL 497, held-out NLL infinite). → censored QMLE.
- DE's default relative tolerance (1% of the NLL) stopped after ~24 iterations, coarser than model differences;
  absolute tolerance improved fits by 28–39 NLL. → `tol=0, atol=1`.

### 5.2 Generation 1 (`0c3de87`)
- Urgency allowed down to −0.5: the urgency factor reaches 0 at 2 s and flips sign within the 5 s stimulus. 93 UW fits
  used that region. → bound −0.15 (`7ec9003`).
- UW decisions before 0.3 s were **truncated** (dropped), based on a misreading of UW raw RTs (see 6.1). With
  truncation, most UW fits dropped every simulated trial and won on uniform smoothed probabilities (bound a ≈ 0.3–0.45
  in 23–32 of 32 models per UW mouse). → floor rule (`40858bd`).
- UCLA fits never reached either problem and stayed valid (their CV fits were reused in generation 2).

### 5.3 Generation 2 (`fits_no_guess`, 5-fold CV)
Per-mechanism held-out NLL change when switched on (negative helps), from `compare_models --fits_dir ddm/archive/fits_no_guess`:

| Mechanism | Mice helped / hurt (> 2) | Sum | Family protected exceedance |
|---|---|---|---|
| leak | 8 / 1 | −422 | 0.93 |
| urgency | 9 / 0 | −493 | 0.76 |
| sv | 7 / 1 | −543 | 0.61 |
| sz | 8 / 0 | −302 | 0.75 |
| free k | 1 / 3 | +6 | 0.51 |

- Free k not supported → fixed at 1 (raw ME), later removed (`ddd497a`).
- **Fit quality** (notebook 3.0, figure `ddm_fit_quality_common_model.png`, model L1U1V1Z1K0): psychometric and
  no-response functions good, but **error RTs at high coherence much faster in data than model**. Cause: responses
  < 0.6 s are 17% (UCLA) / 20% (UW) of responses and near chance at every coherence (74% / 59% correct even at 100%),
  ~45% of errors at 100% coherence. The DDM cannot produce chance-level fast responses → fast-guess component.

### 5.4 Generation 3 (`fits_guess`, 5-fold CV) — current
From `python -m scripts.ddm.compare_models`:

| Mechanism | Mice helped / hurt (> 2) | Sum | Family protected exceedance |
|---|---|---|---|
| sv | 9 / 0 | −555 | 0.87 |
| leak | 8 / 1 | −273 | 0.74 |
| guess | 7 / 3 | −471 | 0.66 |
| urgency | 8 / 0 | −330 | 0.58 |
| sz | 7 / 0 | −171 | 0.41 |

- Best summed model **L1U1V1Z0G1** (leak + urgency + sv + guesses, no sz). Next: L1U0V1Z1G1 +38, L1U1V1Z1G1 +39.
- Guesses improve the best model by 303–357 held-out NLL over generation 2's best (same folds, likelihood and
  evaluation draws, so directly comparable). The same no-guess model fitted in both generations differs by 13 NLL,
  a rough run-to-run noise floor.
- sz lost support once guesses were added (as expected: its role was mainly fast errors); urgency weakened.
- **Fit quality** (figure `ddm_fit_quality_L1U1V1Z0G1.png`): error RTs now faster than correct at high coherence and
  close to the data for most mice. Remaining misfits: 100% errors still too slow for DBM6 and DBM14; 36% errors faster
  in data than model for several mice; UCLA mice choose left more than predicted at −36% to 0%; PSUIM7 no-response rate
  at negative coherence underpredicted.
- **The "guess" process acts more like a lapse process:** p_guess 0.14–0.47, guess_tau often at its 2 s limit (25
  all-trial fits), i.e. stimulus-independent responses at all RTs. drift_gain at its lower bound in 39 all-trial fits.
- **Optimizer failures:** 1.3% of nested pairs (all trials) have the larger model worse by > 20 NLL, concentrated in
  PSUIM7 and in models with sz added → the comparison may understate sz (and somewhat leak and urgency).

### 5.5 Generation 3 follow-ups: warm starts and guess forms (plan steps 1–2, commit `3a97ea6`)

**Warm starts (step 1).** A larger model fitted with the same noise draws can only match or beat a model it contains,
so a larger model with a worse training NLL marks an optimizer that stopped short.
- `fit()` now accepts *seeds*: parameter vectors placed in differential evolution's initial population (the rest is
  Latin-hypercube sampled as before). `fit_mouse_ddm.py --warm_start_from <folder>` seeds each fit with its own earlier
  fit and every nested model's fit (parameters a nested model lacks take their "off" value). Because the noise draws are
  the same, each seed reproduces its model's NLL exactly, so a warm-started fit cannot end worse than any model it
  contains.
- **Smoke test** (DBM14, L0U0V1Z0G1, all trials, 15 repetitions, one iteration): NLL 2,107.8 → 2,099.39, exactly the
  nested L0U0V0Z0G1 fit's NLL.
- **Which fits:** `scripts/ddm/find_refits.py` lists fits worse than a nested model by more than a threshold:
  629 fits at > 0 NLL, 224 at > 5, 38 at > 20. **Threshold 5 chosen** (224 fits): gaps of 5–20 NLL can shift the
  per-mechanism comparison, smaller gaps hardly matter. The list (`scripts/ddm/jobs/refits_round1.txt`, 223 jobs)
  excludes `PSUIM6_L1U1V1Z1G1_all`, which was still running in the original grid. A second round may be needed: a
  refitted nested model can expose a new gap in a model containing it.
- `compare_models.py --fits_dir ddm/fits_guess ddm/fits_guess_warm` merges the folders, keeping the better fit.

**Guess forms (step 2).** The single guess component (exponential delay up to 2 s) acts as a catch-all for fast
guesses and slow lapses. Two alternatives, selected with `--guess_model`, are fitted for the leading model
L1U1V1Z0G1 on all mice, 5 CV folds + all trials (60 jobs each), warm-started from the single-form fits:
- `fast_only`: guess delay capped at 0.3 s (guess_tau ≤ 0.3);
- `guess_lapse`: the same fast guess plus a lapse (`p_lapse`; random choice with the same bias, RT uniform over
  0.3–5 s). Implemented in `apply_guesses()`; with `p_lapse` = 0 it reproduces the single-component code exactly.
Each writes to `ddm/fits_guess_<form>` by default (sharing a folder would make the skip-if-done rule skip them).

**Results (2026-10-21, commit `2954fad`).**
- *Warm starts worked.* Merged (`fits_guess` + `fits_guess_warm`, 2,240 fits), no nested pair has the larger model
  worse by > 5.9 NLL (was > 20 in 1.3%). `find_refits` on the merged set: 12 fits with gaps of 5–5.9, none > 20. These
  gaps are below the per-mouse Monte Carlo noise (section 5.6), so **no second round**.
- *Leading model unchanged:* L1U1V1Z0G1 has the best summed held-out NLL; L1U1V1Z1G1 and L1U0V1Z1G1 are +16.7 and
  +16.8, within noise. Random-effects BMS over 32 models is uninformative (omnibus risk 0.72); family-level pxp: sv
  0.87, leak 0.75, guess 0.66, urgency 0.60, sz 0.40.
- *Guess forms* (`compare_guess_forms.py`, held-out NLL relative to the single form, summed over mice): fast_only
  −69.9 (better in 9/10 mice), guess_lapse −83.5; no guesses +377. guess_lapse beats fast_only by only 13.6 summed
  (within noise) for one more parameter, and its p_lapse is ≤ 0.015 in 8/10 mice (0.10 DBM12, 0.13 DBM15).
  **fast_only is preferred** (parsimony rule 3): p_guess 0–0.32 (median ≈ 0.2), guess_tau ≤ 0.3 s, i.e. "about 20%
  fast responses at chance", matching the 17–20% of responses < 0.6 s at chance in the data.
- *Lapse check fails as a lapse estimate:* the psychometric asymptote implies lapses of 16–53% (all RTs) or 9–47%
  (RT ≥ 0.6 s) at 100% coherence, but the uniform-RT lapse is ≈ 0 in most mice. High-coherence errors are therefore
  explained inside the decision process (most likely by sv) and by fast guesses, not by uniform-RT lapses. SUSPECTED,
  to verify with the model's accuracy at 100% coherence in notebook 3.0.
- *Flag:* fast_only fits of DBM14 and DBM15 moved to a different regime (drift_gain 0.86 / 0.98, bound 1.9 / 2.0,
  p_guess 0.23 / 0) with better held-out NLL (−9 / −10). Check in the fit-quality plots before final fits.

**Time-varying evidence weight (for plan step 6.5/6.6, commit after `5235f37`).** `gain_decay` multiplies the drift gain
by exp(−gain_decay · t) (t from stimulus onset; > 0 primacy, < 0 recency); bounds −0.5 to 3 /s. Added to both
simulator backends (they agree; 0 reproduces the constant-weight model) and as `fit_mouse_ddm.py --time_varying_gain`.
The primacy analysis plan was locked in `aeb0a22` ([`primacy-analysis-plan.md`](primacy-analysis-plan.md)).

**Negative leak (self-exciting accumulator).** Added as a second primacy mechanism (primacy plan, amendment 1):
`fit_mouse_ddm.py --signed_leak` allows `leak_rate` down to −1/s. Checking the simulator against a float64 step-by-step
reference showed that the GPU backend's FFT closed form for leak loses accuracy when leak < 0 (its weights grow): 1–4%
of trials off by > 1 ms, up to 0.9 s. Positive leak (all fits so far) was exact on both backends. For leak < 0 the GPU
backend now uses a rescaled cumulative sum in double precision; it matches the reference exactly, with and without sz.
Note: urgency is not a primacy/recency mechanism; it scales all accumulated evidence equally.

### 5.6 Monte Carlo noise and mechanism selection (plan step 3.1–3.2, 2026-10-21, commit `2954fad`)

`mc_noise.py` re-scored the original `fits_guess` CV fits of L1U1V1Z0G1 and its neighbours (70 Hyak jobs, ~5.7 GPU-h)
at 10 evaluation seeds × 15 and 50 repetitions. The grid's own score (seed 12345, 15 reps) was reproduced in 350/350
folds. Output: `ddm/mc_noise/`, `mc_noise_summary.csv`, `mc_noise_per_mouse.csv`.
- **Noise of a model difference** (SD across seeds, CV-summed): per mouse, median 6.5–12.8 NLL at 15 repetitions and
  4.1–5.9 at 50 (max 31 and 14); summed over mice, 22–54 at 15 and 13–21 at 50. The old "> 2 NLL" criterion was far
  inside the noise; a single 15-rep score cannot resolve per-mouse differences under ~15–25 NLL.
- **Per mouse**, mean of 10 seeds at 50 reps (SE 0.5–4.4), neighbour minus L1U1V1Z0G1, i.e. the cost of removing (or
  adding sz):

  | change | summed | mice favouring L1U1V1Z0G1 (> 2 SE) | against | mice > 5 NLL |
  |---|---|---|---|---|
  | − sv | +422 | 9 | 1 (DBM13, −6) | 9 |
  | − guess | +443 | 7 | 0 | 7 |
  | − leak | +93 | 4 | 1 | 4 (DBM12, PSUIM5/6/7) |
  | − urgency | +99 | 3 | 2 | 3 (PSUIM5/6/7) |
  | + sz | +10 | 2 | 2 | 1 |

  These use the original fits; the warm refits improved some neighbour folds (e.g. PSUIM5 without urgency +13.8 here,
  +1.6 with the refits at 15 reps), so the leak and urgency counts can only shrink.
- **Under parsimony rule 2** ("improves held-out fit beyond noise in most mice"): sv and guesses pass; sz fails
  (adding it does not help); **leak and urgency fail**: each helps clearly only in the three or four mice with the most
  trials (2,800–7,500) and is undetectable, not shown absent, in the others. Common-model choice pending the authors'
  decision (next-steps plan, step 3).
- **Not a power problem (2026-10-22).** The seven mice other than PSUIM5/6/7, pooled (12,307 trials, more than PSUIM6
  alone), gain +6.8 ± 4.0 from leak and −0.3 ± 4.5 from urgency, against +57.6 and +36.9 in PSUIM6 (7,458 trials).
  By rig: UCLA +86 / +99 (18,220 trials), UW +6 / +0.5 (11,810). The per-trial benefit differs 5–10×: a difference
  between mice (three of four UCLA mice), not missing power. Source: `ddm/mc_noise/mc_noise_per_mouse.csv`.
- **What leak + urgency fit** (`scripts/ddm/diagnose_leak_urgency.py`, control trials only, all-trial fits, 20 reps;
  G statistic per |coherence| × outcome × RT-decile cell). In PSUIM6 and PSUIM7 most of the misfit removed is the
  **rate of censored (> 5 s) trials** (+174, +196); gains and losses over RT bins largely cancel. VERIFIED (in-sample, simulation
  noise not quantified).
- **The censored trials are late responses, not missed trials.** (Corrected 2026-10-22 after V. Thakur's note: the
  5 s cutoff is our censoring choice, the stimulus kept running.) Of the 4,537 censored trials, 60–100% per mouse are
  responses after 5 s (median 7.7 s, 90th percentile 18.6 s; `censored_trials.csv`, column `censored_rt`). Their
  accuracy rises with coherence (UCLA 0.57 / 0.67 / 0.81 / 0.88 at 9 / 18 / 36 / 100%; UW 0.61 / 0.59 / 0.67 / 0.81),
  is 0.63–0.77 per mouse at |coh| ≥ 36%, and barely depends on how late (0.70 at 5–8 s, 0.65 at 15–61 s). VERIFIED.
- **But their share is nearly coherence-independent:** P(censored) is flat from 0 to 36% coherence (PSUIM6 0.27, 0.29,
  0.27, 0.21; PSUIM7 0.10 at all four) and 5–12% at 100% in every mouse checked; both models underpredict it at 100%
  (PSUIM6: data 0.109, strict 0.068, full 0.064). Leak produces a flat rate of long trials by letting the
  accumulator stall. SUSPECTED: in PSUIM5/6/7 leak and urgency stand in for a delayed, variable start of integration
  (late engagement, then a normal coherence-dependent decision), not for leaky integration or urgency. An earlier
  version of this note called these trials disengagement; that was wrong (they are coherence-dependent).
  A delayed-engagement parameter was considered and not pursued (V. Thakur, 2026-10-22).
- **Decision (2026-10-22, V. Thakur): strict**, i.e. L0U0V1Z0G1 + fast_only guesses; L1U1V1Z0G1 + fast_only is the
  secondary baseline for the primacy test (primacy plan, amendment 3). The options considered: *strict* (rule 2 as written): L0U0V1Z0G1 + fast_only guesses,
  leak + urgency model as secondary baseline; *relaxed*: L1U1V1Z0G1 + fast_only, by summed held-out NLL (leak +93,
  urgency +99, about 5 summed noise SDs) but helps 3–4 of 10 mice and slightly hurts 1–2 (≈ −3.5 NLL). Recommended:
  strict. Source for the numbers: `mc_noise --summarize`, `mc_noise_per_mouse.csv`.
- **UCLA vs UW behaviour (data only).** UCLA mice other than PSUIM7 respond slower (median correct RT at
  |coh| ≥ 36%: 1.33–1.55 s vs 0.86–1.36 s in UW), make fewer fast responses (< 0.6 s: 5–11% vs 14–34%) and PSUIM5/6
  miss more trials (22%). PSUIM7 is UW-like in RT. Figure: `dissemination/figures/leak_urgency_diagnosis_20261022.png`.

---

## 6. Things that did not work, and why

### 6.1 Misreadings of the data
- **UW early responses (gen 1):** raw UW `response_time` starts at the response-window opening (0.3 s after onset);
  preprocessing adds 0.3 s (`notebooks/0.0-data-compilation.ipynb`, `min_viewing_time_uw`). Comparing raw times to 0.3 s
  made it look as if UW accepted early responses that were then excluded. They are in the data, at 0.3–0.6 s.
- **Control trials (3.2):** the 324 UW trials were valid controls.

### 6.2 Objective and optimizer pitfalls
- Skipping cells without predictions (plain QMLE, also in the NHP code) → models win by predicting nothing.
- Dropping simulated trials (truncation) + smoothing to uniform → same exploit; now guarded (empty-cell penalty).
- Relative DE tolerance → premature stopping.
- Negative urgency beyond −1/T → decision variable pinned and sign-flipped.

### 6.3 Modelling choices that were dropped
- **Free noise weight k:** improved no mouse's held-out fit in the DDM (1 of 10 at most); fixed at 1, then the S/N split
  was removed from the model (`ddd497a`). The choice-level estimate (k ≈ 0.50) stands on its own.
- **sz** (provisionally): no population support once guesses are in.

---

## 6b. Rig code check (plan step 0, 2026-10-20)

Checked against the task code: UW `NeuRPi` (`protocols/random_dot_motion/rt_pulse`, core task, stimulus manager,
`neurpi/tasks/trial_construct.py`; current `main`) and UCLA `RDK-Task` (`Burst_Experiment.py`, `StimDisplay.py`,
`RandomMotion.py`; public repo, single 2021 commit), plus the per-session UW configs in the raw data.

**Confirmed**
- **UW response timing:** a timer opens the response window at `min_viewing` (0.3 s in all 219 session configs); licks
  before it are never queued; `response_time` is measured from the window opening, so preprocessing's +0.3 s is right.
  The response is the first lick *onset* after the window opens, so a decision made earlier registers at the next
  lick, i.e. at 0.3 s plus part of a lick cycle (UW RTs show no pile-up at 0.3 s, a flat density just after it).
- **UCLA response timing:** the clock starts with the stimulus; after `minViewTime` the loop checks the current
  lick-contact state, so a mouse already in contact registers at 0.3 s (the pile-up at 0.3 s). RT is from stimulus
  onset; nothing added in preprocessing.
- **Floor rule:** right for UCLA; an approximation for UW (true response = next lick onset after 0.3 s).
- **Pulse frames:** UW applies the pulse on the scheduled frame and moves the dots on it (as in the replay). UCLA
  applies `updateBurst` on a display-loop pass without moving or drawing the dots (a one-pass freeze, as in the replay).
  UCLA bursts start after a drawn delay (normal, mean 60 or 240 ms, SD 15 ms) and end 50 ms later by wall clock.
- **UW stimulus settings:** all 219 UW session configs use 1280 x 720, dot radius 17, fill 15, speed 350 px/s,
  lifetime 30 frames, min viewing 0.3 s, as in the replay.
- **UCLA noise directions:** `randint(360)`, as in the replay.

**Resolution (confirmed by V. Thakur, 2026-10-20):** the UW rigs drew non-coherent directions with `randint(360)`
during data collection, as the replay does, and the replay's other settings (UW 10 px/deg and 60 Hz, UCLA display
settings) are correct. The items below were open questions from the code check; none requires a change.

**Open questions from the code check (resolved as above)**
- **UW noise directions:** current NeuRPi draws non-coherent directions from 8 discrete values
  (`choice(randTheta)`); our replay copy (`scripts/uw_rdk.py`) uses `randint(360)` (the other line is commented out in
  each). The two consume the random generator differently, so if the rig used `choice` during data collection, every
  replayed UW stimulus (noise directions, positions, respawns) differs from what the mice saw; the programmed coherence
  and pulses are unaffected. NeuRPi's history starts 2025-05-31, so the code cannot say which ran. A behavioural test
  was inconclusive: on 3,404 UW control trials neither version's hidden coherence predicts choice (weights 0.005 ± 0.007
  and -0.003 ± 0.007), but UW mice are too insensitive for this test to have power. **Needs confirmation.**
- **UW screen scale:** the session config comments `"dot_vel": 350,  # 50 degrees/sec`, i.e. ~7 px/deg, not the 10 px/deg
  assumed. If so, UW dots move at ~50°/s, not 30°/s, and the motion-energy filters (tuned to 30°/s) are mistuned for UW.
- **UCLA frame rate and dot settings:** the display loop moves dots once per pass, capped by `tick(FrameRate)` (default
  150, settable in the interface) with vsync off; radius, speed, lifetime and frame rate are interface settings not
  recorded in the data. The replay assumes 190 passes/s, speed 3 px per pass, radius 14, lifetime 60 passes, stepped at
  60 Hz with speed scaled. The fixed per-trial bias (onset positions and noise directions) is reproduced exactly if
  the dot count matches; frame-by-frame positions are not (lifetime and respawns count loop passes), and the true dot
  speed depends on the loop rate achieved. **Needs the settings used.**
- **UW frame rate:** set by the rig's display preferences (`max_fps`, `vsync`; 60 in the example config), not recorded
  in the session configs. Pulse timing is in frames and converted at 16.67 ms per frame. **Needs confirmation (60 Hz).**
- RT clocks start when the stimulus is commanded, not at the first drawn frame; the display latency is absorbed by the
  non-decision time.

---

## 7. Open issues and next steps

The detailed plan, with the purpose, method, cost and expected benefit of each step, is in
[`mouse-ddm-next-steps.md`](mouse-ddm-next-steps.md).

Status (2026-10-20): step 0 (rig code check) done (section 6b); steps 1 (warm-start refits, 223 jobs) and 2 (guess
forms, 120 jobs) implemented and submitted (section 5.5); `PSUIM6_L1U1V1Z1G1_all` still running.

1. **Round 2 of warm starts** if `find_refits` finds new gaps after merging the refits.
2. **Fix the common model** from the merged comparison (currently L1U1V1Z0G1) and the guess-form comparison; decide
   whether sz and urgency stay; check the fits with drift_gain at its lower bound and the lapse rate against each
   mouse's psychometric lapse.
3. **Model recovery** (`scripts/ddm/model_recovery.py`): set `COMMON` to the chosen model, then run (720 jobs at 6
   generators). Key questions: can sz vs guesses and urgency vs guesses be told apart?
4. **Primacy test:** with the control-only fits of the chosen model, predict pulse trials and compare predicted vs
   observed pulse effects by timing (Okazawa et al. 2018: in RT tasks late pulses matter less even with constant
   weights, so primacy means *less than the model predicts*).
5. **Screen geometry** (methods doc 3.7) and filter-sensitivity analysis (methods doc 5).

---

## 8. Replication commands

To reproduce an earlier state, check out its commit, then run the steps below. Fit scripts skip outputs that already
exist; use a new `--out_dir` (or `--force`).

### 8.1 Motion energy
```bash
python -m scripts.compute_motion_energy_full --gpu 0 --shard 0 --num-shards 2   # and --gpu 1 --shard 1
python -m scripts.assemble_motion_energy                                        # calibration + per-region pickles
```
Outputs: `motion_energy_mouse/` (shards, `me_calibrated.npz`), `motion_energies_normalized/`, `motion_energies_full/`.

### 8.2 Kernels and hidden coherence
Run `notebooks/2.14-psychophysical-kernel-analysis.ipynb` (writes `hidden_coherence.csv` and figures in
`dissemination/figures/`). 2.11 and 2.10 also run on the outputs of 8.1.

### 8.3 DDM inputs
```bash
python -m scripts.ddm.make_censored_trials                                       # censored_trials.csv
python -m scripts.compute_motion_energy_full --gpu 0 --shard 0 --num-shards 2 --trials censored_trials.csv --out-dir motion_energy_mouse_censored   # and shard 1
python -m scripts.ddm.build_ddm_inputs                                           # ddm/ddm_inputs_global.npz
```
The fits only need `ddm/ddm_inputs_global.npz` (78 MB); copy it to the cluster data folder.

### 8.4 Fits on Hyak
```bash
git checkout <commit>                         # e.g. ddd497a for generation 3
cp scripts/slurm/cluster.env.example .env     # set CLUSTER_DATA_PATH and SIF_PATH (the NHP image works)
python3 -m scripts.ddm.fit_mouse_ddm --list   # job_id ranges per split
sbatch --array=0-319 --export=ALL,JOB_OFFSET=1600 --time=16:00:00 scripts/slurm/fit_mouse_ddm.slurm   # all trials
# CV folds: offsets 0, 320, 640, 960, 1280; control only: 1920
```
Generation folders: gen 1 ran with the then-default `ddm/fits` (renamed `fits0`, then archived); gen 2 in `ddm/fits`
(archived as `fits_no_guess`); gen 3 writes to `ddm/fits_guess` by default.

### 8.4a Keeping the NAS copy and Hyak in sync
`processed/` exists twice: the lab NAS (`nas.uwcnc.net:/mnt/Pool-Backup/cnc/vaib_data/mouse-pulse-experiment`, mounted as
`/mnt/data`) and Hyak (`/gscratch/walkerlab/vaibhav/mouse-pulse-data`). Fits are created, moved and deleted on Hyak only,
and copied one way, Hyak → NAS; the only file going the other way is `ddm_inputs_global.npz` after a rebuild. Syncing
without `--delete` after a move on Hyak once left stale folders next to `archive/`.
```bash
# routine update (new fits; never deletes)
rsync -avh --progress --exclude='*.tmp' vthakur@klone.hyak.uw.edu:/gscratch/walkerlab/vaibhav/mouse-pulse-data/processed/ddm/ /mnt/data/processed/ddm/
# after moving or deleting on Hyak: dry run (-n), check the "deleting" lines, then rerun without -n
rsync -avhn --delete --exclude='*.tmp' vthakur@klone.hyak.uw.edu:/gscratch/walkerlab/vaibhav/mouse-pulse-data/processed/ddm/ /mnt/data/processed/ddm/
```
`--exclude='*.tmp'` skips fits still being written (the fit script writes `<name>.tmp`, then renames it). To check that
both sides match, list `<folder> <file count> <hash of file names>` on each side and compare:
`for d in $(find . -type d | sort); do echo "$d $(find $d -maxdepth 1 -type f | wc -l) $(find $d -maxdepth 1 -type f -printf "%f\n" | sort | md5sum | cut -c1-8)"; done`
(`scripts/sync_ddm_data.sh` wraps the same rules for a machine that has both the NAS and `ssh hyak`.)

### 8.4b Warm-start refits and guess forms (generation 3a/3b)
```bash
python -m scripts.ddm.find_refits --threshold 5 --out scripts/ddm/jobs/refits_round1.txt   # list (job ids into the full grid)
env EXTRA_ARGS="--job_file scripts/ddm/jobs/refits_round1.txt --warm_start_from ddm/fits_guess --out_dir ddm/fits_guess_warm" \
    sbatch --array=0-222 --time=16:00:00 scripts/slurm/fit_mouse_ddm.slurm
for form in fast_only guess_lapse; do
  env EXTRA_ARGS="--variants L1U1V1Z0G1 --splits cv0 cv1 cv2 cv3 cv4 all --guess_model $form --warm_start_from ddm/fits_guess" \
      sbatch --array=0-59 --time=16:00:00 scripts/slurm/fit_mouse_ddm.slurm
done
python -m scripts.ddm.find_refits --fits_dir ddm/fits_guess ddm/fits_guess_warm --out scripts/ddm/jobs/refits_round2.txt   # round 2 check: 12 fits at 5-5.9, not run
python -m scripts.ddm.compare_guess_forms --variant L1U1V1Z0G1         # guess forms vs psychometric lapse (section 5.5)
python -m scripts.ddm.diagnose_leak_urgency                            # where leak + urgency help (simulates, ~10 min CPU)
python -m scripts.ddm.diagnose_leak_urgency --data_only                # censored-trial checks only
# Monte Carlo noise (step 3.1)
sbatch --array=0-69 --export=ALL,JOB_OFFSET=0,MODULE=scripts.ddm.mc_noise scripts/slurm/fit_mouse_ddm.slurm
python -m scripts.ddm.mc_noise --summarize
```

### 8.4c Strict common model: guess bias, control-only CV, generator fits (2026-10-22)
Common model L0U0V1Z0G1 with fast-only guesses (section 5.6). All warm-started where an earlier fit of the same split
exists; the control-only CV splits (`ccv0`–`ccv4`, new) have none, so check nested pairs afterwards.
```bash
# (fish: set W "--guess_model fast_only --warm_start_from ddm/fits_guess ddm/fits_guess_warm")
W="--guess_model fast_only --warm_start_from ddm/fits_guess ddm/fits_guess_warm"
# 1. strict model, guess_bias free -> ddm/fits_guess_fast_only (70)
env EXTRA_ARGS="--variants L0U0V1Z0G1 --splits cv0 cv1 cv2 cv3 cv4 all control $W" sbatch --array=0-69 --time=16:00:00 scripts/slurm/fit_mouse_ddm.slurm
# 2. strict model, guess_bias fixed at 0.5 -> ddm/fits_guess_fast_only_FB (70); parsimony rule 3
env EXTRA_ARGS="--variants L0U0V1Z0G1 --splits cv0 cv1 cv2 cv3 cv4 all control $W --fixed_guess_bias" sbatch --array=0-69 --time=16:00:00 scripts/slurm/fit_mouse_ddm.slurm
# 3. secondary baseline, control-only fit (10), and all-trial fits of the recovery generators (30)
env EXTRA_ARGS="--variants L1U1V1Z0G1 --splits control $W" sbatch --array=0-9 --time=16:00:00 scripts/slurm/fit_mouse_ddm.slurm
env EXTRA_ARGS="--variants L0U0V0Z0G1 L1U0V1Z0G1 L0U1V1Z0G1 --splits all $W" sbatch --array=0-29 --time=16:00:00 scripts/slurm/fit_mouse_ddm.slurm
# 4. plan step 3.3: CV within control trials, strict model and its neighbours (300)
env EXTRA_ARGS="--variants L0U0V1Z0G1 L0U0V0Z0G1 L0U0V1Z0G0 L1U0V1Z0G1 L0U1V1Z0G1 L1U1V1Z0G1 --splits ccv0 ccv1 ccv2 ccv3 ccv4 $W" sbatch --array=0-299 --time=16:00:00 scripts/slurm/fit_mouse_ddm.slurm
# afterwards
python -m scripts.ddm.compare_guess_forms --variant L0U0V1Z0G1        # free vs fixed bias (fast_only vs fast_only_FB)
python -m scripts.ddm.compare_models --fits_dir ddm/fits_guess_fast_only --folds ccv0 ccv1 ccv2 ccv3 ccv4   # step 3.3
```

### 8.5 Analysis
```bash
python -m scripts.ddm.compare_models                                  # generation 3
python -m scripts.ddm.compare_models --fits_dir ddm/fits_guess ddm/fits_guess_warm   # generation 3 with warm-start refits
python -m scripts.ddm.compare_models --fits_dir ddm/archive/fits_no_guess   # generation 2
```
Fit-quality plots: `notebooks/3.0-ddm-fit-quality.ipynb` (set `MODEL` and `FITS`).

### 8.6 Model recovery (submitted with 8.4c, 2026-10-22)
Generators and candidates: L0U0V1Z0G1, minus sv, minus guesses, plus leak, plus urgency (fast-only guesses, guess_bias
free); 10 mice × 5 × 5 × 2 replicates = 500 jobs. Generating parameters are the all-trial fits of 8.4c batches 1 and
3b (the no-guess model from `ddm/fits_guess`), so recovery waits for those arrays (`afterany`). A generator fit with a
different guess form is refused, never substituted. If guess_bias is later fixed, rerun with `--fixed_guess_bias` and
`--out_dir ddm/recovery_FB` only if the mechanism verdicts could plausibly change.
```fish
set J1 (sbatch --parsable --array=0-69 ... )      # 8.4c batch 1, captured with --parsable
set J3b (sbatch --parsable --array=0-29 ... )     # 8.4c batch 3b
python -m scripts.ddm.model_recovery --list
for off in 0 250
  sbatch --dependency=afterany:$J1:$J3b --array=0-249 --time=16:00:00 --export=ALL,JOB_OFFSET=$off,MODULE=scripts.ddm.model_recovery scripts/slurm/fit_mouse_ddm.slurm
end
```

---

## 9. Appendix: NHP DDM review

Reviewed `prior-encoding-in-nhp-sc` (branch `vaib`, head `fc6228b`), whose engine this repo's `src/ddm` derives from.

- **The finalized fits used the KL objective, not QMLE.** `ddm.py` always builds the KL calculator; the QMLE settings
  (`rt_nllh_weight`) were silently ignored. Confirmed on all 450 pickles (KL, 9 bins, CAF weight 1.0, chronometric
  weight 2.0); re-scoring reproduces the stored NLLs with KL (~0.15–0.4 per trial; QMLE would be ~2.7–3.1).
- **Model comparison invalid:** AIC/BIC computed on a non-likelihood objective, and penalizing one fit's parameters
  instead of 90 fits'. The "leak + urgency" conclusion is not supported.
- **Other issues:** DE relative tolerance (premature stopping, worse for QMLE's larger NLL), urgency down to −0.5 with
  stimuli up to 8 s, leak bound 0–0.3/s too narrow to matter, QMLE skipping empty cells and cells with < 9 trials
  (most error RTs ignored at session level), `main` behind `vaib` (KL `return 0` bug).
- **Possible reason earlier QMLE fits looked poor:** the 1% stopping rule is ~10× coarser for QMLE than KL, and error
  RTs were mostly excluded from the QMLE objective. Suggested test: refit a few sessions with QMLE after fixing the
  stopping rule and urgency bound, and compare chronometric fits.
