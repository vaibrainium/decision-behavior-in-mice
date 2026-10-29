<!-- np-contract
stage: S1 ; section: spine_v2_changes ; agent: np-architect ; version: v2
thesis: "On held-out control trials, a single bounded accumulator of net motion energy with fast guesses predicts mouse choices and response times better at group level than rapid-forgetting or extrema-detection models, but model recovery shows that control-trial behavior alone cannot tell these strategies apart."
claims: C002, C006, C008, C009, C010, C011, C012, C015, C017, C018, C019
numbers: N005, N006, N007, N008, N009, N010, N011, N012, N013, N014, N026, N027, N028, N029, N030, N031, N032, N033
sources: stine2020differentiating
-->

# Spine v2: response to the devil's-advocate challenge (one revision)

Labels: **ACCEPTED** = fixed in spine v2 by wording, scope or figure plan. **PARTIAL** = the wording part
is fixed; the rest needs an analysis or an author decision (see NEEDS HUMAN). **NEEDS HUMAN** = not
resolved by the architect. No point is contested outright; contested sub-points are marked with a reason.

## Point by point

| Point | Label | What v2 does | Remaining |
|---|---|---|---|
| P0-1 FP_X is not the error rate of the group claim | PARTIAL | Key control no longer says FP_X is "the false-positive rate of the Fig 3 conclusion"; criterion G (cohort level, exact Fig 3 t-test, Holm) is fully specified as an option; Clopper-Pearson CIs always reported; δ (per 1,000) shown beside Δ in Fig 4 panel B; cohorts' non-independence (2 replicates) stated | NH2: which criterion sets the wording |
| P0-1(a) Δ > 10 scales with trial count | PARTIAL | Stated in Fig 4 via δ; criterion G uses the per-1,000 scale | Part of NH2 |
| P0-1(b) 20 datasets are not 20 independent draws | ACCEPTED | Methods/Fig 4 legend state 10 mice x 2 replicates | none |
| P0-1(c) wide binomial CIs | ACCEPTED | CIs reported for every count, whichever criterion | none |
| P0-1(d) SENS ≥ 10/20 lenient | NEEDS HUMAN (in NH2) | v1 threshold kept; changing it is a rule change the author must make before counts are read | NH2 sub-choice |
| P0-1 unpaired preview seen | ACCEPTED | Scope line and C019: Methods discloses the unpaired run as superseded and invalid; no counts reported (they are not in the ledger) | Log in decisions.md |
| P0-1 D002 "partial" band folded into "not separated" | ACCEPTED | Rule text keeps the fold-in explicitly (3–5/20 = not separated); Methods says so | none |
| P0-2 ESx loophole / ES missing from recovery | NEEDS HUMAN (BLOCKER) | X_ext slot with three mechanical options; NH1-b wording "paper-exact extrema detection (nominal-coherence input, no drift variability or fast guesses)" and its scope line pre-written; H3 row states the component confound | NH1 |
| P0-3 "of motion energy" not shown; RT-shape / front-end bias | PARTIAL | THESIS says "net motion energy" as the model input; scope line: no claim that within-trial fluctuations drive the advantage; new hypothesis row H0b; INPUT slot lets the phrase be dropped mechanically | NH3 |
| P1-1 forking paths (D004/D005, DDMx gain bound, D007, D009) | PARTIAL | C019 discloses that the recovery rule was fixed before counts; scope line on no-sv flagged as conflicting with the D005 note | NH4 (no-sv sentence); DDMx gain-bound change and D007 should be stated in Methods (no new analysis needed; decide under NH4 with the same entry) |
| P1-2 positive clause fragile | PARTIAL | THESIS and all variants say "at group level"; C008/C009 carry the Wilcoxon p and per-mouse > 10 counts (N030–N033); Resolution states them | NH6 (LOMO, mixed model) is optional |
| P1-3 architecture (Kirkpatrick et al. 2021) | ACCEPTED (fix 1–3); optional fit 4 not taken | "single bounded accumulator of net motion energy" everywhere; Variant A no longer says "behave as bounded accumulators"; scope line with doi, unverified until S2; H4 row; new C018 ties N026 to architecture and starting-point-variability alternatives (N026 stays exploratory); glossary "architecture" | Race/LCA fit only if a reviewer asks (author's call, not listed as NH) |
| P1-4a rodent RDK literature missing | ACCEPTED | Opening frames flat chronometry and fast errors as a known rodent pattern; Reinagel 2013, Shevinsky & Reinagel 2019, Frontiers 2019 and Treviño et al. go to the "For S2" list, not cited | S2 verification |
| P1-4b design guide for the B result | NEEDS HUMAN | Not added (new simulations) | NH7 (optional) |
| P1-5 leak band, free-leak hidden | PARTIAL | Scope says rapid forgetting = 20–200/s (5–50 ms) and no integration time constant is claimed; D009 kept | NH5 |
| P2-1 figures vs claims | ACCEPTED | C002 uses N028; C006 "comparable"; new C017 (model over-predicts kernel, N029); Fig 3 split into panel A (matched) and B ("different components and input") | Fig 4 does not exist yet (pending) |
| P2-2 mechanism wording | ACCEPTED | Scope: no "mechanism" or "strategy used by mice" outside A; Variant A rewritten | none |
| P2-3 recovery at point estimates | ACCEPTED | Scope line | none |
| P2-4 B0 trigger | ACCEPTED | No partial counts; completion check reads fit counts and manifests only. The "not done by G3" trigger is kept as a schedule fallback, contested only in that it is not an escape: it can only produce B0, the weakest variant | none |
| P2-5 DDMx rows excluded | ACCEPTED | Reason written into the rule | none |
| P2-6 fast guess vs lapse | ACCEPTED | Glossary defines fast guess and states that errors at 100% coherence are not split except through the fitted model; Fig 1 legend promise | none |

## NEEDS HUMAN

Each item is decided by the author and logged in decisions.md. NH1 and NH2 must be logged **before any
output of the running recovery job is opened** (the completion check may count fits and compare
manifests, but must not read NLL values). The selection rule in spine.md already has a mechanical form
for every option below.

### NH1. Extrema side of the recovery: add ES, or restrict the wording to ESx (BLOCKER)
- **NH1-a. Add ES as 5th generator and candidate; the rule uses ES.** Option text: "ES is added to the
  paired recovery as a generator (20 CPU pre-generated datasets, same mice, 2 replicates, new sha256
  manifest) and as a candidate on all datasets; the selection rule uses X set = {E, ES}; ESx is reported
  in the matrix but does not enter the rule." Cost: 180 extra fits (ES candidate on the 80 existing
  datasets + 5 candidates on 20 ES datasets), one more cluster job; whether model_recovery already
  supports ES as a generator is unverified. Reverses plan amendment 14 (ES dropped because its
  assumptions were judged wrong). Strongest claim if separated.
