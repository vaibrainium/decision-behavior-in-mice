"""Compare the historical pulse correctness/dilution estimators with fixed fitted models.

No decision-model parameters are fitted here. The binomial regressions are the
same descriptive readouts used on the real data. Outputs are versioned separately
from the historical analysis. Run with OMP/OPENBLAS/MKL_NUM_THREADS=1.

  python -m scripts.ddm.pulse_dynamics_bridge --prepare
  CUDA_VISIBLE_DEVICES=0 python -m scripts.ddm.pulse_dynamics_bridge --simulate --families primary no_sv --seed 0
  python -m scripts.ddm.pulse_dynamics_bridge --analyze
"""
import argparse
import gc
import hashlib
import json
import pickle
import time
import warnings
import zlib
from pathlib import Path

import numpy as np
import pandas as pd
import statsmodels.api as sm
import statsmodels.formula.api as smf

from config import dir_config

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'dissemination/pulse_dynamics_2026-11-13'
DDM = Path(dir_config.data.processed) / 'ddm'
TRIAL_TABLE = Path(dir_config.data.processed) / 'pulse_followup/20261023T191030Z_fa8de8b/data/trial_table.csv'
INPUT = DDM / 'ddm_inputs_global_ucla_nofreeze.npz'
TIMING = DDM / 'pulse_timing_global.npz'
EDGES = np.array([.1, .3, .6, .9, 1.2, 1.5, 2.1, 5.])
GROUP = ['mouse', 'coherence_pct', 'pulse', 'bin']
FAMILIES = ['control_primary', 'primary', 'no_sv', 'power_leak_urgency', 'norm_leak',
            'pulse_linear_leak', 'pulse_norm_ugm_no_sv', 'primary_sv0']
WEIGHTED_FAMILIES = ['pulse_norm_ugm_choice_w2', 'pulse_norm_ugm_choice_w4',
                     'pulse_norm_ugm_choice_w8', 'pulse_norm_ugm_choice_only']
LABELS = {'data': 'Observed data', 'control_primary': 'Control-trained integrator',
          'primary': 'Joint integrator with drift variability', 'no_sv': 'Joint integrator without drift variability',
          'power_leak_urgency': 'Power input + leak + urgency', 'norm_leak': 'Normalized input + leak',
          'pulse_linear_leak': 'Pulse-only leak model', 'pulse_norm_ugm_no_sv': 'Pulse-only normalized urgency gating, no sv',
          'primary_sv0': 'Joint integrator, sv set to zero (ablation)',
          'pulse_norm_ugm_choice_w2': 'Normalized UGM, 2× relative choice weight',
          'pulse_norm_ugm_choice_w4': 'Normalized UGM, 4× relative choice weight',
          'pulse_norm_ugm_choice_w8': 'Normalized UGM, 8× relative choice weight',
          'pulse_norm_ugm_choice_only': 'Normalized UGM, choice-only fit'}


