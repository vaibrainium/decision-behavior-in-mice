"""Continuous recorded-onset slope of directional pulse influence, mouse fixed offsets."""
import argparse
import hashlib
import itertools
import json
from pathlib import Path
from types import SimpleNamespace
import numpy as np
import pandas as pd
from scipy.optimize import least_squares
from scipy.special import expit,xlogy
from scipy import stats
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from scripts.paper.reproduce_pulse_time_notebook import VALID
from scripts.paper.style import RC

CENTER=.15;SCALE=.2
TAIL=['common_pulse_offset','common_time_offset','direction_offset','direction_time_offset','beta_control','common_pulse_slope','common_time_slope','direction_slope','direction_time_slope','lapse','gamma']


def prepare(cells,mice,center=CENTER):
    mi=pd.Categorical(cells.mouse,categories=mice).codes
    if np.any(mi<0):raise ValueError('Unknown mouse label')
    d=cells.direction.to_numpy(dtype=float);P=(d!=0).astype(float);x=np.where(P,(cells.onset_s.to_numpy()-center)/SCALE,0.)
    XA=np.column_stack([np.eye(len(mice))[mi],P,P*x,d,d*x]);XB=np.column_stack([np.ones(len(d)),P,P*x,d,d*x])
    return SimpleNamespace(cells=cells,mice=mice,mi=mi,XA=XA,XB=XB,c=cells.coherence_pct.to_numpy(),n=cells.n.to_numpy(),k=cells.k.to_numpy(),y=cells.y.to_numpy(),M=len(mice))


def model(theta,data):
    K=data.M+4;A=data.XA@theta[:K];B=data.XB@theta[K:K+5];z=expit(B*(data.c+A));amp=1-theta[-2]-theta[-1];p=theta[-2]+amp*z;f=amp*z*(1-z)
    J=np.column_stack([(f*B)[:,None]*data.XA,(f*(data.c+A))[:,None]*data.XB,1-z,-z])
    return p,J


def residual_jac(theta,data,objective):
    p,J=model(theta,data)
    if objective=='wls':return np.sqrt(data.n)*(p-data.y),np.sqrt(data.n)[:,None]*J
    p=np.clip(p,1e-12,1-1e-12);dev=np.maximum(0,2*(xlogy(data.k,data.k/(data.n*p))+xlogy(data.n-data.k,(data.n-data.k)/(data.n*(1-p)))))
    r=np.sign(p-data.y)*np.sqrt(dev);w=np.sqrt(data.n/(p*(1-p)));valid=dev>1e-8;w[valid]=np.abs(data.n[valid]*p[valid]-data.k[valid])/(p[valid]*(1-p[valid])*np.sqrt(dev[valid]))
    return r,w[:,None]*J


def fit(data,objective,seed,quick=False):
    M=data.M;bounds=(np.r_[np.repeat(-30.,M+9),0.,0.],np.r_[np.repeat(30.,M+9),.4,.4]);starts=[seed]
    if quick:
        neutral=seed.copy();neutral[M+3]=0;starts.append(neutral)
    else:
        neutral=seed.copy();neutral[M+2:M+4]=0;starts.append(neutral)
        for w0,wT,b0 in itertools.product([-15,15],[-5,5],[.03,.07]):
            q=seed.copy();q[M+2:M+4]=[w0,wT];q[M+4]=b0;starts.append(q)
    runs=[];attempts=[]
    for seed in starts:
        cache={}
        def get(q):
            if 'q' not in cache or not np.array_equal(q,cache['q']):cache.update(q=q.copy(),value=residual_jac(q,data,objective))
            return cache['value']
        r=least_squares(lambda q:get(q)[0],np.clip(seed,*bounds),jac=lambda q:get(q)[1],bounds=bounds,x_scale='jac',max_nfev=2000,ftol=1e-10,xtol=1e-10,gtol=1e-8)
        attempts.append({'success':bool(r.success),'cost':float(r.cost),'nfev':int(r.nfev),'optimality':float(r.optimality),'theta':r.x.tolist()})
        if r.success and np.isfinite(r.cost):runs.append(r)
    if not runs:raise RuntimeError('No successful continuous-time fit')
    best=min(runs,key=lambda r:r.cost);return SimpleNamespace(theta=best.x,cost=best.cost,attempts=attempts,bounds=bounds,optimality=best.optimality)


def score(theta,data,objective):
    p,J=model(theta,data);w=data.n*(p-data.y)
    if objective=='binomial':w/=p*(1-p)
    return w[:,None]*J


def covariance(theta,data,objective,step_scale=1e-5):
    columns=[]
    for j in range(len(theta)):
        step=step_scale*max(1,abs(theta[j]));up=theta.copy();down=theta.copy();up[j]+=step;down[j]-=step;columns.append((score(up,data,objective).sum(axis=0)-score(down,data,objective).sum(axis=0))/(2*step))
    H=np.column_stack(columns);H=(H+H.T)/2;S=np.stack([score(theta,data,objective)[data.mi==j].sum(axis=0) for j in range(data.M)])
    influence=np.linalg.solve(H,S.T);G=data.M;N=int(data.n.sum());K=len(theta);V=G/(G-1)*(N-1)/(N-K)*(influence@influence.T)
    return V,H,S


