# Plan: write up the mouse evidence integration paper
Status: active
Created: 2026-10-20 by Claude (Opus 5.5)
Related reports: dissemination/reports/mouse-ddm-analysis-log.md, dissemination/reports/mouse-ddm-next-steps.md,
dissemination/reports/primacy-analysis-plan.md

## Goal
A full manuscript draft in `dissemination/paper/`, built from the outline in `dissemination/paper/outline.md`, with every
number traceable to a report, notebook or script.

Current authorized drafting pass (2026-10-22, Codex): integration versus extrema detection is the primary question;
primacy is secondary and conditional on predictive adequacy and sensitivity. Draft the established results and
Methods now, with explicit pending sections for queued Hyak analyses. No new fits or pulse-outcome analysis in this pass.

## Context
Analysis steps 0–7 are tracked in `dissemination/reports/mouse-ddm-next-steps.md`. Motion energy and hidden coherence
are final; the DDM common model is provisional (steps 1–2 fits submitted, 3.1 script ready); primacy test not run.

## Assumptions
- One paper covering ME method, hidden coherence, DDM and primacy (to be confirmed by the authors; outline §5).
- Methods and R1–R3 will not change much when the remaining fits finish.

## Steps
- [x] 1. Outline, figure plan, writing order, open decisions (`dissemination/paper/outline.md`).
- [ ] 2. Authors settle outline §5 decisions (journal, authorship, one vs two papers, public timestamp of primacy plan).
- [ ] 3. Fill MISSING Methods facts (animals, ethics, training, exclusions).
- [x] 4. Draft Methods: task/rigs, trial labelling, motion energy, hidden coherence (first prose pass in manuscript_2026-10-22.md; animal/exclusion facts still missing).
- [ ] 5. Make Figs 1–3 and draft Results R1–R3.
  - [x] 5a. Fig 1 (task/behaviour): `scripts/paper/fig1_behaviour.py` → `dissemination/paper/figures/`; caption in
        `dissemination/paper/figure_captions.md` with numbers from the script's printed summary.
  - [x] 5b. Fig 2 (motion energy): `scripts/paper/fig2_motion_energy.py`; caption.
  - [ ] 5c. Fig 3 (hidden coherence): `scripts/paper/fig3_hidden_coherence.py`; caption.
  - Conventions: mouse is the unit (per-mouse curves + mean ± SEM across mice); behaviour uses the *scheduled* pulse
    label (`build_ddm_inputs.scheduled_pulse`); provisional 180 mm width until a journal is chosen; never overwrite an
    output (scripts write a date-stamped file).
- [ ] 6. Draft DDM Methods (model, likelihood, fitting, CV); fill R4 once next-steps step 3 is done.
- [ ] 7. Add S2–S5 and recovery after next-steps steps 3–4.
- [ ] 8. R5 + Fig 5 after next-steps step 6; then Intro, Discussion, Abstract, Title.
- [ ] 9. Verify: every number in the draft traced to a FINAL source; references checked; ARRIVE 2.0 checklist filled.

