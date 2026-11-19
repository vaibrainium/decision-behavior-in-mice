"""Audit timing coefficient averages against observed curves and a shared-asymptote sensitivity."""
import argparse
import hashlib
import itertools
import json
from pathlib import Path
import numpy as np
import pandas as pd
from scipy.optimize import least_squares
from scipy.special import expit
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from scripts.paper.style import RC,LEFT_COLOR,RIGHT_COLOR
from src.utils.pmf_utils import fit_psychometric_function

DIRECTIONS=[0,-1,1];STAGES=['early','middle']
COLORS={0:'.4',-1:LEFT_COLOR,1:RIGHT_COLOR};NAMES={0:'Control',-1:'Left pulse',1:'Right pulse'}


def predict(q,x,d):
    return q[6]+(1-q[6]-q[7])*expit(q[3+d]*(x-q[d]))


def fit_group(group,warm=None):
    x=group.coherence_pct.to_numpy();y=group['mean'].to_numpy();d=group.direction.map({k:i for i,k in enumerate(DIRECTIONS)}).to_numpy()
    def residual(q):return predict(q,x,d)-y
    bounds=([-100]*3+[1e-5]*3+[1e-5]*2,[100]*3+[30]*3+[.4]*2)
    if warm is None:
        starts=[np.array([0,-shift,shift,b,b,b,l,u]) for shift,b,(l,u) in itertools.product([-20,0,20],[.015,.05,.15],[(.05,.05),(.2,.1)])]
    else:starts=[warm,np.array([0,0,0,.05,.05,.05,.1,.1])]
    runs=[least_squares(residual,np.clip(seed,*bounds),bounds=bounds,max_nfev=2000,ftol=1e-10,xtol=1e-10,gtol=1e-10) for seed in starts]
    good=[r for r in runs if r.success and np.all(np.isfinite(r.fun))]
    if not good:raise RuntimeError('All joint curve starts failed')
    return min(good,key=lambda r:np.sum(r.fun**2))


