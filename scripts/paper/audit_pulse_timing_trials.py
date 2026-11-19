"""Exact trial accounting: notebook rows versus post-pulse timing eligibility."""
import argparse
import hashlib
import json
from pathlib import Path
import numpy as np
import pandas as pd
from scripts.paper.reproduce_pulse_time_notebook import VALID

TABLE=Path('/mnt/data/processed/pulse_followup/20261023T191030Z_fa8de8b/data/trial_table.csv')


def main():
    p=argparse.ArgumentParser(__doc__);p.add_argument('--eligible',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();a.output.mkdir(parents=True,exist_ok=False)
    v=pd.read_csv(VALID);raw=pd.read_csv(TABLE,low_memory=False).set_index('trial_id');e=pd.read_csv(a.eligible)
    x=raw.loc[v.agg_code].reset_index();x['original_label']=v.pulse_type.to_numpy();x['reason']='retained';keep=np.ones(len(x),dtype=bool);steps=[]
    def apply(name,ok):
        nonlocal keep
        ok=np.asarray(ok,dtype=bool);removed=keep&~ok;x.loc[removed,'reason']=name;keep=keep&ok
        steps.append({'rule':name,'removed_this_step':int(removed.sum()),'remaining':int(keep.sum()),'independent_failures_among_all_original_rows':int((~ok).sum())})
    apply('not_in_model_input',x.in_ddm_input.astype(bool))
    apply('no_recorded_response',x.response_side.ne('none'))
    apply('one_pulse_direction_scheduled',x.signs_scheduled_symmetric.astype(bool))
    apply('no_change_pulse_category',x.pulse_category.isin(['control','positive','negative']))
    prewindow=x[keep].copy();pulse=prewindow.pulse_category.ne('control');dur=prewindow.recorded_duration_s.where(pulse)
    onset=prewindow.recorded_onset_s.where(pulse,prewindow.control_onset_s)
    offset=onset+dur.where(pulse,prewindow.rig.map(dur.groupby(prewindow.rig).median()))
    x['analysis_onset_s']=np.nan;x['analysis_offset_s']=np.nan;x.loc[prewindow.index,'analysis_onset_s']=onset;x.loc[prewindow.index,'analysis_offset_s']=offset
    # Each sequential rule uses a full-length positional mask; previous exclusions
    # pass later rules so counts are mutually exclusive and free of index alignment.
    end_ok=np.ones(len(x),dtype=bool);end_ok[prewindow.index]=prewindow.rt_s.to_numpy()>=offset.to_numpy()
    apply('response_before_actual_or_virtual_pulse_end',end_ok)
    onset_ok=np.ones(len(x),dtype=bool);onset_ok[prewindow.index]=prewindow.rt_s.to_numpy()-onset.to_numpy()>=.1
    apply('response_less_than_100ms_after_onset',onset_ok)
    assert set(x.loc[keep,'trial_id'])==set(e.trial_id)
    assert len(v)==25508 and keep.sum()==21725
    assert (x.loc[keep,'original_label']==x.loc[keep,'ddm_sched_pulse_type']).all()
    selected_cols=['trial_id','mouse','rig','original_label','ddm_sched_pulse_type','pulse_category','coherence_pct','pulse_coherence_pct','pulse_equals_baseline','onset_stratum','rt_s','analysis_onset_s','analysis_offset_s','in_ddm_input','signs_scheduled_symmetric','reason']
    x[selected_cols].to_csv(a.output/'trial_accounting.csv',index=False);pd.DataFrame(steps).to_csv(a.output/'flow.csv',index=False)
    pd.crosstab(x.original_label,x.ddm_sched_pulse_type,dropna=False).to_csv(a.output/'label_crosstab.csv')
    x.groupby(['reason','pulse_category']).size().rename('n').reset_index().to_csv(a.output/'reason_by_category.csv',index=False)
    x.groupby(['mouse','reason']).size().unstack(fill_value=0).to_csv(a.output/'mouse_exclusions.csv')
    # Check whether audit-table model membership differs from current model inputs.
    inputs=np.load('/mnt/data/processed/ddm/ddm_inputs_global.npz',allow_pickle=True)
    ids=set(inputs['agg_code'].astype(str));missing=x[x.reason=='not_in_model_input'].copy();missing['in_current_npz']=missing.trial_id.isin(ids);missing[selected_cols+['in_current_npz']].to_csv(a.output/'model_input_exclusions.csv',index=False)
    changed=x.ddm_sched_pulse_type.notna()&x.original_label.ne(x.ddm_sched_pulse_type)
    manifest={'original':len(v),'retained':int(keep.sum()),'excluded':int((~keep).sum()),'retained_label_changes':0,'original_response_control_reassigned_as_scheduled_pulse':int((changed&x.original_label.eq(0)).sum()),'all_such_early_label_changes_excluded':bool((~keep[changed]).all()),'null_pulses_in_original':int(x.pulse_category.eq('null_pulse').sum()),'current_npz_members_among_model_table_exclusions':int(missing.in_current_npz.sum()),'steps':steps,'scope':'Counts of exclusions in explicit rule order; some rules overlap before ordering. Sensitivity bundled label/selection choices from post-pulse workflow; no fitting.','source_hashes':{str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in [VALID,TABLE,a.eligible,Path(__file__)]}}
    (a.output/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n');print(json.dumps(manifest,indent=2))

if __name__=='__main__':main()
