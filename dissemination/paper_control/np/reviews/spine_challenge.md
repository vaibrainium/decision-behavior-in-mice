<!-- np-contract
stage: S1 ; section: spine_challenge ; agent: np-devils-advocate ; version: v1
thesis: "On held-out control trials, a bounded accumulator of motion energy with fast guesses predicts mouse choices and response times better than rapid-forgetting or extrema-detection strategies, but model recovery shows that control-trial behavior alone cannot tell these strategies apart."
claims: C001, C002, C003, C004, C005, C006, C007, C008, C009, C010, C011, C012, C013, C014, C015, C016
numbers: N005, N006, N007, N008, N009, N010, N011, N012, N013, N014, N015, N019, N021, N022, N023, N024, N026, N027, N028, N029, N030, N031, N032, N033
sources: stine2020differentiating, caballero2022rt, usher2001leaky; NEW (unverified, for S2): Kirkpatrick, Turner & Sederberg 2021 Psychol Rev 128(6):1051-1087 doi:10.1037/rev0000284; Reinagel 2013 (rats, RDK RT); Shevinsky & Reinagel 2019 (rats, errors vs RT)
-->

# Spine challenge (S1, devil's advocate)

Files read: np/spine.md (v1, unlocked), np/ledger/claims.csv, np/ledger/numbers.csv (N001–N033),
np/config.md, np/decisions.md, paper_accumulation/np/decisions.md (D002–D010),
.agents/reports/2026-10-29-control-descriptives.md, 2026-10-28-stine-exact-models.md,
2026-10-27-f1a-strategy-recovery-responded.md, 2026-10-28-recovery-synthetic-data-mismatch.md,
.agents/plans/2026-10-28-full-recovery-matrix.md, reports/primacy-analysis-plan.md (amendments 13–14),
np/lit/notes/stine2020differentiating.md. Two quick web searches for rodent RDK RT work.

Not re-litigated (settled): control trials only; no-response trials excluded; rig is a covariate only;
ES has sv and fast guesses (same components as C, extrema sample rule).

Ranking: **P0** = sinks or misstates the thesis unless fixed before G1 lock or before the recovery
result is opened; **P1** = a hostile reviewer will make it a major revision; **P2** = minor.

## What a hostile eLife reviewer writes first

