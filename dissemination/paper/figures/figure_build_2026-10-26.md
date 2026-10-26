# Main-figure build status — 2026-10-26

Selected current drafts (PDF and SVG are editable vector exports; PNG is the 300-dpi review rendering):

- Figure 1: `fig1_task_behaviour_2026-10-26_v2.{pdf,svg,png}`
- Figure 2: `fig2_stimulus_reconstruction_2026-10-26_v5.{pdf,svg,png}`
- Figure 3: `fig3_control_models_2026-10-26_v4.{pdf,svg,png}`
- Figure 4: `fig4_pulse_behaviour_2026-10-26_v2.{pdf,svg,png}`
- Figure 5: `fig5_model_mismatch_2026-10-26_v3.{pdf,svg,png}`

Each selected basename has adjacent `*_source_*.csv` files containing exactly the rows used in the artwork. Earlier
same-day versions are retained because repository policy forbids overwriting results; they are layout drafts and are
not the selected versions.

The selected set uses a provisional 180-mm full width pending final journal production specifications. Same-day earlier
versions are retained as layout drafts and are not selected artwork.

## Draft captions for the assembled figures

### Figure 1. The experiment provided choice, response-time and no-response constraints during motion discrimination with scheduled directional perturbations

**(A)** Head-fixed mice viewed dynamic random-dot motion and reported leftward or rightward motion at two lick ports.
Responses could register after the 0.3-s minimum viewing interval. The 5-s cutoff is an analysis boundary, not a shared
task-termination time. **(B)** Scheduled replacement of the baseline stimulus by ±100% coherence. UCLA pulses occurred
at early and middle onsets (medians 61 and 241 ms; median duration 51 ms); UW pulses occurred at 50, 233 and 417 ms
(duration 67 ms). Fine horizontal lines show the observed UCLA onset ranges. **(C)** Rightward-response probability on
scheduled-control trials, conditional on response by 5 s. Grey traces are mice; black points and bars are the equal-mouse
mean ± SEM. All 10 mice contributed at each signed coherence; the displayed trial counts from −100% to +100% were
2,277, 1,380, 1,292, 1,356, 1,315, 1,350, 1,392, 1,400 and 2,253 (14,015 responses total). **(D)** Within-mouse median
response time for correct and error responses versus absolute coherence. At zero coherence all responses are shown
separately. A mouse entered a cell with at least 10 responses; all 10 mice met this threshold at every displayed point.
The zero-coherence count was 1,315; correct counts at 9, 18, 36 and 100% were 1,544, 1,772, 2,082 and 3,908, and error
counts were 1,162, 912, 698 and 622. Thin traces show mice and emphasized symbols show equal-mouse mean ± SEM.
**(E)** Probability of no response by 5 s on all scheduled-control trials. Green circles and purple squares identify
UCLA and UW mice; black points and bars are equal-mouse mean ± SEM across all 10 mice. From −100% to +100%, total
trial counts were 2,528, 1,664, 1,629, 1,650, 1,627, 1,661, 1,666, 1,630 and 2,467, of which 251, 284, 337, 294,
312, 311, 274, 230 and 214 had no response by 5 s. The complete dataset comprised 10 mice, 50 mouse-sessions,
25,508 within-window responses and 4,537 no-response trials. Panels C–E are descriptive and use mice, not trials or
sessions, for group uncertainty. No asterisks are used.

### Figure 2. Stimulus reconstruction defined the model input and exposed replay uncertainty beyond nominal coherence

**(A)** Reconstruction pipeline from logged seed and task parameters through rendered 60-Hz dot frames, causal
direction-opponent filtering, spatial averaging and rig-specific calibration to equivalent-coherence units. The replay
is model-derived and is not claimed to be a frame-perfect display record. **(B)** Motion energy averaged over 0.33–5 s
versus programmed coherence on responded scheduled-control trials. Symbols and bars are trial mean ± SD (UCLA,
9,258 trials; UW, 4,757 trials); the dotted line is identity. **(C)** Distribution of the same 0.33–5-s average on
nominal 0% control trials (UCLA, 872 trials; UW, 443 trials). Small points are trials, violins show their distributions,
and open symbols and bars are trial mean ± SD. **(D)** Paired, same-seed replay difference between pulse-present and
physically pulse-omitted stimuli, multiplied by scheduled pulse sign and aligned to logged onset (UCLA, 76 trials; UW,
108 trials). Lines are trial means and bands are pointwise 95% Student-t intervals. The streams are identical before
onset and diverge after the task consumes different random draws; later dispersion therefore includes random-stream
divergence. The grey span covers the longer, four-frame pulse window. **(E)** UCLA pulse energy over 0–333 ms under the
stored replay and three labelled alternatives, using the same 76 trials per convention. Points and bars are trial means
and 95% Student-t intervals; annotations give ratios to the stored replay. These alternatives probe assumptions and do
not identify the acquisition settings. Panels B–E describe stimulus or replay variation, not behavioral uncertainty
across mice; temporal-filter delay is not neural latency. No asterisks are used.

### Figure 3. Joint held-out prediction on control trials favoured the tested accumulator among the tested implementations

