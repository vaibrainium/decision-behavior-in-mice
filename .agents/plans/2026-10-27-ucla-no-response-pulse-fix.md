# Plan: fix UCLA no-response pulse direction in preprocessing (v3 model inputs)
Status: abandoned (2026-10-27): moot for analyses once all trials without a response by 5 s are excluded; all 48 affected trials are no-response trials. The notebook 0.0 target bug remains for no-response rows only (harmless under the rule); fix only if those rows are ever used.
Created: 2026-10-27 by Claude (Opus 5.5)
Related: reports/2026-10-23-pulse-data-20261023T191030Z_fa8de8b.md (bug found); plans/2026-10-26-v2-refits-and-strategy-recovery.md
(refits switch from v2 to v3 inputs); dissemination/paper_accumulation/np/decisions.md D002

## Goal
Model inputs built from corrected preprocessing, not a patched copy: the 38 genuine UCLA no-response pulses labelled
and replayed as pulses, the 5 direction-unknown 0% trials excluded with a logged rule, the 5 null pulses replayed like
other null pulses. Nothing existing overwritten; raw data untouched.

## Context
- Root cause: notebooks/0.0-data-compilation.ipynb cell 8 derives UCLA `target` from Correct/Response, so
  Response = NaN (532 no-response rows) gives target NaN and pulse_coherence NaN; build_ddm_inputs then labels the
  trial control (sign(NaN) -> 0), and the censored replay renders it without a pulse.
- Task rule (RDK-Task Burst_Experiment.py): pulse direction = sign(BurstCoh x coherence); reproduces the notebook on
  15,025/15,025 nonzero-coherence pulses (pulse-data report).
- Notebook 0.0 writes its outputs into the raw folder; the fixed run writes to processed/preprocessing/2026-10-27/.

## Assumptions
- For responded trials, target = sign(Coherence) at nonzero coherence equals the Correct/Response formula (checked in step 2).
- Row order of aggregate_data is unchanged by the fix, so censored agg_codes (built from row index) are unchanged.

## Steps
- [ ] 1. Notebook 0.0: target = sign(Coherence) when Coherence != 0, else from Correct/Response (NaN if no response);
      outputs to processed/preprocessing/2026-10-27/. Notebook 0.1: reads/writes that folder.
- [ ] 2. Run both notebooks' code cells (no nbconvert; runner skips magics). Verify: only the 48 rows change in
      aggregate_data (target/pulse_coherence), valid_data.csv identical to the existing one.
- [ ] 3. make_censored_trials --data-dir; verify only the expected rows differ from the existing censored_trials.csv.
- [ ] 4. Re-render motion energy (CPU, --gpu -1) for the censored trials whose pulse_coherence changed (43) into the
      version folder; other censored and all responded trials reuse existing replays.
- [ ] 5. build_ddm_inputs --data-dir/--censored-me/--out -> preprocessing/2026-10-27/ddm_inputs_global_v3.npz; drops
      direction-unknown pulse trials (expect 5) with a printed count.
- [ ] 6. Verify v3 vs v2: same trials, same labels; signal/noise of the 38 close; templates differ only slightly
      (re-estimated with the corrected pulse set). Record sha256.
- [ ] 7. Update refit plan commands to v3; report; STATUS known issue.

## Out of scope
Rerunning analyses of the first paper version; the 15 invalid-duration exclusions (separate known issue); UW data.

## Log
- 2026-10-27: plan written after author decision ("yes, fix in preprocessing").
- 2026-10-27: PAUSED before any edit. Author: "We don't want to use no response trials at all". Censored set = 4,537 trials in DDM inputs: 435 with no RT, 4,102 responded after 5 s. If no-response trials are excluded, the 48 mislabel disappears from the fits and this fix is unnecessary for them; awaiting the author's definition and the consequences decision (likelihood truncation; pulse contrast conditioning).
- 2026-10-27: abandoned; author rule excludes all no-response-by-5 s trials (responded-only refits instead).
