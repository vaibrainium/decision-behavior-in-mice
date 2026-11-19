"""Notebook-shaped joint model with categorical mouse offsets and clustered regression tests."""
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
from scripts.paper.reproduce_pulse_time_notebook import NOTEBOOK,VALID,notebook_fit
from scripts.paper.pulse_time_per_mouse_joint import holm
from scripts.paper.style import RC,LEFT_COLOR,RIGHT_COLOR

SHARED=['alpha_direction','alpha_time','alpha_direction_time','beta_control','beta_direction','beta_time','beta_direction_time','lapse','gamma']


def model(theta,cells,mice):
    M=len(mice);mi=pd.Categorical(cells.mouse,categories=mice).codes
    c=cells.coherence_pct.to_numpy();d=cells.direction.to_numpy();t=cells.stage.to_numpy();dt=d*t
    a=theta[mi]+theta[M]*d+theta[M+1]*t+theta[M+2]*dt
    b=theta[M+3]+theta[M+4]*d+theta[M+5]*t+theta[M+6]*dt
    z=expit(b*(c+a));amp=1-theta[-2]-theta[-1];p=theta[-2]+amp*z
    slope=amp*z*(1-z);J=np.zeros((len(c),len(theta)));J[np.arange(len(c)),mi]=slope*b
    J[:,M:M+3]=(slope*b)[:,None]*np.column_stack([d,t,dt])
    J[:,M+3:M+7]=(slope*(c+a))[:,None]*np.column_stack([np.ones(len(c)),d,t,dt])
    J[:,-2]=1-z;J[:,-1]=-z
    return p,J


def residual_jac(theta,cells,mice,objective):
    p,J=model(theta,cells,mice);n=cells.n.to_numpy();y=cells.y.to_numpy();k=cells.k.to_numpy()
    if objective=='wls':return np.sqrt(n)*(p-y),np.sqrt(n)[:,None]*J
    p=np.clip(p,1e-12,1-1e-12)
    dev=np.maximum(0,2*(xlogy(k,k/(n*p))+xlogy(n-k,(n-k)/(n*(1-p)))))
    res=np.sign(p-y)*np.sqrt(dev);deriv=np.sqrt(n/(p*(1-p)))
    stable=dev>1e-8;deriv[stable]=np.abs(n[stable]*p[stable]-k[stable])/(p[stable]*(1-p[stable])*np.sqrt(dev[stable]))
    return res,deriv[:,None]*J


def fit(cells,mice,objective,seed,quick=False):
    M=len(mice);bounds=(np.array([-30.]*(M+7)+[0.,0.]),np.array([30.]*(M+7)+[.4,.4]))
    starts=[seed]
    for shift,beta in itertools.product([-15.,0.,15.],[.025,.07]):
        q=seed.copy();q[M:M+3]=[shift,0,0];q[M+3:M+7]=[beta,0,0,0];q[-2:]=[.15,.13];starts.append(q)
    if quick:starts=starts[:1]+starts[3:4]
    solved=[]
    for q in starts:
        res=least_squares(lambda x:residual_jac(x,cells,mice,objective)[0],np.clip(q,*bounds),jac=lambda x:residual_jac(x,cells,mice,objective)[1],bounds=bounds,x_scale='jac',max_nfev=2500,ftol=1e-11,xtol=1e-11,gtol=1e-9)
        if res.success and np.isfinite(res.cost):solved.append(res)
    if not solved:raise RuntimeError('No converged fit')
    best=min(solved,key=lambda r:r.cost);return SimpleNamespace(theta=best.x,cost=best.cost,n_success=len(solved),n_starts=len(starts),optimality=best.optimality,bounds=bounds)


def cluster_cov(theta,cells,mice,objective):
    p,J=model(theta,cells,mice);n=cells.n.to_numpy();y=cells.y.to_numpy();G=len(mice);K=len(theta);N=int(cells.n.sum())
    if objective=='wls':score=(n*(p-y))[:,None]*J;bread=J.T@(n[:,None]*J)
    else:
        p=np.clip(p,1e-12,1-1e-12);score=(n*(p-y)/(p*(1-p)))[:,None]*J;bread=J.T@((n/(p*(1-p)))[:,None]*J)
    S=pd.DataFrame(score).assign(mouse=cells.mouse.to_numpy()).groupby('mouse').sum().reindex(mice).to_numpy()
    influence=np.linalg.solve(bread,S.T);correction=G/(G-1)*(N-1)/(N-K);cov=correction*(influence@influence.T)
    return cov,S,bread,correction


