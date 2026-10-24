# Report: manuscript story integration pass
Date: 2026-10-23   Agent: Codex   Commit: 10c1b06 (starting snapshot; current draft changes uncommitted)
Plan: [paper write-up](../plans/2026-10-20-paper-writeup.md), V–X

## Question
Can the completed behavioural pulse follow-up be integrated into a coherent paper draft without overstating strategy or temporal-mechanism claims?

## Summary
Revised the Markdown manuscript around the agreed argument: control behaviour favours the tested accumulator, randomized pulses redirect choices, and the fitted models misplace the pulse effect in time. Added the assignment-based effect, pulse-aligned response curves, stimulus audit, model diagnostics and corresponding Methods. Preserved the original/revised failed gates, low strategy sensitivity and the decision not to run the confirmatory timing test. The tau-p pilot remains outside formal claims pending its planned independent check.

## Findings
- DRAFTED: title and 193-word abstract now state the relative control-model result, exploratory pulse effect, joint choice/response-time failure and unresolved mechanism. Source: `dissemination/paper/manuscript_2026-10-23.md`, C079–C081.
- DRAFTED: Results C082–C092 report the scheduled-assignment analysis, primary +5.84 percentage-point contrast, response components, pulse-versus-control contrasts, response time course, estimator simulation, stimulus audit and two-mouse gain tradeoff. Sources: E024–E029; exact files and commands are recorded in those source locators and the component reports.
- DRAFTED: Discussion C093–C095 distinguishes the randomized behavioural result from the relative model comparison and from unique mechanism identification. Methods C096–C100 declare the exploratory assignment analysis, weighting, competing outcomes, simulation check, replay audit and likelihood diagnostics.
- VERIFIED BY LOCAL AUDIT: source manifest schema passes; all 94 physical claim lines have unique IDs, matching hashes and existing evidence IDs; local links pass. Human scientific verification remains `unverified` by design.
- VERIFIED BY LOCAL AUDIT: `consistency_2026-10-23-v2.json` passes with 66 numeric facts, five methods and five results. The revision corrects inherited numerator fields N037–N041 only in the v2 registry; the historical registry is preserved.
- VERIFIED: abstract is 193 words. Text through Discussion is 4,845 whitespace-delimited words including headings and drafting markers, within the provisional eLife target of roughly 5,000 words but with little room for expansion.

## What did not work / unresolved
- The manuscript linter correctly fails on the explicit scheduled-control sensitivity TODO at line 191. It also warns that no manuscript confidentiality manifest was supplied and flags existing recovery wording for human overstatement review. These are drafting gates, not corrupted output.
- Animal/ethics/training, final exclusions, declarations, authorship, data/code availability and environment records remain explicitly missing.
- The Results remain longer than the final narrative should be because the detailed gate/amendment chronology is still in the main text after the new pulse sections. A later compression pass should move calibration detail to Figure 5 supplements while retaining the failures and stopping decision in the main Results.
- The hidden-coherence scheduled-control sensitivity remains pending. Figure assembly and caption reconciliation have not started in this pass.
- The tau-p negative pilot was authored by the coordinator and has no independent post-run check yet. It is mentioned only in an author note and is absent from the claim and consistency registries.

## How to reproduce
Starting snapshot: `10c1b06`. Inputs are the committed manuscript/evidence package plus `dissemination/paper/pulse_followup_results_2026-10-23.md` and reports E024–E029. Validate with:

```bash
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -B .claude/skills/scientific-writing/scripts/check_consistency.py dissemination/paper/consistency_2026-10-23-v2.json
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -B .claude/skills/scientific-writing/scripts/lint_manuscript.py dissemination/paper/manuscript_2026-10-23.md
git diff --check
```

The claim check follows `audit_claims.py::claim_text_hash`: extract one claim/evidence marker pair per physical line, validate every evidence ID against `sources_2026-10-23.json`, compare hashes with `claims_2026-10-23-v2.csv`, and resolve local Markdown links. The full `audit_claims.py` intentionally fails while sources and claims await accountable human verification.

## Caveats
This is a working scientific draft, not a submission candidate. All new pulse analyses are exploratory and were developed after the original predictive gates failed. The group unit for behavioural inference is the mouse; model-diagnostic evidence for the gain conflict is strong in two mice. No unpublished material was sent to an external service. The existing References and drafting-assistance section already include the Scientific Agent Skills workflow citation used in this pass.

## Open questions and next steps
- [ ] Author reviews the central story, title and level of detail retained for the predictive gates.
- [ ] Coordinator supplies the independent tau-p check; then decide whether its negative result belongs in a Figure 5 supplement and thesis chapter.
- [ ] Resolve the scheduled-control hidden-coherence sensitivity or label the historical analysis explicitly.
- [ ] Supply animal, ethics, training, author and declaration facts from records.
- [ ] Build Figures 1–5 from audited source tables and reconcile every legend with the rendered panels.
