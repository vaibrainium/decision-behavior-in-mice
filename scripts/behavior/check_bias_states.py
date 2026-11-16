"""Prespecified numerical/interpretive sensitivities for bias-state diagnosis."""
import time
import numpy as np
import pandas as pd
from scipy import special
from scripts.behavior.history_dynamics import OUT,DATA,design,logistic,sha,write_json
from scripts.behavior.predictive_bias_states import bce,dynamics,fit,predict


def run():
    g=pd.read_pickle(OUT/'cache/aligned_trials.pkl')
    pred=pd.read_pickle(OUT/'cache/states_v2_grid15_predictions.pkl')
    cache=pd.read_pickle(OUT/'cache/states_v2_grid15_fits.pkl')
    raw=pd.read_csv(DATA/'aggregate_data.csv',low_memory=False)
    raw['aggregate_row']=np.arange(len(raw))
    side=raw.choice.map({0.:-1.,1.:1.}).fillna(0.)
    raw['win']=side*(raw.outcome==1);raw['loss']=side*(raw.outcome==0)
    for lag in range(2,11):
        for kind in ['win','loss']:
            raw[f'{kind}_lag{lag}']=raw.groupby('idx_session')[kind].shift(lag).fillna(0.)
    columns=[f'{kind}_lag{lag}'for lag in range(2,11)for kind in ['win','loss']]
    extra=raw.loc[g.aggregate_row,columns].to_numpy(float)
    results=[];fine=[];sensitivity_predictions=[];fine_models={}
    for mouse,indices in g.groupby('mouse',sort=True).indices.items():
        tic=time.time();z=g.iloc[indices].reset_index(drop=True)
        X,names=design(z,history=True);H=np.column_stack([X,extra[indices]])
        v=pred[pred.mouse==mouse].copy().reset_index(drop=True)
        v['p_history10']=np.nan
        for kind in ['continuous','discrete']:v[f'p_stationary_{kind}']=np.nan
        for f in [2,3,4]:
            tr=z.fold.to_numpy()<f;te=z.fold.to_numpy()==f;seen=z.fold.to_numpy()<=f
            test=v.fold.to_numpy()==f
            beta,ok=logistic(H[tr],z.choice.to_numpy()[tr]);assert ok
            v.loc[test,'p_history10']=special.expit(H[te]@beta)
            for kind in ['continuous','discrete']:
                fitted=cache[(mouse,f,kind)]['parameters']
                a,bias,pi=dynamics(kind,fitted[X.shape[1]:])
                v.loc[test,f'p_stationary_{kind}']=special.expit((X[te]@fitted[:X.shape[1]])[:,None]+bias).dot(pi)
            if mouse in ['PSUIM6','PSUIM7']:
                original=cache[(mouse,f,'continuous')]['parameters']
                beta,ok=logistic(X[tr],z.choice.to_numpy()[tr]);assert ok
                best,records=fit(z[tr],X[tr],'continuous',beta,n_grid=31,extra_start=original)
                p=predict(z[seen],X[seen],best.x,'continuous',n_grid=31)
                p=p[z.loc[seen,'fold'].to_numpy()==f,0]
                old=v.loc[test,'p_continuous'].to_numpy()
                fine.append({'mouse':mouse,'fold':f,'converged':best.success,
                    'n_test':int(te.sum()),'sigma':np.exp(best.x[-2]),'tau_rows':np.exp(best.x[-1]),
                    'nll_grid31':bce(z.loc[te,'choice'].to_numpy(),p).sum(),
                    'nll_grid15':bce(z.loc[te,'choice'].to_numpy(),old).sum(),
                    'mean_absolute_prediction_change':np.mean(np.abs(p-old)),
                    'max_absolute_prediction_change':np.max(np.abs(p-old))})
                fine_models[(mouse,f)]={'parameters':best.x,'starts':records}
        row={'mouse':mouse,'n_test':len(v)};y=v.choice.to_numpy()
        for kind in ['continuous','discrete']:
            row[f'{kind}_filter_gain_vs_stationary_bits']=np.mean(bce(y,v[f'p_stationary_{kind}'])-bce(y,v[f'p_{kind}']))/np.log(2)
            row[f'{kind}_gain_vs_history10_bits']=np.mean(bce(y,v.p_history10)-bce(y,v[f'p_{kind}']))/np.log(2)
        row['history10_gain_vs_history1_bits']=np.mean(bce(y,v.p_static)-bce(y,v.p_history10))/np.log(2)
        results.append(row);sensitivity_predictions.append(v)
        print('CHECK',mouse,'seconds',round(time.time()-tic,1),row,flush=True)
    pd.DataFrame(results).to_csv(OUT/'state_sensitivities_by_mouse.csv',index=False)
    pd.DataFrame(fine).to_csv(OUT/'continuous_grid31_check.csv',index=False)
    pd.concat(sensitivity_predictions,ignore_index=True).to_pickle(OUT/'cache/state_sensitivity_predictions.pkl')
    pd.to_pickle(fine_models,OUT/'cache/continuous_grid31_fits.pkl')
    write_json(OUT/'state_sensitivity_manifest.json',{'source_sha256':sha(__file__),
        'long_history':'same nuisance/evidence covariates plus rewarded/unrewarded choice at recorded-row lags 2-10',
        'stationary':'same fitted model emissions, replace filtered pre-choice state distribution by stationary prior',
        'grid_check':'refit continuous approximation at 31 states; PSUIM6/7; training-only starts',
        'inference':'sensitivity estimates, no additional significance fishing'})


if __name__=='__main__':run()