def main():
    p=argparse.ArgumentParser(__doc__);p.add_argument('--source',type=Path,required=True);p.add_argument('--output',type=Path,required=True);p.add_argument('--bootstrap',type=int,default=120)
    a=p.parse_args();a.output.mkdir(parents=True,exist_ok=False)
    cells=pd.read_csv(a.source/'mouse_cells.csv');cells=cells[cells.onset_stratum.isin(STAGES)].copy();mice=sorted(cells.mouse.unique());assert len(mice)==10
    raw=pd.read_csv('/mnt/data/processed/pulse_followup/20261023T191030Z_fa8de8b/data/trial_table.csv',low_memory=False).set_index('trial_id')
    trials=pd.read_csv(a.source/'eligible_trials.csv');pulse=trials[trials.direction!=0];rawp=raw.loc[pulse.trial_id]
    assert np.array_equal(np.sign(rawp.pulse_coherence_pct.to_numpy()),pulse.direction.to_numpy())
    groups=cells.groupby(['onset_stratum','direction','coherence_pct'],as_index=False)['mean'].agg(mean='mean',sem='sem',n_mice='size');groups.to_csv(a.output/'observed_group.csv',index=False)
    gen=np.random.default_rng(13719);draws=gen.multinomial(10,np.full(10,.1),size=a.bootstrap);params=[];boots=[];pred=[];free=[]
    for stage in STAGES:
        g=groups[groups.onset_stratum==stage];best=fit_group(g);q=best.x
        for i,d in enumerate(DIRECTIONS):
            z=g[g.direction==d];f=fit_psychometric_function(z.coherence_pct.to_numpy(),z['mean'].to_numpy(),None,'logit_4');c=f.coefs_
            ratio=(.5-c['lapse_rate'])/(1-c['guess_rate']-c['lapse_rate'])
            crossing=c['mean']+np.log(ratio/(1-ratio))/c['var'] if 0<ratio<1 else np.nan
            free.append({'stage':stage,'direction':d,'alpha':c['mean'],'beta':c['var'],'lower':c['lapse_rate'],'upper':1-c['guess_rate'],'p_half_crossing':crossing,'sse':f.weighted_sse_})
            params.append({'stage':stage,'direction':d,'alpha':q[i],'beta':q[3+i],'delta_beta':q[3+i]-q[3],'lower':q[6],'upper':1-q[7],'joint_sse':float(np.sum(best.fun**2)),'jac_condition':float(np.linalg.cond(best.jac.T@best.jac))})
            grid=np.linspace(z.coherence_pct.min(),z.coherence_pct.max(),301)
            pred.append(pd.DataFrame({'stage':stage,'direction':d,'coherence_pct':grid,'shared_fit':predict(q,grid,i),'free_fit':f.predict(grid)}))
        z=cells[cells.onset_stratum==stage].copy();z['mi']=pd.Categorical(z.mouse,categories=mice).codes
        for b,counts in enumerate(draws):
            z['weight']=counts[z.mi.to_numpy()];z['weighted']=z['mean']*z.weight
            bg=z.groupby(['direction','coherence_pct'],as_index=False).agg(n=('weight','sum'),total=('weighted','sum'));bg=bg[bg.n>0];bg['mean']=bg.total/bg.n
            bfit=fit_group(bg,q);bq=bfit.x
            for i,d in enumerate(DIRECTIONS):boots.append({'stage':stage,'rep':b,'direction':d,'alpha':bq[i],'beta':bq[3+i],'delta_beta':bq[3+i]-bq[3],'lower':bq[6],'upper':1-bq[7]})
        print(stage,'bootstrap complete',flush=True)
    params=pd.DataFrame(params);boots=pd.DataFrame(boots);pred=pd.concat(pred);free=pd.DataFrame(free)
    params.to_csv(a.output/'shared_parameters.csv',index=False);boots.to_csv(a.output/'bootstrap_parameters.csv',index=False);pred.to_csv(a.output/'curve_predictions.csv',index=False);free.to_csv(a.output/'independent_population_fits.csv',index=False)
    intervals=boots.groupby(['stage','direction'])[['alpha','beta','delta_beta']].quantile([.025,.975]);intervals.index.names=['stage','direction','quantile'];intervals.to_csv(a.output/'intervals.csv')
    with plt.rc_context(RC):
        fig,axes=plt.subplots(1,2,figsize=(7,3.2),layout='constrained')
        for ax,stage in zip(axes,STAGES):
            for d in DIRECTIONS:
                z=groups[(groups.onset_stratum==stage)&(groups.direction==d)].sort_values('coherence_pct');f=pred[(pred.stage==stage)&(pred.direction==d)]
                ax.errorbar(z.coherence_pct,z['mean'],yerr=z['sem'],fmt='o',color=COLORS[d],capsize=2,ms=3,label=NAMES[d]);ax.plot(f.coherence_pct,f.shared_fit,c=COLORS[d],lw=1.2)
            ax.axhline(.5,c='.8',ls=':',lw=.6);ax.set(xlim=(-105,105),ylim=(0,1),xlabel='Signed baseline coherence (%)',ylabel='P(right choice)',title=stage.capitalize()+' pulse')
        axes[0].legend();fig.suptitle('Observed choice curves: all 10 mice\nPoints: equal-mouse means ± SEM; lines: joint fits with shared asymptotes',fontsize=8)
        for ext in ['png','pdf','svg']:fig.savefig(a.output/f'observed_curves.{ext}',dpi=250)
        plt.close(fig)
        fig,axes=plt.subplots(1,2,figsize=(7,3.2),layout='constrained')
        for ax,param,label in zip(axes,['alpha','delta_beta'],['α: population-curve midpoint (% coherence)','Δβ: pulse − control (per % coherence)']):
            for d in [-1,1]:
                z=params[params.direction==d].set_index('stage').loc[STAGES];lo=intervals.xs(d,level='direction').xs(.025,level='quantile').loc[STAGES,param];hi=intervals.xs(d,level='direction').xs(.975,level='quantile').loc[STAGES,param]
                ax.plot([0,1],z[param],'o-',c=COLORS[d],label=NAMES[d]);ax.vlines([0,1],lo,hi,colors=COLORS[d]);ax.plot([0,1],lo,'_',c=COLORS[d]);ax.plot([0,1],hi,'_',c=COLORS[d])
            ax.axhline(0,c='.7',ls=':',lw=.7);ax.set(xticks=[0,1],xticklabels=['Early','Middle'],xlabel='Scheduled pulse time',ylabel=label)
        axes[0].legend();fig.suptitle('Population-curve sensitivity: shared asymptotes, all 10 mice\nWhole-mouse bootstrap 95% intervals; no imposed direction or timing trend',fontsize=8)
        for ext in ['png','pdf','svg']:fig.savefig(a.output/f'population_parameters.{ext}',dpi=250)
        plt.close(fig)
    zero=cells[cells.coherence_pct==0].pivot(index=['mouse','onset_stratum'],columns='direction',values='mean');zero['right_minus_left']=zero[1]-zero[-1];zero.to_csv(a.output/'zero_coherence_mouse_choices.csv')
    manifest={'scope':'Audit and changed-estimand sensitivity, not replacement individual-mean coefficients','physical_direction_mismatches':0,'n_mice':10,'n_bootstrap':a.bootstrap,'seed':13719,'main_fit':'Joint per-time fit to equal-mouse coherence means; each curve has own alpha/beta, all3 curves share lower/upper asymptotes within time; WLS unweighted across group points as Figure4A','bootstrap':'Whole-mouse resampling, same draws across times and directions;120 percentile intervals exploratory','selection':'Minimum residual error from both direction-shift signs and flat starts; no sign restrictions on alpha or trends','source_hashes':{str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in [a.source/'mouse_cells.csv',a.source/'fits.csv',Path(__file__)]}}
    (a.output/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n');print(params.to_string(index=False),flush=True);print(zero.groupby('onset_stratum').right_minus_left.agg(['mean','sem']).to_string(),flush=True)

if __name__=='__main__':main()
