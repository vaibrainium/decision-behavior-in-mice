"""Training-only broader-search check of the response-delay pilot.

The local pilot can collapse at the nested sigma=0 boundary. Independently
explore coupled timing/accumulation changes before treating that as evidence.
No held-out outcome is read. New results are stored beside, not over, the pilot.
"""
import argparse
import gc
import time

import numpy as np
import pandas as pd
from scipy.optimize import differential_evolution, minimize

from scripts.ddm.fit_response_delay import (OUT, FITS, inputs, model_for, partition,
    select, initialize, source_path, save_pickle, sha)


def run(mouse, split, device):
    path = FITS / f'{mouse}_delay_{split}_search_check.pkl'
    if path.exists():
        print('CACHED', path, flush=True)
        return
    anchor = pd.read_pickle(source_path(mouse, 'fixed', split))
    drift = pd.read_pickle(source_path(mouse, 'drift', split))
    x = inputs()
    train, _ = partition(x, mouse, split)
    n_times = int(anchor['n_pulse_times'])
    data, stim = select(x, train, pulse_times=n_times)
    model = model_for('delay', n_times, device)
    b = np.array([(v.lower_bound, v.upper_bound) for v in model.fit_param_specs.values()])
    lo, span = b[:, 0], np.diff(b, axis=1).ravel()
    unit = lambda p: np.clip((np.array([p[k] for k in model.fit_keys])-lo)/span, 0, 1)
    rng = np.random.default_rng(581)
    population = []
    for base in [anchor, drift]:
        for mean in [.05, .25, .5, .75]:
            for sigma in [.15, .7, 1.3]:
                p = base['parameters'] | {'ndt': mean, 'ndt_sigma': sigma}
                population.append(unit(p))
    population.append(unit(anchor['parameters'] | {'ndt_sigma': 0.}))
    while len(population) < 48:
        center = population[rng.integers(0, 24)]
        population.append(np.clip(center + rng.normal(0, .06, len(center)), 0, 1))
    best = {'nll': float('inf'), 'unit': None}
    calls = [0]
    start = time.monotonic()
    reps = [3]
    initialize(None, data, stim, 3, 42, model)

    def objective(u):
        nll = float(model._objective_function(lo + span * u, data, stim, reps[0], 0.))
        calls[0] += 1
        if nll < best['nll']:
            best.update(nll=nll, unit=np.array(u).copy())
        if calls[0] % 100 == 0:
            print(f'SEARCH {mouse} {split} reps={reps[0]} eval={calls[0]} best={best["nll"]:.3f} seconds={time.monotonic()-start:.1f}', flush=True)
        return nll

    de = differential_evolution(objective, [(0., 1.)] * len(lo), init=np.array(population),
                               maxiter=20, tol=0., atol=0., seed=581, polish=False,
                               recombination=.8, mutation=(.5, 1.0))
    screening = {'nll': best['nll'], 'unit': best['unit'].copy(), 'evaluations': calls[0]}
    initialize(None, data, stim, 15, 42, model)
    reps[0] = 15
    best = {'nll': float('inf'), 'unit': None}
    candidates = [de.x, unit(anchor['parameters'] | {'ndt_sigma': 0.})]
    old = source_path(mouse, 'delay', split)
    if old.exists():
        candidates.append(unit(pd.read_pickle(old)['parameters']))
    scored = [(objective(u), u) for u in candidates]
    # Refine both the DE candidate and nested solution, with every common
    # parameter free. The candidate is not chosen using held-out scores.
    results = []
    for _, u in sorted(scored[:2], key=lambda z: z[0]):
        simplex = np.repeat(u[None, :], len(u)+1, axis=0)
        for j in range(len(u)):
            simplex[j+1,j] += .025 if u[j] < .975 else -.025
        nm = minimize(objective, u, method='Nelder-Mead', bounds=[(0.,1.)]*len(u),
                      options={'maxfev': 450, 'xatol': 1e-4, 'fatol': .05, 'initial_simplex': simplex})
        results.append({'nll': float(nm.fun), 'converged': bool(nm.success), 'nfev': int(nm.nfev),
                        'message': str(nm.message)})
    p = model._build_params(lo + span * best['unit'])
    save_pickle(path, {'mouse': mouse, 'split': split, 'parameters': p, 'train_nll': best['nll'],
                      'screen': screening, 'refine': results, 'seconds': time.monotonic()-start,
                      'source_sha256': sha(__file__), 'anchor_sha256': sha(source_path(mouse,'fixed',split)),
                      'budget': '48 DE population x 20 generations at 3 reps; two 450-evaluation NM refinements at 15 reps',
                      'seed': 581, 'simulation_seed': 42, 'heldout_used': False})
    print(f'DONE {mouse} {split} nll={best["nll"]:.3f} ndt={p["ndt"]:.3f} sigma={p["ndt_sigma"]:.3f}', flush=True)
    model.simulator.clear_cache()
    del model, stim
    gc.collect()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--mouse', required=True)
    parser.add_argument('--split', default='all')
    parser.add_argument('--device', default='cuda', choices=['cuda','cpu'])
    a = parser.parse_args()
    run(a.mouse, a.split, a.device)
