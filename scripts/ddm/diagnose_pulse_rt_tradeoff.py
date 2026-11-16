"""Decompose the held-out choice/RT objective for the pulse-model tradeoff.

Uses the original CV folds, fitted parameters, QMLE bins, smoothing and simulation
draws. Model parameters are not refitted. The additional matched pulse-weight
pair differs by the presence of drift variability, avoiding an entirely
confounded comparison with the power/leak/urgency benchmark.
"""
import argparse
import gc
import hashlib
import json
import pickle
import time
from pathlib import Path

import numpy as np
import pandas as pd

from scripts.ddm.fit_mouse_ddm import cv_folds, select
from scripts.ddm.rescore_fits import inputs
from scripts.ddm.primacy import make_model
from src.ddm.likelihood_calculator_censored import CensoredQMLE, EMPTY_CELL_PENALTY

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'dissemination/pulse_rt_tradeoff_2026-11-13'
DDM = Path('/mnt/data/processed/ddm')
MODELS = {
    'power_leak_urgency': ('fits_joint_power_integrators', 'L1U1V1Z0G1', 'power'),
    'pw_per_time': ('fits_joint_unfreeze_pulse_time_weights', 'L0U0V1Z0G1', None),
    'pw_per_time_no_sv': ('fits_joint_unfreeze_pulse_time_weights', 'L0U0V0Z0G1', None),
}
RT_EDGES = np.round(np.arange(.3, 5.0001, .1), 6)


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def details(q, rp, cp, kp, data, coherence, pulse):
    cells, bins, hist = [], [], []
    rd, cd, kd = (data[k] for k in ['rt', 'choice', 'condition'])
    for condition in np.unique(kd):
        d, m = kd == condition, kp == condition
        cohs, pulses = np.unique(coherence[d]), np.unique(pulse[d])
        assert len(cohs) == len(pulses) == 1
        coh, pul = int(round(cohs[0] * 100)), int(pulses[0])
        meta = {'condition': int(condition), 'coherence': coh, 'scheduled_pulse': pul,
                'trial_type': 'control' if pul == 0 else 'pulse', 'pulse_stage': abs(pul)}
        dc = np.array([(cd[d] == k).sum() for k in [0, 1]])
        mc = np.array([(cp[m] == k).sum() for k in [0, 1]])
        if mc.sum() == 0:
            cells.append(meta | {'choice_nll': 0., 'rt_nll': 0., 'empty_penalty': EMPTY_CELL_PENALTY * dc.sum(),
                                 'n': int(dc.sum()), 'simulated_responses': 0})
            continue
        outcome = q._multinomial_nll(dc, mc)
        rt_total = 0.
        for k in [0, 1]:
            observed = rd[d & (cd == k)]
            predicted = rp[m & (cp == k)]
            correctness = 'zero_coherence' if coh == 0 else ('correct' if (k == 1) == (coh > 0) else 'error')
            h_data = np.histogram(observed, bins=RT_EDGES)[0]
            h_model = np.histogram(predicted, bins=RT_EDGES)[0]
            for b in range(len(RT_EDGES) - 1):
                hist.append(meta | {'choice': k, 'correctness': correctness, 'lo_s': RT_EDGES[b], 'hi_s': RT_EDGES[b + 1],
                                    'data_n': int(h_data[b]), 'model_n': int(h_model[b])})
            if len(observed) < q.nbins:
                continue
            edges = np.quantile(observed, np.linspace(0, 1, q.nbins + 1))
            edges[0], edges[-1] = -np.inf, np.inf
            n = np.histogram(observed, edges)[0]
            h = np.histogram(predicted, edges)[0]
            prob = (h + q.alpha) / (h.sum() + q.alpha * len(h))
            nll = -n * np.log(prob)
            rt_total += nll.sum()
            assert np.isclose(nll.sum(), q._rt_nll(observed, predicted))
            for b in range(q.nbins):
                bins.append(meta | {'choice': k, 'correctness': correctness, 'quantile_bin': b,
                                    'lo_s': edges[b], 'hi_s': edges[b + 1], 'observed_count': int(n[b]),
                                    'simulated_count': int(h[b]), 'probability': prob[b], 'rt_nll': nll[b]})
        cells.append(meta | {'choice_nll': outcome, 'rt_nll': rt_total, 'empty_penalty': 0.,
                             'n': int(dc.sum()), 'simulated_responses': int(mc.sum())})
    cells, bins, hist = pd.DataFrame(cells), pd.DataFrame(bins), pd.DataFrame(hist)
    total = q.compute_nll(rp, cp, rd, cd, kp, kd)
    assert np.isclose(total, cells[['choice_nll', 'rt_nll', 'empty_penalty']].to_numpy().sum(), atol=1e-7)
    return total, cells, bins, hist


