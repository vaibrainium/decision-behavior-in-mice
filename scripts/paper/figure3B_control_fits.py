"""Observed control psychometrics/choice RT and saved full-control fit predictions."""
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
from scripts.ddm.fit_mouse_ddm import load_inputs, responded_only, select
from scripts.ddm.primacy import make_model, simulate_outcomes
from scripts.paper.figure3_information_metrics import SPECS, MODELS
from scripts.paper.style import RC

ROOT = Path(__file__).resolve().parents[2]
DDM = Path('/mnt/data/processed/ddm')
BLUE = '#0072B2'
ORANGE = '#D55E00'


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def summarize(frame, mouse, model):
    psy = frame.groupby('coh', as_index=False).agg(n_resp=('choice', 'size'), n_right=('choice', 'sum'))
    psy['p_right'] = psy.n_right/psy.n_resp
    rt = frame.groupby(['coh', 'choice'], as_index=False).agg(n_resp=('rt', 'size'), rt_sum=('rt', 'sum'))
    rt['mean_rt'] = rt.rt_sum/rt.n_resp
    return psy.assign(mouse=mouse, model=model), rt.assign(mouse=mouse, model=model)


def draw(out, pg, rg):
    with plt.rc_context({**RC, 'font.family': 'DejaVu Sans'}):
        fig, axes = plt.subplots(2, 5, figsize=(230/25.4, 118/25.4), sharex=True, sharey='row')
        fig.subplots_adjust(left=.075, right=.985, bottom=.12, top=.78, wspace=.12, hspace=.25)
        fig.text(.015,.98,'B',fontsize=12,fontweight='bold',va='top')
        fig.text(.075,.98,'Control behavior and model fits',fontsize=10,va='top')
        fig.text(.075,.91,'Points: data   |   Lines: full-control model fits   |   Shading: data SEM across mice',fontsize=7,color='.3')
        for j,model in enumerate(MODELS):
            p, t = axes[:,j]
            p.set_title(model,fontsize=9,pad=8)
            z=pg[pg.model=='data'];q=pg[pg.model==model]
            p.fill_between(z.coh,z['mean']-z['sem'],z['mean']+z['sem'],color='.5',alpha=.15,lw=0)
            p.plot(z.coh,z['mean'],'o',c='.15',ms=3)
            p.plot(q.coh,q['mean'],'-',c='.15',lw=1)
            p.set(ylim=(-.04,1.04),yticks=[0,.5,1])
            for choice,color,marker in [(1,ORANGE,'o'),(0,BLUE,'s')]:
                z=rg[(rg.model=='data')&(rg.choice==choice)]
                q=rg[(rg.model==model)&(rg.choice==choice)]
                t.fill_between(z.coh,z['mean']-z['sem'],z['mean']+z['sem'],color=color,alpha=.15,lw=0)
                t.plot(z.coh,z['mean'],marker,c=color,ms=2.7)
                t.plot(q.coh,q['mean'],'-',c=color,lw=1)
            t.set(xlabel='Signed coherence (%)',xticks=[-100,-36,0,36,100])
            t.tick_params(axis='x',labelsize=6,rotation=45)
            for ax in (p,t):ax.axvline(0,c='.85',ls=':',lw=.5,zorder=0)
        axes[0,0].set_ylabel('P(right choice)')
        axes[1,0].set_ylabel('Mean RT (s)')
        handles=[plt.Line2D([],[],color=ORANGE,marker='o',lw=1,label='Right choice'),
                 plt.Line2D([],[],color=BLUE,marker='s',lw=1,label='Left choice')]
        fig.legend(handles=handles,loc='upper right',bbox_to_anchor=(.985,.87),ncol=2,frameon=False,fontsize=7)
        for ext in ['png','pdf','svg']:fig.savefig(out/f'figure3B.{ext}',dpi=300,facecolor='white')
        plt.close(fig)


