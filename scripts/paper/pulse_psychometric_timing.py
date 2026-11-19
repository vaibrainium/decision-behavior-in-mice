"""Exploratory control-relative midpoint/slope versus scheduled pulse time."""
import argparse
import hashlib
import json
from pathlib import Path
import warnings
import numpy as np
import pandas as pd
from scipy.optimize import least_squares
from scipy.special import expit
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from src.utils.pmf_utils import fit_psychometric_function
from scripts.paper.style import RC, LEFT_COLOR, RIGHT_COLOR

SOURCE=Path('/mnt/data/processed/pulse_followup/20261023T191030Z_fa8de8b/data/trial_table.csv')
STAGES=['early','middle','late']


def load_trials():
    t=pd.read_csv(SOURCE,low_memory=False)
    t=t[t.in_ddm_input.astype(bool)&t.response_side.ne('none')&t.signs_scheduled_symmetric.astype(bool)&t.pulse_category.isin(['control','positive','negative'])].copy()
    pulse=t.pulse_category.ne('control');duration=t.recorded_duration_s.where(pulse)
    t['onset_s']=t.recorded_onset_s.where(pulse,t.control_onset_s)
    t['offset_s']=t.onset_s+duration.where(pulse,t.rig.map(duration.groupby(t.rig).median()))
    t=t[(t.rt_s>=t.offset_s)&((t.rt_s-t.onset_s)>=.1)].copy()
    t['direction']=np.where(t.pulse_category.eq('control'),0,t.pulse_sign).astype(int)
    t['right']=t.response_side.eq('R').astype(int)
    assert len(t[t.onset_stratum.isin(['early','middle'])])==19313
    assert (t[t.onset_stratum.isin(['early','middle'])].direction!=0).sum()==8529
    return t


def fixed_fit(z,ctl):
    x=z.coherence_pct.to_numpy();y=z['mean'].to_numpy();w=np.sqrt(z['size'].to_numpy())
    gamma,lam=ctl['lapse_rate'],ctl['guess_rate']
    def residual(q):return w*(gamma+(1-gamma-lam)*expit(q[1]*(x-q[0]))-y)
    span=max(float(np.ptp(x)),1)
    runs=[least_squares(residual,np.clip([m,b],[-100,1e-5],[100,30]),bounds=([-100,1e-5],[100,30]),max_nfev=3000,ftol=1e-10,xtol=1e-10,gtol=1e-10)
          for m in np.linspace(x.min(),x.max(),5)[1:4] for b in np.array([3,10,30])/span]
    good=[r for r in runs if r.success and np.all(np.isfinite(r.fun))]
    if not good:raise RuntimeError('All fixed-asymptote fits failed')
    best=min(good,key=lambda r:np.sum(r.fun**2))
    return {'mean':best.x[0],'var':best.x[1],'lapse_rate':gamma,'guess_rate':lam},float(np.sum(best.fun**2)),bool(np.isclose(abs(best.x[0]),100)),bool(np.isclose(best.x[1],30) or np.isclose(best.x[1],1e-5)),len(good),float(np.linalg.cond(best.jac.T@best.jac))