def sha(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as f:
        for b in iter(lambda: f.read(1048576), b''):
            h.update(b)
    return h.hexdigest()


def inputs():
    from scripts.ddm.fit_mouse_ddm import load_inputs, responded_only
    x = load_inputs(INPUT)
    with np.load(TIMING) as f:
        assert np.array_equal(f['agg_code'], x['agg_code'])
        x.update({k: f[k] for k in ['pulse_onset_frame0', 'pulse_n_frames', 'pulse_coherence']})
    return responded_only(x)


def metadata(x):
    """Historical Huk trial population before conditioning on response after offset."""
    t = pd.read_csv(TRIAL_TABLE, low_memory=False).set_index('trial_id').reindex(x['agg_code'].astype(str)).reset_index()
    assert t.mouse.notna().all() and t.trial_id.is_unique
    t['row'] = np.arange(len(t))
    t = t[t.in_ddm_input.astype(bool) & (t.response_side != 'none') & t.signs_scheduled_symmetric.astype(bool)
          & t.pulse_category.isin(['control', 'positive', 'negative']) & (t.onset_stratum != 'late')].copy()
    pulsed = t.pulse_category != 'control'
    duration = (t.recorded_offset_s - t.recorded_onset_s).where(pulsed)
    t['onset_s'] = np.where(pulsed, t.recorded_onset_s, t.control_onset_s)
    t['offset_s'] = t.onset_s + np.where(pulsed, duration, t.rig.map(duration.groupby(t.rig).median()))
    t['pulse'] = np.where(pulsed, t.pulse_sign, 0).astype(int)
    assert t.onset_s.notna().all() and t.offset_s.notna().all()
    return t.set_index('row', drop=False)


def frame(meta, outcomes=None):
    if outcomes is None:
        t = meta.copy()
        t['rt'] = t.rt_s
        t['choice'] = (t.response_side == 'R').astype(int)
        t['rep'] = -1
    else:
        m = meta.loc[outcomes.row.to_numpy()]
        t = pd.DataFrame({k: m[k].to_numpy() for k in ['row', 'mouse', 'rig', 'coherence_pct', 'pulse', 'onset_s', 'offset_s']})
        t[['rt', 'choice', 'rep']] = outcomes[['rt', 'choice', 'rep']].reset_index(drop=True)
    keep = (t.choice >= 0) & np.isfinite(t.rt) & (t.rt <= 5) & (t.rt >= t.offset_s)
    t = t[keep].copy()
    t['rel_rt_s'] = t.rt - t.onset_s
    t = t[(t.rel_rt_s >= EDGES[0]) & (t.rel_rt_s < EDGES[-1])].copy()
    t['bin'] = pd.cut(t.rel_rt_s, EDGES, labels=False, right=False).astype(int)
    t['right'] = (t.choice == 1).astype(int)
    return t


def aggregate(t, by_rep=False):
    keys = (['rep'] if by_rep else []) + GROUP
    return t.groupby(keys, observed=True).agg(k=('right', 'sum'), n=('right', 'size'), rt_sum=('rt', 'sum')).reset_index()


def fit_binomial(formula, d):
    with warnings.catch_warnings():
        warnings.simplefilter('ignore')
        result = smf.glm(formula, d.assign(right_rate=d.k / d.n), family=sm.families.Binomial(), freq_weights=d.n).fit(maxiter=200, tol=1e-10)
    if not result.converged:
        raise RuntimeError(f'Grouped-binomial estimator did not converge: {formula}')
    return result


def readout(counts, full=True):
    d = counts.copy()
    d['coh'] = d.coherence_pct / 100
    rows = []
    for b in range(len(EDGES) - 1):
        u = d[d.bin == b]
        if u.empty or u.pulse.nunique() < 2:
            continue
        slope = fit_binomial('right_rate ~ coh + C(mouse)', u[u.coherence_pct.abs() <= 36]).params['coh'] / 100
        direction = fit_binomial('right_rate ~ C(coherence_pct) + C(mouse) + pulse', u).params['pulse']
        T = u.rt_sum.sum() / u.n.sum()
        rows.append({'bin': b, 'lo_s': EDGES[b], 'hi_s': EDGES[b + 1], 'D': direction, 'b1_per_pct': slope,
                     'gamma_pct': direction / slope, 'T_s': T, 'gammaT': direction / slope * T,
                     'n': u.n.sum(), 'n_pulse': u.loc[u.pulse != 0, 'n'].sum(), 'positive_slope': slope > 0})
    res = pd.DataFrame(rows)
    if res.empty:
        return res
    early = (res.lo_s >= .3) & (res.hi_s <= 1.2)
    res['K'] = res.loc[early, 'gammaT'].mean()
    res['gammaT_minus_K'] = res.gammaT - res.K
    res['gammaT_over_K'] = res.gammaT / res.K
    if full:
        d_terms, s_terms = [], []
        for b in range(len(EDGES) - 1):
            d[f'D{b}'] = d.pulse * (d.bin == b)
            d[f'S{b}'] = np.sign(d.coherence_pct) * (d.pulse != 0) * (d.bin == b)
            d_terms.append(f'D{b}')
            s_terms.append(f'S{b}')
        formula = 'right_rate ~ C(coherence_pct):C(bin) + C(mouse) + ' + ' + '.join(d_terms + s_terms)
        r = fit_binomial(formula, d)
        res['D_joint'] = [r.params[f'D{b}'] for b in res.bin]
        res['S_joint'] = [r.params[f'S{b}'] for b in res.bin]
        res['congruent_logit'] = res.D_joint + res.S_joint
        res['incongruent_logit'] = -res.D_joint + res.S_joint
    return res


def prepare(models=None):
    from scripts.behavior.huk_shadlen_replication import load
    x = inputs()
    m = metadata(x)
    t = frame(m)
    old = load()
    old = old[(old.rel_rt_s >= .1) & (old.rel_rt_s < 5)]
    assert set(t.trial_id) == set(old.trial_id)
    res = readout(aggregate(t))
    ref = pd.read_csv(ROOT / 'dissemination/paper_accumulation/tables/pulse_dilution_2026-10-30.csv')
    errors = {c: float(np.max(np.abs(res[c].to_numpy() - ref[c].to_numpy()))) for c in ['D', 'b1_per_pct', 'gamma_pct', 'T_s', 'gammaT', 'K']}
    assert errors['gammaT'] < 1e-5, errors
    ref_d = pd.read_csv(ROOT / 'dissemination/paper_accumulation/tables/pulse_decomposition_2026-10-30_bins.csv')
    errors['D_joint'] = float(np.max(np.abs(res.D_joint.to_numpy() - ref_d.D.to_numpy())))
    errors['S_joint'] = float(np.max(np.abs(res.S_joint.to_numpy() - ref_d.S.to_numpy())))
    assert max(errors['D_joint'], errors['S_joint']) < 1e-5, errors
    m.to_pickle(OUT / 'cache/metadata.pkl')
    aggregate(t, by_rep=True).to_pickle(OUT / 'cache/data_counts.pkl')
    res.assign(family='data', seed=-1, scope='all_coherences').to_csv(OUT / 'data_readouts.csv', index=False)
    lo = readout(aggregate(t[t.coherence_pct.abs() <= 36]))
    lo.assign(family='data', seed=-1, scope='coherence_le36').to_csv(OUT / 'data_readouts_low_coherence.csv', index=False)
    record = {'exact_historical_trial_selection': True, 'n_input_trials': len(x['rt']), 'eligible_schedules': len(m),
              'n_readout_trials': len(t), 'grouped_estimator_max_absolute_errors': errors,
              'input_sha256': sha(INPUT), 'timing_sha256': sha(TIMING), 'trial_table_sha256': sha(TRIAL_TABLE),
              'models': list(models or FAMILIES), 'labels': LABELS, 'edged_seconds': EDGES.tolist(),
              'scope': 'Fixed parameters; same empirical responded-trial stimulus pool as existing fits; no parameter uncertainty'}
    (OUT / 'preparation_checks.json').write_text(json.dumps(record, indent=2) + '\n')
    print(json.dumps(record, indent=2), flush=True)


def fit_for(family, mouse):
    from scripts.ddm.pulse_joint_signatures import model_path
    if family == 'control_primary':
        return DDM / 'fits_resp_final' / f'{mouse}_L0U0V1Z0G1_control.pkl'
    return model_path('primary' if family == 'primary_sv0' else family)(mouse)


def simulate(families, mice, seed, reps):
    import torch
    from scripts.ddm.fit_mouse_ddm import select
    from scripts.ddm.primacy import make_model, simulate_outcomes
    from scripts.ddm.pulse_joint_signatures import OPTIONS
    x = inputs()
    meta = pd.read_pickle(OUT / 'cache/metadata.pkl')
    source_sha = {str(p.relative_to(ROOT)): sha(p) for p in [Path(__file__), ROOT / 'src/ddm/simulator.py', ROOT / 'src/ddm/ddm.py',
                                                           ROOT / 'scripts/ddm/fit_mouse_ddm.py']}
    for family in families:
        for mouse in sorted(mice or meta.mouse.unique()):
            path = fit_for(family, mouse)
            cache = OUT / 'cache' / f'{family}_{mouse}_seed{seed}_r{reps}.pkl'
            fingerprint = {'fit_sha256': sha(path), 'source_sha256': source_sha, 'input_sha256': sha(INPUT),
                           'metadata_sha256': sha(OUT / 'cache/metadata.pkl'), 'seed': seed, 'reps': reps}
            if cache.exists():
                previous = pd.read_pickle(cache)
                assert previous['fingerprint'] == fingerprint, f'Stale cache: {cache}'
                print(f'CACHED {family} {mouse} seed={seed} reps={reps}', flush=True)
                continue
            with path.open('rb') as f:
                fit = pickle.load(f)
            base = 'primary' if family == 'primary_sv0' else family
            opt = OPTIONS.get(base, {})
            rig = meta.loc[meta.mouse == mouse, 'rig'].iloc[0]
            rows = meta.loc[meta.mouse == mouse, 'row'].to_numpy()
            pw, nt = bool(fit.get('pulse_weight')), int(fit.get('n_pulse_times') or 0)
            model = make_model(fit['variant'], rig, fixed_guess_bias=False, responded=True,
                               front_end=opt.get('front_end'), ugm=opt.get('ugm', False), pulse_weight=pw, n_pulse_times=nt)
            assert fit.get('front_end') == opt.get('front_end')
            assert bool(fit.get('ugm')) == opt.get('ugm', False)
            assert fit.get('guess_model') == 'fast_only'
            assert fit.get('likelihood_params', {}).get('include_censored') is False
            data, stimulus = select(x, rows, pulse_weight=pw, pulse_times=nt)
            params = dict(fit['parameters'])
            if family == 'primary_sv0':
                params['sv'] = 0.
            independent_mouse_seed = zlib.crc32(f'{mouse}|{seed}'.encode())
            start = time.monotonic()
            raw = simulate_outcomes(model, params, stimulus, data['condition'], reps, independent_mouse_seed)
            raw['row'] = rows[raw.trial.to_numpy()]
            out = raw[['row', 'rep', 'rt', 'choice']].copy()
            out['row'] = out.row.astype(np.int32)
            out['rep'] = out.rep.astype(np.int16)
            out['rt'] = out.rt.astype(np.float32)
            out['choice'] = out.choice.astype(np.int8)
            assert len(out) == len(rows) * reps
            assert out.groupby('rep').row.nunique().eq(len(rows)).all()
            record = {'fingerprint': fingerprint, 'family': family, 'mouse': mouse, 'master_seed': seed,
                      'mouse_seed': independent_mouse_seed, 'reps': reps, 'fit_path': str(path), 'parameters': params,
                      'seconds': time.monotonic() - start, 'outcomes': out,
                      'simulated_nonresponse_fraction': float((out.choice < 0).mean())}
            pd.to_pickle(record, cache)
            print(f'DONE {family} {mouse} seed={seed} reps={reps} seconds={record["seconds"]:.2f} nonresponse={record["simulated_nonresponse_fraction"]:.3f}', flush=True)
            model.simulator.clear_cache()
            del stimulus, model, raw, out, record
            gc.collect()
            if torch.cuda.is_available():
                torch.cuda.empty_cache()


def analyze(families, seeds, reps, per_rep):
    meta = pd.read_pickle(OUT / 'cache/metadata.pkl')
    all_rows, replicate_rows, coverage = [], [], []
    for family in families:
        for seed in seeds:
            target = OUT / f'readout_{family}_seed{seed}_r{reps}.csv'
            replicate_target = OUT / f'readout_replicates_{family}_seed{seed}_r{reps}.csv'
            if target.exists() and (not per_rep or replicate_target.exists()):
                all_rows.append(pd.read_csv(target))
                if per_rep:
                    replicate_rows.append(pd.read_csv(replicate_target))
                continue
            parts, diagnostics = [], []
            for mouse in sorted(meta.mouse.unique()):
                p = OUT / 'cache' / f'{family}_{mouse}_seed{seed}_r{reps}.pkl'
                if not p.exists():
                    raise FileNotFoundError(p)
                r = pd.read_pickle(p)
                t = frame(meta, r['outcomes'])
                parts.append(t)
                diagnostics.append({'family': family, 'seed': seed, 'mouse': mouse,
                                    'simulated_nonresponse_fraction': r['simulated_nonresponse_fraction'],
                                    'simulated_trials': len(r['outcomes']), 'readout_trials': len(t)})
            t = pd.concat(parts, ignore_index=True)
            results, rep_results = [], []
            for scope, use in [('all_coherences', t), ('coherence_le36', t[t.coherence_pct.abs() <= 36])]:
                c = aggregate(use, by_rep=True)
                expected = c.groupby(GROUP, observed=True)[['k', 'n', 'rt_sum']].sum().reset_index()
                curve = readout(expected).assign(family=family, seed=seed, scope=scope)
                results.append(curve)
                if per_rep:
                    for rep, part in c.groupby('rep'):
                        try:
                            rr = readout(part, full=False).assign(family=family, seed=seed, scope=scope, rep=rep)
                            rr['failed'] = False
                        except Exception as e:
                            rr = pd.DataFrame([{'family': family, 'seed': seed, 'scope': scope, 'rep': rep,
                                                'failed': True, 'error': repr(e)}])
                        rep_results.append(rr)
            full = pd.concat(results, ignore_index=True)
            full.to_csv(target, index=False)
            all_rows.append(full)
            if rep_results:
                rep_frame = pd.concat(rep_results, ignore_index=True)
                rep_frame.to_csv(replicate_target, index=False)
                replicate_rows.append(rep_frame)
            pd.DataFrame(diagnostics).to_csv(OUT / f'coverage_{family}_seed{seed}_r{reps}.csv', index=False)
            coverage.extend(diagnostics)
            print(f'ANALYZED {family} seed={seed}', flush=True)
    data = pd.concat([pd.read_csv(OUT / 'data_readouts.csv'), pd.read_csv(OUT / 'data_readouts_low_coherence.csv')])
    curves = pd.concat([data, *all_rows], ignore_index=True)
    curves.to_csv(OUT / 'all_readouts.csv', index=False)
    summaries = []
    for (family, seed, scope), g in curves.groupby(['family', 'seed', 'scope'], sort=False):
        late = g[g.lo_s >= 1.2]
        summaries.append({'family': family, 'seed': seed, 'scope': scope, 'K': g.K.iloc[0],
                          'late_gammaT_mean': late.gammaT.mean(), 'late_over_early': late.gammaT.mean() / g.K.iloc[0],
                          'late_minus_early': late.gammaT.mean() - g.K.iloc[0], 'minimum_slope': g.b1_per_pct.min()})
    pd.DataFrame(summaries).to_csv(OUT / 'readout_summary.csv', index=False)
    if replicate_rows:
        pd.concat(replicate_rows, ignore_index=True).to_csv(OUT / 'all_replicate_readouts.csv', index=False)


def main():
    global OUT
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, default=OUT,
                        help='versioned output directory (default preserves the historical location)')
    parser.add_argument('--prepare', action='store_true')
    parser.add_argument('--simulate', action='store_true')
    parser.add_argument('--analyze', action='store_true')
    parser.add_argument('--families', nargs='+', choices=FAMILIES + WEIGHTED_FAMILIES, default=FAMILIES)
    parser.add_argument('--mice', nargs='+')
    parser.add_argument('--seed', type=int, default=0)
    parser.add_argument('--seeds', nargs='+', type=int, default=[0, 1])
    parser.add_argument('--reps', type=int, default=30)
    parser.add_argument('--per-rep', action='store_true')
    args = parser.parse_args()
    OUT = args.output
    (OUT / 'cache').mkdir(parents=True, exist_ok=True)
    if args.prepare:
        prepare(args.families)
    if args.simulate:
        simulate(args.families, args.mice, args.seed, args.reps)
    if args.analyze:
        analyze(args.families, args.seeds, args.reps, args.per_rep)


if __name__ == '__main__':
    main()
