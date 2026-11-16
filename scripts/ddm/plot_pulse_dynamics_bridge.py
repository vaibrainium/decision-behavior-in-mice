"""Plot the fixed-parameter pulse-dynamics comparison and write source summaries."""
from pathlib import Path
import json
import pickle

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

from scripts.ddm.pulse_dynamics_bridge import OUT, ROOT, FAMILIES, LABELS
FAMILIES = [*FAMILIES, 'pw_per_time', 'pw_per_time_no_sv']

COLORS = {'primary': '#4878a8', 'no_sv': '#4a9568', 'power_leak_urgency': '#c25850',
          'pulse_norm_ugm_no_sv': '#9866ab', 'control_primary': '#b08b42',
          'norm_leak': '#b96b35', 'pulse_linear_leak': '#6f657e', 'primary_sv0': '#758b84'}
COLORS.update(pw_per_time='#b1608b', pw_per_time_no_sv='#5296a5')
SHORT = {'control_primary': 'Control-trained integrator', 'primary': 'Joint integrator, sv',
         'no_sv': 'Joint integrator, no sv', 'power_leak_urgency': 'Power + leak + urgency',
         'norm_leak': 'Normalized + leak', 'pulse_linear_leak': 'Pulse-only leak',
         'pulse_norm_ugm_no_sv': 'Pulse-only normalized UGM, no sv', 'primary_sv0': 'Joint integrator, sv = 0 ablation'}
SHORT.update(pw_per_time='Onset-specific pulse weights, sv', pw_per_time_no_sv='Onset-specific pulse weights, no sv')


