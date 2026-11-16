"""Collect the exploratory response-delay pilot and check held-out pulse/RT fit.

All displayed model profiles use out-of-fold predictions, never in-sample pulse
summary fitting. Data intervals resample 50-trial blocks within each mouse and
session. They are pointwise descriptive intervals, not corrected group tests.
"""
import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd

from scripts.ddm.fit_response_delay import OUT, FITS, source_path, inputs, sha, write_json
from scripts.ddm.pulse_leak_urgency_signatures import observed, pseudo_onsets, with_bins, BINS
from scripts.ddm.pulse_descriptive_package import effect
from scripts.ddm.pulse_joint_signatures import stats_of

MICE = ['PSUIM6', 'PSUIM7']
FAMILIES = ['drift', 'fixed', 'delay']
COLORS = {'drift': '#0072B2', 'fixed': '#E69F00', 'delay': '#009E73'}
LINES = {'drift': '-', 'fixed': '--', 'delay': ':'}
MARKERS = {'drift': '^', 'fixed': 's', 'delay': 'D'}
LABELS = {'drift': 'Drift variability', 'fixed': 'Fixed delay, no drift variability', 'delay': 'Variable response delay'}


class Contrast:
    """Count-based implementation of existing coherence-matched pulse effects.

    Trials are expanded once per control pseudo-onset stage, just as with_bins.
    A bootstrap weight belongs to an original trial and is reused for every
    expansion; controls are not independently resampled for each pulse stage.
    """
    def __init__(self, obs, onsets, window=False):
        x = with_bins(obs, onsets)
        x = x[x.bin.notna()].copy()
        x['bin'] = x.bin.astype(int)
        self.window = window
        if window:
            x['window'] = np.where(x.bin < 3, '0.3-1.2', '1.2-5')
        by = ['mouse', 'stage', 'window'] if window else ['mouse', 'bin']
        self.by = by
        key = obs.reset_index(drop=True).reset_index().set_index('row')['index']
        tidx = key.loc[x.row].to_numpy()
        pulse, control = x.s.to_numpy() != 0, x.s.to_numpy() == 0
        self.pidx, self.cidx = tidx[pulse], tidx[control]
        self.pright = (x.choice.to_numpy()[pulse] == 1).astype(float)
        self.cright = (x.choice.to_numpy()[control] == 1).astype(float)
        pc = x.loc[pulse, by + ['coh', 's']].drop_duplicates().reset_index(drop=True)
        cc = x.loc[control, by + ['coh']].drop_duplicates().reset_index(drop=True)
        pmap = {tuple(v): i for i, v in enumerate(pc.itertuples(index=False, name=None))}
        cmap = {tuple(v): i for i, v in enumerate(cc.itertuples(index=False, name=None))}
        self.pc = pc
        self.pcodes = np.array([pmap[tuple(v)] for v in x.loc[pulse, by + ['coh', 's']].itertuples(index=False, name=None)])
        self.ccodes = np.array([cmap[tuple(v)] for v in x.loc[control, by + ['coh']].itertuples(index=False, name=None)])
        self.match = np.array([cmap.get(tuple(v), -1) for v in pc[by + ['coh']].itertuples(index=False, name=None)])
        self.nc = len(cc)
        self.groups = {}
        # Stage weighting in windows is equivalent to pulse-count weighting over
        # all valid cells; retain coherence matching within the relevant stage.
        outby = ['mouse', 'window'] if window else ['mouse', 'bin']
        for key, indices in pc.groupby(outby, sort=True).indices.items():
            for sign in [0, -1, 1]:
                ids = np.asarray(indices)
                if sign:
                    ids = ids[pc.s.to_numpy()[ids] == sign]
                self.groups[tuple(key) + (sign,)] = ids
        self.outby = outby + ['sign']

    def __call__(self, weights):
        pn = np.bincount(self.pcodes, weights[self.pidx], len(self.pc))
        pk = np.bincount(self.pcodes, weights[self.pidx] * self.pright, len(self.pc))
        cn = np.bincount(self.ccodes, weights[self.cidx], self.nc)
        ck = np.bincount(self.ccodes, weights[self.cidx] * self.cright, self.nc)
        ok = (self.match >= 0) & (pn > 0)
        ok[ok] &= cn[self.match[ok]] > 0
        delta = np.zeros(len(pn))
        delta[ok] = 100 * self.pc.s.to_numpy()[ok] * (pk[ok] / pn[ok] - ck[self.match[ok]] / cn[self.match[ok]])
        vals = []
        for ids in self.groups.values():
            ids = ids[ok[ids]]
            vals.append(np.average(delta[ids], weights=pn[ids]) if len(ids) else np.nan)
        return np.array(vals)

    def table(self, weights):
        return pd.DataFrame(list(self.groups), columns=self.outby).assign(effect_pp=self(weights))

    def cell_table(self):
        """Unweighted pulse/control probabilities before coherence averaging."""
        pn = np.bincount(self.pcodes, minlength=len(self.pc))
        pk = np.bincount(self.pcodes, self.pright, len(self.pc))
        cn = np.bincount(self.ccodes, minlength=self.nc)
        ck = np.bincount(self.ccodes, self.cright, self.nc)
        ok = (self.match >= 0) & (pn > 0)
        ok[ok] &= cn[self.match[ok]] > 0
        t = self.pc.loc[ok].copy()
        t['n_pulse'] = pn[ok]
        t['p_right_pulse'] = pk[ok] / pn[ok]
        t['p_right_control'] = ck[self.match[ok]] / cn[self.match[ok]]
        t['effect_pp'] = 100 * t.s * (t.p_right_pulse - t.p_right_control)
        return t