"Under the default variant, the main result is that Stine et al. (2020) also hold in mice: control-trial
choices and RTs do not tell integration from non-integration. The positive half ('the accumulator
predicts better') rests on n = 10, t-test Holm p 0.023–0.037 with every Wilcoxon above 0.05, a
model family chosen after the authors saw that dropping drift variability reversed the comparison with
extrema sampling, and a 'motion energy' input whose fluctuations the mice do not detectably use (kernel
null). The recovery that is supposed to calibrate the comparison is scored per mouse, but the claim is
made at group level. It also leaves out the one extrema model with matched components, and it can
'separate' paper-exact extrema detection simply because that model has no fast guesses. Finally, an
opponent single-accumulator design cannot speak to accumulator architecture (Kirkpatrick et al. 2021)."

Each point is taken in turn below.

---

## P0 (fix before G1 lock / before the paired recovery is opened)

### P0-1. The selection rule calibrates the wrong inference (per dataset, not the group claim)
- **Argument.** The spine says FP_X "is the false-positive rate of the Fig 3 conclusion". It is not.
  Fig 3 is a group-level claim: a one-sample t / Wilcoxon on per-1,000-trial ΔNLL across 10 mice, Holm
  (N005–N012). FP_X counts single synthetic mouse-datasets with summed Δ > 10. These two error rates can
  differ in either direction. Example: if the per-dataset FP were 5/20 (the unpaired F1a preview) and
  mice were independent, P(≥5 of 10 mice exceed 10 | E) is about 0.08 under a binomial with p = 0.25. The
  cohort-level false-positive rate of "5/10 mice favor C" could therefore be acceptable while the rule
  still says "not separated", or the reverse.
- **Calibration problems inside the rule.**
  (a) A summed-NLL threshold of 10 scales with trial count (259–4,095 per mouse, N003). FP and SENS are
  therefore set mostly by the 2–3 large mice (PSUIM6+7 already supply 71–74% of the real-data sums, D006),
  and a small mouse can almost never reach Δ > 10. The real-data group test uses per-1,000-trial values,
  so it is not on the same scale as the rule.
  (b) The 20 datasets are 10 mice x 2 replicates. They are not 20 independent draws.
  (c) Binomial uncertainty is large. FP = 2/20 has a Clopper-Pearson 95% CI of about [0.01, 0.32]. Under
  variant A, "identifies the generator" would rest on a false-positive rate that could be as high as 32%.
  (d) SENS ≥ 10/20 is lenient: a test that detects C only half the time would count as "separated".
- **"Fixed before any result" is technically true but incomplete.** An unpaired preview exists:
  FP_E = 5/20 and SENS_E = 16/20 (F1a, 2026-10-27). It is invalid because the synthetic data were
  unpaired, but the author has seen it. The rule also folds D002's "partial" band (3–4/20) into "not
  separated". Neither change favors the authors, but a reviewer will ask about both.
- **Fix (proportionate).** Keep the per-dataset counts as Fig 4, and add a cohort-level calibration
  computed from the same 320 fits. For each generator X, build synthetic 10-mouse cohorts (one replicate
  per mouse, all 2^10 combinations or a bootstrap), run the *exact* Fig 3 test (per-1,000 ΔNLL, t and
  Wilcoxon, Holm over 4), and report P(cohort reproduces the real-data result | X generated) and
  P(... | C generated). Also report FP_X and SENS_X with Clopper-Pearson CIs. Add one sentence to the
  spine: the per-dataset rule sets the wording; the cohort calibration is reported beside it. Write this
  into decisions.md **before** the paired results are read. Disclose the unpaired preview in Methods.

### P0-2. The ESx loophole: "separating extrema detection" can follow from missing components, not strategy
- **Argument.** ESx (and DDMx) differ from C in three ways at once: nominal-coherence input instead of
  motion energy, no sv, and no fast guesses. Removing fast guesses alone costs about 25 NLL per 1,000
  trials (N014, dz 2.01). So SENS_ESx (C-generated data favor C over ESx) is expected to be high because
  ESx cannot produce fast guesses. FP_ESx (ESx-generated data favor C by > 10) is expected to be low
  because C can absorb a plain extrema RT distribution with sv and the bound. ESx is therefore likely to
  be "separated" trivially. The pre-written Variant I would then print "this comparison rules out
  extrema detection". That is a strategy claim earned by a component mismatch. The spine's own H0 row
  and claim C009's note concede this confound ("E is the matched control"). There is no matched control
  on the extrema side of the recovery.
- **Internal inconsistency.** ES, the matched-component extrema model, is in the real-data comparison
  and in the THESIS ("better than ... extrema-detection strategies", N007–N008). Yet it was dropped from
  the recovery because "the author judges its assumptions wrong" (amendment 14,
  plans/2026-10-28-full-recovery-matrix.md). Either ES is a fair stand-in for extrema detection, in
  which case it belongs in the recovery, or it is not, in which case it cannot support the THESIS's
  extrema clause.
- **Fix (pick one, before the recovery is opened).**
  (1) Preferred: add ES as a generator and candidate (at least the ES-generated row and the C-generated
  datasets scored against ES: 20 + 20 + 20 fits on the existing CPU datasets plus ES-generated datasets),
  and let the rule use ES, not ESx, for the extrema side.
  (2) Minimum: rewrite variants I and A so that the extrema clause reads "paper-exact extrema detection
  (nominal input, no drift variability or fast guesses)". Add a scope line that ESx separation does not
  rule out extrema detection with matched components. Also either drop ES from the THESIS's real-data
  clause or state why its assumptions are acceptable for Fig 3 but not for Fig 4.
- **This is the BLOCKER** (see the end of this file).

### P0-3. "Accumulator *of motion energy*" is not shown, and the win may come from RT shape and fast-guess allocation
- **Argument.** The THESIS names the input. Nothing in the evidence shows that within-trial motion
  energy, rather than nominal coherence plus RT-distribution shape, drives the advantage:
  - The stimulus kernel is null (N019, 0.14 [−0.36, 0.63]). The report says the kernel "is driven by the
    per-trial mean of the noise: the fluctuation-only kernel is about 0". The hidden-coherence analysis
    gives k = 0.50, i.e. mice use only part of the reconstructed noise. The model kernels (0.4–0.55, N029)
    sit above the data (0.1–0.2).
  - The task gives a nearly flat chronometric function (1.35 s at 9% vs 1.16 s at 100%; T1 fails Holm,
    N022) and 16% errors at 100% coherence (N028). So the conditions that give Stine et al. their leverage
    (RT strongly modulated by coherence) are weak here. Much of the held-out likelihood must therefore come
    from the RT-distribution shape and from how many trials each model assigns to the fast-guess
    component.
  - **Front-end bias against non-integrators.** E (time constant 5–50 ms) and ES (single-sample
    threshold) respond to the momentary noise in the input. A perfect integrator averages it away. If the
    reconstructed motion energy contains noise the mouse does not see (k = 0.5, screen geometry
    uncorrected), C is penalized least by a wrong front end. C could then win because it is robust to
    input error, not because mice integrate.
- **Fix.**
  (a) Input ablation on real data: refit C, E and ES with nominal coherence (no fluctuations) or with
  time-shuffled motion energy. If C-nominal predicts held-out trials as well as C-ME, delete "of motion
  energy" from the THESIS and glossary.
  (b) Free fluctuation gain: add a weight on the noise component (the two-channel input from
  `--pulse_weight` already exists; apply the same idea to N(t)) for C, E and ES, and check that the
  ranking survives.
  (c) Decompose ΔNLL (C vs E, C vs ES) into a choice part and an RT part, by |coherence| and by RT
  quantile, and report each model's fitted fast-guess fraction. If the advantage sits in the fastest
  quantile or at 0% coherence, say so in Fig 3.
  These are local CPU or short cluster refits on real data only. They do not depend on the recovery.

---

## P1 (major revision if unanswered)

### P1-1. Analysis flexibility in choosing the model family (forking paths)
- **Evidence.** D004 applied the parsimony rules as written and chose the no-sv model. D005 withdrew that
  choice *after* seeing that without sv the accumulator beats ES in only 1/10 mice (with sv: 6/10). Yet sv
  is not needed at group level (N013, Holm p 0.30). Other post hoc choices: DDMx's gain bound was changed
  after its first results (amendment 13 addendum); D007 dropped the recovery qualifier from conclusion 1
  after k = 5/20; D009 removed the free-leak fits.
- **Conflict.** The spine's scope line says "No ... discussion of the model without drift variability".
  This contradicts the D005 note that the manuscript will say in one sentence that the control comparison
  depends on drift variability. A reviewer who finds this dependence in the code or data will treat the
  omission as concealment.
- **Fix.** Methods: state that the model set was fixed after the no-sv comparison was seen, and give the
  no-sv C-vs-ES result (1/10) as a sensitivity result in a supplement table. Drop or soften the scope
  line, with author approval logged in decisions.md. Make "the real-data ranking depends on sv" a stated
  limitation.

### P1-2. The positive clause is statistically fragile but is stated flatly
- **Evidence.** For all four alternatives the t-test Holm p is 0.023–0.037 and the Wilcoxon Holm p is
  0.055–0.059 (N006, N008, N010, N012). Per mouse, C is better by > 10 in only 5–6 of 10 mice (N030–N033).
  Ranges include negative values (C vs E down to −16.9). Two mice dominate the sums. The THESIS says
  "predicts ... better than" without qualification.
- **Fix.** Keep both tests in the text. Add a leave-one-mouse-out analysis and a hierarchical estimate
  (mixed model on per-trial ΔNLL with mouse random effects). In the THESIS, consider "predicts ... better
  at group level (5–6 of 10 mice individually)". State in Fig 3 that the nonparametric test does not reach
  0.05.

### P1-3. Accumulator architecture is untested (Kirkpatrick, Turner & Sederberg 2021; added by author)
- **Point.** Kirkpatrick, Turner & Sederberg 2021 (Psychol Rev 128(6):1051–1087, doi:10.1037/rev0000284;
  unverified here, check at S2) argue that standard single-direction RDK coherence designs under-constrain
  accumulator architecture. Fully dependent (DDM), partially dependent (LCA/FFI) and independent
  (race/LBA) architectures could only be told apart with equal-evidence conditions, and LCA fit best.
- **Why it applies here.** Every model in this paper takes *net* (opponent) motion energy into one
  decision variable, so all are fully dependent by construction. No race or LCA model was fitted. E is a
  one-dimensional leaky (OU) accumulator, not an LCA with mutual inhibition. The control task has no
  equal-evidence condition, so the data cannot constrain architecture. The common model also
  under-predicts fast errors (N026, −71 ms; exploratory, uncorrected). Fast and slow error patterns are a
  classic signature by which race, LCA or starting-point-variability models differ from a DDM with sv
  only.
- **Severity: P1, not P0.** The THESIS compares strategies over time (integration vs forgetting vs
  extrema), not architectures, and the default variant B already concedes non-identifiability. The
  architecture gap adds alternatives that the comparison does not cover; it does not reverse any
  reported number. It becomes **P0 only under Variant A**. A's wording "mice ... behave as bounded
  accumulators" reads as an architectural and mechanistic claim that an opponent single-accumulator
  comparison cannot support.
- **Proportionate fix.**
  (1) Wording: in the THESIS and glossary, write "a single bounded accumulator of net (opponent) motion
  energy". Rewrite Variant A so it claims only "integration rather than rapid forgetting or extrema
  detection", not "behave as bounded accumulators".
  (2) Add a scope line: "No claim about accumulator architecture (single opponent accumulator vs race or
  competing accumulators); the control task has no equal-evidence condition that could constrain it
  [Kirkpatrick et al. 2021]."
  (3) Discussion: one limitation paragraph tying N026 (fast errors under-predicted) to the architecture
  and starting-point-variability alternatives. Keep N026 labeled exploratory.
  (4) Optional, only if a reviewer insists: a two-channel race/LCA fit on separate rightward and leftward
  motion energy for the 10 mice, reported as a supplement. Not needed for the thesis.