def infer(theta,cov,M,G,method,dataset,objective):
    rows=[]
    for block,indices in [('alpha_directional',[M,M+2]),('beta_directional',[M+4,M+6])]:
        b=theta[indices];V=cov[np.ix_(indices,indices)];F=float(b@np.linalg.solve(V,b)/2)
        rows.append({'dataset':dataset,'objective':objective,'uncertainty':method,'family':'omnibus2','test':block,'df_num':2,'df_denom':G-1,'statistic_F':F,'p_raw':stats.f.sf(F,2,G-1)})
    adjusted=holm([r['p_raw'] for r in rows])
    for r,p in zip(rows,adjusted):r['p_holm']=p
    follow=[]
    for stage in [1,2]:
        c=np.zeros(len(theta));c[M]=2;c[M+2]=2*stage;effect=float(c@theta);se=float(np.sqrt(c@cov@c));t=effect/se;margin=stats.t.ppf(.975,G-1)*se
        follow.append({'dataset':dataset,'objective':objective,'uncertainty':method,'family':'alpha_followup2','test':f'alpha_right_minus_left_stage{stage}','estimate':effect,'se':se,'ci_lo':effect-margin,'ci_hi':effect+margin,'df_denom':G-1,'statistic_t':t,'p_raw':2*stats.t.sf(abs(t),G-1)})
    for r,p in zip(follow,holm([r['p_raw'] for r in follow])):r['p_holm']=p
    return rows+follow


