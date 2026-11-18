"""High-repetition check of already selected, fixed pilot solutions."""
import argparse
import gc
import hashlib
import json
import logging
from pathlib import Path
import numpy as np
import pandas as pd
import torch
from scripts.paper.control_c_optimization_pilot import DDM,PILOT,load_inputs,responded_only,select,load_fit,make,prepare,stats,write


def main():
    p=argparse.ArgumentParser(__doc__);p.add_argument('--pilot',type=Path,required=True);a=p.parse_args()
    out=a.pilot/'confirmation_100reps';out.mkdir(exist_ok=False)
    for name in ['src.ddm.ddm','src.ddm.simulator']:logging.getLogger(name).setLevel(logging.WARNING)
    inputs=responded_only(load_inputs(DDM/'ddm_inputs_global.npz'));records=[]
    seeds=[123456,234567,345678]
    for mouse in PILOT:
        selection=json.loads((a.pilot/'validation_v2'/(mouse+'.json')).read_text())['decision']
        path,fit=load_fit(mouse,'control');assert selection['archived_parameters']==fit['parameters']
        rows=np.flatnonzero((inputs['subject_id']==mouse)&(inputs['sched_pulse_type']==0))
        data,stim=select(inputs,rows);data['coh']=inputs['signed_coherence'][rows]
        model=make(fit,np.unique(inputs['data_source'][rows]).item());mouse_records=[]
        for seed in seeds:
            prepare(model,data,stim,100,seed)
            for name,params in [('archived_fit',fit['parameters']),('selected_refit',selection['selected_parameters'])]:
                result={'mouse':mouse,'name':name,'seed':seed,'n_reps':100,**stats(model,params,data,stim,100)}
                mouse_records.append(result);records.append(result)
            last=mouse_records[-2:]
            print(mouse,seed,'new-minus-old joint NLL',last[1]['joint_nll']-last[0]['joint_nll'],flush=True)
        write(out/(mouse+'.json'),{'selected_name':selection['selected_name'],'records':mouse_records,'parameters_fixed_before_seeds':True})
        model.simulator.clear_cache();del model,stim;gc.collect();torch.cuda.empty_cache()
    frame=pd.DataFrame(records);frame.to_csv(out/'scores.csv',index=False)
    metrics=['joint_nll','choice_nll','rt_nll','psy_rmse','central_deficit','mean_rt_rmse_s','quantile_mae_s']
    changes=[]
    for (mouse,seed),g in frame.groupby(['mouse','seed']):
        z=g.set_index('name');changes.append({'mouse':mouse,'seed':seed,**{k:float(z.loc['selected_refit',k]-z.loc['archived_fit',k]) for k in metrics}})
    pd.DataFrame(changes).to_csv(out/'new_minus_original.csv',index=False)
    write(out/'manifest.json',{'selection_source':'validation_v2, fixed before these seeds','seeds':seeds,'n_reps':100,
          'no_selection_or_optimization_on_these_draws':True,'script_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest()})


if __name__=='__main__':main()
