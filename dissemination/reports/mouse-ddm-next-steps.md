# Mouse pulse task: plan for the next DDM steps

**Written:** 2026-10-20. **Branch:** `mouse-motion-energy`. Background and everything done so far:
[`mouse-ddm-analysis-log.md`](mouse-ddm-analysis-log.md).

## Where we are

The DDM is driven by each trial's own motion energy, handles the 5 s deadline (censoring) and the 0.3 s minimum
viewing time (floor), and includes a fast-guess component. The current 32-model grid (`ddm/fits_guess`, 2,239 of 2,240
fits, 5-fold cross-validation) favours **leak + urgency + sv + guesses, without sz** (`L1U1V1Z0G1`), and that model
fits psychometric, chronometric and no-response functions much better than any model without guesses.

Four things stop us from treating that as the answer yet:
1. Some larger models were under-optimized, which biases the comparison against extra mechanisms (mostly sz).
2. The "guess" component behaves like a general lapse process (rate 14–47%, delays up to its 2 s limit), which makes
   it hard to interpret and may absorb what leak, urgency or the drift gain should explain.
3. We have not checked that the mechanisms can be told apart at these trial counts (model recovery).
4. The scientific question, whether late pulses matter less than a constant-weight accumulator predicts (primacy), has
   not been tested.

The plan below addresses them in order. Each step says what it is for, how, what it costs, and what we decide from it.

---

## Step 1. Warm-start refits of under-optimized fits

**Why:** in 1.3% of nested pairs (all-trial fits) a larger model fits worse than a model it contains by > 20 NLL, which
is impossible at the optimum. These failures are concentrated in PSUIM7 and in models with sz added. Left alone, they
make sz (and to a lesser degree leak and urgency) look less useful than they are.

**How:** add an option to `fit_mouse_ddm.py` to seed differential evolution with the best parameters of each nested
model (the same model with one mechanism switched off, plus the extra parameter at its "off" value). A larger model
then starts at least as good as every model it contains. Refit only the failing fits (about 50, across splits) and the
missing `PSUIM6_L1U1V1Z1G1_all`, into a new folder; rerun `compare_models.py`.

**Cost:** ~50 Hyak jobs, mostly the big UCLA mice (1–5 h each).

**Benefit / decision:** an unbiased per-mechanism comparison. Decide whether sz stays out and how strong the case for
urgency is once guesses are present.

## Step 2. Make the guess component interpretable

**Why:** at present one component covers both fast anticipatory responses (< 0.6 s, near chance) and slow
stimulus-independent responses (delays up to 2 s). That mixes two behaviours, and a broad lapse process can take over
variance that belongs to the decision process (drift gain hits its lower bound in 39 all-trial fits).

**How:** compare, by cross-validation on the leading model only (not the full grid):
- (a) current single guess component;
- (b) a fast guess with a constrained delay (e.g. guess_tau ≤ 0.3 s) plus a separate lapse component with a uniform RT
  over 0.3–5 s;
- (c) a fast guess only (guess_tau ≤ 0.3 s), no lapse.
Check which fits the chronometric and no-response functions best, and where the drift gain lands.

**Cost:** 3 variants × 10 mice × 6 splits ≈ 180 jobs.

