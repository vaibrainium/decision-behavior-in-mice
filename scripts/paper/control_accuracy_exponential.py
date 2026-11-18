"""Descriptive exponential CAF overlays; equal-mouse trial likelihood and cluster bootstrap."""
import argparse
import hashlib
import json
from pathlib import Path
import numpy as np
import pandas as pd
from scipy.optimize import minimize, check_grad
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from scripts.ddm.fit_mouse_ddm import load_inputs, responded_only
from scripts.paper.control_conditional_accuracy import COLORS, COHERENCES
from scripts.paper.style import RC

BOUNDS=[(1e-6,1-1e-6),(0,1),(np.log(.01),np.log(20))]

def predict(theta,x):
    p0,a,lt=theta
    return p0+(1-p0)*a*(-np.expm1(-x/np.exp(lt)))

def objective(theta,x,y,w):
    p0,a,lt=theta; z=x/np.exp(lt); e=np.exp(-z); f=-np.expm1(-z)
    p=np.clip(predict(theta,x),1e-10,1-1e-10)
    value=-np.sum(w*(y*np.log(p)+(1-y)*np.log1p(-p)))
    deriv=np.array([1-a*f,(1-p0)*f,-(1-p0)*a*e*z])
    return value,deriv@(w*(p-y)/(p*(1-p)))

def fit(x,y,w,warm=None):
    starts=[np.array([.4,.7,np.log(t)]) for t in [.08,.3,1.,5.]] if warm is None else [warm,np.array([.4,.7,np.log(.15)]),np.array([.5,.4,np.log(2.)])]
    results=[minimize(objective,s,args=(x,y,w),jac=True,bounds=BOUNDS,method='L-BFGS-B',options={'ftol':1e-12,'gtol':1e-7,'maxiter':400}) for s in starts]
    successful=[r for r in results if r.success and np.isfinite(r.fun)]
    if not successful: raise RuntimeError('No converged multistart fit')
    return min(successful,key=lambda r:r.fun)

