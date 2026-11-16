"""Prefix-fitted, pre-choice-filtered bias models on audited mouse chronology.

This is a choice diagnostic. It is not a joint choice/RT DDM or an attention
classifier. The AR(1) model uses a Rouwenhorst finite-state approximation with
the exact stationary variance and one-step correlation of its latent process.
"""
import argparse
import itertools
import json
import time
from pathlib import Path

import numba
import numpy as np
import pandas as pd
from scipy import linalg, optimize, special, stats
from statsmodels.stats.multitest import multipletests

from scripts.behavior.history_dynamics import (
    OUT, RIDGE, acf_table, design, logistic, sha, write_json,
)

ENDPOINTS=['continuous_gain_bits','discrete_gain_bits','discrete_minus_continuous_bits',
           'continuous_rt_alignment','discrete_rt_alignment']


def rouwenhorst(n,rho):
    """Standardized AR(1) grid: variance one and lag-one correlation rho."""
    p=(1+rho)/2
    a=np.array([[p,1-p],[1-p,p]])
    for k in range(3,n+1):
        b=np.zeros((k,k))
        b[:-1,:-1]+=p*a;b[:-1,1:]+=(1-p)*a
        b[1:,:-1]+=(1-p)*a;b[1:,1:]+=p*a
        b[1:-1]/=2
        a=b
    grid=np.linspace(-np.sqrt(n-1),np.sqrt(n-1),n)
    initial=stats.binom.pmf(np.arange(n),n-1,.5)
    return a,grid,initial


def dynamics(kind,theta,n_grid=15):
    if kind=='continuous':
        sigma,tau=np.exp(theta)
        a,z,pi=rouwenhorst(n_grid,np.exp(-1/tau))
        return a,sigma*z,pi
    d,p0,p1=theta
    a=np.array([[p0,1-p0],[1-p1,p1]])
    pi=np.array([1-p1,1-p0])/(2-p0-p1)
    return a,np.array([-d,d]),pi


@numba.njit(cache=True)
def forward_backward(eta,y,row,n_rows,starts,a,bias,pi):
    """Scaled likelihood/gradient statistics; absent emissions stay one."""
    k=len(bias);n=len(eta)
    em=np.ones((n_rows,k));probs=np.empty((n,k))
    for i in range(n):
        for s in range(k):
            z=eta[i]+bias[s]
            p=1/(1+np.exp(-z))
            p=min(max(p,1e-14),1-1e-14)
            probs[i,s]=p
            em[row[i],s]=p if y[i]==1 else 1-p
    alpha=np.zeros((n_rows,k));scale=np.zeros(n_rows)
    ll=0.
    for t in range(n_rows):
        prior=pi.copy() if starts[t] else alpha[t-1]@a
        alpha[t]=prior*em[t]
        scale[t]=np.sum(alpha[t]);alpha[t]/=scale[t]
        ll+=np.log(scale[t])
    back=np.ones((n_rows,k))
    for t in range(n_rows-2,-1,-1):
        if not starts[t+1]:back[t]=a@(em[t+1]*back[t+1])/scale[t+1]
    counts=np.zeros((k,k));initial_counts=np.zeros(k)
    for t in range(n_rows):
        if starts[t]:initial_counts+=alpha[t]*back[t]
        elif t>0:
            for u in range(k):
                for v in range(k):
                    counts[u,v]+=alpha[t-1,u]*a[u,v]*em[t,v]*back[t,v]/scale[t]
    posterior=np.empty((n,k))
    for i in range(n):posterior[i]=alpha[row[i]]*back[row[i]]
    return ll,posterior,probs,counts,initial_counts


def layout(g):
    # Concatenate dense recorded rows, resetting at every session boundary.
    row=np.empty(len(g),dtype=np.int64);starts=[];offset=0
    for _,ix in g.groupby('idx_session',sort=False).indices.items():
        length=int(g.iloc[ix].position.max())+1
        row[ix]=offset+g.iloc[ix].position.to_numpy(int)
        starts.extend([True]+[False]*(length-1));offset+=length
    return row,offset,np.asarray(starts,dtype=np.bool_)


