# Status
Last updated: 2026-10-29 by Claude (Opus 5.5; joint control + pulse refits)

## Current focus
Joint control + pulse refits done (reports/2026-10-29-joint-control-pulse-refits.md): fitting pulses does not make any family reproduce the pulse effect; next decision: race-model illustration (author).
Leak vs urgency from pulse trials (author question 2026-10-28): research done, plan done. Verdict: existing descriptive
signatures cannot separate them; the pulses are informative in principle (S1 profile separates leak >= 1 /s from the
leak-free model by 2-10 SE in PSUIM6/7) but no family member reproduces the observed sustained 0.3-1.2 s effect without a
late reversal, so a joint (L, u, w) fit would fail falsification before deciding L vs u. Route with stop rules proposed;
author to fix thresholds (reports/2026-10-29-pulse-leak-vs-urgency.md; literature:
dissemination/reports/pulse-leak-vs-urgency-literature-2026-10-29.md).
S6 panel review complete: roadmap `dissemination/paper/np/panel/roadmap.md` (simulated major revision, 7 P0/14 P1/3 P2). Waiting at G5 for author disposition (`np/checkpoints/G5.md`).
Manuscript-facing text converted to American spelling (D010; spine re-locked; `scripts/paper/americanize_spelling.py`); Fig 2 v6 / Fig 3 v5 re-exported with US labels (data identical). Plan done.
G4 is approved and the exact N105–N107 Methods patch is applied. The manuscript has been assembled, independently
coherence-reviewed and repaired without scientific-scope changes. Supplementary Figure S6 v2 is selected with adjacent
source tables and audited denominator record N108. Integrity audit 1 passed after a bounded-fix recheck.
The exploratory pulse follow-up status is unchanged: the tau_p pilot failed its frozen criteria and modelling stopped;
its independent check remains pending before any formal manuscript claim.

## Previous focus
Older draft dissemination/paper/manuscript_2026-10-22.md includes first-pass gate failures and predates adoption of amendment 6. Newer draft: manuscript_2026-10-23.md. Timing tests remain withheld after both revised gates failed.
Primary paper question: integration versus extrema detection; primacy secondary, conditional on adequacy/sensitivity.

## Active plans
- plans/2026-10-29-pulse-weight-joint.md : free pulse weight, sv and no-sv, 10 mice cv + all; Hyak job 42579333 (120); next: pull, readout; then LCA illustration
- plans/2026-10-29-control-paper.md : third paper (control trials only, Stine 2020 framing) in dissemination/paper_control/; G0 approved; descriptives done; paired recovery submitted (job 42579825); S1 spine drafted, devil's advocate running
- plans/2026-10-28-full-recovery-matrix.md : ON HOLD (author); recovery rerun on fixed CPU datasets if it becomes necessary
- plans/2026-10-26-v2-refits-and-strategy-recovery.md : responded-only refits + full point-3 re-run (amendment 9); commands ready; next: user syncs code, submits R1-R6 (460), then F1a (80) and P1-P4 (850)
- plans/2026-10-26-paper-accumulation-variant.md : second paper version (accumulation-first) in dissemination/paper_accumulation/; G1 held; waiting on v2 refits + E-recovery (plans/2026-10-26-v2-refits-and-strategy-recovery.md)
- plans/2026-10-23-pulse-followup-parallel.md : A-E, G1, F3 pilot done (FAIL -> modelling stopped); next: H2 check of pilot, H4 finalize; original primacy procedure remains closed
- plans/2026-10-23-amendment-4-extrema.md : code done and checked; next: Hyak fits (commands in analysis log 8.4d)
- plans/2026-10-22-primacy-analysis-code.md : done; next: predictive check (gate 1) first pass when 8.4c batch 1 lands
- plans/2026-10-20-paper-writeup.md : Methods/Results/legends passed; next: mandatory author midpoint verification, then Discussion drafting
- ../dissemination/reports/mouse-ddm-next-steps.md : analysis plan (kept in dissemination/reports); steps 0–3 done
  (3.3 confirmed the strict model); next: guess-bias fits, fit quality, gate 1 first pass, recovery (jobs running)

