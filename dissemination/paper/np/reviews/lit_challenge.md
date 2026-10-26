<!-- np-contract
stage: S2 ; section: literature ; agent: np-devils-advocate ; version: v1
thesis: "Joint held-out prediction on control trials favoured the tested accumulator over a rapid-forgetting implementation, but randomized motion pulses exposed a failure of the tested model-and-input pipelines to generalize to transient strong evidence."
claims: C010, C011, C012, C013, C014, C015, C016, C017, C018
numbers:
sources: stine2020differentiating, hyafil2023temporal, huk2005neural, zhou2009time, carland2016evidence, yates2017functional, okazawa2018psychophysical, steinemann2024direct, stine2023termination, parespujolras2026glimpses_v3
-->
# Literature challenge

## Verdict

No source found closes the narrow predictive-generalization gap. The present scoop verdict is nevertheless not ready for G2 approval because two of the closest pulse-and-model studies are absent and one recent record is tied to an obsolete preprint note. The paper's defensible contribution is a quantitative failure of a specified control-selected pipeline under stronger transient evidence, not the first use of pulses, joint choice/RT modelling, or evidence-accumulation tests.

## Independent public search log

Only public topic strings and identifiers were sent to search services. No unpublished text, result or project-specific phrase was submitted.

| # | Query or retrieval | Source checked | Outcome |
|---|---|---|---|
| DA1 | `"motion pulse" evidence accumulation model choice reaction time prediction` | Public web index; primary-source results opened | Recovered Wong et al. 2007 and the 2024 eLife macaque paper below; no duplicate of the locked transfer test. |
| DA2 | `"random dot motion" pulse mice evidence accumulation model response time` | Public web index | Recovered pulse-based mouse/rat tasks, but no continuous-motion control-to-strong-pulse generalization analysis matching the locked claim. |
| DA3 | `perceptual decision model out-of-distribution generalization pulse evidence accumulation` | Public web index | No primary perceptual-decision paper using this terminology closed the gap; machine-learning OOD surveys were excluded. |
| DA4 | `2025 2026 motion evidence pulse decision model preprint` | Public web index | Recovered recent intermittent-evidence work; no matching held-out transfer study. |
| DA5 | Exact official record `10.7554/eLife.90859.3` | eLife Version of Record | Steinemann et al. 2024 fitted bounded drift diffusion to macaque choice/RT data and used randomized weak pulses as additional support for integration. Missing from the ledger. |
| DA6 | `Gabriel Stine 2023 motion pulse decision termination random dot motion`; exact DOI `10.1016/j.neuron.2023.05.028` | PubMed and open Neuron/PMC full text | Stine et al. 2023 fitted choice/RT data, used randomized weak pulses, reported effects nearly one second later and pulse persistence in LIP, and claimed support for accumulation. Missing from the ledger. |
| DA7 | Exact official record `10.7554/eLife.107980.3` | eLife Reviewed Preprint v3, 2026-09-18 | Parés-Pujolràs et al. now has a v3 reviewed preprint with stronger assessment and revised modelling; the current bioRxiv-level note is stale. |

## Ranked challenges

