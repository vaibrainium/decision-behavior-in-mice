"""Bounded NHP-SSM pulse-state pilot with same-session future-block scoring.

The fork supplies masked input-driven likelihoods, forward/backward inference
and EM. PulseObservations implements exact unique-parameter sharing in the
binary M-step. All model/start/prior choices use training prefixes only.
"""
import argparse
import hashlib
import importlib.metadata as metadata
import json
import pickle
import subprocess
import time
from pathlib import Path
import numpy as np
import pandas as pd
import ssm
from scipy import special
from scripts.behavior.nhp_pulse_observations import PulseObservations

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'dissemination/nhp_pulse_hmm_2026-11-15'
INPUT=ROOT/'dissemination/history_dynamics_2026-11-14/cache/nhp_pulse6_inputs.pkl'
ALIGNED=ROOT/'dissemination/history_dynamics_2026-11-14/cache/aligned_trials.pkl'
FAMILIES=['static','tied','free']
PRIORS=[1.,2.,5.]
STARTS=4
CHUNK=20
MAX_ITERS=200
TOL=1e-3


def sha(path):
    h=hashlib.sha256()
    with Path(path).open('rb')as f:
        for b in iter(lambda:f.read(1048576),b''):h.update(b)
    return h.hexdigest()


def dump(path,value):
    path.parent.mkdir(parents=True,exist_ok=True)
    tmp=path.with_suffix('.tmp')
    with tmp.open('wb')as f:pickle.dump(value,f)
    tmp.replace(path)


def js(path,value):
    path.write_text(json.dumps(value,indent=2,default=lambda x:x.item()if isinstance(x,np.generic)else str(x))+'\n')


def prepare(mouse,collection):
    item=collection[mouse];n_sessions=len(item['inputs'])
    names=list(item['feature_names'])+[f'session_{s}'for s in item['session_ids'][1:]]+['position','position2']
    pulse=np.array([i for i,n in enumerate(names)if n.startswith('pulse_')])
    nuisance=np.arange(len(item['feature_names']),len(names))
    parts=[]
    for j,(X,y,mask,rows,sid)in enumerate(zip(item['inputs'],item['observations'],item['masks'],item['aggregate_rows'],item['session_ids'])):
        T=len(X);pos=np.arange(T)/max(1,T-1)
        session=np.zeros((T,n_sessions-1))
        if j:session[:,j-1]=1.
        Z=np.column_stack([X,session,pos-.5,(pos-.5)**2])
        parts.append(dict(X=Z,y=y.astype(int),mask=mask.astype(bool),rows=rows,
            fold=np.minimum(4,(5*pos).astype(int)),sid=int(sid),position=np.arange(T)))
    assert sum(p['mask'].sum()for p in parts)>0
    return dict(mouse=mouse,parts=parts,names=names,pulse=pulse,nuisance=nuisance)


def split(pack,cut):
    parts=[]
    for p in pack['parts']:
        ix=p['fold']<cut
        if not ix.any():continue
        parts.append({k:(v[ix]if isinstance(v,np.ndarray)and len(v)==len(ix)else v)for k,v in p.items()})
    return parts


def lists(parts):return tuple([[p[key]for p in parts]for key in ['y','X','mask']])


def model(pack,family,sigma):
    K=1 if family=='static'else 2
    common=list(pack['nuisance'])+(list(pack['pulse'])if family=='tied'else[])
    obs=PulseObservations(K,1,len(pack['names']),shared_columns=common,prior_sigma=sigma)
    return ssm.HMM(K,1,len(pack['names']),observations=obs,transitions='standard')


def snapshot(m):
    return dict(weights=m.observations.params.copy(),transition=m.transitions.transition_matrix.copy(),
        initial=m.init_state_distn.initial_state_distn.copy())


def restore(pack,family,sigma,state):
    m=model(pack,family,sigma);m.observations.params=state['weights'].copy()
    m.transitions.params=(np.log(state['transition']),)
    m.init_state_distn.params=(np.log(state['initial']),)
    return m


def initial_state(pack,family,sigma,base,seed,tied=None):
    rng=np.random.default_rng(11500+seed)
    m=model(pack,family,sigma);K=m.K
    if tied is not None and seed==0:
        return restore(pack,family,sigma,tied)
    W=np.repeat(base['weights'],K,axis=0)
    if K==2:
        W+=rng.normal(0,.12,W.shape)
        # Symmetric opposite-bias starts, specified before outcomes are scored.
        W[:,0,0]+=np.array([-.6,.6])*(1. if seed%2==0 else -1.)
        stay=[.9,.97,.99,.95][seed%4]
        m.transitions.params=(np.log(np.array([[stay,1-stay],[1-stay,stay]])),)
        m.init_state_distn.params=(np.log(np.array([.5,.5])),)
    m.observations.params=W
    return m


