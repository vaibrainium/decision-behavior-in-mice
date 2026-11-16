"""Chronology-aware, exploratory history/RT and serial-dependence diagnostics.

Original inputs/results are read-only. Primary inference uses mice as the unit.
Current-RT-conditioned history curves are descriptive. Residual predictions hold
out contiguous within-session blocks; this is not new-session generalization.
"""
import argparse
import hashlib
import json
import platform
from pathlib import Path
import subprocess
import time

import numpy as np
import pandas as pd
from scipy import linalg, special, stats
from statsmodels.stats.multitest import multipletests

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'dissemination/history_dynamics_2026-11-14'
DATA=Path('/mnt/data/processed')
TABLE=DATA/'pulse_followup/20261023T191030Z_fa8de8b/data/trial_table.csv'
INPUT=DATA/'ddm/ddm_inputs_global_ucla_nofreeze.npz'
RIDGE=.1
ENDPOINTS=['win_bias_late_minus_early','loss_bias_late_minus_early',
           'choice_residual_acf_2_10','rt_residual_acf_2_10']


def sha(p):
    h=hashlib.sha256()
    with Path(p).open('rb')as f:
        for c in iter(lambda:f.read(1048576),b''):h.update(c)
    return h.hexdigest()


def write_json(path,data):
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(data,indent=2,default=lambda v:v.item()if isinstance(v,np.generic)else str(v))+'\n')


