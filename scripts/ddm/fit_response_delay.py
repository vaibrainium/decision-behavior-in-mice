"""Exploratory PSUIM6/7 response-delay pilot; existing fits are never overwritten.

Fits all common parameters on each training partition. Split-specific fixed/sv
fits initialize a bounded, two-precision local search. This is a pilot optimizer,
not a claim of a global optimum. Original fits remain the reference benchmarks.
No held-out outcomes or pulse-readout scores select starts or fitted parameters.
"""
from __future__ import annotations

import argparse
import gc
import hashlib
import json
import logging
import pickle
import platform
import subprocess
import time
from pathlib import Path

import numpy as np
import pandas as pd
import scipy
from scipy.optimize import minimize
import torch

from scripts.ddm.fit_mouse_ddm import (MouseDDM, RESPONDED_LIKELIHOOD_PARAMS,
    cv_folds, make_params, select)
from scripts.ddm.rescore_fits import inputs, terms
from src.ddm.ddm import FreeParam
from src.ddm.response_delay import ResponseDelaySimulator

ROOT = Path(__file__).resolve().parents[2]
DDM = Path('/mnt/data/processed/ddm')
SOURCE = DDM / 'fits_joint_unfreeze_pulse_time_weights'
OUT = ROOT / 'dissemination/response_delay_2026-11-14'
FITS = DDM / 'fits_response_delay_2026-11-14'
VARIANTS = {'fixed': 'L0U0V0Z0G1', 'drift': 'L0U0V1Z0G1'}
SOURCES = [Path(__file__), ROOT / 'src/ddm/response_delay.py', ROOT / 'src/ddm/simulator.py',
           ROOT / 'src/ddm/ddm.py', ROOT / 'src/ddm/likelihood_calculator_censored.py',
           ROOT / 'scripts/ddm/fit_mouse_ddm.py']