**(A)** Schematic of the two candidate control-trial pipelines. Both receive reconstructed motion energy and share the
response bounds, fast-response mixture and mapping to choice, response time and no response; the tested distinction is
no leak versus rapid forgetting (leak 20–200 s⁻¹). **(B)** Per-mouse held-out control score, rapid-forgetting minus
accumulator negative log likelihood (NLL), summed over five control-only cross-validation folds. Positive values favour
the accumulator. The sum was 345.7 NLL units; six of ten mice exceeded the prespecified working difference of 10 and
none favoured rapid forgetting by more than 10. Dashed lines show ±10 as a working Monte Carlo-resolution threshold,
not a confidence interval or population test. **(C)** Held-out changes when drift variability (`sv`) or the fast-response
component was removed from the strict accumulator (left), or leak and urgency terms were added (right). Open circles are
mice, diamonds are equal-mouse means and annotations are sums across mice. Positive values favour the strict model over
the named comparator. Removing `sv` or fast guesses cost 1017.8 and 858.1 NLL units, respectively; adding leak, urgency,
or both changed the summed score by −21.3, +25.8 and −33.3. **(D)** Descriptive fit quality of the final all-trial strict
model evaluated on control trials. Points and error bars are equal-mouse observed means ± SEM; lines are equal-mouse
means from 20 fixed-seed simulations per contributing trial. Error-response-time cells enter only when the corresponding
observed mouse-by-coherence cell contains at least five errors. Panel D is in-sample fit quality and is not part of the
held-out comparison in B–C. Simulated repetitions are not biological replicates.

### Figure 4. Randomized signed pulse assignment shifted response direction, and the cumulative response-associated contrast emerged mainly 0.5–2 s after logged onset

**(A)** Directional contrast for positive versus negative scheduled pulse assignment in each mouse,
`(ΔP(right) − ΔP(left))/2`. The equal-mouse mean was 5.84 percentage points (95% Student-t CI 1.80–9.89; raw
two-sided one-sample t-test p = 0.0097; Holm-adjusted p = 0.019). Squares and circles identify UW and UCLA mice;
the group interval uses mice as the unit. **(B)** Changes in right-response, left-response and no-response-by-5-s
probabilities. Thin lines connect the three components from each mouse; coloured points and bars are equal-mouse means
and 95% Student-t intervals. The three components sum to zero within mouse. **(C)** Directional contrasts for positive
pulses versus timing-matched controls and controls versus negative pulses (Holm-adjusted p = 0.004 and 0.393). UW
controls use recorded sham times and UCLA controls use outcome-independent pseudo-onsets; the two comparisons use
different supported cells and do not estimate pulse-sign asymmetry. **(D)** All-scheduled cumulative directional
contrast after logged pulse onset. Thin lines are mice, the emphasized line is their equal-weight mean and the band is
the pointwise, not simultaneous, 95% Student-t interval. The endpoint was 5.80 percentage points at 4.58 s. The analysis
used 10,281 scheduled pulse trials in 717 supported cells, retaining 118 responses before logged onset and 1,709 trials
with no response by 5 s. Cells used smaller-arm weights normalized within mouse; mice were equal-weighted. The curve
locates emitted responses and is not a neural latency, memory kernel or confirmatory timing/primacy test. No asterisks
are used.

### Figure 5. The tested model-and-input pipeline predicted a different temporal pulse profile from the observed response contrast

**(A)** Ten-mouse mean cumulative directional contrast on the common historical model-input rows: observed responses
and primary-pipeline predictions at the original gain of one, stored joint-objective gain and choice-optimizing gain.
Control parameters were fixed. **(B)** Changes within 0–0.5, 0.5–1, 1–2 and 2–4.58 s after onset. Points and bars are
equal-mouse means and 95% Student-t intervals. Observed changes were +0.39, +3.21, +2.13 and +0.12 percentage points;
the choice-gain predictions were +3.00, +4.72, +0.25 and −2.98. A negative late increment is a partial decline from an
earlier cumulative contrast, not an overall reversal of the pulse effect. **(C)** In-sample choice and joint-objective
profiles for PSUIM6 and PSUIM7 over gains 0–10. Each curve is shown as ΔNLL from its minimum divided by its displayed
range so both objectives remain visible; normalization does not change the optima. Solid lines/circles denote choice
and dashed lines/squares the joint objective. Joint-to-choice optima were 2.4 to 7.0 for PSUIM6 and 1.4 to 4.0 for
PSUIM7. These mice were selected for dense response-time coverage, not as representative examples. **(D)** Held-out NLL
change when fold-specific gain was chosen for choice rather than the joint objective. Negative choice-term values are
improvements; positive remaining-objective values are costs. Values are summed over the five held-out folds and averaged
over available simulation seeds. Filled markers identify the two mice meeting the prespecified tradeoff criterion:
choice improved by 10.40 and 10.01 NLL units while the remaining objective worsened by 96.01 and 106.61 in PSUIM6 and
PSUIM7. Panels A–B are descriptive group comparisons rather than paired observed-minus-predicted tests; C is in-sample,
and the QMLE changes in D do not have a calibrated inferential threshold. Historical label omissions remain unchanged,
and overlays use only the observed–predicted common intersection.
