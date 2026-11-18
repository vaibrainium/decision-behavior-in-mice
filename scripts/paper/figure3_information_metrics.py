"""Connected-point bits/trial and QMLE-based delta-BIC views of control models.

No parameter fitting. Test scores are read from audited archives. Choice nulls
use training trials only. Full-control BIC scores use independent simulation
seeds, with exact saved free-parameter counts and source hashes.
"""
import argparse
import gc
import hashlib
import json
import logging
import pickle
from pathlib import Path
import time

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
from matplotlib.ticker import MaxNLocator
import numpy as np
import pandas as pd
import torch
from scripts.paper.style import RC
from scripts.ddm.fit_mouse_ddm import load_inputs, responded_only, select, cv_folds, heldout_nll
from scripts.ddm.primacy import make_model

ROOT = Path(__file__).resolve().parents[2]
DDM = Path('/mnt/data/processed/ddm')
MODELS = ['C','E','ES','DDMx','ESx']
SPECS = {
    'C': ('fits_resp_final','L0U0V1Z0G1',False,False,None),
    'E': ('fits_resp_fast_only_leak20-200_cap','L1U0V1Z0G1',False,False,(20.,200.)),
    'ES': ('fits_resp_fast_only_es_cap','L0U0V1Z0G1',False,True,None),
    'DDMx': ('fits_resp_nominal_ddm_g001','L0U0V0Z0G0',True,False,None),
    'ESx': ('fits_resp_nominal_es','L0U0V0Z0G0',True,True,None),
}


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def draw(values, title, ylabel, direction, letter, path, book):
    with plt.rc_context({**RC,'font.family':'DejaVu Sans'}):
        fig, ax = plt.subplots(figsize=(100/25.4,85/25.4))
        fig.subplots_adjust(left=.23,right=.97,bottom=.18,top=.77)
        fig.text(.04,.97,letter,fontsize=12,fontweight='bold',va='top')
        fig.text(.23,.97,title,fontsize=8.5,va='top')
        fig.text(.23,.86,f'Mean across 10 mice; {direction} is better',fontsize=6.7,color='.3')
        y=np.asarray(values,dtype=float)
        span=float(np.ptp(y)); pad=max(span*.30,.001)
        ax.plot(range(5),y,'o-',color='.2',lw=1,ms=5.5)
        for j,value in enumerate(y):
            label=f'{value:.3f}' if 'bits' in ylabel else f'{value:.1f}'
            ax.text(j,value+pad*.20,label,ha='center',fontsize=6.3)
        ax.set(xticks=range(5),xticklabels=MODELS,xlabel='Model',ylabel=ylabel,
               xlim=(-.45,4.45),ylim=(float(y.min())-pad,float(y.max())+pad))
        ax.yaxis.set_major_locator(MaxNLocator(nbins=4))
        ax.ticklabel_format(axis='y',style='plain',useOffset=False)
        if 'BIC' in ylabel:
            ax.axhline(0,c='.75',lw=.65,ls=':')
        for ext in ['png','pdf','svg']:
            fig.savefig(path.with_suffix('.'+ext),dpi=300,facecolor='white')
        book.savefig(fig)
        plt.close(fig)


