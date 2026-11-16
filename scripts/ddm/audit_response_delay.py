"""Integrity and provenance audit for the completed exploratory delay pilot."""
import json
import platform
import subprocess
from pathlib import Path

import numpy as np
import pandas as pd

from scripts.ddm.fit_response_delay import (OUT, ROOT, SOURCES, source_path, sha,
    inputs, partition, write_json)


def main():
    x = inputs()
    fits = []
    checked = 0
    outcomes = 0
    max_reconstruction_error = 0.
    for mouse in ['PSUIM6', 'PSUIM7']:
        for split in ['all'] + [f'cv{k}' for k in range(5)]:
            train, test = partition(x, mouse, split)
            for family in ['fixed', 'drift', 'delay']:
                path = source_path(mouse, family, split)
                r = pd.read_pickle(path)
                assert len(train) == r['n_train']
                if test is not None:
                    assert len(test) == r['n_test'] and not np.intersect1d(train, test).size
                p = r['parameters']
                sigma = float(p.get('ndt_sigma', 0.))
                fits.append({'mouse': mouse, 'split': split, 'family': family,
                    'n_train': len(train), 'k': len(r['free_parameters']), 'fit_path': str(path),
                    'sha256': sha(path), 'stored_train_nll': r['train_nll'],
                    **{k: float(v) for k, v in p.items()},
                    'mean_response_delay_s': p['ndt'],
                    'response_delay_sd_s': p['ndt'] * np.sqrt(np.expm1(sigma**2)),
                    'bounded_pilot': family == 'delay'})
                if family == 'delay':
                    assert p['sv'] == 0 and 0 <= sigma <= 1.5
                    for rel, digest in r['signature']['source_sha256'].items():
                        assert sha(ROOT / rel) == digest, f'Source changed after fit: {rel}'
                    fixed = pd.read_pickle(source_path(mouse, 'fixed', split))
                    assert r['train_nll'] <= fixed['train_nll'] + 1e-7, 'Nested solution missing from search'
                if test is None:
                    continue
                for seed in [12345, 23456, 34567]:
                    record = pd.read_pickle(OUT / 'cache' / f'score_{family}_{mouse}_{split}_r60_s{seed}.pkl')
                    assert record['fingerprint']['fit_sha256'] == sha(path)
                    o = record['outcomes']
                    assert len(o) == len(test) * 60
                    assert np.array_equal(o.row.to_numpy(), np.tile(test, 60))
                    assert np.array_equal(o.signed_coherence.to_numpy(), x['condition'][o.row.to_numpy()])
                    responded = o.choice >= 0
                    assert o.loc[responded, 'rt'].between(.3, 5.).all()
                    assert np.isinf(o.loc[~responded, 'rt']).all()
                    for rel, digest in record['fingerprint']['source_sha256'].items():
                        assert sha(ROOT / rel) == digest
                    error = abs(record['nll'] - record['choice_nll'] - record['rt_nll'])
                    max_reconstruction_error = max(max_reconstruction_error, error)
                    assert error < 1e-7
                    outcomes += len(o)
                    checked += 1
    fits = pd.DataFrame(fits)
    ks = fits.pivot(index=['mouse', 'split'], columns='family', values='k')
    assert (ks.drift == ks.delay).all() and (ks.fixed + 1 == ks.delay).all()
    fits.to_csv(OUT / 'fit_parameters_and_provenance.csv', index=False)
    zero = json.loads((OUT / 'real_data_zero_spread_checks.json').read_text())
    assert all(v['difference'] == 0. for v in zero.values())
    estimator = json.loads((OUT / 'pulse_estimator_checks.json').read_text())
    assert estimator['profile_max_error_pp'] < 1e-8 and estimator['window_max_error_pp'] < 1e-8
    assert checked == 90
    extra = [ROOT / 'scripts/ddm/assess_response_delay.py', ROOT / 'scripts/ddm/check_response_delay_search.py',
             ROOT / 'tests/test_response_delay.py', Path(__file__)]
    artifacts = {p.name: sha(p) for p in OUT.glob('*.csv')}
    for p in [OUT / 'response_delay_pilot.pdf', OUT / 'response_delay_pilot.png']:
        if p.exists():
            artifacts[p.name] = sha(p)
    record = {'commit': subprocess.check_output(['git','rev-parse','HEAD'], cwd=ROOT, text=True).strip(),
        'source_sha256': {str(p.relative_to(ROOT)): sha(p) for p in SOURCES + extra},
        'checked_scores': checked, 'simulated_outcomes': outcomes,
        'fit_parameter_records': len(fits), 'equal_drift_delay_parameter_count': True,
        'all_sources_match_fitting_and_scoring_hashes': True,
        'nested_training_solution_retained': True, 'trial_and_condition_alignment': True,
        'maximum_nll_reconstruction_error': max_reconstruction_error,
        'raw_zero_spread_checks': zero, 'pulse_estimator_checks': estimator,
        'artifacts_sha256': artifacts, 'python': platform.python_version(),
        'scope': 'Two selected mice; no population tests, model recovery, parameter intervals or global optimum claim'}
    write_json(OUT / 'integrity_audit.json', record)
    print(json.dumps({k: record[k] for k in ['checked_scores','simulated_outcomes','fit_parameter_records',
          'equal_drift_delay_parameter_count','maximum_nll_reconstruction_error']}, indent=2))


if __name__ == '__main__':
    main()