## Recent reports (newest first, keep about 10)
- reports/2026-10-29-heldout-choice-rt-split.md : held-out table reproduced by control_heldout.py; C advantage mostly RT terms (vs ES choice part ~0); small consistent choice advantage over E only; robust to leave-one-mouse-out
- reports/2026-10-29-pulse-race-lca-illustration.md : race and LCA variants (incl. baseline LCA of Kirkpatrick et al. 2021), matched to control trials in 3 mice, predict 2.7-5.1 pp vs 13.1 pp observed; no reversal; architecture does not fix the size problem
- reports/2026-10-29-likelihood-ignores-trial-me.md : held-out likelihood is pooled per coherence, so it never uses trial-by-trial motion energy (shuffle = seed noise); shuffled-ME ablation is a no-op; RT terms are ~80% of NLL
- reports/2026-10-29-control-descriptives.md : control trials: RT falls with coherence (Holm 0.06), errors 118 ms faster (Holm 0.06; common model under-predicts, exploratory), ME kernel ~0.1-0.3% coh, null and underpowered; paired CPU recovery datasets ready (80, sha256)
- reports/2026-10-29-joint-control-pulse-refits.md : 12 families refit on control + pulse trials: ranking unchanged (L1U1 -72 sum, 2/10 mice), parameters ~1.0x control fits (UCLA shift not reproduced); no family reproduces the pulse effect (2.3-4.5 vs 5.48 pp at 0.3-1.2 s); late reversal only with sv/leak; addendum: sv causes the reversal (dose-response, eta selection 10/10 mice) and also cuts the early effect 16.4 -> 5.2 pp at fixed gain
- reports/2026-10-29-ucla-pulse-me-nofreeze.md : removing the UCLA replay freeze raises the UCLA pulse x1.13-1.15 (UW/UCLA 1.65 -> 1.45, ~pulse length); new inputs ddm_inputs_global_ucla_nofreeze.npz; DDM kernel verified; pulse moves the fitted decision variable only 2-4% of the bound
- reports/2026-10-29-pulse-descriptive-package.md : 10 mice: pulse effect in responses 0.3-1.2 s after the pulse 5.5 pp [0.8, 10.2] (Holm 0.08), none after 1.2 s (1.2 [-2.8, 5.2]); no reversal in PSUIM6/7 but DBM6 reverses; S2 uninformative
- reports/2026-10-29-pulse-leak-vs-urgency.md : pulse tests of leak vs urgency: what was tried, literature verdict, feasibility illustration (SR1 passes in 2 dense mice; every variant mis-predicts the 0.9-1.2 s bin and the late window), calibrated route with stop rules SR1-SR5
- ../dissemination/reports/pulse-leak-vs-urgency-literature-2026-10-29.md : literature synthesis (62 DOIs): first-order pulse signatures are shared by all bounded integrators; leak identifiable only above ~1 /s with NDT pinned; design S1-S3 + (L, u, w) inference + recovery grid
- reports/2026-10-28-pulse-time-comparison.md : no within-mouse change of the pulse effect across pulse times (Bayes early-middle 0.14 log-odds [-0.08, 0.37]; per-mouse Holm >= 0.27); late looks smaller only because its 6 mice have small effects throughout
- reports/2026-10-28-pulse-direction-by-time.md : right vs left pulse per pulse time; bias differs (early -17.1% coh, Holm 0.047 over 6, post hoc family; middle -12.4, Holm 0.10; late n.s.), slope does not
- reports/2026-10-28-pulse-psychometric-parameter-bootstrap.md : per-stage bootstrap on psychometric bias/slope; early congruent-incongruent slope +0.040 (Holm 0.022) and early right-pulse bias -15.1% (Holm 0.011); rest n.s.
- reports/2026-10-28-pulse-congruency-tests.md : congruent 3.0 pp (Holm 0.096) and incongruent 3.6 pp (0.39) pulse effects each non-significant; positive-vs-negative (7.52 pp, Holm 0.012) pools both
- reports/2026-10-28-recovery-synthetic-data-mismatch.md : BUG: recovery candidates scored on different synthetic data (GPU-dependent synthesis); F1a k=5, ES and ESx/DDMx recoveries invalid until rerun on fixed CPU datasets
- reports/2026-10-28-stine-exact-models.md : paper-exact Stine models barely differ (ESx-DDMx 62.7, DDMx 3/10, ESx 0/10), pulse test not distinguished, recovery weak; both fit far worse than the common model (C better 6/10)
- reports/2026-10-27-f1a-strategy-recovery-responded.md : F1a k = 5/20 E-generated datasets scored as accumulator (genuine, not optimizer) -> THESIS_B under D002; E vs C on real data 278.9 (C 5/10, E 0/10); E pulse strategy test not distinguished
- reports/2026-10-27-pulse-readout-model-rt-split.md : primary model gets the RT shape of the pulse effect right but is too weak at RT ~0.5-1.3 s and predicts a late reversal the data lack
- reports/2026-10-27-pulse-readout-bias-checks.md : readout-bias (slow-trial) account not supported: pulse effect in fast-middle RTs, slow ±100% trials most accurate, pulse-direction choices faster
- reports/2026-10-27-pulse-asymmetry-lapse-checks.md : no congruency asymmetry beyond models (0.54 ± 3.22 pp) once asymmetric UW cells are dropped; ±100% excess errors are slow, not fast guesses
- reports/2026-10-27-pulse-psychometric-variants.md : all 7 responded-only variants underpredict pulse effects (0.35-1.9 pp vs observed 2.0 congruent / 4.0 incongruent)
- reports/2026-10-27-pulse-effect-vs-coherence-change.md : pulse effect vs coherence change inconclusive (slope 0.27 [-0.16, 0.69] logit/100%; design range too narrow)
- reports/2026-10-27-pulse-me-old-vs-new-filter.md : pulse ME difference from nb 2.11 is the intended filter change (old filter non-causal), not a bug
- reports/2026-10-27-pulse-contrast-responders-only.md : (src-46) pulse effect holds without no-response trials: pos vs neg 5.84 -> 7.52 pp [2.73, 12.30], Holm 0.012; pulse does not change response rate (p 0.086)
- reports/2026-10-26-fluctuation-kernel-observed.md : amendment 8 response-aligned kernel on real choices: neither model fits (inconclusive; not used as support)
- reports/2026-10-26-neuropaper-s5-s6.md : G4 recorded; S5 assembled/coherence-repaired; S6 v2 selected with exact gate, coverage and calibration denominators
- reports/2026-10-26-neuropaper-s4-g4.md : all six S4 sections passed; G4 awaits approval plus an exact N105–N107 Methods provenance reconciliation
- reports/2026-10-26-figure-notebooks.md : five executable, panel-by-panel figure notebooks wrap canonical modules without writing publication outputs
- reports/2026-10-26-main-figures-1-2.md : Figures 1–2 selected; N105–N107 close main-art denominator mappings and the five-figure package is reconciled
- reports/2026-10-26-main-figures-3-5.md : selected Figures 3–5 assembled with vector/300-dpi exports, source data and artwork-matched captions
- reports/2026-10-25-results-narrative-rewrite.md : Results v4 uses a natural question-to-result narrative; all claims,
  tokens and scientific boundaries preserved; deterministic checks pass; author verification pending
