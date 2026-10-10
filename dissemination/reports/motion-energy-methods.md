# Motion energy for mouse RDK trials: method review and corrections

**Status (2026-10-10):** review and proposed method. The fixes below have been validated in a prototype but are **not yet implemented** in the pipeline. The shard outputs currently on disk (`processed/motion_data_dict/me_shard_{0,1}.pkl`, 25,508 trials) were produced with the old settings described in section 1.

**Purpose:** motion energy (ME) is the trial-by-trial evidence signal for the psychophysical kernels and for the DDM fits. This document records how ME is currently computed, which problems that has, and the corrected method for mice. The corrected method must also be fast enough to regenerate for every trial.

---

## 1. Current pipeline

Code: [`scripts/compute_motion_energy_full.py`](../../scripts/compute_motion_energy_full.py), helpers in [`scripts/motion_energy.py`](../../scripts/motion_energy.py), and postprocessing in [`notebooks/2.10-motion-energy-postprocessing.ipynb`](../../notebooks/2.10-motion-energy-postprocessing.ipynb).

1. **Stimulus replay.** Each trial's random-dot stimulus is regenerated from `stimulus_seed` and `signed_coherence` with the rig's own RDK code (`ucla_rdk.py` or `uw_rdk.py`). If the trial had a pulse, coherence is switched at the pulse onset frame and back at the offset frame. Frames are rendered up to `rt_frame`.
   - Dots are drawn at native screen resolution: UCLA 1920×1080 at 20 px/deg, UW 1280×720 at 10 px/deg.
   - Each frame is then resampled to 0.2° per sample.
2. **Filters.** These follow the Adelson & Bergen (1985) energy model as used by Kiani, Hanks & Shadlen (2008):
   - Spatial: `f1 = cos⁴(α)·cos(4α)` and `f2 = cos⁴(α)·sin(4α)`, with α = atan(x/σc), each multiplied by a Gaussian in y with width σg.
   - Temporal: `gₙ(t) = (kt)ⁿ e^{−kt} [1/n! − (kt)²/(n+2)!]` for n = 3 and 5.
   - Settings: σc = 4°, σg = 2°, k = 2π·5 ≈ 31.4 s⁻¹. The filter grid is x, y ∈ [−6°, 6°) at 0.1° and t ∈ [0, 0.1) s at 1/60 s.
3. **Energy.** The two rightward filters are f1g1 + f2g2 and f2g1 − f1g2; the leftward filters are f1g1 − f2g2 and f2g1 + f1g2. The stimulus is convolved with each using `F.conv3d` with centered padding, and **ME = R1² + R2² − L1² − L2²**. Positive values mean rightward motion.
4. **Pooling.** ME is averaged over space into time series per trial: `global`, `center` (the middle half of the screen in each dimension), and the quadrants `Q1` to `Q4`.
5. **Postprocessing.** The last 3 samples are dropped, each series is padded with NaN to 600 frames, and each session is divided by its largest absolute value.

### Comparison with Kiani, Hanks & Shadlen (2008)

| | Kiani et al. 2008 | Current pipeline |
|---|---|---|
| Filter equations | as above | same |
| σc | 0.35° | 4° (8° in practice, see 2.1) |
| σg | not stated | 2° |
| k | 60 s⁻¹ | 31.4 s⁻¹ |
| Tuning rule | "centered on the speed of coherent motion in our display" | rescaled for mice, but see 2.1 |
| Spatial pooling | sum | mean (only changes the scale) |
| Normalization | none | divide by session maximum |
| Kernel analysis | 0% coherence trials, split by choice, aligned to onset | coherence-mean-subtracted residuals (Nienborg & Cumming 2009; Okazawa et al. 2018) |

The Kiani task had a fixed viewing duration. Ours is reaction-time.

---

## 2. Problems found

