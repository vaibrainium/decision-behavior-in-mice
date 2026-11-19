"""Notebook joint pulse-time model fitted within each mouse; subject-level exploratory comparisons."""
import argparse
import itertools
import json
import hashlib
from pathlib import Path
import warnings
import numpy as np
import pandas as pd
from scipy.optimize import curve_fit
from scipy import stats
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from scripts.paper.reproduce_pulse_time_notebook import notebook_fit, PARAMS, NOTEBOOK, VALID
from scripts.paper.style import RC,LEFT_COLOR,RIGHT_COLOR

BOUNDS=([-30.]*8+[0.,0.],[30.]*8+[.4,.4])


def holm(values):
    values=np.asarray(values);order=np.argsort(values);adjusted=np.empty(len(values));run=0.
    for j,k in enumerate(order):run=max(run,(len(values)-j)*values[k]);adjusted[k]=min(run,1.)
    return adjusted


def test_difference(values):
    x=np.asarray(values);n=len(x);mean=x.mean();sd=x.std(ddof=1);se=sd/np.sqrt(n)
    signs=np.array(list(itertools.product([-1,1],repeat=n)))
    p=np.mean(np.abs(signs@x/n)>=abs(mean)-1e-12);margin=stats.t.ppf(.975,n-1)*se
    return dict(n_mice=n,mean=mean,median=np.median(x),sem=se,ci_lo=mean-margin,ci_hi=mean+margin,dz=mean/sd if sd>0 else np.nan,n_positive=int((x>0).sum()),p_exact=p)


