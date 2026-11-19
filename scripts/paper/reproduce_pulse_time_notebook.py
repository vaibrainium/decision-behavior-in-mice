"""Directly reproduce notebook population model, preserving equation and trial weights."""
import argparse
import ast
import hashlib
import json
from pathlib import Path
import re
import warnings
import numpy as np
import pandas as pd
from scipy.optimize import curve_fit
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from scripts.paper.style import RC,LEFT_COLOR,RIGHT_COLOR

NOTEBOOK=Path('notebooks/1.0-psychometric-analysis.ipynb')
VALID=Path('/mnt/data/processed/valid_data.csv')
PARAMS=[f'alpha_{i}' for i in range(1,5)]+[f'beta_{i}' for i in range(1,5)]+['lapse','gamma']


def notebook_fit(data,nb):
    saved={}
    def capture(*args,**kwargs):
        result=curve_fit(*args,**kwargs);saved.update(params=result[0],covariance=result[1],x=np.asarray(args[1]),y=np.asarray(args[2]),sigma=kwargs['sigma']);return result
    namespace={'np':np,'pd':pd,'curve_fit':capture}
    tree=ast.parse(''.join(nb['cells'][5]['source']))
    for node in tree.body:
        if isinstance(node,ast.FunctionDef) and node.name in ['pulse_time_glm_function','pulse_time_glm_fit','get_pulse_time_psych_data']:
            exec(compile(ast.Module(body=[node],type_ignores=[]),'notebook-cell5','exec'),namespace)
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter('always');_,params,_=namespace['get_pulse_time_psych_data'](data)
    np.testing.assert_allclose(saved['params'],list(params.values()),rtol=0,atol=0)
    saved['fit_function']=namespace['pulse_time_glm_function'];saved['warnings']=list(dict.fromkeys(str(w.message) for w in caught))
    return saved