def prepare(n_boot):
    x = inputs()
    obs = observed(x, MICE)
    obs['session'] = x['idx_session'][obs.row.to_numpy()]
    # Blocks are defined in the original session chronology, before selecting
    # symmetric/low-coherence trials, so gaps do not concatenate trial history.
    full = pd.DataFrame({'mouse': x['subject_id'], 'session': x['idx_session']})
    full['block'] = full.groupby(['mouse', 'session']).cumcount() // 50
    obs['block'] = full.block.to_numpy()[obs.row.to_numpy()]
    onsets = pseudo_onsets(obs)
    rng = np.random.default_rng(187)
    weights = []
    for _ in range(n_boot):
        w = np.zeros(len(obs))
        for _, sg in obs.groupby(['mouse', 'session']):
            blocks = list(sg.groupby('block').groups.values())
            for b in rng.integers(0, len(blocks), len(blocks)):
                w[np.asarray(blocks[b])] += 1
        weights.append(w)
    checks = {}
    for name, window in [('profile', False), ('window', True)]:
        est = Contrast(obs, onsets, window)
        result = est.table(np.ones(len(obs)))
        boot = np.array([est(w) for w in weights])
        result['lo_pp'], result['hi_pp'] = np.nanpercentile(boot, [2.5, 97.5], axis=0)
        result['se_pp'] = np.nanstd(boot, axis=0, ddof=1)
        result['n_boot'] = n_boot
        result['interval'] = 'Pointwise 95% within-session 50-trial block bootstrap; exploratory'
        result.to_csv(OUT / f'data_pulse_{name}.csv', index=False)
        if window:
            est.cell_table().to_csv(OUT / 'data_pulse_coherence_cells.csv', index=False)
        # Independent comparison to the pre-existing estimator, sign pooled.
        pooled = result[result.sign == 0]
        if window:
            ref = stats_of(obs, onsets)[0].stack().rename('ref').reset_index()
            ref.columns = ['mouse', 'window', 'ref']
            test = pooled.merge(ref, on=['mouse', 'window'])
        else:
            ref = effect(with_bins(obs, onsets).dropna(subset='bin'), ['mouse', 'bin'])
            test = pooled.merge(ref.rename(columns={'effect': 'ref'}), on=['mouse', 'bin'])
        checks[f'{name}_max_error_pp'] = float(np.max(np.abs(test.effect_pp - test.ref)))
        assert checks[f'{name}_max_error_pp'] < 1e-8
    obs.to_pickle(OUT / 'cache/data_pulse_observed.pkl')
    pd.to_pickle(onsets, OUT / 'cache/data_pulse_onsets.pkl')
    write_json(OUT / 'pulse_estimator_checks.json', checks | {'n_boot': n_boot, 'seed': 187,
        'sampling_unit': '50-trial blocks within mouse/session; pointwise within-mouse inference only'})
    print('Pulse estimator checks:', checks, flush=True)


