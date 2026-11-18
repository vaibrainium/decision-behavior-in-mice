"""Render absolute QMLE-based BIC from verified seed-averaged mouse scores."""
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


def main():
    parser = argparse.ArgumentParser(__doc__)
    parser.add_argument('--input', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=False)
    source = args.input / 'bic_per_mouse.csv'
    per = pd.read_csv(source)
    models = ['C', 'E', 'ES', 'DDMx', 'ESx']
    assert not per.duplicated(['mouse', 'model']).any()
    wide = per.pivot(index='mouse', columns='model', values='bic_qmle')[models]
    assert wide.shape == (10, 5) and np.isfinite(wide.to_numpy()).all()
    group = wide.mean().rename('mean_bic_qmle').to_frame()
    previous = pd.read_csv(args.input / 'group_metrics.csv').set_index('model')
    delta = group.mean_bic_qmle - group.loc['C', 'mean_bic_qmle']
    np.testing.assert_allclose(delta, previous.loc[models, 'delta_bic_vs_C'], atol=1e-9)
    group.to_csv(args.output / 'group_absolute_bic.csv')
    (args.output / 'source_bic_per_mouse.csv').write_bytes(source.read_bytes())
    with plt.rc_context({**RC, 'font.family': 'DejaVu Sans'}):
        fig, ax = plt.subplots(figsize=(100/25.4, 85/25.4))
        fig.subplots_adjust(left=.23, right=.97, bottom=.18, top=.77)
        fig.text(.04, .97, 'C', fontsize=12, fontweight='bold', va='top')
        fig.text(.23, .97, 'Complexity-adjusted model fit', fontsize=8.5, va='top')
        fig.text(.23, .86, 'Mean across 10 mice; lower is better', fontsize=6.7, color='.3')
        y = group.mean_bic_qmle.to_numpy()
        pad = np.ptp(y)*.30
        ax.plot(range(5), y, 'o-', color='.2', lw=1, ms=5.5)
        for j, v in enumerate(y):
            ax.text(j, v+pad*.20, f'{v:.1f}', ha='center', fontsize=6.3)
        ax.set(xticks=range(5), xticklabels=models, xlabel='Model', ylabel='Mean BIC (QMLE-based)',
               xlim=(-.45, 4.45), ylim=(y.min()-pad, y.max()+pad))
        ax.yaxis.set_major_locator(MaxNLocator(nbins=4))
        ax.ticklabel_format(axis='y', style='plain', useOffset=False)
        for ext in ['png', 'pdf', 'svg']:
            fig.savefig(args.output / f'absolute_bic.{ext}', dpi=300, facecolor='white')
        plt.close(fig)
    (args.output/'caption.md').write_text(
        'Absolute QMLE-based BIC. Points show the equal-mouse mean across 10 mice, '
        'after averaging the two independent scoring seeds within mouse/model. '
        'BIC = 2 NLL_training + k ln(n_training), using previously independently '
        'evaluated full-control fits. Lower is better. No reference subtraction, '
        'error bars or new significance tests. Line connects categorical means as '
        'a visual guide; the labeled y-axis does not begin at zero. '
        'This is the same QMLE approximation and source scores as the preceding ΔBIC '
        'preview. No new score evaluation or parameter fitting.\n')
    (args.output/'manifest.json').write_text(json.dumps({
        'source': str(source.resolve()), 'source_sha256': hashlib.sha256(source.read_bytes()).hexdigest(),
        'scope': 'Rendering and equal-mouse aggregation of existing scores only',
        'n_mice': 10, 'models': models,
        'check_mean_differences_match_previous_delta_bic': True,
        'script_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    }, indent=2)+'\n')
    print(group.to_string())


if __name__ == '__main__':
    main()