- **NH1-b. Keep 4 x 4; restrict the wording to paper-exact extrema detection.** Option text: "The rule
  uses X set = {E, ESx}. In every variant, EXT_LABEL = 'paper-exact extrema detection (nominal-coherence
  input, no drift variability or fast guesses)'. Scope: ESx separation does not rule out extrema
  detection with matched components; ES is compared on real data only, and Methods states that ES was
  left out of recovery by author decision." Cost: none; Variant I/A then says less; a reviewer may still
  ask why ES is fair for Fig 3 but not Fig 4.
- **NH1-c. Drop extrema from the rule.** Option text: "The rule uses X set = {E}; ESx rows are reported
  descriptively. Possible variants: A_E, B, B0." Cost: none; gives up any recovery-based extrema statement.

### NH2. Level of the recovery criterion
- **NH2-P. Per dataset (v1 rule) + Clopper-Pearson CIs.** Option text: "Separated iff FP_X ≤ 2/20 and
  SENS_X ≥ 10/20 (Δ > 10 per dataset); CIs reported; the text states that this calibrates the per-mouse
  > 10 rule, not the group test." Cost: none. Sub-choice: keep SENS ≥ 10/20 or raise it (e.g. ≥ 14/20);
  must be fixed now.
- **NH2-G. Cohort level sets the wording.** Option text: "Separated iff, over all 1,024 synthetic
  10-mouse cohorts (one replicate per mouse), FPg_X ≤ 0.10 and SENSg_X ≥ 0.50, where a cohort reproduces
  the real-data result if mean δ_X > 0 and the one-sample t-test has Holm p < 0.05 (Holm over all non-C
  candidates); per-dataset counts with CIs are reported beside it." Cost: a post-processing script on
  the existing fits (local CPU, no new fits); cohorts share 2 replicates per mouse, so the rates are
  resampling summaries.
- **NH2-P+G. Both must pass.** Option text: "Separated iff P-separated and G-separated." Cost: as NH2-G;
  most conservative (more likely B).
- (The devil's advocate's own suggestion, "P sets the wording, G reported beside it", is NH2-P plus the
  G computation as a descriptive panel; the author may pick it explicitly.)