### Current drafting pass
- [x] A. Review existing evidence, implementation, and scientific-writing instructions; confirm scope with user.
- [x] B. Write manuscript prose for Introduction, established Results, and Methods; leave pending results explicit.
- [x] C. Attach evidence IDs and source/claim records; distinguish agent inspection from human verification.
- [x] D. Check numerical provenance, missing details, and claim strength; write a handover report and update status.
- [x] E. Inspect newly arrived control-strategy, guess-bias and recovery results against saved fits; preserve pulse blinding.
- [x] F. Incorporate verified arrivals into prose and provenance records, check consistency, and report remaining dependencies.
- [x] G. Verify frozen prediction integrity and predicted contrasts; inspect completeness of synthetic strategy sensitivity.
- [x] H. Update the draft and evidence records for prediction-stage findings without examining recorded pulse outcomes.
- [x] I. Verify saved observed gate/strategy results, distinguish first-pass evidence from final fits, and review proposed amendment without adopting it.
- [x] J. Revise manuscript and provenance for the failed predictive gate and inconclusive strategy test; report remaining decisions.
- [x] K. Review pulse design, completed calibration, and primary literature to identify defensible thesis claims and discriminating follow-up analyses.
- [x] L. Record a sourced pulse research synthesis, ranked analysis options, validation criteria, and conditional time estimates; check citations and update status.
- [x] M. Draft a parallel implementation handoff for the existing-data pulse follow-up, with shared data rules, file ownership, dependencies and stopping criteria: [child plan](2026-10-23-pulse-followup-parallel.md). Implementation is tracked there; no analyses launched in this drafting pass.
- [x] N. Review the completed pulse follow-up, earlier evidence and available figures; propose the central paper story and order of Results, with pending model work explicitly separate.
- [x] O. Draft a five-main-figure arrangement with panel purposes, source outputs, supplementary allocation and figure-production dependencies.
- [x] P. Write evidence-linked draft captions for the proposed main figures, preserving analysis populations, uncertainty definitions and exploratory status.
- [x] Q. Verify caption numbers/source links and scientific scope; save a discussion-ready story/figure package and handoff report. Leave existing manuscript/captions intact while the pulse coordinator works. Report: [story/figures/captions](../reports/2026-10-23-story-figures-captions.md).
- [x] R. Adapt the discussion outline for a provisional eLife paper and an expanded thesis chapter, with a structured account of successful, unsuccessful and inconclusive approaches; verify current journal guidance without changing scientific claims. Completed in the story document and [report addendum](../reports/2026-10-23-story-figures-captions.md).

- [x] S. Inspect the supplied SfN 2025 poster visually and extract its framing, figure sequence and scientific claims; compare them with the current evidence. Extracted PDF text and inspected embedded figures; a full-page renderer is unavailable.
- [x] T. Update the story/figure document and caption production notes with useful poster elements and explicit replacements for superseded claims.
- [x] U. Verify the poster provenance, unchanged scientific claim hashes and document links; record the review and handoff without altering active pulse analyses. [Poster review report](../reports/2026-10-23-poster-story-review.md).
- [x] V. Reorganize the committed manuscript around the agreed paper story and integrate the completed exploratory pulse behavioural results, time course and model diagnosis.
- [x] W. Add the corresponding pulse Methods, evidence records, claim registry and numerical consistency entries; keep the tau-p pilot out of the scientific claims until its independent check is complete.
- [x] X. Audit the revised draft for claim/source coverage, numerical consistency, unresolved author facts and journal length; write a [drafting handoff](../reports/2026-10-23-manuscript-story-integration.md).

## Out of scope
Running analyses (tracked in the next-steps plan); editing the poster; the SC WFV inactivation experiments (separate study). Reviewing the old poster for paper/thesis inspiration is authorized under S–U below.

