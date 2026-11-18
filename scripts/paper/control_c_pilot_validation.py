"""Independent checks with explicit immutable archived-fit baseline."""
import argparse
import gc
import hashlib
import json
import logging
from pathlib import Path
import numpy as np
import pandas as pd
import torch
from scripts.paper.control_c_optimization_pilot import (DDM,PILOT,SELECT_SEEDS,CONFIRM_SEED,load_inputs,
    responded_only,select,make,prepare,stats,load_fit,write)


def main():
    p=argparse.ArgumentParser(__doc__);p.add_argument('--pilot',type=Path,required=True);a=p.parse_args()
    out=a.pilot/'validation_v2';out.mkdir(exist_ok=False)
    for name in ['src.ddm.simulator','src.ddm.ddm']:logging.getLogger(name).setLevel(logging.WARNING)
    inputs=responded_only(load_inputs(DDM/'ddm_inputs_global.npz'))
    allrows=[];conf=[];decisions=[]
    for mouse in PILOT:
        path,fit=load_fit(mouse,'control');base=fit['parameters']
        candidates=[json.loads(p.read_text()) for p in (a.pilot/mouse/'control').glob('*_restart.json')]
        assert len(candidates)==3
        sets={'archived_fit':dict(base)}
        sets.update({'refit_'+c['name']:c['parameters'] for c in candidates})
        assert len(sets)==4 and sets['archived_fit']==fit['parameters']
        rows=np.flatnonzero((inputs['subject_id']==mouse)&(inputs['sched_pulse_type']==0));data,stim=select(inputs,rows)
        data['coh']=inputs['signed_coherence'][rows];model=make(fit,np.unique(inputs['data_source'][rows]).item())
        results=[]
        for seed in SELECT_SEEDS:
            prepare(model,data,stim,30,seed)
            for name,params in sets.items():
                results.append({'mouse':mouse,'name':name,'seed':seed,'n_reps':30,**stats(model,params,data,stim,30)})
        f=pd.DataFrame(results);means=f.groupby('name').joint_nll.mean();invalid=f.groupby('name').training_guard_violated.any()
        winner=means[~invalid].idxmin()
        baseline=means['archived_fit'];delta=float(means[winner]-baseline)
        confirmation=[];prepare(model,data,stim,60,CONFIRM_SEED)
        for name in dict.fromkeys(['archived_fit',winner]):
            confirmation.append({'mouse':mouse,'name':name,'seed':CONFIRM_SEED,'n_reps':60,**stats(model,sets[name],data,stim,60)})
        cf=pd.DataFrame(confirmation).set_index('name');old=cf.loc['archived_fit'];new=cf.loc[winner]
        decision={'mouse':mouse,'selected_name':winner,'selection_mean_nll_change':delta,
            'confirmation_nll_change':float(new.joint_nll-old.joint_nll),
            'confirmation_psy_rmse_change':float(new.psy_rmse-old.psy_rmse),
            'confirmation_central_deficit_change':float(new.central_deficit-old.central_deficit),
            'both_selection_seeds_improve':bool(all(f[(f.name==winner)&(f.seed==seed)].joint_nll.item()<f[(f.name=='archived_fit')&(f.seed==seed)].joint_nll.item() for seed in SELECT_SEEDS)),
            'confirmation_improves':bool(new.joint_nll<old.joint_nll),
            'selected_parameters':sets[winner],
            'archived_parameters':base,'archived_fit_path':str(path),'archived_fit_sha256':hashlib.sha256(path.read_bytes()).hexdigest()}
        write(out/(mouse+'.json'),{'selection_records':results,'confirmation_records':confirmation,'decision':decision})
        allrows+=results;conf+=confirmation;decisions.append({k:v for k,v in decision.items() if not isinstance(v,dict)})
        print(mouse,winner,'selection delta',delta,'confirmation delta',decision['confirmation_nll_change'],'psych RMSE delta',decision['confirmation_psy_rmse_change'],flush=True)
        model.simulator.clear_cache();del model,stim;gc.collect();torch.cuda.empty_cache()
    pd.DataFrame(allrows).to_csv(out/'selection_scores.csv',index=False);pd.DataFrame(conf).to_csv(out/'confirmation_scores.csv',index=False)
    pd.DataFrame(decisions).to_csv(out/'pilot_decisions.csv',index=False)
    write(out/'manifest.json',{'scope':'Corrected independent original-fit versus refit comparison',
          'immutable_archived_fit_baselines_checked':True,'selection_seeds':SELECT_SEEDS,'selection_reps':30,
          'confirmation_seed':CONFIRM_SEED,'confirmation_reps':60,'validation_script_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
          'objective_module_sha256':hashlib.sha256(Path('scripts/paper/control_c_optimization_pilot.py').read_bytes()).hexdigest(),
          'supersedes':'Original per-mouse independent_evaluation.json baseline-label collision; optimizer results/sensitivity maps unaffected'})


if __name__=='__main__':main()