def collect(reps, seeds):
    score_rows, profile_rows, window_rows, coherence_rows, condition_rows = [], [], [], [], []
    x = inputs()
    obs = pd.read_pickle(OUT / 'cache/data_pulse_observed.pkl')
    onsets = pd.read_pickle(OUT / 'cache/data_pulse_onsets.pkl')
    for mouse in MICE:
        for family in FAMILIES:
            for seed in seeds:
                parts = []
                for fold in range(5):
                    path = OUT / 'cache' / f'score_{family}_{mouse}_cv{fold}_r{reps}_s{seed}.pkl'
                    r = pd.read_pickle(path)
                    assert r['fingerprint']['fit_sha256'] == sha(source_path(mouse, family, f'cv{fold}'))
                    score_rows.append({k: v for k, v in r.items() if k not in ['fingerprint', 'outcomes']})
                    parts.append(r['outcomes'])
                out = pd.concat(parts, ignore_index=True)
                # Each empirical input schedule appears exactly once per rep
                # across held-out folds; every outcome has an out-of-fold fit.
                assert out.groupby('rep').row.nunique().eq(sum(r0.shape[0] // reps for r0 in parts)).all()
                o = out[out.choice >= 0].copy()
                o['coherence_pct'] = np.round(x['signed_coherence'][o.row.to_numpy()] * 100).astype(int)
                o['scheduled_pulse'] = x['sched_pulse_type'][o.row.to_numpy()]
                for (coh, pulse), g in o.groupby(['coherence_pct', 'scheduled_pulse']):
                    condition_rows.append({'mouse': mouse, 'family': family, 'seed': seed,
                        'coherence_pct': coh, 'scheduled_pulse': int(pulse), 'n': len(g),
                        'p_right': g.choice.mean(), 'rt_mean_s': g.rt.mean(), 'rt_median_s': g.rt.median()})
                del o
                keep = obs[obs.mouse == mouse].set_index('row', drop=False)
                out = out[(out.choice >= 0) & out.row.isin(keep.index)]
                m = keep.loc[out.row]
                t = pd.DataFrame({k: m[k].to_numpy() for k in ['row', 'mouse', 'rig', 'coh', 's', 'stage', 'onset']})
                t['choice'] = np.where(out.choice.to_numpy() == 1, 1, -1)
                t['rt'] = out.rt.to_numpy()
                # Each simulated schedule x repetition is an individual trial.
                # Original input rows repeat; give expanded outcomes unique IDs
                # before Contrast builds its original-trial weight mapping.
                t['row'] = np.arange(len(t))
                for window, target in [(False, profile_rows), (True, window_rows)]:
                    est = Contrast(t, onsets, window)
                    # Uniform weights give the pooled point prediction; no
                    # bootstrap weights are used for simulated outcomes.
                    result = est.table(np.ones(len(t)))
                    result = result.assign(mouse=mouse, family=family, seed=seed, reps=reps)
                    target.extend(result.to_dict('records'))
                    if window:
                        coherence_rows.extend(est.cell_table().assign(family=family, seed=seed).to_dict('records'))
    scores = pd.DataFrame(score_rows)
    assert len(scores) == len(MICE) * len(FAMILIES) * 5 * len(seeds)
    scores.to_csv(OUT / 'heldout_fold_scores.csv', index=False)
    totals = scores.groupby(['mouse', 'family', 'seed'], as_index=False)[['n', 'nll', 'choice_nll', 'rt_nll']].sum()
    totals.to_csv(OUT / 'heldout_scores_by_seed.csv', index=False)
    reference = totals[totals.family == 'drift'].drop(columns='family')
    diffs = totals.merge(reference, on=['mouse', 'seed'], suffixes=('', '_drift'))
    for key in ['nll', 'choice_nll', 'rt_nll']:
        diffs[f'delta_{key}'] = diffs[key] - diffs[f'{key}_drift']
    diffs.to_csv(OUT / 'heldout_differences_from_drift.csv', index=False)
    summary = diffs.groupby(['mouse', 'family'])[['delta_nll', 'delta_choice_nll', 'delta_rt_nll']].agg(['mean', 'std', 'min', 'max'])
    summary.columns = ['_'.join(c) for c in summary.columns]
    summary.reset_index().to_csv(OUT / 'heldout_difference_summary.csv', index=False)
    pd.DataFrame(profile_rows).to_csv(OUT / 'model_pulse_profile.csv', index=False)
    pd.DataFrame(window_rows).to_csv(OUT / 'model_pulse_window.csv', index=False)
    pd.DataFrame(coherence_rows).to_csv(OUT / 'model_pulse_coherence_cells.csv', index=False)
    pd.DataFrame(condition_rows).to_csv(OUT / 'model_condition_predictions.csv', index=False)
    print(summary.round(3).to_string(), flush=True)


def plot(reps, seeds):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    plt.rcParams.update({'pdf.fonttype': 42, 'ps.fonttype': 42, 'font.size': 9,
                         'axes.spines.top': False, 'axes.spines.right': False,
                         'savefig.facecolor': 'white'})
    data = pd.read_csv(OUT / 'data_pulse_profile.csv')
    pred = pd.read_csv(OUT / 'model_pulse_profile.csv')
    scores = pd.read_csv(OUT / 'heldout_differences_from_drift.csv')
    x = inputs()
    fig, axes = plt.subplots(2, 4, figsize=(16, 7.3), constrained_layout=True)
    for row, mouse in enumerate(MICE):
        ax = axes[row, 0]
        s = scores[(scores.mouse == mouse) & (scores.family != 'drift')]
        for j, family in enumerate(['fixed', 'delay']):
            z = s[s.family == family]
            for shift, key, label in [(-.13, 'delta_choice_nll', 'Choice'), (.13, 'delta_rt_nll', 'RT')]:
                ax.bar(j + shift, z[key].mean(), width=.25, color=COLORS[family], alpha=.55 if shift < 0 else 1)
                ax.plot(np.full(len(z), j + shift), z[key], '.', color='#333333', ms=3)
        ax.axhline(0, color='black', lw=.6)
        ax.set(xticks=[0, 1], xticklabels=['Fixed delay', 'Variable delay'], ylabel='Held-out NLL difference vs drift model',
               title=f'{mouse}: choice (pale) and RT (dark)')
        ax = axes[row, 1]
        schedules = np.flatnonzero((x['subject_id'] == mouse) & (x['sched_pulse_type'] == 0)
                                  & (np.round(x['signed_coherence'] * 100) == -100))
        rows = schedules[x['choice'][schedules] == 0]
        bins = np.linspace(.3, 5, 48)
        d = np.histogram(x['rt'][rows], bins)[0] / len(rows) / np.diff(bins)
        ax.stairs(d, bins, color='black', lw=1.7, label='Observed')
        for family in FAMILIES:
            vals = []
            for seed in seeds:
                for fold in range(5):
                    r = pd.read_pickle(OUT / 'cache' / f'score_{family}_{mouse}_cv{fold}_r{reps}_s{seed}.pkl')
                    o = r['outcomes']
                    # Condition on each dataset's own correct responses. Do not
                    # select simulated schedules by the animal's observed choice.
                    keep = np.isin(o.row, schedules) & (o.choice.to_numpy() == 0)
                    vals.extend(o.loc[keep, 'rt'].to_numpy())
            h = np.histogram(vals, bins)[0] / len(vals) / np.diff(bins)
            ax.stairs(h, bins, color=COLORS[family], linestyle=LINES[family], lw=1.3, label=LABELS[family])
        ax.set(xlim=(.3, 5.), xlabel='Response time (s)', ylabel='Density', title='Correct −100% control responses')
        if row == 0:
            ax.legend(frameon=False, fontsize=7)
        for col, sign in [(2, 1), (3, -1)]:
            ax = axes[row, col]
            d = data[(data.mouse == mouse) & (data.sign == sign)]
            mid = (np.array(BINS[:-1]) + BINS[1:]) / 2
            idx = d.bin.to_numpy(dtype=int)
            ax.errorbar(mid[idx], d.effect_pp, yerr=[d.effect_pp-d.lo_pp, d.hi_pp-d.effect_pp], fmt='o',
                        color='black', ms=3.5, lw=.8, capsize=2, label='Observed, pointwise block CI')
            for family in FAMILIES:
                p = pred[(pred.mouse == mouse) & (pred.sign == sign) & (pred.family == family)]
                g = p.groupby('bin').effect_pp.agg(['mean', 'min', 'max'])
                idx = g.index.to_numpy(dtype=int)
                ax.plot(mid[idx], g['mean'], linestyle=LINES[family], marker=MARKERS[family],
                        color=COLORS[family], ms=2.5, lw=1.2)
                ax.fill_between(mid[idx], g['min'], g['max'], color=COLORS[family], alpha=.12)
            ax.axhline(0, color='black', lw=.6)
            ax.axvspan(.3, 1.2, color='#777777', alpha=.06)
            ax.set(xlabel='Time after pulse onset (s)', ylabel='Choice shift toward pulse (pp)',
                   title='Positive pulse' if sign == 1 else 'Negative pulse')
    pulse_lo, pulse_hi = min(-2., data.lo_pp.min()), max(2., data.hi_pp.max())
    for ax in axes[:, 2:].ravel():
        ax.set_ylim(pulse_lo-2., pulse_hi+2.)
        ax.set_xlim(.25, 5.)
    fig.suptitle('Variable postdecision delay: exploratory out-of-fold prediction checks\n'
                 'Points in score panels and shading on predictions show simulation-seed variation', fontsize=12)
    fig.savefig(OUT / 'response_delay_pilot.pdf')
    fig.savefig(OUT / 'response_delay_pilot.png', dpi=160)
    plt.close(fig)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--prepare', action='store_true')
    parser.add_argument('--collect', action='store_true')
    parser.add_argument('--plot', action='store_true')
    parser.add_argument('--n-boot', type=int, default=500)
    parser.add_argument('--eval-reps', type=int, default=60)
    parser.add_argument('--eval-seeds', nargs='+', type=int, default=[12345, 23456, 34567])
    args = parser.parse_args()
    (OUT / 'cache').mkdir(parents=True, exist_ok=True)
    if args.prepare:
        prepare(args.n_boot)
    if args.collect:
        collect(args.eval_reps, args.eval_seeds)
    if args.plot:
        plot(args.eval_reps, args.eval_seeds)


if __name__ == '__main__':
    main()
