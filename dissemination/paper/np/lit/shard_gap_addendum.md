<!-- np-contract
stage: S2 ; section: gap_addendum ; agent: np-librarian ; version: v1
thesis: "Joint held-out prediction on control trials favoured the tested accumulator over a rapid-forgetting implementation, but randomized motion pulses exposed a failure of the tested model-and-input pipelines to generalize to transient strong evidence."
claims: C010, C011, C012, C014
numbers: none
sources: stine2023termination, steinemann2024direct, parespujolras2026glimpses
-->

# Gap literature addendum: three challenge records

Access date for every lookup: **2026-10-24**. Only exact public identifiers and public primary-source records were queried; no unpublished project text was submitted.

## Lookup log

| # | Public source | Exact lookup | Filter | Hits | Screened | Kept |
|---|---|---|---|---:|---:|---:|
| A1 | PubMed E-utilities | `10.1016/j.neuron.2023.05.028[doi]` | exact DOI | 1 | 1 | 1 |
| A2 | Europe PMC full-text API | `PMC10565788/fullTextXML` | Stine et al. 2023 primary full text | 1 | 1 | 1 |
| A3 | Crossref REST | `works/10.7554/eLife.90859.3` | exact versioned DOI | 1 | 1 | 1 |
| A4 | PubMed E-utilities | `PMID 39422555` | exact PMID | 1 | 1 | 1 |
| A5 | Europe PMC full-text API | `PMC11488853/fullTextXML` | Steinemann et al. 2024 Version of Record | 1 | 1 | 1 |
| A6 | eLife official record | `reviewed-preprints/107980v3` and `reviewed-preprints/107980v3.xml` | exact v3 DOI `10.7554/eLife.107980.3` | 1 | 1 | 1 |

## Fit-versus-test comparison

| Record | Fit condition | Pulse condition / strength | Outcomes modelled | Were pulse predictions genuinely held out? |
|---|---|---|---|---|
| Stine et al. 2023 | Bounded accumulation fit to monkey choice and mean RT; the Figure 1/S1 fit maximized a combined likelihood for choice data and mean RTs. The text does not report a no-pulse-only training split. | Interleaved on about half of trials; 100 ms; randomly signed and timed; 4.0% coherence in monkey M and 3.2% in monkey J; onset 0.1–0.8 s. | Choice and mean RT in the parsimonious behavioural fit; pulse effects on choice, RT and LIP/SC activity were also analysed. | **No.** Pulses were randomized evidence manipulations and supplied empirical support, but the paper does not report fitting on no-pulse controls and prospectively evaluating a frozen model on pulse trials. |
| Steinemann et al. 2024 | A racing bounded drift-diffusion model was fit per session to choice–RT data; neural coding directions/decoders were analysed with cross-validation for neural questions. | Same macaque dataset/manipulation: 100 ms on about half of trials; randomly timed 0.1–0.8 s; ±3.2% or 4.0% coherence for monkeys J and M. | Behavioural choice and RT; single-trial LIP signals, neural leverage on choice and RT. Pulse choice/RT effects are shown descriptively in Figure 1—figure supplement 1. | **No.** Neural decoder cross-validation is not a held-out pulse-generalization test, and the article does not report a control-only behavioural fit evaluated on pulse trials. |
| Parés-Pujolràs et al. 2026 v3 | Three-parameter bounded model fit separately by experiment to grand-averaged accuracy for all single- and two-pulse conditions; alternative models were likewise fit to all accuracy conditions. | Human intermittent-evidence task; one or two 200 ms motion epochs separated by specified gaps; individualised low/high coherences (group means 19.82–44.73% across experiment/level). | Accuracy only in the fitted decision models; CPP and motor-beta patterns were simulated from the accuracy-fitted model and compared qualitatively with EEG. RT was not the modelled decision outcome. | **No.** The pulse conditions constituted the fitting dataset; EEG simulations were not an untouched pulse test. |

## Addendum conclusion

Stine et al. and Steinemann et al. are the closest positive precedents because randomized weak pulses accompanied bounded choice/RT fits and macaque neural evidence for persistent accumulation. They materially narrow novelty, but do not perform the paper's control-only-fit to separately evaluated strong-pulse transfer test. Parés-Pujolràs v3 is a relevant counter/comparator because it localizes transient versus sustained signals and now compares bounded with reweighting alternatives; all decision models were fit to the pulse-task accuracy data, so it also does not close the predictive-generalization gap. These distinctions support a preparation- and pipeline-specific claim, not priority for motion pulses or a universal failure of accumulation.