def prepare():
    a=pd.read_csv(DATA/'aggregate_data.csv',low_memory=False)
    a['aggregate_row']=np.arange(len(a))
    # Recorded file order is retained within each session. Counters can repeat
    # on no-choice records and are not physical-row identifiers.
    a['position']=a.groupby('idx_session',sort=False).cumcount()
    a['n_session']=a.groupby('idx_session').idx_session.transform('size')
    a['position_frac']=a.position/np.maximum(a.n_session-1,1)
    grp=a.groupby('idx_session',sort=False)
    prev=grp[['choice','outcome','reaction_time','is_correction_trial','signed_coherence','target']].shift()
    prev.columns=['prev_choice','prev_outcome','prev_rt','prev_correction','prev_coherence','prev_target']
    for c in prev:a[c]=prev[c]
    side=a.prev_choice.map({0.:-1.,1.:1.}).fillna(0.)
    a['h_win']=side*(a.prev_outcome==1)
    a['h_loss']=side*(a.prev_outcome==0)
    a['prev_missing']=(a.prev_choice.isna()&(a.position>0)).astype(float)
    a['first_trial']=(a.position==0).astype(float)
    a['prev_correction']=a.prev_correction.fillna(False).astype(float)
    a['prev_late']=(a.prev_rt>5).astype(float)
    a['prev_logrt']=np.log(a.prev_rt.where(a.prev_rt>0)).fillna(0.)
    a['prev_coherence']=a.prev_coherence.fillna(0.)/100
    tt=pd.read_csv(TABLE,low_memory=False).set_index('trial_id',drop=False)
    with np.load(INPUT)as x:
        keep=x['choice']>=0
        ids=x['agg_code'][keep].astype(str)
        t=tt.loc[ids].copy().reset_index(drop=True)
        g=a.iloc[t.aggregate_row.to_numpy()].copy().reset_index(drop=True)
        assert np.array_equal(g.subject_id.to_numpy(),t.mouse.to_numpy())
        assert np.array_equal(g.idx_session.to_numpy(),t.idx_session.to_numpy())
        assert np.array_equal(g.choice.to_numpy(),x['choice'][keep])
        assert np.allclose(g.reaction_time,x['rt'][keep],atol=2e-6)
        g['input_row']=np.flatnonzero(keep)
        g['condition']=x['condition'][keep]
        g['scheduled_pulse']=x['sched_pulse_type'][keep]
    assert g.aggregate_row.is_unique
    g['trial_id']=ids
    g['mouse']=g.subject_id
    g['rt']=g.reaction_time
    g['coherence_pct']=g.signed_coherence.astype(int)
    g['session']=g.idx_session.astype(str)
    g['fold']=np.minimum(4,(5*g.position_frac).astype(int))
    errors={}
    for c in ['prev_choice','prev_outcome']:
        errors[c]=int((~np.isclose(g[c],t[c],equal_nan=True)).sum())
        assert errors[c]==0,errors
    rows=[]
    for m,z in g.groupby('mouse'):
        raw=a[a.subject_id==m]
        old=z.groupby('idx_session').choice.shift()
        naive=old.notna()&z.prev_choice.notna()
        different=naive&(old!=z.prev_choice)
        ordered=z.sort_values(['idx_session','position'])
        gaps=ordered.groupby('idx_session').position.diff()
        nc=raw[~raw.is_correction_trial.astype(bool)]
        prevtar=nc.groupby('idx_session').target.shift()
        targetok=nc.target.notna()&prevtar.notna()
        rows.append({'mouse':m,'n_main':len(z),'n_sessions':z.idx_session.nunique(),
            'n_previous_missing':int(z.prev_missing.sum()),'n_previous_late':int(z.prev_late.sum()),
            'n_previous_correction':int(z.prev_correction.sum()),
            'n_retained_adjacencies_with_raw_gap':int((gaps>1).sum()),
            'n_naive_previous_choice_disagreements':int(different.sum()),
            'target_repeat_noncorrection':float((nc.loc[targetok,'target']==prevtar[targetok]).mean())})
    report={'n_aggregate_records':len(a),'n_main':len(g),'n_mice':g.mouse.nunique(),
        'n_sessions':g.idx_session.nunique(),'raw_counter_duplicate_records':int(a.duplicated(['idx_session','idx_valid_trial','idx_correction']).sum()),
        'counter_inversions_in_recorded_order':int(sum((z.idx_valid_trial.diff()<0).sum()for _,z in a.groupby('idx_session'))),
        'alignment_history_disagreements':errors,
        'definition':'Physical recorded-row order within idx_session; no compression of excluded/correction/late records',
        'input_sha256':sha(INPUT),'table_sha256':sha(TABLE),'aggregate_sha256':sha(DATA/'aggregate_data.csv')}
    pd.DataFrame(rows).to_csv(OUT/'chronology_by_mouse.csv',index=False)
    write_json(OUT/'chronology_audit.json',report)
    g.to_pickle(OUT/'cache/aligned_trials.pkl')
    print('PREPARED',report,flush=True)
    return g


def logistic(X,y,weights=None,start=None,penalty=RIDGE):
    """Ridge binomial log loss, unpenalized intercept; deterministic Newton fit."""
    w=np.ones(len(y))if weights is None else np.asarray(weights,float)
    lam=np.full(X.shape[1],penalty);lam[0]=0.
    beta=np.zeros(X.shape[1])if start is None else np.asarray(start,float).copy()
    if start is None:beta[0]=special.logit(np.clip(np.average(y,weights=w),.01,.99))
    def loss(b):
        eta=X@b
        return float(w@(np.logaddexp(0,eta)-y*eta)+.5*np.dot(lam*b,b))
    converged=False
    for _ in range(80):
        p=special.expit(X@beta)
        score=X.T@(w*(y-p))-lam*beta
        h=X.T@((w*p*(1-p))[:,None]*X)+np.diag(lam)
        step=linalg.solve(h,score,assume_a='pos')
        old=loss(beta);scale=1.
        while scale>1e-6 and loss(beta+scale*step)>old+1e-10:scale*=.5
        beta+=scale*step
        if np.max(np.abs(scale*step))<1e-7:
            converged=True;break
    return beta,converged


def dummies(z,prefix):
    d=pd.get_dummies(z.astype(str),prefix=prefix,drop_first=True,dtype=float)
    return d.to_numpy(),list(d.columns)


