"""Audit saved results for the three-part paper story without new model fits.

Run from /src:
  .venv/bin/python dissemination/reviewer_2026-11-13/audit_completed_results.py
Writes only beside this script. Sources and their hashes accompany the results.
"""
from pathlib import Path
import hashlib
import itertools
import json
import pickle
import subprocess

import numpy as np
import pandas as pd
from scipy import stats

ROOT = Path(__file__).resolve().parents[2]
OUT = Path(__file__).resolve().parent
DDM = Path('/mnt/data/processed/ddm')
QC = ROOT / 'dissemination/figures/qc'
CONTROL = ROOT / 'dissemination/paper_control/tables'
BEHAVIOR = ROOT / 'dissemination/paper_accumulation/tables'
NAMES = {'L0U0V1Z0G1': 'C', 'L1U0V1Z0G1': 'E', 'ES': 'ES', 'DDMx': 'DDMx', 'ESx': 'ESx'}
ALTS = ['E', 'ES', 'DDMx', 'ESx']


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def holm(p):
    order = np.argsort(p, axis=-1)
    sorted_p = np.take_along_axis(p, order, axis=-1)
    corrected = np.minimum(1, np.maximum.accumulate(sorted_p * np.arange(p.shape[-1], 0, -1), axis=-1))
    return np.take_along_axis(corrected, np.argsort(order, axis=-1), axis=-1)


def recovery():
    datasets = DDM / 'recovery_datasets_cpu_2026-10-29'
    manifest = json.loads((datasets / 'manifest.json').read_text())
    for filename, record in manifest.items():
        assert record['device'] == 'cpu'
        assert sha(datasets / filename) == record['sha256']
    rows = []
    for file in sorted((DDM / 'recovery_full_cpu_resp').glob('*.pkl')):
        with file.open('rb') as f:
            r = pickle.load(f)
        key = f"{r['mouse']}_gen-{r['generator']}_rep{r['replicate']}.npz"
        m = manifest[key]
        assert r['datasets_dir'] == str(datasets)
        assert r['n_train'] == m['n_train_responded'] and r['n_test'] == m['n_test_responded']
        assert np.isfinite(r['test_nll'])
        rows.append({'file': file.name, 'mouse': r['mouse'], 'generator': NAMES[r['generator']],
                     'candidate': NAMES[r['candidate']], 'replicate': r['replicate'],
                     'n_train': r['n_train'], 'n_test': r['n_test'], 'test_nll': r['test_nll']})
    df = pd.DataFrame(rows)
    assert len(df) == 500 and len(manifest) == 100
    assert df.groupby(['generator', 'candidate']).size().eq(20).all()
    assert df.groupby(['generator', 'mouse', 'replicate'])[['n_train', 'n_test']].nunique().eq(1).all().all()
    scores = df.pivot(index=['generator', 'mouse', 'replicate'], columns='candidate', values='test_nll')
    n = df.groupby(['generator', 'mouse', 'replicate']).n_test.first()
    differences = scores[ALTS].sub(scores.C, axis=0).div(n, axis=0) * 1000
    rates = []
    for generator in sorted(df.generator.unique()):
        g = differences.loc[generator]
        mice = sorted(g.index.get_level_values('mouse').unique())
        vals = np.array([[g.loc[(m, r), ALTS].to_numpy() for r in [0, 1]] for m in mice])
        bits = np.array(list(itertools.product([0, 1], repeat=len(mice))))
        cohorts = vals[np.arange(len(mice))[None, :], bits]
        p = stats.ttest_1samp(cohorts, 0, axis=1).pvalue
        qualifies = (cohorts.mean(axis=1) > 0) & (holm(p) < .05)
        rates.append({'generator': generator, **{f'rep_{a}': qualifies[:, j].mean() for j, a in enumerate(ALTS)}})
    rates = pd.DataFrame(rates).set_index('generator')
    saved = pd.read_csv(CONTROL / 'recovery_cohort_rates_2026-10-30_v3.csv').set_index('generator')
    assert np.allclose(rates, saved.loc[rates.index, rates.columns])
    best = df.loc[df.groupby(['generator', 'mouse', 'replicate']).test_nll.idxmin()]
    confusion = pd.crosstab(best.generator, best.candidate)
    saved_conf = pd.read_csv(CONTROL / 'recovery_confusion_2026-10-30_v3.csv').set_index('generator')
    assert confusion.equals(saved_conf.loc[confusion.index, confusion.columns])
    df.to_csv(OUT / 'recovery_fit_inventory.csv', index=False)
    rates.to_csv(OUT / 'recovery_cohort_rates_reproduced.csv')
    confusion.to_csv(OUT / 'recovery_confusion_reproduced.csv')
    return {'fits': len(df), 'datasets': len(manifest), 'datasets_per_generator': 20,
            'replicates_per_mouse': 2, 'all_dataset_hashes_match': True,
            'all_fits_paired_by_dataset_and_counts': True, 'v3_rates_and_confusion_reproduced': True,
            'cohort_rates': rates.reset_index().to_dict('records')}


