# Report: existing-data route to a concrete pulse thesis contribution
Date: 2026-10-23   Agent: Codex   Commit: fa8de8b2d33421c7dd18fc990b19984c4df4bac0
Plan: plans/2026-10-20-paper-writeup.md, K–L

## Question
How can pulse experiments support a stronger, defensible thesis contribution using existing data only?

## Summary
Completed a targeted primary-literature review and read-only pipeline/data audit. Recommend adjusted directional
pulse effects and pulse-aligned joint choice–RT distributions, then stimulus validation and a small exploratory
model comparison conditional on recoverability. Existing primacy stopping rules remain intact. The user explicitly
ruled out new behavioural data. Detailed synthesis: `dissemination/reports/pulse-thesis-research-2026-10-23.md`;
public search/source record: `dissemination/reports/pulse-thesis-searches-2026-10-23.json`.

## Findings
- VERIFIED: both revised gates fail; primary departure 0.241769 (95% posterior interval 0.090580–0.365729),
  predicted effect 0.056748; secondary 0.308882 (0.197824–0.405981), predicted 0.028899. Sources: saved gates below.
- VERIFIED: 20 simulated datasets per level; gate passes 19/14/7/1 at decay levels 0/0.1/0.2/0.4; primary detections
  0/0/1/0. The single detection is outside a passing gate. This assesses the specified fixed-control-fit procedure,
  not all possible pulse analyses. Sources: calibration CSVs and `scripts/ddm/primacy_calibration.py`.
- VERIFIED: retained responded trials include 6,030 UCLA and 5,449 UW pulse trials, total 11,479, in 10 mice.
  UCLA has 456 mouse–seed–coherence cells with both pulse signs, 220 also with a control; UW has none. These are
  feasibility counts, not choice-effect estimates. Source: metadata join in the reproduction command below.
- VERIFIED IMPLEMENTATION: pulse offset redraws some noise-dot directions in both replay rigs; the original
  directions are not restored in the checked seed/coherence examples. `primacy.no_pulse_frames` removes an average
  pulse component while retaining the pulsed replay's residual, rather than performing a physical no-pulse replay.
  Sources: `scripts/ucla_rdk.py::updateBurst`, `scripts/uw_rdk.py::update_coherence`, `primacy.py::no_pulse_frames`.
- UNTESTED CONSEQUENCE: whether that counterfactual difference or the known UCLA freeze mismatch materially
  changes pulse ME, gain estimates, or evidence for persistence. Do not call this an established behavioural artefact.
- RECOMMENDATION, NOT ADOPTED MODEL: prioritize joint choice/RT diagnosis, then one targeted input/response
  extension with matched competing models. New fitting/calibration requires a concrete implementation plan and
  separate cluster authorization; no such jobs were submitted here.

## What did not work
PMC browser challenges required author PDFs and Europe PMC XML. Two XML requests failed with HTTP 500.
Crossref metadata checks succeeded for Huk, Cisek, Yates, Okazawa, Stine and Kumano; six others returned HTTP 429.
Those identities were checked through their primary article/PubMed/publisher records instead. Tsetsos's reference
list has an incorrect DOI for Zhou et al.; the correct DOI is 10.1162/neco.2009.07-08-817 (PMID 19416080).
No fits, timing tests or scientific result files were changed. The existing figure-caption edit belongs to earlier work.

## How to reproduce
Run from `/src` in the existing environment. This reads outcomes only from already-saved gate results; the inventory
does not compute a new observed choice-by-timing contrast. Pulse-reset checks operate on synthetic dot states only.