def render_absolute_alpha(source, output):
    """Author-requested alpha levels, preserving delta beta; no refitting."""
    manifest=json.loads((source/'manifest.json').read_text())
    f=pd.read_csv(source/'fits.csv');delta=pd.read_csv(source/'paired_control_differences.csv')
    summaries=[]
    for name,mice,times in [('same_six',manifest['primary_mice'],STAGES),('early_middle_ten',manifest['early_middle_mice'],STAGES[:2])]:
        z=delta[delta.mouse.isin(mice)&delta.stage.isin(times)]
        g=z.groupby(['method','stage','direction'])[['alpha','delta_beta']].agg(['mean','sem','count'])
        g.columns=['_'.join(c) for c in g.columns];g=g.reset_index();g['population']=name;summaries.append(g)
        for method,title in [('free4','Independent four-parameter fits'),('fixed_asymptotes','Sensitivity: pulse curves share control asymptotes')]:
            with plt.rc_context(RC):
                fig,axes=plt.subplots(1,2,figsize=(7.5,3.35),layout='constrained')
                for ax,param,label in zip(axes,['alpha','delta_beta'],['α: psychometric midpoint (% coherence)','Δβ: pulse − control (per % coherence)']):
                    for direction,color,text in [(-1,LEFT_COLOR,'Left pulse'),(1,RIGHT_COLOR,'Right pulse')]:
                        q=g[(g.method==method)&(g.direction==direction)].set_index('stage').loc[times]
                        ax.errorbar(np.arange(len(times)),q[f'{param}_mean'],yerr=q[f'{param}_sem'],fmt='o-',color=color,capsize=3,label=text,lw=1.2)
                    ax.axhline(0,color='.7',ls=':',lw=.7)
                    labels=['Early\n50 ms','Middle\n233 ms','Late\n417 ms'] if name=='same_six' else [s.capitalize() for s in times]
                    ax.set(xticks=np.arange(len(times)),xticklabels=labels,xlabel='Scheduled pulse onset' if name=='same_six' else 'Scheduled pulse time',ylabel=label,title='Pulse-time effect on α' if param=='alpha' else 'Pulse-time effect on β')
                axes[0].legend();fig.suptitle(f'{title}: same {len(mice)} mice at every shown time\nMean ± SEM; α shown directly, β relative to control',fontsize=8)
                for ext in ['png','pdf','svg']:fig.savefig(output/f'{name}_{method}.{ext}',dpi=250)
                plt.close(fig)
    pd.concat(summaries).to_csv(output/'group_parameters.csv',index=False)
    (output/'manifest.json').write_text(json.dumps({'source_results':str(source),'source_fits_sha256':hashlib.sha256((source/'fits.csv').read_bytes()).hexdigest(),'source_differences_sha256':hashlib.sha256((source/'paired_control_differences.csv').read_bytes()).hexdigest(),'source_script_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'alpha':'Absolute midpoint, no control subtraction','beta':'Pulse-minus-stage-matched-control slope change','uncertainty':'Across-mouse SEM of fitted coefficients; curve-estimation uncertainty not propagated','refitted':False,'primary_mice':manifest['primary_mice'],'early_middle_mice':manifest['early_middle_mice']},indent=2)+'\n')


def main():
    parser=argparse.ArgumentParser(__doc__);parser.add_argument('--output',type=Path,required=True);parser.add_argument('--from-results',type=Path);a=parser.parse_args();a.output.mkdir(parents=True,exist_ok=False)
    if a.from_results is not None:
        render_absolute_alpha(a.from_results,a.output)
        return
    t=load_trials();t[['trial_id','mouse','rig','onset_stratum','direction','coherence_pct','right','rt_s','onset_s','offset_s']].to_csv(a.output/'eligible_trials.csv',index=False)
    cells=t.groupby(['mouse','rig','onset_stratum','direction','coherence_pct'],as_index=False).right.agg(mean='mean',size='size',n_right='sum')
    cells.to_csv(a.output/'mouse_cells.csv',index=False)
    timing=t[t.direction!=0].groupby(['rig','onset_stratum']).onset_s.agg(['min','median','max']).reset_index();timing.to_csv(a.output/'timing.csv',index=False)
    fits=[];curve=[]
    for (mouse,stage),panel in cells.groupby(['mouse','onset_stratum']):
        ctl=None
        for direction in [0,-1,1]:
            z=panel[panel.direction==direction].sort_values('coherence_pct')
            with warnings.catch_warnings(record=True) as caught:
                warnings.simplefilter('always')
                f=fit_psychometric_function(z.coherence_pct.to_numpy(),z['mean'].to_numpy(),z['size'].to_numpy(),'logit_4')
            co=f.coefs_
            if direction==0:ctl=dict(co)
            variants=[('free4',co,f.weighted_sse_,f.fit_diagnostics_['at_bound'][0],f.fit_diagnostics_['at_bound'][1],f.fit_diagnostics_['n_success'],float(np.linalg.cond(f.covar_)))]
            if direction==0:variants.append(('fixed_asymptotes',co,f.weighted_sse_,f.fit_diagnostics_['at_bound'][0],f.fit_diagnostics_['at_bound'][1],f.fit_diagnostics_['n_success'],float(np.linalg.cond(f.covar_))))
            else:variants.append(('fixed_asymptotes',*fixed_fit(z,ctl)))
            for method,q,sse,abound,bbound,success,condition in variants:
                fits.append({'mouse':mouse,'rig':panel.rig.iloc[0],'stage':stage,'direction':direction,'method':method,
                    'alpha':q['mean'],'beta':q['var'],'lower_asymptote':q['lapse_rate'],'upper_asymptote':1-q['guess_rate'],
                    'weighted_sse':sse,'alpha_at_bound':abound,'beta_at_bound':bbound,'condition_number':condition,
                    'n_success':success,'n_coherences':len(z),'n_trials':int(z['size'].sum()),'coherence_min':float(z.coherence_pct.min()),'coherence_max':float(z.coherence_pct.max())})
                grid=np.linspace(-100,100,401);prob=q['lapse_rate']+(1-q['guess_rate']-q['lapse_rate'])*expit(q['var']*(grid-q['mean']))
                curve.append(pd.DataFrame({'mouse':mouse,'stage':stage,'direction':direction,'method':method,'coherence_pct':grid,'p_right':prob}))
        print(mouse,stage,'complete',flush=True)
    f=pd.DataFrame(fits);f.to_csv(a.output/'fits.csv',index=False);pd.concat(curve).to_csv(a.output/'curves.csv',index=False)
    control=f[f.direction==0][['mouse','stage','method','alpha','beta']].rename(columns={'alpha':'control_alpha','beta':'control_beta'})
    delta=f[f.direction!=0].merge(control,on=['mouse','stage','method'],validate='many_to_one')
    delta['delta_alpha']=delta.alpha-delta.control_alpha;delta['delta_beta']=delta.beta-delta.control_beta
    delta.to_csv(a.output/'paired_control_differences.csv',index=False)
    stages=t.groupby('mouse').onset_stratum.agg(set);complete=sorted(stages[stages.map(lambda z:set(STAGES)<=z)].index)
    earlymid=sorted(stages[stages.map(lambda z:{'early','middle'}<=z)].index)
    summaries=[]
    for name,mice,times in [('same_six',complete,STAGES),('early_middle_ten',earlymid,STAGES[:2])]:
        z=delta[delta.mouse.isin(mice)&delta.stage.isin(times)]
        g=z.groupby(['method','stage','direction'])[['delta_alpha','delta_beta']].agg(['mean','sem','count'])
        g.columns=['_'.join(c) for c in g.columns];g=g.reset_index();g['population']=name;summaries.append(g)
        for method,title in [('free4','Independent four-parameter fits'),('fixed_asymptotes','Sensitivity: pulse curves share matched-control asymptotes')]:
            with plt.rc_context(RC):
                fig,axes=plt.subplots(1,2,figsize=(7.5,3.35),layout='constrained')
                for ax,param,label in zip(axes,['alpha','beta'],['Δα: pulse − control (% coherence)','Δβ: pulse − control (per % coherence)']):
                    for direction,color,text in [(-1,LEFT_COLOR,'Left pulse'),(1,RIGHT_COLOR,'Right pulse')]:
                        q=g[(g.method==method)&(g.direction==direction)].set_index('stage').loc[times]
                        ax.errorbar(np.arange(len(times)),q[f'delta_{param}_mean'],yerr=q[f'delta_{param}_sem'],fmt='o-',color=color,capsize=3,label=text,lw=1.2)
                    ax.axhline(0,color='.7',ls=':',lw=.7)
                    ax.set(xticks=np.arange(len(times)),xticklabels=[s.capitalize() for s in times],xlabel='Scheduled pulse time',ylabel=label,title=f'Pulse-time effect on {param}')
                axes[0].legend();fig.suptitle(f'{title}\nSame {len(mice)} mice at every shown time; mean ± SEM',fontsize=8)
                for ext in ['png','pdf','svg']:fig.savefig(a.output/f'{name}_{method}.{ext}',dpi=250)
                plt.close(fig)
    pd.concat(summaries).to_csv(a.output/'group_differences.csv',index=False)
    audit={'primary_mice':complete,'early_middle_mice':earlymid,'n_eligible_trials':len(t),'scope':'Exploratory; Figure4 mask plus restored late stratum; scheduled direction/time, symmetric cells, after offset and >=100ms after onset','parameter_definitions':'alpha=horizontal midpoint; beta=positive slope coefficient. Plots show within-mouse pulse minus stage-matched control differences, including negative delta beta. Alpha has opposite sign to original notebook additive offset.','uncertainty':'Across-mouse SEM of paired fitted coefficients, not curve-estimation uncertainty. No new tests.','methods':{'free4':'Updated helper default multistart trial-count WLS, all4 parameters free within original helper bounds','fixed_asymptotes':'Sensitivity: same mouse/time control asymptotes fixed for each pulse curve; 9-start WLS for alpha/beta'},'no_forced_timing_trend':True,'source_hashes':{str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in [SOURCE,Path(__file__),Path('src/utils/pmf_utils.py'),Path('notebooks/1.0-psychometric-analysis.ipynb')]}}
    (a.output/'manifest.json').write_text(json.dumps(audit,indent=2)+'\n')
    print(pd.concat(summaries).to_string(index=False),flush=True)

if __name__=='__main__':main()
