"""Direct-label group recovery display from existing cohort-recombination rates."""
import argparse
import hashlib
import json
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch
import pandas as pd
from scripts.paper.style import RC


def main():
    p=argparse.ArgumentParser(__doc__);p.add_argument('--input',type=Path,required=True);p.add_argument('--output',type=Path,required=True)
    a=p.parse_args();a.output.mkdir(parents=True,exist_ok=False)
    frame=pd.read_csv(a.input).set_index('generator').loc[['C','E','ES']]
    # One direct percentage can represent both comparisons only because their rates coincide here.
    assert frame.rep_E.equals(frame.rep_ES)
    assert frame.rep_E.isin([0.,1.]).all()
    values=frame.rep_E
    source=frame.reset_index().copy();source['n_recombined_cohorts']=1024
    source['n_favor_C_vs_E']=(source.rep_E*1024).astype(int);source['n_favor_C_vs_ES']=(source.rep_ES*1024).astype(int)
    source.to_csv(a.output/'source_cohort_recovery.csv',index=False)
    with plt.rc_context({**RC,'font.family':'DejaVu Sans'}):
        fig,ax=plt.subplots(figsize=(155/25.4,98/25.4));ax.set_axis_off();ax.set(xlim=(0,1),ylim=(0,1))
        fig.subplots_adjust(left=.025,right=.975,bottom=.035,top=.97)
        ax.text(.005,.99,'D',fontsize=12,fontweight='bold',va='top')
        ax.text(.08,.99,'Can the group analysis recover accumulation?',fontsize=9,va='top')
        ax.text(.09,.84,'Model generating the behavior',fontsize=8,fontweight='bold')
        ax.text(.72,.84,'Group analysis favored C',fontsize=8,fontweight='bold',ha='center')
        ax.text(.72,.78,'Same rates against E and ES',fontsize=6.5,color='.35',ha='center')
        labels={'C':'C — accumulation','E':'E — rapid forgetting','ES':'ES — sample extrema'}
        for model,y in zip(['C','E','ES'],[.64,.43,.22]):
            box=FancyBboxPatch((.07,y-.067),.36,.135,boxstyle='round,pad=.01,rounding_size=.012',
                               facecolor='.95',edgecolor='.75',linewidth=.6)
            ax.add_patch(box);ax.text(.25,y,labels[model],ha='center',va='center',fontsize=8)
            ax.annotate('',xy=(.56,y),xytext=(.46,y),arrowprops={'arrowstyle':'->','color':'.45','lw':1})
            rate=float(values.loc[model]);color='#0072B2' if rate else '.2'
            ax.text(.72,y+.025,f'{100*rate:.0f}%',ha='center',va='center',fontsize=20,fontweight='bold',color=color)
            ax.text(.72,y-.04,f'{int(rate*1024):,} / 1,024 cohorts',ha='center',va='center',fontsize=7,color='.3')
        ax.text(.50,.04,'Cohorts reuse two simulated datasets per mouse; they are not independent experiments.',
                ha='center',va='center',fontsize=6.1,color='.35')
        for ext in ['png','pdf','svg']:fig.savefig(a.output/f'figure3D.{ext}',dpi=300,facecolor='white')
        plt.close(fig)
    (a.output/'caption.md').write_text('''Panel D. Group-level recovery from simulated behavior. Rows identify the model used to generate choices and RTs. Each percentage is the fraction of1,024 recombined ten-mouse cohorts for which the original group analysis favored C over the indicated alternative. The C-versus-E and C-versus-ES rates are identical in every displayed row, so a single percentage is shown for both comparisons: C-generated100%, E-generated0%, ES-generated0%. “Favored C” requires a positive mean normalized held-out NLL advantage and a two-sided mouse-level t-test with Holm-adjusted p<0.05 across the four alternative comparisons. This is not five-way winner selection. Cohorts select one of two simulated dataset replicates per mouse (2^10 combinations); they reuse datasets and are not independent experiments. Percentages are conditional on the tested generating parameters, schedules and candidate set; they are not universal false-positive rates. Values are unchanged from the preceding D.\n''')
    (a.output/'manifest.json').write_text(json.dumps({'source':str(a.input.resolve()),'source_sha256':hashlib.sha256(a.input.read_bytes()).hexdigest(),
        'script_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        'scope':'Rendering-only redesign, identical existing group-recovery rates',
        'checks':{'both_comparison_rates_equal_in_all_rows':True,'all_rates_are_zero_or_one':True,'count_denominator_1024':True},
        'status':'Draft for author review; placement undecided'},indent=2)+'\n')


if __name__=='__main__':main()
