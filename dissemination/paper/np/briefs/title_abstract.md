<!-- np-contract
stage: S3 ; section: title_abstract ; agent: np-architect ; version: v2
thesis: "Joint held-out prediction on control trials favoured the tested accumulator over a rapid-forgetting implementation, but randomized motion pulses exposed a failure of the tested model-and-input pipelines to generalize to transient strong evidence."
claims: C001
numbers: N001, N016, N051, N052, N053, N054, N059
sources:
-->
# Brief: title_abstract

Purpose (one sentence): Give an eLife reader the full control-selection versus pulse-transfer result, its scale and its limits within 230 words of front-of-paper text.

Venue constraints: words 230 total: title up to 120 characters, abstract 175–190 words, third-person impact statement 15–30 words; no citations or undefined abbreviations; claim by sentence 3; present tense for context/implication and past tense for this study's work/findings.

Reader question this section answers: What was tested, what was found, and why does the pulse result change the interpretation of good control-trial prediction?

Paragraph plan:

| # | Move (from section-specs) | Content | Claims | Numbers | Sources | Figure |
|---|---|---|---|---|---|---|
| 1 | Title | Indicative title naming mice, brief motion pulses and model limitation; preferred: “Brief motion pulses expose limits of an evidence-accumulation model in mice.” | C001 | — | none permitted | 3–5 |
| 2 | Abstract context/gap | Two sentences: model-compatible control behaviour may not establish out-of-condition transfer; ask whether a control-selected pipeline predicts randomized strong pulses. | C001 setup | — | none permitted | 3–5 |
| 3 | Here we/approach | By sentence 3, state the mouse reaction-time RDK, reconstructed input, joint held-out control comparison and pulse test. | C001 | N001 | none permitted | 1–5 |
| 4 | Concrete findings | Give control score, directional effect with CI/Holm result, and response-associated emergence; avoid excessive diagnostics. | C001 | N016, N051, N052, N053, N054, N059 | none permitted | 3–4 |
| 5 | Contrast/implication | State descriptive temporal mismatch, two-mouse tradeoff qualitatively, failed gates and withheld timing test; conclude that control selection did not validate transient-evidence processing. | C001 | — | none permitted | 5; S6 |
| 6 | Impact statement | Third-person 15–30-word statement: held-out perturbations exposed a predictive limitation hidden by control-trial performance. | cross-reference C001 | — | none permitted | 3–5 |

Promises this section creates: None beyond the locked paper; every abstract finding must map to a Results heading.

Promises it must deliver: The locked thesis in compressed form; species/task/scale; one control comparison; one randomized behavioural effect; the pipeline mismatch; the mechanism and primacy limits.

Must include: C001 as the sole primary claim; `{{N001}}`, `{{N016}}`, `{{N051}}`–`{{N054}}`; “among the tested implementations” or equivalent; “model-and-input pipeline” or a plain-language equivalent; explicit withholding of the timing test.

Must not include: Citations; broad mouse novelty; a causal mechanism verb in the title; “proves accumulation”; primacy/recency; an integration time constant; hard-coded numbers; detailed PSUIM6/7 scores; missing author/institution facts inside scientific prose.

Known risks / reviewer bait: “Evidence-accumulation model” in the singular can sound universal unless the abstract says tested implementation; too many caveats can bury the result; omitting the failed gates would overstate pulse-model inference.

Acceptance criteria (the reviewer instantiates these at commit time):

- Title is at most 120 characters and uses evidence-matched, indicative language.
- Abstract is 175–190 words, has no citations and states the claim by sentence 3.
- Each finding maps in order to Figures 3, 4, 5 and S6.
- C001 is the sole primary claim and all numeric statements use N tokens.
- Impact statement is third person and 15–30 words.

Front- and end-matter facts kept explicit outside the abstract: `[MISSING: author list/order, affiliations, corresponding author, funding and funder role, author contributions, competing interests]`; `[MISSING: acknowledgements and contributor permissions]`; `[MISSING: final data/software availability statement, repository identifiers, access conditions and release timing]`; `[MISSING: final AI-use disclosure wording after eLife policy recheck]`. References are assembled only from verified keys in `np/ledger/sources.csv`.