- reports/2026-10-25-fluctuation-kernel-power.md : synthetic: fluctuation kernels have no power for primacy; response-aligned index separates integrator vs E (20/20 each); amendment 8 decision pending
- reports/2026-10-25-neuropaper-wave1-review.md : legends PASS; Methods/Results need bounded correction after two rounds; no new analysis required
- reports/2026-10-25-neuropaper-outline-g3.md : five-figure outline and six briefs pass independent K1-K12 review; G3 author approval pending
- reports/2026-10-24-neuropaper-literature-g2.md : 44 verified sources; broad mouse novelty rejected, narrow predictive-transfer gap survives; C010-C021 approved at G2
- reports/2026-10-23-pulse-tau-pilot-20261023T191030Z_fa8de8b.md : tau_p pilot FAIL (fit improves at 300 ms but gains stay 2.3x apart and late reversal persists); modelling stopped
- reports/2026-10-23-pulse-diagnostics-20261023T191030Z_fa8de8b.md : existing model misplaces the pulse effect in time (early, then reverses; data delayed and sustained); choice-RT gain tradeoff demonstrated in 2 mice; proposes one tau_p candidate
- reports/2026-10-23-pulse-validation-g1-20261023T191030Z_fa8de8b.md : t intervals adequate (coverage 0.93-0.975); power 0.64 at 6 pp; bootstrap undercovers
- reports/2026-10-23-pulse-stimulus-20261023T191030Z_fa8de8b.md : no sign-aligned post-pulse stimulus bias except a one-dot rounding shift; UCLA pulse energy possibly x1.3-1.4 understated
- reports/2026-10-23-pulse-response_time-20261023T191030Z_fa8de8b.md : pulse-aligned curves: +5.8 pp direction, emerging 0.5-2 s; no common latency effect (review: reports/2026-10-23-pulse-review-D-...)
- reports/2026-10-23-pulse-behaviour-20261023T191030Z_fa8de8b.md : scheduled pulse Delta_direction +5.84 pp [1.80, 9.89], 10 mice, Holm p = 0.019
- reports/2026-10-23-pulse-data-20261023T191030Z_fa8de8b.md : pulse contract frozen; assignment verified randomized from task source; 48 UCLA no-response pulses mislabelled control in DDM inputs (43 recovered); UW asymmetric-coherence schedule flagged
- reports/2026-10-23-pulse-parallel-plan.md : parallel handoff drafted with explicit ownership, common data contract, minimum behavioural deliverable and conditional mechanism validation; no implementation launched
- reports/2026-10-23-pulse-thesis-research.md : existing-data pulse research synthesis; replay offset redraws noise directions, physical counterfactual validation needed; joint choice/RT route proposed
- reports/2026-10-23-amendment-6-result.md : revised gate fails; timing test calibrated but powerless; primacy not
  answerable with these pulses