def main():
    parser=argparse.ArgumentParser(__doc__)
    parser.add_argument('--output',type=Path,required=True)
    parser.add_argument('--source',type=Path,default=Path('dissemination/paper_accumulation/draft_2026-11-15/figure3_conditional_accuracy_2026-11-18'))
    parser.add_argument('--bootstrap',type=int,default=200)
    args=parser.parse_args(); args.output.mkdir(parents=True,exist_ok=False)
    inputs=responded_only(load_inputs(Path('/mnt/data/processed/ddm/ddm_inputs_global.npz')))
    rows=np.flatnonzero(inputs['sched_pulse_type']==0)
    v=pd.read_csv('/mnt/data/processed/valid_data.csv').set_index('agg_code').loc[inputs['agg_code'][rows]]
    correct=inputs['choice'][rows]==(v.target.to_numpy()>0)
    np.testing.assert_array_equal(correct,v.outcome.to_numpy().astype(bool))
    trials=pd.DataFrame({'mouse':inputs['subject_id'][rows],'abs_coh':np.rint(abs(inputs['signed_coherence'][rows])*100).astype(int),'rt_s':inputs['rt'][rows],'correct':correct.astype(int)})
    assert len(trials)==14014
    trials.to_csv(args.output/'trials.csv',index=False)
    group=pd.read_csv(args.source/'group_accuracy.csv');group=group[group.source=='data']
    mice=sorted(trials.mouse.unique());rng=np.random.default_rng(89123)
    draws=rng.multinomial(len(mice),np.repeat(1/len(mice),len(mice)),size=args.bootstrap)
    grid=np.linspace(.3,5.,401); curves=[]; parameters=[];bootrows=[];checks=[]
    for coh in COHERENCES:
        t=trials[trials.abs_coh==coh];x=t.rt_s.to_numpy()-.3;y=t.correct.to_numpy()
        ids=pd.Categorical(t.mouse,categories=mice).codes
        n=np.bincount(ids,minlength=len(mice));assert np.all(n>0)
        w=1/n[ids]/len(mice)
        c=np.sum(w*y);const_loss=-np.sum(w*(y*np.log(c)+(1-y)*np.log1p(-c)))
        if coh:
            result=fit(x,y,w);theta=result.x; central=predict(theta,grid-.3)
            error=check_grad(lambda z:objective(z,x,y,w)[0],lambda z:objective(z,x,y,w)[1],np.array([.35,.6,np.log(.4)]))
            direct=-np.sum(w*(y*np.log(predict(theta,x))+(1-y)*np.log1p(-predict(theta,x))))
            assert abs(direct-result.fun)<1e-10 and error<1e-5
            checks.append({'abs_coh':coh,'gradient_error':error,'objective_direct_error':abs(direct-result.fun),'weights_sum':float(w.sum())})
            parameters.append({'abs_coh':coh,'p0':theta[0],'p_inf':theta[0]+(1-theta[0])*theta[1],'tau_s':np.exp(theta[2]),'constant_accuracy':c,'mean_weighted_nll':result.fun,'constant_mean_weighted_nll':const_loss,'n_trials':len(t),'success':result.success})
        else:
            central=np.repeat(c,len(grid));parameters.append({'abs_coh':0,'constant_accuracy':c,'mean_weighted_nll':const_loss,'n_trials':len(t),'success':True})
        predictions=[]
        for b,counts in enumerate(draws):
            wb=w*counts[ids];wb=wb/wb.sum()
            if coh:
                r=fit(x,y,wb,theta);z=r.x;pinf=z[0]+(1-z[0])*z[1];tau=np.exp(z[2]); predictions.append(predict(z,grid-.3))
                bootrows.append({'rep':b,'abs_coh':coh,'p0':z[0],'p_inf':pinf,'tau_s':tau,'tau_at_bound':bool(tau<.01001 or tau>19.999),'success':r.success})
            else:
                cb=np.sum(wb*y);predictions.append(np.repeat(cb,len(grid)));bootrows.append({'rep':b,'abs_coh':0,'constant_accuracy':cb,'success':True})
        lo,hi=np.percentile(predictions,[2.5,97.5],axis=0)
        curves.append(pd.DataFrame({'abs_coh':coh,'rt_s':grid,'fit':central,'bootstrap_lo':lo,'bootstrap_hi':hi}))
        print(f'coherence {coh}: finished {args.bootstrap} cluster resamples',flush=True)
    params=pd.DataFrame(parameters);boots=pd.DataFrame(bootrows);curve=pd.concat(curves,ignore_index=True)
    params.to_csv(args.output/'parameters.csv',index=False);boots.to_csv(args.output/'bootstrap_parameters.csv',index=False);curve.to_csv(args.output/'curves.csv',index=False)
    uncertainty=boots.groupby('abs_coh')[['p0','p_inf','tau_s','constant_accuracy']].quantile([.025,.975]);uncertainty.to_csv(args.output/'parameter_intervals.csv')
    with plt.rc_context(RC):
        for show_ci,name in [(False,'figure3D_exponential'),(True,'exponential_bootstrap_diagnostic')]:
            fig,ax=plt.subplots(figsize=(4.9,3.6),layout='constrained')
            for coh in COHERENCES:
                g=group[group.abs_coh==coh].sort_values('bin');q=curve[curve.abs_coh==coh];color=COLORS[coh]
                ax.plot(g.rt_ms,g['mean'],'o',color=color,ms=3,label=f'{coh}%')
                if not show_ci:ax.fill_between(g.rt_ms,g['mean']-g['sem'],g['mean']+g['sem'],color=color,alpha=.10,lw=0)
                else:ax.fill_between(q.rt_s*1000,q.bootstrap_lo,q.bootstrap_hi,color=color,alpha=.12,lw=0)
                ax.plot(q.rt_s*1000,q['fit'],color=color,lw=1.2)
            ax.axhline(.5,color='.65',ls=':',lw=.7)
            ax.set(xlim=(250,5050),ylim=(0,1.03),xlabel='Reaction time (ms)',ylabel='Probability correct',title='D   Control accuracy: exponential fits',xticks=[500,1500,2500,3500,4500])
            ax.legend(title='|Coherence|',ncol=3,loc='lower left')
            for ext in ['png','pdf','svg']:fig.savefig(args.output/f'{name}.{ext}',dpi=240)
            plt.close(fig)
    manifest={'n_trials':len(trials),'n_mice':len(mice),'bootstrap_reps':args.bootstrap,'seed':89123,'tau_bounds_s':[.01,20.], 'time_anchor_s':.3,'weights':'Each mouse contributes 1/10 within coherence; trials equally weighted within mouse/coherence','intervals':'Pointwise 95% percentile intervals by resampling whole mice; common resampling indices across coherences','equation':'p(t)=p0+(1-p0)*a*(1-exp(-(t-.3)/tau)); 0<=a<=1','scope':'Exploratory descriptive monotonic common curve, no mechanistic interpretation or hypothesis tests','source_script_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'checks':checks}
    (args.output/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    print(params.to_string(index=False),flush=True)

if __name__=='__main__':main()
