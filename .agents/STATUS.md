# Status
Last updated: 2026-11-18 by Codex (client date)

## Current focus
Figure3 work checkpointed in local topic commits7f80063 (A alternatives),316c8af (fits/recovery panels),fd2ee9c (likelihood/RT audit and supplement),0f9ffc5 (slope/optimization pilot); no push. Both A alternatives retained, B/C approved, former D result text-only. Combined A–C assembly remains pending A choice; no parameters replaced by pilot. Current task: author requests next figure. Begin Figure4 pulse-influence review at A: dissemination/paper_accumulation/draft_2026-11-15/figure4_pulse_review_2026-11-18/figure4.png (unchanged earlier pulse figure relabeled). All5 source tables verified equal, caption matched, render inspected. Next review A then B–D; pulse artwork review resumed, no new pulse fits/simulations. See reports/2026-11-18-figure3-commits.md and reports/2026-11-18-figure4-review.md. Supplement RT diagnostic refinement remains pending.

Selected Figure 1: dissemination/paper_accumulation/draft_2026-11-15/figure1_revision_2026-11-17_v6/figure1.pdf (A–D). C uses control points and author logit_4 fits; D uses left/right-choice mean control RTs, solid traces and shaded pointwise SEM. Exclusions remain in Methods. Figure previews should be images embedded in chat; the initial HTML viewer and packaged Word draft remain older versions, explicitly labeled in README.

Earlier 2026-11-15 checkpoint: accumulated nonignored work saved as12 focused topic commits plus a final handoff commit on mouse-motion-energy; no push. Commit map and checks: reports/2026-11-15-commit-work.md and adjacent JSON records. The writing objective and next step are unchanged.

Figures-first paper packet complete: reports/2026-11-16-figures-first-draft.md. Author requested figures → captions → Methods → Results and comparable decision-making language/structure. Selected files: dissemination/paper_accumulation/draft_2026-11-15/figures_v5/main_figures.pdf and working_draft_v3.docx (same revision in Markdown); separate captions, methods and results files are current. Main figures include completed recovery, sustained pulse influence, individual/cohort uncertainty and matched RT tradeoffs. No new fits or simulations.

Active writing plan: plans/2026-10-26-paper-accumulation-variant.md, next unchecked current step G: Introduction, Discussion, Summary and final title. Working prose follows task → matched accumulation evidence → pulse persistence/dynamics. Original manuscripts and historical results remain intact. Missing author-specific animal/ethics/apparatus/declaration facts stay explicit; human source verification is not fabricated. Exact Neuron formatting remains provisional because the official author page was inaccessible.

The author explicitly retains the Huk-style post-pulse analysis centrally. Foreground sustained directional influence and retain the late decline; compare full trajectories without treating that decline alone as an intrinsic forgetting constant. Completed paired recovery supersedes older incomplete-recovery notes. Several cohort-average pulse predictions are compatible; stronger individual/time-course constraints and PSUIM7 concentration remain visible. The author has waived earlier manually imposed scientific gates.

## Previous focus
Historical notes retained for provenance; use the new direction report and completed-results inventory when these older assessments conflict.

NHP SSM installed and two-mouse pulse-state pilot complete: reports/2026-11-15-nhp-pulse-hmm-pilot.md. Environment /mnt/data/venvs/nhp-glmhmm-2026-11-15 contains the exact author fork; original DDM environment unchanged. Latest user selection: six physical direction × time indicators, congruency views on nonzero coherence. Shared-pulse state model improves future choices in PSUIM6/7; freeing pulse coefficients worsens PSUIM6 and gives unresolved PSUIM7 change. Current-RT validation does not support a consistent state interpretation. No late pulses in these two mice. Final results/figure: dissemination/nhp_pulse_hmm_2026-11-15/RESULTS.md and pulse_hmm_pilot_final.pdf. Next scientific option is a compact joint choice/RT baseline-state account with shared pulse weights, not a larger pulse-weight HMM campaign.

