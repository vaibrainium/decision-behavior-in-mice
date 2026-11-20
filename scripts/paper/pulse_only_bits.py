"""Held-out joint bits/trial for pulse-only models, matching Figure3's equal-mouse metric."""
import argparse,hashlib,json,subprocess
from pathlib import Path
import numpy as np
import pandas as pd
SOURCE=Path('dissemination/figures/qc/model_ic_per_mouse_2026-11-12_rescored.csv')

def main():
    p=argparse.ArgumentParser(__doc__);p.add_argument('--output',type=Path,required=True);a=p.parse_args();a.output.mkdir(parents=True,exist_ok=False)
    d=pd.read_csv(SOURCE);z=d[d.kind=='pulse_only'].copy()
    assert z.family.nunique()==22 and z.mouse.nunique()==10 and len(z)==220
    assert not z.duplicated(['family','mouse']).any()
    assert np.isfinite(z[['heldout_nll','n_heldout']]).all().all() and (z.n_heldout>0).all()
    counts=z.pivot(index='mouse',columns='family',values='n_heldout');assert counts.notna().all().all() and counts.nunique(axis=1).eq(1).all()
    z['heldout_ll']=-z.heldout_nll;z['joint_test_bits_per_trial']=z.heldout_ll/(z.n_heldout*np.log(2))
    rows=[]
    for family,g in z.groupby('family'):
        rows.append({'family':family,'n_mice':g.mouse.nunique(),'n_test_total':int(g.n_heldout.sum()),'mean_joint_test_bits_per_trial':g.joint_test_bits_per_trial.mean(),'total_heldout_nll':g.heldout_nll.sum(),'pooled_trial_weighted_bits_per_trial':-g.heldout_nll.sum()/(g.n_heldout.sum()*np.log(2))})
    group=pd.DataFrame(rows).sort_values('mean_joint_test_bits_per_trial',ascending=False).reset_index(drop=True)
    group['rank']=np.arange(1,len(group)+1);group['difference_from_best_bits_per_trial']=group.mean_joint_test_bits_per_trial-group.mean_joint_test_bits_per_trial.max()
    np.testing.assert_allclose(z.joint_test_bits_per_trial*np.log(2)*z.n_heldout,-z.heldout_nll,atol=1e-10)
    assert group.n_test_total.nunique()==1
    z.to_csv(a.output/'bits_per_mouse.csv',index=False);group.to_csv(a.output/'bits_summary.csv',index=False)
    metadata={'source':str(SOURCE),'source_sha256':hashlib.sha256(SOURCE.read_bytes()).hexdigest(),'code_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'base_commit':subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),'definition':'within-mouse -heldout_nll/(n_heldout ln2), then equal-mouse mean; higher is better','winner_equal_mouse':group.family.iloc[0],'winner_pooled':group.loc[group.pooled_trial_weighted_bits_per_trial.idxmax(),'family'],'matched_denominators_verified':True,'formula_inversion_verified':True,'new_fits':False,'uncertainty':'Descriptive ranking only; no new significance tests; no null baseline subtraction.'}
    (a.output/'manifest.json').write_text(json.dumps(metadata,indent=2)+'\n')
    print(group[['rank','family','mean_joint_test_bits_per_trial','total_heldout_nll','pooled_trial_weighted_bits_per_trial']].to_string(index=False))

if __name__=='__main__':main()
