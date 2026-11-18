"""Control conditional accuracy versus RT, with notebook-selection audit."""
import argparse
import gc
import hashlib
import json
import logging
import pickle
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import torch
from scripts.ddm.fit_mouse_ddm import load_inputs,responded_only,select
from scripts.ddm.primacy import make_model,simulate_outcomes
from scripts.paper.figure3_information_metrics import SPECS
from scripts.paper.style import RC

ROOT=Path(__file__).resolve().parents[2]
DDM=Path('/mnt/data/processed/ddm')
COHERENCES=[100,36,18,9,0]
COLORS=dict(zip(COHERENCES,['#4C72B0','#DD8452','#55A868','#C44E52','#8172B2']))


def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()


def summarize(frame,source):
    z=frame.copy();z['bin']=np.floor(z.rt_s/.4+1e-10).astype(int)
    z=z.groupby(['mouse','abs_coh','bin'],as_index=False).agg(n_trials=('correct','size'),n_correct=('correct','sum'))
    z['accuracy']=z.n_correct/z.n_trials;z['source']=source
    return z


def coords(group):
    group=group.copy();group['lo_s']=np.maximum(.3,group['bin']*.4)
    group['hi_s']=np.minimum(5.,(group['bin']+1)*.4);group['rt_ms']=1000*(group.lo_s+group.hi_s)/2
    return group


def plot(ax,group,model=None):
    for coh in COHERENCES:
        data=coords(group[(group.source=='data')&(group.abs_coh==coh)]).set_index('bin').reindex(range(13))
        # Preserve missing-bin gaps, rather than connecting across absent observations.
        x=1000*(np.maximum(.3,np.arange(13)*.4)+np.minimum(5.,(np.arange(13)+1)*.4))/2
        color=COLORS[coh]
        if model is None:
            ax.plot(x,data['mean'],'o-',c=color,ms=3,lw=1,label=f'{coh}%')
            ax.fill_between(x,data['mean']-data['sem'],data['mean']+data['sem'],color=color,alpha=.12,lw=0)
        else:
            ax.plot(x,data['mean'],'o',c=color,ms=2.5,label=f'{coh}%')
            pred=coords(group[(group.source==model)&(group.abs_coh==coh)]).set_index('bin').reindex(range(13))
            ax.plot(x,pred['mean'],'-',c=color,lw=1)
    ax.axhline(.5,c='.65',ls=':',lw=.7)
    ax.set(xlim=(250,5050),ylim=(0,1.03),xticks=[500,1500,2500,3500,4500],xlabel='Reaction time (ms)',ylabel='Probability correct')


