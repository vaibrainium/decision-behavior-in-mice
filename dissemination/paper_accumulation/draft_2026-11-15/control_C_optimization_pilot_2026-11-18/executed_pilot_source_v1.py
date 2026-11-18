"""Control-only C sensitivity, local-restart pilot and train-selected CV checks.

All outputs are new derived results. Never overwrites original parameter fits.
"""
import argparse
import gc
import hashlib
import itertools
import json
import logging
import pickle
from pathlib import Path
import time
import numpy as np
import pandas as pd
from scipy.optimize import minimize
import torch
from scripts.ddm.fit_mouse_ddm import (load_inputs,responded_only,select,cv_folds,make_params,MouseDDM,
    MIN_RT,CENSOR_AT,too_few_responses,heldout_nll,EVAL_SEED)

ROOT=Path(__file__).resolve().parents[2]
DDM=Path('/mnt/data/processed/ddm')
VARIANT='L0U0V1Z0G1'
PILOT=['DBM13','DBM12','PSUIM10']
PROFILE_SEED=42
SELECT_SEEDS=[10101,20202]
CONFIRM_SEED=30303


def h(p):return hashlib.sha256(p.read_bytes()).hexdigest()

def write(p,x):
    temp=p.with_suffix(p.suffix+'.tmp');temp.write_text(json.dumps(x,indent=2,allow_nan=False)+'\n');temp.replace(p)


def make(fit,rig):
    free,fixed=make_params(VARIANT,'fast_only',fixed_guess_bias=False)
    return MouseDDM(free,fixed,device='cuda',likelihood_params=fit['likelihood_params'],min_rt=MIN_RT[rig],censor_at=CENSOR_AT)


def prepare(model,data,stim,reps,seed):
    model.simulator.clear_cache();model._set_seed(seed);model._labels=data['condition']
    model.precompute(*model._stimulus_shape(stim),n_reps=reps)


def stats(model,params,data,stim,reps):
    sim=model._simulate_condition(stim,params,reps)
    assert sim is not None
    joint=model.likelihood_calc.compute_nll(sim.rt,sim.choice,data['rt'],data['choice'],sim.signed_coherence,data['condition'])
    bad=too_few_responses(model.likelihood_calc,sim.choice.to_numpy())
    choice=0.;psy=[];central=[];rterr=[];qerr=[];qw=[]
    for condition in np.unique(data['condition']):
        d=data['condition']==condition;m=sim.signed_coherence.to_numpy()==condition
        pc=sim.choice.to_numpy()[m];pr=sim.rt.to_numpy()[m];n=int((pc>=0).sum())
        observed=data['choice'][d];odrt=data['rt'][d]
        if n==0:
            choice+=20*len(observed);bad=True;continue
        probs=np.array([(pc==side).sum() for side in [0,1]])
        smooth=(probs+.5)/(n+1)
        choice-=sum((observed==side).sum()*np.log(smooth[side]) for side in [0,1])
        actual=observed.mean();pred=(pc==1).sum()/n
        psy.append((actual-pred)**2)
        # Control condition label encodes coherence; recover coherence from separately attached array.
        coh=float(np.unique(data['coh'][d]).item())
        if abs(round(coh*100)) in [18,36]:central.append((actual-pred)*np.sign(coh))
        for side in [0,1]:
            a=odrt[observed==side];b=pr[pc==side]
            if len(a)>=10 and len(b):rterr.append((a.mean()-b.mean())**2)
            if len(a)>=9 and len(b):
                qerr.append(float(np.mean(abs(np.quantile(a,[.1,.3,.5,.7,.9])-np.quantile(b,[.1,.3,.5,.7,.9])))))
                qw.append(len(a))
    return {'joint_nll':float(joint),'choice_nll':float(choice),'rt_nll':float(joint-choice),
        'psy_rmse':float(np.sqrt(np.mean(psy))) if psy else 1.,
        'central_deficit':float(np.mean(central)) if central else 0.,
        'mean_rt_rmse_s':float(np.sqrt(np.mean(rterr))) if rterr else 5.,
        'quantile_mae_s':float(np.average(qerr,weights=qw)) if qw else 5.,
        'no_response_fraction':float(np.mean(sim.choice<0)),'training_guard_violated':bool(bad)}


