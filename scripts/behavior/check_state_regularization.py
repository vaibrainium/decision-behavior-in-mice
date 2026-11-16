"""Nested prefix tuning of the common GLM penalty for continuous bias.

Both static and dynamic candidates select among the same five penalties using
only the last available training block. This checks sensitivity of the original
fixed-penalty comparison, particularly for mice with few trials.
"""
import json
import time
import numpy as np
import pandas as pd
from scipy import special,stats
from scripts.behavior.history_dynamics import OUT,RIDGE,design,logistic,sha,write_json
from scripts.behavior.predictive_bias_states import bce,fit,predict


def scaled(X,lam):
    Z=X.copy();Z[:,1:]*=np.sqrt(RIDGE/lam);return Z


def run():
    g=pd.read_pickle(OUT/'cache/aligned_trials.pkl')
    base=pd.read_pickle(OUT/'cache/history_regularization_predictions.pkl')
    results=[];selection=[];predictions=[];models={}
    for mouse,z in g.groupby('mouse',sort=True):
        tic=time.time();z=z.reset_index(drop=True);X,names=design(z,history=True)
        v=base[base.mouse==mouse].copy().reset_index(drop=True)
        v['p_continuous_tuned']=np.nan
        for f in [2,3,4]:
            inner=z.fold.to_numpy()<f-1;valid=z.fold.to_numpy()==f-1
            tr=z.fold.to_numpy()<f;te=z.fold.to_numpy()==f;seen=z.fold.to_numpy()<=f
            candidates=[]
            for lam in [.01,.1,1.,10.,100.]:
                Z=scaled(X,lam);beta,ok=logistic(Z[inner],z.choice.to_numpy()[inner]);assert ok
                best,restarts=fit(z[inner],Z[inner],'continuous',beta)
                p=predict(z[z.fold<f],Z[z.fold.to_numpy()<f],best.x,'continuous')
                p=p[z.loc[z.fold<f,'fold'].to_numpy()==f-1,0]
                score=bce(z.loc[valid,'choice'].to_numpy(),p).sum()
                candidates.append((score,lam,best.x))
                selection.append(dict(mouse=mouse,fold=f,penalty=lam,inner_validation_nll=score,
                                      converged=bool(best.success),selected=False))
            score,lam,start=min(candidates,key=lambda r:r[0]);Z=scaled(X,lam)
            selection[-5+[r[1]for r in candidates].index(lam)]['selected']=True
            beta,ok=logistic(Z[tr],z.choice.to_numpy()[tr]);assert ok
            best,restarts=fit(z[tr],Z[tr],'continuous',beta,extra_start=start)
            assert best.success,(mouse,f,restarts)
            p=predict(z[seen],Z[seen],best.x,'continuous')
            p=p[z.loc[seen,'fold'].to_numpy()==f,0]
            v.loc[v.fold==f,'p_continuous_tuned']=p
            models[(mouse,f)]=dict(penalty=lam,parameters=best.x,starts=restarts,names=names)
        row={'mouse':mouse,'n_test':len(v)}
        for tag in ['history1','history10']:
            row[f'continuous_tuned_gain_vs_{tag}_tuned_bits']=np.mean(bce(v.choice,v[f'p_{tag}_tuned'])-bce(v.choice,v.p_continuous_tuned))/np.log(2)
        row['continuous_tuned_gain_vs_original_static_bits']=np.mean(bce(v.choice,v.p_static)-bce(v.choice,v.p_continuous_tuned))/np.log(2)
        results.append(row);predictions.append(v)
        print('TUNED',mouse,'seconds',round(time.time()-tic,1),row,flush=True)
    tab=pd.DataFrame(results);tab.to_csv(OUT/'state_regularization_sensitivity.csv',index=False)
    pd.DataFrame(selection).to_csv(OUT/'state_regularization_selection.csv',index=False)
    pd.concat(predictions,ignore_index=True).to_pickle(OUT/'cache/state_regularization_predictions.pkl')
    pd.to_pickle(models,OUT/'cache/continuous_regularization_models.pkl')
    rows=[]
    for c in tab.columns[2:]:
        a=tab[c].to_numpy();ci=stats.t.interval(.95,len(a)-1,loc=a.mean(),scale=stats.sem(a))
        rows.append(dict(metric=c,mean=a.mean(),lo=ci[0],hi=ci[1],n_positive=int((a>0).sum()),
                         inference='Uncorrected descriptive sensitivity interval; no new primary test'))
    pd.DataFrame(rows).to_csv(OUT/'state_regularization_group_estimates.csv',index=False)
    write_json(OUT/'state_regularization_manifest.json',dict(source_sha256=sha(__file__),
        penalties=[.01,.1,1.,10.,100.],selection='Nested last-prefix-block prediction, no outer-test tuning',
        limitation='Same sessions, responded choices; no unique latent-process interpretation'))


if __name__=='__main__':run()