| Rank | Challenge | Evidence and consequence | Resolution |
|---|---|---|---|
| **MAJOR 1: closest positive pulse precedents are missing** | Stine et al. 2023 and Steinemann et al. 2024 use randomized motion pulses in a reaction-time random-dot task, fit bounded drift-diffusion models to choices and RTs, and interpret pulse effects as support for integration. The latter is an eLife Version of Record; both use closely related macaque data. | These studies do not appear in `sources.csv`, the matrix or the scoop table. They do not report the present held-out strong-pulse failure, but they are closer than several retained general methods papers and create the most informative contrast: the same broad pulse logic supported a primate model while the current mouse pipeline failed. | Add, verify and summarize both primary sources. Put them in the closest-work table and Discussion comparison. State exactly whether their behavioral models were fit to all trials or evaluated out of condition; do not imply that pulse persistence alone settled mechanism. |
| **MAJOR 2: the recent-version sweep is stale** | The ledger verifies the 2025 bioRxiv DOI for Parés-Pujolràs et al. while noting only later versions. The official record is now eLife Reviewed Preprint v3, DOI `10.7554/eLife.107980.3`, dated 2026-09-18. It reports transient local pulse processing, sustained downstream motor evidence, bounded modelling and viable reweighting alternatives. | The current note says no published version was found and excludes the work from the matrix and scoop verdict. That is factually obsolete on the current search date. The paper is directly relevant to the spine's unresolved sensory/decision/response-stage account. | Replace or supersede the bioRxiv row with the official v3 metadata, refresh the full-text note, and add it as a recent comparator. It narrows mechanistic interpretation but does not close the control-to-pulse generalization gap. |
| **MAJOR 3: the gap is defined by an overly bespoke conjunction** | “A complete model-and-input pipeline selected on ordinary continuous motion trials and then evaluated...” risks sounding like distinctiveness by procedural exclusion. “Complete” is also inconsistent with unresolved display timing and omitted sensory/response processes. | Prior studies already combine joint choice/RT fits, randomized pulses and mechanistic models. What remains distinctive is quantitative transfer failure under a strong perturbation, with censoring and sensitivity reported, not possession of every pipeline component. | Replace “complete” with “specified” and state the scientific gap: whether joint predictive adequacy under ordinary evidence generalizes quantitatively to strong transient evidence. Add a comparison table showing fit condition, perturbation strength, outcomes predicted and whether perturbation predictions were genuinely held out. |
| **MAJOR 4: counterevidence is represented, but neural positive evidence is underweighted** | The synthesis fairly includes leak, urgency, sensory dynamics and model mimicry. It gives less weight to recent neural evidence for drift-diffusion and pulse persistence, especially Stine 2023 and Steinemann 2024. | This imbalance makes the gap read as though model failure is the dominant recent result. A hostile reviewer can cite these papers immediately and argue that the mouse result may reflect replay or task implementation rather than accumulation failure. | Present the recent macaque work as strong positive evidence in another preparation, then use the species/task/input difference to motivate pipeline validation rather than universal mechanism rejection. |
| **MINOR 1: C013 is categorical and partly tautological** | C013 says perturbations distinguish implementations “only when” predictions remain separable. Zhou, Hawkins and Tsetsos show regime-dependent separability, but they do not establish a universal necessary condition across every perturbation paradigm. | The intended methodological point is sound, but “only when” overstates source scope. | Revise to: “The ability of time-varying perturbations to distinguish decision-model implementations depends on prediction separability under the tested noise, timing and response regime.” |
| **MINOR 2: C018 turns a validation recommendation into an absolute rule** | Wiecki and Lüken demonstrate recovery and identifiability problems in specified DDM/LBA settings. They do not prove that every accumulation estimate is uninterpretable without a formal recovery study. | The present project did run recovery, so narrower wording loses nothing. | Revise “require recovery” to “should be accompanied by recovery or identifiability checks before mechanistic interpretation,” retaining model/task scope. |

## Claim-fidelity review, C010-C018

| Claim | Verdict | Reason |
|---|---|---|
| C010 | Supported with scope | Stine 2020, Tsetsos, Cisek and Okazawa support model mimicry and composite temporal weighting. Keep “tested strategies.” |
| C011 | Supported | Stine 2020 and standard diffusion work support joint choice/RT constraints as stronger than accuracy alone; this is not unique identification. |
| C012 | Supported with access caveat | Huk, Kiani and Tsetsos support timing/commitment effects; Carland supports policy dependence but the retained note relies on the abstract. Avoid details beyond that abstract. |
| C013 | Revise wording | The source set supports regime dependence, not the current universal “only when” wording. |
| C014 | Supported with preparation limit | Yates supports sensory generation of early weighting inherited by a perfect downstream integrator; it does not explain the current late mouse response contrast. |
| C015 | Supported | Hyafil's full text supports the multi-dataset relative result and explicitly does not exhaust non-integration policies. |
| C016 | Supported | The cited diffusion literature supports joint accuracy/RT modelling, not validation of this likelihood. |
| C017 | Supported | Adelson and Bergen support the filter computation only, not replay fidelity. |
| C018 | Revise strength | Recovery/identifiability checks are strongly motivated; “should be accompanied by” is more faithful than an unconditional “require.” |

## Scoop verdict

**The exact gap survives, provisionally.** Stine et al. 2023 and Steinemann et al. 2024 come closest: they combine random-time motion pulses, choice/RT fits and positive accumulation interpretations, but the inspected reports do not establish a separately held-out test in which a control-selected full response-distribution pipeline fails on strong pulse trials. Parés-Pujolràs et al. v3 separates transient local processing from sustained downstream maintenance in a different two-pulse delayed-response task. None duplicates the present combination of continuous mouse motion, no-response outcomes, strong signed perturbations, failed predictive gates and explicit sensitivity limits.

The contribution must remain narrow: **joint predictive success under ordinary evidence did not transfer to a strong transient perturbation in the tested pipeline.** The literature package should not claim priority until the three missing/current-version records above are integrated and the comparison table confirms the fit-versus-test distinction.

## Required revision before G2

1. Add and verify Stine et al. 2023 and Steinemann et al. 2024.
2. Refresh Parés-Pujolràs et al. to eLife Reviewed Preprint v3.
3. Revise C013 and C018 as above.
4. Replace “complete pipeline” with “specified pipeline” and add a fit-condition versus perturbation-test comparison.

BLOCKER: G2 should not be approved until these bounded literature corrections are incorporated and re-audited.
