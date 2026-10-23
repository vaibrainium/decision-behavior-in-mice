# Report: first observed gate failure and proposed pulse-gain revision
Date: 2026-10-22   Agent: Codex   Commit: b027a4c (inspection snapshot; manuscript changes uncommitted)
Plan: plans/2026-10-20-paper-writeup.md, steps I–J

## Question
What do the first observed pulse results establish, and what remains proposed rather than completed?

## Summary
Read saved gate and strategy outputs and checked coverage counts and prediction commits. Both baselines fail
choice and RT adequacy; strategy test remains not distinguished under its original rule. Added these findings
to manuscript Results/Abstract/Discussion and withheld primacy claims. Amendment 6 is a draft, not adopted here.

## Findings
- VERIFIED (saved posterior summary): primary departure mean 0.295969, 95% posterior interval
  0.175016–0.404677, predicted pulse effect 0.030055. Secondary mean 0.317407, interval 0.208982–0.407751,
  predicted effect 0.026221. Both choice gate passes are false; both full gates false. Source:
  `/mnt/data/processed/ddm/primacy/results_{primary,secondary}_gate.pkl`, `gate_departure` and `gate_pass`.
- VERIFIED: each baseline has 34/50 RT quantile cells inside its simulation range, below 0.8. Censoring
  coverage is 9/10 primary, 5/10 secondary. Computed directly from `gate_distributions` boolean columns.
- VERIFIED: both gate outputs report max R-hat 1.00 and one divergence. Intervals are first-pass estimates;
  convergence cannot be declared solely from R-hat. Prediction commits match 17511ca; fitting used the
  preliminary 15-repetition control fits, not the final settings in step 5. No timing tests were computed here.
- VERIFIED: strategy pulse gain sum 5.414500, SD 1.825324, z 2.966323, same sign in 8/10 mice. Total sum
  -8.575880, SD 11.612961, z -0.738475. Both saved verdicts: not distinguished. Do not round 2.966 into a
  threshold-passing 3. Source: `results_strategy.pkl` at the same processed path.
- VERIFIED (log inspection, not independent reanalysis): analysis log section 5.10 gives 0%-coherence
  pooled pulse-direction choices 0.574 observed versus 0.508 predicted, n=1,388. This is descriptive and
  trial-weighted; the gate intercept is not a pure causal pulse-effect estimate. Between-mouse heterogeneity
  is documented, and site/cohort/training/rig confounding prevents a location attribution.
- VERIFIED (proposal inspection): amendment 6 in `primacy-analysis-plan.md` is DRAFT. It proposes per-mouse
  pulse gain fitted with cross-validation, revised gating and sensitivity before timing tests. Not implemented,
  adopted, or run in this pass.
- INTERPRETATION: the proposed claim that a timing-invariant gain cannot produce timing differences is too
  strong. Its effect can interact with the nonlinear bound and the number of decisions still underway at each
  pulse. Out-of-fold prediction reduces own-trial fitting dependence but does not restore a wholly pre-outcome
  analysis after model selection from observed misfit. Label revisions as informed by the failed gate and
  simulate their full procedure, including a no-decay condition, before interpreting timing.

## What didn't work
The first manuscript patch failed because its expected paragraph claim ID was stale; the patch was atomic and
made no changes. Read the current line and reapplied successfully. No scientific computation failed.
The external rig repository could not be re-read in the upstream diagnostic; the reported replay energy bias
is therefore a suspected magnitude based on the replay and prior rig knowledge, not newly verified here.

## How to reproduce
Existing venv, read-only summaries; no new fit or MCMC sampling:

```bash
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -B - <<'PY'
from pathlib import Path
import hashlib, pickle
b = Path('/mnt/data/processed/ddm/primacy')
for name in ['results_primary_gate.pkl', 'results_secondary_gate.pkl', 'results_strategy.pkl']:
    p = b/name
    with p.open('rb') as f:
        r = pickle.load(f)
    print(name, hashlib.sha256(p.read_bytes()).hexdigest())
    if 'gate_pass' in r:
        print(r['gate_departure'], r['gate_pass'], r['prediction_commits'])
        d = r['gate_distributions']
        cols = [c for c in d if c.startswith('rt_q')]
        print(d[cols].to_numpy().sum(), d[cols].size, d.censored_inside.sum(), len(d))
    else:
        print(r['pulse_gain'], r['total'])
PY
```

SHA-256 at inspection:
- primary gate: `51ab63ab317ef9b6e2c99d92cc725b24c00df7ecf3e82940cb7ec9f81ceb0aab`
- secondary gate: `0e56d99fd4cddeef506c2880b90240b343bd115129a45a0168f59de935231ee1`
- strategy: `028c7b2262156da61ef56cd1144e35987602ff6736c62e8ad42ea4b0fbfc194a`

Upstream commands documented in analysis log 5.10: `primacy --analyze --gate_only --baseline
{primary,secondary} --unblind`, then `primacy --strategy_test --unblind`; original commits 80bde85 and 79ae5e4.
These are provenance, not commands rerun in this pass.

## Caveats
First-pass results require final-fit and sampler diagnostic review. No group-level causal pulse-effect estimate
was computed. Pulse strategy sensitivity is low, and both models fail adequacy; neither a near-threshold score
nor the control comparison identifies a unique behavioural mechanism. Scientific result files remain unchanged.

## Open questions and next steps
- [ ] Settle the proposed amendment explicitly; this review does not approve or implement it.
- [ ] Prioritize final-fit evaluation and a bounded revision only if it is needed for the intended claims.
- [ ] If revising, retain initial failures and label the adaptation; assess full-pipeline sensitivity/null behaviour.
- [ ] Keep primacy claims withheld on failed baselines; do not extend tonight's modelling without a stopping rule.
- [ ] Complete manuscript author facts and figures independently of the unresolved timing analysis.
