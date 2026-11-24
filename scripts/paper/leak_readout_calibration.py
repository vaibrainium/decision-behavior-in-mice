"""Calibrate the Figure 4D descriptive exponential against accumulators with known leak (plan 2026-11-24-lit-followups).

Piet et al. 2018 (Fig. 3c-d) logic: simulate agents whose leak is known, apply the same readout, ask whether the
readout recovers the leak. Every parameter except leak_rate stays at each mouse's fitted value (joint fits, bases
'no_sv' and 'primary'). The gammaT readout is the exact historical estimator in scripts.ddm.pulse_dynamics_bridge;
the exponential is scripts.paper.preview_pulse_exponential.fit_exp on the same six bins with the same fixed observed
time coordinates. No decision-model parameters are fitted.

  OMP_NUM_THREADS=4 OPENBLAS_NUM_THREADS=1 .venv/bin/python -m scripts.paper.leak_readout_calibration --output <new dir>
"""
import argparse
import hashlib
import json
import pickle
import subprocess
import time
import zlib
from pathlib import Path

import numpy as np
import pandas as pd

from scripts.ddm import pulse_dynamics_bridge as B
from scripts.paper.preview_pulse_exponential import fit_exp

ROOT = Path(__file__).resolve().parents[2]
OBS = ROOT / 'dissemination/paper_accumulation/draft_2026-11-15/pulse_exponential_preview_2026-11-18/observations.csv'
LEAKS = [0.0, 0.5, 1.0, 2.0, 5.0, 10.0, 20.0]
BASES = ['no_sv', 'primary']


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def simulate(out, bases, leaks, seeds, reps):
    from scripts.ddm.fit_mouse_ddm import select
    from scripts.ddm.primacy import make_model, simulate_outcomes
    x = B.inputs()
    meta = pd.read_pickle(B.OUT / 'cache/metadata.pkl')
    for base in bases:
        for leak in leaks:
            for seed in seeds:
                for mouse in sorted(meta.mouse.unique()):
                    cache = out / 'cache' / f'{base}_leak{leak:g}_{mouse}_seed{seed}_r{reps}.pkl'
                    if cache.exists():
                        continue
                    path = B.fit_for(base, mouse)
                    fit = pickle.load(path.open('rb'))
                    assert fit.get('front_end') is None and not fit.get('ugm') and not fit.get('pulse_weight')
                    rig = meta.loc[meta.mouse == mouse, 'rig'].iloc[0]
                    rows = meta.loc[meta.mouse == mouse, 'row'].to_numpy()
                    model = make_model(fit['variant'], rig, fixed_guess_bias=False, responded=True)
                    data, stimulus = select(x, rows, pulse_weight=False, pulse_times=0)
                    params = dict(fit['parameters'])
                    assert params['leak_rate'] == 0.0, (path, params['leak_rate'])
                    params['leak_rate'] = float(leak)
                    t0 = time.monotonic()
                    raw = simulate_outcomes(model, params, stimulus, data['condition'], reps,
                                            zlib.crc32(f'{mouse}|{seed}'.encode()))
                    raw['row'] = rows[raw.trial.to_numpy()]
                    o = raw[['row', 'rep', 'rt', 'choice']].copy()
                    assert len(o) == len(rows) * reps
                    pd.to_pickle({'base': base, 'leak': leak, 'seed': seed, 'mouse': mouse, 'fit_path': str(path),
                                  'fit_sha256': sha(path), 'parameters': params, 'outcomes': o,
                                  'nonresponse': float((o.choice < 0).mean()), 'seconds': time.monotonic() - t0}, cache)
                    model.simulator.clear_cache()
                print(f'SIMULATED {base} leak={leak} seed={seed}', flush=True)


