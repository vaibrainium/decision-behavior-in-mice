"""Counterfactual: fast guesses that read the decision variable (Molano-Mazon et al. 2024 action initiation).

Fitted models treat a fast guess as a coin flip (choice 1 with probability guess_bias) at RT = guess_t0 + Exp(guess_tau).
Here the same guess trials, with the same RTs, instead report the side of the decision variable at the guess time:
  readout_mid   : DV above the bound midpoint a/2 -> right (keeps the fitted start-point bias)
  readout_start : DV above its own starting point -> right (removes the start-point bias)
If the accumulator had already reached a bound by then, its committed choice is used. DV time = guess RT - ndt, or
guess RT - read_lag with --read-lag (a short efferent delay as in Molano et al.; the accumulator's own ndt is unchanged).
RT distributions are identical to the fitted model by construction, so only guess-trial choices change.
Every version shares all random draws (noise, sv, sz, guess draws) within a rep: the comparison is paired.
No parameters are fitted. src/ddm is unchanged; the kernel below copies _simulate_ddm_trials_numba (no extrema, no
gain decay) and adds the readout; an exact-equality check against the production kernel runs first.

  OMP_NUM_THREADS=8 OPENBLAS_NUM_THREADS=1 .venv/bin/python -m scripts.paper.guess_readout_counterfactual --output <new dir>
"""
import argparse
import hashlib
import json
import pickle
import subprocess
import zlib
from pathlib import Path

import numpy as np
import pandas as pd
from numba import njit, prange

from scripts.ddm import pulse_dynamics_bridge as B
from src.ddm.simulator import _simulate_ddm_trials_numba, front_end_active, front_end_numpy, normalized_urgency

ROOT = Path(__file__).resolve().parents[2]
FAMILIES = ['pulse_norm_ugm_no_sv', 'no_sv', 'primary']
VERSIONS = ['coin', 'readout_mid', 'readout_start']


@njit(parallel=True)
def kernel(stimulus, noise, sv_draws, z_offsets, drift_gain, drift_offset, a, z, ndt, dt, leak_rate, time_constant, read_step):
    n_trials, n_timepoints = stimulus.shape
    rt = np.full(n_trials, np.nan, dtype=np.float32)
    choice = np.full(n_trials, np.nan, dtype=np.float32)
    read_mid = np.full(n_trials, np.nan, dtype=np.float32)
    read_start = np.full(n_trials, np.nan, dtype=np.float32)
    for trial in prange(n_trials):
        z_trial = min(0.99, max(0.01, z + z_offsets[trial]))
        starting_point = z_trial * a
        evidence = starting_point
        trial_drift_offset = drift_offset + sv_draws[trial]
        decision_var = starting_point
        rs = read_step[trial]
        if rs == 0:
            read_mid[trial] = 1.0 if decision_var > a / 2 else 0.0
            read_start[trial] = 0.5
        for t in range(1, n_timepoints):
            if np.isnan(stimulus[trial, t]):
                break
            drift = (drift_gain * stimulus[trial, t - 1] + trial_drift_offset) * dt
            leak = leak_rate * (evidence - starting_point) * dt
            evidence += drift + noise[trial, t - 1] - leak
            if time_constant != 0.0:
                decision_var = starting_point + (evidence - starting_point) * (1.0 + t * dt * time_constant)
            else:
                decision_var = evidence
            if decision_var >= a:
                rt[trial] = t * dt + ndt
                choice[trial] = 1.0
                break
            if decision_var <= 0.0:
                rt[trial] = t * dt + ndt
                choice[trial] = 0.0
                break
            if t == rs:
                read_mid[trial] = 1.0 if decision_var > a / 2 else 0.0
                read_start[trial] = 1.0 if decision_var > starting_point else (0.0 if decision_var < starting_point else 0.5)
        # committed before the readout, or input ended first: use the committed choice / last DV
        if np.isnan(read_mid[trial]):
            if not np.isnan(choice[trial]):
                read_mid[trial] = choice[trial]
                read_start[trial] = choice[trial]
            else:
                read_mid[trial] = 1.0 if decision_var > a / 2 else 0.0
                read_start[trial] = 1.0 if decision_var > starting_point else 0.0
    return rt, choice, read_mid, read_start


def fit_path(family, mouse):
    from scripts.ddm.pulse_joint_signatures import model_path
    return model_path(family)(mouse) if family == 'pulse_norm_ugm_no_sv' else B.fit_for(family, mouse)


