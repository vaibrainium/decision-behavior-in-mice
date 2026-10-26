VERDICT: REVISE

<!-- np-contract
stage: S6 ; section: panel-domain ; agent: np-domain-reviewer ; version: v1
thesis: "Joint held-out prediction on control trials favoured the tested accumulator over a rapid-forgetting implementation, but randomized motion pulses exposed a failure of the tested model-and-input pipelines to generalize to transient strong evidence."
claims: C001, C003, C004, C005, C006, C007, C008, C009, C010, C011, C012, C013, C014, C015, C016, C017, C018, C019, C020, C021
numbers: N001, N004, N005, N006, N016, N024, N025, N026, N027, N030, N034, N035, N036, N051, N052, N053, N054, N055, N056, N057, N058, N059, N063, N064, N065, N066, N108
sources: stine2020differentiating, hyafil2023temporal, huk2005neural, stine2023termination, steinemann2024direct, parespujolras2026glimpses, zhou2009time, tsetsos2012timevarying, carland2016evidence, yates2017functional, okazawa2018psychophysical, marques2018mousev1, pinto2018visualpulses, odoemene2018visual, koay2020amplitude, chakravarty2025cross, caballero2022rt, you2022dynamics
-->

# S6 domain review: mouse dynamic visual decisions and evidence accumulation

Criteria file: `np/panel/criteria_domain.md`  
Review type: working simulated field-expert assessment for the author; not an editorial decision  
Simulated decision: **MAJOR REVISION**, limited to three bounded interpretive/reporting repairs; no new
analysis or experiment is needed for the domain issues below.

## Overall assessment

The manuscript makes a useful and defensible contribution: it separates a relative, within-cohort
control-model comparison from a genuinely out-of-condition test under strong transient evidence. The
mouse novelty statement is unusually careful. It explicitly acknowledges earlier continuous-RDK,
discrete visual-evidence and visual choice/RT work, then limits the gap to the conjunction not found in
the bounded search. The pulse contribution is also appropriately partitioned into a randomized
directional behavioural effect, a failure of the specified prediction pipelines and an inconclusive
timing/strategy programme. The text does not treat the weak procedure as evidence of equivalence or a
flat kernel.

The interpretation is physiologically restrained throughout the Results and Discussion: response-
associated timing is not called a neural latency or memory duration, reconstructed motion energy is
not presented as a display recording, and sensory, commitment, decision, nondecision and response
accounts remain open. The recent macaque pulse/LIP results are represented as stronger positive
accumulation evidence in another preparation rather than dismissed as conflicting data. These are
important strengths.

The remaining problems are bounded but material. The title assigns the limitation to an evidence-
accumulation model even though the manuscript's own supported conclusion is about a complete model-
and-input pipeline. Two already-verified recent comparators are absent at the exact points where they
would sharpen the mouse/policy and physiological-stage framing. Finally, the rapid-forgetting time
constants and Euler step are printed without units, obscuring the very time-scale distinction that
defines the comparator.

## Criterion results

| ID | Result | Evidence |
|---|---|---|
| D1 | partly met | Lines 15–108 consistently preserve pipeline-level scope, but the title at line 1 narrows the failure to an evidence-accumulation model. |
| D2 | met | Line 19 positively cites established mouse RDK, discrete visual-evidence and visual choice/RT precedents and rejects broad mouse priority. |
| D3 | met | Line 19 uses bounded-search language and defines the preparation-specific conjunction; the literature audit found no retained duplicate. |
| D4 | met | Lines 49–57 and 98–104 repeatedly limit the result to the tested implementations and do not equate rapid forgetting with all non-integration. |
| D5 | met | Lines 15–17 and 100–106 retain leak, urgency, sensory, commitment, policy and response-stage alternatives. |
| D6 | met | Lines 59–94 distinguish randomized behavioural redirection, failed pipeline transfer, low sensitivity and the unrun confirmatory test. |
| D7 | met | Lines 37–45, 71–81 and 102–106 avoid neural-latency, memory-duration and processing-stage claims. |
| D8 | met | Lines 17 and 100 distinguish macaque weak-pulse neural evidence from the mouse strong-pulse pipeline test. |
| D9 | partly met | Core priors are cited, but the verified Parés-Pujolràs 2026 and Chakravarty 2025 comparators are absent from the relevant prose. |
| D10 | met | Sixteen citations were spot-checked across closest priors, mouse precedents and alternatives; species, task, method and result scopes match their notes. |
| D11 | met with search limit | Bounded 2024–2026 Europe PMC and OpenAlex searches found no study duplicating the held-out transfer test. One 2026 preprint lead was excluded from requested additions because only metadata/abstract, not full source fidelity, was checked. |
| D12 | met | Each issue below has a manuscript location and a wording/citation/unit repair; none requires new data or an expanded study. |