def main():
    parser=argparse.ArgumentParser(__doc__);parser.add_argument('--eligible',type=Path,required=True);parser.add_argument('--output',type=Path,required=True);a=parser.parse_args();a.output.mkdir(parents=True,exist_ok=False)
    raw=pd.read_csv(VALID).rename(columns={'subject_id':'mouse'});raw=raw[raw.pulse_type.abs()<=2]
    e=pd.read_csv(a.eligible);e=e[e.onset_stratum.isin(['early','middle'])];e=e.assign(pulse_type=e.direction*e.onset_stratum.map({'early':1,'middle':2}),signed_coherence=e.coherence_pct,choice=e.right)
    nb=json.loads(NOTEBOOK.read_text());allcoef=[];alltests=[];fitinfo=[];allderived=[];checks=[];jackrows=[]
    for dataset,data in [('restricted',e),('original_selection',raw)]:
        data=data.assign(direction=np.sign(data.pulse_type),stage=data.pulse_type.abs(),coherence_pct=data.signed_coherence)
        cells=data.groupby(['mouse','direction','stage','coherence_pct'],as_index=False).choice.agg(k='sum',n='size');cells['y']=cells.k/cells.n;mice=sorted(cells.mouse.unique());M=len(mice);assert M==10
        q0=notebook_fit(data,nb)['params'];seed=np.r_[np.repeat(q0[0],M),q0[1:]];cells.to_csv(a.output/f'{dataset}_cells.csv',index=False)
        for objective in ['wls','binomial']:
            result=fit(cells,mice,objective,seed);theta=result.theta;cov,S,H,correction=cluster_cov(theta,cells,mice,objective);names=[f'alpha_baseline_{m}' for m in mice]+SHARED
            np.save(a.output/f'{dataset}_{objective}_cluster_cov.npy',cov);np.save(a.output/f'{dataset}_{objective}_bread.npy',H);pd.DataFrame(S,index=mice,columns=names).to_csv(a.output/f'{dataset}_{objective}_cluster_scores.csv')
            pred,J=model(theta,cells,mice);cells.assign(predicted=pred).to_csv(a.output/f'{dataset}_{objective}_predictions.csv',index=False)
            # Independent central finite differences of probability Jacobian.
            numeric=[]
            for j in range(len(theta)):
                step=1e-6*max(1,abs(theta[j]));up=theta.copy();down=theta.copy();up[j]+=step;down[j]-=step;numeric.append((model(up,cells,mice)[0]-model(down,cells,mice)[0])/(2*step))
            jac_error=float(np.max(np.abs(np.column_stack(numeric)-J)));assert jac_error<1e-5
            beta_actual=theta[M+3]+theta[M+4]*cells.direction+theta[M+5]*cells.stage+theta[M+6]*cells.direction*cells.stage
            fitinfo.append({'dataset':dataset,'objective':objective,'n_trials':len(data),'n_cells':len(cells),'n_mice':M,'n_parameters':len(theta),'cost':result.cost,'n_starts':result.n_starts,'n_success':result.n_success,'optimality':result.optimality,'bread_condition':float(np.linalg.cond(H)),'CR1_factor':correction,'bound_parameters':','.join(np.asarray(names)[np.isclose(theta,result.bounds[0],atol=1e-6)|np.isclose(theta,result.bounds[1],atol=1e-6)]),'all_observed_slopes_positive':bool((beta_actual>0).all())})
            checks.append({'dataset':dataset,'objective':objective,'probability_jacobian_max_error':jac_error})
            for j,name in enumerate(names):
                se=np.sqrt(cov[j,j]);allcoef.append({'dataset':dataset,'objective':objective,'parameter':name,'estimate':theta[j],'cluster_se':se,'df':M-1,'conditional_raw_p':2*stats.t.sf(abs(theta[j]/se),M-1) if se>0 else np.nan})
            alltests.extend(infer(theta,cov,M,M,'cluster_CR1',dataset,objective))
            if objective=='wls':
                shared=[]
                for omitted in mice:
                    ms=[m for m in mice if m!=omitted];z=cells[cells.mouse!=omitted];warm=np.r_[[theta[mice.index(m)] for m in ms],theta[M:]]
                    rr=fit(z,ms,objective,warm,quick=True);shared.append(rr.theta[len(ms):]);jackrows.append({'dataset':dataset,'omitted':omitted,**dict(zip(SHARED,rr.theta[len(ms):]))})
                shared=np.array(shared);center=shared-shared.mean(axis=0);V=(M-1)/M*(center.T@center);np.save(a.output/f'{dataset}_wls_jackknife_shared_cov.npy',V)
                padded=np.zeros_like(cov);padded[M:,M:]=V;alltests.extend(infer(theta,padded,M,M,'cluster_jackknife',dataset,objective))
            for stage in [1,2]:
                for direction in [-1,1]:
                    ca=np.r_[np.repeat(1/M,M),direction,stage,direction*stage,0,0,0,0,0,0];cb=np.r_[np.zeros(M+3),0,direction,stage,direction*stage,0,0]
                    for parameter,c in [('alpha_full',ca),('beta_change',cb)]:
                        effect=float(c@theta);se=float(np.sqrt(c@cov@c));margin=stats.t.ppf(.975,M-1)*se;allderived.append({'dataset':dataset,'objective':objective,'stage':stage,'direction':direction,'parameter':parameter,'estimate':effect,'se':se,'ci_lo':effect-margin,'ci_hi':effect+margin})
            print(dataset,objective,'cost',result.cost,'complete',flush=True)
            if objective=='wls':seed=theta
    coefficients=pd.DataFrame(allcoef);tests=pd.DataFrame(alltests);derived=pd.DataFrame(allderived);coefficients.to_csv(a.output/'coefficients.csv',index=False);tests.to_csv(a.output/'regression_tests.csv',index=False);derived.to_csv(a.output/'display_values.csv',index=False);pd.DataFrame(fitinfo).to_csv(a.output/'fit_diagnostics.csv',index=False);pd.DataFrame(jackrows).to_csv(a.output/'leave_one_mouse_fits.csv',index=False)
    for dataset in ['restricted','original_selection']:
        z=derived[(derived.dataset==dataset)&(derived.objective=='wls')]
        with plt.rc_context(RC):
            fig,axes=plt.subplots(1,2,figsize=(7.5,3.3),layout='constrained')
            for ax,param,label in zip(axes,['alpha_full','beta_change'],['α: full additive coherence offset (% coherence)','Δβ: slope change from control (per % coherence)']):
                for direction,color,text in [(-1,LEFT_COLOR,'Leftward pulse'),(1,RIGHT_COLOR,'Rightward pulse')]:
                    q=z[(z.parameter==param)&(z.direction==direction)].sort_values('stage');ax.plot(q.stage,q.estimate,'o-',c=color,label=text);ax.vlines(q.stage,q.ci_lo,q.ci_hi,color=color);ax.plot(q.stage,q.ci_lo,'_',c=color);ax.plot(q.stage,q.ci_hi,'_',c=color)
                ax.axhline(0,c='.7',ls=':',lw=.7);ax.set(xticks=[1,2],xticklabels=['Early','Middle'],xlabel='Pulse stage',ylabel=label)
            axes[0].legend();fig.suptitle(f'Joint model with categorical mouse baseline offsets: {dataset.replace("_"," ")}\nShared pulse coefficients; mouse-cluster 95% intervals, t(9)',fontsize=8)
            for ext in ['png','pdf','svg']:fig.savefig(a.output/f'{dataset}_mouse_fixed_effects.{ext}',dpi=250)
            plt.close(fig)
    manifest={'model':'Notebook probability equation with10 categorical mouse additive offsets replacing alpha1; remaining9 coefficients shared, including asymptotes','main_objective':'trial-count WLS, identical notebook objective conditional on mouse; binomial likelihood sensitivity separately labeled','n_primary_trials':len(e),'n_original_sensitivity_trials':len(raw),'timing':'Early/middle only for common10-mouse support; no late extrapolation','inference':'Mouse-cluster CR1 nonlinear sandwich with Gauss-Newton/Fisher bread; t9/F2,9 approximate with only10 clusters. WLS cluster-delete jackknife sensitivity','tests':'2 primary omnibus blocks alpha(direction, direction*time), beta(direction, direction*time), Holm2; separate2 exploratory early/middle alpha direction contrasts, Holm2. Do not choose inference method by significance.','weighting':'Trial-count weighted conditional fit; mouse fixed effects do not imply equal mouse pulse weights or random pulse slopes','verification':checks,'source_hashes':{str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in [VALID,NOTEBOOK,a.eligible,Path(__file__)]}}
    (a.output/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n');print(tests.to_string(index=False),flush=True)

if __name__=='__main__':main()