def fit_start(pack,parts,family,sigma,seed,base,stage,signature,tied=None):
    dest=OUT/'cache/fits'/f'{pack["mouse"]}_{stage}_{family}_p{sigma:g}_s{seed}.pkl'
    if dest.exists():
        result=pd.read_pickle(dest);assert result['signature']==signature
        return result
    tic=time.time()
    m=initial_state(pack,family,sigma,base,seed,tied)
    ys,Xs,masks=lists(parts)
    trajectory=[float(m.log_probability(ys,inputs=Xs,masks=masks))]
    mstep_failures=0;progress=[];converged=False
    max_iters=10 if family=='static'else MAX_ITERS
    chunk=2 if family=='static'else CHUNK
    for iteration in range(0,max_iters,chunk):
        m.fit(ys,inputs=Xs,masks=masks,method='em',num_iters=chunk,initialize=False,
              tolerance=0.,verbose=0)
        # Fork progress combines a previous E-step LL and updated prior; select
        # and stop using the actual post-update model objective instead.
        actual=float(m.log_probability(ys,inputs=Xs,masks=masks))
        trajectory.append(actual);gain=trajectory[-1]-trajectory[-2]
        records=m.observations.mstep_records
        mstep_failures=sum(not r['converged']for r in records)
        progress.append(dict(iterations=iteration+chunk,actual_log_probability=actual,change=gain))
        if gain < -1e-5:raise RuntimeError(('EM objective decreased',pack['mouse'],family,stage,progress))
        if abs(gain)<TOL:
            converged=True;break
    n_train=int(sum(p['mask'].sum()for p in parts))
    ll=float(m.log_likelihood(ys,inputs=Xs,masks=masks))
    r=dict(signature=signature,mouse=pack['mouse'],family=family,prior_sigma=sigma,seed=seed,stage=stage,
        state=snapshot(m),n_train=n_train,actual_log_probability=trajectory[-1],log_likelihood=ll,
        n_unique=m.observations.n_unique,converged=converged,iterations=iteration+chunk,
        last_objective_change=gain,mstep_failures=mstep_failures,
        max_mstep_gradient=max((r['max_abs_gradient']for r in records),default=0.),
        progress=progress,fit_seconds=time.time()-tic)
    dump(dest,r)
    print('FIT',pack['mouse'],stage,family,'prior',sigma,'seed',seed,'LL',round(ll,3),
        'iters',r['iterations'],'converged',converged,'sec',round(r['fit_seconds'],1),flush=True)
    return r


def groupfit(pack,parts,family,sigma,base,stage,signature,tied=None):
    n=1 if family=='static'else STARTS
    fits=[fit_start(pack,parts,family,sigma,seed,base,stage,signature,tied)for seed in range(n)]
    return max(fits,key=lambda r:r['actual_log_probability']),fits


def predict(pack,result,test_fold):
    m=restore(pack,result['family'],result['prior_sigma'],result['state'])
    rows=[]
    for p in pack['parts']:
        seen=p['fold']<=test_fold
        y,X,mask=p['y'][seen],p['X'][seen],p['mask'][seen]
        prior=m.filter(y,input=X,mask=mask)
        logits=m.observations.calculate_logits(X)
        pstate=np.exp(logits[:,:,1]);prob=np.sum(prior*pstate,axis=1)
        chosen=(p['fold'][seen]==test_fold)&mask[:,0]
        indices=np.flatnonzero(seen)[chosen]
        # State contrast at +/-36%, zero history/session offsets, position 0.
        templates=np.zeros((2,len(pack['names'])));templates[:,0]=1.
        for j,c in enumerate([-36,36]):
            templates[j,pack['names'].index(f'coherence_{c}')]=1.
        curve=np.exp(m.observations.calculate_logits(templates)[:,:,1])
        contrast=curve[1]-curve[0];high=int(np.argmax(contrast))
        for local,full in zip(np.flatnonzero(chosen),indices):
            pi=prior[local]
            right=np.clip(prob[local],1e-12,1-1e-12)
            rows.append(dict(mouse=pack['mouse'],family=result['family'],fold=test_fold,
                aggregate_row=int(p['rows'][full]),idx_session=p['sid'],position=int(p['position'][full]),
                choice=int(y[local,0]),p_right=right,nll=-np.log(right if y[local,0] else 1-right),
                prior_state0=float(pi[0]),prior_state1=float(pi[1])if m.K==2 else 0.,
                prior_higher_coherence_contrast=float(pi[high])))
    return pd.DataFrame(rows)