def objective(par,X,y,lay,kind,n_grid=15):
    nb=X.shape[1];beta=par[:nb];theta=par[nb:]
    a,bias,pi=dynamics(kind,theta,n_grid)
    ll,post,probs,counts,ic=forward_backward(X@beta,y,*lay,a,bias,pi)
    r=post*(y[:,None]-probs)
    gb=X.T@r.sum(axis=1)
    if kind=='continuous':
        gt=[np.sum(r*bias[None,:]),0.]
        deriv_indices=[1]
    else:
        gt=[np.sum(r*np.array([-1.,1.])),0.,0.]
        deriv_indices=[1,2]
    # Only the small transition/initial matrices need numerical derivatives;
    # the full likelihood's coefficient and emission gradients are analytic.
    for j in deriv_indices:
        h=1e-5 if kind=='continuous' else 1e-6
        xp=theta.copy();xm=theta.copy();xp[j]+=h;xm[j]-=h
        ap,_,pip=dynamics(kind,xp,n_grid);am,_,pim=dynamics(kind,xm,n_grid)
        da=(ap-am)/(2*h);dpi=(pip-pim)/(2*h)
        gt[j]=np.sum(counts*np.divide(da,a,out=np.zeros_like(a),where=a>1e-300))
        gt[j]+=np.sum(ic*dpi/pi)
    lam=np.full(nb,RIDGE);lam[0]=0.
    penalty=.5*np.dot(lam*beta,beta)
    gb-=lam*beta
    # Equal weak emission-scale regularization; no transition penalty.
    amplitude=np.exp(theta[0])if kind=='continuous' else theta[0]
    penalty+=.5*RIDGE*amplitude**2
    gt[0]-=RIDGE*amplitude**2 if kind=='continuous' else RIDGE*amplitude
    return -ll+penalty,-np.r_[gb,gt]


def fit(g,X,kind,beta,n_grid=15,extra_start=None):
    lay=layout(g);y=g.choice.to_numpy(float);nb=X.shape[1]
    if kind=='continuous':
        seeds=[np.log([.5,8.]),np.log([1.,60.])]
        bounds=[(np.log(.02),np.log(3.)),(0.,np.log(500.))]
    else:
        seeds=[np.array([.5,.9,.9]),np.array([1.,.98,.98])]
        bounds=[(0.,6.),(.5,.9995),(.5,.9995)]
    starts=[np.r_[beta,s]for s in seeds]
    if extra_start is not None:starts.append(np.asarray(extra_start))
    records=[];best=None
    for start in starts:
        r=optimize.minimize(objective,start,args=(X,y,lay,kind,n_grid),jac=True,
            method='L-BFGS-B',bounds=[(None,None)]*nb+bounds,
            options={'maxiter':300,'ftol':1e-10,'gtol':1e-5,'maxls':30})
        records.append({'objective':r.fun,'success':r.success,'message':str(r.message),
                        'nit':r.nit,'max_abs_gradient':float(np.max(np.abs(r.jac)))})
        if best is None or r.fun<best.fun:best=r
    return best,records


@numba.njit(cache=True)
def filter_predictions(eta,y,positions,sessions,a,bias,pi):
    """Prediction precedes current response; gaps apply A repeatedly."""
    n=len(y);k=len(pi);out=np.empty((n,4));post=pi.copy()
    for i in range(n):
        if i==0 or sessions[i]!=sessions[i-1]:
            prior=pi.copy()
        else:
            prior=post.copy()
            for _ in range(positions[i]-positions[i-1]):prior=prior@a
        mean=np.dot(prior,bias)
        variance=np.dot(prior,bias*bias)-mean*mean
        pstate=1/(1+np.exp(-(eta[i]+bias)))
        p=np.dot(prior,pstate)
        p=min(max(p,1e-14),1-1e-14)
        out[i,0]=p;out[i,1]=mean;out[i,2]=variance
        out[i,3]=1-np.dot(prior,prior)
        post=prior*(pstate if y[i]==1 else 1-pstate)
        post/=np.sum(post)
    return out


def predict(g,X,par,kind,n_grid=15):
    a,bias,pi=dynamics(kind,par[X.shape[1]:],n_grid)
    return filter_predictions(X@par[:X.shape[1]],g.choice.to_numpy(float),
        g.position.to_numpy(np.int64),g.idx_session.to_numpy(np.int64),a,bias,pi)


def bce(y,p):return -(y*np.log(p)+(1-y)*np.log1p(-p))


def rt_validation(g,pred):
    # Outcome was unused by current state inference. Current-choice adjustment
    # makes this a conditional association, not a causal RT effect.
    X,names=design(g,history=True,rtoutcome=True)
    lr=np.log(g.rt.to_numpy())
    out={}
    for kind in ['continuous','discrete']:
        b=pred[f'bias_{kind}'].to_numpy();side=2*g.choice.to_numpy()-1
        Z=np.column_stack([X,np.abs(b),side*b])
        lam=np.eye(Z.shape[1])*RIDGE;lam[0,0]=0
        coef=linalg.solve(Z.T@Z+lam,Z.T@lr,assume_a='pos')
        out[f'{kind}_rt_alignment']=coef[-1]
    return out


def inference(summary):
    rows=[]
    for key in ENDPOINTS:
        v=summary[key].to_numpy();n=len(v);se=stats.sem(v)
        ci=stats.t.interval(.95,n-1,loc=np.mean(v),scale=se)
        rows.append({'metric':key,'n_mice':n,'mean':v.mean(),'median':np.median(v),
            'lo':ci[0],'hi':ci[1],'dz':v.mean()/v.std(ddof=1),
            'p_t':stats.ttest_1samp(v,0).pvalue,'p_wilcoxon':stats.wilcoxon(v).pvalue,
            'n_positive':int((v>0).sum())})
    tab=pd.DataFrame(rows);tab['p_holm_5']=multipletests(tab.p_t,method='holm')[1]
    return tab