def simulate_mouse(x, meta, family, mouse, seed, reps, check=False, read_lag=None):
    from scripts.ddm.fit_mouse_ddm import select
    from scripts.ddm.primacy import make_model
    from scripts.ddm.pulse_joint_signatures import OPTIONS
    path = fit_path(family, mouse)
    fit = pickle.load(path.open('rb'))
    opt = OPTIONS.get(family, {})
    assert not fit.get('pulse_weight') and fit.get('guess_model') == 'fast_only'
    rig = meta.loc[meta.mouse == mouse, 'rig'].iloc[0]
    rows = meta.loc[meta.mouse == mouse, 'row'].to_numpy()
    model = make_model(fit['variant'], rig, fixed_guess_bias=False, responded=True, front_end=opt.get('front_end'),
                       ugm=opt.get('ugm', False))
    data, stim = select(x, rows)
    p = normalized_urgency(dict(fit['parameters']))
    assert float(p.get('gain_decay', 0.0)) == 0.0 and float(p.get('extrema_bound', 0.0)) == 0.0
    stim = np.asarray(stim, dtype=np.float32)
    if front_end_active(p):
        stim = front_end_numpy(stim, p)
    n, T = stim.shape
    rng = np.random.default_rng(zlib.crc32(f'{family}|{mouse}|{seed}'.encode()))
    out = {v: [] for v in VERSIONS}
    for rep in range(reps):
        noise = (rng.standard_normal((n, T - 1), dtype=np.float32) * np.sqrt(p['variance'] * p['dt'])).astype(np.float32)
        sv = (rng.standard_normal(n) * float(p.get('sv', 0.0))).astype(np.float32)
        sz = ((rng.uniform(size=n) - .5) * float(p.get('sz', 0.0))).astype(np.float32)
        u = rng.uniform(size=(n, 3))
        is_guess = u[:, 0] < p['p_guess']
        g_rt = p['guess_t0'] - p['guess_tau'] * np.log1p(-u[:, 2])
        lag = p['ndt'] if read_lag is None else read_lag  # Molano: readout at initiation, then a short efferent delay
        read_step = np.where(is_guess, np.maximum(0, np.round((g_rt - lag) / p['dt'])), -1).astype(np.int64)
        args = (stim, noise, sv, sz, p['drift_gain'], p['drift_offset'], p['a'], p['z'], p['ndt'], p['dt'],
                p['leak_rate'], p['time_constant'])
        rt, ch, rmid, rstart = kernel(*args, read_step)
        if check and rep == 0:  # exact equality with the production kernel for the DDM outcome
            rt0, ch0, _ = _simulate_ddm_trials_numba(*args, 0.0, 0.0, np.full(n, -1, dtype=np.int64))
            assert np.array_equal(np.nan_to_num(rt, nan=-9), np.nan_to_num(rt0, nan=-9))
            assert np.array_equal(np.nan_to_num(ch, nan=-9), np.nan_to_num(ch0, nan=-9))
        tie = rstart == 0.5
        rstart = np.where(tie, (u[:, 1] < p['guess_bias']).astype(np.float32), rstart)
        coin = (u[:, 1] < p['guess_bias']).astype(np.float32)
        for v, gchoice in [('coin', coin), ('readout_mid', rmid), ('readout_start', rstart)]:
            sim = pd.DataFrame({'rt': np.where(is_guess, g_rt, rt), 'choice': np.where(is_guess, gchoice, ch)})
            sim = model._map_outcomes(sim.assign(trial=np.arange(n)))
            o = pd.DataFrame({'row': rows[sim.trial.to_numpy()], 'rep': rep, 'rt': sim.rt.to_numpy(),
                              'choice': sim.choice.to_numpy(), 'guess': is_guess[sim.trial.to_numpy()]})
            out[v].append(o)
    return {v: pd.concat(o, ignore_index=True) for v, o in out.items()}, fit, path