def run(models, mice, folds, seed):
    import torch
    x = inputs()
    for family in models:
        folder, variant, frontend = MODELS[family]
        for mouse in sorted(mice or np.unique(x['subject_id'])):
            mr = np.flatnonzero(x['subject_id'] == mouse)
            labels = cv_folds(x['condition'][mr], 5)
            for fold in folds:
                path = DDM / folder / f'{mouse}_{variant}_cv{fold}.pkl'
                cache = OUT / 'cache' / f'{family}_{mouse}_cv{fold}_seed{seed}.pkl'
                fingerprint = {'fit_sha256': sha(path), 'script_sha256': sha(__file__), 'seed': seed}
                if cache.exists():
                    r = pd.read_pickle(cache)
                    assert r['fingerprint'] == fingerprint
                    continue
                with path.open('rb') as f:
                    fit = pickle.load(f)
                test = mr[labels == fold]
                assert len(test) == fit['n_test']
                nt = int(fit.get('n_pulse_times') or 0)
                data, stimulus = select(x, test, pulse_times=nt)
                rig = str(np.unique(x['data_source'][mr]).item())
                model = make_model(variant, rig, False, responded=True, front_end=frontend, n_pulse_times=nt)
                q = model.likelihood_calc
                assert isinstance(q, CensoredQMLE) and not q.include_censored and q.rt_nllh_weight == 1
                start = time.monotonic()
                np.random.seed(seed)
                model.simulator.clear_cache()
                model._labels = data['condition']
                model.precompute(*model._stimulus_shape(stimulus), n_reps=fit['n_reps'])
                sim = model._simulate_condition(stimulus, fit['parameters'], fit['n_reps'])
                if sim is None:
                    raise RuntimeError(f'Simulation failed: {path}')
                total, cells, bins, hist = details(q, sim.rt.to_numpy(), sim.choice.to_numpy(), sim.signed_coherence.to_numpy(),
                                                  data, x['signed_coherence'][test], x['sched_pulse_type'][test])
                r = {'family': family, 'mouse': mouse, 'fold': fold, 'seed': seed, 'n_reps': fit['n_reps'],
                     'stored_test_nll': fit['test_nll'], 'test_nll': total, 'difference_from_stored': total - fit['test_nll'],
                     'n_test': len(test), 'seconds': time.monotonic() - start, 'fingerprint': fingerprint,
                     'cells': cells, 'bins': bins, 'hist': hist}
                pd.to_pickle(r, cache)
                print(f'{family} {mouse} cv{fold} seed={seed}: score={total:.3f}, stored difference={r["difference_from_stored"]:.4f}, seconds={r["seconds"]:.2f}', flush=True)
                model.simulator.clear_cache()
                del model, stimulus, sim, r
                gc.collect()
                if torch.cuda.is_available():
                    torch.cuda.empty_cache()