History/state follow-up and bounded positive-gain feasibility completed; report: reports/2026-11-14-history-state-gain.md. Verified original logged row order for all 50 accepted sessions, preserved excluded-row gaps. Continuous bias predicts held-out session portions beyond first-order history; extended history explains much of its benefit in the main pulse mice. Current-RT validation does not identify a common state mechanism. Gain partly improves the RT/late-pulse tradeoff but still underpredicts early pulse amplitude; two-mouse full-training pilot only, not held-out gain validation.

Author clarified task-assigned correct side before latest physical-input selection. Alternate six onset × target-congruency inputs remain coded/exported/tested in dissemination/nhp_ssm_2026-11-15/target_inputs_v2/. Exact SSM source is vaibrainium/ssm at a109af369797d852904fd9496f3532524de8f15a; installation and actual fork-based fits are now complete as above. UCLA target is reconstructed from Response/Correct; provenance limitation remains in reports/2026-11-15-nhp-ssm-target-congruency.md.

Literature assessment: dissemination/attention_decision_review_2026-11-14/ (32 verified/curated reference records). Response-delay pilot remains complete and unhelpful; see reports/2026-11-14-response-delay-pilot.md. Historical protocols below predate the author's current exploratory authorization.

Mapping x accumulator + nominal-coherence fits complete (1,260; exploratory, no rules): power/norm mappings fit slightly better
than linear, integrators beat E/ES under every mapping, no family reproduces the pulse effect per mouse; all integrators
predict a late reversal (reports/2026-11-09-mapping-accumulator-exploratory.md). Next: rules discussion with the author.
Fits now checkpoint every DE generation and resume after preemption (plans/2026-11-08-fit-checkpointing.md; ckpt-all requeues at ~8 h).
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

Older draft dissemination/paper/manuscript_2026-10-22.md includes first-pass gate failures and predates adoption of amendment 6. Newer draft: manuscript_2026-10-23.md. Timing tests remain withheld after both revised gates failed.
Primary paper question: integration versus extrema detection; primacy secondary, conditional on adequacy/sensitivity.

## Active plans
- plans/2026-10-29-control-paper.md : third paper (control trials only, Stine 2020 framing) in dissemination/paper_control/; G1 approved 2026-10-30 (D004), spine locked, stage S2; paired recovery 42579825 analysed: E separated (provisional, ES fits not yet submitted)
- plans/2026-10-28-full-recovery-matrix.md : ON HOLD (author); recovery rerun on fixed CPU datasets if it becomes necessary
- plans/2026-10-26-v2-refits-and-strategy-recovery.md : responded-only refits + full point-3 re-run (amendment 9); commands ready; next: user syncs code, submits R1-R6 (460), then F1a (80) and P1-P4 (850)
- plans/2026-10-26-paper-accumulation-variant.md : resumed under current author authorization; figures/captions/Methods/Results packet complete in draft_2026-11-15/; next current step G is Introduction/Discussion/Summary/title. Historical gated stages superseded.
- plans/2026-10-23-pulse-followup-parallel.md : A-E, G1, F3 pilot done (FAIL -> modelling stopped); next: H2 check of pilot, H4 finalize; original primacy procedure remains closed
- plans/2026-10-23-amendment-4-extrema.md : code done and checked; next: Hyak fits (commands in analysis log 8.4d)
- plans/2026-10-22-primacy-analysis-code.md : done; next: predictive check (gate 1) first pass when 8.4c batch 1 lands
- plans/2026-10-20-paper-writeup.md : Methods/Results/legends passed; next: mandatory author midpoint verification, then Discussion drafting
- ../dissemination/reports/mouse-ddm-next-steps.md : analysis plan (kept in dissemination/reports); steps 0–3 done
  (3.3 confirmed the strict model); next: guess-bias fits, fit quality, gate 1 first pass, recovery (jobs running)

