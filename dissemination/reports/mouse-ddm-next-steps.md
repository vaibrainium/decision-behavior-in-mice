# Mouse pulse task: plan for the next DDM steps

**Written:** 2026-10-20; **revised** the same day after a critical review (changes summarized at the end).
**Branch:** `mouse-motion-energy`. Background and everything done so far:
[`mouse-ddm-analysis-log.md`](mouse-ddm-analysis-log.md).

## Where we are

The DDM is driven by each trial's own motion energy, handles the 5 s deadline (censoring) and the 0.3 s minimum
viewing time (floor), and includes a fast-guess component. The current 32-model grid (`ddm/fits_guess`, 2,239 of 2,240
fits, 5-fold cross-validation) favours **leak + urgency + sv + guesses, without sz** (`L1U1V1Z0G1`), and that model
fits psychometric, chronometric and no-response functions much better than any model without guesses.

Things that stop us from treating that as the answer yet:
1. Some larger models were under-optimized, which biases the comparison against extra mechanisms (mostly sz).
2. The "guess" component behaves like a general lapse process (rate 14–47%, delays up to its 2 s limit), which makes
   it hard to interpret and may absorb what leak, urgency or the drift gain should explain.
3. Model-comparison differences of a few NLL per mouse are within the Monte Carlo noise of a 15-repetition likelihood;
   we have no measured noise threshold yet.
4. We have not checked that the mechanisms can be told apart at these trial counts (model recovery).
5. The scientific question, whether late pulses matter less than a constant-weight accumulator predicts (primacy), has
   not been tested, and as first planned the test was exposed to the rig confound (late pulses only on UW), to the
   baseline model's own temporal weighting (leak, urgency), and to model misfit on pulse trials.

Each step says what it is for, how, what it costs, and what we decide from it.

## Parsimony rules (agreed 2026-10-20)

To keep the model from growing with each question:
1. **Primacy mechanisms are tests, not model parts.** Gain decay and negative leak are each added one at a time (one
   extra parameter) to the common model to answer one question. The reported model stays the common model unless an
   extension wins clearly (rule 2).
2. **Complexity budget.** A mechanism stays in the common model only if it improves held-out fit beyond the Monte Carlo
   noise threshold in most mice, is recoverable in model recovery, and has a clear interpretation. Failing any one
   removes it, whatever the summed NLL says.
3. **Prefer the simpler form.** Among guess/lapse forms that fit about equally (within the noise threshold), take the one
   with fewer parameters; fix guess_bias at 0.5 unless a free bias clearly improves held-out fit.
4. **No more factorial grids.** The 32-model grid answered which mechanisms matter; after step 3 every further question
   is a single targeted comparison with the common model.
5. **Model-free check.** Each model-based conclusion that matters (primacy above all) is paired with a model-free
   analysis of the same data; agreement means the conclusion does not hinge on model details.

Expected size of the final model: about 8–10 parameters (5 core + leak + urgency + sv + a 2–3-parameter guess
component).

---

## Step 0. Confirm rig behaviour (quick, no compute)

**Why:** two simulation rules were inferred from the data, not from the task code: (i) a decision before 0.3 s
registers at 0.3 s on both rigs (UCLA RTs pile up at 0.3 s; UW raw times start at the response-window opening), and
(ii) the UCLA replay holds the dots still on the frames where a pulse starts and ends. Both affect simulated RTs and
pulse inputs directly.

**How:** check the rig task code, or ask whoever ran the rigs. If either rule is wrong, fix it before step 1.

**Status: done (2026-10-20).** Findings in the analysis log, section 6b. Both rules hold: the floor is exact for
UCLA and an approximation for UW (there the response is the next lick onset after 0.3 s); the UCLA pulse-frame freeze
matches the rig. The UW rigs used `randint(360)` noise directions, as the replay does, and the replay's other settings
are correct (confirmed by V. Thakur), so no replay or input needs regenerating.

## Step 1. Warm-start refits of under-optimized fits

**Why:** in 1.3% of nested pairs (all-trial fits) a larger model fits worse than a model it contains by > 20 NLL, which
is impossible at the optimum. These failures are concentrated in PSUIM7 and in models with sz added. Left alone, they
make sz (and to a lesser degree leak and urgency) look less useful than they are.