def control():
    mice = sorted(pd.read_csv(CONTROL / 'heldout_nll_per_mouse_2026-10-29.csv').mouse.unique())
    families = {
        'C': ('fits_resp_fast_only', 'L0U0V1Z0G1'),
        'E': ('fits_resp_fast_only_leak20-200_cap', 'L1U0V1Z0G1'),
        'ES': ('fits_resp_fast_only_es_cap', 'L0U0V1Z0G1'),
        'DDMx': ('fits_resp_nominal_ddm_g001', 'L0U0V0Z0G0'),
        'ESx': ('fits_resp_nominal_es', 'L0U0V0Z0G0'),
        'C_nom': ('fits_resp_nominal_matched_C', 'L0U0V1Z0G1'),
        'E_nom': ('fits_resp_nominal_matched_E', 'L1U0V1Z0G1'),
        'ES_nom': ('fits_resp_nominal_matched_ES', 'L0U0V1Z0G1'),
    }
    rows = []
    for name, (folder, variant) in families.items():
        for mouse in mice:
            for fold in range(5):
                path = DDM / folder / f'{mouse}_{variant}_ccv{fold}.pkl'
                with path.open('rb') as f:
                    r = pickle.load(f)
                rows.append({'model': name, 'mouse': mouse, 'fold': fold, 'n_test': r['n_test'],
                             'test_nll': r['test_nll'], 'path': str(path)})
    folds = pd.DataFrame(rows)
    assert folds.groupby(['mouse', 'fold']).n_test.nunique().eq(1).all()
    totals = folds.groupby(['model', 'mouse'])[['test_nll', 'n_test']].sum()
    ref = totals.loc['C']
    differences = []
    for model in ALTS:
        d = (totals.loc[model].test_nll - ref.test_nll) / ref.n_test * 1000
        differences.extend({'model': model, 'mouse': m, 'per_1000': v} for m, v in d.items())
    differences = pd.DataFrame(differences)
    saved = pd.read_csv(CONTROL / 'heldout_diff_per_mouse_2026-10-29.csv')
    joined = differences.merge(saved[saved.part == 'total'], on=['model', 'mouse'], suffixes=('_fresh', '_saved'), validate='one_to_one')
    assert np.allclose(joined.per_1000_fresh, joined.per_1000_saved)
    folds.to_csv(OUT / 'control_fold_inventory.csv', index=False)
    differences.to_csv(OUT / 'control_differences_reproduced.csv', index=False)
    return {'fold_fit_files_read': len(folds), 'control_trials': int(ref.n_test.sum()),
            'same_test_counts_across_models_and_folds': True, 'saved_comparisons_reproduced': True,
            'mean_nll_advantage_per_1000': differences.groupby('model').per_1000.mean().to_dict()}


def sources():
    inventory = []
    for folder in [CONTROL, BEHAVIOR, QC]:
        for file in sorted(folder.glob('*.csv')):
            try:
                d = pd.read_csv(file)
                inventory.append({'path': str(file.relative_to(ROOT)), 'rows': len(d),
                                  'columns': '|'.join(d.columns), 'sha256': sha(file)})
            except (pd.errors.EmptyDataError, UnicodeError):
                inventory.append({'path': str(file.relative_to(ROOT)), 'rows': None, 'columns': '', 'sha256': sha(file)})
    pd.DataFrame(inventory).to_csv(OUT / 'results_table_inventory.csv', index=False)
    reports = []
    for file in sorted((ROOT / '.agents/reports').glob('*.md')):
        s = file.read_text()
        start = s.find('## Summary')
        if start < 0:
            continue
        end = s.find('\n## ', start + 5)
        reports.append({'path': str(file.relative_to(ROOT)), 'sha256': sha(file),
                        'summary': s[start:end if end >= 0 else len(s)]})
    (OUT / 'report_summary_inventory.json').write_text(json.dumps(reports, indent=2) + '\n')
    return {'csv_tables_cataloged': len(inventory), 'reports_with_summary_cataloged': len(reports)}


def main():
    result = {'commit': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
              'scope': 'Audits existing fits and tables; no model fitting or fresh simulation',
              'recovery': recovery(), 'control': control(), 'inventory': sources()}
    dilution = pd.read_csv(BEHAVIOR / 'pulse_dilution_2026-10-30.csv')
    late = dilution[dilution.lo_s >= 1.2].copy()
    late['p_holm_below_plateau'] = holm(late.p_below_K.to_numpy())
    late.to_csv(OUT / 'dilution_late_contrasts_with_holm.csv', index=False)
    result['dilution'] = {'plateau_K': dilution.K.iloc[0], 'K_lo': dilution.K_lo.iloc[0],
                          'K_hi': dilution.K_hi.iloc[0], 'late_holm': late[['lo_s', 'hi_s', 'p_holm_below_plateau']].to_dict('records')}
    ic = pd.read_csv(QC / 'model_ic_summary_2026-11-12_rescored.csv')
    result['rescored_family_counts'] = ic.groupby('kind').size().to_dict()
    result['joint_best_bic'] = ic[ic.kind == 'joint'].nsmallest(3, 'bic')[['family', 'd_bic', 'd_heldout', 'seed_sd']].to_dict('records')
    result['pulse_only_best_bic'] = ic[ic.kind == 'pulse_only'].nsmallest(3, 'bic')[['family', 'd_bic', 'd_heldout', 'seed_sd']].to_dict('records')
    (OUT / 'completed_results_audit.json').write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
