"""Scientific figures from saved CSVs; runs in the original plotting environment."""
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'dissemination/nhp_pulse_hmm_2026-11-15'
DATA=OUT/'assessment_v2'
COLORS={'static':'#888888','tied':'#0072B2','free':'#009E73'}
LABELS={'static':'Static GLM','tied':'Shared pulse weights','free':'State-specific pulse weights'}


def interval_point(ax,x,y,lo,hi,color,marker='o',label=None):
    ax.vlines(x,lo,hi,color=color,lw=1.2)
    ax.plot(x,y,marker,color=color,ms=5,label=label)


def run():
    diff=pd.read_csv(DATA/'heldout_differences.csv');rt=pd.read_csv(DATA/'rt_external_validation.csv')
    coefficients=pd.read_csv(DATA/'coefficients.csv');pulse=pd.read_csv(DATA/'pulse_congruency_validation.csv')
    plt.rcParams.update({'font.size':9,'pdf.fonttype':42,'ps.fonttype':42,
        'axes.spines.top':False,'axes.spines.right':False,'savefig.facecolor':'white'})
    fig,axes=plt.subplots(2,4,figsize=(16,8),constrained_layout=True)
    for i,mouse in enumerate(['PSUIM6','PSUIM7']):
        ax=axes[i,0]
        comparisons=[('tied','static'),('free','static'),('free','tied')]
        for j,(candidate,baseline)in enumerate(comparisons):
            z=diff[(diff.mouse==mouse)&(diff.candidate==candidate)&(diff.baseline==baseline)].iloc[0]
            interval_point(ax,j,z.gain_bits_per_trial,z.lo,z.hi,COLORS[candidate])
        ax.axhline(0,color='black',lw=.6)
        ax.set(title=f'{mouse}: future choice prediction',xticks=range(3),
            xticklabels=['Shared\nvs static','Free\nvs static','Free\nvs shared'],
            ylabel='Gain (bits / test trial)')
        ax=axes[i,1]
        names=[f'pulse_{direction}_stage{stage}'for stage in [1,2,3]for direction in ['left','right']]
        z=coefficients[(coefficients.mouse==mouse)&(coefficients.family=='free')]
        for shift,high,color,label in [(-.12,False,'#D55E00','Lower coherence contrast'),
                                     (.12,True,'#009E73','Higher coherence contrast')]:
            for j,name in enumerate(names):
                v=z[(z.feature==name)&(z.is_higher_contrast==high)].coefficient_right_logodds.dropna()
                if len(v):
                    interval_point(ax,j+shift,v.mean(),v.min(),v.max(),color,label=label if j==0 else None)
        ax.axhline(0,color='black',lw=.6)
        ax.axvspan(3.5,5.5,color='#777777',alpha=.07)
        ax.text(4.5,.96,'No late\npulses',ha='center',va='top',transform=ax.get_xaxis_transform(),fontsize=8)
        ax.set(title='Free pulse weights by state',xticks=range(6),xticklabels=['E-L','E-R','M-L','M-R','L-L','L-R'],
            ylabel='Right-choice log-odds coefficient')
        if i==0:ax.legend(frameon=False,fontsize=7,loc='lower left')
        ax=axes[i,2]
        for j,family in enumerate(['tied','free']):
            z=rt[(rt.mouse==mouse)&(rt.family==family)].iloc[0]
            interval_point(ax,j,z.coefficient_logrt,z.lo,z.hi,COLORS[family])
        ax.axhline(0,color='black',lw=.6)
        ax.set(title='Unused current-RT association',xticks=[0,1],xticklabels=['Shared','Free'],
            ylabel='Conditional log-RT slope for pre-choice state')
        ax=axes[i,3]
        for j,(stage,congruency)in enumerate([(1,'congruent'),(1,'incongruent'),(2,'congruent'),(2,'incongruent')]):
            for shift,family in [(-.24,'observed'),(-.08,'static'),(.08,'tied'),(.24,'free')]:
                z=pulse[(pulse.mouse==mouse)&(pulse.stage==stage)&(pulse.congruency==congruency)&(pulse.family==family)].iloc[0]
                if family=='observed':interval_point(ax,j+shift,z.effect_pp,z.lo,z.hi,'black',label='Observed'if j==0 else None)
                else:ax.plot(j+shift,z.effect_pp,'s',color=COLORS[family],ms=3.5,label=LABELS[family]if j==0 else None)
        ax.axhline(0,color='black',lw=.6)
        ax.set(title='Marginal pulse accuracy contrasts',xticks=range(4),
            xticklabels=['E-C','E-I','M-C','M-I'],ylabel='Pulse minus matched control (pp)')
        if i==0:ax.legend(frameon=False,fontsize=7,loc='lower right')
    fig.suptitle('NHP-fork GLM-HMM: states predict choices; state-specific pulse weights add no consistent gain\n'
        'Choice/RT intervals condition on trained models; coefficient ranges span training prefixes. Pulse contrasts pool retained RTs.',fontsize=11)
    fig.savefig(OUT/'pulse_hmm_pilot_final.pdf');fig.savefig(OUT/'pulse_hmm_pilot_final.png',dpi=160);plt.close(fig)


if __name__=='__main__':run()