def run(n_grid=15):
    g=pd.read_pickle(OUT/'cache/aligned_trials.pkl')
    predictions=[];fits=[];summaries=[];acfs=[];fit_cache={}
    for mouse,z in g.groupby('mouse',sort=True):
        tic=time.time();z=z.reset_index(drop=True)
        X,names=design(z,history=True);y=z.choice.to_numpy(float)
        out=z[['aggregate_row','mouse','idx_session','position','fold','choice','rt',
               'condition','scheduled_pulse','coherence_pct']].copy()
        for c in ['p_static','p_continuous','p_discrete','bias_continuous','bias_discrete',
                  'variance_continuous','variance_discrete']:out[c]=np.nan
        for f in [2,3,4]:
            tr=z.fold.to_numpy()<f;te=z.fold.to_numpy()==f;seen=z.fold.to_numpy()<=f
            beta,ok=logistic(X[tr],y[tr]);assert ok
            out.loc[te,'p_static']=special.expit(X[te]@beta)
            for kind in ['continuous','discrete']:
                best,restarts=fit(z[tr],X[tr],kind,beta,n_grid)
                pred=predict(z[seen],X[seen],best.x,kind,n_grid)
                selected=pred[z.loc[seen,'fold'].to_numpy()==f]
                out.loc[te,f'p_{kind}']=selected[:,0]
                out.loc[te,f'bias_{kind}']=selected[:,1]
                out.loc[te,f'variance_{kind}']=selected[:,2]
                theta=best.x[X.shape[1]:]
                if kind=='continuous':params={'sigma':np.exp(theta[0]),'tau_rows':np.exp(theta[1])}
                else:params={'offset':theta[0],'p00':theta[1],'p11':theta[2]}
                fits.append({'mouse':mouse,'fold':f,'model':kind,'n_train':int(tr.sum()),
                    'n_test':int(te.sum()),'penalized_training_nll':best.fun,'converged':bool(best.success),
                    'starts':json.dumps(restarts),'parameters':json.dumps(params)})
                fit_cache[(mouse,f,kind)]={'parameters':best.x,'names':names,'n_grid':n_grid,
                                          'training_row_ids':z.loc[tr,'aggregate_row'].to_numpy()}
        keep=out.fold>=2;v=out[keep].reset_index(drop=True);zz=z[keep].reset_index(drop=True)
        assert v[['p_static','p_continuous','p_discrete']].notna().all().all()
        row={'mouse':mouse,'n_test':len(v)}
        for kind in ['static','continuous','discrete']:
            row[f'{kind}_nll']=bce(v.choice.to_numpy(),v[f'p_{kind}'].to_numpy()).sum()
            tab=acf_table(zz,v.choice.to_numpy()-v[f'p_{kind}'].to_numpy())
            tab['mouse']=mouse;tab['model']=kind;acfs+=tab.to_dict('records')
        for kind in ['continuous','discrete']:
            row[f'{kind}_gain_bits']=(row['static_nll']-row[f'{kind}_nll'])/len(v)/np.log(2)
        row['discrete_minus_continuous_bits']=(row['continuous_nll']-row['discrete_nll'])/len(v)/np.log(2)
        row.update(rt_validation(zz,v));summaries.append(row);predictions.append(v)
        print('DONE',mouse,'seconds',round(time.time()-tic,1),'bits',
              round(row['continuous_gain_bits'],4),round(row['discrete_gain_bits'],4),flush=True)
    tab=pd.DataFrame(summaries)
    tag=f'states_grid{n_grid}'
    pd.concat(predictions,ignore_index=True).to_pickle(OUT/f'cache/{tag}_predictions.pkl')
    pd.to_pickle(fit_cache,OUT/f'cache/{tag}_fits.pkl')
    pd.DataFrame(fits).to_csv(OUT/f'{tag}_fits.csv',index=False)
    tab.to_csv(OUT/f'{tag}_mouse_summary.csv',index=False)
    inference(tab).to_csv(OUT/f'{tag}_group_inference.csv',index=False)
    pd.DataFrame(acfs).to_csv(OUT/f'{tag}_residual_acf.csv',index=False)
    write_json(OUT/f'{tag}_manifest.json',{'source_sha256':sha(__file__),'n_grid':n_grid,
        'ridge':RIDGE,'training':'prefix folds <2/<3/<4, test next fold; same sessions',
        'state_prediction':'filtered before current choice, no current RT, advance every recorded row',
        'models':['static history GLM','continuous AR1 bias approximation','two-state bias-only GLM-HMM'],
        'group_endpoints':ENDPOINTS,'multiplicity':'Holm five endpoints',
        'limitations':['responded-only conditional choices','same-session forecasting',
                       'bias states, not attention labels','RT validation conditional, not causal']})
    print(inference(tab).round(6).to_string(index=False),flush=True)


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--grid',type=int,default=15)
    run(p.parse_args().grid)