def main():
    parser=argparse.ArgumentParser(__doc__);parser.add_argument('--eligible',type=Path,required=True);parser.add_argument('--output',type=Path,required=True);a=parser.parse_args();a.output.mkdir(parents=True,exist_ok=False)
    nb=json.loads(NOTEBOOK.read_text());valid=pd.read_csv(VALID);eligible=pd.read_csv(a.eligible)
    eligible=eligible.assign(pulse_type=eligible.direction*eligible.onset_stratum.map({'early':1,'middle':2,'late':3}),signed_coherence=eligible.coherence_pct,choice=eligible.right)
    output='\n'.join(''.join(o.get('text',[])) for o in nb['cells'][14].get('outputs',[]))
    reference={k:float(v) for k,v in re.findall(r'^\s*(alpha_[1-4]|beta_[1-4]|lapse|gamma)\s+([-\d.]+)',output,re.M)}
    assert len(reference)==10
    parameter_rows=[];displays=[];checks=[]
    for name,data,stages in [('original_notebook',valid,[1,2,3]),('same_model_current_early_middle',eligible[eligible.onset_stratum.isin(['early','middle'])],[1,2]),('same_model_current_all_times',eligible,[1,2,3])]:
        result=notebook_fit(data,nb);q=result['params'];cov=result['covariance'];np.save(a.output/f'{name}_covariance.npy',cov)
        if name=='original_notebook':
            error=max(abs(q[i]-reference[k]) for i,k in enumerate(PARAMS));assert error<5.01e-7
        else:error=None
        X,y,sigma=result['x'],result['y'],result['sigma'];pred=result['fit_function'](X,*q)
        cells=pd.DataFrame({'coherence_pct':X[0],'direction':X[1],'stage':X[2],'p_right':y,'n_trials':np.rint(1/sigma**2).astype(int),'predicted':pred});cells.to_csv(a.output/f'{name}_cells.csv',index=False)
        assert cells.n_trials.sum()==len(data)
        for i,k in enumerate(PARAMS):parameter_rows.append({'dataset':name,'parameter':k,'estimate':q[i],'se':np.sqrt(cov[i,i]),'notebook_saved_rounded':reference[k] if name=='original_notebook' else np.nan})
        for d in [-1,1]:
            for t in stages:
                ca=np.zeros(10);ca[1:4]=[d,t,d*t];cb=np.zeros(10);cb[5:8]=[d,t,d*t];full=ca.copy();full[0]=1
                # Original display omits baseline; full additive offset includes alpha1.
                displays.append({'dataset':name,'direction':d,'stage':t,'alpha_original_display':ca@q,'alpha_full_offset':full@q,'alpha_native_midpoint':-full@q,'alpha_contrast_se':np.sqrt(ca@cov@ca),'alpha_full_se':np.sqrt(full@cov@full),'alpha_old_error_bar':np.sqrt(cov[1,1])+t*np.sqrt(cov[3,3]),'beta_change':cb@q,'beta_change_se':np.sqrt(cb@cov@cb),'beta_full':q[4]+cb@q})
        checks.append({'dataset':name,'n_trials':len(data),'weighted_sse':float(np.sum(((pred-y)/sigma)**2)),'max_parameter_error_vs_saved_rounding':error,'warnings':result['warnings']})
        print(name,dict(zip(PARAMS,q)),flush=True)
    params=pd.DataFrame(parameter_rows);display=pd.DataFrame(displays);params.to_csv(a.output/'parameters.csv',index=False);display.to_csv(a.output/'display_values.csv',index=False)
    for mode in ['original_display','full_offset']:
        z=display[display.dataset=='original_notebook'];col='alpha_original_display' if mode=='original_display' else 'alpha_full_offset';se='alpha_contrast_se' if mode=='original_display' else 'alpha_full_se'
        with plt.rc_context(RC):
            fig,axes=plt.subplots(1,2,figsize=(7.5,3.2),layout='constrained')
            for d,color,text in [(-1,LEFT_COLOR,'Leftward pulse'),(1,RIGHT_COLOR,'Rightward pulse')]:
                r=z[z.direction==d].sort_values('stage')
                axes[0].errorbar(r.stage,r[col],yerr=r[se],fmt='o-',c=color,capsize=3,label=text)
                axes[1].errorbar(r.stage,r.beta_change,yerr=r.beta_change_se,fmt='o-',c=color,capsize=3,label=text)
            for ax in axes:ax.axhline(0,c='.7',ls=':',lw=.7);ax.set(xticks=[1,2,3],xticklabels=['Early','Middle','Late'],xlabel='Pulse stage (ordinal model input)')
            axes[0].set(ylabel='α: additive coherence offset (% coherence)',title='Pulse-time effect on α');axes[1].set(ylabel='Slope change from control (per % coherence)',title='Pulse-time effect on β');axes[0].legend()
            subtitle='Original plotted α terms; baseline omitted' if mode=='original_display' else 'Full α includes the baseline offset'
            fig.suptitle('Exact notebook population model on the original data\n'+subtitle+'; error bars use full covariance (±1 SE)',fontsize=8)
            for ext in ['png','pdf','svg']:fig.savefig(a.output/f'notebook_{mode}.{ext}',dpi=250)
            plt.close(fig)
    manifest={'fits':checks,'notebook_cells':[5,13,14,15,16],'scope':'Direct notebook functions executed without changing fitting equation, initial guess, bounds or weighting. Later trial masks compared under same model.','alpha_mapping':'notebook full additive offset A=alpha1+alpha2*d+alpha3*t+alpha4*d*t; native midpoint mu=-A. Original plot shows A-alpha1, not mu.','error_bars':'Correct full contrast covariance c.T@Cov@c, conditional model SE; not across-mouse uncertainty. Original notebook SE2+t*SE4 preserved in table for audit only.','timing':'Ordinal stages1/2/3; linear stage trend imposed; physical schedules differ by site and late only UW','source_hashes':{str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in [NOTEBOOK,VALID,a.eligible,Path(__file__)]}}
    (a.output/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n');print(display[display.dataset=='original_notebook'].to_string(index=False),flush=True)

if __name__=='__main__':main()