def slope_test(theta,V,M,dataset,objective,method):
    effect=theta[M+3]/SCALE;se=np.sqrt(V[M+3,M+3])/SCALE;crit=stats.t.ppf(.975,M-1);t=effect/se
    return {'dataset':dataset,'objective':objective,'uncertainty':method,'n_mice':M,'effect_per_second':effect,'effect_per_100ms':effect*.1,'se_per_100ms':se*.1,'ci_lo_per_100ms':(effect-crit*se)*.1,'ci_hi_per_100ms':(effect+crit*se)*.1,'t_statistic':t,'df':M-1,'p_two_sided':2*stats.t.sf(abs(t),M-1),'primary_test':'directional influence time slope =0'}


def main():
    parser=argparse.ArgumentParser(__doc__);parser.add_argument('--eligible',type=Path,required=True);parser.add_argument('--previous',type=Path,required=True);parser.add_argument('--output',type=Path,required=True);a=parser.parse_args();a.output.mkdir(parents=True,exist_ok=False)
    v=pd.read_csv(VALID).rename(columns={'subject_id':'mouse'});v=v[v.pulse_type.abs()<=2].copy();v['direction']=np.sign(v.pulse_type);v['onset_s']=v.pulse_onset.where(v.direction!=0,0.);v['coherence_pct']=v.signed_coherence;v['right']=v.choice
    e=pd.read_csv(a.eligible);e=e[e.onset_stratum.isin(['early','middle'])].copy();e['onset_s']=e.onset_s.where(e.direction!=0,0.)
    previous=pd.read_csv(a.previous/'coefficients.csv');allcoefs=[];tests=[];diagnostics=[];jack=[];allattempts=[];curve=[]
    for dataset,trials in [('restricted',e),('original_selection',v)]:
        assert np.isfinite(trials.onset_s).all();cells=trials.groupby(['mouse','direction','onset_s','coherence_pct'],as_index=False).right.agg(k='sum',n='size');cells['y']=cells.k/cells.n;mice=sorted(cells.mouse.unique());data=prepare(cells,mice);M=len(mice);assert M==10
        cells.to_csv(a.output/f'{dataset}_cells.csv',index=False);trials[trials.direction!=0].groupby('mouse').onset_s.agg(['size','min','median','max']).to_csv(a.output/f'{dataset}_onset_support.csv')
        old=previous[(previous.dataset==dataset)&(previous.objective=='wls')].set_index('parameter').estimate
        spacing=.23338-.05001;tc=1+(CENTER-.05001)/spacing;scale=SCALE/spacing
        seed=np.r_[[old[f'alpha_baseline_{m}'] for m in mice],old.alpha_time*tc,old.alpha_time*scale,old.alpha_direction+old.alpha_direction_time*tc,old.alpha_direction_time*scale,old.beta_control,old.beta_time*tc,old.beta_time*scale,old.beta_direction+old.beta_direction_time*tc,old.beta_direction_time*scale,old.lapse,old.gamma]
        for objective in ['wls','binomial']:
            result=fit(data,objective,seed);theta=result.theta;V,H,S=covariance(theta,data,objective);np.save(a.output/f'{dataset}_{objective}_covariance.npy',V);np.save(a.output/f'{dataset}_{objective}_score_hessian.npy',H)
            names=[f'baseline_{m}' for m in mice]+TAIL
            pd.DataFrame(S,index=mice,columns=names).to_csv(a.output/f'{dataset}_{objective}_cluster_scores.csv')
            for name,value,se in zip(names,theta,np.sqrt(np.diag(V))):allcoefs.append({'dataset':dataset,'objective':objective,'parameter':name,'estimate_internal':value,'cluster_se_internal':se,'raw_t_p':2*stats.t.sf(abs(value/se),M-1)})
            for j,row in enumerate(result.attempts):allattempts.append({'dataset':dataset,'objective':objective,'start':j,**row})
            tests.append(slope_test(theta,V,M,dataset,objective,'mouse_cluster_observed_Hessian_CR1'))
            p,J=model(theta,data);cells.assign(predicted=p).to_csv(a.output/f'{dataset}_{objective}_predictions.csv',index=False)
            bound=np.isclose(theta,result.bounds[0],atol=1e-6)|np.isclose(theta,result.bounds[1],atol=1e-6)
            B=data.XB@theta[M+4:M+9];diagnostics.append({'dataset':dataset,'objective':objective,'n_trials':len(trials),'n_cells':len(cells),'n_parameters':len(theta),'cost':result.cost,'n_starts':len(result.attempts),'n_success':sum(r['success'] for r in result.attempts),'optimality':result.optimality,'bound_parameters':','.join(np.array(names)[bound]),'min_hessian_eigenvalue':float(np.linalg.eigvalsh(H).min()),'hessian_condition':float(np.linalg.cond(H)),'all_observed_slopes_positive':bool((B>0).all())})
            if objective=='wls':
                omitted_shared=[]
                for omitted in mice:
                    ms=[m for m in mice if m!=omitted];z=cells[cells.mouse!=omitted];prepared=prepare(z,ms);warm=np.r_[[theta[mice.index(m)] for m in ms],theta[M:]];rr=fit(prepared,objective,warm,quick=True);omitted_shared.append(rr.theta[len(ms):]);jack.append({'dataset':dataset,'omitted':omitted,'slope_per_100ms':rr.theta[len(ms)+3]/SCALE*.1,'cost':rr.cost})
                samples=np.array(omitted_shared);center=samples-samples.mean(axis=0);C=(M-1)/M*center.T@center;full=np.zeros_like(V);full[M:,M:]=C;tests.append(slope_test(theta,full,M,dataset,objective,'mouse_cluster_jackknife'))
                seed=theta
            support=trials.loc[trials.direction!=0,'onset_s'];grid=np.linspace(support.min(),support.max(),201)
            for t in grid:
                contrast=np.zeros(len(theta));contrast[M+2]=1;contrast[M+3]=(t-CENTER)/SCALE;w=float(contrast@theta);se=float(np.sqrt(contrast@V@contrast));margin=stats.t.ppf(.975,M-1)*se;curve.append({'dataset':dataset,'objective':objective,'onset_s':t,'pulse_influence':w,'ci_lo':w-margin,'ci_hi':w+margin})
            print(dataset,objective,'primary slope/100ms',tests[-1]['effect_per_100ms'],'complete',flush=True)
    coefficients=pd.DataFrame(allcoefs);test=pd.DataFrame(tests);curves=pd.DataFrame(curve);coefficients.to_csv(a.output/'coefficients.csv',index=False);test.to_csv(a.output/'primary_slope_tests.csv',index=False);pd.DataFrame(diagnostics).to_csv(a.output/'fit_diagnostics.csv',index=False);pd.DataFrame(jack).to_csv(a.output/'leave_one_mouse_slopes.csv',index=False);curves.to_csv(a.output/'pulse_influence_curves.csv',index=False);(a.output/'optimizer_starts.json').write_text(json.dumps(allattempts,indent=2)+'\n')
    for dataset in ['restricted','original_selection']:
        z=curves[(curves.dataset==dataset)&(curves.objective=='wls')];row=test[(test.dataset==dataset)&(test.objective=='wls')&(test.uncertainty=='mouse_cluster_observed_Hessian_CR1')].iloc[0]
        with plt.rc_context(RC):
            fig,ax=plt.subplots(figsize=(5,3.4),layout='constrained');ax.fill_between(z.onset_s*1000,z.ci_lo,z.ci_hi,color='#0072B2',alpha=.15,lw=0);ax.plot(z.onset_s*1000,z.pulse_influence,c='#0072B2',lw=1.3)
            ax.axhline(0,c='.65',ls=':',lw=.7);ax.set(xlabel='Recorded pulse-onset time (ms)',ylabel='Directional pulse influence w (% coherence)',title='Continuous onset-time slope of pulse influence')
            ax.text(.03,.04,f'Slope per 100 ms: {row.effect_per_100ms:.2f} [{row.ci_lo_per_100ms:.2f}, {row.ci_hi_per_100ms:.2f}]\nTwo-sided mouse-cluster t(9): p = {row.p_two_sided:.3f}',transform=ax.transAxes,fontsize=7)
            fig.suptitle(f'{dataset.replace("_"," ")}: joint model, 10 mouse baseline offsets\nLine: fitted directional influence; shading: pointwise 95% cluster intervals',fontsize=8)
            for ext in ['png','pdf','svg']:fig.savefig(a.output/f'{dataset}_continuous_time.{ext}',dpi=250)
            plt.close(fig)
    manifest={'model':'A=u_mouse+aP*P+aT*P*x+d*(w0+wT*x); B=b0+bP*P+bT*P*x+d*(v0+vT*x); p=L+(1-L-G)*logistic(B*(coherence+A))','time':'x=(recorded_onset_s-.15)/.2 for pulses; control x=P=d=0. Pulse-presence nuisance terms preserve center invariance.','primary':'One exploratory two-sided wT=0 test, report wT/.2 per second and scaled per100ms. No multiplicity adjustment for single primary; other coefficient p values descriptive.','inference':'Full observed score-Hessian mouse-cluster CR1 covariance, t9; WLS cluster jackknife sensitivity;10 clusters approximate','objectives':'Notebook trial-count WLS primary on exact continuous-onset cells; binomial sensitivity. Original selection sensitivity separately labeled. No permanent omissions.','support':'Earlier stages only, same10 mice. Actual onset values are discrete in UW and spread in UCLA; line assumes linear influence across windows.','weights':'Trial weighted, common pulse/slopes/asymptotes with mouse-specific baseline offsets','source_hashes':{str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in [VALID,a.eligible,a.previous/'coefficients.csv',Path(__file__)]}}
    (a.output/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n');print(test.to_string(index=False),flush=True)

if __name__=='__main__':main()