def design(g,history=True,rtcurve=False,rtoutcome=False):
    pieces=[np.ones((len(g),1))];names=['intercept']
    for col in ['condition','session']:
        a,n=dummies(g[col],col);pieces.append(a);names+=n
    pos=g.position_frac.to_numpy()-.5
    pieces += [pos[:,None],(pos**2)[:,None]];names+=['position','position2']
    base=['first_trial','prev_missing','prev_correction','prev_late','prev_coherence']
    if history:base+=['h_win','h_loss','prev_logrt']
    pieces.append(g[base].to_numpy(float));names+=base
    if rtoutcome:
        choice=g.choice.to_numpy(float)
        pieces.append(choice[:,None]);names+=['current_choice']
        coh,cn=dummies(g.coherence_pct,'coh_choice')
        pieces.append(coh*choice[:,None]);names+=cn
    if rtcurve:
        lr=np.log(g.rt.to_numpy())
        pieces += [lr[:,None],(lr**2)[:,None]];names+=['logrt','logrt2']
        for col in ['coherence_pct','scheduled_pulse']:
            d,n=dummies(g[col],col+'_logrt');pieces.append(d*lr[:,None]);names+=n
        pieces += [(g.h_win.to_numpy()*lr)[:,None],(g.h_loss.to_numpy()*lr)[:,None]]
        names+=['win_x_logrt','loss_x_logrt']
    X=np.column_stack(pieces)
    keep=np.r_[True,np.ptp(X[:,1:],axis=0)>1e-12]
    return X[:,keep],[n for n,k in zip(names,keep)if k]