### NH3. "Of motion energy": run the input ablation, or drop the phrase
- **NH3-a. Run the ablation before G1, with a fixed criterion.** Option text: "Refit C, E and ES on the
  control split with (i) nominal coherence and (ii) within-trial time-shuffled motion energy; report the
  choice vs RT split of held-out ΔNLL and each model's fitted fast-guess fraction. INPUT keeps 'of net
  motion energy' iff C with motion energy beats C with nominal input on held-out per-1,000 NLL at group
  level (t-test, Holm over the two ablations, p < 0.05); otherwise INPUT = 'a single bounded
  accumulator'. C vs E/ES with nominal input is reported as a sensitivity result." Cost: 3 models x 2
  inputs x 10 mice cross-validated fits (local CPU or a short cluster job); whether per-trial choice and
  RT NLL terms are stored in the existing outputs is unverified. Risk: the devil's advocate names this
  the result that could sink the positive clause.
- **NH3-b. Drop the phrase now.** Option text: "INPUT = 'a single bounded accumulator' in every variant;
  Methods states the model input is net motion energy; the front-end-robustness alternative (H0b) is a
  stated limitation." Cost: none; weaker title/abstract; the limitation remains open for reviewers.
- **NH3-c. Keep the phrase as input description only, plus the cheap NLL split.** Option text: "INPUT
  unchanged; scope line 'no claim that within-trial fluctuations drive the advantage' stays; only the
  choice vs RT and RT-quantile split of existing held-out NLLs and the fast-guess fractions are added
  (Fig 3 supplement)." Cost: post hoc on existing fits if per-trial terms are stored [unverified];
  otherwise reruns of scoring only.

### NH4. D005 note vs the scope line "no discussion of the model without drift variability"
- **NH4-a. Follow the D005 note.** Option text: "One sentence in Results or Methods states that the
  real-data comparison with extrema sampling depends on drift variability, with the no-sv result in a
  supplement table; config.md and the scope line are changed." Cost: the no-sv C-vs-ES numbers (1/10 mice
  per the challenge) must first be added to numbers.csv from the paper_accumulation tables; changes a
  fixed author rule.
- **NH4-b. Methods disclosure without numbers.** Option text: "Methods states that the model set
  (with drift variability) was fixed after a comparison without drift variability had been seen, and
  that the extrema comparison depends on it; no supplement table." Cost: none; partial transparency.
- **NH4-c. Keep the v1 scope line (config rule).** Option text: "No mention of the no-sv model." Cost:
  none now; the devil's advocate rates this a concealment risk at review.
- The same decision entry should say whether Methods states the DDMx gain-bound change (amendment 13
  addendum) and D007.

### NH5. Free-leak result (D009 says not used)
- **NH5-a. Keep D009 (default in v2).** Option text: "No free-leak fits; scope states that rapid
  forgetting means 20–200/s and that slower leak is not tested." Cost: none; reviewer likely asks for the
  integration time constant.
- **NH5-b. Reverse D009: report the existing free-leak estimates as a supplement.** Option text:
  "Per-mouse free-leak estimates and held-out NLL from the existing fits go to a supplement table,
  labeled post hoc." Cost: ledger the numbers from the existing fits (not in numbers.csv); needs a
  decisions.md entry reversing D009.
- **NH5-c. Leak profile.** Option text: "Held-out NLL per mouse over fixed leak values (e.g. 0, 1, 2, 5,
  10, 20, 50/s), reported as a lower bound on the time constant." Cost: new cross-validated fits (7 leak
  values x 10 mice); new analysis.

### NH6. Robustness of the positive clause (optional)
- **NH6-a. Wording only (v2 default).** "At group level", Wilcoxon and per-mouse counts stated. Cost: none.
- **NH6-b. Add leave-one-mouse-out group tests and a mixed model on per-trial ΔNLL (mouse random
  effects).** Cost: local, on existing per-trial held-out NLLs if stored [unverified].

### NH7. Added value under variant B: design guide (optional)
- **NH7-a. None; Discussion says qualitatively that designed perturbations are needed.** Cost: none.
- **NH7-b. Trial-count curve: subsample/upsample synthetic trial counts and report FP/SENS vs n.** Cost:
  new recovery runs at several n.
- **NH7-c. Simulated designed perturbations (e.g. equal-evidence or brief-pulse trials) in recovery.**
  Cost: new generators and fits; must stay simulation-only to respect the no-pulse-results scope.

## Not changed
- THESIS remains variant B (conservative default) until the rule is applied.
- No new numbers or citations were added; new literature is in the spine's "For S2" list.
- decisions.md was not edited by the architect; the orchestrator logs NH choices.
