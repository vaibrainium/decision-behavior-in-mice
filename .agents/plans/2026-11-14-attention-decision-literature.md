# Plan: attention and decision variability literature review
Status: done
Created: 2026-11-14 by Codex
Related reports: ../reports/2026-11-14-response-delay-pilot.md; ../../dissemination/reviewer_2026-11-12/LITERATURE.md
Completed report: ../reports/2026-11-14-attention-decision-literature.md

## Goal
Produce a source-verified critical literature synthesis that ranks the next existing-data analyses and compact model comparisons for the pulse/choice/RT mismatch. Distinguish computational hypotheses from evidence for attention or a neural mechanism.

## Context
The variable postdecision-delay pilot did not resolve the mismatch. Positive gain variability was proposed, not established. The user now requests a broader decision-making/attention literature review to decide what to do. No further experiments are possible.

## Assumptions
- This is a focused critical narrative review, not an exhaustive systematic review or meta-analysis.
- Primary empirical and theoretical reports carry the scientific claims; reviews help discovery only. Check recent studies and preprint/publication status.
- Existing reports and analyses are evidence to build upon, not tasks to repeat without checking.
- No model fits, package changes, cluster jobs, experimental-data uploads, external AI services, or modifications of historical results are needed for this review.

## Steps
- [x] 1. Read relevant prior findings, identify existing state/history analyses and available behavioral variables, and record the search scope.
- [x] 2. Search and verify primary sources across accumulation, attention/gain, engagement states, sensory transients, sequential history, and identifiability; save search provenance and accessible full texts/metadata.
- [x] 3. Extract findings, limitations, applicability and discriminating existing-data predictions into an evidence matrix; distinguish full-text from abstract-only assessment.
- [x] 4. Write an integrated review and ranked, concrete analysis/model plan with an honest publication-level claim ladder.
- [x] 5. Verify references and scientific/source traceability, save the report, update STATUS, and explain the decision clearly to the user.

## Out of scope
New experiments; calling a fitted gain variable 'attention' without independent evidence; unvalidated latent-state mechanisms; automatically trying every candidate; exporting unpublished material.

## Log
- 2026-11-14: User requested the literature review after the completed response-delay pilot. Reading existing synthesis and scientific skills; new scope emphasizes attention, state dependence and sensory/decision confounds.
- 2026-11-14: Retrieved selected metadata from Europe PMC and fresh Crossref records for the new synthesis, plus 10 OA XML bodies; author PDFs/PMC web pages recovered several XML failures. Browser bot challenges and Europe PMC HTTP 500 failures are recorded, not interpreted as absent evidence. Scope is a focused narrative review; no screening-completeness claim.
- 2026-11-14: Existing mouse history results are substantial and generic GLM-HMM code exists, but an audited mouse state/RT/pulse fit was not located in reviewed reports or processed directories. The aligned trial table supplies previous choice/outcome, trial position, session and schedules; it has no pupil/movement columns. Generic GLM-HMM code includes a different human/color-task context, so do not assume it is a ready validated mouse analysis.
- 2026-11-14: Literature changes the recommended order: history and state structure before interpreting iid gain as attention. Urai 2019 motivates ongoing drift-bias vs starting-point comparisons; Ashwood 2022/Hulsey 2024 motivate state checks with independent outcomes; Goris 2014 shows gain can be temporally correlated. McGaughey & Gold 2026 gives a recent RDK encoding-versus-integration comparator; its observational neural/pupil links do not identify the mechanism here.
- 2026-11-14: Completed REVIEW, NEXT_ANALYSES, evidence matrix and a 32-record bibliography with 26 fresh DOI identity checks. Existing system Python supplied the citation tool's missing dependency; no packages changed. Verified bibliography fixes page ranges/article locator/preprint type, preserves collective authors and genuine article identifiers. Source access failures and narrative-selection limits documented. No new fits or behavioral statistics; report and STATUS updated.