**How:** add an option to `fit_mouse_ddm.py` to seed differential evolution with the best parameters of each nested
model (the same model with one mechanism switched off, plus the extra parameter at its "off" value). A larger model
then starts at least as good as every model it contains. Refit only the failing fits (about 50, across splits) and the
missing `PSUIM6_L1U1V1Z1G1_all`, into a new folder; rerun `compare_models.py`.

**Cost:** ~50 Hyak jobs, mostly the big UCLA mice (1–5 h each).

**Status (2026-10-20): implemented and submitted** (commit `3a97ea6`; analysis log section 5.5). Threshold lowered to
5 NLL after counting (629 fits at > 0, 224 at > 5, 38 at > 20): 223 jobs (`scripts/ddm/jobs/refits_round1.txt`) into
`ddm/fits_guess_warm`. Smoke test: the warm-started fit reproduced the best nested model's NLL exactly on its first
iteration. Next: merge, check for a second round with `find_refits`, rerun `compare_models`.

**Decision:** whether sz stays out, and how strong the case for urgency is once guesses are present.

**Result (2026-10-21): done.** Merged, no nested pair is off by more than 5.9 NLL (below the Monte Carlo noise), so no
second round. sz stays out; urgency and leak are decided in step 3 (analysis log, sections 5.5–5.6).

## Step 2. Make the guess component interpretable

**Why:** one component currently covers both fast anticipatory responses (< 0.6 s, near chance) and slow
stimulus-independent responses (delays up to 2 s). p_guess up to 0.47 is not plausible for trained mice, and a broad
lapse process can take over variance that belongs to the decision process (drift gain at its lower bound in 39
all-trial fits).

**How:** compare, by cross-validation on the leading model only:
- (a) current single guess component;
- (b) a fast guess with a constrained delay (e.g. guess_tau ≤ 0.3 s) plus a separate lapse component with a uniform RT
  over 0.3–5 s;
- (c) a fast guess only (guess_tau ≤ 0.3 s), no lapse.

Check fit to the chronometric and no-response functions, where the drift gain lands, and an **independent check**: the
fitted lapse rate against the lapse implied by each mouse's psychometric asymptote (about 2 × (1 − accuracy at 100%
coherence)).

**Cost:** 3 variants × 10 mice × 6 splits ≈ 180 jobs.

**Status (2026-10-20): implemented and submitted** (commit `3a97ea6`; analysis log section 5.5). (a) is the existing
L1U1V1Z0G1 in `ddm/fits_guess`; (b) `guess_lapse` and (c) `fast_only` run as 60 jobs each (5 CV folds + all trials),
warm-started from (a), into `ddm/fits_guess_guess_lapse` and `ddm/fits_guess_fast_only`.