### 2.1 Filter and stimulus grids differ
The filters are built at 0.1° per sample, but the stimulus is resampled at 0.2° per sample. `get_stimulus_array_*` defaults to `dx_deg=0.2`, and the script does not override it. Each filter tap therefore covers 0.2° of stimulus, which doubles the effective filter size and the preferred speed.

| | Preferred SF | Preferred TF | Preferred speed |
|---|---|---|---|
| Kiani 2008 (σc 0.35°, k 60) | 1.36 c/deg | 4.4 Hz | 3.2°/s |
| Current, as written (σc 4°, k 31.4) | 0.12 c/deg | 2.4 Hz | 20°/s |
| **Current, as run** (effective σc 8°) | 0.06 c/deg | 2.4 Hz | **40°/s** |
| Dot speed | | | UCLA 28.5°/s, UW 30°/s |

Dot speeds come from the RDK code: UCLA moves 3 px × 190/60 per frame at 20 px/deg, and UW moves int(350/60) = 5 px per frame at 10 px/deg, both at 60 Hz.

### 2.2 Temporal filters are cut short
With k = 31.4 s⁻¹, the fast filter (n = 3) peaks at about 73 ms and the slow one (n = 5) at about 124 ms. The window `t_range_s = (0, 0.1)` keeps only 6 frames, ending at 83 ms. Most of the slow filter is missing, so the two are not a proper quadrature pair and direction selectivity is weakened.

### 2.3 Temporal padding is off by one and uses future frames
Even-sized kernels with `s//2` padding on each side make each output one sample longer than the input. Centered padding also means each time point uses about 3 frames that come after it. Dropping the last 3 samples (`me[:-3]`) in notebook 2.10 is a workaround for this.

### 2.4 Normalization depends on one extreme trial
Dividing each session by its largest |ME| sets the scale from a single high-coherence trial. As a result the scale varies between sessions and is not comparable between rigs. The rigs genuinely differ by about 5× in raw ME (section 4) because of dot size and pixels per degree.

### 2.5 Notebook 2.10 cannot read the current output
The loader expects one file per trial, named `me_array_<code>.pkl`, which is what the older scripts wrote. `compute_motion_energy_full.py` writes two shard dictionaries keyed by `agg_code`, so the notebook would read them as two "trials" called `me_shard_0` and `me_shard_1`.

### 2.6 DDM time base does not match (high impact)
[`src/models/ddm/full_ddm.py`](../../src/models/ddm/full_ddm.py) steps at `dt = 1 ms` and reads `stimulus[trial, t-1]`, but each ME sample is one 16.67 ms frame. The model therefore treats 600 frames as 0.6 s, compressing the evidence about 17× in time.

### 2.7 ME stops at the observed RT (high impact)
The simulator stops at the first NaN, and ME is only generated up to `rt_frame`. A simulated trial therefore cannot respond later than the animal actually did. This leaks the observed RT into the model and biases the RT fit.

---

## 3. Corrected method

### 3.1 Filter parameters for mice
Following Kiani et al., the filters are tuned to the speed of the dots (about 30°/s on both rigs), while staying inside the range mice are sensitive to:
- Mouse V1 neurons prefer about 0.03–0.04 c/deg (range 0.01–0.18) and about 1.8 Hz (range 0.25–8 Hz).
- Behavioral optomotor responses are strongest at 0.1–0.2 c/deg, with acuity limited to about 0.4 c/deg.

The filters' peak frequencies scale as **SF ≈ 0.477 / σc** and **TF ≈ 0.071 · k**.