## Issues

| # | Severity | Exact location | Problem | Evidence / why it matters | Corroboration-ready phrasing | Bounded remedy |
|---:|:---:|---|---|---|---|---|
| 1 | P1 | Title, `manuscript.md:1`; contrast `:81`, `:98`, `:104`, `:108` | “limits of an evidence-accumulation model” attributes the transfer failure to the decision model more narrowly than the supported object. The predictions depend jointly on reconstructed input, temporal filtering, decision dynamics, likelihood and response mapping. | The manuscript explicitly states that the descriptive mismatch does not establish failure of the accumulator itself (`:81`) and that sensory, decision and response stages remain unresolved (`:98`, `:104`). A field reader sees the title before those safeguards. | “The pulse data expose a limit of the tested model-and-input pipeline; they do not isolate the accumulator dynamics as the failed component.” | Retitle with pipeline-level or prediction-level language. One faithful option is **“Brief motion pulses expose limits of a control-fitted model-and-input pipeline in mice.”** If “evidence accumulation” is retained for discoverability, explicitly modify “predictions” or “pipeline,” not the biological mechanism. |
| 2 | P1 | Mouse context, `manuscript.md:19`; model-identification/physiology context, `:100–102` | Two recent, already-verified records that sharpen the paper's field position are in `sources.csv` and the literature matrix but not cited in the manuscript: Chakravarty et al. 2025 and Parés-Pujolràs et al. 2026. | Chakravarty uses a shared repeated-pulse task across mice, rats and humans and reports species/policy-dependent strategies; it reinforces that mouse visual pulse accumulation and response-policy variation are established. Parés-Pujolràs combines separated motion glimpses, EEG and bounded/reweighting models; it directly supports the manuscript's key physiological restraint that transient local pulse processing can coexist with sustained downstream evidence. Neither study used a frozen control-only joint choice/RT/no-response pulse-transfer test, so the bounded novelty survives. | “Recent pulse-task work likewise shows that inferred strategy depends on species and policy, while human EEG separates transient pulse-local activity from a sustained downstream representation; neither study performed the present frozen control-to-pulse transfer test.” | Add `[@chakravarty2025cross]` near the mouse discrete-pulse context at line 19 or policy discussion at line 100, and add a one-sentence, explicitly cross-species comparison using `[@parespujolras2026glimpses]` at lines 100–102. Preserve reviewed-preprint status and do not imply either source validates the mouse mechanism. **Missing decisive-literature count: 2.** |
| 3 | P1 | Rapid-forgetting Methods, `manuscript.md:178`; Figure 3A/legend context `:314–318` | The comparator is reported as “nominal time constants 5-50; Euler dt=1” without units. This makes the physiological meaning of the rapid-forgetting range ambiguous and weakens reproducibility. | The registered rate is 20–200 s⁻¹, corresponding to nominal continuous time constants of 5–50 ms; the analysis plan states that the simulator uses a 1 ms Euler step. These are implementation scales, not biological time constants. | “The operational comparator used leak rates of 20–200 s⁻¹ (nominal time constants 5–50 ms) with a 1-ms Euler step; these values define the tested approximation rather than a physiological estimate.” | Add `ms` to both the nominal time-constant range and Euler step, and retain the existing statement that this is an operational rapid-forgetting approximation rather than an exact extrema detector. |

P0: **0** · P1: **3** · P2: **0**

## Citation-fidelity spot checks

