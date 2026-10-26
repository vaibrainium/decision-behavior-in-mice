# stine2023termination

Stine GM, Trautmann EM, Jeurissen D, Shadlen MN (2023). *A neural mechanism for terminating decisions*. **Neuron** 111:2601–2613.e5. DOI: 10.1016/j.neuron.2023.05.028; PMID: 37352857; PMCID: PMC10565788. Access: primary full text via Europe PMC plus PubMed metadata.

## Study and fit/test structure

| Item | Primary-source detail |
|---|---|
| Species / task | Two rhesus macaques; free-response random-dot-motion direction discrimination reported by saccade. Locator: Results, Figure 1A; STAR Methods, "Perceptual decision-making task." |
| Behavioural fit | Bounded accumulation model fit to choice and RT. For Figures 1 and S1, the parsimonious flat, symmetric-bound model maximized a combined likelihood of choice data and mean RTs. Locator: Results, Figure 1B; STAR Methods, "Behavioral analyses," Equations 2–5. |
| Pulse | On about half the trials, a randomly signed 100 ms coherence increment/decrement occurred at a random onset from 0.1–0.8 s. Strength was 4.0% coherence for monkey M and 3.2% for monkey J. Locator: Results paragraph accompanying Figure S1; STAR Methods, "Perceptual decision-making task." |
| Outcomes | Choice and mean RT in the parsimonious behavioural fit; choice, RT and LIP/SC firing-rate pulse effects in separate analyses. Locator: Figure S1; Figures 2C–D; STAR Methods, Equation 9. |
| Held-out pulse prediction? | **No genuine held-out pulse test is reported.** The methods do not specify fitting the behavioural model only to no-pulse trials and then evaluating a frozen model on pulse trials. The pulse manipulation is randomized and informative, but its persistence is used as convergent within-task evidence. |

## Key findings and relevance

- Weak pulses affected choices and RT; early pulses affected choices made nearly one second later. Locator: Results paragraph introducing Figure S1.
- Pulse effects on LIP activity persisted for several hundred milliseconds, whereas SC effects were more transient. Locator: Results, Figures 2C–D.
- Single-trial LIP population dynamics approximated drift diffusion, while SC showed bursts; SC inactivation slowed and biased decisions and prolonged LIP buildup. Locator: Abstract; Results, Figures 3–6.
- **Relevance:** Strong positive accumulation precedent combining randomized pulses, choice/RT modelling and neural recording. It is the closest contrast to the mouse pipeline's failed pulse generalization.

## Interpretation limits

The authors' pulse argument combines behavioural persistence with neural evidence; it is not a prospective out-of-condition prediction exercise. Pulse strength was weak and individually fixed, species and report modality differ, and the main causal manipulation concerns SC termination rather than sensory pulse processing. The study limitations section also notes that the LIP–SC association is correlational and that the recorded LIP populations incompletely represent the full signal.

**Paraphrase for the paper:** In macaques, randomized weak motion pulses had persistent behavioural and LIP consequences alongside drift-diffusion-like population dynamics, but pulse trials were not presented as a held-out test of a model trained only on ordinary trials.