| Parameter | Value | Reason |
|---|---|---|
| σc | **6°** | gives 0.080 c/deg |
| k | **34 s⁻¹** | gives 2.40 Hz; preferred speed 30.2°/s, matching the dots |
| σg | **3°** (σc/2) | receptive field about as wide as it is tall (half-widths about 3.8° in x and 3.5° in y) |
| Grid | **0.5° per sample** for both stimulus and filters | passes frequencies up to 1 c/deg, far above the filter passband; 6–9× fewer pixels than now |
| Downsampling | render at native resolution, then `cv2.INTER_AREA` | area averaging avoids aliasing; overlapping dots render as they did on screen |
| x extent | ±3σc = ±18° | covers 98.6% of the filter envelope's weight |
| y extent | ±3σg = ±9° | |
| t extent | 0–0.55 s (33 frames) | both temporal filters are below 1% of peak by 550 ms (peaks at 67 and 117 ms) |
| Time step | 1/60 s | one sample per display frame |

### 3.2 Causal temporal filtering
Pad only at the start with zeros (accurate, because the screen is blank before the dots appear), and use no future frames. The output has the same length as the input, so the `[:-3]` trim is no longer needed.

The filters delay the response: they peak at 67 and 117 ms, and their response is centred at about 116 and 176 ms. This stands in for the sensory delay of a real visual system. In the DDM it is absorbed by the non-decision time, so the fitted `ndt` includes it. Its lower bound (currently 0.1 s) should be reviewed with that in mind.

**Do not use forward-backward (zero-phase) filtering to remove this delay.**
- Direction selectivity comes from the timing difference between the fast and slow temporal filters. Running each filter forward and then backward makes it symmetric in time and removes that difference. In the prototype, net ME at ±100% coherence fell from ±126 to ±0.8, a loss of about 160×.
- It would also put future frames, including frames after the decision, into the evidence at time t.
- For figures only, ME may be plotted against `t − ~100 ms`, stated in the caption, without changing the data.

### 3.3 Spatial borders
Zero padding in space. This matches the display, since the screen is surrounded by darkness.

### 3.4 Calibration per rig
Raw ME scale depends on dot size and pixels per degree. For each rig:
1. Fit how mean ME (after the first ~150 ms, once the filters have warmed up) grows with nominal signed coherence.
2. Divide by that slope.

ME is then in equivalent-%-coherence units, so `drift_gain` means the same thing on both rigs and can be compared with a DDM fitted to nominal coherence. This replaces normalizing per session.

### 3.5 Generate ME beyond the RT for the DDM
The dots are fully determined by the seed, so each trial can be regenerated out to the longest time being fitted (5 s = 300 frames). This is what the stimulus would have shown had the animal not yet responded.
- **DDM:** use ME out to the full duration (300 frames).
- **Psychophysical kernels:** use ME cut at the RT, i.e. only what was actually shown.

### 3.6 DDM indexing
Index ME by frame inside the 1 ms simulation loop: `ME[trial, int(t_ms / 16.667)]`. Alternatively, repeat each frame to 1 ms steps before fitting. Store one float32 array of trials × 300 frames per pooling region.

### 3.7 Screen geometry (needs rig measurements)
A constant 20 or 10 px/deg is only correct at the screen center. The UCLA screen spans about 96°, and on a flat screen close to the mouse the degrees per pixel change strongly toward the edges. Pixels should be mapped to visual angle with `atan(x_cm / viewing_distance)`, which takes one `cv2.remap` per frame.

**Needed:** screen width and eye-to-screen distance for each rig.

---

## 4. Fast implementation

Each directional filter is a sum of space-time-separable parts. Write `A_ab` for the stimulus filtered by `f_a(x)`, then the y-Gaussian, then `g_b(t)`, with a, b ∈ {1, 2}. The net energy then reduces exactly to

```
ME = (R1² + R2²) − (L1² + L2²) = 4 · (A11·A22 − A12·A21)
```

This needs one y-pass, two x-passes and four t-passes, all 1-D: about 215 multiplications per pixel at the 0.5° grid, instead of about 165k for four full 3-D kernels. On the GPU, trials can be batched with `conv1d`, or with an FFT along time.

### Prototype validation
These results come from a scratchpad prototype run on CPU, using the rigs' own RDK code at 0.5° and with the parameters in 3.1.