def sha(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as f:
        for b in iter(lambda: f.read(1048576), b''):
            h.update(b)
    return h.hexdigest()


def write_json(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + '.tmp')
    tmp.write_text(json.dumps(value, indent=2, allow_nan=False) + '\n')
    tmp.replace(path)


def save_pickle(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix('.tmp')
    with tmp.open('wb') as f:
        pickle.dump(value, f)
    tmp.replace(path)


def source_path(mouse, family, split):
    return FITS / f'{mouse}_delay_{split}.pkl' if family == 'delay' else SOURCE / f'{mouse}_{VARIANTS[family]}_{split}.pkl'


def partition(x, mouse, split):
    rows = np.flatnonzero(x['subject_id'] == mouse)
    if split == 'all':
        return rows, None
    if split not in [f'cv{k}' for k in range(5)]:
        raise ValueError(split)
    folds = cv_folds(x['condition'][rows], 5)
    return rows[folds != int(split[2:])], rows[folds == int(split[2:])]


def model_for(family, n_times, device='cuda'):
    variant = 'L0U0V1Z0G1' if family == 'drift' else 'L0U0V0Z0G1'
    free, fixed = make_params(variant, 'fast_only', n_pulse_times=n_times)
    if family == 'delay':
        free['ndt_sigma'] = FreeParam(0., 1.5)
    model = MouseDDM(free, fixed, device=device, censor_at=5., min_rt=(.3, 'floor'),
                     likelihood_params=RESPONDED_LIKELIHOOD_PARAMS)
    if family == 'delay':
        model.simulator = ResponseDelaySimulator(device)
    return model


def initialize(x, data, stimulus, n_reps, seed, model):
    model.simulator.clear_cache()
    model._precomputed = None
    gc.collect()
    np.random.seed(seed)
    model._labels = data['condition']
    model.precompute(*model._stimulus_shape(stimulus), n_reps)


def fit_one(x, mouse, split, args):
    path = source_path(mouse, 'delay', split)
    anchors = {}
    for family in ['fixed', 'drift']:
        p = source_path(mouse, family, split)
        anchors[family] = pd.read_pickle(p)
    train, test = partition(x, mouse, split)
    n_times = int(anchors['fixed']['n_pulse_times'])
    assert n_times == int(anchors['drift']['n_pulse_times'])
    assert all(a['n_train'] == len(train) for a in anchors.values())
    signature = dict(mouse=mouse, split=split, seed=args.fit_seed,
                     source_sha256={str(p.relative_to(ROOT)): sha(p) for p in SOURCES},
                     anchor_sha256={f: sha(source_path(mouse, f, split)) for f in anchors},
                     screen_reps=args.screen_reps, n_reps=args.n_reps,
                     screen_evals=args.screen_evals, refine_evals=args.refine_evals,
                     train_rows_sha256=hashlib.sha256(train.tobytes()).hexdigest())
    if path.exists():
        previous = pd.read_pickle(path)
        assert previous['signature'] == signature, f'Existing incompatible result: {path}'
        print(f'CACHED {mouse} {split}', flush=True)
        return
    model = model_for('delay', n_times, args.device)
    data, stim = select(x, train, pulse_times=n_times)
    bounds = np.array([(s.lower_bound, s.upper_bound) for s in model.fit_param_specs.values()])
    lo, span = bounds[:, 0], np.diff(bounds, axis=1).ravel()
    params_to_unit = lambda p: np.clip((np.array([p[k] for k in model.fit_keys]) - lo) / span, 0, 1)
    checkpoint = path.with_suffix('.pilot_checkpoint.pkl')
    state = {'signature': signature, 'completed_stages': {}, 'stage_best': {}}
    if checkpoint.exists():
        state = pd.read_pickle(checkpoint)
        assert state['signature'] == signature, f'Incompatible checkpoint: {checkpoint}'
    initial = []
    for family, a in anchors.items():
        for sigma in [0., .25, .5, .8, 1.2]:
            initial.append((f'{family}_sigma{sigma}', params_to_unit(a['parameters'] | {'ndt_sigma': sigma})))
    # Additional timing-dominant starts explore a larger mean and smaller bound;
    # all are specified before scoring and use training fits only.
    for mean in [.45, .7]:
        p = anchors['fixed']['parameters'] | {'ndt': mean, 'ndt_sigma': .7}
        p['a'] *= .75
        initial.append((f'timing_mean{mean}', params_to_unit(p)))
    trace = []
    t0 = time.monotonic()
    for stage, reps, budget in [('screen', args.screen_reps, args.screen_evals),
                                 ('refine', args.n_reps, args.refine_evals)]:
        if stage in state['completed_stages']:
            print(f'RESUME {mouse} {split} completed {stage}', flush=True)
            continue
        initialize(x, data, stim, reps, args.fit_seed, model)
        best = state['stage_best'].get(stage, {'nll': float('inf'), 'unit': None})
        calls = [0]

        def objective(unit):
            values = lo + span * np.clip(unit, 0, 1)
            nll = float(model._objective_function(values, data, stim, reps, 0.))
            calls[0] += 1
            if nll < best['nll']:
                best.update(nll=nll, unit=np.clip(unit, 0, 1).copy())
            if calls[0] % 50 == 0:
                state['stage_best'][stage] = best.copy()
                save_pickle(checkpoint, state)
                trace.append({'stage': stage, 'evaluations': calls[0], 'best_nll': best['nll'],
                              'seconds': time.monotonic() - t0})
                print(f'FIT {mouse} {split} {stage} eval={calls[0]} best={best["nll"]:.3f} elapsed={time.monotonic()-t0:.1f}s', flush=True)
            return nll

        candidates = list(initial)
        if stage == 'refine':
            candidates.extend((f'screen_{i}', v['unit']) for i, v in enumerate(state['completed_stages']['screen']['solutions']))
        if best['unit'] is not None:
            candidates.append(('checkpoint_best', best['unit']))
        scored = sorted([(objective(u), name, u) for name, u in candidates], key=lambda v: v[0])
        # Two separated starts at each precision. Common parameters are free in
        # both; no pulse summary or held-out score enters this selection.
        chosen = [scored[0]]
        for item in scored[1:]:
            if np.linalg.norm(item[2] - chosen[0][2]) > .08:
                chosen.append(item)
                break
        solutions = []
        for score, name, unit in chosen:
            steps = np.full(len(unit), .015)
            steps[model.fit_keys.index('ndt')] = .025 / span[model.fit_keys.index('ndt')]
            steps[model.fit_keys.index('ndt_sigma')] = .08 / 1.5
            simplex = np.repeat(unit[None, :], len(unit) + 1, axis=0)
            for j, step in enumerate(steps):
                simplex[j+1, j] += step if unit[j] + step <= 1 else -step
            result = minimize(objective, unit, method='Nelder-Mead', bounds=[(0., 1.)] * len(unit),
                              options={'maxfev': budget, 'xatol': 1e-4, 'fatol': .05,
                                       'initial_simplex': simplex})
            solutions.append({'start': name, 'nll': float(result.fun), 'unit': result.x,
                              'converged': bool(result.success), 'message': str(result.message),
                              'nfev': int(result.nfev)})
        solutions.append({'start': 'best_evaluated', **best, 'converged': False,
                          'message': 'Best evaluated point, not an independent convergence certificate'})
        state['completed_stages'][stage] = {'reps': reps, 'evaluations': calls[0],
                                           'solutions': solutions, 'best': best.copy()}
        state['stage_best'][stage] = best.copy()
        save_pickle(checkpoint, state)
    best = state['completed_stages']['refine']['best']
    parameters = model._build_params(lo + span * best['unit'])
    result = dict(mouse=mouse, family='delay', split=split, parameters=parameters,
                  free_parameters=model.fit_keys, n_train=len(train), n_test=0 if test is None else len(test),
                  train_nll=float(best['nll']), signature=signature, stages=state['completed_stages'],
                  fit_seconds=time.monotonic() - t0, n_pulse_times=n_times,
                  likelihood_params=RESPONDED_LIKELIHOOD_PARAMS, optimizer='bounded_multistart_Nelder-Mead_pilot',
                  global_optimum_established=False, trace=trace)
    save_pickle(path, result)
    print(f'DONE {mouse} {split} nll={best["nll"]:.3f} mean_delay={parameters["ndt"]:.3f} sigma={parameters["ndt_sigma"]:.3f}', flush=True)
    model.simulator.clear_cache()
    del model, stim
    gc.collect()


def simulate_selected(model, params, data, stim, reps, seed):
    initialize(None, data, stim, reps, seed, model)
    out = model._simulate_condition(stim, params, reps)
    assert out is not None and len(out) == len(data['rt']) * reps
    return out


def score_one(x, mouse, family, split, args):
    if split == 'all':
        return
    fit_path = source_path(mouse, family, split)
    fit = pd.read_pickle(fit_path)
    train, test = partition(x, mouse, split)
    assert fit['n_train'] == len(train) and fit['n_test'] == len(test)
    n_times = int(fit['n_pulse_times'])
    model = model_for(family, n_times, args.device)
    data, stim = select(x, test, pulse_times=n_times)
    for seed in args.eval_seeds:
        path = OUT / 'cache' / f'score_{family}_{mouse}_{split}_r{args.eval_reps}_s{seed}.pkl'
        fingerprint = {'fit_sha256': sha(fit_path), 'source_sha256': {str(p.relative_to(ROOT)): sha(p) for p in SOURCES},
                       'seed': seed, 'reps': args.eval_reps}
        if path.exists():
            assert pd.read_pickle(path)['fingerprint'] == fingerprint
            continue
        out = simulate_selected(model, fit['parameters'], data, stim, args.eval_reps, seed)
        total, choice, rt = terms(model.likelihood_calc, out.rt.to_numpy(), out.choice.to_numpy(),
                                  out.signed_coherence.to_numpy(), data['rt'], data['choice'], data['condition'])
        assert np.isclose(total, choice + rt, atol=1e-7), 'Empty-cell penalty or reconstruction failure'
        result = dict(fingerprint=fingerprint, mouse=mouse, family=family, split=split, seed=seed,
                       n=len(test), nll=total, choice_nll=choice, rt_nll=rt,
                       nonresponse=float((out.choice < 0).mean()))
        # Save trial/choice/RT outcomes for absolute fit plots and per-bin audits.
        out['row'] = np.tile(test, args.eval_reps)
        out['rep'] = np.repeat(np.arange(args.eval_reps), len(test))
        result['outcomes'] = out
        save_pickle(path, result)
        print(f'SCORE {family} {mouse} {split} seed={seed} nll={total:.3f} choice={choice:.3f} rt={rt:.3f}', flush=True)
    model.simulator.clear_cache()


def manifest(args):
    record = {'commit': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
              'source_sha256': {str(p.relative_to(ROOT)): sha(p) for p in SOURCES},
              'input_sha256': sha(DDM / 'ddm_inputs_global_ucla_nofreeze.npz'),
              'timing_sha256': sha(DDM / 'pulse_timing_global.npz'),
              'python': platform.python_version(), 'numpy': np.__version__, 'scipy': scipy.__version__,
              'pandas': pd.__version__, 'torch': torch.__version__, 'cuda': torch.version.cuda,
              'device': args.device, 'args': vars(args),
              'generalization': 'Trial holdout within the same mice/sessions, not new sessions or animals',
              'status': 'Exploratory pilot; no recovery or parameter confidence intervals yet'}
    target = OUT / f'manifest_{"fit" if args.fit else "score"}_{"_".join(args.mice)}.json'
    if target.exists():
        assert json.loads(target.read_text()) == record, f'Incompatible existing manifest: {target}'
    else:
        write_json(target, record)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--fit', action='store_true')
    parser.add_argument('--score', action='store_true')
    parser.add_argument('--mice', nargs='+', default=['PSUIM6', 'PSUIM7'])
    parser.add_argument('--splits', nargs='+', default=['all', 'cv0', 'cv1', 'cv2', 'cv3', 'cv4'])
    parser.add_argument('--families', nargs='+', choices=['fixed', 'drift', 'delay'], default=['fixed', 'drift', 'delay'])
    parser.add_argument('--device', choices=['cuda', 'cpu'], default='cuda')
    parser.add_argument('--fit-seed', type=int, default=42)
    parser.add_argument('--screen-reps', type=int, default=3)
    parser.add_argument('--n-reps', type=int, default=15)
    parser.add_argument('--screen-evals', type=int, default=350)
    parser.add_argument('--refine-evals', type=int, default=600)
    parser.add_argument('--eval-reps', type=int, default=60)
    parser.add_argument('--eval-seeds', type=int, nargs='+', default=[12345, 23456, 34567])
    args = parser.parse_args()
    if not args.fit and not args.score:
        parser.error('Choose --fit or --score')
    logging.getLogger().setLevel(logging.WARNING)
    OUT.mkdir(parents=True, exist_ok=True)
    FITS.mkdir(parents=True, exist_ok=True)
    manifest(args)
    x = inputs()
    for mouse in args.mice:
        for split in args.splits:
            if args.fit:
                fit_one(x, mouse, split, args)
            if args.score:
                for family in args.families:
                    score_one(x, mouse, family, split, args)


if __name__ == '__main__':
    main()
