"""Audit paired pulse psychometrics using unchanged WLS objective and bounds."""
import argparse
import hashlib
import itertools
import json
from pathlib import Path
import numpy as np
import pandas as pd
from scipy.optimize import least_squares
from scipy.special import expit
from scipy import stats


def main():
    p=argparse.ArgumentParser(__doc__);p.add_argument('--input',type=Path,required=True);p.add_argument('--output',type=Path,required=True)
    a=p.parse_args();a.output.mkdir(parents=True,exist_ok=False)
    source=a.input/'source_data/fig4_A_psychometric_mouse.csv';oldpath=a.input/'source_data/fig4_B_paired_parameters.csv'
    data=pd.read_csv(source);old=pd.read_csv(oldpath).set_index(['mouse','pulse']);rows=[];runs=[]
    bounds=([-100,1e-5,1e-5,1e-5],[100,30,.4,.4])
    for (mouse,pulse),z in data[data.pulse.isin([-1,1])].groupby(['mouse','pulse']):
        original=old.loc[(mouse,pulse)];xx=z.coherence_pct.to_numpy();yy=z['mean'].to_numpy();ww=np.sqrt(z['size'].to_numpy())
        def residual(q):return ww*(q[2]+(1-q[2]-q[3])*expit(q[1]*(xx-q[0]))-yy)
        x0=[original.alpha,original.beta,original.lower_asymptote,1-original.upper_asymptote]
        starts=[x0]+[[m,b,l,u] for m,b,(l,u) in itertools.product([-40,0,40],[.015,.05,.15],[(.05,.05),(.25,.15)])]
        outcomes=[]
        for j,seed in enumerate(starts):
            res=least_squares(residual,np.clip(seed,bounds[0],bounds[1]),bounds=bounds,max_nfev=3000,ftol=1e-10,xtol=1e-10,gtol=1e-10)
            value=float(np.sum(res.fun**2));outcomes.append((value,res))
            runs.append({'mouse':mouse,'pulse':pulse,'start':j,'weighted_sse':value,'alpha':res.x[0],'beta':res.x[1],
                         'gamma':res.x[2],'lambda':res.x[3],'success':res.success,'nfev':res.nfev})
        sse,best=min(outcomes,key=lambda q:q[0]);assert sse<=original.weighted_sse+1e-8
        rows.append({'mouse':mouse,'pulse':pulse,'original_alpha':original.alpha,'original_beta':original.beta,
            'original_sse':original.weighted_sse,'best_alpha':best.x[0],'best_beta':best.x[1],
            'best_gamma':best.x[2],'best_lambda':best.x[3],'best_sse':sse,'sse_improvement':original.weighted_sse-sse,
            'jacobian_condition_number':float(np.linalg.cond(best.jac.T@best.jac)),
            'alpha_at_bound':bool(np.isclose(abs(best.x[0]),100)),
            'beta_at_lower_bound':bool(np.isclose(best.x[1],1e-5,atol=1e-9))})
        print(mouse,int(pulse),'SSE improvement',original.weighted_sse-sse,'alpha',original.alpha,'->',best.x[0],flush=True)
    result=pd.DataFrame(rows);result.to_csv(a.output/'fit_audit.csv',index=False);pd.DataFrame(runs).to_csv(a.output/'all_starts.csv',index=False)
    tests=[]
    for version in ['original','best']:
        for parameter in ['alpha','beta']:
            w=result.pivot(index='mouse',columns='pulse',values=version+'_'+parameter).sort_index();d=(w[1]-w[-1]).to_numpy()
            signs=np.array(list(itertools.product([-1,1],repeat=10)));p=float(np.mean(np.abs((signs*d).mean(axis=1))>=abs(d.mean())-1e-12))
            tests.append({'version':version,'parameter':parameter,'mean_difference':float(d.mean()),'median_difference':float(np.median(d)),
                          'n_negative':int((d<0).sum()),'p_exact_signflip':p,'p_paired_t':float(stats.ttest_rel(w[1],w[-1]).pvalue)})
    t=pd.DataFrame(tests);t['p_holm']=np.nan
    for version in ['original','best']:
        ix=t[t.version==version].index.to_numpy();values=t.loc[ix,'p_exact_signflip'].to_numpy();order=np.argsort(values);run=0
        for j,k in enumerate(order):run=max(run,(2-j)*values[k]);t.loc[ix[k],'p_holm']=min(run,1.)
    t.to_csv(a.output/'test_audit.csv',index=False)
    (a.output/'manifest.json').write_text(json.dumps({'scope':'Same equation/bounds/WLS objective,19 starts per curve, no data exclusions or model family changes',
        'source_hashes':{str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in [source,oldpath,Path(__file__)]},
        'selection':'Minimum WLS residual sum of squares only; no p-value selection',
        'interpretation':'Optimization audit does not resolve parameter identifiability or make tests confirmatory'},indent=2)+'\n')
    print(t.to_string(index=False),flush=True)


if __name__=='__main__':main()
