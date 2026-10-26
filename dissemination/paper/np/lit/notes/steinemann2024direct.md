# steinemann2024direct

Steinemann N, Stine GM, Trautmann E, Zylberberg A, Wolpert DM, Shadlen MN (2024). *Direct observation of the neural computations underlying a single decision*. **eLife** 12:RP90859. Version-of-record DOI: 10.7554/eLife.90859.3; PubMed records canonical DOI 10.7554/eLife.90859; PMID: 39422555; PMCID: PMC11488853. Access: eLife/Crossref versioned record and primary full text via Europe PMC.

## Study and fit/test structure

| Item | Primary-source detail |
|---|---|
| Species / task | Two rhesus macaques; reaction-time random-dot-motion direction discrimination by saccade, with Neuropixels recordings from LIP. Locator: Results, Figure 1A; Methods, "Main task." |
| Behavioural fit | Neurally inspired racing drift-diffusion model fit separately to each session's choice–RT data. The model generated full RT distributions after convolution with a non-decision-time distribution; Figure 1B displays the choice and mean-RT summaries with bounded-model fits. Locator: Results, Figure 1B; Methods, "Behavioral analyses." |
| Pulse | On approximately half of trials, a weak 100 ms pulse was added at a random time 0.1–0.8 s after motion onset; strength was ±3.2% for monkey J and ±4.0% for monkey M. Locator: Methods, "Main task." |
| Outcomes | Behavioural choice and RT; single-trial LIP drift/diffusion signals and their leverage on choice and RT. Pulse effects on choice and mean RT are shown in Figure 1—figure supplement 1. |
| Held-out pulse prediction? | **No.** Cross-validation in the article concerns neural decoding/coding directions. The paper does not report a behavioural model trained on no-pulse controls and evaluated on pulse trials; the pulse supplement is an empirical within-task support analysis. |

## Key findings and relevance

- The bounded drift-diffusion model described monkey choice and RT. Locator: Results, Figure 1B.
- Random weak pulses biased choice and RT equivalently to shifting the functions by ±1.4% coherence, and pulse effects on choice persisted toward the response. Locator: Figure 1—figure supplement 1.
- A low-dimensional LIP population signal exhibited deterministic drift plus stochastic diffusion and covaried with trial-to-trial choice and RT. Locator: Abstract; Results, Figures 2–5.
- **Relevance:** Closest recent neural positive evidence for the computation targeted by the tested accumulator. It requires the paper to frame its mouse finding as a model-and-input transfer failure rather than evidence against accumulation generally.

## Interpretation limits

This is substantially stronger neural evidence than behaviour alone, but it tests a different preparation and weak perturbation. Pulse trials were interleaved within the dataset rather than held out as a strong-input transfer condition. The pulse panel was adapted from Stine et al. 2023, and the paper's primary claim is about single-trial LIP population dynamics, not quantitative pulse generalization.

**Paraphrase for the paper:** Macaque LIP population activity carried a drift-diffusion-like signal linked to choice and RT, with randomized weak pulses providing convergent within-task support rather than a frozen control-model transfer test.
