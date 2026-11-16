"""Collect independent simulations of the training-only gain feasibility pilot."""
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from scripts.ddm.evidence_gain_feasibility import OUT,FITS,SOURCE,VARIANTS,inputs,sha,write_json
from scripts.ddm.assess_response_delay import Contrast
from scripts.ddm.pulse_leak_urgency_signatures import BINS,observed,pseudo_onsets
from scripts.behavior.history_dynamics import OUT as HISTORY_OUT,block_weights

MICE=['PSUIM6','PSUIM7'];FAMILIES=['fixed','drift','gain'];SEEDS=[415,839];REPS=60
COLORS={'fixed':'#E69F00','drift':'#0072B2','gain':'#009E73'}
LABELS={'fixed':'No trial variability','drift':'Additive drift variability','gain':'Positive evidence gain'}
PRIOR=OUT.parent/'response_delay_2026-11-14'


def run():
    x=inputs();obs=observed(x,MICE);onsets=pseudo_onsets(obs)
    # Bootstrap the original saved-record blocks rather than compressing the
    # selected/retained pulse trials into an artificial chronology.
    aligned=pd.read_pickle(HISTORY_OUT/'cache/aligned_trials.pkl').set_index('trial_id')
    chronology=aligned.loc[x['agg_code'][obs.row.to_numpy()].astype(str)].reset_index(drop=True)
    rng=np.random.default_rng(11427)
    weights=[block_weights(chronology,rng)for _ in range(400)]
    for window,name in [(False,'profile'),(True,'window')]:
        est=Contrast(obs,onsets,window);tab=est.table(np.ones(len(obs)))
        boot=np.array([est(w)for w in weights]);tab['lo_pp'],tab['hi_pp']=np.nanquantile(boot,[.025,.975],axis=0)
        tab.to_csv(OUT/f'data_pulse_{name}.csv',index=False)
        keys=est.outby
        ref=pd.read_csv(PRIOR/f'data_pulse_{name}.csv')
        check=tab.merge(ref,on=keys,suffixes=('','_prior'))
        np.testing.assert_allclose(check.effect_pp,check.effect_pp_prior,atol=1e-10)
    scores=[];profiles=[];windows=[];quantiles=[];parameters=[];outcomes={}
    for mouse in MICE:
        for family in FAMILIES:
            fp=FITS/f'{mouse}_gain_all.pkl'if family=='gain'else SOURCE/f'{mouse}_{VARIANTS[family]}_all.pkl'
            fit=pd.read_pickle(fp)
            parameters.append(dict(mouse=mouse,family=family,**fit['parameters']))
            for seed in SEEDS:
                r=pd.read_pickle(OUT/'cache'/f'eval_{mouse}_{family}_r{REPS}_s{seed}.pkl')
                assert r['fit_sha256']==sha(fp)
                out=r['outcomes'];outcomes[(mouse,family,seed)]=out
                assert len(out)==REPS*r['n']
                assert out.groupby('rep').row.nunique().eq(r['n']).all()
                scores.append({k:v for k,v in r.items()if k not in ['outcomes','fit_sha256']})
                keep=obs[obs.mouse==mouse].set_index('row',drop=False)
                o=out[(out.choice>=0)&out.row.isin(keep.index)]
                m=keep.loc[o.row]
                t=pd.DataFrame({k:m[k].to_numpy()for k in ['row','mouse','rig','coh','s','stage','onset']})
                t['choice']=np.where(o.choice.to_numpy()==1,1,-1);t['rt']=o.rt.to_numpy()
                t['row']=np.arange(len(t))
                for window,target in [(False,profiles),(True,windows)]:
                    est=Contrast(t,onsets,window)
                    target.extend(est.table(np.ones(len(t))).assign(family=family,seed=seed,reps=REPS).to_dict('records'))
                for coh in sorted(set(np.round(x['signed_coherence'][x['subject_id']==mouse]*100).astype(int))):
                    schedules=np.flatnonzero((x['subject_id']==mouse)&(x['sched_pulse_type']==0)&(np.round(x['signed_coherence']*100)==coh))
                    for choice in [0,1]:
                        d=x['rt'][schedules[x['choice'][schedules]==choice]]
                        p=out.loc[out.row.isin(schedules)&(out.choice==choice),'rt'].to_numpy()
                        if len(d)and len(p):
                            for q in [.1,.25,.5,.75,.9]:
                                quantiles.append(dict(mouse=mouse,family=family,seed=seed,coherence_pct=coh,
                                    choice=choice,quantile=q,n_data=len(d),n_sim=len(p),
                                    data_rt_s=np.quantile(d,q),model_rt_s=np.quantile(p,q)))
    score=pd.DataFrame(scores);score.to_csv(OUT/'training_scores_by_seed.csv',index=False)
    ref=score[score.family=='drift'].drop(columns='family')
    delta=score.merge(ref,on=['mouse','seed'],suffixes=('','_drift'))
    for c in ['nll','choice_nll','rt_nll']:delta[f'delta_{c}']=delta[c]-delta[f'{c}_drift']
    delta.to_csv(OUT/'training_differences_from_drift.csv',index=False)
    pd.DataFrame(profiles).to_csv(OUT/'model_pulse_profile.csv',index=False)
    pd.DataFrame(windows).to_csv(OUT/'model_pulse_window.csv',index=False)
    pd.DataFrame(quantiles).to_csv(OUT/'control_rt_quantiles.csv',index=False)
    pd.DataFrame(parameters).to_csv(OUT/'parameters.csv',index=False)
    write_json(OUT/'assessment_audit.json',dict(source_sha256=sha(__file__),
        n_scores=len(score),n_simulated_outcomes=sum(len(v)for v in outcomes.values()),
        input_trials_each_rep_verified=True,fit_hashes_verified=True,choice_rt_terms_additive=True,
        uncertainty='Simulation-seed range; not sampling CI',
        target='Independent simulations of full-training fits, no held-out generalization',
        observed_profile_source=str(OUT/'data_pulse_profile.csv'),
        observed_intervals='400 within-session 50-original-record block resamples; pointwise exploratory',
        observed_point_estimator_matches_prior=True))
    print(delta.groupby(['mouse','family'])[['delta_nll','delta_choice_nll','delta_rt_nll']].mean().round(3).to_string())
    plot(x,outcomes,pd.DataFrame(profiles),delta)