## Recent reports (newest first, keep about 10)
- reports/2026-11-18-figure4-review.md : next pulse-influence figure A–D re-exported unchanged; begin panel A review.
- reports/2026-11-18-figure3-commits.md : four focused Figure3 checkpoints plus final handoff; no push.
- reports/2026-11-18-figure3C-accepted.md : C approved, standalone source-verified artwork saved; A–C panel review complete, A alternative choice deferred.
- reports/2026-11-18-cohort-recovery-text-only.md : D result moved to Results text; current Figure3 A–C, historical artwork excluded.
- reports/2026-11-18-figure3D-intuitive.md : direct-label group-recovery D redesign; same exact rates/counts, conditional interpretation retained.
- reports/2026-11-18-figure3B-accepted.md : B approved; accepted smooth C-only psychometric/chronometric artwork preserved; next recovery C.
- reports/2026-11-18-control-C-optimization-pilot.md :270 profiles/9 local restarts; independent100-rep checks show no reliable joint improvement, conditional CV not expanded; current fits retained.
- reports/2026-11-18-control-psychometric-slope.md : raw C predictions understate intermediate-coherence sensitivity; assess optimization/gain-variability-guess tradeoff before nonlinear mapping; no new fits.
- reports/2026-11-18-control-rt-supplement.md : RT diagnostic retained as supplementary draft with further revision pending; number unassigned.
- reports/2026-11-18-control-rt-score-diagnostic.md : all150 held-out C/E/ES scores reproduced; C gains middle RT bins, alternatives slowest bins; absolute quantile diagnostic complete.
- reports/2026-11-18-figure3B-mean-versus-score.md : E/ES closer to group mean RT by descriptive RMSE; C retains better archived held-out quantile score; distinct estimands/fit sources.
- reports/2026-11-18-figure3B-model-c.md : C-only psychometric/chronometric panel B from full-control fits; held-out scores remain prediction assessment; pulse deferred.
- reports/2026-11-17-ddm-likelihood-audit.md : Figure 3 DDM objective and sampled scores reproduced. Fold-specific RT quantiles and sparse choice cells qualify held-out score interpretation.
- reports/2026-11-18-figure3B-control-fits.md : B replaced by control psychometric/choice-conditioned RT data/model overlays; full-control predictions verified; one-trial Fig1 difference documented.
- reports/2026-11-18-figure3-remaining-panels.md : reviewed B decomposition and C/D recovery; start B, D supplementary placement proposed.
- reports/2026-11-17-figure3A-final-alternatives.md : both dual-axis alternatives author-finalized and added to paper packet; final A selection deferred.
- reports/2026-11-17-figure3A-metric-alternatives.md : two panel-A alternatives, dual-axis NLL/BIC and separate bits/BIC subpanels; verified rendering only.
- reports/2026-11-17-figure3-absolute-bic.md : absolute BIC preview; same source scores, mean differences checked against prior ΔBIC.
- reports/2026-11-17-figure3-bits-bic.md : verified joint test bits, choice-only bias-normalized bits and independently rescored QMLE ΔBIC; B/C previews ready.
- reports/2026-11-17-figure3-review.md : model figure committed; control-results redesign begins with prediction-source audit.
- reports/2026-11-17-figure2-review.md : Figure 1 checkpointed; initial Figure 2 panel walkthrough and model-introduction recommendation.
- reports/2026-11-17-basso-rt-display.md : verified Basso RT plotting precedents; mean-vs-median distinction and D recommendation.
- reports/2026-11-17-figure1-review.md : Figure 1 initial walkthrough; author discussion pending.
- reports/2026-11-15-commit-work.md : accumulated analysis/code/results/drafts split into topic commits; intended-environment tests pass; no push.
- reports/2026-11-16-figures-first-draft.md : four figures, captions, Methods and Results assembled with source records and an editable packet; comparable-paper structure applied; next is remaining manuscript sections.
- reports/2026-11-15-huk-pulse-interpretation.md : author retains main-paper pulse analysis; original Huk/Shadlen explicitly separates persistence evidence from estimating leak; no results changed.
- reports/2026-11-15-paper-direction.md : recommends original accumulation-first paper with pulse constraints central; completed recovery retained, attention/state headline unsupported; Neuron mechanism advance remains unresolved.
- reports/2026-11-15-nhp-pulse-hmm-pilot.md : installed exact fork; 132 converged fits; baseline/history states predict future choices, state-specific pulse weights do not help consistently; original environment preserved.
- reports/2026-11-15-nhp-ssm-target-congruency.md : exact author's SSM fork/revision pinned from NHP lock; target-relative six-category export audited including zero coherence; isolated setup prepared, no installation/fits.
- reports/2026-11-14-history-state-gain.md : chronology verified against original logs; persistent choice bias predicts future session portions; gain partly improves RT/late pulse but early effect remains too small; NHP six-type adapter ready, congruency definition pending.
- reports/2026-11-14-attention-decision-literature.md : literature revises next priority to history/state diagnostics, then gain feasibility; attention/encoding alternatives and scoring limitations mapped to existing data.
- reports/2026-11-14-response-delay-pilot.md : variable postdecision delay fails to resolve RT/pulse mismatch in PSUIM6/7; new implementation/tests, original folds, 90 audited held-out scores; gain variability proposed next.
- reports/2026-11-13-pulse-weight-signatures.md : free pulse weights (shared / per time) raise PSUIM6/7 early effect only to 6.5-7.5 pp (data 15.5 / 13.5); best early chi2 74.6, worse than normalized UGM no sv; BIC +274 to +907

