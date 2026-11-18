"""Summarize completed sensitivity and independently checked local refits."""
import argparse
import json
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scripts.paper.style import RC


def main():
    p=argparse.ArgumentParser(__doc__);p.add_argument('--pilot',type=Path,required=True);p.add_argument('--output',type=Path);a=p.parse_args()
    out=a.output or a.pilot/'summary';out.mkdir(exist_ok=False)
    rows=[]
    for path in a.pilot.glob('*/control/sensitivity.json'):
        record=json.loads(path.read_text());f=pd.DataFrame([{k:v for k,v in r.items() if k!='parameters'} for r in record['rows']])
        old=f[(f.gain_factor==1)&(f.sv_factor==1)&(f.guess_factor==1)].iloc[0]
        psych=f.loc[f.psy_rmse.idxmin()];joint=f.loc[f.joint_nll.idxmin()];n=record['meta']['n_train']
        rows.append({'mouse':record['meta']['mouse'],'n_controls':n,
            'psych_best_rmse_change_pp':100*(psych.psy_rmse-old.psy_rmse),
            'psych_best_joint_nll_change':psych.joint_nll-old.joint_nll,
            'psych_best_rt_nll_change_per1000':1000*(psych.rt_nll-old.rt_nll)/n,
            'psych_best_choice_nll_change_per1000':1000*(psych.choice_nll-old.choice_nll)/n,
            'joint_best_nll_change':joint.joint_nll-old.joint_nll})
    maps=pd.DataFrame(rows).sort_values('mouse');maps.to_csv(out/'sensitivity_tradeoffs.csv',index=False)
    confirm=pd.read_csv(a.pilot/'confirmation_100reps/new_minus_original.csv')
    confirm['joint_nll_change_per1000']=confirm.joint_nll*1000/confirm.mouse.map(maps.set_index('mouse').n_controls)
    confirm['psych_rmse_change_pp']=100*confirm.psy_rmse
    summary=confirm.groupby('mouse',as_index=False).agg(joint_nll_change=('joint_nll','mean'),
        joint_nll_change_per1000=('joint_nll_change_per1000','mean'),
        min_joint_change=('joint_nll','min'),max_joint_change=('joint_nll','max'),
        psych_rmse_change_pp=('psych_rmse_change_pp','mean'),central_deficit_change=('central_deficit','mean'))
    summary.to_csv(out/'confirmation_summary.csv',index=False)
    with plt.rc_context({**RC,'font.family':'DejaVu Sans'}):
        fig,axes=plt.subplots(1,3,figsize=(230/25.4,86/25.4))
        fig.subplots_adjust(left=.075,right=.985,bottom=.23,top=.76,wspace=.48)
        fig.text(.025,.98,'Control C: sensitivity and bounded optimization pilot',fontsize=10,va='top')
        fig.text(.075,.88,'Same model and likelihood. Existing manuscript fits retained.',fontsize=7,c='.3')
        ax=axes[0]
        ax.scatter(maps.psych_best_rmse_change_pp,maps.psych_best_rt_nll_change_per1000,c='.2',s=17)
        for i,r in enumerate(maps.itertuples()):
            ax.annotate(r.mouse,(r.psych_best_rmse_change_pp,r.psych_best_rt_nll_change_per1000),
                        xytext=(3,3 if i%2==0 else -8),textcoords='offset points',fontsize=5.5)
        ax.axhline(0,c='.6',ls=':',lw=.7)
        ax.set(xlabel='Change in choice-proportion RMSE (pp)\nNegative = closer psychometric fit',
               ylabel='Change in RT NLL / 1,000 controls\nPositive = worse RT score',title='Best choice-fit setting in each map')
        ax=axes[1];mice=['DBM13','DBM12','PSUIM10']
        for j,mouse in enumerate(mice):
            z=confirm[confirm.mouse==mouse]
            ax.plot(j+np.linspace(-.08,.08,len(z)),z.joint_nll_change_per1000,'o',c='.5',ms=3.5)
            ax.plot(j,z.joint_nll_change_per1000.mean(),'D',c='.1',ms=4)
        ax.axhline(0,c='.6',ls=':',lw=.7)
        ax.set(xticks=range(3),xticklabels=mice,ylabel='Refit − archived joint NLL\n(per 1,000 controls)',title='Independent 100-repetition checks')
        ax.text(.02,.97,'Dots: simulation seeds; diamonds: mean',transform=ax.transAxes,fontsize=5.2,va='top')
        ax=axes[2]
        scores=pd.read_csv(a.pilot/'confirmation_100reps/scores.csv')
        colors=['.2','#0072B2','#D55E00']
        for color,mouse in zip(colors,mice):
            z=scores[scores.mouse==mouse].groupby('name').central_deficit.mean()
            ax.plot([0,1],[z['archived_fit']*100,z['selected_refit']*100],'o-',c=color,lw=1,ms=3.5,label=mouse)
        ax.axhline(0,c='.6',ls=':',lw=.7)
        ax.set(xlim=(-.2,1.2),xticks=[0,1],xticklabels=['Archived fit','Selected refit'],ylabel='Intermediate-coherence deficit (pp)\nPositive = insufficient choice sensitivity',title='Did the shallow slope improve?')
        ax.legend(frameon=False,fontsize=5.5)
        for ax in axes:ax.title.set_fontsize(7)
        fig.text(.075,.025,'Exploratory local pilot. Simulation seeds are numerical checks, not biological replicates; no new significance tests.',fontsize=6,c='.3')
        for ext in ['png','pdf','svg']:fig.savefig(out/f'optimization_pilot.{ext}',dpi=300,facecolor='white')
        plt.close(fig)
    print(summary.to_string(index=False))


if __name__=='__main__':main()
