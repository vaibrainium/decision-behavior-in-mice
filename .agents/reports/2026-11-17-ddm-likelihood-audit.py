"""Reproduce the Figure 3A likelihood audit from saved data and fits."""

import hashlib
from pathlib import Path
import pickle

import numpy as np
import pandas as pd
import torch

from scripts.ddm.fit_mouse_ddm import (
    CENSOR_AT, EVAL_SEED, MIN_RT, MouseDDM, cv_folds, heldout_nll,
    load_inputs, make_params, responded_only, select, too_few_responses,
)
from src.ddm.likelihood_calculator_censored import CensoredQMLE

ddm = Path('/mnt/data/processed/ddm')
draft = Path('dissemination/paper_accumulation/draft_2026-11-15')
inv = pd.read_csv('dissemination/reviewer_2026-11-13/control_fold_inventory.csv')
published = pd.read_csv(next((draft / 'figure3A_final_alternatives_2026-11-17').glob('*.csv'))).set_index('model')
inv = inv[inv.model.isin(published.index)]
source = ddm / 'ddm_inputs_global.npz'
raw = load_inputs(source)
assert np.array_equal(raw['censored'], raw['choice'] == -1)
assert np.array_equal(raw['censored'], np.isposinf(raw['rt']))
inputs = responded_only(raw)
assert np.isin(inputs['choice'], [0, 1]).all()
assert np.isfinite(inputs['rt']).all()
assert np.all((inputs['rt'] >= 0.3) & (inputs['rt'] <= 5.0))
pair = pd.DataFrame({key: raw[key] for key in ['condition', 'sched_pulse_type', 'signed_coherence']}).drop_duplicates()
assert not pair['condition'].duplicated().any()

def calculator(bins=9, censor=False):
    return CensoredQMLE(nbins=bins, include_censored=censor)

def score(q, pd_rt, pd_choice, obs_rt, obs_choice):
    return q.compute_nll(pd_rt, pd_choice, obs_rt, obs_choice,
                         np.zeros(len(pd_rt)), np.zeros(len(obs_rt)))

def hand_score(pr, pc, obs_rt, obs_choice, b=9, edges_source=None, unique=False):
    obs_choice = np.asarray(obs_choice)
    obs_rt = np.asarray(obs_rt)
    nc = (pc >= 0).sum()
    if nc == 0:
        return 20 * len(obs_choice)
    value = 0.0
    for side in [0, 1]:
        observed = obs_rt[obs_choice == side]
        sim = pr[pc == side]
        p_choice = (len(sim) + 0.5) / (nc + 1)
        value -= len(observed) * np.log(p_choice)
        reference = observed if edges_source is None else edges_source[0][edges_source[1] == side]
        if len(reference) >= b:
            cuts = np.quantile(reference, np.arange(1, b) / b)
            if unique:
                cuts = np.unique(cuts)
            observed_bins = np.searchsorted(cuts, observed, side='right')
            sim_bins = np.searchsorted(cuts, sim, side='right')
            counts = np.bincount(sim_bins, minlength=len(cuts) + 1)
            p = (counts + 0.5) / (len(sim) + 0.5 * len(counts))
            assert np.isclose(p.sum(), 1)
            value -= np.log(p[observed_bins]).sum()
    return value

pr = np.array([0.4, 0.6, 1.4, 0.7, np.inf])
pc = np.array([0, 0, 0, 1, -1])
rt = np.array([0.5, 1.0, 0.9, 1.3])
ch = np.array([0, 0, 1, 1])
known = -np.log((3.5 / 5) ** 2 * (1.5 / 5) ** 2 * (2.5 / 4) * (1.5 / 4) * (1.5 / 2) * (0.5 / 2))
np.testing.assert_allclose(score(calculator(2), pr, pc, rt, ch), known)
np.testing.assert_allclose(score(calculator(2), pr, pc, rt, ch), hand_score(pr, pc, rt, ch, b=2))
censored_known = known + 2 * np.log(6.5 / 5) * 2 - np.log(1.5 / 6.5)
np.testing.assert_allclose(score(calculator(2, True), pr, pc, np.r_[rt, np.inf], np.r_[ch, -1]), censored_known)
assert score(calculator(), pr[-1:], pc[-1:], rt, ch) == 80
np.testing.assert_allclose(score(calculator(), pr, pc, rt, ch), -2 * np.log(3.5 / 5) - 2 * np.log(1.5 / 5))
try:
    score(calculator(), pr, pc, np.r_[rt, np.inf], np.r_[ch, -1])