def main():
    d = pd.read_csv(OUT / 'all_readouts.csv')
    summary = pd.read_csv(OUT / 'readout_summary.csv')
    means = d.groupby(['family', 'scope', 'bin'], sort=False).mean(numeric_only=True).reset_index()
    rows = []
    for (family, scope), g in summary.groupby(['family', 'scope'], sort=False):
        row = {'family': family, 'scope': scope}
        for col in ['K', 'late_gammaT_mean', 'late_over_early', 'late_minus_early']:
            row[col] = g[col].mean()
            row[col + '_seed_min'] = g[col].min()
            row[col + '_seed_max'] = g[col].max()
        rows.append(row)
    s = pd.DataFrame(rows)
    s.to_csv(OUT / 'summary_across_seeds.csv', index=False)
    r = pd.read_csv(OUT / 'all_replicate_readouts.csv')
    rep_summaries = []
    for (family, seed, scope, rep), g in r.groupby(['family', 'seed', 'scope', 'rep']):
        good = not g.failed.fillna(True).astype(bool).any() and g.gammaT.notna().sum() == 7
        if not good:
            rep_summaries.append({'family': family, 'seed': seed, 'scope': scope, 'rep': rep, 'valid': False})
            continue
        K = g.K.iloc[0]
        late = g[g.lo_s >= 1.2].gammaT.mean()
        rep_summaries.append({'family': family, 'seed': seed, 'scope': scope, 'rep': rep, 'valid': True,
                              'K': K, 'late_gammaT_mean': late, 'late_over_early': late / K,
                              'late_minus_early': late - K, 'all_slopes_positive': bool(g.loc[g.lo_s >= .3, 'positive_slope'].all())})
    reps = pd.DataFrame(rep_summaries)
    reps.to_csv(OUT / 'replicate_summary.csv', index=False)
    predictive = []
    for (family, scope), g in reps.groupby(['family', 'scope']):
        good = g[g.valid]
        row = {'family': family, 'scope': scope, 'n_reps': len(g), 'n_readout_valid': len(good),
               'n_nonpositive_early_K': int((good.K <= 0).sum()),
               'n_nonpositive_slopes': int((~good.all_slopes_positive.astype(bool)).sum())}
        for col in ['K', 'late_gammaT_mean', 'late_over_early', 'late_minus_early']:
            row[col + '_rep_lo'], row[col + '_rep_hi'] = np.percentile(good[col], [2.5, 97.5])
        predictive.append(row)
    pred = pd.DataFrame(predictive)
    pred.to_csv(OUT / 'conditional_prediction_intervals.csv', index=False)

    old_d = pd.read_csv(ROOT / 'dissemination/paper_accumulation/tables/pulse_dilution_2026-10-30.csv')
    old_dir = pd.read_csv(ROOT / 'dissemination/paper_accumulation/tables/pulse_decomposition_2026-10-30_bins.csv')
    select = ['no_sv', 'power_leak_urgency', 'pulse_norm_ugm_no_sv', 'pw_per_time_no_sv']
    fig, axes = plt.subplots(2, 2, figsize=(14.8, 10), constrained_layout=True)
    centers = (old_d.lo_s + old_d.hi_s) / 2
    for ax, col, low, high, title, ylabel in [
            (axes[0, 0], 'D_joint', old_dir.D_boot_lo, old_dir.D_boot_hi,
             'A  Directional pulse influence', 'Directional coefficient (log-odds)'),
            (axes[0, 1], 'gammaT', old_d.gammaT_lo, old_d.gammaT_hi,
             'B  Pulse influence after the dilution adjustment', 'Coherence-equivalent influence × RT (% coh × s)')]:
        observed = means[(means.family == 'data') & (means.scope == 'all_coherences')].sort_values('bin')
        mask = observed.lo_s >= (.3 if col == 'gammaT' else .1)
        observed = observed[mask]
        lo, hi = np.asarray(low)[mask], np.asarray(high)[mask]
        values = observed[col].to_numpy()
        ax.errorbar(np.asarray(centers)[mask], values, yerr=[values - lo, hi - values], fmt='o-', color='black',
                    lw=2.5, capsize=3, label='Data, 95% mouse-bootstrap interval', zorder=5)
        for family in select:
            for j, (seed, g) in enumerate(d[(d.family == family) & (d.scope == 'all_coherences')].groupby('seed')):
                g = g[g.lo_s >= (.3 if col == 'gammaT' else .1)]
                ax.plot((g.lo_s + g.hi_s) / 2, g[col], color=COLORS[family], lw=1.8,
                        ls='-' if j == 0 else '--', alpha=.95 if j == 0 else .6,
                        label=SHORT[family] if j == 0 else None)
        ax.axhline(0, color='.65', lw=.8)
        ax.axvline(1.2, color='.65', lw=.8, ls=':')
        ax.set(title=title, xlabel='Time from pulse to response (s)', ylabel=ylabel)
        ax.set_xticks([.2, .75, 1.2, 1.8, 3.55], ['.1–.3', '.6–.9', '1.2', '1.5–2.1', '2.1–5'])
        if col == 'gammaT':
            ax.set_xticks([.45, .75, 1.05, 1.35, 1.8, 3.55], ['.3–.6', '.6–.9', '.9–1.2', '1.2–1.5', '1.5–2.1', '2.1–5'])
    axes[0, 0].legend(fontsize=8, loc='best')

    full = s[s.scope == 'all_coherences'].set_index('family')
    low = s[s.scope == 'coherence_le36'].set_index('family')
    order = ['data', *FAMILIES]
    y = np.arange(len(order))[::-1]
    a = axes[1, 0]
    a.scatter(full.loc[order, 'K'], y + .12, c=['black'] + [COLORS[f] for f in FAMILIES], marker='o', s=45, label='Early mean, .3–1.2 s')
    a.scatter(full.loc[order, 'late_gammaT_mean'], y - .12, c=['black'] + [COLORS[f] for f in FAMILIES], marker='s', s=35, label='Late mean, 1.2–5 s')
    a.axvline(0, color='.65', lw=.8)
    a.set(yticks=y, yticklabels=['Observed data'] + [SHORT[f] for f in FAMILIES],
          xlabel='Coherence-equivalent influence × RT (% coh × s)', title='C  Early and late influence in every finalist')
    if (OUT / 'data_bootstrap_intervals.csv').exists():
        ci = pd.read_csv(OUT / 'data_bootstrap_intervals.csv').set_index('scope').loc['all_coherences']
        for col, offset in [('K', .12), ('late_gammaT_mean', -.12)]:
            estimate = full.loc['data', col]
            a.errorbar(estimate, y[0] + offset,
                       xerr=[[estimate - ci[col + '_lo']], [ci[col + '_hi'] - estimate]], color='black', capsize=3, fmt='none')
    a.legend(fontsize=8)

    a = axes[1, 1]
    for scope, marker, offset, label in [('all_coherences', 'o', .1, 'Historical all-coherence analysis'),
                                         ('coherence_le36', 's', -.1, 'Sensitivity: |coherence| ≤ 36%')]:
        z = s[s.scope == scope].set_index('family').loc[order]
        a.scatter(z.late_over_early, y + offset, marker=marker, facecolors='none' if marker == 's' else ['black'] + [COLORS[f] for f in FAMILIES],
                  edgecolors=['black'] + [COLORS[f] for f in FAMILIES], s=40, label=label)
        a.hlines(y + offset, z.late_over_early_seed_min, z.late_over_early_seed_max,
                 color=['black'] + [COLORS[f] for f in FAMILIES], lw=2)
    a.axvline(0, color='.65', lw=.8)
    a.axvline(1, color='.55', lw=.8, ls=':')
    a.set(yticks=y, yticklabels=[], xlabel='Late influence / early influence',
          title='D  A decline can occur without evidence leakage')
    a.legend(fontsize=8, loc='lower left')
    for a in axes.flat:
        a.spines[['top', 'right']].set_visible(False)
    fig.suptitle('Pulse dynamics from existing fits and matched behavioral readouts\n'
                 'Model parameters fixed; solid/dashed curves show two simulation seeds. sv = drift variability.', fontsize=13)
    fig.savefig(OUT / 'pulse_dynamics_comparison.pdf')
    fig.savefig(OUT / 'pulse_dynamics_comparison.png', dpi=190)
    evidence = {'definition': 'Early: unweighted mean gamma×T over .3–1.2 s bins; late: unweighted mean over 1.2–5 s bins.',
                'model_intervals': 'Conditional prediction intervals from 60 simulated datasets, fixed parameters; no parameter uncertainty.',
                'replicate_readout_failures': int((~reps.valid).sum()),
                'point_estimates': s.to_dict('records')}
    (OUT / 'figure_evidence.json').write_text(json.dumps(evidence, indent=2) + '\n')
    print(s[['family', 'scope', 'K', 'late_gammaT_mean', 'late_over_early']].round(3).to_string(index=False))
    print('\nReadout failures:',int((~reps.valid).sum()))


if __name__ == '__main__':
    main()
