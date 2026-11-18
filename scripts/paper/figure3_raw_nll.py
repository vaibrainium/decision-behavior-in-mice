"""Figure 3A: untransformed held-out NLL, with descriptive group or mouse display."""
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

ROOT = Path(__file__).resolve().parents[2]
MODELS = ['C','E','ES','DDMx','ESx']


def main():
    parser = argparse.ArgumentParser(__doc__)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--display', choices=['group','mouse'], default='group')
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=False)
    score_path = ROOT/'dissemination/paper_control/tables/heldout_nll_per_mouse_2026-10-29.csv'
    fold_path = ROOT/'dissemination/reviewer_2026-11-13/control_fold_inventory.csv'
    difference_path = ROOT/'dissemination/paper_control/tables/heldout_diff_per_mouse_2026-10-29.csv'
    scores = pd.read_csv(score_path)
    scores = scores[scores.model.isin(MODELS)].copy()
    folds = pd.read_csv(fold_path)
    folds = folds[folds.model.isin(MODELS)]
    totals = folds.groupby(['mouse','model']).agg(n_folds=('fold','nunique'),
                n_test=('n_test','sum'), total_nll=('test_nll','sum'))
    assert totals.n_folds.eq(5).all()
    rows = scores.set_index(['mouse','model']).sort_index()
    assert len(rows)==50 and not rows.index.has_duplicates
    assert rows.groupby(level='mouse').control_trials.nunique().eq(1).all()
    np.testing.assert_allclose(rows.test_nll, totals.loc[rows.index].total_nll, rtol=1e-12)
    np.testing.assert_array_equal(rows.control_trials, totals.loc[rows.index].n_test)
    differences = pd.read_csv(difference_path)
    for _, row in differences[differences.part.eq('total') & differences.model.isin(MODELS)].iterrows():
        expected = rows.loc[(row.mouse,row.model),'test_nll'] - rows.loc[(row.mouse,'C'),'test_nll']
        assert np.isclose(expected,row.summed)
    mice = sorted(scores.mouse.unique())
    with plt.rc_context({**RC,'font.family':'DejaVu Sans'}):
        if args.display == 'group':
            group = scores.groupby('model').test_nll.agg(['mean','sem','count']).loc[MODELS]
            assert group['count'].eq(10).all()
            fig, ax = plt.subplots(figsize=(100/25.4,85/25.4))
            fig.subplots_adjust(left=.19,right=.97,bottom=.18,top=.77)
            fig.text(.04,.97,'A',fontsize=12,fontweight='bold',va='top')
            fig.text(.19,.97,'Held-out model likelihood',fontsize=9,va='top')
            fig.text(.19,.86,'Mean across 10 mice; lower is better',fontsize=6.7,color='.3')
            ax.scatter(range(5),group['mean'],color='.2',s=30,zorder=3)
            ax.plot(range(5),group['mean'],color='.2',lw=1,zorder=2)
            span = float(group['mean'].max()-group['mean'].min())
            padding = max(span*.30,1.)
            for pos,value in enumerate(group['mean']):
                ax.text(pos,value+padding*.20,f'{value:,.1f}',ha='center',fontsize=6.4)
            ax.set(xticks=range(5),xticklabels=MODELS,ylabel='Mean total held-out NLL',
                   xlabel='Model',xlim=(-.45,4.45),ylim=(float(group['mean'].min())-padding,float(group['mean'].max())+padding))
            ax.yaxis.set_major_locator(MaxNLocator(nbins=4))
            ax.ticklabel_format(axis='y',style='plain',useOffset=False)
            group.reset_index().to_csv(args.output/'group_nll.csv',index=False)
        else:
            fig, axes = plt.subplots(2,5,figsize=(180/25.4,100/25.4))
            fig.subplots_adjust(left=.085,right=.95,bottom=.15,top=.78,wspace=1.10,hspace=.95)
            fig.text(.025,.97,'A',fontsize=12,fontweight='bold',va='top')
            fig.text(.085,.97,'Held-out NLL by mouse',fontsize=10,va='top')
            fig.text(.085,.875,'Five-fold totals; lower is better. Compare models within each mouse.',fontsize=6.8,color='.3')
            for ax,mouse in zip(axes.flat,mice):
                values = rows.loc[mouse].loc[MODELS]
                assert values.test_nll.ge(0).all()
                ax.barh(range(5),values.test_nll,color='.25',height=.62)
                largest = values.test_nll.max()
                for pos,value in enumerate(values.test_nll):
                    ax.text(value+largest*.025,pos,f'{value:.2f}',va='center',fontsize=5.8)
                ax.set_title(f'{mouse}\nn = {int(values.control_trials.iloc[0]):,}',fontsize=7,pad=5)
                ax.set_yticks(range(5),MODELS,fontsize=6.2)
                ax.tick_params(axis='x',labelsize=6.2)
                ax.tick_params(axis='y',length=0)
                ax.xaxis.set_major_locator(MaxNLocator(nbins=2))
                ax.ticklabel_format(axis='x',style='plain',useOffset=False)
                ax.set(xlim=(0,largest*2.0),ylim=(4.6,-.6))
            fig.text(.54,.025,'Total held-out NLL (zero baseline; mouse-specific scales)',ha='center',fontsize=7.5)
        for suffix in ['pdf','svg','png']:
            fig.savefig(args.output/f'figure3A.{suffix}',dpi=300,facecolor='white')
        plt.close(fig)
    scores[['mouse','model','control_trials','test_nll']].to_csv(args.output/'absolute_nll.csv',index=False)
    folds.to_csv(args.output/'fold_scores.csv',index=False)
    manifest = {'scope':'Unsubtracted total held-out NLL, summed over five folds. No normalization, scoring rerun or new fit.',
                'models':MODELS,'mice':mice,'control_trials':int(rows.xs('C',level='model').control_trials.sum()),
                'display':args.display,
                'group_marks':'Mean points connected across categorical models as a visual guide, no error bars; labeled nonzero NLL axis limits for readability.',
                'aggregation':'Equal-mouse arithmetic mean of raw five-fold total NLL; no plotted error bars. SEM retained in source table only, not used to represent paired comparison uncertainty. No trial-count normalization or reference subtraction.',
                'literature_check':{'doi':'10.7554/eLife.55365','figure':'7B','source_metric':'Delta BIC, not raw NLL','adopted_feature':'Subject-specific horizontal-bar display; the requested raw held-out NLL metric is retained.'},
                'checks':{'all_totals_match_fold_inventory':True,'trial_counts_match_fold_inventory':True,'old_differences_reproduced':True},
                'source_hashes':{str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in [score_path,fold_path,difference_path,Path(__file__)]}}
    (args.output/'figure_manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    print(args.output/'figure3A.png')


if __name__=='__main__':
    main()
