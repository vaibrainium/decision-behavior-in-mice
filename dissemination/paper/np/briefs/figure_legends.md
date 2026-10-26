<!-- np-contract
stage: S3 ; section: figure_legends ; agent: np-architect ; version: v2
thesis: "Joint held-out prediction on control trials favoured the tested accumulator over a rapid-forgetting implementation, but randomized motion pulses exposed a failure of the tested model-and-input pipelines to generalize to transient strong evidence."
claims: C002, C003, C004, C005, C006, C007, C009
numbers: N001, N004, N005, N006, N009, N010, N016, N024, N025, N026, N027, N030, N034, N035, N036, N039, N040, N041, N051, N052, N053, N054, N055, N056, N057, N058, N059, N063, N064, N065, N066
sources:
-->
# Brief: figure_legends

Purpose (one sentence): Make Figures 1–5 and S6 interpretable without the main text by defining every panel, population, visual convention, uncertainty interval, test and model score.

Venue constraints: words 1,650 total, separately budgeted from main text; title sentence states the figure-level finding; present tense for what panels show and past tense for analyses; no citations unless indispensable; no primary claim placement because legends restate Results claims.

Reader question this section answers: Can a reader recover exactly what each mark, line, interval, denominator and model comparison represents from the legend alone?

Paragraph plan:

| # | Move (from section-specs) | Content | Claims | Numbers | Sources | Figure |
|---|---|---|---|---|---|---|
| 1 | Standalone legend | Task/timeline, UCLA/UW schedules, psychometric/RT/no-response panels, individual/group conventions, analysis cutoff and denominators. | cross-reference C002 | N001, N004, N005, N006, N009, N010 | — | 1; 220 words |
| 2 | Standalone legend | Replay/filter schematic, calibration, persistent variation, pulse-aligned response, units and replay-alternative caveat; define trial/seed versus mouse `n`. | cross-reference C003 | — | — | 2; 270 words |
| 3 | Standalone legend | Candidate diagram, score sign, held-out comparison, working threshold, component scores, in-sample fit quality and S3 recovery pointer. | cross-reference C004 | N016 | — | 3; 280 words |
| 4 | Standalone legend | Directional estimand, outcome components, control contrasts, cumulative curve, support weights, animal/trial/cell `n`, Student-t intervals, Holm family and pointwise bands. | cross-reference C005 | N051, N052, N053, N054, N055, N056, N057, N058, N059 | — | 4; 330 words |
| 5 | Standalone legend | Title sentence states C006 alone. Describe common-row observed/predicted curves and the descriptive group mismatch first; label PSUIM6/7 gain profiles and held-out tradeoff as a subordinate C009 diagnostic that supports, but does not share, the headline. | headline cross-reference C006; subordinate cross-reference C009 | N063, N064, N065, N066 | — | 5; 330 words |
| 6 | Standalone legend | Original/revised gate metrics, strategy recovery, decay calibration, panel-specific denominators and explicit timing-test withholding. | cross-reference C007 | N024, N025, N026, N027, N030, N034, N035, N036, N039, N040, N041 | — | S6; 220 words |

Promises this section creates: None; legends must only make approved figures self-contained.

Promises it must deliver: Each title matches its Results heading; every panel letter is described in order; all `n`, error bars, line styles, model gain settings and inferential families are defined locally.

Must include: “no response by 5 s” terminology; “pointwise, not simultaneous” for the cumulative band; score sign and working-threshold caveat; C006 as the sole Figure 5 title claim and selected subordinate-diagnostic wording for PSUIM6/7/C009; explicit statement in S6 that low sensitivity is not evidence of no primacy.

Must not include: New interpretation, uncited literature claims, broad novelty, unregistered numeric values, generic `n` without its unit, “representative mice” for PSUIM6/7, or a significance comparison inferred from overlapping intervals.

Known risks / reviewer bait: Final composites are not assembled, so panel letters must be reconciled after rendering; existing draft figures mix SEM and CI; Figure 4 control contrasts use different matched cells; Figure 5 uses legacy-input intersections; S6 combines distinct calibration questions that must not be collapsed.

Acceptance criteria (the reviewer instantiates these at commit time):

- Total is no more than 1,650 words and follows Figure 1–5, S6 order.
- Each panel, denominator, error representation, test and model convention is defined.
- No claim appears as a new primary placement.
- Every numeric statement is an N token and agrees with the Results brief.
- Legends remain valid when read without the manuscript body.
