# Plan: write up the mouse primacy / DDM paper
Status: active
Created: 2026-10-20 by Claude (Opus 5.5)
Related reports: dissemination/reports/mouse-ddm-analysis-log.md, dissemination/reports/mouse-ddm-next-steps.md,
dissemination/reports/primacy-analysis-plan.md

## Goal
A full manuscript draft in `dissemination/paper/`, built from the outline in `dissemination/paper/outline.md`, with every
number traceable to a report, notebook or script.

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
- [ ] 4. Draft Methods: task/rigs, trial labelling, motion energy, hidden coherence.
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

## Out of scope
Running analyses (tracked in the next-steps plan); the poster; the SC WFV inactivation experiments (separate study).

## Log
- 2026-10-20: outline written. `.agents/` created for the first time; earlier tracking lives in dissemination/reports.
- 2026-10-20: outline updated from the SfN 2025 poster (framing, figures, authors/funding, references). Flagged: poster primacy claim needs the model-based test; WFV inactivation proposed for a separate paper; session count (26 vs 219) to resolve.
- 2026-10-20: WFV inactivation excluded from this paper (V. Thakur: a different study).
- 2026-10-20: Figs 1-2 drafted (scripts/paper/, figures in dissemination/paper/figures/, captions in figure_captions.md). Fig 1 restyled to follow the SfN poster (pooled psychometric, pulse coherence traces, trial timeline) at the user's request. Found: poster's "26 sessions" is a counting bug (session labels shared across mice); 50 mouse-sessions. Next: Fig 3 (hidden coherence).
- 2026-10-22: outline R4 now lists how the two common-model choices (strict vs relaxed) change the story; S2/S4 results final (figures to make). Common model still to be chosen by the authors.
- 2026-10-22: outline revised after the model choice, leak/urgency diagnosis and primacy power report: R5 split into gate-1 branches (a/b/c); censored trials = late responses; Fig 1F relabel and pre-gate design simulation proposed.
- 2026-10-23: outline updated after reviewing Stine et al. 2020 (integration vs extrema detection as core question 5); draft amendment 4 written to dissemination/reports/primacy-amendment-4-DRAFT.md, awaiting the authors' decision (must be committed and run before gate 1).
