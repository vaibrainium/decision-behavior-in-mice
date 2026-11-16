"""Signed pulse contrasts by predicted pre-choice bias, on common support.

Descriptive responded-trial contrast, no current-RT stratification. Bias uses
the prefix-fitted choice filter, never current choice/RT. Block intervals hold
the fitted state model and common-support weights fixed; they are exploratory.
"""
import numpy as np
import pandas as pd
from scripts.behavior.history_dynamics import OUT,block_weights,sha,write_json
from scripts.ddm.rescore_fits import inputs
from scripts.ddm.pulse_leak_urgency_signatures import observed


def estimate(g,weights,cells,standard):
    tab=g[['stage','coh','regime','sign']].copy()
    tab['n']=weights;tab['right']=weights*g.choice.to_numpy()
    tab=tab.groupby(['stage','coh','regime','sign'])[['n','right']].sum()
    values=[]
    for regime in ['near_neutral','biased']:
        for sign in [-1,1]:
            delta=[]
            for stage,coh in cells:
                p=tab.loc[(stage,coh,regime,sign)];c=tab.loc[(0,coh,regime,0)]
                delta.append(100*sign*(p.right/p.n-c.right/c.n)if min(p.n,c.n)>0 else np.nan)
            values.append(np.dot(standard,delta))
    return np.array(values)


def run(reps=400):
    x=inputs();obs=observed(x,['PSUIM6','PSUIM7'])
    g=pd.read_pickle(OUT/'cache/aligned_trials.pkl')
    pred=pd.read_pickle(OUT/'cache/states_v2_grid15_predictions.pkl')
    # State cache uses aggregate row; established DDM pulse estimators use the
    # responded-input row. Match through unique agg_code, not raw NPZ index.
    identity=pd.DataFrame({'trial_id':x['agg_code'].astype(str),'row':np.arange(len(x['rt']))})
    link=g[['aggregate_row','trial_id']].merge(identity,on='trial_id',validate='one_to_one')
    pred=pred.merge(link[['aggregate_row','row']],on='aggregate_row',validate='one_to_one')
    z=g.merge(pred[['aggregate_row','bias_continuous']],on='aggregate_row',validate='one_to_one')
    z=z.merge(link[['aggregate_row','row']],on='aggregate_row',validate='one_to_one')
    z=z[z.row.isin(obs.row)].copy()
    z['regime']=np.where(z.bias_continuous.abs()<.5,'near_neutral','biased')
    z['coh']=z.coherence_pct;z['stage']=z.scheduled_pulse.abs();z['sign']=np.sign(z.scheduled_pulse)
    rng=np.random.default_rng(11419);rows=[];support=[];counts=[]
    for mouse,v in z.groupby('mouse'):
        v=v.reset_index(drop=True)
        n=v.groupby(['stage','coh','regime','sign']).size()
        for key,num in n.items():counts.append(dict(mouse=mouse,stage=key[0],coh=key[1],regime=key[2],sign=key[3],n=num))
        cells=[];weights=[]
        for stage in sorted(set(v.stage)-{0}):
            for coh in sorted(v.coh.unique()):
                keys=[(stage,coh,r,s)for r in ['near_neutral','biased']for s in [-1,1]]
                keys +=[(0,coh,r,0)for r in ['near_neutral','biased']]
                if all(n.get(k,0)>=5 for k in keys):
                    cells.append((stage,coh));weights.append(sum(n[k]for k in keys[:4]))
        if not cells:
            rows.append(dict(mouse=mouse,status='no common cells with >=5 per sign/regime/control'));continue
        w=np.asarray(weights)/np.sum(weights)
        for (stage,coh),weight in zip(cells,w):support.append(dict(mouse=mouse,stage=stage,coh=coh,weight=weight))
        point=estimate(v,np.ones(len(v)),cells,w)
        boots=np.array([estimate(v,block_weights(v,rng),cells,w)for _ in range(reps)])
        for i,(regime,sign)in enumerate([(r,s)for r in ['near_neutral','biased']for s in [-1,1]]):
            valid=np.isfinite(boots[:,i]);ci=np.quantile(boots[valid,i],[.025,.975])
            rows.append(dict(mouse=mouse,regime=regime,sign=sign,effect_pp=point[i],lo=ci[0],hi=ci[1],
                successful_bootstraps=int(valid.sum()),n_bootstrap=reps,n_common_cells=len(cells),
                n_regime=int((v.regime==regime).sum()),status='exploratory conditional-on-state-fit interval'))
    pd.DataFrame(rows).to_csv(OUT/'pulse_by_pretrial_bias.csv',index=False)
    pd.DataFrame(support).to_csv(OUT/'pulse_by_pretrial_bias_support.csv',index=False)
    pd.DataFrame(counts).to_csv(OUT/'pulse_by_pretrial_bias_counts.csv',index=False)
    write_json(OUT/'pulse_by_pretrial_bias_manifest.json',dict(source_sha256=sha(__file__),
        threshold_abs_latent_bias_logodds=.5,cohort='PSUIM6/7, original symmetric low-coherence responded sample, prefix test blocks',
        standardization='Same pooled pulse-count weights over common coherence/stage cells in both regimes and signs; minimum five per cell',
        interval='Within-session 50-record blocks; state fits/threshold/common support/weights held fixed',
        limitations=['Responded-trial selection','No current RT conditioning','No population test from two mice',
                     'Does not propagate state-parameter uncertainty; exploratory']))
    print(pd.DataFrame(rows).round(3).to_string(index=False))


if __name__=='__main__':run()
