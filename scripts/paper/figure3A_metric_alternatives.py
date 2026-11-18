"""Panel A alternatives from approved NLL, joint test bits and absolute BIC."""
import argparse
import hashlib
import json
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator
import numpy as np
import pandas as pd
from scripts.paper.style import RC

MODELS = ['C', 'E', 'ES', 'DDMx', 'ESx']
BLUE = '#0072B2'
ORANGE = '#C45B00'


def axis_style(ax, values, ylabel, color='.2'):
    ax.set(xticks=range(5), xticklabels=MODELS, xlabel='Model', ylabel=ylabel, xlim=(-.45, 4.45))
    ax.yaxis.set_major_locator(MaxNLocator(nbins=4))
    ax.ticklabel_format(axis='y', style='plain', useOffset=False)
    ax.margins(y=.25)
    ax.yaxis.label.set_color(color)
    ax.tick_params(axis='y', colors=color)


def save(fig, output, name):
    for ext in ['png', 'pdf', 'svg']:
        fig.savefig(output/f'{name}.{ext}', dpi=300, facecolor='white')
    plt.close(fig)


def main():
    p = argparse.ArgumentParser(__doc__)
    p.add_argument('--draft', type=Path, required=True)
    p.add_argument('--output', type=Path, required=True)
    p.add_argument('--likelihood', choices=['nll', 'll'], default='nll')
    a = p.parse_args()
    a.output.mkdir(parents=True, exist_ok=False)
    paths = {
        'nll': a.draft/'figure3A_group_nll_connected_2026-11-17/group_nll.csv',
        'bits': a.draft/'figure3_information_metrics_2026-11-17/group_metrics.csv',
        'bic': a.draft/'figure3_absolute_bic_2026-11-17/group_absolute_bic.csv',
    }
    nll = pd.read_csv(paths['nll']).set_index('model').loc[MODELS]
    assert nll['count'].eq(10).all()
    metrics = pd.read_csv(paths['bits']).set_index('model').loc[MODELS]
    bic = pd.read_csv(paths['bic']).set_index('model').loc[MODELS]
    data = pd.DataFrame({'mean_test_nll': nll['mean'],
                         'mean_joint_test_bits_per_trial': metrics.joint_test_logscore_bits_per_trial,
                         'mean_bic_qmle': bic.mean_bic_qmle})
    assert np.isfinite(data.to_numpy()).all()
    np.testing.assert_allclose(data.mean_bic_qmle-data.loc['C', 'mean_bic_qmle'], metrics.delta_bic_vs_C, atol=1e-9)
    data['mean_test_ll'] = -data.mean_test_nll
    np.testing.assert_array_equal(data.mean_test_ll, -nll['mean'])
    data.to_csv(a.output/'source_panel_A.csv')
    likelihood = data.mean_test_ll if a.likelihood == 'll' else data.mean_test_nll
    ll_label = 'LL' if a.likelihood == 'll' else 'NLL'
    with plt.rc_context({**RC, 'font.family': 'DejaVu Sans'}):
        fig, ax = plt.subplots(figsize=(110/25.4, 88/25.4))
        fig.subplots_adjust(left=.20, right=.80, bottom=.17, top=.74)
        right = ax.twinx()
        ax.plot(range(5), likelihood, 'o-', color=BLUE, lw=1, ms=5, label='Test '+ll_label)
        right.plot(range(5), data.mean_bic_qmle, 's--', color=ORANGE, lw=1, ms=4.5, label='Training BIC')
        axis_style(ax, likelihood, 'Mean test '+ll_label, BLUE)
        axis_style(right, data.mean_bic_qmle, 'Mean BIC (QMLE-based)', ORANGE)
        right.spines['right'].set_visible(True)
        ax.spines['left'].set_color(BLUE)
        right.spines['right'].set_color(ORANGE)
        fig.text(.035, .97, 'A', fontsize=12, fontweight='bold', va='top')
        fig.text(.20, .97, 'Log likelihood and BIC', fontsize=9, va='top')
        fig.text(.20, .87, ('10 mice; LL higher, BIC lower is better' if a.likelihood == 'll' else 'Mean across 10 mice; lower is better'), fontsize=6.6, color='.3')
        fig.legend(handles=ax.lines+right.lines, loc='upper center', bbox_to_anchor=(.5,.835),
                   ncol=2, frameon=False, fontsize=6.6, handlelength=2.2)
        save(fig, a.output, 'A1_'+a.likelihood+'_bic_dual_axis')
        fig, axes = plt.subplots(1, 2, figsize=(180/25.4, 85/25.4))
        fig.subplots_adjust(left=.12, right=.98, bottom=.18, top=.76, wspace=.55)
        specs = [(data.mean_joint_test_bits_per_trial, 'Joint test log score (bits/trial)',
                  'Test prediction; higher is better', '.2', 'o'),
                 (data.mean_bic_qmle, 'Mean BIC (QMLE-based)',
                  'Training fit; lower is better', '.2', 'o')]
        for ax, (y, ylabel, title, color, marker) in zip(axes, specs):
            ax.plot(range(5), y, marker+'-', color=color, lw=1, ms=5.5)
            axis_style(ax, y, ylabel)
            pad = np.ptp(y)*.06
            for j, value in enumerate(y):
                text = f'{value:.3f}' if 'bits' in ylabel else f'{value:.1f}'
                ax.text(j, value+pad, text, ha='center', fontsize=6.2)
            ax.set_title(title, fontsize=7, pad=14)
        fig.text(.035, .97, 'A', fontsize=12, fontweight='bold', va='top')
        fig.text(.12, .97, 'Test bits/trial and BIC', fontsize=9, va='top')
        fig.text(.12, .88, 'Mean across 10 mice', fontsize=6.6, color='.3')
        save(fig, a.output, 'A2_bits_bic_side_by_side')
    (a.output/'captions.md').write_text(
        '# Panel A alternatives\n\n'
        '1. Dual axes: blue circles/solid line show equal-mouse mean total five-fold held-out ' + ll_label +
        (' (left, higher better; LL = −NLL); orange' if a.likelihood == 'll' else ' (left, lower better); orange') + ' squares/dashed line show mean full-training QMLE-based BIC '
        '(right, lower better). Both include the same 10 mice. The axes have independently labeled '
        'nonzero ranges and different units; curve intersections/vertical alignment have no meaning. '
        'These are distinct test and training scores, not BIC calculated from the plotted test NLL.\n\n'
        '2. Separate subpanels: left shows equal-mouse mean held-out joint choice/RT quantile '
        'log score in bits/trial (higher better); right shows the same absolute BIC as alternative 1 '
        '(lower better). Bits here are the existing joint score converted by −NLL/(n_test ln2), '
        'not choice-only information gain over a bias baseline.\n\n'
        'Both alternatives: categorical means joined as visual guides, no error bars or significance '
        'tests. Existing seed-averaged independent training scores used for BIC; same QMLE approximation '
        'and caveats as earlier previews. No new fits or score evaluations. Publication styling is provisional.\n')
    (a.output/'manifest.json').write_text(json.dumps({
        'sources': {k: {'path':str(v.resolve()), 'sha256':hashlib.sha256(v.read_bytes()).hexdigest()} for k,v in paths.items()},
        'scope':'Rendering approved mean scores only; no fits or rescoring',
        'likelihood_display':a.likelihood,
        'script_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        'checks':{'all_values_finite':True, 'nll_group_n_is_10':True, 'll_equals_negative_saved_nll':True, 'bic_differences_match_previous_delta':True},
        'second_layout':'Literal interpretation of requested right panel: separate BIC subpanel'
    }, indent=2)+'\n')
    print(data.to_string())


if __name__ == '__main__':
    main()