| Source | Manuscript use | Domain ruling |
|---|---|---|
| `stine2020differentiating` | Non-integration can mimic accuracy/kernels; joint choice/RT is more constraining. | Supported; correctly framed as improved discrimination, not unique identification. |
| `hyafil2023temporal` | Integration outperformed tested extrema/snapshot variants across discrete-sample datasets. | Supported; the manuscript preserves the source's non-exhaustive-candidate limitation. |
| `huk2005neural` | Pulse effects depend on timing/commitment and include choice, RT and LIP consequences. | Supported; macaque neural evidence is not imported into mouse behaviour. |
| `stine2023termination` | Weak randomized macaque pulses had persistent behavioural/LIP effects. | Supported; accurately distinguished from a held-out no-pulse-trained prediction test. |
| `steinemann2024direct` | Drift-diffusion-like LIP population evidence plus weak pulse effects. | Supported; neural decoder cross-validation is not misrepresented as behavioural pulse transfer. |
| `marques2018mousev1` | Mouse continuous RDK precedent. | Supported; fixed-duration task differences remain clear. |
| `pinto2018visualpulses` | Mouse discrete visual-tower accumulation. | Supported; not called an embedded continuous-RDK perturbation. |
| `odoemene2018visual` | Mouse stochastic visual-flash accumulation. | Supported; fixed-duration discrete evidence is distinguished from the current task. |
| `koay2020amplitude` | Cortical responses during mouse pulsatile evidence accumulation. | Supported; the cues are correctly treated as the task evidence stream. |
| `you2022dynamics` | Mouse visual choice/RT analysis. | Supported; the source is not represented as continuous RDK. |
| `caballero2022rt` | Mouse visual diffusion modelling of choices and response latency. | Supported within abstract-level access; no stronger detail is asserted. |
| `zhou2009time` | Perturbation discrimination depends on realistic noise and delay. | Supported; manuscript wording is appropriately conditional. |
| `carland2016evidence` | Pulse efficacy varies with decision policy and can favour leak/urgency. | Supported within abstract-level access; manuscript does not overgeneralize to mice. |
| `yates2017functional` | Sensory dynamics can be inherited by a downstream integrator. | Supported; used as an alternative, not an explanation proved here. |
| `okazawa2018psychophysical` | Behavioural temporal kernels mix sensory, decision and response processes. | Supported; correctly used to block stage localization. |
| `parespujolras2026glimpses` | Not currently cited. | Verified ledger comparator; should be added only with the scoped wording in issue 2. |

## Recent-search record and exclusions

Access date: 2026-10-26. Public generic queries only; no unpublished manuscript phrase, result or
numeric value was submitted.

- Europe PMC query: `("mouse" AND ("visual evidence accumulation" OR "motion pulse") AND
  PUB_YEAR:[2024 TO 2026])`; 9 hits returned and screened at metadata level. No mouse continuous-RDK
  strong-pulse held-out transfer study was identified.
- Europe PMC query: `(("random dot motion" OR "motion evidence") AND (pulse OR perturbation) AND
  (decision OR accumulation) AND PUB_YEAR:[2024 TO 2026])`; 50 hits reported, newest 20 screened.
  No record displaced Stine 2023 or Steinemann 2024 as the closest positive motion-pulse precedents.
- Europe PMC query: `(("evidence accumulation" OR "perceptual decision") AND
  ("out-of-distribution" OR generalization OR "held-out" OR "control trials") AND
  (pulse OR perturbation) AND PUB_YEAR:[2024 TO 2026])`; 99 hits reported, newest 20 screened. The
  query was noisy and supplied no matching held-out transfer study; this is not an exhaustive absence
  result.
- OpenAlex search: `"motion pulse" evidence accumulation decision`, filtered 2024-01-01 through
  2026-10-26; 9 results. A new 2026 bioRxiv preprint by Vivar et al., DOI
  `10.64898/2026.10.09.757813`, was confirmed in Europe PMC metadata and abstract. It concerns macaque
  temporal-weighting conditions and sensory-decision circuit interactions, not the present held-out
  transfer design. Because full source fidelity was not audited, it is **not** requested as a citation
  and was not added to any ledger or manuscript file.

## Review limits

This domain pass relied on the rendered manuscript, locked spine, canonical ledgers, paper notes,
literature synthesis/challenges, integrity audits, selected artwork and source manifest. It did not
re-fit models or re-run biological analyses. Detailed statistical calibration belongs to the parallel
statistics review. Author-supplied animal/ethics and reproducibility placeholders remain important for
submission but are outside the three domain issues above and do not alter this field-interpretation
verdict.

