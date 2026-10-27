# Plan: descriptive checks of a pulse readout-bias (slow-trial) account
Status: done (report: reports/2026-10-27-pulse-readout-bias-checks.md)
Created: 2026-10-27 by Claude Opus 5.5
Related reports: reports/2026-10-27-pulse-asymmetry-lapse-checks.md, reports/2026-10-23-pulse-diagnostics-20261023T191030Z_fa8de8b.md

## Goal
Model-free checks proposed by the author (paste, 2026-10-27): does the pulse effect live in slow trials, are slow
±100% control trials near chance, and are RTs unchanged given choice? Exploratory, post hoc, outside the closed protocol.

## Design (fixed before computing)
Responded trials, symmetric cells. RT bins: per mouse x |coherence|, quintile edges from that mouse's control RTs.
Sets: ±100% (incongruent pulses only exist) and |c| <= 36% (0% included; both pulse signs).
1. Pulse effect by RT bin: per (mouse, c, pulse sign s, bin) P(choice = s | pulse) - P(choice = s | control), averaged
   over (c, s) cells weighted by pulse-trial count, then mean ± SEM over mice. Expectation (slow-trial account): rises with bin.
2. Control accuracy by RT bin at ±100%, mean ± SEM over mice. Expectation: slowest bin approaches 0.5.
3. RT given choice: per (mouse, c, s), RT quantiles (0.1, 0.3, 0.5, 0.7, 0.9) of choices = s on pulse trials minus the same
   on control trials at c; same for choices = -s. Average over cells (pulse-count weighted), mean ± SEM over mice.
   Readout bias: ~0 shift; evidence account: pulse-direction choices faster.
4. No-response rates: NOT run (author rule 2026-10-27 excludes no-response trials from every analysis); asked.

## Steps
- [x] 1. scripts/ddm/pulse_readout_checks.py
- [x] 2. Run; figure + csv in dissemination/figures/qc/
- [x] 3. Report + STATUS

## Log
- 2026-10-27: done; checks 1-3 run, 4 not run (no-response rule). Results contradict the slow-trial expectation.
- 2026-10-27: author: no response-rate exception (lapse capture ruled out; existing number is positive vs negative, not pulse vs control). Check 4 stays not run.