- reports/2026-10-22-observed-gate-review.md : both first-pass gates fail; strategy z=2.966 remains not distinguished; proposed pulse-gain revision reviewed, not adopted
- reports/2026-10-22-prediction-sensitivity.md : all frozen hashes match; pulse-specific test selects generator in 1/20 extrema and 0/20 integrator simulations; observed pulse analysis pending
- reports/2026-10-22-arriving-results.md : independently verified control preference for integrator, free guess bias and completed recovery; manuscript updated; pulse predictions/comparison pending
- reports/2026-10-22-paper-first-draft.md : first manuscript prose; qualified hidden-coherence population claim, separated analysis sets; final strategy results pending
- reports/2026-10-23-control-only-selection.md : strict model holds under control-only CV (sv, guesses needed;
  leak/urgency not); batches 1, 3b and recovery resubmitted
- reports/2026-10-22-primacy-power.md : primacy pipeline built (synthetic-only checks); predicted pulse effect
  ~0.025 logit, so the timing test has ~no power under the fitted model; decision pending
- reports/2026-10-22-leak-urgency-diagnosis.md : leak/urgency gains are specific to PSUIM5/6/7 and mostly fit the
  coherence-flat rate of > 5 s responses (likely late engagement); not a power issue
- reports/2026-10-21-ddm-common-model-selection.md : sv and fast guesses pass the noise threshold in most mice; leak
  and urgency only in the 3–4 best-sampled mice; sz out; fast_only guess form preferred
- ../dissemination/reports/primacy-analysis-plan.md : locked confirmatory primacy plan (commit aeb0a22), 2 amendments
- ../dissemination/reports/mouse-ddm-analysis-log.md : full analysis log (ME, hidden coherence, DDM generations)
- ../dissemination/reports/motion-energy-methods.md : motion-energy method review and corrections