def plot(x,outcomes,profiles,delta):
    plt.rcParams.update({'font.size':9,'pdf.fonttype':42,'ps.fonttype':42,
        'axes.spines.top':False,'axes.spines.right':False})
    data=pd.read_csv(OUT/'data_pulse_profile.csv')
    fig,axes=plt.subplots(2,4,figsize=(15.5,7.4),constrained_layout=True)
    for i,mouse in enumerate(MICE):
        ax=axes[i,0]
        for j,family in enumerate(['fixed','gain']):
            z=delta[(delta.mouse==mouse)&(delta.family==family)]
            for shift,key in [(-.13,'delta_choice_nll'),(.13,'delta_rt_nll')]:
                ax.bar(j+shift,z[key].mean(),width=.25,color=COLORS[family],alpha=.45 if shift<0 else 1.)
                ax.plot(np.full(len(z),j+shift),z[key],'.',color='#333333',ms=3)
        ax.axhline(0,color='black',lw=.6)
        ax.set(title=f'{mouse}: choice (pale) / RT (dark)',xticks=[0,1],xticklabels=['Fixed','Positive gain'],
               ylabel='Training NLL difference versus drift variability')
        ax=axes[i,1];bins=np.linspace(.3,5,48)
        schedules=np.flatnonzero((x['subject_id']==mouse)&(x['sched_pulse_type']==0)&(np.round(x['signed_coherence']*100)==-100))
        vals=x['rt'][schedules[x['choice'][schedules]==0]]
        ax.stairs(np.histogram(vals,bins)[0]/len(vals)/np.diff(bins),bins,color='black',label='Observed',lw=1.8)
        for family in FAMILIES:
            vals=np.concatenate([o.loc[o.row.isin(schedules)&(o.choice==0),'rt'].to_numpy()
                for key,o in outcomes.items()if key[0]==mouse and key[1]==family])
            ax.stairs(np.histogram(vals,bins)[0]/len(vals)/np.diff(bins),bins,color=COLORS[family],label=LABELS[family])
        ax.set(title='Correct −100% control responses',xlabel='Response time (s)',ylabel='Density',xlim=(.3,5))
        if i==0:ax.legend(frameon=False,fontsize=7)
        for j,sign in [(2,1),(3,-1)]:
            ax=axes[i,j];z=data[(data.mouse==mouse)&(data.sign==sign)]
            mid=(np.array(BINS[:-1])+BINS[1:])/2;k=z.bin.to_numpy(int)
            ax.errorbar(mid[k],z.effect_pp,yerr=[z.effect_pp-z.lo_pp,z.hi_pp-z.effect_pp],fmt='o',
                color='black',ms=3,lw=.8,capsize=2)
            for family in FAMILIES:
                p=profiles[(profiles.mouse==mouse)&(profiles.family==family)&(profiles.sign==sign)]
                t=p.groupby('bin').effect_pp.agg(['mean','min','max']);ix=t.index.to_numpy(int)
                ax.plot(mid[ix],t['mean'],color=COLORS[family],lw=1.3)
                ax.fill_between(mid[ix],t['min'],t['max'],color=COLORS[family],alpha=.12)
            ax.axhline(0,color='black',lw=.6)
            ax.set(title='Positive pulse'if sign==1 else'Negative pulse',xlabel='Time after pulse onset (s)',
                   ylabel='Choice shift toward pulse (pp)',xlim=(.25,5),ylim=(-10,30))
    fig.suptitle('Positive evidence gain: bounded training-data feasibility\nFresh simulation seeds assess numerical noise; these are full-data fits, not held-out predictions',fontsize=12)
    fig.savefig(OUT/'gain_feasibility.pdf');fig.savefig(OUT/'gain_feasibility.png',dpi=160);plt.close(fig)


if __name__=='__main__':run()