def analyze(out, bases, leaks, seeds, reps):
    meta = pd.read_pickle(B.OUT / 'cache/metadata.pkl')
    obs = pd.read_csv(OBS).sort_values('bin')
    coords = obs.set_index('bin').mean_delay_s
    pooled, per_rep, diag = [], [], []
    for base in bases:
        for leak in leaks:
            for seed in seeds:
                parts = []
                for mouse in sorted(meta.mouse.unique()):
                    r = pd.read_pickle(out / 'cache' / f'{base}_leak{leak:g}_{mouse}_seed{seed}_r{reps}.pkl')
                    t = B.frame(meta, r['outcomes'])
                    parts.append(t)
                    o = r['outcomes']
                    ok = o.choice >= 0
                    diag.append({'base': base, 'leak': leak, 'seed': seed, 'mouse': mouse, 'nonresponse': r['nonresponse'],
                                 'mean_rt': float(o.rt[ok].mean()), 'readout_trials_per_rep': len(t) / reps})
                t = pd.concat(parts, ignore_index=True)
                c = B.aggregate(t, by_rep=True)
                expected = c.groupby(B.GROUP, observed=True)[['k', 'n', 'rt_sum']].sum().reset_index()
                configs = [('pooled', -1, expected)] + [('rep', int(rep), g) for rep, g in c.groupby('rep')]
                for kind, rep, counts in configs:
                    row = {'base': base, 'leak': leak, 'seed': seed, 'rep': rep}
                    try:
                        res = B.readout(counts, full=False)
                        res = res[res.lo_s >= .3].set_index('bin').reindex(coords.index)
                        row.update({f'gammaT_{b}': v for b, v in res.gammaT.items()})
                        row['K'] = float(res.K.dropna().iloc[0]) if res.K.notna().any() else np.nan
                        row['late_mean'] = float(res.loc[res.lo_s >= 1.2, 'gammaT'].mean())
                        row['min_slope'] = float(res.b1_per_pct.min())
                        if res.gammaT.notna().all():
                            f = fit_exp(coords.to_numpy(), res.gammaT.to_numpy())
                            row.update({'tau_s': f['tau_s'], 'amplitude': f['amplitude'], 'boundary': f['boundary']})
                        row['failed'] = False
                    except Exception as e:  # recorded, not dropped silently
                        row.update({'failed': True, 'error': repr(e)})
                    (pooled if kind == 'pooled' else per_rep).append(row)
                print(f'ANALYZED {base} leak={leak} seed={seed}', flush=True)
    pooled, per_rep = pd.DataFrame(pooled), pd.DataFrame(per_rep)
    pooled.to_csv(out / 'pooled_readouts.csv', index=False)
    per_rep.to_csv(out / 'per_rep_readouts.csv', index=False)
    pd.DataFrame(diag).to_csv(out / 'simulation_diagnostics.csv', index=False)
    data_fit = fit_exp(coords.to_numpy(), obs.gammaT.to_numpy())
    lo, hi = 0.45057015675961337, 3.7254887142659414  # data bootstrap interval, preview manifest.json
    summary = []
    for (base, leak), g in per_rep.groupby(['base', 'leak']):
        ok = g[~g.failed & g.tau_s.notna()]
        pool = pooled[(pooled.base == base) & (pooled.leak == leak)]
        summary.append({'base': base, 'leak': leak, 'pooled_tau_s_seed_mean': pool.tau_s.mean(),
                        'pooled_K_seed_mean': pool.K.mean(), 'pooled_late_seed_mean': pool.late_mean.mean(),
                        'rep_n': len(g), 'rep_failed_or_unfit': int(len(g) - len(ok)),
                        'rep_boundary': int(ok.boundary.sum()) if len(ok) else 0,
                        'rep_tau_median': ok.tau_s.median(), 'rep_tau_q025': ok.tau_s.quantile(.025),
                        'rep_tau_q975': ok.tau_s.quantile(.975),
                        'rep_frac_tau_in_data_interval': float(((ok.tau_s >= lo) & (ok.tau_s <= hi)).mean()) if len(ok) else np.nan,
                        'rep_frac_tau_le_data_point': float((ok.tau_s <= data_fit['tau_s']).mean()) if len(ok) else np.nan})
    pd.DataFrame(summary).to_csv(out / 'summary.csv', index=False)
    manifest = {'data_tau_s': data_fit['tau_s'], 'data_tau_interval_s': [lo, hi], 'leaks_per_s': LEAKS, 'bases': bases,
                'seeds': seeds, 'reps': reps, 'time_coordinates_s': coords.to_dict(),
                'commit': subprocess.run(['git', 'rev-parse', 'HEAD'], capture_output=True, text=True, cwd=ROOT).stdout.strip(),
                'sources_sha256': {str(p.relative_to(ROOT)): sha(p) for p in [Path(__file__), ROOT / 'scripts/ddm/pulse_dynamics_bridge.py',
                                   ROOT / 'scripts/paper/preview_pulse_exponential.py', ROOT / 'src/ddm/simulator.py', OBS]},
                'scope': 'Fixed fitted parameters except leak_rate; per-rep spread is simulation sampling at data size, not mouse resampling or parameter uncertainty.'}
    (out / 'manifest.json').write_text(json.dumps(manifest, indent=2) + '\n')


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--output', type=Path, required=True)
    p.add_argument('--bases', nargs='+', default=BASES, choices=BASES)
    p.add_argument('--leaks', nargs='+', type=float, default=LEAKS)
    p.add_argument('--seeds', nargs='+', type=int, default=[0, 1])
    p.add_argument('--reps', type=int, default=30)
    p.add_argument('--analyze-only', action='store_true')
    a = p.parse_args()
    (a.output / 'cache').mkdir(parents=True, exist_ok=True)
    if not a.analyze_only:
        simulate(a.output, a.bases, a.leaks, a.seeds, a.reps)
    analyze(a.output, a.bases, a.leaks, a.seeds, a.reps)


if __name__ == '__main__':
    main()
