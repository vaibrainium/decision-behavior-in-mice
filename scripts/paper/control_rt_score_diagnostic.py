"""Exact archived-CV RT-bin decomposition and matched conditional RT quantiles."""
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
import numpy as np
import pandas as pd
import torch
from scripts.ddm.fit_mouse_ddm import CENSOR_AT,EVAL_SEED,MIN_RT,MouseDDM,cv_folds,heldout_nll,load_inputs,make_params,responded_only,select
from scripts.paper.style import RC

MODELS=['C','E','ES']
QUANTILES=[.1,.3,.5,.7,.9]
ROOT=Path(__file__).resolve().parents[2]


class CapturedModel(MouseDDM):
    def _simulate_condition(self,stimulus,params,n_reps):
        result=super()._simulate_condition(stimulus,params,n_reps)
        self.scored_simulation=result
        return result


def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()


def decompose(data,sim,coherence,mouse,fold,model):
    records=[];quantiles=[]
    for condition in np.unique(data['condition']):
        obs=data['condition']==condition
        pred=sim.signed_coherence.to_numpy()==condition
        pc=sim.loc[pred,'choice'].to_numpy();pr=sim.loc[pred,'rt'].to_numpy()
        responded=int((pc>=0).sum())
        coh=int(np.rint(np.unique(coherence[obs]).item()*100))
        assert responded>0,'Empty prediction condition must be handled as an explicit penalty before further use'
        for side in [0,1]:
            od=data['rt'][obs&(data['choice']==side)];md=pr[pc==side]
            base={'mouse':mouse,'fold':fold,'model':model,'condition':int(condition),'coh':coh,'choice':side}
            prob=(len(md)+.5)/(responded+1)
            records.append({**base,'component':'choice','bin':0,'n_obs':len(od),'n_sim':len(md),'probability':prob,
                            'nll':-len(od)*np.log(prob),'lower_s':np.nan,'upper_s':np.nan})
            if len(od)<9:continue
            edges=np.quantile(od,np.linspace(0,1,10));edges[0]=-np.inf;edges[-1]=np.inf
            oc=np.histogram(od,bins=edges)[0];mc=np.histogram(md,bins=edges)[0]
            probs=(mc+.5)/(len(md)+4.5)
            np.testing.assert_allclose(probs.sum(),1)
            for j in range(9):
                records.append({**base,'component':'rt','bin':j+1,'n_obs':int(oc[j]),'n_sim':int(mc[j]),'probability':probs[j],
                                'nll':-oc[j]*np.log(probs[j]),'lower_s':edges[j],'upper_s':edges[j+1]})
            oq=np.quantile(od,QUANTILES)
            mq=np.quantile(md,QUANTILES) if len(md) else np.full(5,np.nan)
            for q,observed,predicted in zip(QUANTILES,oq,mq):
                quantiles.append({**base,'quantile':q,'n_obs_cell':len(od),'n_sim_choice':len(md),
                                  'observed_rt_s':observed,'predicted_rt_s':predicted,'bias_s':predicted-observed})
    return pd.DataFrame(records),pd.DataFrame(quantiles)