```bash
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -B - <<'PY'
from pathlib import Path
import pickle, hashlib
import numpy as np
import pandas as pd
from scipy.stats import beta
from scripts.ucla_rdk import DotMotionStim
from scripts.uw_rdk import RandomDotMotion
p = Path('/mnt/data/processed')
z = np.load(p/'ddm/ddm_inputs_global.npz')
cols = ['agg_code','subject_id','idx_session','data_source','stimulus_seed',
        'signed_coherence','is_pulse_trial','pulse_coherence','pulse_onset',
        'pulse_duration','reaction_time']
d = pd.read_csv(p/'valid_data.csv', usecols=cols).merge(
    pd.DataFrame({'agg_code':z['agg_code'],'scheduled':z['sched_pulse_type']}),
    on='agg_code', validate='one_to_one')
for rig,g in d.groupby('data_source'):
    q = g[g.scheduled != 0]
    print(rig, 'mice/pulses/controls', q.subject_id.nunique(), len(q), (g.scheduled==0).sum())
    print('onsets', q.pulse_onset.min(), q.pulse_onset.max(), q.pulse_onset.nunique())
    print('pre-onset/500ms-lag', (q.reaction_time<q.pulse_onset).sum(),
          (q.reaction_time>=q.pulse_onset+.5).sum())
    s = g.assign(direction=np.sign(g.scheduled)).groupby(
        ['subject_id','stimulus_seed','signed_coherence']).direction.agg(lambda x:frozenset(x))
    print('matched both signs / plus control', sum({-1,1}.issubset(x) for x in s),
          sum({-1,0,1}.issubset(x) for x in s))
    print('pulse duration', q.pulse_duration.agg(['min','median','max']).to_dict())
for b in ['primary','secondary']:
    f = p/'ddm/primacy_revised'/f'results_{b}_gate.pkl'
    r = pickle.load(f.open('rb'))
    print(b, r['gate_departure'], r['gate_pass'])
for f in sorted((p/'ddm/primacy_calibration').glob('calibration_summary_levels*.csv')):
    a = pd.read_csv(f)
    print(f.name, a.groupby('level').agg(n=('dataset','size'),gate=('gate_pass','sum'),
                                      detection=('primary_primacy','sum')))
    print('detections passing gate', (a.primary_primacy & a.gate_pass).sum())
print('0/20 exact 95% upper', beta.ppf(.975,1,20))
for folder, pattern, key in [('fits_final','*.pkl','fit_seconds'),
                              ('primacy_calibration','*_lv0.00_ds00.pkl','seconds')]:
    vals = [pickle.load(f.open('rb'))[key] for f in (p/'ddm'/folder).glob(pattern)]
    print(folder, len(vals), np.quantile(vals,[0,.5,1]))
for rig in ['ucla','uw']:
    for c in [0,18,-18]:
        r = DotMotionStim() if rig=='ucla' else RandomDotMotion()
        if rig=='ucla': r.newStimulus(c,1)
        else: r.new_stimulus({'coherence':c,'seed':1})
        before = r.theta.copy()
        if rig=='ucla': r.updateBurst(100); r.updateBurst(c)
        else: r.move_dots(new_coherence=100); r.move_dots(new_coherence=c)
        print(rig,c,'original directions restored',np.array_equal(before,r.theta))
PY
```

Source hashes (SHA-256; paths relative to `/mnt/data/processed`):

```text
be508cc2e7918ae66bf7e82728d2617d07265b9f0f18442d6d531f345921e020  valid_data.csv
1a6c88ecf5da258e18435ceab600c799b3e413f0a0adc464d70b6115e1d69980  ddm/ddm_inputs_global.npz
69f28e273475b5aec78b38cfd121800a72136345564264288cfe6cb8a6927ea4  ddm/primacy_revised/results_primary_gate.pkl
a858531f7b233539f43f713576992b36769da375d424fc4af3f6d59789e9479d  ddm/primacy_revised/results_secondary_gate.pkl
4630ef19f12f9cfe4c6f8379657a9f6f761a1a1620a1b35da7aaa76c0c6fa33c  ddm/primacy_calibration/calibration_summary_levels0.csv
7cda6bdbd426fb10895756d11cb5c30b707d4630dcc7ddcb1a0ee30e22c37686  ddm/primacy_calibration/calibration_summary_levels0.1.csv
ca27dcb73c1fc2bd32b550f1bfda162c3b3add02cfa7009a277fdec505ba1fa5  ddm/primacy_calibration/calibration_summary_levels0.2.csv
00d378d60a235f9b253a03ee0b0f9e2047d6c95f18d4e7ec5ea7d3d239d53a34  ddm/primacy_calibration/calibration_summary_levels0.4.csv
```

## Caveats
Randomization and original display-loop timing were not verified against acquisition logs. Metadata support
feasibility, not guaranteed power. Zero nominal coherence contains hidden stimulus evidence. Restricting future RT
can select on a pulse consequence. Sensory persistence and decision retention may remain inseparable. The research
note's effort estimates are conditional planning judgments, supported only loosely by existing runtime metadata.
The literature synthesis is targeted and single-agent; the recent cross-species source is a reviewed preprint.

## Open questions and next steps
- [ ] Adopt a bounded exploratory follow-up, distinct from the closed primacy procedure, if desired.
- [ ] Validate physical pulse/no-pulse replay differences and post-offset direction-aligned ME before a retention claim.
- [ ] Verify assignment and sham scheduling; estimate mouse-level directional effects and pulse-aligned joint outcomes.
- [ ] Diagnose choice-versus-RT gain tension before selecting a new model; simulate discrimination before interpreting it.
- [ ] Keep original failures, retrospective status and any unresolved non-identifiability explicit in the thesis.
