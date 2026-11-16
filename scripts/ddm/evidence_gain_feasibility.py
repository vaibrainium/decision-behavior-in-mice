"""Bounded training-data feasibility pilot for positive evidence-gain spread.

Two main pulse mice, all common parameters free, local multistart search. This
is neither held-out validation nor a global optimum. Independent evaluation
seeds check optimization noise, not generalization. Prior results stay intact.
"""
import argparse
import gc
import hashlib
import time
from pathlib import Path
import numpy as np
import pandas as pd
from scipy.optimize import minimize
from scripts.ddm.fit_mouse_ddm import MouseDDM,make_params,select,RESPONDED_LIKELIHOOD_PARAMS
from scripts.ddm.fit_response_delay import initialize,save_pickle,sha,write_json
from scripts.ddm.rescore_fits import inputs,terms
from src.ddm.ddm import FreeParam
from src.ddm.evidence_gain import EvidenceGainSimulator

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'dissemination/evidence_gain_2026-11-14'
FITS=Path('/mnt/data/processed/ddm/fits_evidence_gain_2026-11-14')
SOURCE=Path('/mnt/data/processed/ddm/fits_joint_unfreeze_pulse_time_weights')
VARIANTS={'fixed':'L0U0V0Z0G1','drift':'L0U0V1Z0G1'}
FIT_SEED=114143


def model_for(family,n_times,device):
    free,fixed=make_params(VARIANTS.get(family,'L0U0V0Z0G1'),'fast_only',n_pulse_times=n_times)
    if family=='gain':free['gain_sigma']=FreeParam(0.,1.5)
    m=MouseDDM(free,fixed,device=device,censor_at=5.,min_rt=(.3,'floor'),
               likelihood_params=RESPONDED_LIKELIHOOD_PARAMS)
    if family=='gain':m.simulator=EvidenceGainSimulator(device)
    return m


def fit_mouse(x,mouse,device):
    path=FITS/f'{mouse}_gain_all.pkl'
    if path.exists():raise FileExistsError(f'Preserve existing pilot: {path}')
    anchors={f:pd.read_pickle(SOURCE/f'{mouse}_{v}_all.pkl')for f,v in VARIANTS.items()}
    rows=np.flatnonzero(x['subject_id']==mouse);n_times=int(anchors['fixed']['n_pulse_times'])
    data,stim=select(x,rows,pulse_times=n_times)
    m=model_for('gain',n_times,device)
    bounds=np.array([(s.lower_bound,s.upper_bound)for s in m.fit_param_specs.values()])
    lo=bounds[:,0];span=bounds[:,1]-lo
    unit=lambda p:np.clip((np.array([p[k]for k in m.fit_keys])-lo)/span,0,1)
    candidates=[]
    for family,anchor in anchors.items():
        for sigma in [0.,.25,.5,.8,1.2]:
            for scale in [.75,1.,1.4]:
                p=anchor['parameters']|{'gain_sigma':sigma,'sv':0.}
                p['drift_gain']*=scale
                candidates.append((f'{family}_sigma{sigma}_k{scale}',unit(p)))
    stages={};tic=time.time();trace=[];profile=[]
    for stage,reps,budget in [('screen',3,350),('refine',15,600)]:
        initialize(None,data,stim,reps,FIT_SEED,m)
        best={'nll':float('inf'),'unit':None};calls=[0]
        def objective(u):
            val=float(m._objective_function(lo+span*np.clip(u,0,1),data,stim,reps,0.))
            calls[0]+=1
            if val<best['nll']:best.update(nll=val,unit=np.clip(u,0,1).copy())
            if calls[0]%100==0:
                print('GAIN',mouse,stage,calls[0],round(best['nll'],3),'seconds',round(time.time()-tic,1),flush=True)
                save_pickle(FITS/f'{mouse}_gain_checkpoint.pkl',dict(stage=stage,best=best,stages=stages))
            return val
        options=list(candidates)
        if stage=='refine':options +=[(f'screen_{i}',s['unit'])for i,s in enumerate(stages['screen']['solutions'])]
        scored=[]
        for name,u in options:
            score=objective(u);scored.append((score,name,u))
            if stage=='screen':profile.append(dict(mouse=mouse,start=name,nll=score))
        scored.sort(key=lambda r:r[0]);chosen=[scored[0]]
        for item in scored[1:]:
            if np.linalg.norm(item[2]-chosen[0][2])>.08:chosen.append(item);break
        solutions=[]
        for score,name,u in chosen:
            steps=np.full(len(u),.015);steps[m.fit_keys.index('gain_sigma')]=.08/1.5
            steps[m.fit_keys.index('ndt')]=.025/span[m.fit_keys.index('ndt')]
            simplex=np.repeat(u[None,:],len(u)+1,axis=0)
            for j,step in enumerate(steps):simplex[j+1,j]+=step if u[j]+step<=1 else-step
            result=minimize(objective,u,method='Nelder-Mead',bounds=[(0.,1.)]*len(u),
                options={'maxfev':budget,'xatol':1e-4,'fatol':.05,'initial_simplex':simplex})
            solutions.append(dict(start=name,unit=result.x,nll=float(result.fun),converged=bool(result.success),
                                  message=str(result.message),nfev=int(result.nfev)))
        solutions.append(dict(start='best_evaluated',**best))
        stages[stage]=dict(reps=reps,budget_per_start=budget,best=best.copy(),solutions=solutions)
    par=m._build_params(lo+span*stages['refine']['best']['unit'])
    result=dict(mouse=mouse,family='gain',split='all',parameters=par,free_parameters=m.fit_keys,
        n_train=len(rows),n_test=0,n_pulse_times=n_times,train_nll=stages['refine']['best']['nll'],
        fit_seconds=time.time()-tic,stages=stages,seed=FIT_SEED,global_optimum_established=False,
        validation='Training-data feasibility only; pulse summaries not optimized separately')
    save_pickle(path,result);pd.DataFrame(profile).to_csv(OUT/f'{mouse}_initial_profile.csv',index=False)
    print('DONE GAIN',mouse,'sigma',par['gain_sigma'],'nll',result['train_nll'],flush=True)
    m.simulator.clear_cache();del m,stim;gc.collect()