### P1-4. Novelty: under B, the result is "Stine et al. hold in mice", and the rodent RDK RT literature is missing
- **Evidence.** The default variant is a negative methods result that Stine et al. (2020) already made in
  general form. Rodent RDK reaction-time work with similar features is not in sources.csv:
  - Reinagel 2013 (rats, RDK): concludes that response time is governed more by elapsed time than by an
    evidence criterion.
  - Shevinsky & Reinagel 2019 (rats): accuracy rises with RT, i.e. errors are fast, the opposite of
    primates.
  Only Treviño et al. 2022 (caballero2022rt, mouse DDM) is in the ledger. The mice here show the same
  features: a flat chronometric function and faster errors in 9/10 mice (N025).
- **Fix.**
  (a) Add the Reinagel papers at S2, and frame the fast errors and flat chronometry as a rodent-wide
  pattern, not a new finding.
  (b) Give the B result added value. Use the recovery machinery to estimate how many control trials, or
  which designed perturbation (pulses at known times, equal-evidence or reversal trials), would push
  FP_X ≤ 2/20, for example by subsampling or upsampling the synthetic trial counts. A design guide for
  mouse RDK labs is a contribution that Stine et al. do not provide for rodents.

### P1-5. The forgetting alternative is a band, not the continuum; the free-leak evidence is hidden
- **Evidence.** E's leak is constrained to 20–200/s (time constant 5–50 ms). D009 removed the free-leak
  fits, which gave a fitted leak of 0–1.8/s, i.e. long time constants. That evidence *favors*
  integration, yet it is withheld. As D009 itself notes, the 5–20/s range is covered by no reported
  analysis. A reviewer will ask: "what integration time constant do the data allow?"