def parameter_grid(model,base):
    keys=['drift_gain','sv','p_guess'];levels=[[.8,1.,1.2],[.75,1.,1.25],[.75,1.,1.25]]
    rows=[];seen=set()
    for factors in itertools.product(*levels):
        params=dict(base)
        for key,factor in zip(keys,factors):
            bound=model.fit_param_specs[key];params[key]=float(np.clip(base[key]*factor,bound.lower_bound,bound.upper_bound))
        signature=tuple(params[k] for k in keys)
        if signature in seen:continue
        seen.add(signature);rows.append((factors,params))
    return rows


def profile(out,model,base,data,stim,reps,meta):
    path=out/'sensitivity.json'
    if path.exists():
        saved=json.loads(path.read_text());assert saved['meta']==meta;return saved['rows']
    prepare(model,data,stim,reps,PROFILE_SEED);rows=[]
    for factors,params in parameter_grid(model,base):
        result=stats(model,params,data,stim,reps)
        rows.append({'gain_factor':factors[0],'sv_factor':factors[1],'guess_factor':factors[2],
                     'parameters':params,**result})
    write(path,{'meta':meta,'rows':rows})
    return rows


def starts(base,rows):
    usable=[r for r in rows if not r['training_guard_violated']]
    order=[('original',dict(base)),('map_joint_best',min(usable,key=lambda r:r['joint_nll'])['parameters']),
           ('map_choice_best',min(usable,key=lambda r:r['psy_rmse'])['parameters'])]
    return order


def optimize(out,model,base,data,stim,reps,rows,maxfev,meta):
    results=[];bounds=np.array([(b.lower_bound,b.upper_bound) for b in model.fit_param_specs.values()])
    lo,hi=bounds.T;span=hi-lo;keys=model.fit_keys
    for label,initial in starts(base,rows):
        path=out/(label+'_restart.json')
        if path.exists():
            saved=json.loads(path.read_text());assert saved['meta']==meta;results.append(saved);continue
        prepare(model,data,stim,reps,PROFILE_SEED)
        x=np.clip((np.array([initial[k] for k in keys])-lo)/span,0,1)
        trace=[];best=[np.inf,None]
        def objective(unit):
            physical=lo+np.clip(unit,0,1)*span
            value=float(model._objective_function(physical,data,stim,reps))
            trace.append({'evaluation':len(trace)+1,'joint_nll':value,'parameters':dict(zip(keys,map(float,physical)))})
            if value<best[0]:best[:]=[value,physical.copy()]
            return value
        simplex=np.tile(x,(len(keys)+1,1))
        for j in range(len(keys)):
            step=.025
            simplex[j+1,j]=x[j]+step if x[j]+step<=1 else x[j]-step
        t=time.monotonic()
        opt=minimize(objective,x,method='Nelder-Mead',bounds=[(0.,1.)]*len(keys),
            options={'initial_simplex':simplex,'maxfev':maxfev,'maxiter':maxfev,'xatol':1e-4,'fatol':.02})
        assert best[1] is not None
        params=model._build_params(best[1])
        result={'meta':meta,'name':label,'parameters':{k:float(v) for k,v in params.items()},
                'best_training_nll':float(best[0]),'n_evaluations':len(trace),'optimizer_success':bool(opt.success),
                'optimizer_message':str(opt.message),'runtime_s':time.monotonic()-t,'trace':trace}
        write(path,result);results.append(result)
        print(f"  {meta['mouse']} {meta['split']} {label}: {len(trace)} evals, fit score {best[0]:.3f} ({time.monotonic()-t:.1f}s)",flush=True)
    return results


def evaluate(out,model,base,candidates,data,stim,meta):
    path=out/'independent_evaluation.json'
    if path.exists():
        record=json.loads(path.read_text());assert record['meta']==meta;return record
    sets={'original':dict(base),**{r['name']:r['parameters'] for r in candidates}}
    records=[]
    for seed in SELECT_SEEDS:
        prepare(model,data,stim,30,seed)
        for name,params in sets.items():
            records.append({'name':name,'seed':seed,'n_reps':30,**stats(model,params,data,stim,30)})
    frame=pd.DataFrame(records)
    legal=frame.groupby('name').training_guard_violated.any()
    means=frame.groupby('name').joint_nll.mean();legal_names=legal[~legal].index
    winner=means.loc[legal_names].idxmin()
    # Independent confirmation is not used to select a different winner.
    confirmation=[];prepare(model,data,stim,60,CONFIRM_SEED)
    for name in dict.fromkeys(['original',winner]):
        confirmation.append({'name':name,'seed':CONFIRM_SEED,'n_reps':60,**stats(model,sets[name],data,stim,60)})
    record={'meta':meta,'selection_records':records,'winner_from_selection_seeds':winner,
            'selected_parameters':sets[winner],'confirmation_records':confirmation}
    write(path,record)
    return record