def main():
    p=argparse.ArgumentParser(__doc__);p.add_argument('--output',type=Path,required=True);p.add_argument('--n-reps',type=int,default=30)
    p.add_argument('--seed',type=int,default=45678);a=p.parse_args();a.output.mkdir(parents=True,exist_ok=False)
    for name in ['src.ddm.ddm','src.ddm.simulator','fontTools']:logging.getLogger(name).setLevel(logging.WARNING)
    vp=Path('/mnt/data/processed/valid_data.csv');ip=DDM/'ddm_inputs_global.npz';v=pd.read_csv(vp)
    scheduled=(~v.is_pulse_trial)|v.pulse_coherence.eq(v.signed_coherence);notebook=v.pulse_type.eq(0)
    contamination=v[notebook&~scheduled].copy();contamination.to_csv(a.output/'notebook_misclassified_controls.csv',index=False)
    # Exact notebook-style response-coded selection and pooled trial means; retained for audit only.
    old=v[notebook].copy();old['bin']=np.floor((old.reaction_time*1000).astype(int)/400).astype(int);old['abs_coh']=old.signed_coherence.abs().astype(int)
    orig=old.groupby(['abs_coh','bin'],as_index=False).outcome.agg(accuracy='mean',n_trials='size');orig['rt_ms']=orig['bin']*400+200
    orig.to_csv(a.output/'notebook_pooled_accuracy.csv',index=False)
    inputs=responded_only(load_inputs(ip));rows=np.flatnonzero(inputs['sched_pulse_type']==0)
    raw=v.set_index('agg_code').loc[inputs['agg_code'][rows]]
    target=(raw.target.to_numpy()>0).astype(int);observed=(inputs['choice'][rows]==target)
    np.testing.assert_array_equal(observed,raw.outcome.to_numpy().astype(bool))
    nonzero=inputs['signed_coherence'][rows]!=0
    np.testing.assert_array_equal(target[nonzero],(inputs['signed_coherence'][rows][nonzero]>0).astype(int))
    assert len(rows)==14014
    obs=pd.DataFrame({'mouse':inputs['subject_id'][rows],'abs_coh':np.rint(abs(inputs['signed_coherence'][rows])*100).astype(int),
                      'rt_s':inputs['rt'][rows],'correct':observed})
    actual=summarize(obs,'data');allframes=[actual];fits=[];counts=[]
    for mouse in sorted(actual.mouse.unique()):
        local=np.flatnonzero((inputs['subject_id']==mouse)&(inputs['sched_pulse_type']==0));rawmouse=v.set_index('agg_code').loc[inputs['agg_code'][local]]
        correct_side=(rawmouse.target.to_numpy()>0).astype(int);coh=np.rint(abs(inputs['signed_coherence'][local])*100).astype(int)
        data,stim=select(inputs,local)
        for key in ['C','E','ES']:
            folder,variant,nominal,extrema,leak=SPECS[key];assert not nominal
            path=DDM/folder/f'{mouse}_{variant}_control.pkl';fit=pickle.load(path.open('rb'));assert fit['n_train']==len(local)
            model=make_model(variant,np.unique(inputs['data_source'][local]).item(),False,responded=True,leak_bounds=leak,extrema_samples=extrema)
            sim=simulate_outcomes(model,fit['parameters'],stim,data['condition'],a.n_reps,a.seed)
            keep=(sim.choice>=0)&sim.rt.between(.3,5);s=sim[keep];ix=s.trial.to_numpy(dtype=int)
            frame=pd.DataFrame({'mouse':mouse,'abs_coh':coh[ix],'rt_s':s.rt.to_numpy(),'correct':s.choice.to_numpy()==correct_side[ix]})
            allframes.append(summarize(frame,key));counts.append({'mouse':mouse,'model':key,'n_sim':len(sim),'n_resp':len(s)})
            fits.append({'mouse':mouse,'model':key,'path':str(path),'sha256':sha(path),'n_train':len(local)})
            model.simulator.clear_cache();del model,sim;gc.collect();torch.cuda.empty_cache()
        del stim
    per=pd.concat(allframes,ignore_index=True)
    # Model summaries use only observed mouse/coherence/bin cells; no minimum-count exclusions.
    cells=actual[['mouse','abs_coh','bin']].assign(observed_cell=True)
    per=per.merge(cells,on=['mouse','abs_coh','bin'],how='left');per['observed_cell']=per.observed_cell.eq(True)
    displayed=per[per.observed_cell]
    group=displayed.groupby(['source','abs_coh','bin'],as_index=False).agg(mean=('accuracy','mean'),sem=('accuracy','sem'),
        n_mice=('mouse','nunique'),n_trials=('n_trials','sum'))
    group=coords(group)
    actual.to_csv(a.output/'data_mouse_accuracy.csv',index=False);per.to_csv(a.output/'all_mouse_accuracy.csv',index=False);group.to_csv(a.output/'group_accuracy.csv',index=False)
    pd.DataFrame(fits).to_csv(a.output/'fit_inventory.csv',index=False);pd.DataFrame(counts).to_csv(a.output/'simulation_counts.csv',index=False)
    with plt.rc_context({**RC,'font.family':'DejaVu Sans'}):
        fig,ax=plt.subplots(figsize=(115/25.4,90/25.4));fig.subplots_adjust(left=.16,right=.96,bottom=.20,top=.79)
        plot(ax,group);ax.set_title('D   Control accuracy versus response time',loc='left',fontsize=8.5,pad=12)
        ax.legend(title='|Coherence|',ncol=3,frameon=False,fontsize=6,title_fontsize=6,loc='lower left')
        fig.text(.16,.90,'Equal-mouse means ± SEM; scheduled controls only',fontsize=6.4,c='.3')
        for ext in ['png','pdf','svg']:fig.savefig(a.output/f'figure3D_conditional_accuracy.{ext}',dpi=300,facecolor='white')
        plt.close(fig)
        fig,axes=plt.subplots(1,3,figsize=(210/25.4,85/25.4),sharey=True)
        fig.subplots_adjust(left=.08,right=.98,bottom=.20,top=.78,wspace=.23)
        for ax,key in zip(axes,['C','E','ES']):plot(ax,group,key);ax.set_title(key,fontsize=9);ax.tick_params(axis='x',rotation=35,labelsize=6)
        axes[0].legend(frameon=False,fontsize=6,ncol=2,loc='lower left');fig.text(.08,.95,'Conditional accuracy: data points and fixed full-control fit predictions',fontsize=9)
        for ext in ['png','pdf','svg']:fig.savefig(a.output/f'model_comparison.{ext}',dpi=300,facecolor='white')
        plt.close(fig)
    audit={'notebook_response_coded_control_count':int(notebook.sum()),'scheduled_controls_in_valid_data':int(scheduled.sum()),
        'scheduled_pulse_trials_in_notebook_control':len(contamination),'modeled_scheduled_controls':len(rows),
        'zero_coherence_correctness':'Agreement with randomized task-assigned target side, not an objective motion direction',
        'binning':'Notebook400ms grid retained; centers use actual response-window overlap, first300–400ms center350, last4800–5000 center4900',
        'aggregation':'Within-mouse mean accuracy; equal-mouse group means/SEM among nonempty cells; all cells/counts exported, no minimum-count exclusions',
        'model_scope':'Descriptive fixed full-control fits C/E/ES; no fitting or unseen-data validation','seed':a.seed,'n_reps':a.n_reps,
        'source_hashes':{str(p):sha(p) for p in [vp,ip,ROOT/'notebooks/1.2-accumulator-analysis.ipynb',Path(__file__)]}}
    (a.output/'manifest.json').write_text(json.dumps(audit,indent=2)+'\n');print(json.dumps({k:v for k,v in audit.items() if k!='source_hashes'},indent=2))


if __name__=='__main__':main()