def main():
    p=argparse.ArgumentParser(__doc__);p.add_argument('--eligible',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();a.output.mkdir(parents=True,exist_ok=False)
    nb=json.loads(NOTEBOOK.read_text());raw=pd.read_csv(VALID).rename(columns={'subject_id':'mouse'})
    e=pd.read_csv(a.eligible);e=e.assign(pulse_type=e.direction*e.onset_stratum.map({'early':1,'middle':2,'late':3}),signed_coherence=e.coherence_pct,choice=e.right)
    attempts=[];coefs=[];diagnostics=[];derived=[];predictions=[];observed=[]
    for dataset,data in [('original_notebook',raw),('scheduled_eligible_sensitivity',e)]:
        pooled=notebook_fit(data,nb)['params']
        for mouse,z in data.groupby('mouse'):
            native=notebook_fit(z,nb);func=native['fit_function'];X,y,sigma=native['x'],native['y'],native['sigma'];w=1/sigma
            def sse(q):return float(np.sum(((func(X,*q)-y)*w)**2))
            q0=native['params'];native_error=sse(q0);solved=[(native_error,q0,native['covariance'],0)]
            starts=[q0,pooled]+[np.array([0,alpha2,0,alpha4,beta,0,0,0,.15,.13]) for alpha2,alpha4,beta in itertools.product([-15,0,15],[-5,0,5],[.02,.05,.1])]
            for index,start in enumerate(starts):
                if index==0:q,cov=q0,native['covariance'];error=native_error;success=True;failure=''
                else:
                    try:
                        with warnings.catch_warnings(record=True):
                            warnings.simplefilter('always');q,cov=curve_fit(func,X,y,p0=np.clip(start,*BOUNDS),bounds=BOUNDS,sigma=sigma,absolute_sigma=False,max_nfev=3000,ftol=1e-10,xtol=1e-10,gtol=1e-10)
                        error=sse(q);success=bool(np.isfinite(error) and np.all(np.isfinite(q)))
                        if success:solved.append((error,q,cov,index))
                        failure=''
                    except (RuntimeError,ValueError,FloatingPointError) as exc:q=np.full(10,np.nan);error=np.nan;success=False;failure=str(exc)
                attempts.append({'dataset':dataset,'mouse':mouse,'start':index,'success':success,'weighted_sse':error,'error':failure,**dict(zip(PARAMS,q))})
            error,q,cov,selected=min(solved,key=lambda s:s[0]);assert error<=native_error+1e-9
            np.save(a.output/f'{dataset}_{mouse}_covariance.npy',cov)
            bound=np.isclose(q,BOUNDS[0],atol=1e-6,rtol=0)|np.isclose(q,BOUNDS[1],atol=1e-6,rtol=0)
            cond=float(np.linalg.cond(cov)) if np.isfinite(cov).all() else np.inf
            rows=pd.DataFrame({'dataset':dataset,'mouse':mouse,'coherence_pct':X[0],'direction':X[1],'stage':X[2],'p_right':y,'n_trials':np.rint(1/sigma**2).astype(int),'predicted':func(X,*q)})
            assert rows.n_trials.sum()==len(z);observed.append(rows)
            actual_stages=sorted(set(abs(z.pulse_type))-set([0]))
            negative=[]
            for t in actual_stages:
                for d in [-1,1]:
                    ca=np.array([0,d,t,d*t,0,0,0,0,0,0]);full=ca.copy();full[0]=1;cb=np.array([0,0,0,0,0,d,t,d*t,0,0])
                    alpha=full@q;beta=q[4]+cb@q;native_alpha=full@q0
                    if beta<=0:negative.append(f'{d}:{t}')
                    derived.append({'dataset':dataset,'mouse':mouse,'stage':int(t),'direction':d,'alpha_full':alpha,'alpha_original_display':ca@q,'alpha_native_midpoint':-alpha,'beta_full':beta,'beta_change':cb@q,'alpha_conditional_se':float(np.sqrt(max(0,full@cov@full))),'alpha_native_start_full':native_alpha,'alpha_original_start_display':ca@q0,'beta_native_start_full':q0[4]+cb@q0})
                    # Save curves within actual observed coherence support only.
                    points=rows[(rows.stage==t)&(rows.direction==d)];grid=np.linspace(points.coherence_pct.min(),points.coherence_pct.max(),201);xx=np.vstack([grid,np.repeat(d,len(grid)),np.repeat(t,len(grid))]);predictions.append(pd.DataFrame({'dataset':dataset,'mouse':mouse,'stage':t,'direction':d,'coherence_pct':grid,'p_fit':func(xx,*q)}))
            for i,k in enumerate(PARAMS):coefs.append({'dataset':dataset,'mouse':mouse,'parameter':k,'estimate':q[i],'native_estimate':q0[i],'at_bound':bool(bound[i])})
            diagnostics.append({'dataset':dataset,'mouse':mouse,'n_trials':len(z),'n_cells':len(y),'n_stages':len(actual_stages),'native_sse':native_error,'selected_sse':error,'improvement':native_error-error,'selected_start':selected,'n_starts':len(starts),'n_success':len(solved),'any_bound':bool(bound.any()),'bound_parameters':','.join(np.asarray(PARAMS)[bound]),'covariance_condition':cond,'nonpositive_observed_slopes':','.join(negative)})
            print(dataset,mouse,'SSE',round(native_error,5),'->',round(error,5),'bounds',','.join(np.asarray(PARAMS)[bound]),flush=True)
    pd.DataFrame(attempts).to_csv(a.output/'all_starts.csv',index=False);coef=pd.DataFrame(coefs);coef.to_csv(a.output/'coefficients.csv',index=False);diag=pd.DataFrame(diagnostics);diag.to_csv(a.output/'diagnostics.csv',index=False)
    derived=pd.DataFrame(derived);derived.to_csv(a.output/'mouse_stage_parameters.csv',index=False);obs=pd.concat(observed);obs.to_csv(a.output/'observed_cells.csv',index=False);pred=pd.concat(predictions);pred.to_csv(a.output/'fitted_curves.csv',index=False)
    contrasts=[];tests=[]
    for dataset,z in derived.groupby('dataset'):
        for t in [1,2,3]:
            for parameter in ['alpha_full','beta_full']:
                pairs=z[z.stage==t].pivot(index='mouse',columns='direction',values=parameter).dropna();dif=pairs[1]-pairs[-1]
                for mouse,value in dif.items():contrasts.append({'dataset':dataset,'mouse':mouse,'stage':t,'parameter':parameter,'right_minus_left':value})
                tests.append({'dataset':dataset,'family':'direction_6','contrast':f'{parameter}:right_minus_left:stage{t}',**test_difference(dif)})
        for parameter in ['alpha_full','beta_full']:
            zz=pd.DataFrame([row for row in contrasts if row['dataset']==dataset and row['parameter']==parameter]);wide=zz.pivot(index='mouse',columns='stage',values='right_minus_left');dif=wide[2]-wide[1]
            tests.append({'dataset':dataset,'family':'timing_2','contrast':f'{parameter}:directional_difference_middle_minus_early',**test_difference(dif)})
    tests=pd.DataFrame(tests)
    for _,ix in tests.groupby(['dataset','family']).groups.items():tests.loc[ix,'p_holm']=holm(tests.loc[ix,'p_exact'])
    tests.to_csv(a.output/'group_tests.csv',index=False);pd.DataFrame(contrasts).to_csv(a.output/'mouse_direction_contrasts.csv',index=False)
    groups=[]
    for dataset,z in derived.groupby('dataset'):
        for population,stages in [('all10_early_middle',[1,2]),('same6_all_times',[1,2,3])]:
            mice=sorted(z[z.stage==3].mouse.unique()) if population=='same6_all_times' else sorted(z.mouse.unique())
            zz=z[z.mouse.isin(mice)&z.stage.isin(stages)];g=zz.groupby(['stage','direction'])[['alpha_full','alpha_original_display','beta_change']].agg(['mean','sem','count']);g.columns=['_'.join(c) for c in g.columns];g=g.reset_index();g['dataset']=dataset;g['population']=population;groups.append(g)
            if dataset!='original_notebook':continue
            with plt.rc_context(RC):
                fig,axes=plt.subplots(1,2,figsize=(7.5,3.25),layout='constrained')
                for ax,param,label in zip(axes,['alpha_full','beta_change'],['α: full additive coherence offset (% coherence)','Δβ: slope change from control (per % coherence)']):
                    for direction,color,text in [(-1,LEFT_COLOR,'Leftward pulse'),(1,RIGHT_COLOR,'Rightward pulse')]:
                        q=g[g.direction==direction].sort_values('stage');ax.errorbar(q.stage,q[param+'_mean'],yerr=q[param+'_sem'],fmt='o-',c=color,capsize=3,label=text)
                    ax.axhline(0,c='.7',ls=':',lw=.7);ax.set(xticks=stages,xticklabels=[{1:'Early',2:'Middle',3:'Late'}[t] for t in stages],xlabel='Pulse stage',ylabel=label)
                axes[0].legend();fig.suptitle(f'Original joint model fitted separately per mouse: same {len(mice)} mice\nMean ± SEM; notebook offset convention; no individual fits excluded',fontsize=8)
                for ext in ['png','pdf','svg']:fig.savefig(a.output/f'{population}.{ext}',dpi=250)
                plt.close(fig)
    pd.concat(groups).to_csv(a.output/'group_parameters.csv',index=False)
    with plt.rc_context(RC):
        fig,axes=plt.subplots(1,2,figsize=(6.5,3.6),layout='constrained')
        for ax,t in zip(axes,[1,2]):
            z=derived[(derived.dataset=='original_notebook')&(derived.stage==t)].pivot(index='mouse',columns='direction',values='alpha_full').sort_index()
            for i,(mouse,row) in enumerate(z.iterrows()):ax.plot([0,1],[row[-1],row[1]],c='.7',lw=.8);ax.text(1.03,row[1],mouse,fontsize=5)
            ax.scatter(np.zeros(len(z)),z[-1],c=LEFT_COLOR,s=15);ax.scatter(np.ones(len(z)),z[1],c=RIGHT_COLOR,s=15);ax.axhline(0,c='.7',ls=':',lw=.7);ax.set(xticks=[0,1],xticklabels=['Leftward','Rightward'],xlim=(-.15,1.45),ylabel='α: full additive offset (% coherence)',title={1:'Early',2:'Middle'}[t]+' pulse')
        fig.suptitle('Joint per-mouse fits: paired α estimates',fontsize=8)
        for ext in ['png','pdf','svg']:fig.savefig(a.output/f'paired_individual_alpha.{ext}',dpi=250)
        plt.close(fig)
    manifest={'scope':'Joint notebook model fitted per mouse, no separate-direction curve fitting or population-parameter substitution','primary':'original_notebook valid_data response-coded labels, same rows as exact reproduction','sensitivity':'scheduled_eligible_sensitivity current Figure4-type response timing/symmetric labels, includes late exploratory stratum','n_starts':29,'selection':'Native original-start fit retained; pooled-fit seed plus27 starts, minimum same-objective WLS only','alpha':'Full additive offset, notebook coh+A convention; original displayed baseline-omitted and native midpoint alternatives exported','group_tests':'Exact two-sided mouse sign-flip; Holm6 stage×parameter directional contrasts; separate Holm2 early-to-middle directional changes, per dataset. Conditional on fitted coefficients; t95% intervals unadjusted.','source_hashes':{str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in [NOTEBOOK,VALID,a.eligible,Path(__file__)]}}
    (a.output/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n');print(tests.to_string(index=False),flush=True)

if __name__=='__main__':main()
