<!-- np-contract
stage: S1 ; section: spine_v3_changes ; agent: np-architect ; version: v3
thesis: "On held-out control trials, a single bounded accumulator of net motion energy with fast guesses predicts the per-coherence distributions of mouse choices and response times better at group level than rapid-forgetting or extrema-detection models, mostly through response times, but model recovery shows that control-trial behavior alone cannot tell these strategies apart."
claims: C005, C008, C009, C010, C011, C012, C019, C020, C021, C022, C023, C024, C025, C026
numbers: N005, N006, N007, N008, N034, N035, N036, N037, N038, N039, N040, N041, N042
sources: stine2020differentiating
-->

# Spine v3: author decisions D002/D003 and the new results applied

## NEEDS HUMAN items from v2 and how v3 resolves them
| Item | Decision | What v3 does |
|---|---|---|
| NH1 extrema side | D002-1, D003: add ES | 5 x 5 grid (C, E, ES, DDMx, ESx), 500 fits (320 + 180). X set = {E, ES}, EXT_LABEL = "extrema detection". Variant A_E and the NH1-b/NH1-c text are removed. Variant I is split into I_E and I_ES, each with its own wording. The validity check counts 500 fits and checks the 100-dataset manifest. |
| NH2 criterion | D002-2, D003: cohort level primary | Criterion G sets the wording: 1,024 cohorts per generator, mean δ > 0 and t-test Holm p < 0.05 over the 4 non-C candidates (the Fig 3 family), separated iff FPg ≤ 0.10 and SENSg ≥ 0.50. The thresholds were fixed now from the NH2-G option text the author chose. Per-dataset FP/SENS (Δ > 10) with Clopper-Pearson CIs are reported for all 25 cells and are not decisive. If they disagree with G, both are reported and the wording follows G. There is no binomial CI on cohort fractions (cohorts share replicates). |
| (rule) DDMx/ESx | n/a (required by task) | The spine section "Why only E and ES decide" explains that E and ES differ from C only in leak or the sampling rule. DDMx and ESx differ in input, sv and fast guesses all at once, so separating them measures component and input detectability, not integration vs non-integration, and DDMx is itself integration. They stay in the Holm family so that the cohort test equals the Fig 3 test. |
| NH3 input | D003: shuffle dropped; split done; nominal refits pending | The THESIS says "per-coherence distributions ... mostly through response times". Scope adds: no trial-level-use claim, and no claim of a better choice prediction than ES. New H0b (RT shape) is marked supported against ES/ESx/DDMx and partly against E. New H0c (input) is decided by the nominal refits. The INPUT rule is fixed: keep "of net motion energy" iff Δnom_C > 0 with t Holm p < 0.05 (Holm over C, E, ES); otherwise, or if the refits are not complete by G3, drop the phrase. Interpretation is fixed in advance: within-coherence stimulus distribution, not trial-level use. Fig 3—figure supplement 1 and claim slots C025/C026 were added. |
| NH4 no-sv | D003: one Methods sentence, no numbers | C020 gives the sentence. The scope line now permits exactly that sentence and nothing else. |
| NH5 free leak | D009 kept | Scope unchanged: 20–200/s, slower leak untested, no free-leak fits. |
| NH6 robustness | D003: leave-one-mouse-out | C023 (N042, uncorrected p values labeled as such); Fig 3 supplement table; Resolution and promises updated. |
| NH7 design guide | D003: none | Scope line added; the Discussion stays qualitative under B/I. |

## New results integrated
- N034–N041 (choice/RT split) give C021 (matched alternatives) and C022 (paper-exact). The THESIS clause "mostly through response times" holds for all four alternatives: the RT part is 10.2 of 12.8 (E), 17.5 of 18.7 (ES), 24.6 of 28.2 (DDMx) and 30.1 of 30.2 (ESx) per 1,000 trials. Against ES the choice part is about 0 (N036). Against E there is a small choice advantage that is positive in every mouse (N034, min 0.7).
- The pooled likelihood (report 2026-10-29-likelihood-ignores-trial-me) gives C024 (Methods) and a scope line. C008 now says "per-coherence choice and RT distributions". C005 is noted as the only trial-level test.
- N042 gives C023.

## Other changes
- C010–C012 were rewritten for G-primary, the 5 x 5 grid and the I_E/I_ES variants. C019 now covers the v3 rule, the nominal rule and the ES reversal of plan amendment 14.
- Fig 3 adds panel D (split), figure supplement 1 (nominal refits, PENDING) and a LOMO table. The source paths point to paper_control/tables/*_2026-10-29.csv, which reproduce the 2026-10-28 table exactly. Fig 4 now has panel A = cohort rates (primary) and panel B = per-dataset counts with CIs.
- Glossary additions: nominal-coherence refit, choice part / RT part, synthetic cohort, reproduces. "separated" and "held-out NLL" were redefined.

## Not changed
- The THESIS line is still variant B with INPUT = "of net motion energy". Only the recovery rule and the INPUT rule can change it.
- No numbers or citations were invented. FPg/SENSg, Δnom and the nominal ranking are [PENDING].

## Open items for the orchestrator or the author
1. Log the v3 selection rule and INPUT rule in decisions.md before any output of job 42579825 or of the ES-cell job is opened (C019 depends on this entry).
2. Confirm the INPUT rule. D002-3 made "of motion energy" conditional on the ablation. D003 says the thesis "treats net motion energy as model input". v3 carries the D002 condition over to the nominal refits, with a default of dropping the phrase if the refits are not done by G3. If the author prefers to keep the phrase unconditionally as an input description, the INPUT rule is deleted and Fig 3—figure supplement 1 becomes sensitivity only.
3. The config.md line "The no-sv model is not discussed" conflicts with C020/D003 and needs an update by the orchestrator.
4. Carried over from v2 NH4 and not addressed by D003: should Methods state the DDMx gain-bound change (amendment 13 addendum) and D007?
5. Missing scripts: cohort-level recovery post-processing; `_nom` models in control_heldout.py; panel scripts for Fig 3D and Fig 4.
6. Check that C's CV fits respect the 50% non-response cap (open item in report 2026-10-29-heldout-choice-rt-split; NOT CHECKED).
