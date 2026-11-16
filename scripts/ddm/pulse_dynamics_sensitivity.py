"""Additional existing pulse-weight finalists and mouse-bootstrap readout uncertainty.

These are exploratory extensions of the same estimator, with no new model fits.
"""
import argparse
import json
import time

import numpy as np
import pandas as pd

from scripts.ddm import pulse_dynamics_bridge as bridge

EXTRA = ['pw_per_time', 'pw_per_time_no_sv']


def bootstrap(n_boot):
    counts = pd.read_pickle(bridge.OUT / 'cache/data_counts.pkl')
    groups = {m: g.drop(columns='rep').copy() for m, g in counts.groupby('mouse')}
    mice = list(groups)
    rng = np.random.default_rng(20261113)
    rows, failures = [], []
    started = time.monotonic()
    for rep in range(n_boot):
        draw = rng.choice(mice, len(mice))
        b = pd.concat([groups[m].assign(mouse=f'{m}_{i}') for i, m in enumerate(draw)], ignore_index=True)
        for scope, u in [('all_coherences', b), ('coherence_le36', b[b.coherence_pct.abs() <= 36])]:
            try:
                r = bridge.readout(u, full=False).assign(scope=scope, rep=rep)
                assert len(r) == 7
                rows.append(r)
            except Exception as exc:
                failures.append({'rep': rep, 'scope': scope, 'error': repr(exc)})
        if (rep + 1) % 100 == 0:
            print(f'BOOTSTRAP {rep + 1}/{n_boot}, seconds={time.monotonic() - started:.1f}', flush=True)
    curves = pd.concat(rows, ignore_index=True)
    curves.to_csv(bridge.OUT / 'data_bootstrap_readouts.csv', index=False)
    pd.DataFrame(failures, columns=['rep', 'scope', 'error']).to_csv(bridge.OUT / 'data_bootstrap_failures.csv', index=False)
    summaries = []
    for (rep, scope), g in curves.groupby(['rep', 'scope']):
        K = g.K.iloc[0]
        late = g.loc[g.lo_s >= 1.2, 'gammaT'].mean()
        summaries.append({'rep': rep, 'scope': scope, 'K': K, 'late_gammaT_mean': late,
                          'late_minus_early': late - K, 'late_over_early': late / K,
                          'positive_slopes_used': bool(g.loc[g.lo_s >= .3, 'positive_slope'].all())})
    s = pd.DataFrame(summaries)
    s.to_csv(bridge.OUT / 'data_bootstrap_summary.csv', index=False)
    intervals = []
    for scope, g in s.groupby('scope'):
        r = {'scope': scope, 'n_boot_ok': len(g), 'n_boot_requested': n_boot,
             'nonpositive_K': int((g.K <= 0).sum()), 'nonpositive_slopes_used': int((~g.positive_slopes_used).sum())}
        for col in ['K', 'late_gammaT_mean', 'late_minus_early', 'late_over_early']:
            r[col + '_lo'], r[col + '_hi'] = np.percentile(g[col], [2.5, 97.5])
        intervals.append(r)
    pd.DataFrame(intervals).to_csv(bridge.OUT / 'data_bootstrap_intervals.csv', index=False)
    print(pd.DataFrame(intervals).round(4).to_string(index=False), flush=True)


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--simulate-extra', action='store_true')
    p.add_argument('--analyze-extra', action='store_true')
    p.add_argument('--bootstrap', type=int, default=0)
    p.add_argument('--seed', type=int, default=0)
    a = p.parse_args()
    if a.simulate_extra:
        bridge.simulate(EXTRA, None, a.seed, 30)
    if a.analyze_extra:
        bridge.analyze(bridge.FAMILIES + EXTRA, [0, 1], 30, True)
    if a.bootstrap:
        bootstrap(a.bootstrap)


if __name__ == '__main__':
    main()
