"""Improve scaling of two-state transition optimization; preserve v1 outputs."""
import json
import numpy as np
import pandas as pd
from scipy import optimize,special
from scripts.behavior.history_dynamics import OUT,acf_table,design,logistic,sha,write_json
from scripts.behavior.predictive_bias_states import (
    bce,inference,layout,objective,predict,rt_validation,
)


def unscale(q,nb):
    p=q.copy();p[nb+1:]=special.expit(q[nb+1:]);return p


def scaled_objective(q,X,y,lay):
    nb=X.shape[1];p=unscale(q,nb)
    loss,grad=objective(p,X,y,lay,'discrete')
    grad[nb+1:]*=p[nb+1:]*(1-p[nb+1:])
    return loss,grad


def refit(g,X,start):
    nb=X.shape[1];lay=layout(g);y=g.choice.to_numpy(float)
    seeds=[start.copy()]
    for d,p0,p1 in [(.5,.9,.9),(1.,.98,.98),(1.5,.995,.995)]:
        seeds.append(np.r_[start[:nb],d,p0,p1])
    best=None;records=[]
    for par in seeds:
        q=par.copy();q[nb+1:]=special.logit(q[nb+1:])
        r=optimize.minimize(scaled_objective,q,args=(X,y,lay),jac=True,method='L-BFGS-B',
            bounds=[(None,None)]*nb+[(0.,6.)]+[(0.,special.logit(.9995))]*2,
            options={'maxiter':1000,'ftol':1e-11,'gtol':1e-5,'maxls':40})
        records.append({'objective':r.fun,'success':bool(r.success),'nit':r.nit,
                        'message':str(r.message),'max_abs_gradient':float(np.max(np.abs(r.jac)))})
        if best is None or r.fun<best.fun:best=r
    return unscale(best.x,nb),best,records


def run():
    g=pd.read_pickle(OUT/'cache/aligned_trials.pkl')
    pred=pd.read_pickle(OUT/'cache/states_grid15_predictions.pkl')
    cache=pd.read_pickle(OUT/'cache/states_grid15_fits.pkl')
    fits=pd.read_csv(OUT/'states_grid15_fits.csv')
    rows=[];acf=[];records=[];predictions=[]
    for mouse,z in g.groupby('mouse',sort=True):
        z=z.reset_index(drop=True);X,names=design(z,history=True)
        v=pred[pred.mouse==mouse].copy().reset_index(drop=True)
        for f in [2,3,4]:
            tr=z.fold.to_numpy()<f;te=z.fold.to_numpy()==f;seen=z.fold.to_numpy()<=f
            start=cache[(mouse,f,'discrete')]['parameters']
            par,best,starts=refit(z[tr],X[tr],start)
            p=predict(z[seen],X[seen],par,'discrete')
            p=p[z.loc[seen,'fold'].to_numpy()==f]
            ix=v.fold.to_numpy()==f
            v.loc[ix,'p_discrete']=p[:,0];v.loc[ix,'bias_discrete']=p[:,1]
            v.loc[ix,'variance_discrete']=p[:,2]
            cache[(mouse,f,'discrete')]['parameters']=par
            old=fits[(fits.mouse==mouse)&(fits.fold==f)&(fits.model=='discrete')].iloc[0]
            records.append({'mouse':mouse,'fold':f,'model':'discrete','converged':bool(best.success),
                'old_penalized_training_nll':old.penalized_training_nll,'penalized_training_nll':best.fun,
                'parameters':json.dumps(dict(offset=par[-3],p00=par[-2],p11=par[-1])),
                'starts':json.dumps(starts)})
        zz=z[z.fold>=2].reset_index(drop=True)
        row={'mouse':mouse,'n_test':len(v)}
        for kind in ['static','continuous','discrete']:
            row[f'{kind}_nll']=bce(v.choice.to_numpy(),v[f'p_{kind}'].to_numpy()).sum()
            tab=acf_table(zz,v.choice.to_numpy()-v[f'p_{kind}'].to_numpy())
            tab['mouse']=mouse;tab['model']=kind;acf+=tab.to_dict('records')
        for kind in ['continuous','discrete']:
            row[f'{kind}_gain_bits']=(row['static_nll']-row[f'{kind}_nll'])/len(v)/np.log(2)
        row['discrete_minus_continuous_bits']=(row['continuous_nll']-row['discrete_nll'])/len(v)/np.log(2)
        row.update(rt_validation(zz,v));rows.append(row);predictions.append(v)
        print('REFINED',mouse,'bits',row['discrete_gain_bits'],flush=True)
    tab=pd.DataFrame(rows);tag='states_v2_grid15'
    pd.concat(predictions,ignore_index=True).to_pickle(OUT/f'cache/{tag}_predictions.pkl')
    pd.to_pickle(cache,OUT/f'cache/{tag}_fits.pkl')
    pd.DataFrame(records).to_csv(OUT/'discrete_refinement.csv',index=False)
    merged=pd.concat([fits[fits.model=='continuous'],pd.DataFrame(records)],ignore_index=True)
    merged.to_csv(OUT/f'{tag}_fits.csv',index=False)
    tab.to_csv(OUT/f'{tag}_mouse_summary.csv',index=False)
    pd.DataFrame(acf).to_csv(OUT/f'{tag}_residual_acf.csv',index=False)
    inference(tab).to_csv(OUT/f'{tag}_group_inference.csv',index=False)
    write_json(OUT/f'{tag}_manifest.json',{'source_sha256':sha(__file__),
        'original_model_source_sha256':sha('scripts/behavior/predictive_bias_states.py'),
        'change':'Optimize the same two-state model in logit self-transition coordinates; more iterations/starts',
        'original_outputs':'states_grid15_* retained; continuous fits identical',
        'selection':'training likelihood only; no change to endpoints or test blocks'})
    print(inference(tab).round(6).to_string(index=False),flush=True)


if __name__=='__main__':run()