def run(args):
    OUT.mkdir(exist_ok=True);(OUT/'cache').mkdir(exist_ok=True)
    source=[Path(__file__),ROOT/'scripts/behavior/nhp_pulse_observations.py']
    signature=dict(sources={str(p.relative_to(ROOT)):sha(p)for p in source},input_sha256=sha(INPUT),
        priors=PRIORS,starts=STARTS,max_em_iters=MAX_ITERS,chunk=CHUNK,tolerance=TOL)
    manifest=signature|dict(commit=subprocess.check_output(['git','rev-parse','HEAD'],text=True,cwd=ROOT).strip(),
        encoding='Six physical direction x onset indicators; controls reference; preserve zero coherence',
        validation='same-session phase prefixes, not novel sessions/days',
        prior_selection='first 20% train, next 20% validate, fixed thereafter for all outer blocks',
        start_selection='actual training log_probability, no held-out selection',
        states='baseline/coherence/history can vary; session and position shared; pulse tied vs free',
        inactive='late pulse types absent in these two mice; not estimable',
        group_claim='none from two mice',ssm_origin=json.loads(metadata.distribution('ssm').read_text('direct_url.json')))
    js(OUT/'pilot_manifest.json',manifest)
    collection=pd.read_pickle(INPUT);all_predictions=[];all_fits=[];selections=[];chosen_cache={}
    for mouse in args.mice:
        pack=prepare(mouse,collection);inner=split(pack,1)
        chosen={};candidates={}
        for sigma in PRIORS:
            # The one-state optimum also provides NHP-style informed starts.
            zero=dict(weights=np.zeros((1,1,len(pack['names']))))
            static,records=groupfit(pack,inner,'static',sigma,zero,'inner',signature)
            all_fits+=records;candidates[('static',sigma)]=static
            tied,records=groupfit(pack,inner,'tied',sigma,static['state'],'inner',signature)
            all_fits+=records;candidates[('tied',sigma)]=tied
            free,records=groupfit(pack,inner,'free',sigma,static['state'],'inner',signature,tied['state'])
            all_fits+=records;candidates[('free',sigma)]=free
        for family in FAMILIES:
            scores=[]
            for sigma in PRIORS:
                r=candidates[(family,sigma)];p=predict(pack,r,1)
                score=float(p.nll.sum());scores.append((score,sigma))
                selections.append(dict(mouse=mouse,family=family,prior_sigma=sigma,inner_validation_nll=score,
                    selected=False))
            score,sigma=min(scores);chosen[family]=sigma
            selections[-len(PRIORS)+PRIORS.index(sigma)]['selected']=True
        for fold in [2,3,4]:
            train=split(pack,fold);best={}
            sigma=chosen['static'];zero=dict(weights=np.zeros((1,1,len(pack['names']))))
            best['static'],records=groupfit(pack,train,'static',sigma,zero,f'outer{fold}',signature)
            all_fits+=records
            for family in ['tied','free']:
                best[family],records=groupfit(pack,train,family,chosen[family],best['static']['state'],
                    f'outer{fold}',signature,best['tied']['state']if family=='free'else None)
                all_fits+=records
            for family,r in best.items():
                p=predict(pack,r,fold);all_predictions.append(p)
                chosen_cache[(mouse,fold,family)]=dict(result=r,names=pack['names'],pulse=pack['pulse'],
                    nuisance=pack['nuisance'])
            # Save reviewable progress after each completed outer block.
            pd.concat(all_predictions,ignore_index=True).to_csv(OUT/'predictions_progress.csv',index=False)
            dump(OUT/'cache/selected_models_progress.pkl',chosen_cache)
        print('MOUSE DONE',mouse,'selected priors',chosen,flush=True)
    pd.concat(all_predictions,ignore_index=True).to_csv(OUT/'heldout_predictions.csv',index=False)
    dump(OUT/'cache/selected_models.pkl',chosen_cache)
    summary=[{k:v for k,v in r.items()if k not in ['state','signature','progress']}for r in all_fits]
    pd.DataFrame(summary).to_csv(OUT/'fit_audit.csv',index=False)
    pd.DataFrame(selections).to_csv(OUT/'prior_selection.csv',index=False)
    print('COMPLETE',len(all_fits),'fits;',len(all_predictions),'held-out model blocks',flush=True)


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--mice',nargs='+',default=['PSUIM6','PSUIM7'])
    run(p.parse_args())
