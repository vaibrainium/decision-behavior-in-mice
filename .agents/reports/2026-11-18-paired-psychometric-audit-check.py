"""Independent verification of corrected paired psychometric fits and statistics."""
from pathlib import Path
import json
import numpy as np
import pandas as pd
from scipy.special import expit

root=Path('/src');b=root/'dissemination/paper_accumulation/draft_2026-11-15'
audit=b/'pulse_psychometric_pair_audit_2026-11-18_v2';out=b/'figure4_revision_2026-11-18_v5';old=b/'figure4_revision_2026-11-18_v4'
p=pd.read_csv(out/'source_data/fig4_B_paired_parameters.csv');best=pd.read_csv(audit/'fit_audit.csv')
z=p.merge(best,on=['mouse','pulse']);np.testing.assert_allclose(z.alpha,z.best_alpha,atol=1e-7);np.testing.assert_allclose(z.beta,z.best_beta,atol=1e-7)
assert len(p)==20 and p.mouse.nunique()==10 and (z.weighted_sse<=z.original_sse+1e-8).all()
curves=pd.read_csv(out/'source_data/fig4_B_paired_individual_curves.csv');data=pd.read_csv(out/'source_data/fig4_A_psychometric_mouse.csv')
for row in p.itertuples():
    c=curves[(curves.mouse==row.mouse)&(curves.pulse==row.pulse)]
    pred=lambda x:row.lower_asymptote+(row.upper_asymptote-row.lower_asymptote)*expit(row.beta*(x-row.alpha))
    np.testing.assert_allclose(c.p_right,pred(c.coherence_pct),atol=1e-12)
    d=data[(data.mouse==row.mouse)&(data.pulse==row.pulse)]
    np.testing.assert_allclose(row.weighted_sse,np.sum(d['size']*(pred(d.coherence_pct)-d['mean'])**2),atol=1e-9)
for path in (old/'source_data').glob('fig4_A_*.csv'):pd.testing.assert_frame_equal(pd.read_csv(path),pd.read_csv(out/'source_data'/path.name))
for name in ['fig4_C_directional_shared.csv','fig4_D_dilution_adjustment.csv','fig4_E_assignment_effects.csv']:pd.testing.assert_frame_equal(pd.read_csv(old/'source_data'/name),pd.read_csv(out/'source_data'/name))
t=pd.read_csv(out/'source_data/fig4_B_paired_tests.csv');signs=2*((np.arange(1024)[:,None]>>np.arange(10))&1)-1
pv=[]
for key in ['alpha','beta']:
    w=p.pivot(index='mouse',columns='pulse',values=key).sort_index();d=(w[1]-w[-1]).to_numpy()
    raw=float(np.mean(np.abs((signs*d).mean(axis=1))>=abs(d.mean())-1e-12));pv.append(raw)
    np.testing.assert_allclose(raw,t.loc[t.parameter==key,'p_exact_signflip'].item())
np.testing.assert_allclose(t.p_holm,[min(1,2*pv[0]),max(min(1,2*pv[0]),pv[1])])
allstarts=pd.read_csv(audit/'all_starts.csv');pools={}
for (mouse,side),g in allstarts.groupby(['mouse','pulse']):pools[(mouse,side)]=g[g.weighted_sse<=g.weighted_sse.min()+1e-5].alpha.to_numpy()
rng=np.random.default_rng(20261118);values=[];mice=sorted(p.mouse.unique())
for _ in range(500):
    d=np.array([rng.choice(pools[(m,1)])-rng.choice(pools[(m,-1)]) for m in mice])
    values.append(float(np.mean(np.abs((signs*d).mean(axis=1))>=abs(d.mean())-1e-12)))
assert min(values)==max(values)==pv[0]
group=pd.read_csv(audit/'group_A_fit_audit.csv');assert (group.difference.abs()<1e-10).all()
checks={'all20_fits_match_independent_multistart_audit':True,'fits_selected_by_WLS_objective_only':True,
        'no_subjects_excluded':True,'equation_and_weighted_sse_verified':True,'all1024_paired_sign_patterns_verified':True,
        'holm_family_unchanged_two_parameters':True,'A_curves_and_points_unchanged':True,'old_temporal_assignment_values_unchanged':True,
        'near_minimum_numerical_checks':500,'near_minimum_alpha_raw_p_range':[min(values),max(values)],
        'numerical_checks_are_not_additional_animal_or_trial_resamples':True}
(out/'verification.json').write_text(json.dumps(checks,indent=2)+'\n')
print(json.dumps(checks,indent=2))