def plots(out,qgroup,bingroup,cohgroup,mouseparts):
    colors={'C':'.15','E':'#D55E00','ES':'#0072B2'}
    with plt.rc_context({**RC,'font.family':'DejaVu Sans'}):
        fig,axes=plt.subplots(2,2,figsize=(180/25.4,135/25.4))
        fig.subplots_adjust(left=.10,right=.98,bottom=.13,top=.84,hspace=.70,wspace=.38)
        fig.suptitle('Why mean RT curves and held-out scores can rank differently',fontsize=9,y=.98)
        ax=axes[0,0]
        for model in MODELS:
            z=qgroup[qgroup.model==model];ax.plot(z['quantile'],z.mae_ms,'o-',c=colors[model],ms=3,lw=1,label=model)
        ax.set(xlabel='Conditional RT quantile',ylabel='Mean absolute quantile error (ms)',title='Matched held-out RT quantile accuracy')
        ax.legend(frameon=False,ncol=3,fontsize=6)
        ax=axes[0,1]
        for model in ['E','ES']:
            z=bingroup[bingroup.model==model];ax.plot(z['bin'],z.adv_per1000,'o-',c=colors[model],ms=3,lw=1,label='C versus '+model)
        ax.axhline(0,c='.7',ls=':',lw=.7);ax.set(xlabel='Observed RT bin (1 = fastest; 9 = slowest)',ylabel='Mean RT score advantage for C\n(NLL units / 1,000 controls)',title='Exact score contribution by RT bin',xticks=range(1,10))
        ax.legend(frameon=False,fontsize=6)
        ax=axes[1,0]
        for model in ['E','ES']:
            z=cohgroup[(cohgroup.model==model)&(cohgroup.component=='rt')];ax.plot(z.coh,z.adv_per1000,'o-',c=colors[model],ms=3,lw=1)
        ax.axhline(0,c='.7',ls=':',lw=.7);ax.set(xlabel='Signed coherence (%)',ylabel='Mean RT score advantage for C\n(NLL units / 1,000 controls)',title='Where the RT advantage originates',xticks=[-100,-36,0,36,100])
        ax=axes[1,1]
        mice=sorted(mouseparts.mouse.unique())
        for j,model in enumerate(['E','ES']):
            z=mouseparts[(mouseparts.model==model)&(mouseparts.component=='rt')].set_index('mouse').loc[mice]
            ax.plot(range(len(mice)),z.adv_per1000,'o-',c=colors[model],ms=3,lw=.7)
        ax.axhline(0,c='.7',ls=':',lw=.7);ax.set(xticks=range(len(mice)),xticklabels=mice,ylabel='RT score advantage for C\n(NLL units / 1,000 controls)',title='Individual-mouse contributions')
        ax.tick_params(axis='x',rotation=60,labelsize=5.5)
        for ax in axes.flat:ax.title.set_fontsize(7)
        fig.text(.10,.025,'Diagnostic only. Positive score differences favor C; no new significance tests. All curves use CV fits.',fontsize=6,color='.3')
        for ext in ['png','pdf','svg']:fig.savefig(out/f'control_rt_diagnostic.{ext}',dpi=300,facecolor='white')
        plt.close(fig)


