"""Training-only regularization sensitivity for fixed multi-trial history.

The un-tuned long-history check can overfit short sessions. Select its added
history penalty on the last block of the available training prefix, then refit
the whole prefix. Main state-model results are not changed by this sensitivity.
"""
import numpy as np
import pandas as pd
from scipy import special
from scripts.behavior.history_dynamics import OUT,DATA,RIDGE,design,logistic,sha,write_json
from scripts.behavior.predictive_bias_states import bce


def run():
    g=pd.read_pickle(OUT/'cache/aligned_trials.pkl')
    pred=pd.read_pickle(OUT/'cache/states_v2_grid15_predictions.pkl')
    raw=pd.read_csv(DATA/'aggregate_data.csv',low_memory=False)
    side=raw.choice.map({0.:-1.,1.:1.}).fillna(0.)
    raw['win']=side*(raw.outcome==1);raw['loss']=side*(raw.outcome==0)
    cols=[]
    for lag in range(2,11):
        for kind in ['win','loss']:
            c=f'{kind}_lag{lag}';cols.append(c)
            raw[c]=raw.groupby('idx_session')[kind].shift(lag).fillna(0.)
    extra=raw.iloc[g.aggregate_row.to_numpy()][cols].to_numpy(float)
    summary=[];choices=[];predictions=[]
    for mouse,ix in g.groupby('mouse',sort=True).indices.items():
        z=g.iloc[ix].reset_index(drop=True);X,names=design(z,history=True)
        H=np.column_stack([X,extra[ix]]);nb=X.shape[1];y=z.choice.to_numpy(float)
        v=pred[pred.mouse==mouse].copy().reset_index(drop=True)
        v['p_history10_tuned']=np.nan;v['p_history1_tuned']=np.nan
        for f in [2,3,4]:
            tr=z.fold.to_numpy()<f;te=z.fold.to_numpy()==f
            inner=z.fold.to_numpy()<f-1;validation=z.fold.to_numpy()==f-1
            for tag in ['history1','history10']:
                candidates=[]
                for lam in [.01,.1,1.,10.,100.]:
                    Z=X if tag=='history1'else np.column_stack([X,extra[ix]*np.sqrt(RIDGE/lam)])
                    penalty=lam if tag=='history1'else RIDGE
                    coef,ok=logistic(Z[inner],y[inner],penalty=penalty);assert ok
                    p=np.clip(special.expit(Z[validation]@coef),1e-14,1-1e-14)
                    candidates.append((bce(y[validation],p).sum(),lam,Z,penalty))
                loss,lam,Z,penalty=min(candidates,key=lambda c:c[0])
                coef,ok=logistic(Z[tr],y[tr],penalty=penalty);assert ok
                v.loc[v.fold==f,f'p_{tag}_tuned']=special.expit(Z[te]@coef)
                choices.append(dict(mouse=mouse,fold=f,model=tag,selected_penalty=lam,
                                    inner_validation_nll=loss))
        row={'mouse':mouse,'n_test':len(v)}
        for tag in ['history1','history10']:
            row[f'{tag}_tuned_gain_vs_static_bits']=np.mean(bce(v.choice,v.p_static)-bce(v.choice,v[f'p_{tag}_tuned']))/np.log(2)
            for kind in ['continuous','discrete']:
                row[f'{kind}_gain_vs_{tag}_tuned_bits']=np.mean(bce(v.choice,v[f'p_{tag}_tuned'])-bce(v.choice,v[f'p_{kind}']))/np.log(2)
        summary.append(row);predictions.append(v)
    pd.DataFrame(summary).to_csv(OUT/'history_regularization_sensitivity.csv',index=False)
    pd.DataFrame(choices).to_csv(OUT/'history_regularization_choices.csv',index=False)
    pd.concat(predictions,ignore_index=True).to_pickle(OUT/'cache/history_regularization_predictions.pkl')
    write_json(OUT/'history_regularization_manifest.json',{'source_sha256':sha(__file__),
        'penalties':[.01,.1,1.,10.,100.],
        'selection':'last block of available training prefix, earlier blocks train coefficients; never outer test',
        'history1':'select common ridge penalty',
        'history10':'keep common-covariate ridge 0.1; select added lags 2-10 penalty',
        'purpose':'sensitivity to short-history baseline and long-history overfit, exploratory'})
    print(pd.DataFrame(summary).round(5).to_string(index=False))


if __name__=='__main__':run()