def effects(meta, o):
    """Per mouse x stage: mean over |coh| <= 36 of P(right | right pulse) - P(right | left pulse), responses by 5 s
    from 0.3 s, all response times and 0.6-1.0 s; plus fast (< 0.6 s) control accuracy by |coherence|."""
    m = meta.loc[o.row.to_numpy()]
    d = pd.DataFrame({'mouse': m.mouse.to_numpy(), 'coh': m.coherence_pct.to_numpy(), 'pulse': m.pulse.to_numpy(),
                      'stage': m.onset_stratum.to_numpy(), 'rt': o.rt.to_numpy(), 'R': (o.choice.to_numpy() == 1).astype(int),
                      'ok': (o.choice.to_numpy() >= 0) & np.isfinite(o.rt.to_numpy()) & (o.rt.to_numpy() <= 5)})
    d = d[d.ok]
    rows = []
    for win, sel in [('all', d.rt >= 0), ('0.3-0.6s', d.rt < .6), ('0.6-1.0s', (d.rt >= .6) & (d.rt < 1.0)),
                     ('1.0-5s', d.rt >= 1.0)]:
        p = d[sel & (d.pulse != 0) & (d.coh.abs() <= 36)]
        e = p.groupby(['mouse', 'stage', 'coh', 'pulse']).R.mean().unstack('pulse')
        e = (e[1] - e[-1]).dropna().groupby(['mouse', 'stage']).mean() * 100
        rows.append(e.rename('pp').reset_index().assign(measure=f'pulse_effect_{win}'))
    c = d[(d.pulse == 0) & (d.coh != 0) & (d.rt < .6)]
    acc = ((np.sign(c.coh) > 0) == (c.R == 1)).groupby([c.mouse, c.coh.abs()]).mean() * 100
    rows.append(acc.rename('pp').reset_index().rename(columns={'coh': 'abs_coh'}).assign(measure='fast_control_accuracy'))
    return pd.concat(rows, ignore_index=True)


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--output', type=Path, required=True)
    ap.add_argument('--families', nargs='+', default=FAMILIES, choices=FAMILIES)
    ap.add_argument('--seeds', nargs='+', type=int, default=[0, 1])
    ap.add_argument('--reps', type=int, default=30)
    ap.add_argument('--read-lag', type=float)
    a = ap.parse_args()
    out = a.output
    (out / 'cache').mkdir(parents=True, exist_ok=False)
    x = B.inputs()
    meta = pd.read_pickle(B.OUT / 'cache/metadata.pkl')
    data_out = pd.DataFrame({'row': meta.row.to_numpy(), 'rep': -1, 'rt': meta.rt_s.to_numpy(),
                             'choice': np.where(meta.response_side == 'R', 1, 0)})
    eff = [effects(meta, data_out).assign(family='data', version='data', seed=-1)]
    readouts, fits_used = [], {}
    for family in a.families:
        for seed in a.seeds:
            parts = {v: [] for v in VERSIONS}
            for i, mouse in enumerate(sorted(meta.mouse.unique())):
                sims, fit, path = simulate_mouse(x, meta, family, mouse, seed, a.reps, check=(i == 0 and seed == a.seeds[0]), read_lag=a.read_lag)
                fits_used[f'{family}|{mouse}'] = {'path': str(path), 'p_guess': fit['parameters']['p_guess']}
                for v, o in sims.items():
                    parts[v].append(o)
                    eff.append(effects(meta, o).assign(family=family, version=v, seed=seed))
            for v in VERSIONS:
                o = pd.concat(parts[v], ignore_index=True)
                o.to_pickle(out / 'cache' / f'{family}_{v}_seed{seed}.pkl')
                t = B.frame(meta, o)
                c = B.aggregate(t, by_rep=True).groupby(B.GROUP, observed=True)[['k', 'n', 'rt_sum']].sum().reset_index()
                readouts.append(B.readout(c, full=False).assign(family=family, version=v, seed=seed))
            print(f'DONE {family} seed={seed}', flush=True)
    eff = pd.concat(eff, ignore_index=True)
    eff.to_csv(out / 'effects_by_mouse.csv', index=False)
    ro = pd.concat(readouts, ignore_index=True)
    ro.to_csv(out / 'gammaT_readouts.csv', index=False)
    # summaries: seeds averaged; equal-mouse means
    s = eff.groupby(['family', 'version', 'measure', 'mouse', 'stage', 'abs_coh'], dropna=False).pp.mean().reset_index()
    s.to_csv(out / 'effects_by_mouse_seedmean.csv', index=False)
    (out / 'manifest.json').write_text(json.dumps({
        'families': a.families, 'read_lag_s': a.read_lag, 'versions': VERSIONS, 'seeds': a.seeds, 'reps': a.reps, 'fits': fits_used,
        'commit': subprocess.run(['git', 'rev-parse', 'HEAD'], capture_output=True, text=True, cwd=ROOT).stdout.strip(),
        'source_sha256': {str(q.relative_to(ROOT)): hashlib.sha256(q.read_bytes()).hexdigest()
                          for q in [Path(__file__), ROOT / 'src/ddm/simulator.py', ROOT / 'src/ddm/ddm.py']},
        'scope': 'Fixed fitted parameters (fitted under coin-flip guesses); RTs identical across versions; descriptive.'},
        indent=2) + '\n')


if __name__ == '__main__':
    main()