- **Fix.** Report a per-mouse profile of held-out NLL over leak (for example 0, 1, 2, 5, 10, 20, 50/s),
  or at least the free-leak estimates as a supplement. This turns the C-vs-E dichotomy into a lower bound
  on the time constant. It needs author approval to reverse D009.

---

## P2 (minor)

- **P2-1. Figures vs claims.**
  - Fig 1: rebuild on responded control trials only. C002 has no ledgered number; use N028.
  - Fig 2 D–E (kernels with model overlays): N029 shows both models predict a kernel 2–3x the data.
    Present this as a model misfit, not only as "underpowered". C006 says variability is "as large as" the
    kernel; the N027 range 0.2–1.1 against 0.4–0.55 supports "comparable", not "as large" in every mouse.
  - Fig 4 does not exist yet.
  - Fig 3 includes DDMx/ESx comparisons that are confounded by components (C009 note). Put them in a
    separate panel labeled "different components and input".
- **P2-2. Mechanism vs correlation.** The paper is a model comparison with no perturbation. This is fine,
  but avoid "mechanism" and "strategy used by mice" outside Variant A. Variant A's "behave as" is already
  borderline.
- **P2-3. Recovery at point estimates only.** Generators use each mouse's fitted parameters. Add one
  sentence that recovery away from the fitted parameters (for example E at 10–20/s) is untested, which
  links to P1-5.
