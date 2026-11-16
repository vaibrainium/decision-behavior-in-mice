"""Summarize the exact held-out likelihood decomposition and draw its diagnostic."""
import json
from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

from scripts.ddm.diagnose_pulse_rt_tradeoff import OUT

PAIR = 'pw_per_time_no_sv_minus_pw_per_time'


def main():
    cells = pd.read_csv(OUT / 'cell_differences_seed12345.csv')
    bins = pd.read_csv(OUT / 'rt_bin_differences_seed12345.csv')
    folds = pd.read_csv(OUT / 'fold_scores_seed12345.csv')
    assert len(folds) == 150 and folds.difference_from_stored.abs().max() < 1e-7
    for pair in cells.pair.unique():
        assert np.isclose(cells.loc[cells.pair == pair, 'delta_rt_nll'].sum(), bins.loc[bins.pair == pair, 'delta_rt_nll'].sum())
    c, b = cells[cells.pair == PAIR].copy(), bins[bins.pair == PAIR].copy()
    mouse = c.groupby('mouse')[['delta_choice_nll', 'delta_rt_nll', 'delta_total', 'n']].sum()
    trial = c.groupby('trial_type')[['delta_choice_nll', 'delta_rt_nll', 'delta_total']].sum()
    correctness = b.groupby('correctness').delta_rt_nll.sum()
    q = b.groupby('quantile_bin').delta_rt_nll.sum()
    coherence = c.assign(abs_coherence=c.coherence.abs()).groupby('abs_coherence').delta_rt_nll.sum()
    thirds = b.assign(third=b.quantile_bin // 3).groupby('third').delta_rt_nll.sum()
    top = b.groupby(['mouse', 'coherence', 'scheduled_pulse', 'correctness']).delta_rt_nll.sum().sort_values(ascending=False)
    top.rename('delta_rt_nll').reset_index().to_csv(OUT / 'largest_matched_rt_contributions.csv', index=False)
    seed_checks = []
    for seed in [12345, 23456]:
        z = pd.read_csv(OUT / f'cell_differences_seed{seed}.csv')
        z = z[(z.pair == PAIR) & z.mouse.isin(['PSUIM6', 'PSUIM7'])]
        for m, v in z.groupby('mouse'):
            seed_checks.append({'seed': seed, 'mouse': m, 'choice': v.delta_choice_nll.sum(),
                                'rt': v.delta_rt_nll.sum(), 'total': v.delta_total.sum()})
    pd.DataFrame(seed_checks).to_csv(OUT / 'dominant_mouse_seed_check.csv', index=False)
    record = {'original_scores_reproduced_max_error': folds.difference_from_stored.abs().max(),
              'matched_pair_definition': PAIR, 'matched_choice_delta': c.delta_choice_nll.sum(),
              'matched_rt_delta': c.delta_rt_nll.sum(), 'matched_total_delta': c.delta_total.sum(),
              'matched_total_without_PSUIM7': mouse.drop('PSUIM7').delta_total.sum(),
              'matched_total_without_PSUIM6_and_7': mouse.drop(['PSUIM6', 'PSUIM7']).delta_total.sum(),
              'PSUIM7_share_of_matched_total': mouse.loc['PSUIM7', 'delta_total'] / mouse.delta_total.sum(),
              'by_trial_type': trial.reset_index().to_dict('records'), 'rt_by_correctness': correctness.to_dict(),
              'rt_by_abs_coherence': coherence.to_dict(), 'rt_by_quantile_third': thirds.to_dict(),
              'seed_checks': seed_checks}
    (OUT / 'diagnostic_summary.json').write_text(json.dumps(record, indent=2) + '\n')

    fig, axes = plt.subplots(2, 2, figsize=(13.4, 9.5), constrained_layout=True)
    a = axes[0, 0]
    y = np.arange(len(mouse))
    a.barh(y + .17, mouse.delta_choice_nll, height=.32, color='#4878a8', label='Choice')
    a.barh(y - .17, mouse.delta_rt_nll, height=.32, color='#c47f35', label='RT')
    a.scatter(mouse.delta_total, y, color='black', s=18, label='Total', zorder=4)
    a.set(yticks=y, yticklabels=mouse.index, xlabel='NLL difference: no sv minus sv', title='A  The matched-model difference is concentrated')
    a.axvline(0, c='.6', lw=.8)
    a.legend(fontsize=8)
    a = axes[0, 1]
    a.bar(q.index + 1, q.values, color=np.where(q.values >= 0, '#c47f35', '#4878a8'))
    a.axhline(0, c='.6', lw=.8)
    a.set(xticks=np.arange(1, 10), xlabel='RT quantile bin within condition and choice (fast → slow)',
          ylabel='RT NLL difference: no sv minus sv', title='B  The no-sv model loses in central RT bins')
    a = axes[1, 0]
    x = np.arange(len(coherence))
    a.bar(x, coherence.values, color='#c47f35')
    a.set(xticks=x, xticklabels=coherence.index.astype(int), xlabel='Absolute baseline coherence (%)',
          ylabel='RT NLL difference: no sv minus sv', title='C  Strong-evidence responses carry much of the loss')
    a.axhline(0, c='.6', lw=.8)
    a = axes[1, 1]
    hist = pd.read_csv(OUT / 'rt_histograms_seed12345.csv')
    u = hist[(hist.mouse == 'PSUIM7') & (hist.coherence == -100) & (hist.scheduled_pulse == 0) & (hist.correctness == 'correct')]
    colors = {'pw_per_time': '#4878a8', 'pw_per_time_no_sv': '#4a9568', 'power_leak_urgency': '#c25850'}
    labels = {'pw_per_time': 'Onset weights, sv', 'pw_per_time_no_sv': 'Onset weights, no sv', 'power_leak_urgency': 'Power + leak + urgency'}
    for family, g in u.groupby('family'):
        v = g.groupby('lo_s')[['data_n', 'model_n']].sum()
        centers = v.index.to_numpy() + .05
        a.plot(centers, v.model_n / v.model_n.sum() / .1, color=colors[family], lw=1.7, label=labels[family])
    v = u[u.family == 'pw_per_time'].groupby('lo_s').data_n.sum()
    a.plot(v.index.to_numpy() + .05, v / v.sum() / .1, 'o-', color='black', lw=1, ms=3, label='Observed correct RTs')
    a.set(xlim=(.3, 2.6), xlabel='RT (s)', ylabel='Conditional density (/s)',
          title='D  Illustrative largest loss cell: PSUIM7, −100%, control')
    a.legend(fontsize=8)
    for a in axes.flat:
        a.spines[['top', 'right']].set_visible(False)
    fig.suptitle('Where the held-out response-time advantage comes from\nMatched onset-weight models differ by drift variability; positive differences favor sv', fontsize=13)
    fig.savefig(OUT / 'rt_tradeoff_diagnostic.pdf')
    fig.savefig(OUT / 'rt_tradeoff_diagnostic.png', dpi=180)
    print(json.dumps(record, indent=2))


if __name__ == '__main__':
    main()