## Log
- 2026-10-23 (Codex; V–X complete): revised `manuscript_2026-10-23.md` around the agreed pulse-centred story; added E024–E029, 22 new claims and a v2 consistency registry. Abstract 193 words; text through Discussion 4,845 words including markers/headings. Source schema, 94 claim hashes/evidence links, local links, consistency registry and whitespace checks pass. Linter retains one explicit hidden-coherence TODO plus expected human/confidentiality warnings. Tau-p pilot remains outside formal claims pending independent review. Report: ../reports/2026-10-23-manuscript-story-integration.md.
- 2026-10-23 (Codex): user authorizes starting the paper draft after committing the prior writing package. Resume at V–X in the existing plan. Use Markdown as the source; integrate A–E/G1, preserve exploratory labels and the failed gates, and defer formal use of the tau-p pilot pending its independent review.
- 2026-10-23 (Codex; S–U complete): extracted the supplied poster text and embedded figures with installed PDF.js; retained its task-first/comparative motivation and recorded superseded inferences, inconsistent pulse colours and denominator corrections. Updated story and caption production notes; E114 records poster provenance. Source schema, ten unchanged claim hashes, local links, original-PDF hash and whitespace checks pass. Full-page rendering unavailable; no packages installed and no new scientific analyses. Report: ../reports/2026-10-23-poster-story-review.md.
- 2026-10-23 (Codex): user asks to review the supplied SfN poster for inspiration/updates after accepting the general paper structure. Resume the writing plan at S–U. Inspect the local PDF and update the writing package; preserve the poster and coordinator-owned analysis files. No new fits or publication figures in this pass.
- 2026-10-23 (Codex; R complete): added provisional eLife guidance, seven-section thesis outline, figure allocation and distinctions among unsuccessful outcomes. Official journal guidance checked; source schema, all ten unchanged claim hashes, local links and whitespace checks pass. No new analysis, figure rendering or coordinator-file edits. Broader manuscript integration remains open.
- 2026-10-23 (Codex): user identifies eLife as a possible journal and asks for a thesis version including what worked and did not. Extend the story document under R; maintain one shared evidence record and distinct paper/thesis levels of explanation. This authorizes drafting, not publication or new analysis.
- 2026-10-23 (Codex; N–Q complete): proposed five-main-figure story and captions saved to dissemination/paper/story_and_figures_2026-10-23.md and figure_captions_story_2026-10-23.md, with source/claim/check records. Numeric C/D/E caption checks, ten claim hashes, local links, source stability and whitespace checks pass. Existing manuscript/captions and analysis coordinator files preserved; report ../reports/2026-10-23-story-figures-captions.md. Next: author discussion, final masks/layouts and manuscript integration. Input-correction/pilot-specification commits arrived during drafting but no evaluated pilot result is used. The broader paper plan remains active.
- 2026-10-23 (Codex): user requests story development, key-results outline, neuroscience figure arrangement and captions. Resume the writing plan at N–Q. Use completed A–E/G1 evidence with the independent-review qualifications; no new modelling or figure rendering in this pass. General neuroscience format is provisional pending target-journal preference. Preserve existing manuscript/figure captions and the pulse coordinator's active analysis files; save versioned drafting documents.
- 2026-10-23 (Codex; M complete): user requested a plan that other agents can implement in parallel. Created the linked exploratory child plan for A–H work packages; drafting handover: ../reports/2026-10-23-pulse-parallel-plan.md. The original primacy procedure stays closed. No workers, model fits, behavioural analyses or cluster jobs launched. This writing plan remains active.
- 2026-10-23 (Codex; K–L complete): existing-data pulse review saved to dissemination/reports/pulse-thesis-research-2026-10-23.md with public query/source JSON. Report: ../reports/2026-10-23-pulse-thesis-research.md. Twelve core primary sources assessed; saved gates/calibration and metadata inventory checked; stimulus reset demonstrated without behavioural fitting. Document/JSON/source-link/reproduction-syntax checks and git diff --check pass. Next: user/researcher settles a bounded exploratory analysis; original primacy procedure remains closed. Main write-up plan remains active.
- 2026-10-23 (Codex): user specifies existing data only for the pulse thesis work. Research recommendations exclude new experiments. Pulse-offset direction reset is verified in both replay implementations by a deterministic stimulus-only check; its effect on behavioural conclusions remains unquantified and is a priority validation question.
- 2026-10-23 (Codex): user requests deep research on making pulses a concrete thesis contribution. Resume this writing plan with a targeted critical literature review and read-only implementation audit. This authorizes research and a local handover report, not new fits, cluster submissions, or reopening the closed confirmatory primacy procedure. Any new modelling is a proposed exploratory follow-up.
- 2026-10-22 (Codex; gate review complete): saved outputs verified; observed gate/strategy Results, Abstract and Discussion updated with evidence records. Registry consistency, claim hashes/source links and whitespace checks pass. Report: ../reports/2026-10-22-observed-gate-review.md. No new analysis or amendment adoption. Next: author decision on draft amendment and final-fit evaluation; timing claims remain withheld.
- 2026-10-22 (Codex; gate-result pass): user requested latest update, source b027a4c. Read completed gate and strategy summaries only; no new timing contrasts, fits or amendment adoption. Amendment 6 remains draft.
- 2026-10-22 (Codex; prediction pass complete): thirty frozen hashes checked; completed strategy sensitivity has low primary discrimination (1/20 extrema, 0/20 integrator). Manuscript/source/claim/numeric records updated; consistency/hash/link/whitespace checks pass. Report: ../reports/2026-10-22-prediction-sensitivity.md. Recorded pulse analysis not performed; original gate/testing order remains intact.
- 2026-10-22 (Codex; frozen-prediction pass): user reports further analysis; source snapshot 002fafb. Inspect frozen predictions and synthetic sensitivity only, update manuscript, and leave outcome analyses in the agreed order.
- 2026-10-22 (Codex; results arrival pass complete): verified saved scores/recovery without pulse-outcome inspection; manuscript and source/claim/numeric records updated. Numeric-registry, paragraph-hash/source-reference and whitespace checks pass. Report: ../reports/2026-10-22-arriving-results.md. Next scientific dependency: strategy sensitivity and frozen pulse predictions, then planned pulse comparisons; paper remains unfinished.
- 2026-10-22 (Codex; results arrival pass, source 17511ca): user reports new results. Resume with saved-fit verification and manuscript updates. New decisions/results in analysis log section 5.8; no refits, cluster submissions or pulse-outcome analysis in this pass.
- 2026-10-22 (Codex; first prose pass finished): manuscript_2026-10-22.md and source/claim/consistency records added; Introduction, established Results and Methods drafted, pending strategy/temporal-weighting results explicit. Captions corrected for censoring; images not regenerated. Source schema, numeric consistency and reference syntax checks pass; human verification and missing-content gates intentionally incomplete. Report: ../reports/2026-10-22-paper-first-draft.md. This writing plan remains active until analyses, figures, author facts and final verification are complete.
- 2026-10-22 (Codex; client date): user confirmed strategy discrimination as primary, primacy as secondary, and authorized manuscript work. Hyak jobs are queued. Resume this plan, without starting a parallel plan. Existing entries dated 2026-10-23 are preserved as prior records. Hidden-coherence shared profile interval is conditional on a common ratio; the saved across-mouse paired test gives p = 0.492 and does not establish a consistent population discount. Draft accordingly. Journal, authorship, and animal details remain missing and do not block an explicitly incomplete local draft.
- 2026-10-20: outline written. `.agents/` created for the first time; earlier tracking lives in dissemination/reports.
- 2026-10-20: outline updated from the SfN 2025 poster (framing, figures, authors/funding, references). Flagged: poster primacy claim needs the model-based test; WFV inactivation proposed for a separate paper; session count (26 vs 219) to resolve.
- 2026-10-20: WFV inactivation excluded from this paper (V. Thakur: a different study).
- 2026-10-20: Figs 1-2 drafted (scripts/paper/, figures in dissemination/paper/figures/, captions in figure_captions.md). Fig 1 restyled to follow the SfN poster (pooled psychometric, pulse coherence traces, trial timeline) at the user's request. Found: poster's "26 sessions" is a counting bug (session labels shared across mice); 50 mouse-sessions. Next: Fig 3 (hidden coherence).
- 2026-10-22: outline R4 now lists how the two common-model choices (strict vs relaxed) change the story; S2/S4 results final (figures to make). Common model still to be chosen by the authors.
- 2026-10-22: outline revised after the model choice, leak/urgency diagnosis and primacy power report: R5 split into gate-1 branches (a/b/c); censored trials = late responses; Fig 1F relabel and pre-gate design simulation proposed.
- 2026-10-23: outline updated after reviewing Stine et al. 2020 (integration vs extrema detection as core question 5); draft amendment 4 written to dissemination/reports/primacy-amendment-4-DRAFT.md, awaiting the authors' decision (must be committed and run before gate 1).
- 2026-10-23: manuscript_2026-10-23.md (new version; 10-22 kept): amendment 6 revision, failed revised gate, calibration and
  stopping decision added (claims C071–C077, evidence E022, facts N030–N044; claim hashes recomputed). Outline R5 set to
  branch (a2). Notebook 2.14 section 6 removed; its figure moved to dissemination/figures/superseded/.