except ValueError:
    pass
else:
    raise AssertionError('Accepted censored observed input in responded-only mode')
print('Hand-computed choice/RT/censored, empty and sparse cases passed', flush=True)

def describe_cells(rows):
    labels = inputs['condition'][rows]
    choices = inputs['choice'][rows]
    times = inputs['rt'][rows]
    cells, bins, omissions, omitted_rts, ties, affected = 0, 0, 0, 0, 0, 0
    for condition in np.unique(labels):
        for side in [0, 1]:
            rt = times[(labels == condition) & (choices == side)]
            if len(rt) == 0:
                continue
            cells += 1
            if len(rt) < 9:
                omissions += 1
                omitted_rts += len(rt)
                continue
            bins += 1
            cuts = np.quantile(rt, np.linspace(0, 1, 10)[1:-1])
            if len(np.unique(cuts)) < len(cuts):
                ties += 1
                affected += len(rt)
    return np.array([cells, bins, omissions, omitted_rts, ties, affected])

fold_rows = {}
full_rows = {}
full_counts = np.zeros(6, dtype=int)
test_counts = np.zeros(6, dtype=int)
for mouse in sorted(inv.mouse.unique()):
    rows = np.flatnonzero((inputs['subject_id'] == mouse) & (inputs['sched_pulse_type'] == 0))
    full_rows[mouse] = rows
    full_counts += describe_cells(rows)
    folds = cv_folds(inputs['condition'][rows], 5)
    for fold in range(5):
        test = rows[folds == fold]
        train = rows[folds != fold]
        sub = inv[(inv.mouse == mouse) & (inv.fold == fold)]
        assert len(sub) == 5 and (sub.n_test == len(test)).all()
        assert len(np.intersect1d(train, test)) == 0
        fold_rows[(mouse, fold)] = (train, test)
        test_counts += describe_cells(test)
print('Cell counts [nonempty choices, RT-scored, sparse choices, RTs skipped, tied cut choices, RTs in tied cells]')
print('FULL', full_counts, 'TEST', test_counts, 'controls', sum(map(len, full_rows.values())), flush=True)
print('Min/max observed RT', inputs['rt'].min(), inputs['rt'].max(), 'CUDA', torch.cuda.is_available())

sc = inv.groupby(['mouse', 'model']).agg(nll=('test_nll', 'sum'), n=('n_test', 'sum'))
np.testing.assert_allclose(sc.nll.groupby('model').mean().loc[published.index], published.mean_test_nll)
np.testing.assert_allclose(-sc.nll.groupby('model').mean().loc[published.index], published.mean_test_ll)
np.testing.assert_allclose((-sc.nll / (np.log(2) * sc.n)).groupby('model').mean().loc[published.index],
                           published.mean_joint_test_bits_per_trial)
metrics = draft / 'figure3_information_metrics_2026-11-17'
training = pd.read_csv(metrics / 'independent_training_scores.csv')
assert len(training) == 100 and not training.duplicated(['mouse', 'model', 'seed']).any()
assert (training.input_sha256 == hashlib.file_digest(source.open('rb'), 'sha256').hexdigest()).all()
terms = 2 * training.training_nll_independent_seed + training.k * np.log(training.n_train)
np.testing.assert_allclose(terms, training.bic_qmle, rtol=1e-12)
np.testing.assert_allclose(terms.groupby(training.model).mean().loc[published.index], published.mean_bic_qmle, rtol=1e-12)
fit_inv = pd.read_csv(metrics / 'full_control_fit_inventory.csv')
for row in fit_inv.itertuples():
    path = Path(row.path)
    assert hashlib.file_digest(path.open('rb'), 'sha256').hexdigest() == row.sha256
    with path.open('rb') as f:
        fit = pickle.load(f)
    assert row.n_train == fit['n_train'] == len(full_rows[row.mouse])
    assert len(fit['free_parameters']) == row.k
print('Figure 3A score arithmetic and full-control hashes verified', flush=True)

class AuditedMouseDDM(MouseDDM):
    def _simulate_condition(self, stimulus, params, n_reps):
        self.simulated_rows = super()._simulate_condition(stimulus, params, n_reps)
        return self.simulated_rows

