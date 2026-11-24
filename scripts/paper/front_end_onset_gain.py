"""Effective input gain of the fitted divisive front end at pulse onset, by pulse stage (plan 2026-11-24-lit-followups).

Norm front end (src/ddm/simulator.py front_end_numpy): x' = x / (1 + fe_beta * p), p a causal low-pass of |x| with
time constant fe_tau, starting at 0 at stimulus onset. This is a continuous analogue of Brunton et al. 2013 click
depression. Here we only read the gain g = 1 / (1 + fe_beta * p) out of the fitted pulse_norm_ugm_no_sv parameters on
each mouse's actual 1 ms motion-energy inputs. Primary: g averaged over the pulse's own (filter-delayed) motion-energy
component, weighted by its magnitude; also g just before the logged onset and the mean g over the logged pulse frames. Compared,
descriptively, with the observed and model-predicted right-minus-left pulse effects per stage
(pulse_onset_diagnosis_2026-11-19_final/mouse.csv). No fitting, no simulation of choices.

  .venv/bin/python -m scripts.paper.front_end_onset_gain --output <new dir>
"""
import argparse
import hashlib
import json
import pickle
import subprocess
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.signal import lfilter
from scipy.stats import spearmanr

from scripts.ddm import pulse_dynamics_bridge as B
from scripts.ddm.fit_mouse_ddm import DT, select
from scripts.ddm.pulse_joint_signatures import model_path

ROOT = Path(__file__).resolve().parents[2]
DIAG = ROOT / 'dissemination/paper_accumulation/draft_2026-11-15/pulse_onset_diagnosis_2026-11-19_final/mouse.csv'
FAMILY = 'pulse_norm_ugm_no_sv'


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--output', type=Path, required=True)
    out = ap.parse_args().output
    out.mkdir(parents=True, exist_ok=False)
    x = B.inputs()
    fr = int(x['frame_rate'])
    meta = pd.read_csv(B.TRIAL_TABLE, low_memory=False).set_index('trial_id').reindex(x['agg_code'].astype(str))
    mice = meta.mouse.to_numpy()
    stage = np.abs(x['sched_pulse_type']).astype(int)
    rows_out, params_out = [], []
    for mouse in sorted(pd.unique(mice)):
        path = model_path(FAMILY)(mouse)
        fit = pickle.load(path.open('rb'))
        assert fit.get('front_end') == 'norm'
        p = fit['parameters']
        beta, tau = float(p['fe_beta']), float(p['fe_tau'])
        assert float(p.get('fe_gamma', 1.0)) == 1.0 and float(p.get('fe_h', 0.0)) == 0.0
        params_out.append({'mouse': mouse, 'fe_beta': beta, 'fe_tau_s': tau, 'leak_rate': p.get('leak_rate'),
                           'fe_beta_at_bound_20': beta > 19.9})
        rows = np.flatnonzero((mice == mouse) & (stage > 0))
        _, stim = select(x, rows)
        _, (_, pulse) = select(x, rows, pulse_weight=True)  # pulse component of the motion energy (filter-delayed)
        w = np.nan_to_num(np.abs(pulse))
        k = min(1.0, DT / tau)
        pool = lfilter([k], [1.0, k - 1.0], np.nan_to_num(np.abs(stim)), axis=1)
        gain = 1.0 / (1.0 + beta * pool)
        for i, r in enumerate(rows):
            on = int(round(x['pulse_onset_frame0'][r] / fr / DT))
            off = int(round((x['pulse_onset_frame0'][r] + x['pulse_n_frames'][r]) / fr / DT))
            if on < 1 or off > stim.shape[1] or not np.isfinite(stim[i, on - 1]):
                continue
            rows_out.append({'mouse': mouse, 'stage': int(stage[r]), 'onset_s': on * DT,
                             'gain_pre': float(gain[i, on - 1]), 'gain_during': float(np.nanmean(gain[i, on:off])),
                             'gain_pulse_weighted': float((gain[i] * w[i]).sum() / w[i].sum()) if w[i].sum() > 0 else np.nan,
                             'pool_pre': float(pool[i, on - 1])})
    trials = pd.DataFrame(rows_out)
    trials.to_csv(out / 'trial_gain.csv', index=False)
    pd.DataFrame(params_out).to_csv(out / 'front_end_parameters.csv', index=False)
    by = trials.groupby(['mouse', 'stage']).agg(n=('gain_pre', 'size'), onset_s=('onset_s', 'median'),
                                                gain_pre=('gain_pre', 'mean'), gain_during=('gain_during', 'mean'),
                                                gain_pw=('gain_pulse_weighted', 'mean')).reset_index()
    by.to_csv(out / 'mouse_stage_gain.csv', index=False)
    # observed and predicted right-minus-left effects (pp), early/middle in all mice
    d = pd.read_csv(DIAG)
    d = d[(d.measure == 'right_choice_difference_pp') & (d.support == 'early_middle')]
    eff = d.pivot_table(index=['mouse'], columns=['source', 'stage'], values='pp', aggfunc='mean')
    g = by.pivot(index='mouse', columns='stage', values='gain_pw')  # primary: pulse-weighted gain
    g0 = by.pivot(index='mouse', columns='stage', values='gain_pre')
    gd = by.pivot(index='mouse', columns='stage', values='gain_during')
    comp = pd.DataFrame({'gain_pw_early': g[1], 'gain_pw_middle': g[2], 'gain_pw_late': g.get(3),
                         'gain_pre_early': g0[1], 'gain_pre_middle': g0[2],
                         'gain_during_early': gd[1], 'gain_during_middle': gd[2],
                         'obs_early_pp': eff[('data', 1)], 'obs_middle_pp': eff[('data', 2)],
                         'model_early_pp': eff[(FAMILY, 1)], 'model_middle_pp': eff[(FAMILY, 2)]})
    comp['gain_ratio_early_over_middle'] = comp.gain_pw_early / comp.gain_pw_middle
    comp['obs_ratio_early_over_middle'] = comp.obs_early_pp / comp.obs_middle_pp
    comp['obs_early_minus_middle_pp'] = comp.obs_early_pp - comp.obs_middle_pp
    comp['model_early_minus_middle_pp'] = comp.model_early_pp - comp.model_middle_pp
    comp = comp.join(pd.DataFrame(params_out).set_index('mouse'))
    comp.to_csv(out / 'mouse_comparison.csv')
    rho = {}
    for a, b in [('gain_ratio_early_over_middle', 'obs_early_minus_middle_pp'),
                 ('gain_ratio_early_over_middle', 'model_early_minus_middle_pp'),
                 ('fe_beta', 'obs_early_pp')]:
        s = spearmanr(comp[a], comp[b], nan_policy='omit')
        rho[f'{a}__vs__{b}'] = {'rho': float(s.statistic), 'p_uncorrected': float(s.pvalue), 'n': int(comp[[a, b]].dropna().shape[0])}
    manifest = {'family': FAMILY, 'spearman_descriptive': rho,
                'commit': subprocess.run(['git', 'rev-parse', 'HEAD'], capture_output=True, text=True, cwd=ROOT).stdout.strip(),
                'sources_sha256': {str(q.relative_to(ROOT)): sha(q) for q in [Path(__file__), ROOT / 'src/ddm/simulator.py', DIAG]},
                'scope': 'Descriptive; n = 10 mice; fixed fitted parameters; gain is a front-end property only (leak, urgency and bounds also shape stage effects).'}
    (out / 'manifest.json').write_text(json.dumps(manifest, indent=2) + '\n')
    print(comp.round(3).to_string())
    print(json.dumps(rho, indent=2))


if __name__ == '__main__':
    main()