## Known issues
- 2026-10-29: all-trial (control + pulse) responded-only fits differ from control-only fits in the 4 UCLA mice (median ratio a 0.82, drift_gain 0.85, sv 0.76, ndt 1.9) but not in UW (about 1.0). The parameter table parameters_common_model_resp_2026-10-27.md uses the all-trial fits. UPDATE 2026-10-29: not reproduced by the joint no-freeze refits (primary ratios ~1.0; equal-NLL fits with different parameters = ridge; reports/2026-10-29-joint-control-pulse-refits.md). Cause not identified: UCLA pulse ME understated only 1.13-1.20x (reports/2026-10-29-ucla-pulse-me-nofreeze.md; refit deferred) or pulse misfit pressure; rig and mouse are confounded. Until resolved, compare mice on control-split fits or show both.
- 2026-10-29: paired-recovery fix implemented (4dbef52; CPU datasets in processed/ddm/recovery_datasets_cpu_2026-10-29); rerun not yet submitted.
- 2026-10-28: all strategy recoveries (F1a, ES, ESx/DDMx, cross matrix) are unpaired: synthetic data differ between candidates (63/80 datasets). F1a k = 5 / THESIS_B provisional (reports/2026-10-28-recovery-synthetic-data-mismatch.md). Old 500-fit variant recovery also suspect (GPU synthesis; not checkable). Fix + rerun pinned by author; do not cite recovery results meanwhile.
- 2026-10-27 author rule: trials without a response by 5 s (435 no RT + 4,102 RT > 5 s = 4,537) must not enter any analysis. All existing DDM fits, gates, calibration, pulse-gain diagnostics and the primary pulse contrast (1,709 unresponded) included them; superseded for the accumulation-first paper by responded-only refits (--responded_only). The first paper version is not yet redone.
- DDM inputs label 48 UCLA no-response pulse trials as controls (direction lost in notebook 0.0); the 15 trials dropped for invalid duration are responses during the pulse (outcome-dependent). Existing inputs unchanged (pulse-data report).
- UW: one |coherence| per session (18% or 36%) schedules only rightward pulses; excluded from signed and pulse-vs-control contrasts (pulse-data report).
- Both replays redraw noise directions at pulse offset; removing the mean pulse component is not a physical no-pulse
  replay. The paired physical-omission audit found identical pre-onset streams, post-offset random-stream divergence and
  no resolved late sign-aligned mean at the audited sample size (pulse-stimulus report; Figure 2D).
- Primacy: original and revised gates FAIL; timing test not run; calibration shows ~no power at 10-40% decay. Final
  under amendment 6 item 8 (analysis log 5.11; reports/2026-10-23-amendment-6-result.md).
- Historical first-pass gates failed (departure +0.30 logit vs predicted effect 0.03), using preliminary control fits and one divergence each; superseded by the completed amendment 6 gate review for current status.
- Pulse-specific strategy test has low sensitivity under frozen fitted candidates (1/20 extrema, 0/20 integrator correct); predicted effects differ by ~0.01 logit. Do not infer equivalence or independent pulse confirmation from an inconclusive result.
- Recovery: sv false-positive rate 7/20 at working threshold; guess-delay parameter poorly recovered. sv bounds and high-coherence error/late-response misfit limit mechanism interpretation (arriving-results report).
- Hidden-coherence k = 0.50 is a shared-model estimate; paired across-mouse coefficient comparison p = 0.492. Notebook controls use RT-dependent labels; scheduled-control sensitivity remains pending (first-draft report).
- Manuscript contains explicit pending/missing sections and unverified author-source records; selected main artwork is
  indexed separately in `dissemination/paper/figures/figure_build_2026-10-26.md`.
- Primacy test: predicted pulse effect ~0.025 logit; test likely cannot detect primacy (analysis log 5.7).
- Psychometric lapses (9–53%) are not captured by the fitted lapse; high-coherence errors probably absorbed by sv.
- Screen geometry not corrected in ME (ME methods §3.7).

## Decisions
- 2026-10-28: D010 pulse effects reported as right vs left (per pulse time, psychometric bias/slope bootstrap); congruency framing dropped (reports/2026-10-28-pulse-direction-by-time.md).
- 2026-10-27: exclude all trials without a response by 5 s from every analysis (V. Thakur: "both of these trials should not have been considered for any analysis"); likelihood made conditional on a response by 5 s.
- 2026-10-26: approved G4 with the bounded N105–N107 Methods patch and the order S5 assembly, S6 artwork, then panel review (D009).
- 2026-10-26: approved Discussion v1 and continuation (“approved and continue”); recorded D008 and authorized
  Introduction drafting.
- 2026-10-25: approved Results v4 narrative rewrite (“approve the revised Results”); recorded D007, returned Results
  to passed and closed the mandatory S4 midpoint review.
