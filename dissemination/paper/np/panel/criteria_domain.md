<!-- np-contract
stage: S6 ; section: panel-domain ; agent: np-domain-reviewer ; version: v1
thesis: "Joint held-out prediction on control trials favoured the tested accumulator over a rapid-forgetting implementation, but randomized motion pulses exposed a failure of the tested model-and-input pipelines to generalize to transient strong evidence."
claims: C001, C003, C004, C005, C006, C007, C008, C009, C010, C011, C012, C013, C014, C015, C016, C017, C018, C019, C020, C021
numbers:
sources: stine2020differentiating, hyafil2023temporal, huk2005neural, stine2023termination, steinemann2024direct, parespujolras2026glimpses, zhou2009time, tsetsos2012timevarying, carland2016evidence, yates2017functional, okazawa2018psychophysical, marques2018mousev1, pinto2018visualpulses, odoemene2018visual, koay2020amplitude, caballero2022rt, you2022dynamics
-->
# Criteria commitment: S6 domain review

Sources used before commitment: locked `np/spine.md`, `np/config.md`, `np/lit/gaps.md`,
`np/lit/matrix.md`, the neuropaper S6 workflow and review rubric. The rendered manuscript, draft
sections, source ledger and paper notes were not read before this commitment.

## Scope and review boundary

This is a working simulated field-expert review for an author-directed internal panel, not an editorial
decision. I will assess the mouse dynamic-visual decision context, literature coverage and
representation, novelty, relative model claims, pulse contribution and physiological scope. I will not
independently adjudicate the detailed statistical implementation assigned to the statistics reviewer,
except where it changes a biological or model interpretation. Unpublished material remains local;
public scholarly APIs may be used only for generic citation verification or bounded recent-literature
searches, never with unpublished manuscript text as a query.

## Precommitted criteria

| ID | Criterion | What I will look for | P0 if | P1 if |
|---|---|---|---|---|
| D1 | Thesis and scope fidelity | The paper consistently describes a relative comparison of specified model-and-input pipelines, followed by an out-of-condition pulse transfer failure. | It claims accumulation is proved, every non-integrating strategy is excluded, or the mismatch localizes to decision dynamics. | Qualifiers are present but emphasis invites a broader mechanistic reading than the spine permits. |
| D2 | Mouse-field context | Continuous mouse RDK psychophysics, dynamic/discrete visual accumulation, visual pulse tasks and mouse choice/RT diffusion modelling are acknowledged as established. | The work is called the first mouse dynamic-visual, RDK, pulse, accumulation or choice/RT modelling study. | Relevant mouse precedents are omitted or described so vaguely that the bounded contribution appears broader than it is. |
| D3 | Bounded novelty | Novelty is restricted to the searched conjunction: continuous noisy RDK, randomized signed pulses and a frozen control-only pipeline tested jointly against choice, response probability and RT outcomes. | The manuscript asserts priority beyond what the bounded search establishes or ignores a verified study containing the same decisive conjunction. | The distinction from the closest prior studies is accurate but unclear, buried or undersold. |
| D4 | Relative model interpretation | The accumulator result is explicitly relative to the tested 20–200 s^-1 rapid-forgetting approximation and fitted alternatives, with good held-out prediction separated from unique biological identification. | The operational rapid-forgetting model is equated with all extrema/non-integration models, or CV preference is treated as proof of the true neural computation. | The main relative comparison is technically qualified but colloquial phrasing elsewhere weakens the boundary. |
| D5 | Alternative model landscape | The discussion recognizes leak/competition, extrema/snapshot policies, urgency or collapsing policies, sensory filtering/adaptation, bound crossing/commitment, strategic reweighting, and response/nondecision processes as distinct alternatives. | A viable alternative is declared ruled out by an analysis that did not test it, or a pipeline failure is assigned to one stage without evidence. | Alternatives are listed but not connected to the observed control-versus-pulse pattern or to a discriminating remedy. |
| D6 | Pulse contribution | Randomized assignment supports a behavioural directional effect; predictive failure constrains the fitted pipelines; neither result alone establishes primacy, an integration kernel or neural memory duration. Failed gates, low sensitivity and the withheld timing test remain visible. | Inconclusive/underpowered pulse strategy or timing tests are used as positive evidence for equivalence, flat weighting, primacy/recency, or absence of a mechanism. | The distinction between the robust behavioural effect, failed generalization and unresolved mechanism is not sufficiently prominent. |
| D7 | Temporal and physiological restraint | Pulse-aligned cumulative response timing is treated as response-associated and compatible with sensory, decision, commitment and motor stages; replay is not presented as a physical display recording. | Response latency is interpreted as neural integration time, sensory persistence or a localized physiological process without direct measurement. | The caveat exists but mechanistic verbs or figure prose still imply localization. |
| D8 | Cross-species interpretation | Human, rat and macaque evidence is used as context or counter-evidence, not direct validation of the mouse pipeline; task, response mode, pulse strength and neural-measurement differences are explicit where consequential. | Cross-species findings are represented as direct replication or contradiction without the preparation differences that determine interpretation. | Species/task bridges are accurate but incomplete around the closest comparator. |
| D9 | Must-cite closest priors | At minimum the argument is tested against Stine 2020, Hyafil 2023, Huk 2005, Stine 2023, Steinemann 2024, and the current Pares-Pujolras record; mouse novelty is tested against Marques 2018, Pinto 2018, Odoemene 2018, Koay 2020, Caballero 2022 and You 2022. Zhou 2009, Tsetsos 2012, Carland 2016, Yates 2017 and Okazawa 2018 should anchor sensitivity and pipeline-stage alternatives where those claims appear. | A missing decisive prior makes a central novelty or mechanistic claim false or materially unsupported. | A key prior is absent where it would materially sharpen attribution, scope or contrast but does not overturn the thesis. |
| D10 | Citation fidelity | Spot-check at least eight citations across closest positive, counterexample, mouse-precedent, model-identification and physiological-alternative roles against their notes and verified identifiers. Species, task, method, pulse regime and stated result must align. | A citation is nonexistent, unverified, or materially misrepresented in support of a central claim. | A real citation supports only a narrower statement, or a secondary source is used where an already-verified primary source is available. |
| D11 | Recent-literature challenge | Conduct bounded generic searches for 2024–2026 work on mouse visual evidence accumulation/pulses, motion-pulse decision modelling and control-to-perturbation predictive transfer. Any proposed citation must have a verified DOI/PMID or other stable public record; absence is reported as search-bounded, never universal. | A verified recent paper directly defeats the stated novelty and the manuscript makes an unqualified novelty claim. | A relevant recent comparator changes framing or deserves citation but does not invalidate the bounded contribution. |
| D12 | Proportionate remedy and decision | Every issue will give an exact location, evidence, consequence and smallest adequate remedy; new experiments/analyses will be requested only if essential to a central claim, with narrowing or limitation language offered first. | The central thesis cannot be made evidence-bounded without a new plan, integrity repair or spine change. | A bounded citation, wording, comparison or limitation repair is needed before the paper is field-ready. |

## Decision rule

- **PASS / simulated accept or minor revision:** no P0; the bounded novelty and relative-mechanism framing
  survive; only optional or local clarification remains.
- **REVISE / simulated major revision:** one or more P1 issues materially affect field interpretation,
  novelty, citation coverage or physiological scope but have bounded remedies within the existing study.
- **BLOCK / simulated reject:** a P0 defeats the central framing, exposes a central unsupported or false
  field claim, or requires a different scientific plan. The wording remains simulated advice to the
  author, not an editor's decision.

