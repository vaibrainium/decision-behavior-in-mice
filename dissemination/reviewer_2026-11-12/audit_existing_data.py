"""Independent, lightweight reviewer checks; does not refit models or alter inputs.

Run from repository root:
  .venv/bin/python dissemination/reviewer_2026-11-12/audit_existing_data.py
Outputs go beside this script. The eventual-choice analysis is an exploratory
sensitivity, not a replacement for the prespecified five-second endpoint.
"""
from pathlib import Path
import hashlib
import json
import subprocess

import numpy as np
import pandas as pd
from scipy import stats

ROOT = Path(__file__).resolve().parents[2]
OUT = Path(__file__).resolve().parent
PROCESSED = Path('/mnt/data/processed')
TRIALS = PROCESSED / 'pulse_followup/20261023T191030Z_fa8de8b/data/trial_table.csv'


def signed_effect(table, side_column):
    """Independent groupby estimator, using original common-support weights."""
    d = table[table.in_primary_coherence & table.pulse_category.isin(['positive', 'negative'])].copy()
    d['directional_response'] = d[side_column].map({'L': -.5, 'R': .5, 'none': 0.})
    keys = ['mouse', 'session', 'coherence_pct', 'onset_stratum']
    cells = d.groupby(keys + ['pulse_category'], observed=True).directional_response.agg(['mean', 'size'])
    cells = cells.unstack('pulse_category').dropna()
    cells['weight'] = np.minimum(cells['size', 'positive'], cells['size', 'negative'])
    cells['difference'] = 100 * (cells['mean', 'positive'] - cells['mean', 'negative'])
    rows = []
    for mouse, c in cells.groupby(level='mouse'):
        rows.append({'mouse': mouse, 'effect_pp': np.average(c['difference'], weights=c['weight']),
                     'n_cells': len(c), 'n_trials': int(c['size'].sum().sum())})
    return pd.DataFrame(rows)


def summary(values):
    v = np.asarray(values, float)
    n = len(v)
    half = stats.t.ppf(.975, n - 1) * stats.sem(v) if n > 1 else np.nan
    return {'n_mice': n, 'mean_pp': float(v.mean()), 'lo_pp': float(v.mean() - half),
            'hi_pp': float(v.mean() + half), 'p_t_unadjusted': float(stats.ttest_1samp(v, 0).pvalue) if n > 1 else None}


def sha256(path):
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for block in iter(lambda: f.read(1048576), b''):
            h.update(block)
    return h.hexdigest()