- 2026-10-25: approved the exact S4 three-item direct patch and waived a fourth formal review (D006); automated checks passed and first-wave sections are at midpoint.
- 2026-10-25: authorized one bounded Methods/Results v3 correction and final review beyond the neuropaper two-round default; no new analysis.
- 2026-10-25: amendment 7 (visual front end) stopped after the control-trial selection (F1 power law chosen,
  compressive); 7a not adopted; no pulse gate. Primacy analysis closed; focus on the write-up.
- 2026-10-25: revised neuropaper G3 approved as written; five-main-figure outline, 4,980-word main-text budget, mandatory S6 record and indicative title style authorized for S4 drafting.
- 2026-10-25: revised neuropaper G2 approved as written; 44-source literature gap and C010-C021 approved, with broad mouse novelty rejected and no spine change.
- 2026-10-24: G1 approved (“Looks good”); locked neuropaper spine frames relative control-model support plus failure of strong-pulse predictive transfer, with nine own-result claims approved.
- 2026-10-24: G0 approved as written; eLife is the provisional target, V. Thakur approves gates, and unpublished material remains local unless explicitly authorized.
- 2026-10-23: user chose the reduced tau_p pilot with corrected inputs v2; pilot failed its frozen criteria -> modelling stops within this plan (tau-pilot report).
- 2026-10-23: pulse follow-up implementation authorized by the user (A–E + H behavioural package; recommendation before F/G; no jobs/installs). Contract v2 frozen from metadata and task code before any effect estimate (pulse-data report).
- 2026-10-23: user requested a parallel implementation plan for the existing-data pulse follow-up. Draft saved in plans/2026-10-23-pulse-followup-parallel.md; this request did not launch analyses or authorize cluster submissions. Proposed new analyses remain exploratory and separate from the closed primacy protocol.
- 2026-10-23: user requires existing data only for strengthening the pulse thesis contribution. Literature review and diagnostic recommendations completed; no new experimental collection or modelling decision adopted (pulse-thesis-research report).
- 2026-10-23: primacy analysis stopped under amendment 6 item 8 (V. Thakur); extensions not run; model-free timing check
  deferred (optional, descriptive only); all-trial 50-rep common-model fits for reported parameters submitted.
- 2026-10-23: primacy plan amendment 6 adopted with V. Thakur's corrections: cross-validated per-mouse pulse gain,
  labelled a model revision prompted by the failed gate; null calibration + power before the timing test; no
  further model expansion. Original gate failure reported prominently.
- 2026-10-23: guess_bias free (V. Thakur; fixed costs 65.5 held-out NLL). Control trials favour the integrator over
  extrema detection (+346 NLL); no E refit (analysis log 5.8).
- 2026-10-22 (client date): user approved integration-versus-extrema discrimination as primary paper question, primacy secondary; draft established sections while Hyak jobs queue. Preserve existing confirmatory rules/order (first-draft report).
- 2026-10-23: primacy plan amendment 5 adopted by V. Thakur (strategy test: pulse-specific statistic, paired sampling SD; E's
  drift_gain refit rule; implementation-note corrections); null calibration done.
- 2026-10-23: primacy plan amendment 4 adopted (integration vs extrema detection; leak 20–200 /s; 3 SD and 6/10 mice);
  gate 1 waits for its fits and frozen predictions (plans/2026-10-23-amendment-4-extrema.md).
- 2026-10-22: primacy power issue: run the predictive check (gate 1) first; gates 2–3 rule ≥ 80% inside
  (analysis log 5.7).
- 2026-10-22: common DDM model = L0U0V1Z0G1 + fast_only guesses (strict rule 2); secondary baseline L1U1V1Z0G1;
  primacy plan amendment 3 (reports/2026-10-22-leak-urgency-diagnosis.md; analysis log 5.6).
- 2026-10-22: delayed-engagement parameter not pursued (V. Thakur).
- 2026-10-21: no second warm-start round (gaps ≤ 5.9 NLL, below noise); sz out; fast_only guess form preferred
  (reports/2026-10-21-ddm-common-model-selection.md).
- 2026-10-20: primacy analysis plan locked (primacy-analysis-plan.md, commit aeb0a22); parsimony rules agreed
  (next-steps plan).
- 2026-10-20: SC WFV inactivation excluded from the paper; separate study (V. Thakur).