def collect(seed):
    rows, cells, bins, hist = [], [], [], []
    for path in sorted((OUT / 'cache').glob(f'*_seed{seed}.pkl')):
        r = pd.read_pickle(path)
        meta = {k: r[k] for k in ['family', 'mouse', 'fold', 'seed']}
        rows.append({k: v for k, v in r.items() if k not in ['cells', 'bins', 'hist', 'fingerprint']})
        for name, target in [('cells', cells), ('bins', bins), ('hist', hist)]:
            target.append(r[name].assign(**meta))
    summary = pd.DataFrame(rows)
    summary.to_csv(OUT / f'fold_scores_seed{seed}.csv', index=False)
    c, b, h = [pd.concat(parts, ignore_index=True) for parts in [cells, bins, hist]]
    c.to_csv(OUT / f'cell_scores_seed{seed}.csv', index=False)
    b.to_csv(OUT / f'rt_bin_scores_seed{seed}.csv', index=False)
    h.to_csv(OUT / f'rt_histograms_seed{seed}.csv', index=False)
    pairs = [('pw_per_time_no_sv', 'power_leak_urgency'), ('pw_per_time_no_sv', 'pw_per_time'),
             ('pw_per_time', 'power_leak_urgency')]
    changes, bin_changes = [], []
    keys = ['mouse', 'fold', 'condition']
    for candidate, reference in pairs:
        pair = f'{candidate}_minus_{reference}'
        z = c[c.family == candidate].merge(c[c.family == reference], on=keys, suffixes=('_candidate', '_reference'), validate='one_to_one')
        out = z[keys].copy()
        out['pair'] = pair
        for col in ['coherence', 'scheduled_pulse', 'trial_type', 'pulse_stage', 'n']:
            assert (z[col + '_candidate'] == z[col + '_reference']).all()
            out[col] = z[col + '_candidate']
        for col in ['choice_nll', 'rt_nll', 'empty_penalty']:
            out['delta_' + col] = z[col + '_candidate'] - z[col + '_reference']
        out['delta_total'] = out[['delta_choice_nll', 'delta_rt_nll', 'delta_empty_penalty']].sum(axis=1)
        changes.append(out)
        z = b[b.family == candidate].merge(b[b.family == reference], on=keys + ['choice', 'quantile_bin'],
                                          suffixes=('_candidate', '_reference'), validate='one_to_one')
        out = z[keys + ['choice', 'quantile_bin']].copy()
        out['pair'] = pair
        for col in ['coherence', 'scheduled_pulse', 'trial_type', 'pulse_stage', 'correctness', 'lo_s', 'hi_s', 'observed_count']:
            assert (z[col + '_candidate'] == z[col + '_reference']).all()
            out[col] = z[col + '_candidate']
        out['delta_rt_nll'] = z.rt_nll_candidate - z.rt_nll_reference
        bin_changes.append(out)
    delta = pd.concat(changes, ignore_index=True)
    rt_delta = pd.concat(bin_changes, ignore_index=True)
    delta.to_csv(OUT / f'cell_differences_seed{seed}.csv', index=False)
    rt_delta.to_csv(OUT / f'rt_bin_differences_seed{seed}.csv', index=False)
    for name, by in [('mouse', ['mouse']), ('trial_type', ['trial_type']), ('coherence', ['coherence']), ('quantile', ['quantile_bin']),
                     ('correctness', ['correctness']), ('trial_correctness', ['trial_type', 'correctness'])]:
        source = rt_delta if name in ['quantile', 'correctness', 'trial_correctness'] else delta
        cols = ['delta_rt_nll'] if source is rt_delta else ['delta_choice_nll', 'delta_rt_nll', 'delta_total', 'n']
        source.groupby(['pair', *by])[cols].sum().reset_index().to_csv(OUT / f'difference_by_{name}_seed{seed}.csv', index=False)
    print(summary.groupby('family')[['test_nll', 'stored_test_nll', 'difference_from_stored']].sum().to_string(), flush=True)
    print(delta.groupby('pair')[['delta_choice_nll', 'delta_rt_nll', 'delta_total']].sum().to_string(), flush=True)


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--run', action='store_true')
    p.add_argument('--collect', action='store_true')
    p.add_argument('--models', nargs='+', choices=list(MODELS), default=list(MODELS))
    p.add_argument('--mice', nargs='+')
    p.add_argument('--folds', nargs='+', type=int, default=list(range(5)))
    p.add_argument('--seed', type=int, default=12345)
    a = p.parse_args()
    (OUT / 'cache').mkdir(parents=True, exist_ok=True)
    if a.run:
        run(a.models, a.mice, a.folds, a.seed)
    if a.collect:
        collect(a.seed)


if __name__ == '__main__':
    main()