def main():
    t = pd.read_csv(TRIALS, low_memory=False)
    a = pd.read_csv(PROCESSED / 'aggregate_data.csv', dtype={'session_id': str})
    valid = pd.read_csv(PROCESSED / 'valid_data.csv', dtype={'session_id': str})
    assert t.trial_id.is_unique and t.aggregate_row.is_unique
    assert t.event.sum() == len(valid)
    src = a.loc[t.aggregate_row].reset_index(drop=True)
    assert (src.subject_id.to_numpy() == t.mouse.to_numpy()).all()
    assert (src.session_id.to_numpy() == t.session_id.astype(str).to_numpy()).all()
    assert (src.signed_coherence.to_numpy() == t.coherence_pct.to_numpy()).all()
    # Aggregate choices are 0/1 after compilation, confirmed by unique values.
    assert set(src.choice.dropna().unique()).issubset({0., 1.})
    recovered = t.is_censored & src.choice.notna() & src.reaction_time.notna() & (src.reaction_time > 5)
    t['eventual_side'] = t.response_side.copy()
    t.loc[recovered, 'eventual_side'] = np.where(src.loc[recovered, 'choice'] == 1, 'R', 'L')
    first = signed_effect(t, 'response_side').rename(columns={'effect_pp': 'by_5s_pp'})
    eventual = signed_effect(t, 'eventual_side').rename(columns={'effect_pp': 'eventual_pp'})
    p = first.merge(eventual[['mouse', 'eventual_pp']], on='mouse', validate='one_to_one')
    p['rig'] = p.mouse.map(t.groupby('mouse').rig.first())
    p.to_csv(OUT / 'independent_signed_effects.csv', index=False)
    assert abs(p.by_5s_pp.mean() - 5.844356) < .00001
    provenance = {'aggregate_trials': len(a), 'aggregate_mice': a.subject_id.nunique(),
                  'aggregate_sessions': len(a[['subject_id', 'session_id']].drop_duplicates()),
                  'valid_responded_trials': len(valid), 'valid_mice': valid.subject_id.nunique(),
                  'valid_sessions': len(valid[['subject_id', 'session_id']].drop_duplicates()),
                  'table_trials': len(t), 'table_censored': int(t.is_censored.sum()),
                  'late_choices_restored': int(recovered.sum()),
                  'legacy_controls_with_scheduled_signed_pulse': int(((t.pulse_type_rt_dependent == 0) & t.pulse_category.isin(['positive', 'negative'])).sum())}
    effects = {'by_5s': summary(p.by_5s_pp), 'eventual_choice_sensitivity': summary(p.eventual_pp),
               'by_5s_without_PSUIM6_7_exploratory': summary(p[~p.mouse.isin(['PSUIM6', 'PSUIM7'])].by_5s_pp),
               'by_5s_per_rig_descriptive_only': {rig: summary(d.by_5s_pp) for rig, d in p.groupby('rig')}}
    # Recalculate the held-out score split from per-mouse values, rather than reports.
    score_path = ROOT / 'dissemination/paper_control/tables/heldout_diff_per_mouse_2026-10-29.csv'
    score = pd.read_csv(score_path)
    components = score.groupby(['model', 'part']).per_1000.mean().unstack()
    components['choice_share'] = components.choice / components.rescored_total
    components.to_csv(OUT / 'independent_score_components.csv')
    # Verify exact invariance to re-pairing prediction rows within condition.
    from src.ddm.likelihood_calculator_censored import CensoredQMLE
    rng = np.random.default_rng(13)
    cond = np.repeat(np.arange(3), 80)
    rt = rng.uniform(.3, 5, len(cond))
    choice = rng.integers(0, 2, len(cond))
    pred_rt = rng.uniform(.3, 5, len(cond))
    pred_choice = rng.integers(0, 2, len(cond))
    perm = np.concatenate([rng.permutation(np.flatnonzero(cond == k)) for k in np.unique(cond)])
    likelihood = CensoredQMLE(include_censored=False)
    n1 = likelihood.compute_nll(pred_rt, pred_choice, rt, choice, cond, cond)
    n2 = likelihood.compute_nll(pred_rt[perm], pred_choice[perm], rt, choice, cond[perm], cond)
    assert n1 == n2
    result = {'commit': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
              'provenance': provenance, 'effects': effects,
              'synthetic_qmle_pairing_invariance': {'original_nll': n1, 'repaired_nll': n2, 'difference': n2 - n1},
              'input_sha256': {str(f): sha256(f) for f in [TRIALS, PROCESSED / 'aggregate_data.csv', PROCESSED / 'valid_data.csv', score_path]}}
    (OUT / 'independent_audit.json').write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps(result, indent=2))
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    fig, axes = plt.subplots(1, 3, figsize=(13, 4), constrained_layout=True)
    colors = np.where(p.rig == 'uw', '#4878a8', '#b86b33')
    y = np.arange(len(p))
    axes[0].scatter(p.by_5s_pp, y, c=colors, label='By 5 s')
    axes[0].scatter(p.eventual_pp, y, facecolors='none', edgecolors=colors, marker='s', label='Eventual recorded choice')
    axes[0].axvline(0, c='gray', lw=.8)
    axes[0].set(yticks=y, yticklabels=p.mouse, xlabel='Signed assignment effect (percentage points)', title='Independent pulse-effect check')
    axes[0].legend(fontsize=7)
    q = components.loc[['E', 'ES']]
    axes[1].bar(q.index, q.choice, label='Choice', color='#4878a8')
    axes[1].bar(q.index, q.rt, bottom=q.choice, label='Response time', color='#b86b33')
    axes[1].set(ylabel='Alternative minus integrator NLL / 1,000 trials', title='Source of control-model advantage')
    axes[1].legend(fontsize=8)
    axes[2].bar(['All sessions', 'Retained sessions'], [provenance['aggregate_sessions'], provenance['valid_sessions']], color=['.65', '#4878a8'])
    axes[2].set(ylabel='Mouse × session count', title='Restricted analysis population')
    for ax in axes:
        ax.spines[['top', 'right']].set_visible(False)
    fig.savefig(OUT / 'reviewer_diagnostics.png', dpi=180)
    fig.savefig(OUT / 'reviewer_diagnostics.pdf')


if __name__ == '__main__':
    main()
