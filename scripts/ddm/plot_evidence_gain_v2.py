"""Re-render the feasibility figure with the full observed uncertainty range.

Analysis tables/fits are read-only. The original figure is retained.
"""
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from scripts.ddm.assess_evidence_gain import OUT,MICE,FAMILIES,SEEDS,REPS,COLORS,LABELS,inputs,BINS


def run():
    x=inputs();d=pd.read_csv(OUT/'data_pulse_profile.csv');p=pd.read_csv(OUT/'model_pulse_profile.csv')
    delta=pd.read_csv(OUT/'training_differences_from_drift.csv')
    plt.rcParams.update({'font.size':9,'pdf.fonttype':42,'ps.fonttype':42,
        'axes.spines.top':False,'axes.spines.right':False})
    fig,axes=plt.subplots(2,4,figsize=(15.5,7.4),constrained_layout=True)
    for i,mouse in enumerate(MICE):
        ax=axes[i,0]
        for j,family in enumerate(['fixed','gain']):
            z=delta[(delta.mouse==mouse)&(delta.family==family)]
            for shift,key in [(-.13,'delta_choice_nll'),(.13,'delta_rt_nll')]:
                ax.bar(j+shift,z[key].mean(),width=.25,color=COLORS[family],alpha=.45 if shift<0 else 1.)
                ax.plot(np.full(len(z),j+shift),z[key],'.',color='#333333',ms=3)
        ax.axhline(0,color='black',lw=.6);ax.set(title=f'{mouse}: choice (pale) / RT (dark)',
            xticks=[0,1],xticklabels=['Fixed','Positive gain'],ylabel='Training NLL difference versus drift variability')
        ax=axes[i,1];bins=np.linspace(.3,5,48)
        schedules=np.flatnonzero((x['subject_id']==mouse)&(x['sched_pulse_type']==0)&(np.round(x['signed_coherence']*100)==-100))
        vals=x['rt'][schedules[x['choice'][schedules]==0]]
        ax.stairs(np.histogram(vals,bins)[0]/len(vals)/np.diff(bins),bins,color='black',label='Observed',lw=1.8)
        for family in FAMILIES:
            parts=[]
            for seed in SEEDS:
                o=pd.read_pickle(OUT/'cache'/f'eval_{mouse}_{family}_r{REPS}_s{seed}.pkl')['outcomes']
                parts.append(o.loc[o.row.isin(schedules)&(o.choice==0),'rt'].to_numpy())
            vals=np.concatenate(parts)
            ax.stairs(np.histogram(vals,bins)[0]/len(vals)/np.diff(bins),bins,color=COLORS[family],label=LABELS[family])
        ax.set(title='Correct −100% control responses',xlabel='Response time (s)',ylabel='Density',xlim=(.3,5))
        if i==0:ax.legend(frameon=False,fontsize=7)
        for j,sign in [(2,1),(3,-1)]:
            ax=axes[i,j];z=d[(d.mouse==mouse)&(d.sign==sign)]
            mid=(np.array(BINS[:-1])+BINS[1:])/2;k=z.bin.to_numpy(int)
            ax.errorbar(mid[k],z.effect_pp,yerr=[z.effect_pp-z.lo_pp,z.hi_pp-z.effect_pp],fmt='o',color='black',ms=3,lw=.8,capsize=2)
            for family in FAMILIES:
                v=p[(p.mouse==mouse)&(p.family==family)&(p.sign==sign)]
                t=v.groupby('bin').effect_pp.agg(['mean','min','max']);ix=t.index.to_numpy(int)
                ax.plot(mid[ix],t['mean'],color=COLORS[family],lw=1.3)
                ax.fill_between(mid[ix],t['min'],t['max'],color=COLORS[family],alpha=.12)
            ax.axhline(0,color='black',lw=.6)
            whole=d[(d.mouse==mouse)&(d.sign!=0)]
            ax.set(title='Positive pulse'if sign==1 else'Negative pulse',xlabel='Time after pulse onset (s)',
                ylabel='Choice shift toward pulse (pp)',xlim=(.25,5),
                ylim=(min(-5.,whole.lo_pp.min()-1),max(5.,whole.hi_pp.max()+1)))
    fig.suptitle('Positive evidence gain: bounded training-data feasibility\nFresh simulation seeds assess numerical noise; full-data fits, not held-out predictions',fontsize=12)
    fig.savefig(OUT/'gain_feasibility_v2.pdf');fig.savefig(OUT/'gain_feasibility_v2.png',dpi=160);plt.close(fig)


if __name__=='__main__':run()