def load_fit(mouse,split):
    folder='fits_resp_final' if split=='control' else 'fits_resp_fast_only'
    path=DDM/folder/f'{mouse}_{VARIANT}_{split}.pkl'
    fit=pickle.load(path.open('rb'));assert fit['success'] and fit['split']==split
    assert fit['likelihood_params']=={'method':'qmle_censored','nbins':9,'rt_nllh_weight':1.,'include_censored':False}
    return path,fit


def run_one(output,inputs,mouse,split,reps,maxfev,do_restarts):
    rows=np.flatnonzero((inputs['subject_id']==mouse)&(inputs['sched_pulse_type']==0))
    if split=='control':train=rows;test=None
    else:
        folds=cv_folds(inputs['condition'][rows],5);fold=int(split[3:]);train=rows[folds!=fold];test=rows[folds==fold]
    path,fit=load_fit(mouse,split);assert fit['n_train']==len(train)
    rig=np.unique(inputs['data_source'][train]).item();model=make(fit,rig)
    data,stim=select(inputs,train);data['coh']=inputs['signed_coherence'][train]
    out=output/mouse/split;out.mkdir(parents=True,exist_ok=True)
    meta={'mouse':mouse,'split':split,'fit_path':str(path),'fit_sha256':h(path),'n_train':len(train),
          'input_sha256':h(DDM/'ddm_inputs_global.npz'),'profile_reps':reps,'profile_seed':PROFILE_SEED,
          'max_restart_evaluations':maxfev,'pilot_script_sha256':h(Path(__file__))}
    rows=profile(out,model,fit['parameters'],data,stim,reps,meta)
    if do_restarts:
        candidates=optimize(out,model,fit['parameters'],data,stim,reps,rows,maxfev,meta)
        record=evaluate(out,model,fit['parameters'],candidates,data,stim,meta)
        if test is not None:
            tp=out/'heldout_comparison.json'
            if not tp.exists():
                td,ts=select(inputs,test)
                old=heldout_nll(model,fit['parameters'],td,ts,fit['n_reps'],seed=EVAL_SEED)
                np.testing.assert_allclose(old,fit['test_nll'],rtol=0,atol=1e-8)
                new=heldout_nll(model,record['selected_parameters'],td,ts,fit['n_reps'],seed=EVAL_SEED)
                write(tp,{'meta':meta,'n_test':len(test),'original_test_nll':old,'new_test_nll':new,'new_minus_original':new-old,
                          'selected_parameters':record['selected_parameters'],'winner_from_training_only':record['winner_from_selection_seeds']})
    model.simulator.clear_cache();del model,stim;gc.collect();torch.cuda.empty_cache()
    return out


def main():
    parser=argparse.ArgumentParser(__doc__);parser.add_argument('--output',type=Path,required=True)
    parser.add_argument('--stage',choices=['map','pilot','cv'],required=True);parser.add_argument('--maxfev',type=int,default=200)
    parser.add_argument('--mice',nargs='*');a=parser.parse_args();a.output.mkdir(parents=True,exist_ok=True)
    for name in ['src.ddm.simulator','src.ddm.ddm']:logging.getLogger(name).setLevel(logging.WARNING)
    assert torch.cuda.is_available()
    inputs=responded_only(load_inputs(DDM/'ddm_inputs_global.npz'))
    mice=a.mice or (sorted(np.unique(inputs['subject_id'])) if a.stage=='map' else PILOT)
    splits=[f'ccv{k}' for k in range(5)] if a.stage=='cv' else ['control']
    t=time.monotonic()
    for mouse in mice:
        for split in splits:
            run_one(a.output,inputs,mouse,split,15,a.maxfev,a.stage!='map')
            print(f'{a.stage} {mouse} {split} complete ({time.monotonic()-t:.1f}s)',flush=True)
    print(f'Stage {a.stage} complete',flush=True)


if __name__=='__main__':main()
