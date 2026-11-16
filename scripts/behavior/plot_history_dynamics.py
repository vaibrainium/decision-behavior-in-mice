"""Scientific figures from saved subject-level diagnostic outputs."""
import numpy as np
import pandas as pd
from scipy import stats
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from scripts.behavior.history_dynamics import OUT


def interval(a):
    return stats.t.interval(.95,len(a)-1,loc=np.mean(a),scale=stats.sem(a))


def run():
    plt.rcParams.update({'font.size':9,'pdf.fonttype':42,'ps.fonttype':42,
        'axes.spines.top':False,'axes.spines.right':False,'savefig.facecolor':'white'})
    colors={'win':'#0072B2','loss':'#D55E00','static':'#777777','continuous':'#009E73','discrete':'#CC79A7'}
    curves=pd.read_csv(OUT/'history_bias_curves.csv')
    mice=sorted(curves.mouse.unique())
    fig,axes=plt.subplots(2,5,figsize=(14,5.9),constrained_layout=True)
    for mouse,ax in zip(mice,axes.flat):
        for kind,label in [('win','After reward'),('loss','After error')]:
            z=curves[(curves.mouse==mouse)&(curves.scope=='all')&(curves.history==kind)]
            ax.plot(z.rt_s,z.bias_logodds_RminusL,'o-',color=colors[kind],ms=3,label=label)
            ax.fill_between(z.rt_s,z.lo,z.hi,color=colors[kind],alpha=.15)
        ax.axhline(0,color='black',lw=.6);ax.set(title=mouse,xlabel='Current RT (s)')
    axes[0,0].legend(frameon=False,fontsize=8)
    for ax in axes[:,0]:ax.set_ylabel('History bias: log odds\nprevious right versus left')
    fig.suptitle('History bias varies across mice and response times\nShading: pointwise within-session block intervals; current-RT conditioning is descriptive',fontsize=11)
    fig.savefig(OUT/'history_bias_by_mouse.pdf');fig.savefig(OUT/'history_bias_by_mouse.png',dpi=160);plt.close(fig)

    acf=pd.read_csv(OUT/'residual_acf.csv');state=pd.read_csv(OUT/'states_v2_grid15_mouse_summary.csv')
    group=pd.read_csv(OUT/'states_v2_grid15_group_inference.csv').set_index('metric')
    fig,axes=plt.subplots(2,2,figsize=(11,8),constrained_layout=True)
    for ax,kind in zip(axes[0],['choice','rt']):
        for model,color,label in [('base','#777777','Evidence/session'),('history','#0072B2','Plus previous choice/outcome/RT')]:
            z=acf[(acf.kind==kind)&(acf.model==model)]
            t=z.pivot(index='mouse',columns='lag',values='acf')
            mean=t.mean(0);se=t.std(0,ddof=1)/np.sqrt(len(t));margin=stats.t.ppf(.975,len(t)-1)*se
            ax.plot(t.columns,mean,color=color,label=label)
            ax.fill_between(t.columns,mean-margin,mean+margin,color=color,alpha=.12)
        ax.axhline(0,color='black',lw=.6)
        ax.set(title='A  Choice residuals'if kind=='choice'else'B  Log-RT residuals',
               xlabel='Lag in recorded rows',ylabel='Mean residual correlation across mice')
    axes[0,0].legend(frameon=False,fontsize=8)
    ax=axes[1,0];xx=np.arange(len(state))
    for shift,kind,label in [(-.13,'continuous','Continuous bias'),(.13,'discrete','Two-state bias')]:
        ax.scatter(xx+shift,state[f'{kind}_gain_bits'],s=25,color=colors[kind],label=label)
    ax.axhline(0,color='black',lw=.6)
    ax.set(title='C  Prefix-trained choice prediction',xticks=xx,xticklabels=state.mouse,
           ylabel='Gain over fixed history GLM (bits / test trial)')
    ax.tick_params(axis='x',rotation=65);ax.legend(frameon=False,fontsize=8)
    ax=axes[1,1]
    for shift,kind in [(-.13,'continuous'),(.13,'discrete')]:
        ax.scatter(xx+shift,state[f'{kind}_rt_alignment'],s=25,color=colors[kind])
    ax.axhline(0,color='black',lw=.6)
    ax.set(title='D  RT association varies across mice',xticks=xx,xticklabels=state.mouse,
        ylabel='Conditional log-RT slope for choice × prior bias')
    ax.tick_params(axis='x',rotation=65)
    fig.suptitle('Persistent choice structure does not establish a joint choice/RT mechanism\nA–B: same-session held-out blocks; C–D: earlier-prefix training and sequential future prediction',fontsize=11)
    fig.savefig(OUT/'history_state_overview.pdf');fig.savefig(OUT/'history_state_overview.png',dpi=160);plt.close(fig)

    reg=pd.read_csv(OUT/'state_regularization_sensitivity.csv')
    fig,axes=plt.subplots(1,2,figsize=(12,4.3),constrained_layout=True)
    for ax,baseline,title in zip(axes,['history1','history10'],['Tuned first-order history','Tuned ten-record history']):
        values=reg[f'continuous_tuned_gain_vs_{baseline}_tuned_bits']
        ax.bar(np.arange(len(reg)),values,color=colors['continuous'],alpha=.8)
        ax.axhline(0,color='black',lw=.6)
        ax.set(title=title,xticks=np.arange(len(reg)),xticklabels=reg.mouse,
               ylabel='Continuous bias gain (bits / test trial)')
        ax.tick_params(axis='x',rotation=65)
    fig.suptitle('Robustness to fixed history and training-only regularization\nPenalties selected on inner training-prefix blocks; final test outcomes unused',fontsize=11)
    fig.savefig(OUT/'history_state_robustness.pdf');fig.savefig(OUT/'history_state_robustness.png',dpi=160);plt.close(fig)


if __name__=='__main__':run()