def main():
    p=argparse.ArgumentParser(__doc__)
    p.add_argument('--output',type=Path,required=True)
    p.add_argument('--n-reps',type=int,default=20)
    p.add_argument('--seed',type=int,default=34567)
    p.add_argument('--resume',action='store_true')
    a=p.parse_args();a.output.mkdir(parents=True,exist_ok=a.resume)
    cache=a.output/'prediction_cache';cache.mkdir(exist_ok=a.resume)
    for name in ['src.ddm.simulator','fontTools']:logging.getLogger(name).setLevel(logging.WARNING)
    ip=DDM/'ddm_inputs_global.npz';inputs=responded_only(load_inputs(ip))
    ps=[];rs=[];inventory=[];diagnostics=[];hashes={str(ip):sha(ip),str(Path(__file__)):sha(Path(__file__))}
    start=time.monotonic()
    for mouse in sorted(np.unique(inputs['subject_id'])):
        rows=np.flatnonzero((inputs['subject_id']==mouse)&(inputs['sched_pulse_type']==0))
        coh=np.rint(inputs['signed_coherence'][rows]*100).astype(int)
        obs=pd.DataFrame({'coh':coh,'choice':inputs['choice'][rows],'rt':inputs['rt'][rows]})
        assert obs.rt.between(.3,5).all()
        po,ro=summarize(obs,mouse,'data');ps.append(po);rs.append(ro)
        stimuli={}
        for key in MODELS:
            folder,variant,nominal,extrema,leak=SPECS[key]
            path=DDM/folder/f'{mouse}_{variant}_control.pkl'
            fit=pickle.load(path.open('rb'));fitsha=sha(path);hashes[str(path)]=fitsha
            assert fit['n_train']==len(rows) and fit['success'] and fit['split']=='control'
            assert bool(fit.get('nominal_input'))==nominal and bool(fit.get('extrema_samples'))==extrema
            assert fit['likelihood_params']['include_censored'] is False
            assert nominal or fit['guess_model']=='fast_only'
            inventory.append({'mouse':mouse,'model':key,'fit_path':str(path),'sha256':fitsha,'n_train':len(rows)})
            cp=cache/f'{mouse}_{key}.pkl'
            if cp.exists():
                record=pickle.load(cp.open('rb'))
                assert record['fit_sha256']==fitsha and record['seed']==a.seed and record['n_reps']==a.n_reps
                assert record['input_sha256']==hashes[str(ip)]
            else:
                if nominal not in stimuli:stimuli[nominal]=select(inputs,rows,nominal=nominal)
                data,stim=stimuli[nominal]
                model=make_model(variant,'ucla' if mouse.startswith('PSUIM') else 'uw',False,
                                 leak_bounds=leak,responded=True,extrema_samples=extrema,nominal_input=nominal)
                sim=simulate_outcomes(model,fit['parameters'],stim,data['condition'],a.n_reps,a.seed)
                assert len(sim)==len(rows)*a.n_reps
                valid=(sim.choice>=0)&sim.rt.between(.3,5)
                ids=sim.loc[valid,'trial'].to_numpy(dtype=int)
                frame=pd.DataFrame({'coh':coh[ids],'choice':sim.loc[valid,'choice'].to_numpy(),
                                    'rt':sim.loc[valid,'rt'].to_numpy()})
                pp,rr=summarize(frame,mouse,key)
                record={'fit_sha256':fitsha,'input_sha256':hashes[str(ip)],'seed':a.seed,'n_reps':a.n_reps,
                        'psychometric':pp,'rt':rr,'n_sim':len(sim),'n_resp':len(frame)}
                with cp.open('wb') as f:pickle.dump(record,f)
                del model,sim;gc.collect();torch.cuda.empty_cache()
            ps.append(record['psychometric']);rs.append(record['rt'])
            diagnostics.append({'mouse':mouse,'model':key,'n_sim':record['n_sim'],'n_resp':record['n_resp']})
            print(f'{mouse} {key}: prediction complete ({time.monotonic()-start:.1f}s)',flush=True)
        del stimuli
    pm=pd.concat(ps,ignore_index=True);rm=pd.concat(rs,ignore_index=True)
    observed=pm[pm.model=='data'].set_index(['mouse','coh'])
    assert observed.n_resp.sum()==14014
    # Data RT eligibility alone determines the paired subject/coherence/choice population.
    eligible=rm[(rm.model=='data')&(rm.n_resp>=10)][['mouse','coh','choice']].assign(eligible=True)
    rm=rm.merge(eligible,on=['mouse','coh','choice'],how='left');rm['eligible']=rm.eligible.fillna(False).astype(bool)
    shown=rm[rm.eligible]
    expected=shown[shown.model=='data'].set_index(['mouse','coh','choice']).index
    for key in MODELS:assert shown[shown.model==key].set_index(['mouse','coh','choice']).index.sort_values().equals(expected.sort_values())
    pg=pm.groupby(['model','coh'],as_index=False).agg(mean=('p_right','mean'),sem=('p_right','sem'),n_mice=('mouse','nunique'))
    rg=shown.groupby(['model','coh','choice'],as_index=False).agg(mean=('mean_rt','mean'),sem=('mean_rt','sem'),n_mice=('mouse','nunique'))
    # Verify the only difference from Figure 1 is the known absent model-input trial.
    fp=ROOT/'dissemination/paper_accumulation/draft_2026-11-15/figure1_revision_2026-11-17_v6/source_data/fig1_C_psychometric_mouse.csv'
    f=pd.read_csv(fp).rename(columns={'subject_id':'mouse','signed_coherence':'coh'}).set_index(['mouse','coh'])
    compare=observed[['n_resp','p_right']].join(f[['n_trials','p_right']],rsuffix='_fig1')
    diff=compare[compare.n_resp!=compare.n_trials]
    assert len(diff)==1 and diff.index[0]==('PSUIM7',-100) and (diff.n_trials-diff.n_resp).iloc[0]==1
    stable=compare.drop(index=diff.index)
    np.testing.assert_allclose(stable.p_right,stable.p_right_fig1,atol=1e-12)
    for name,frame in [('psychometric_mouse',pm),('rt_mouse',rm),('psychometric_group',pg),('rt_group',rg),('fit_inventory',pd.DataFrame(inventory)),('simulation_response_counts',pd.DataFrame(diagnostics)),('figure1_population_difference',diff.reset_index())]:frame.to_csv(a.output/(name+'.csv'),index=False)
    draw(a.output,pg,rg)
    (a.output/'manifest.json').write_text(json.dumps({'scope':'Descriptive full-control model predictions, not held-out curves; no fitting',
        'n_mice':10,'n_controls':14014,'n_reps':a.n_reps,'seed':a.seed,'source_hashes':hashes,
        'models':MODELS,'rt_eligibility':'At least 10 observed trials in mouse/coherence/choice cell; identical cells for data/all candidates',
        'aggregation':'Pool simulation response counts and RT sums across repetitions within mouse, then equal-mouse means',
        'figure1_difference':'One additional Figure 1 control trial PSUIM7_14_1_344 is absent in model inputs; B uses modeled population.',
        'checks':{'fifty_successful_control_fits_counts_match':True,'same_rt_mouse_cells_all_candidates':True,'other_figure1_choice_cells_match':True}},indent=2)+'\n')
    (a.output/'caption.md').write_text('''Panel B. Control psychometric and chronometric functions with model fits. Columns show C, E, ES, DDMx and ESx. Top: P(right choice) versus signed coherence. Bottom: mean RT conditional on right (orange circles) or left choice (blue squares), using solid model traces. Points show observed equal-mouse means and shaded bands show pointwise SEM across contributing mice. Lines are fixed-parameter predictions from saved full-control fits on each mouse's actual control input schedules, conditional on a simulated response between 0.3 and 5 s. Predictions pool response counts/RT sums across 20 repetitions within mouse before averaging mice. These are descriptive in-sample fits, distinct from A's held-out test score. RT curves use the same mouse/coherence/choice cells as data, restricted to at least 10 observed trials per cell. Mouse counts vary by cell and are exported. All 14,014 modeled controls are included. Figure 1 includes one additional control trial (PSUIM7_14_1_344) absent from model inputs. No new fits or significance tests. No four-parameter logistic is fitted to these model curves.\n''')
    print('Panel B exported:',a.output,flush=True)


if __name__=='__main__':main()