**Decision:** a guess/lapse component that can be described in one sentence ("x% fast anticipatory responses at
chance; y% lapses") and that does not distort the decision parameters.

**Result (2026-10-21): fast_only chosen.** Held-out NLL vs the single form: fast_only −69.9 (9/10 mice), guess_lapse
−83.5; the lapse adds one parameter for 13.6 NLL (within noise) and is ≈ 0 in 8/10 mice. "About 20% fast responses
at chance." The psychometric asymptote implies far larger lapses than the fitted uniform lapse, so high-coherence
errors come from the decision process (probably sv); to check in the fit-quality plots. Still to run: fast_only with
guess_bias fixed at 0.5 (rule 3), on the chosen common model. Analysis log, section 5.5.
**Status (2026-10-22): ready to submit** (`--fixed_guess_bias`, analysis log 8.4c): L0U0V1Z0G1 fast_only with the
bias free and fixed, 5 CV folds + all + control (70 jobs each).

## Step 3. Fix the common model

**How:**
1. **Measure the Monte Carlo noise of the comparison.** Re-score the held-out folds of the top ~6 models with several
   evaluation seeds and 50 repetitions. The spread across seeds sets the threshold a difference must exceed, per mouse
   and summed, replacing the arbitrary "> 2 NLL".
   **Status (2026-10-20): script ready, not yet run.** `scripts/ddm/mc_noise.py` re-scores the saved `ddm/fits_guess`
   CV fits of L1U1V1Z0G1, its five one-mechanism-removed neighbours, L1U1V1Z1G1 and L1U0V1Z1G1 (70 jobs, one per
   mouse × variant) at 10 evaluation seeds × 15 and 50 repetitions; `--summarize` gives the SD across seeds of each
   model's NLL difference from L1U1V1Z0G1 (common random numbers make the difference, not each NLL, the relevant noise).
   Checked locally: seed 12345 at 15 repetitions reproduces the saved test_nll (PSUIM10, cv0, two variants).
   **Result (2026-10-21): done.** SD of a model difference per mouse: median 6.5–12.8 NLL at 15 reps, 4.1–5.9 at 50;
   summed over mice 22–54 and 13–21. Per mouse, sv helps in 9/10 and guesses in 7/10 mice (> 2 SE, 10 seeds × 50
   reps); leak in 4/10 and urgency in 3/10, only the mice with the most trials; sz in none (analysis log, section 5.6).
   **Follow-up (2026-10-22, analysis log 5.6):** the leak/urgency gain is not a power effect. The other seven mice
   pooled (12,307 trials) gain +6.8 ± 4.0 (leak) and −0.3 ± 4.5 (urgency), against +57.6 / +36.9 in PSUIM6 alone.
   Where they help, they mainly fit the rate of censored (> 5 s) trials, which is nearly coherence-independent, while
   the late responses themselves are coherence-dependent (likely late engagement, not leaky integration or urgency).
   A delayed-engagement parameter was considered and **not pursued** (V. Thakur, 2026-10-22).
   **Decision (2026-10-22, V. Thakur): strict.** Common model L0U0V1Z0G1 with fast_only guesses; L1U1V1Z0G1
   (fast_only) is the secondary baseline (primacy plan, amendment 3). Paper consequences in the outline (`dissemination/paper/outline.md`,
   R4). Relaxing rule 2 instead (path B) would be a dated deviation, needs step 3.3 and recovery of leak/urgency, and
   puts a leaky (recency-weighted) baseline under the primacy test.
2. **Select mechanisms** that (i) improve held-out NLL beyond that threshold in most mice and hurt none, and (ii) have
   population-level support (family protected exceedance clearly above 0.5). If in doubt, include: the models are
   nested, so an unneeded mechanism mostly adds parameter noise, while a missing one biases the rest.
3. **Check the choice does not depend on pulse trials.** Mechanisms were selected on all trials, pulses included,
   and the primacy test then uses that model; if leak or urgency were favoured partly because they fit the pulse-timing
   pattern, the test would be partly built in. Re-run the comparison for the top models with cross-validation within
   control trials only (control-only CV split; ~6 models × 10 mice × 5 folds = 300 jobs) and confirm the same
   mechanisms are selected.
   **Status (2026-10-22): ready to submit.** New splits `ccv0`–`ccv4` (CV within control trials) in
   `fit_mouse_ddm.py`; strict model, minus sv, minus guesses, plus leak, plus urgency, plus both (300 jobs, analysis log
   8.4c). No warm starts exist for these splits, so nested pairs are checked before comparing.

**Decision:** one model for all mice, so parameters and pulse predictions are comparable across mice and rigs.

## Step 4. Model and parameter recovery

**Why:** leak, urgency and guesses all shape late decisions and can mimic each other; with 300–7,500 trials per mouse
some may not be identifiable. Without this check we cannot claim a mechanism is present, or interpret its parameter.

**How:** `scripts/ddm/model_recovery.py` with `COMMON` set to the chosen model: simulate each mouse's own trials from the
common model and from each one-mechanism-removed model (using the mouse's fitted parameters), fit all candidates,
score them on an independent simulated test set. Also compare recovered vs generating parameters, and the NLL at the
generating parameters vs at the recovered ones (optimizer check).

**Cost:** 720 jobs at the current 6 generators (2 replicates); fewer if the common model has fewer mechanisms.

**Decision:** for each mechanism and mouse, whether "present" and "absent" are distinguishable. Mechanisms that are not
recoverable are reported as a family ("late-trial mechanisms") rather than individually, and their parameters are not
interpreted for the small mice.

**Status (2026-10-22): script updated, not yet run.** `COMMON = "L0U0V1Z0G1"`, fast-only guesses; generators and
candidates are the common model, minus sv, minus guesses, plus leak, plus urgency (500 jobs). The two added models
test whether the comparison would have detected leak or urgency where present, i.e. "absent" vs "undetectable" in the
smaller mice. Needs the all-trial generator fits (analysis log 8.4c, batch 3) and the guess-bias decision first.

## Step 5. Precise final fits

**How:** refit the common model on all trials and on control trials only, per mouse, with more simulation repetitions
(e.g. 50 instead of 15) and warm starts. Also fit the control-only model **without leak** as a second baseline for
step 6.

**Cost:** ~30 jobs.

**Benefit:** the parameter values to report and the control-only models step 6 needs.

## Step 6. Primacy test (the scientific question)

**Why:** in a reaction-time task, late pulses affect fewer decisions even when evidence is weighted equally over time,
because many trials have already ended or are within the non-decision time (Okazawa et al. 2018). So "late pulses have
smaller effects" is not by itself evidence of primacy. The question is whether they have **smaller effects than a
constant-weight accumulator predicts**.

### 6.1 Write the analysis plan first
**Status:** locked in [`primacy-analysis-plan.md`](primacy-analysis-plan.md), commit `aeb0a22` (2026-10-20).

Before looking at pulse-trial residuals, write down and commit: the outcome measures (pulse effect on choice, e.g.
shift of the psychometric function or change in P(right) in the pulse direction; effect on RT), the time windows and
bins, the statistical model below, and the decision rule. This is the confirmatory test; anything decided after seeing
the residuals is reported as exploratory.

### 6.2 Predictive check on pulse trials
The control-only model must predict pulse trials adequately in ways that do **not** involve the timing contrast:
the pulse effect averaged over all onset times, and pulse-trial RT distributions. If it fails there (e.g. because
the ±100% pulses drive motion energy differently than assumed), fix the model before testing timing; otherwise the
timing residuals absorb that error.

### 6.3 Within-mouse design
The confound between pulse timing and rig (late pulses exist only on UW) is avoided by contrasts **within each mouse**:
rig differences (screens, dots, pulse lengths, cohorts) shift a mouse's overall pulse effect but cancel from
"early minus middle" inside that mouse.
- **Primary:** early vs middle pulses, which both rigs have, so all 10 mice contribute.
- **Secondary:** early/middle vs late, UW mice only (6 mice), reported as such and not pooled into one timing curve.
- Where onset varies within a bin (UCLA), use onset time as a continuous within-mouse regressor.

### 6.4 Statistical model
One mixed-effects model across all mice, not separate tests per rig: pulse effect (observed minus predicted) against
pulse timing, with a random intercept and slope per mouse and rig as a covariate. All mice inform the timing slope; the
rig term only asks whether rigs disagree (a null there is "no evidence of a difference", not replication).

### 6.4b Model-free check (parsimony rule 5)
A logistic regression of the pulse effect on choice by timing, without the DDM (primacy plan, amendment 2). Agreement
with 6.4 means the conclusion does not depend on the model's details.

### 6.5 Baseline dependence
The baseline model itself shapes temporal weighting: leak discounts early evidence (predicts recency), urgency and the
bound reduce the influence of late evidence. Report the residuals against both baselines (with and without leak,
step 5). As the main model-based test, add an explicit time-varying evidence weight (e.g. drift gain decaying over
time) to the common model, fit it on all trials (the pulses carry the timing information), and test it against the
common model by cross-validation (~60–120 jobs).

**Status:** the time-varying weight is implemented (`gain_decay`: drift gain × exp(−gain_decay · t), both simulator
backends; `fit_mouse_ddm.py --time_varying_gain`, output `ddm/fits_guess_W` or `..._<form>_W`). Checked: the two
backends agree, positive values lower and negative values raise accuracy, and 0 reproduces the constant-weight model.
Ready to run once the common model is fixed. A second primacy mechanism was added (primacy plan, amendment 1): a
self-exciting accumulator via negative leak (`--signed_leak`, `leak_rate` down to −1/s, output `..._NL`). Urgency is not a
primacy/recency mechanism: it scales all accumulated evidence equally and only changes when decisions end.

### 6.6 Sensitivity (simulation-based power)
No new mice needed: simulate each mouse's real trials from its fitted model with a known amount of primacy added
(evidence weight decaying by e.g. 10%, 20%, 40% over the first 0.5 s), run the 6.3–6.4 analysis on the simulated data,
and find the smallest decay detected reliably. A null result is then reported as "primacy larger than X is unlikely".
Reuses the model-recovery machinery.

**Status (2026-10-22): code ready and checked on synthetic data** (`primacy.py`, `primacy_sensitivity.py`; analysis
log 5.7). **Power problem:** under the fitted model a pulse moves choices by ~0.025 logit. Even full primacy changes
β_middle by ≤ 0.04, below the test's resolution (~0.1–0.15). Decision pending on how to proceed (analysis log 5.7,
options 1–3).

**Benefit:** a direct, model-based answer to whether mice weight early evidence more, which the noise-based kernels
cannot give (the stimulus noise is fixed within a trial), with the rig confound, the baseline's own temporal weighting
and model misfit on pulse trials handled explicitly.

## Step 7. Remaining misfits and robustness (lower priority)

- **Misfits:** UCLA mice choose left more than predicted at −36% to 0%; errors at 36% are faster in the data than the
  model; errors at 100% still too slow for DBM6 and DBM14. Revisit after step 2.
- **Spatial pooling:** refit the common model with centre-of-screen motion energy (`build_ddm_inputs --region center`).
- **Hidden-coherence ratio (k ≈ 0.50):** refit the choice GLM with lapse terms, or with |coherence| ≤ 18%, since the
  linear-logit assumption affects programmed coherence (up to 36%) more than hidden coherence (about ±6%).
- **Motion-energy settings:** filter-sensitivity check and screen-geometry correction (methods doc, sections 3.7 and 5).
- **Cleanup:** remove or replace section 6 of notebook 2.14 (old pulse kernels, marked "under revision").

---

## Order and dependencies

```
Step 0 (rig behaviour) ─> Step 1 (warm starts) ─┐
                          Step 2 (guess/lapse) ─┼─> Step 3 (noise threshold, common model, control-only check)
                                                │        ├─> Step 4 (recovery)
                                                │        └─> Step 5 (final fits) ─> Step 6 (6.1 plan → 6.2 check → 6.3–6.6)
Step 7 (robustness) ────────────────────────────┴── any time after step 3
```

Steps 1 and 2 can run on Hyak together. Write the step 6.1 analysis plan early (it does not depend on any fit); a first
pass of 6.2 can use the existing control-only fits once step 3 is settled.

## What each step adds to the final analysis

| Step | Without it | With it |
|---|---|---|
| 0 Rig behaviour | Simulation rules rest on inference | Simulated RTs and pulse inputs match the rigs |
| 1 Warm starts | Comparison biased against some mechanisms | Mechanism verdicts reflect the data, not the optimizer |
| 2 Guess/lapse | A catch-all component that is hard to describe and may distort decision parameters | Interpretable guess and lapse rates, checked against the psychometric lapse |
| 3 Common model | Thresholds arbitrary; selection possibly shaped by pulse trials | Noise-based thresholds; one model, selected without pulse trials |
| 4 Recovery | Cannot claim a mechanism is present | Known which mechanisms and parameters are identifiable, per mouse |
| 5 Final fits | Parameters limited by simulation noise; one baseline | Reportable parameters; two baselines for step 6 |
| 6 Primacy test | Confounded by rig, baseline weighting and misfit | Within-mouse, pre-specified, baseline-checked test with known sensitivity |
| 7 Robustness | Results tied to one ME setting | Known sensitivity to spatial pooling and filter choices |

## Changes after the 2026-10-20 review

- Added step 0 (confirm rig behaviour) and the external lapse check in step 2.
- Step 3: measured Monte Carlo noise thresholds; confirmation of the mechanism choice by control-only cross-validation.
- Step 5: a no-leak control-only baseline.
- Step 6 rewritten: analysis plan written first; predictive check on pulse trials; within-mouse contrasts with early vs
  middle as primary (all 10 mice) and late pulses as UW-only secondary, instead of per-rig group tests (too few mice);
  one mixed-effects model with rig as a covariate; baseline dependence; simulation-based sensitivity instead of a
  conventional power analysis.
- Step 7: hidden-coherence robustness and notebook cleanup.
