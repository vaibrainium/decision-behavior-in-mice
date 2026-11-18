"""Render LL/BIC and joint bits/BIC as two dual-axis alternatives for panel A."""
import argparse
import hashlib
import json
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scripts.paper.style import RC
from scripts.paper.figure3A_metric_alternatives import MODELS, BLUE, ORANGE, axis_style, save


def main():
    p = argparse.ArgumentParser(__doc__)
    p.add_argument('--input', type=Path, required=True)
    p.add_argument('--output', type=Path, required=True)
    a = p.parse_args()
    a.output.mkdir(parents=True, exist_ok=False)
    data = pd.read_csv(a.input).set_index('model').loc[MODELS]
    assert np.isfinite(data.to_numpy()).all()
    np.testing.assert_array_equal(data.mean_test_ll, -data.mean_test_nll)
    data.to_csv(a.output/'source_panel_A.csv')
    specs = [('A1_ll_bic_dual_axis', 'Log likelihood and BIC', 'mean_test_ll', 'Mean test LL', 'Test LL'),
             ('A2_bits_bic_dual_axis', 'Test bits/trial and BIC', 'mean_joint_test_bits_per_trial',
              'Joint test log score (bits/trial)', 'Test bits/trial')]
    with plt.rc_context({**RC, 'font.family': 'DejaVu Sans'}):
        for name, title, key, ylabel, legend in specs:
            fig, left = plt.subplots(figsize=(110/25.4, 88/25.4))
            fig.subplots_adjust(left=.20, right=.80, bottom=.17, top=.74)
            right = left.twinx()
            left.plot(range(5), data[key], 'o-', color=BLUE, lw=1, ms=5, label=legend)
            right.plot(range(5), data.mean_bic_qmle, 's--', color=ORANGE, lw=1, ms=4.5, label='Training BIC')
            axis_style(left, data[key], ylabel, BLUE)
            axis_style(right, data.mean_bic_qmle, 'Mean BIC (QMLE-based)', ORANGE)
            right.spines['right'].set_visible(True)
            left.spines['left'].set_color(BLUE)
            right.spines['right'].set_color(ORANGE)
            fig.text(.035, .97, 'A', fontsize=12, fontweight='bold', va='top')
            fig.text(.20, .97, title, fontsize=9, va='top')
            fig.text(.20, .87, '10 mice; blue higher, orange lower is better', fontsize=6.3, color='.3')
            fig.legend(handles=left.lines+right.lines, loc='upper center', bbox_to_anchor=(.5,.835),
                       ncol=2, frameon=False, fontsize=6.6, handlelength=2.2)
            save(fig, a.output, name)
    (a.output/'captions.md').write_text(
        'Two alternatives for panel A, both with two y-axes. Blue solid circles: '
        'left test LL in A1, left joint choice/RT test log score in bits/trial in A2; '
        'higher is better. Orange dashed squares: right mean training QMLE-based BIC, '
        'lower is better. Equal-mouse means across 10 mice; BIC is averaged over existing '
        'independent scoring seeds within mouse. LL = −NLL. Bits/trial = LL/(n_test ln2) '
        'within mouse before averaging; not choice-only gain over a null. '
        'Axes use independently labeled nonzero ranges. Curve intersections have no '
        'statistical meaning. No error bars, tests, new fits or scoring.\n')
    (a.output/'manifest.json').write_text(json.dumps({
        'source': str(a.input.resolve()), 'source_sha256': hashlib.sha256(a.input.read_bytes()).hexdigest(),
        'script_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        'scope': 'Rendering existing verified scores only', 'both_figures_use_two_y_axes': True,
        'll_negative_nll_verified': True
    }, indent=2)+'\n')
    print(a.output)


if __name__ == '__main__':
    main()