def main():
    p=argparse.ArgumentParser(__doc__);p.add_argument('--output',type=Path,required=True);p.add_argument('--resume',action='store_true')
    a=p.parse_args();a.output.mkdir(parents=True,exist_ok=a.resume);cache=a.output/'fold_cache';cache.mkdir(exist_ok=a.resume)
    for logger in ['src.ddm.simulator','src.ddm.ddm','fontTools']:logging.getLogger(logger).setLevel(logging.WARNING)
    ip=Path('/mnt/data/processed/ddm/ddm_inputs_global.npz');invp=ROOT/'dissemination/reviewer_2026-11-13/control_fold_inventory.csv'
    inv=pd.read_csv(invp);inv=inv[inv.model.isin(MODELS)].copy()
    assert torch.cuda.is_available(),'Exact archive matching requires original CUDA backend'
    inputs=responded_only(load_inputs(ip));ih=digest(ip)
    pieces=[];quantiles=[];checks=[];hashes={str(ip):ih,str(invp):digest(invp),str(Path(__file__)):digest(Path(__file__))}
    start=time.monotonic();pop={}
    for mouse in sorted(inv.mouse.unique()):
        rows=np.flatnonzero((inputs['subject_id']==mouse)&(inputs['sched_pulse_type']==0));pop[mouse]=len(rows)
        folds=cv_folds(inputs['condition'][rows],5)
        for fold in range(5):
            test=rows[folds==fold];data,stim=select(inputs,test)
            coherence=inputs['signed_coherence'][test]
            for model in MODELS:
                row=inv[(inv.mouse==mouse)&(inv.fold==fold)&(inv.model==model)].iloc[0]
                path=Path(row.path);fit=pickle.load(path.open('rb'));fh=digest(path);hashes[str(path)]=fh
                assert fit['n_test']==len(test) and fit['n_train']==len(rows)-len(test)
                assert fit['likelihood_params']=={'method':'qmle_censored','nbins':9,'rt_nllh_weight':1.,'include_censored':False}
                cp=cache/f'{mouse}_fold{fold}_{model}.pkl'
                if cp.exists():
                    rec=pickle.load(cp.open('rb'));assert rec['fit_sha256']==fh and rec['input_sha256']==ih
                else:
                    free,fixed=make_params(fit['variant'],fit['guess_model'],fixed_guess_bias=fit['fixed_guess_bias'],
                        leak_bounds=fit['leak_bounds'],extrema_samples=fit.get('extrema_samples',False),nominal_input=fit.get('nominal_input',False))
                    rig=np.unique(inputs['data_source'][test]).item()
                    fitted=CapturedModel(free,fixed,device='cuda',likelihood_params=fit['likelihood_params'],min_rt=MIN_RT[rig],censor_at=CENSOR_AT)
                    official=heldout_nll(fitted,fit['parameters'],data,stim,fit['n_reps'],seed=EVAL_SEED)
                    sim=fitted.scored_simulation
                    np.testing.assert_allclose(official,row.test_nll,rtol=0,atol=1e-8)
                    np.testing.assert_array_equal(sim.signed_coherence,np.tile(data['condition'],fit['n_reps']))
                    bins,q=decompose(data,sim,coherence,mouse,fold,model)
                    np.testing.assert_allclose(bins.nll.sum(),official,rtol=0,atol=1e-8)
                    rec={'fit_sha256':fh,'input_sha256':ih,'bins':bins,'quantiles':q,'official_nll':official,'n_reps':fit['n_reps'],'seed':EVAL_SEED}
                    with cp.open('wb') as file:pickle.dump(rec,file)
                    fitted.simulator.clear_cache();del fitted,sim;gc.collect();torch.cuda.empty_cache()
                pieces.append(rec['bins']);quantiles.append(rec['quantiles'])
                checks.append({'mouse':mouse,'fold':fold,'model':model,'n_test':len(test),'archived_nll':row.test_nll,'recomputed_nll':rec['official_nll'],
                               'decomposed_nll':rec['bins'].nll.sum(),'n_reps':rec['n_reps'],'seed':rec['seed']})
        print(f'{mouse}: all 15 CV scores reproduced ({time.monotonic()-start:.1f}s)',flush=True)
    bins=pd.concat(pieces,ignore_index=True);q=pd.concat(quantiles,ignore_index=True);check=pd.DataFrame(checks)
    assert sum(pop.values())==14014
    keys=['mouse','fold','condition','coh','choice','component','bin']
    wide=bins.pivot(index=keys,columns='model',values='nll')
    assert wide.notna().all().all()
    diffs=[]
    for model in ['E','ES']:
        z=(wide[model]-wide['C']).rename('adv_nll').reset_index();z['model']=model;diffs.append(z)
    diffs=pd.concat(diffs,ignore_index=True)
    diffs['adv_per1000']=diffs.adv_nll*1000/diffs.mouse.map(pop)
    mouseparts=diffs.groupby(['mouse','model','component'],as_index=False).adv_per1000.sum()
    group=mouseparts.groupby(['model','component'],as_index=False).adv_per1000.agg(['mean','sem']).reset_index()
    old=pd.read_csv(ROOT/'dissemination/paper_control/tables/heldout_group_2026-10-29.csv')
    historical=[]
    for row in group.itertuples():
        expected=old[(old.model==row.model)&(old.part==row.component)]['mean'].item()
        historical.append({'model':row.model,'component':row.component,'exact_mean':row.mean,
                           'historical_mean':expected,'exact_minus_historical':row.mean-expected})
    pd.DataFrame(historical).to_csv(a.output/'historical_component_comparison.csv',index=False)
    for model in ['E','ES']:
        total=group[group.model==model]['mean'].sum()
        expected=old[(old.model==model)&(old.part=='total')]['mean'].item()
        np.testing.assert_allclose(total,expected,atol=1e-8)
    bmouse=diffs[diffs.component=='rt'].groupby(['mouse','model','bin']).adv_per1000.sum()
    full=pd.MultiIndex.from_product([sorted(pop),['E','ES'],range(1,10)],names=['mouse','model','bin'])
    bmouse=bmouse.reindex(full,fill_value=0).reset_index()
    bgroup=bmouse.groupby(['model','bin'],as_index=False).adv_per1000.mean()
    cmouse=diffs.groupby(['mouse','model','component','coh']).adv_per1000.sum()
    full=pd.MultiIndex.from_product([sorted(pop),['E','ES'],['choice','rt'],sorted(bins.coh.unique())],names=['mouse','model','component','coh'])
    cmouse=cmouse.reindex(full,fill_value=0).reset_index();cgroup=cmouse.groupby(['model','component','coh'],as_index=False).adv_per1000.mean()
    # Quantile display: compare the same eligible fold/condition/choice cells in each model.
    assert q.predicted_rt_s.notna().all()
    q['weighted_bias']=q.bias_s*q.n_obs_cell
    qm=q.groupby(['mouse','model','quantile'],as_index=False).agg(n=('n_obs_cell','sum'),weighted_bias=('weighted_bias','sum'))
    qm['bias_ms']=1000*qm.weighted_bias/qm.n
    qgroup=qm.groupby(['model','quantile'],as_index=False).bias_ms.mean()
    q['weighted_abs_error']=q.bias_s.abs()*q.n_obs_cell
    qa=q.groupby(['mouse','model','quantile'],as_index=False).agg(n=('n_obs_cell','sum'),weighted_abs_error=('weighted_abs_error','sum'))
    qa['mae_ms']=1000*qa.weighted_abs_error/qa.n
    qag=qa.groupby(['model','quantile'],as_index=False).mae_ms.mean()
    qgroup=qgroup.merge(qag,on=['model','quantile'])
    for name,frame in [('fold_score_verification',check),('bin_scores',bins),('conditional_quantiles',q),('score_differences',diffs),
            ('score_by_mouse_component',mouseparts),('score_group_components',group),('score_by_rt_bin',bgroup),('score_by_coherence',cgroup),
            ('quantile_bias_per_mouse',qm),('quantile_bias_group',qgroup),('quantile_absolute_error_per_mouse',qa),('quantile_absolute_error_group',qag)]:frame.to_csv(a.output/(name+'.csv'),index=False)
    plots(a.output,qgroup,bgroup,cgroup,mouseparts)
    (a.output/'manifest.json').write_text(json.dumps({'scope':'Exact decomposition of archived held-out C/E/ES control scores; no fitting or pulse analysis',
        'source_hashes':hashes,'models':MODELS,'n_mice':10,'n_controls':14014,'folds_per_mouse':5,
        'cv_evaluation_seed':int(EVAL_SEED),'binning':'Original test-fold/condition/choice quantiles, nine RT bins; omit RT if n<9; alpha=.5',
        'aggregation':'Add component contributions over folds within mouse; normalize by all mouse control trials; equal-mouse group mean',
        'quantile_bias_aggregation':'Within mouse, observed-cell-count-weighted fold/condition/choice signed and absolute quantile errors on RT-scored cells; then equal mouse mean',
        'checks':{'all150_archived_scores_match':True,'all150_decompositions_match':True,'group_choice_plus_rt_matches_archived_total':True,
                  'historical_component_caveat':'E RT mean differs by 0.00015548 NLL/1000 controls from older separately rescored component table; exact decomposition matches original total. See historical_component_comparison.csv.',
                  'no_empty_prediction_conditions':True,'conditional_quantiles_available_all_models':True}},indent=2)+'\n')
    print(group.to_string(index=False),flush=True)
    print('RT bin contributions:\n'+bgroup.to_string(index=False),flush=True)
    print('Quantile bias:\n'+qgroup.to_string(index=False),flush=True)


if __name__=='__main__':main()