def evaluate(x,mouse,family,device,reps,seeds):
    path=FITS/f'{mouse}_gain_all.pkl'if family=='gain'else SOURCE/f'{mouse}_{VARIANTS[family]}_all.pkl'
    fit=pd.read_pickle(path);rows=np.flatnonzero(x['subject_id']==mouse)
    m=model_for(family,int(fit['n_pulse_times']),device)
    data,stim=select(x,rows,pulse_times=int(fit['n_pulse_times']))
    for seed in seeds:
        dest=OUT/'cache'/f'eval_{mouse}_{family}_r{reps}_s{seed}.pkl'
        if dest.exists():raise FileExistsError(dest)
        initialize(None,data,stim,reps,seed,m)
        out=m._simulate_condition(stim,fit['parameters'],reps)
        total,choice,rt=terms(m.likelihood_calc,out.rt.to_numpy(),out.choice.to_numpy(),
            out.signed_coherence.to_numpy(),data['rt'],data['choice'],data['condition'])
        assert np.isclose(total,choice+rt,atol=1e-7)
        out['row']=np.tile(rows,reps);out['rep']=np.repeat(np.arange(reps),len(rows))
        save_pickle(dest,dict(mouse=mouse,family=family,seed=seed,reps=reps,n=len(rows),
            nll=total,choice_nll=choice,rt_nll=rt,nonresponse=float((out.choice<0).mean()),
            fit_sha256=sha(path),outcomes=out))
        print('EVAL',mouse,family,seed,round(total,3),flush=True)
    m.simulator.clear_cache();del m,stim;gc.collect()


def run(args):
    OUT.mkdir(parents=True,exist_ok=True);(OUT/'cache').mkdir(exist_ok=True);FITS.mkdir(exist_ok=True)
    sources=[Path(__file__),ROOT/'src/ddm/evidence_gain.py',ROOT/'src/ddm/simulator.py',
        ROOT/'src/ddm/ddm.py',ROOT/'scripts/ddm/fit_response_delay.py',
        ROOT/'scripts/ddm/fit_mouse_ddm.py',ROOT/'src/ddm/likelihood_calculator_censored.py']
    write_json(OUT/'manifest.json',dict(source_sha256={str(p.relative_to(ROOT)):sha(p)for p in sources},
        input_sha256=sha('/mnt/data/processed/ddm/ddm_inputs_global_ucla_nofreeze.npz'),
        fit_seed=FIT_SEED,eval_seeds=args.seeds,eval_reps=args.reps,
        design='Bounded full-training feasibility; all shared parameters free; no held-out claim',
        mice=['PSUIM6','PSUIM7'],gain='G=exp(sigma*Z-sigma^2/2), post-front-end, every evidence channel, sv=0'))
    x=inputs()
    for mouse in ['PSUIM6','PSUIM7']:
        fit_mouse(x,mouse,args.device)
        for family in ['fixed','drift','gain']:evaluate(x,mouse,family,args.device,args.reps,args.seeds)


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--device',default='cuda');p.add_argument('--reps',type=int,default=60)
    p.add_argument('--seeds',nargs='+',type=int,default=[415,839]);run(p.parse_args())