def rescore(row, train_rows, score_rows, seed, reps, expected):
    with Path(row.path).open('rb') as f:
        fit = pickle.load(f)
    free, fixed = make_params(fit['variant'], fit['guess_model'],
                              fixed_guess_bias=fit['fixed_guess_bias'],
                              leak_bounds=fit['leak_bounds'], extrema_samples=fit.get('extrema_samples', False),
                              nominal_input=fit.get('nominal_input', False))
    rig = np.unique(inputs['data_source'][score_rows]).item()
    device = 'cuda' if torch.cuda.is_available() else 'cpu'
    model = AuditedMouseDDM(free, fixed, device=device, likelihood_params=fit['likelihood_params'],
                     min_rt=MIN_RT[rig], censor_at=CENSOR_AT)
    d, stimulus = select(inputs, score_rows, nominal=fit.get('nominal_input', False))
    official = heldout_nll(model, fit['parameters'], d, stimulus, reps, seed=seed)
    sim = model.simulated_rows
    assert len(sim) == reps * len(score_rows)
    pc = sim.choice.to_numpy()
    pr = sim.rt.to_numpy()
    labs = sim.signed_coherence.to_numpy()
    np.testing.assert_array_equal(labs, np.tile(d['condition'], reps))
    assert np.isin(pc, [-1, 0, 1]).all()
    assert np.isfinite(pr[pc >= 0]).all()
    no_resp = (pc < 0).mean()
    assert no_resp < 0.5 and not too_few_responses(model.likelihood_calc, pc)
    sums = np.zeros(3)
    for label in np.unique(d['condition']):
        m = labs == label
        o = d['condition'] == label
        ref = train_rows[inputs['condition'][train_rows] == label]
        args = (pr[m], pc[m], d['rt'][o], d['choice'][o])
        sums[0] += hand_score(*args)
        sums[1] += hand_score(*args, unique=True)
        sums[2] += hand_score(*args, edges_source=(inputs['rt'][ref], inputs['choice'][ref]), unique=True)
    np.testing.assert_allclose(sums[0], official, rtol=1e-12, atol=1e-9)
    if seed == model.seed:
        fitted_values = np.array([fit['parameters'][key] for key in model.fit_keys])
        training_objective = model._objective_function(fitted_values, d, stimulus, reps)
        np.testing.assert_allclose(training_objective, official, rtol=0, atol=1e-8)
    if device == 'cuda':
        np.testing.assert_allclose(official, expected, rtol=0, atol=1e-8)
    print(f'{row.mouse:7} {row.model:4} {seed=} {reps=} n={len(score_rows)} '
          f'archive={expected:.9f} {device}={official:.9f} delta={official-expected:+.6f} '
          f'no_response={no_resp:.4f} dedup_change={sums[1]-official:+.6f} train_edges_score={sums[2]:.6f}',
          flush=True)

for row in inv.itertuples():
    with Path(row.path).open('rb') as f:
        fit = pickle.load(f)
    train_rows, test_rows = fold_rows[(row.mouse, row.fold)]
    assert fit['n_test'] == len(test_rows) and fit['n_train'] == len(train_rows)
    assert fit['likelihood_params'] == {'method': 'qmle_censored', 'nbins': 9,
                                       'rt_nllh_weight': 1.0, 'include_censored': False}
    np.testing.assert_allclose(fit['test_nll'], row.test_nll, rtol=1e-12)
print(f'Read back {len(inv)} CV fit files and matched stored settings/scores', flush=True)
for mouse in ['DBM12', 'PSUIM7']:
    train_rows, test_rows = fold_rows[mouse, 0]
    for row in inv[(inv.mouse == mouse) & (inv.fold == 0)].itertuples():
        with Path(row.path).open('rb') as f:
            fit = pickle.load(f)
        assert fit['n_test'] == len(test_rows) and fit['n_train'] == len(train_rows)
        np.testing.assert_allclose(fit['test_nll'], row.test_nll, rtol=1e-12)
        rescore(row, train_rows, test_rows, EVAL_SEED, fit['n_reps'], row.test_nll)

row = fit_inv[(fit_inv.mouse == 'DBM12') & (fit_inv.model == 'C')].iloc[0]
ref = training[(training.mouse == row.mouse) & (training.model == row.model)].iloc[0]
rescore(row, full_rows[row.mouse], full_rows[row.mouse], int(ref.seed), int(ref.n_reps), ref.training_nll_independent_seed)

row = inv[(inv.mouse == 'DBM12') & (inv.model == 'C') & (inv.fold == 0)].iloc[0]
with Path(row.path).open('rb') as f:
    fit = pickle.load(f)
train_rows, _ = fold_rows[(row.mouse, row.fold)]
rescore(row, train_rows, train_rows, 42, fit['n_reps'], fit['train_nll'])
