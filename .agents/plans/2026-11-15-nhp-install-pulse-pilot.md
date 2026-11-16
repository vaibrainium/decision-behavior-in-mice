# Plan: install pinned NHP SSM and run a small pulse-state pilot
Status: done
Created: 2026-11-15 by Codex
Related reports: ../reports/2026-11-15-nhp-ssm-target-congruency.md; ../reports/2026-11-15-nhp-pulse-hmm-pilot.md

## Goal
Install the author-approved pinned SSM fork in an isolated environment, verify its semantics, and complete a bounded two-mouse comparison asking whether state-specific pulse weights improve future choice prediction beyond changing baseline/history weights.

## Context
NHP lock pins vaibrainium/ssm at a109af369797d852904fd9496f3532524de8f15a. Existing input exports preserve logged rows/masks. Six physical and six target-relative feature sets both exist. User authorized installation/starting work, then latest asynchronous selection requested physical direction × time inputs and nonzero-coherence congruency summaries.

## Assumptions
- Latest selection governs primary fit: six physical direction × onset-stage inputs, control reference. Target congruency remains an annotation; retain zero-coherence trials.
- PSUIM6/7 pilot only, identical retained choices/masks, original logged session rows. No raw-data modification or changes to existing DDM environment/results.
- Fit one-state GLM, two-state HMM with pulse coefficients tied across states, and two-state HMM with pulse coefficients free. Shared stimulus/history features, training-only starts/prior selection; pre-choice filtering for future blocks.
- RT and pulse summaries are external checks, not additional independent likelihood terms or attention labels. No population claim from two mice; no recovery/Neuron-ready claim from this pilot.

## Steps
- [x] 1. Create isolated environment; install pinned build tools/requirements; record resolved environment and Git provenance.
- [x] 2. Run source/semantics smoke test; repair only necessary compatibility issues with auditable versions.
- [x] 3. Implement NHP-fork masked EM pilot, tied/free pulse constraints, log-transition starts and coefficient sign conversion; freeze scoring/split and optimization budget before fitting.
- [x] 4. Run/check prefix-held-out pilot and training-only optimization/regularization checks. Report inactive pulse types and all unsuccessful starts.
- [x] 5. Assess choice prediction, unused current RT and pulse adequacy; save figures, report, environment/provenance and STATUS.

## Out of scope
System-wide installs, changing the DDM environment, cluster submissions, new experiments, automatic large-cohort/state-count searches, or inferring attention/integration memory from a choice-only state fit.

## Log
- 2026-11-15: Complete. Final report ../reports/2026-11-15-nhp-pulse-hmm-pilot.md; final outputs dissemination/nhp_pulse_hmm_2026-11-15/assessment_v2 and RESULTS.md / pulse_hmm_pilot_final.pdf. Shared-pulse HMM improves choice prediction; state-specific pulse weights worsen PSUIM6 and are unresolved in PSUIM7. RT validation is model/mouse dependent. No full-cohort expansion, recovery or joint-RT mechanism claim. Installation/runtime checks, all 132 fits and source/input identity audits complete.
- 2026-11-15: Training audit: all 108 fits converged and no observation M-step failed. Some starts reach distinct local optima; PSUIM7 outer4 tied has a substantially better mode reached by only one of four bias-oriented starts. Before inspecting test comparisons, add two explicitly sensitivity-oriented starts to each of twelve selected two-state outer models, using training data only and keeping the already selected priors fixed. This is an optimization robustness check, not held-out model tuning. Retain original outputs and report any prediction changes.
- 2026-11-15: All 108 prescribed fits and eighteen outer model blocks completed. Selected priors were chosen using the inner block only. Before reading test score differences, assessment endpoints fixed: per-mouse free-minus-tied choice bits primary, tied/free versus static secondary; current-log-RT association with pre-choice higher-coherence-contrast state; marginal congruency accuracy contrasts on nonzero coherence, without RT stratification. No population p-values from two mice. Use 600 within-session fifty-saved-record block resamples conditional on fitted models; report their limited uncertainty target.
- 2026-11-15: Installed-fork smoke and independent constrained-emission tests passed, including numerical gradients/Hessian and a separate optimizer. Exact NHP fork supplies likelihood, masking, forward/backward and EM; only unique-parameter Gaussian prior / binary M-step specialize coefficient sharing. Actual final model objective is used for start selection because the fork's progress trace combines a previous E-step likelihood with an updated prior. No fork source patched.
- 2026-11-15: Pinned fork and modeling dependencies installed successfully in /mnt/data/venvs/nhp-glmhmm-2026-11-15 (Python 3.10.12). Resolved environment saved in dissemination/nhp_pulse_hmm_2026-11-15/environment_freeze.txt; runtime semantic/emission checks started.
- 2026-11-15: Pilot specification frozen before real fits: priors sigma {1,2,5}; select each model's prior using first-20%-to-next-20% prediction, then fix it for 40/60/80%-prefix outer fits. Four deterministic training starts per HMM, one convex GLM start; up to 200 EM iterations in 20-step chunks, actual post-update log_probability tolerance 0.001. Shared session intercepts/position terms in every state; pulse weights tied vs free, other baseline/history weights may vary. Missing rows have no emission but retain transitions. Late pulse types are absent in PSUIM6/7 and are not estimable.
- 2026-11-15: Existing uv can install into the Python 3.10 interpreter without ensurepip. Pinned build tools installed successfully; exact Git-fork runtime installation underway. System/DDM environments unchanged.
- 2026-11-15: Python 3.10 venv creates the isolated interpreter but cannot bootstrap pip because system ensurepip is absent. Prefer an existing uv installer to installing system packages; checking that alternative now.
- 2026-11-15: User authorized starting the prepared isolated install. Most recent asynchronous selection supersedes the task-target input choice for the primary fit; preserve target export as an alternate annotation/data artifact.