- **P2-4. B0 trigger.** "Not done by G3" is a date-based escape. State that if the paired recovery
  partially fails (for example < 320 fits), no partial counts are used.
- **P2-5. DDMx rows are excluded from the rule.** This is reasonable, but say why: DDMx is the
  integration family, so its separation from C is not a strategy question.
- **P2-6. Glossary.** "Fast guess" vs "lapse": the 16% errors at 100% coherence will be read as lapses
  by reviewers. Define how they are split between the guess component and decision errors.

---

## The one experiment / analysis that would sink the paper
The input ablation (P0-3a): if C fitted with nominal coherence (no within-trial fluctuations) predicts
held-out control trials as well as C on motion energy, *and* E and ES fitted with nominal input close the
gap to C, then the THESIS's positive clause reduces to "a DDM with fast guesses fits RT distributions
better than models with worse RT-shape flexibility". That is not evidence about integration of motion.
It is cheap to run on real data now.

## BLOCKER
**P0-2 must be resolved before the spine is locked or the paired recovery result is read.** As written,
Variant I can be selected because the paper-exact extrema model (ESx) lacks fast guesses and sv, and it
would then print "rules out extrema detection". Either add ES to the recovery or restrict the variant
wording to "paper-exact extrema detection (no drift variability or fast guesses)". Log the choice in
decisions.md before any count is computed. P0-1 (add the cohort-level calibration and Clopper-Pearson
CIs) should be fixed in the same decisions.md entry, for the same reason: once the counts are known, any
change looks post hoc.

Sources (web searches, for S2 verification):
- [Reinagel 2013, Speed and accuracy of visual motion discrimination by rats (PMC3695925)](https://pmc.ncbi.nlm.nih.gov/articles/PMC3695925)
- [Shevinsky & Reinagel, bioRxiv 726703 (rats, errors vs RT)](https://www.biorxiv.org/content/10.1101/726703v2.full.pdf)
- [Treviño et al. 2022, Response time distributions ... freely moving mice](https://www.aminer.org/pub/6306016790e50fcafda91688/response-time-distributions-and-the-accumulation-of-visual-evidence-in-freely-moving)
- [Frontiers in Neuroscience 2019, rat vs human RDK (fnins.2019.01211)](https://www.frontiersin.org/journals/neuroscience/articles/10.3389/fnins.2019.01211/pdf)
- Kirkpatrick, Turner & Sederberg 2021, doi:10.1037/rev0000284 (supplied by the author; not fetched)