def main():
    p=argparse.ArgumentParser(__doc__)
    p.add_argument('--output',type=Path,required=True)
    p.add_argument('--resume',action='store_true')
    p.add_argument('--seeds',type=int,nargs='+',default=[12345,23456])
    p.add_argument('--n-reps',type=int,default=30)
    args=p.parse_args()
    args.output.mkdir(parents=True,exist_ok=args.resume)
    cache=args.output/'training_score_cache';cache.mkdir(exist_ok=args.resume)
    logging.getLogger('src.ddm.simulator').setLevel(logging.WARNING)
    logging.getLogger('src.ddm.ddm').setLevel(logging.WARNING)
    score_path=ROOT/'dissemination/paper_control/tables/heldout_nll_per_mouse_2026-10-29.csv'
    inventory_path=ROOT/'dissemination/reviewer_2026-11-13/control_fold_inventory.csv'
    input_path=DDM/'ddm_inputs_global.npz'
    scores=pd.read_csv(score_path);scores=scores[scores.model.isin(MODELS)].copy()
    mice=sorted(scores.mouse.unique());assert len(mice)==10
    assert not scores.duplicated(['mouse','model']).any()
    inv=pd.read_csv(inventory_path);inv=inv[inv.model.isin(MODELS)]
    total=inv.groupby(['mouse','model']).agg(n_test=('n_test','sum'),nll=('test_nll','sum'),folds=('fold','nunique'))
    for row in scores.itertuples():
        z=total.loc[(row.mouse,row.model)]
        assert z.folds==5 and z.n_test==row.control_trials
        assert np.isclose(z.nll,row.test_nll)
    inputs=responded_only(load_inputs(input_path))
    hashes={str(f):digest(f) for f in [score_path,inventory_path,input_path,Path(__file__),ROOT/'scripts/ddm/fit_mouse_ddm.py',ROOT/'src/ddm/likelihood_calculator_censored.py']}
    null_rows=[]
    for mouse in mice:
        rows=np.flatnonzero((inputs['subject_id']==mouse)&(inputs['sched_pulse_type']==0))
        fold=cv_folds(inputs['condition'][rows],5)
        y=inputs['choice'][rows]
        for k in range(5):
            train=y[fold!=k];test=y[fold==k];prob=float(train.mean());assert 0<prob<1
            assert len(test)==int(inv[(inv.mouse==mouse)&(inv.model=='C')&(inv.fold==k)].n_test.iloc[0])
            ll=float(np.sum(test*np.log(prob)+(1-test)*np.log1p(-prob)))
            null_rows.append({'mouse':mouse,'fold':k,'n_train':len(train),'n_test':len(test),'p_right_training':prob,'null_choice_loglik':ll})
    null=pd.DataFrame(null_rows)
    null_total=null.groupby('mouse').null_choice_loglik.sum()
    scores['joint_test_logscore_bits_per_trial']=-scores.test_nll/(scores.control_trials*np.log(2))
    scores['choice_test_gain_bits_per_trial']=(-scores.choice-scores.mouse.map(null_total))/(scores.control_trials*np.log(2))
    assert int(scores[scores.model=='C'].control_trials.sum())==14014
    null.to_csv(args.output/'training_only_choice_nulls.csv',index=False)
    scores.to_csv(args.output/'test_bits_per_mouse.csv',index=False)
    training=[];fit_inventory=[]
    start=time.monotonic()
    for mouse in mice:
        rows=np.flatnonzero((inputs['subject_id']==mouse)&(inputs['sched_pulse_type']==0))
        stimulus_cache={}
        for key in MODELS:
            folder,variant,nominal,extrema,leak=SPECS[key]
            path=DDM/folder/f'{mouse}_{variant}_control.pkl'
            fit=pickle.load(path.open('rb'));fit_hash=digest(path);hashes[str(path)]=fit_hash
            assert fit['n_train']==len(rows) and fit['success']
            assert fit['split']=='control' and bool(fit.get('nominal_input'))==nominal
            assert bool(fit.get('extrema_samples'))==extrema
            assert not fit.get('fixed_guess_bias',False)
            assert fit['likelihood_params']=={'method':'qmle_censored','nbins':9,'rt_nllh_weight':1.,'include_censored':False}
            free=fit['free_parameters'];n_params=len(free)
            fit_inventory.append({'mouse':mouse,'model':key,'path':str(path),'sha256':fit_hash,'n_train':len(rows),'k':n_params,'free_parameters':';'.join(free),'stored_train_nll':fit['train_nll']})
            model=None
            for seed in args.seeds:
                cp=cache/f'{mouse}_{key}_seed{seed}_reps{args.n_reps}.json'
                if cp.exists():
                    rec=json.loads(cp.read_text());assert rec['fit_sha256']==fit_hash and rec['input_sha256']==hashes[str(input_path)]
                else:
                    if nominal not in stimulus_cache:
                        stimulus_cache[nominal]=select(inputs,rows,nominal=nominal)
                    data,stim=stimulus_cache[nominal]
                    if model is None:
                        model=make_model(variant,'ucla' if mouse.startswith('PSUIM') else 'uw',False,
                                         leak_bounds=leak,responded=True,extrema_samples=extrema,nominal_input=nominal)
                    nll=float(heldout_nll(model,fit['parameters'],data,stim,args.n_reps,seed=seed))
                    assert np.isfinite(nll)
                    rec={'mouse':mouse,'model':key,'seed':seed,'n_reps':args.n_reps,'n_train':len(rows),'k':n_params,
                         'training_nll_independent_seed':nll,'bic_qmle':2*nll+n_params*np.log(len(rows)),
                         'fit_sha256':fit_hash,'input_sha256':hashes[str(input_path)]}
                    cp.write_text(json.dumps(rec,indent=2)+'\n')
                training.append(rec)
            if model is not None:
                model.simulator.clear_cache();del model;gc.collect();torch.cuda.empty_cache()
            print(f'{mouse} {key}: training scores evaluated ({time.monotonic()-start:.1f}s)',flush=True)
        del stimulus_cache
    tr=pd.DataFrame(training)
    reference=tr[tr.model=='C'].set_index(['mouse','seed']).bic_qmle
    tr['delta_bic_vs_C']=[r.bic_qmle-reference.loc[(r.mouse,r.seed)] for r in tr.itertuples()]
    tr.to_csv(args.output/'independent_training_scores.csv',index=False)
    pd.DataFrame(fit_inventory).to_csv(args.output/'full_control_fit_inventory.csv',index=False)
    per=tr.groupby(['mouse','model'],as_index=False).agg(bic_qmle=('bic_qmle','mean'),delta_bic_vs_C=('delta_bic_vs_C','mean'))
    per.to_csv(args.output/'bic_per_mouse.csv',index=False)
    group=scores.groupby('model')[['joint_test_logscore_bits_per_trial','choice_test_gain_bits_per_trial']].mean().loc[MODELS]
    group['delta_bic_vs_C']=per.groupby('model').delta_bic_vs_C.mean().loc[MODELS]
    group.to_csv(args.output/'group_metrics.csv')
    seed_groups=tr.groupby(['seed','model']).delta_bic_vs_C.mean().unstack('model')[MODELS]
    seed_groups.to_csv(args.output/'delta_bic_group_by_seed.csv')
    with PdfPages(args.output/'information_metrics.pdf') as book:
        draw(group.joint_test_logscore_bits_per_trial,'Joint test log score','Test choice + RT log score\n(bits/trial)','higher','B',args.output/'test_joint_bits',book)
        draw(group.choice_test_gain_bits_per_trial,'Choice prediction gain','Choice test gain over bias null\n(bits/trial)','higher','B',args.output/'test_choice_gain_bits',book)
        draw(group.delta_bic_vs_C,'Complexity-adjusted model fit','Mean ΔBIC relative to C','lower','C',args.output/'delta_bic',book)
    manifest={'scope':'Score transformations, training-only choice null and independent fixed-parameter training rescoring; no fitting.',
              'models':MODELS,'mice':mice,'seeds':args.seeds,'simulation_repetitions':args.n_reps,
              'formulas':{'joint_test_bits':'-saved_test_nll/(n_test*ln(2)); joint quantile log score, not a Bernoulli-normalized information gain',
                          'choice_gain_bits':'(-saved_choice_test_nll - training-only Bernoulli null test log likelihood)/(n_test*ln(2))',
                          'bic':'2*independent_training_nll + k*ln(n_train); QMLE-based approximation',
                          'delta_bic':'BIC_model-BIC_C within mouse/seed, average seeds, then equal-mouse mean'},
              'reference':{'bits_doi':'10.1038/s41593-021-01007-z','bits_equation':'22; 2021 preprint, 2022 publication',
                           'bic_doi':'10.7554/eLife.55365','bic_equation':'17'},
              'cautions':['Choice-only gain excludes RT, unlike joint score.','Joint quantile score is not a continuous RT log density.',
                          'BIC is based on the quantile fitting objective; do not interpret as an exact Bayes factor.',
                          'Independent scores at fixed fitted parameters retain simulation uncertainty.','No error bars or new inferential tests.'],
              'source_hashes':hashes,'checks':{'saved_test_scores_match_fold_inventory':True,'all_training_counts_match_test_population':True,
                                            'five_converged_full_control_fits_per_mouse':True,'training_only_nulls':True,
                                            'actual_free_parameter_counts_used':True}}
    (args.output/'metric_manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    print(group.to_string(),flush=True)
    print('Delta BIC group by seed:\n'+seed_groups.to_string(),flush=True)


if __name__=='__main__':
    main()