**Benefit / decision:** a guess/lapse component we can describe in one sentence in a paper ("x% fast anticipatory
responses at chance; y% lapses"), and decision parameters that are not distorted by it.

## Step 3. Fix the common model

**How:** from steps 1–2, include each mechanism that (i) improves held-out NLL in most mice and hurts none by more than a
few NLL, and (ii) has population-level support (family protected exceedance probability clearly above 0.5). If in doubt,
include it: the models are nested, so an unneeded mechanism mostly adds parameter noise, while a missing one biases the
rest.

**Benefit:** one model for all mice, so parameters and pulse predictions are comparable across mice and rigs.

## Step 4. Model and parameter recovery

**Why:** leak, urgency and guesses all shape late decisions and can mimic each other; with 300–7,500 trials per mouse
some may not be identifiable. Without this check we cannot claim a mechanism is present, or interpret its parameter.

**How:** `scripts/ddm/model_recovery.py` with `COMMON` set to the chosen model: simulate each mouse's own trials from the
common model and from each one-mechanism-removed model (using the mouse's fitted parameters), fit all candidates,
score them on an independent simulated test set. Also compare recovered vs generating parameters, and the NLL at the
generating parameters vs at the recovered ones (optimizer check).

**Cost:** 720 jobs at the current 6 generators (2 replicates); fewer if the common model has fewer mechanisms.

**Benefit / decision:** for each mechanism and mouse, whether "present" and "absent" are distinguishable. Mechanisms
that are not recoverable are reported as a family ("late-trial mechanisms") rather than individually, and their
parameters are not interpreted for the small mice.

## Step 5. Precise final fits

**How:** refit the common model on all trials and on control trials only, per mouse, with more simulation repetitions
(e.g. 50 instead of 15) and warm starts, so the parameters and predictions are not limited by simulation noise.

**Cost:** 20 jobs (10 mice × 2 splits), longer per job.

**Benefit:** the parameter values to report (bounds, drift gain, leak, urgency, guess rate) and the control-only model
needed for step 6.

## Step 6. Primacy test (the scientific question)

**Why:** in a reaction-time task, late pulses affect fewer decisions even when evidence is weighted equally over time,
because many trials have already ended or are within the non-decision time (Okazawa et al. 2018). So "late pulses have
smaller effects" is not by itself evidence of primacy. The test is whether they have **smaller effects than a
constant-weight accumulator predicts**.

**How:**
1. Take each mouse's control-only fit of the common model (step 5); the control-only split is already fitted for all 32
   models in `fits_guess`, so a first pass can start right after step 3.
2. Simulate the pulse trials with it (their own motion energy, pulses included) and compute the predicted pulse effect
   on choice (e.g. shift of the psychometric function) and on RT, per pulse timing (early / middle / late) and
   direction.
3. Compare with the observed pulse effects: observed minus predicted, per timing bin and mouse; group statistics across
   mice (mouse as the unit).
4. If late pulses fall short of the prediction, fit an extension with time-varying evidence weight (e.g. drift gain
   decaying over time) and test it by cross-validation against the common model.

**Cost:** step 2–3 is local analysis; step 4 is one more small grid (~60–120 jobs).

**Benefit:** a direct, model-based answer to whether mice weight early evidence more, which is the main result the DDM
is for, and which the noise-based kernels cannot give (the stimulus noise is fixed within a trial).

## Step 7. Remaining misfits and robustness (lower priority)

- **Misfits:** UCLA mice choose left more than predicted at −36% to 0%; errors at 36% are faster in the data than the
  model; errors at 100% still too slow for DBM6 and DBM14. Revisit after step 2 (the guess/lapse change may fix some).
- **Spatial pooling:** refit the common model with centre-of-screen motion energy (`build_ddm_inputs --region center`);
  the choice GLM suggests mice may not use the whole screen (hidden coherence weighted at ~0.5).
- **Motion-energy settings:** filter-sensitivity check and screen-geometry correction (methods doc, sections 3.7 and 5).

---

## Order and dependencies

```
Step 1 (warm-start refits) ─┐
Step 2 (guess/lapse)  ──────┼─> Step 3 (common model) ─> Step 4 (recovery)
                            │                        └─> Step 5 (final fits) ─> Step 6 (primacy)
Step 7 (robustness) ────────┴── any time after step 3
```

Steps 1 and 2 can run on Hyak at the same time. A first pass of step 6 can use the existing control-only fits as soon as
step 3 is settled, before steps 4 and 5 finish.

## What each step adds to the final analysis

| Step | Without it | With it |
|---|---|---|
| 1 Warm starts | Comparison biased against some mechanisms | Mechanism verdicts reflect the data, not the optimizer |
| 2 Guess/lapse | A catch-all component that is hard to describe and may distort decision parameters | Interpretable guess and lapse rates; cleaner decision parameters |
| 3 Common model | Different models per mouse; parameters not comparable | One model across mice and rigs |
| 4 Recovery | Cannot claim a mechanism is present | Known which mechanisms and parameters are identifiable, per mouse |
| 5 Final fits | Parameters limited by simulation noise | Reportable parameter estimates and a precise control-only model |
| 6 Primacy test | Pulse timing effects confounded by RT and non-decision time | A model-based test of primacy |
| 7 Robustness | Results tied to one ME setting | Known sensitivity to spatial pooling and filter choices |