def block_weights(g,rng,length=50):
    w=np.zeros(len(g))
    for _,indices in g.groupby('idx_session',sort=False).indices.items():
        b=(g.iloc[indices].position.to_numpy()//length).astype(int)
        unique=np.unique(b);counts=np.bincount(rng.integers(0,len(unique),len(unique)),minlength=len(unique))
        w[indices]=counts[np.searchsorted(unique,b)]
    return w


def curve(g,reps,rng,scope='all'):
    X,names=design(g,rtcurve=True)
    y=g.choice.to_numpy(float)
    b,ok=logistic(X,y)
    assert ok,(g.mouse.iloc[0],scope,'history curve did not converge')
    boots=[]
    for _ in range(reps):
        bb,good=logistic(X,y,block_weights(g,rng),start=b)
        if good:boots.append(bb)
    assert len(boots)>=.95*reps
    boots=np.array(boots)
    q=np.quantile(g.rt,[.1,.3,.5,.7,.9]);lo,hi=np.quantile(g.rt,[.2,.8])
    rows=[];summary={}
    for label,h,inter in [('win','h_win','win_x_logrt'),('loss','h_loss','loss_x_logrt')]:
        if h not in names or inter not in names:continue
        i,j=names.index(h),names.index(inter)
        for k,t in enumerate(q):
            value=2*(b[i]+b[j]*np.log(t))
            bs=2*(boots[:,i]+boots[:,j]*np.log(t));ci=np.quantile(bs,[.025,.975])
            rows.append({'mouse':g.mouse.iloc[0],'scope':scope,'history':label,'rt_quantile':(.1,.3,.5,.7,.9)[k],
                'rt_s':t,'bias_logodds_RminusL':value,'lo':ci[0],'hi':ci[1],
                'odds_ratio_previous_R_vs_L':np.exp(value),'n':len(g),'successful_bootstraps':len(boots)})
        delta=2*b[j]*np.log(hi/lo)
        summary[f'{label}_bias_late_minus_early']=delta
        summary[f'{label}_bias_at_1s']=2*b[i]
    return rows,summary,{'names':names,'coefficients':b,'bootstrap_coefficients':boots,'scope':scope}


def cv_residuals(g):
    y=g.choice.to_numpy(float);lr=np.log(g.rt.to_numpy())
    out=g[['aggregate_row','mouse','idx_session','position','fold','rt','choice','condition','scheduled_pulse']].copy()
    for history in [False,True]:
        tag='history'if history else'base'
        X,names=design(g,history=history)
        Z,znames=design(g,history=history,rtoutcome=True)
        p=np.full(len(g),np.nan);mu=np.full(len(g),np.nan)
        for f in np.unique(g.fold):
            train=g.fold.to_numpy()!=f;test=~train
            b,ok=logistic(X[train],y[train]);assert ok
            p[test]=special.expit(X[test]@b)
            penalty=np.eye(Z.shape[1])*RIDGE;penalty[0,0]=0
            rb=linalg.solve(Z[train].T@Z[train]+penalty,Z[train].T@lr[train],assume_a='pos')
            mu[test]=Z[test]@rb
        assert np.isfinite(p).all()and np.isfinite(mu).all()
        out[f'p_{tag}']=p;out[f'logrt_{tag}']=mu
        out[f'choice_resid_{tag}']=y-p
        out[f'rt_resid_{tag}']=lr-mu
    return out


def acf_table(g,values,lags=range(1,21),weights=None):
    """Pairs separated by physical recorded rows within a session; no compression."""
    total=np.zeros((len(list(lags)),4))
    lags=list(lags)
    for _,ix in g.groupby('idx_session',sort=False).indices.items():
        pos=g.iloc[ix].position.to_numpy(int)
        val=np.asarray(values)[ix].copy()
        val-=val.mean()
        dense=np.full(pos.max()+1,np.nan);dense[pos]=val
        dw=np.ones(len(dense))if weights is None else np.zeros(len(dense))
        if weights is not None:dw[pos]=np.asarray(weights)[ix]
        for j,lag in enumerate(lags):
            if lag>=len(dense):continue
            a,b=dense[:-lag],dense[lag:];good=np.isfinite(a)&np.isfinite(b)
            w=dw[:-lag][good];a,b=a[good],b[good]
            total[j]+=[np.dot(w,a*b),np.dot(w,a*a),np.dot(w,b*b),w.sum()]
    den=np.sqrt(total[:,1]*total[:,2])
    rho=np.divide(total[:,0],den,out=np.full(len(lags),np.nan),where=den>0)
    return pd.DataFrame({'lag':lags,'acf':rho,'n_pairs':total[:,3].astype(int)})


def persistence(g,res,reps,rng):
    rows=[];summ={};nulls=[]
    for kind in ['choice','rt']:
        for model in ['base','history']:
            v=res[f'{kind}_resid_{model}'].to_numpy()
            est=acf_table(g,v)
            boot=np.array([acf_table(g,v,weights=block_weights(g,rng)).acf.to_numpy()for _ in range(reps)])
            est['lo'],est['hi']=np.quantile(boot,[.025,.975],axis=0)
            est['mouse']=g.mouse.iloc[0];est['kind']=kind;est['model']=model
            rows+=est.to_dict('records')
            key=f'{kind}_residual_acf_2_10'
            if model=='history':summ[key]=est.loc[est.lag.between(2,10),'acf'].mean()
        # Conditional fixed-predictor reference only; not a full refitted
        # sequential generative calibration. No biological p-value is derived.
        sims=[]
        for _ in range(reps):
            if kind=='choice':
                p=res.p_history.to_numpy();v=rng.binomial(1,p)-p
            else:
                v=res.rt_resid_history.to_numpy().copy()
                for _,ix in g.groupby('idx_session').indices.items():v[ix]=rng.permutation(v[ix])
            sims.append(acf_table(g,v).acf.to_numpy())
        sims=np.array(sims)
        for j,lag in enumerate(range(1,21)):
            ci=np.quantile(sims[:,j],[.025,.975])
            nulls.append({'mouse':g.mouse.iloc[0],'kind':kind,'lag':lag,'lo':ci[0],'hi':ci[1],
                'reference':'Independent Bernoulli conditional on frozen predictors'if kind=='choice'else'Within-session residual-order permutation',
                'parameter_uncertainty_included':False})
    return rows,summ,nulls


def group_inference(summary):
    rows=[]
    for metric in ENDPOINTS:
        v=summary[metric].dropna().to_numpy();n=len(v);sd=v.std(ddof=1)
        ci=stats.t.interval(.95,n-1,loc=v.mean(),scale=stats.sem(v))
        rows.append({'metric':metric,'n_mice':n,'mean':v.mean(),'median':np.median(v),'lo':ci[0],'hi':ci[1],
            'dz':v.mean()/sd,'p_t':stats.ttest_1samp(v,0).pvalue,'p_wilcoxon':stats.wilcoxon(v).pvalue,
            'n_positive':int((v>0).sum())})
    r=pd.DataFrame(rows);r['p_holm_4']=multipletests(r.p_t,method='holm')[1]
    return r


def run(reps,seed):
    (OUT/'cache').mkdir(parents=True,exist_ok=True)
    g=prepare();rng=np.random.default_rng(seed)
    curves=[];acfs=[];summary=[];residuals=[];null=[]
    models={}
    for mouse,z in g.groupby('mouse',sort=True):
        z=z.reset_index(drop=True);start=time.monotonic()
        c,s,m=curve(z,reps,rng);curves+=c;models[mouse]=m
        for scope,mask in [('controls',z.scheduled_pulse==0),('clean_previous',
            (z.prev_missing==0)&(z.first_trial==0)&(z.prev_late==0)&(z.prev_correction==0))]:
            cc,ss,mm=curve(z[mask].reset_index(drop=True),max(80,reps//2),rng,scope)
            curves+=cc;models[f'{mouse}_{scope}']=mm
        pred=cv_residuals(z);residuals.append(pred)
        a,t,n=persistence(z,pred,reps,rng);acfs+=a;null+=n
        summary.append({'mouse':mouse,'n':len(z),'n_sessions':z.idx_session.nunique(),**s,**t})
        print('DONE',mouse,'n',len(z),'seconds',round(time.monotonic()-start,1),flush=True)
    pd.DataFrame(curves).to_csv(OUT/'history_bias_curves.csv',index=False)
    pd.DataFrame(acfs).to_csv(OUT/'residual_acf.csv',index=False)
    pd.DataFrame(null).to_csv(OUT/'conditional_null_reference.csv',index=False)
    s=pd.DataFrame(summary);s.to_csv(OUT/'mouse_summary.csv',index=False)
    group_inference(s).to_csv(OUT/'group_inference.csv',index=False)
    pd.concat(residuals,ignore_index=True).to_pickle(OUT/'cache/oof_residuals.pkl')
    pd.to_pickle(models,OUT/'cache/history_regressions.pkl')
    write_json(OUT/'manifest.json',{'commit':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
        'source_sha256':sha(__file__),'seed':seed,'block_bootstraps':reps,'block_length_recorded_rows':50,
        'ridge_penalty':RIDGE,'primary_endpoints':ENDPOINTS,'correction':'Holm over four group t-tests',
        'sampling_unit':'mouse for group inference; within-session recorded-row blocks for within-mouse uncertainty',
        'generalization':'Five contiguous within-session blocks; parameters may use other blocks on both sides; not prospective/new-session',
        'rt_curve':'Current RT conditioned, descriptive; previous R vs L log odds contrast',
        'null_reference':'Fixed predictors/residual permutation; no refitting or full sequential generative calibration',
        'python':platform.python_version(),'numpy':np.__version__,'pandas':pd.__version__})
    print(group_inference(s).round(5).to_string(index=False),flush=True)


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--bootstrap',type=int,default=300);p.add_argument('--seed',type=int,default=114)
    a=p.parse_args();run(a.bootstrap,a.seed)