| Check | UCLA | UW |
|---|---|---|
| Separable form vs direct 3-D convolution (max relative error) | 6.0e-8 | 4.0e-8 |
| CPU time per 120 frames, direct 3-D (FFT) → separable | 2.43 s → 0.94 s | 2.52 s → 0.70 s |
| Rendering time per 120 frames (native + area downsample) | 0.11 s | 0.06 s |
| Mean ME at −100 / −25 / 0 / +25 / +100 % coherence | −166 / −52 / −1 / +38 / +180 | −884 / −214 / +1 / +241 / +942 |

- ME scales linearly with coherence and has the correct sign on both rigs.
- The roughly 5× difference in scale between rigs is the reason for calibrating per rig (3.4).
- An alternative that spreads dot centers straight onto the 0.5° grid, skipping rasterization, correlated only 0.96–0.99 with the rendered version because it handles overlapping dots incorrectly. It was rejected.

**Estimated full run:** 25.5k trials × 300 frames is about 4 minutes of rendering across 32 CPU cores, with negligible GPU time. This is an estimate, not a measured end-to-end run.

---

## 5. Validation and robustness

1. **Filter sensitivity.** Compute ME for 2–3 alternative settings (σc 5–7°, k 30–40 s⁻¹). Compare how well each predicts choices on held-out data, using logistic regression of choice on residual ME (each trial's ME minus the mean for its coherence). Do not choose by DDM likelihood, or the same data both picks the filter and gets fit with it.
2. **Sanity checks to keep in the pipeline:**
   - Mean ME at 0% coherence is about zero.
   - Mean ME is linear in coherence, with a consistent slope across sessions within a rig.
   - Pulse trials show the energy change in the expected frames.

---

## 6. To-do

- [ ] Rewrite `compute_motion_energy_full.py` with sections 3.1–3.3 and the separable GPU form, generating 300 frames per trial (3.5).
- [ ] Add the per-rig calibration step (3.4).
- [ ] Update notebook 2.10 to read the shard dictionaries (2.5), and remove the `[:-3]` trim and session-max normalization.
- [ ] Fix the DDM frame indexing (3.6) and review the `ndt` bounds (3.2).
- [ ] Measure screen width and viewing distance for each rig, then add the angle correction (3.7).
- [ ] Run the filter sensitivity analysis (section 5).

---

## References

- Adelson EH, Bergen JR (1985). Spatiotemporal energy models for the perception of motion. *J Opt Soc Am A* 2:284–299.
- Kiani R, Hanks TD, Shadlen MN (2008). Bounded integration in parietal cortex underlies decisions even when viewing duration is dictated by the environment. *J Neurosci* 28:3017–3029. https://www.jneurosci.org/content/28/12/3017
- Niell CM, Stryker MP (2008). Highly selective receptive fields in mouse visual cortex. *J Neurosci* 28:7520–7536. Mouse V1 spatial-frequency values as summarized in https://journals.physiology.org/doi/full/10.1152/jn.00022.2012
- Andermann ML, Kerlin AM, Roumis DK, Glickfeld LL, Reid RC (2011). Functional specialization of mouse higher visual cortical areas. *Neuron* 72:1025–1039. https://pmc.ncbi.nlm.nih.gov/articles/PMC3876958/
- Umino Y, Solessio E, Barlow RB (2008). Speed, spatial, and temporal tuning of rod and cone vision in mouse. *J Neurosci* 28:189–198. https://www.jneurosci.org/content/28/1/189
- Nienborg H, Cumming BG (2009). Decision-related activity in sensory neurons reflects more than a neuron's causal effect. *Nature* 459:89–92.
- Okazawa G, Sha L, Purcell BA, Kiani R (2018). Psychophysical reverse correlation reflects both sensory and decision-making processes. *Nat Commun* 9:3479. https://www.cns.nyu.edu/kianilab/papers/Okazawa_Kiani_2018.pdf