## Known issues
- Control-C optimization pilot: original */control/independent_evaluation.json files are INVALID due to baseline-label collision. Use validation_v2/ and confirmation_100reps/ only; maps/optimizer traces unaffected. See pilot README/report.
- Figure 3 held-out quantile score estimates RT cuts on each test fold and gives sparse condition-by-choice cells a choice-only contribution (1,990 of 14,014 controls). Report it as an outcome-binned score. See reports/2026-11-17-ddm-likelihood-audit.md.
- 2026-11-16 draft: animal/ethics/task author facts and final declarations are missing; named-human source verification pending. Neuron author-page access failed, so exact formatting is unverified. Office pagination not rendered locally; native-size figures and DOCX structure/math were checked.
- Pulse-HMM setup complete in its isolated environment; use that interpreter for ssm. Pilot is choice-only and has no late pulse observations in PSUIM6/7. Alternate UCLA target-congruency inputs use reconstructed targets, not independent target logs. See 2026-11-15 SSM/pilot reports.
- Serial results condition on selected sessions/responded choices. Original logged row order verified; masking excluded records does not model informative missingness. Latent timescales are saved-record steps, not elapsed time or known distinct presentations.
- Response-delay pilot is bounded and exploratory, with no recovery/parameter intervals or group inference. PSUIM6 small NLL rankings remain seed-sensitive; PSUIM7 large RT advantage of drift variability persists. Pulse predictions use out-of-fold parameters and differ from earlier full-fit signatures (response-delay report).
- Fitted NLL (train_nll) is evaluated at the fit's own noise draw (optimistic, model-dependent): use rescored_nll_2026-11-12.csv / model_ic_*_2026-11-12_rescored.csv, not model_ic_*_2026-11-11.csv (reports/2026-11-12-rescored-ic.md).
- 2026-11-12 (resolved same day): /mnt/data was empty because the container started while the NAS was unmounted and a plain bind mount does not pick up later host mounts. docker-compose.yaml now binds host /mnt to /mnt/host (rslave) and links /mnt/data -> /mnt/host/cnc_backup/vaib_data/mouse-pulse-experiment at startup; NAS remounts now appear without a restart. If the NAS drops, /mnt/data reads as an empty local dir and writes go to local disk: check `findmnt -R /mnt/host` before long jobs. Claude history persisted to host ~/.claude-docker (CLAUDE_CONFIG_DIR=/root/.claude).
- Choices vs RTs (choice_binomial_nll_2026-11-12.csv, scripts/ddm/choice_fit_binomial.py): on pulse trials, no-sv fits predict choices better than their sv counterparts (pulse-only: NLL -26 to -60, 8-9/10 mice; all-trial pairs too); sv wins the combined likelihood through RTs.
- Choices after 5 s (13.7% of trials) are stimulus-driven (accuracy equal to on-time); "no response" is a misnomer. RT floor 0.3 s. Choice-history effects not in any model (reports/2026-10-29-behavior-exploration.md).
- 2026-10-29: all-trial (control + pulse) responded-only fits differ from control-only fits in the 4 UCLA mice (median ratio a 0.82, drift_gain 0.85, sv 0.76, ndt 1.9) but not in UW (about 1.0). The parameter table parameters_common_model_resp_2026-10-27.md uses the all-trial fits. UPDATE 2026-10-29: not reproduced by the joint no-freeze refits (primary ratios ~1.0; equal-NLL fits with different parameters = ridge; reports/2026-10-29-joint-control-pulse-refits.md). Cause not identified: UCLA pulse ME understated only 1.13-1.20x (reports/2026-10-29-ucla-pulse-me-nofreeze.md; refit deferred) or pulse misfit pressure; rig and mouse are confounded. Until resolved, compare mice on control-split fits or show both.
- 2026-10-29: paired-recovery fix implemented (4dbef52); rerun 42579825 done and valid (reports/2026-10-30-paired-recovery-cohorts.md); ES cells (180) not yet submitted.
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
- 2026-11-15 (client date): Author explicitly requested local commits of all accumulated work in digestible chunks. Checkpointed without pushing; reports/2026-11-15-commit-work.md.
- 2026-11-16: Follow author-selected figures → captions → Methods → Results order; apply comparable decision-making paper structure in original prose. First packet complete; Introduction/Discussion/Summary next. reports/2026-11-16-figures-first-draft.md.
- 2026-11-15: Author preference: retain Huk-style persistence/decline analysis centrally. Primary-source check supports sustained integration interpretation and cautions against a direct intrinsic forgetting estimate; reports/2026-11-15-huk-pulse-interpretation.md.
- 2026-11-15: Publication-direction recommendation (author adoption pending): retain accumulation-first argument and make pulse predictions the central mechanistic constraint; see reports/2026-11-15-paper-direction.md. No new manual gates or fitting campaign.
- 2026-11-15: latest asynchronous selection sets physical direction × time inputs as primary, nonzero-coherence congruency views. Installed pinned SSM with user authorization; completed bounded two-mouse pilot. Retain shared pulse weights as the simpler benchmark; no consistent predictive benefit for state-specific pulse coefficients (NHP pulse-HMM pilot report).
- 2026-11-15: author defines congruency relative to task-assigned correct side. Implemented six onset × congruency categories with target sign for right/left modeling; keep zero-coherence pulses and original masks. Use SSM fork pinned by the NHP lock, in a separate environment when installation is authorized (NHP SSM/target-congruency report).
- 2026-11-14: positive gain feasibility tested with common-parameter refits in PSUIM6/7; improves part of RT/late-pulse tradeoff, still misses early pulse amplitude. Do not label attention or treat training scores as held-out validation. NHP source reuse audited; physical six-type inputs prepared pending congruency clarification (history/state/gain report).
- 2026-11-14: literature recommendation is history/state diagnostics before another fit campaign; distinguish positive sensitivity gain from attention and evaluate temporal ordering outside the current pooled score. Proposed analyses, not established results (attention-decision literature report).
- 2026-11-14: completed the currently authorized exploratory postdecision-delay pilot; do not expand this unhelpful candidate to the full cohort. Positive-gain variability is proposed, not tested. See reports/2026-11-14-response-delay-pilot.md.
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

## Figure 3D approved — 2026-11-18
Author selected the exponential conditional-accuracy overlay: dissemination/paper_accumulation/draft_2026-11-15/figure3_exponential_2026-11-18/figure3D_exponential.pdf. Figure3 now A–D; both A alternatives retained. Fits, data SEM, whole-mouse bootstrap diagnostics, selection audit and caption are saved. Weak-coherence tau remains poorly identified; no mechanistic tau claim. Report: reports/2026-11-18-control-accuracy-exponential.md. Combined assembly awaits final A choice.
