"""Assemble Figure 4 from saved estimates only; no fitting or data selection."""
import argparse
import hashlib
import json
import shutil
import subprocess
from pathlib import Path

from scripts.paper.build_paper_2026_11_15 import (
    BLUE, ORANGE, PURPLE, GREEN, MICE, STYLE, interval, label, time_axis,
    plt, np, pd, student_t,
)
from scripts.paper.pulse_paired_psychometrics import draw_paired


def save(fig, stem):
    for ext in ('png', 'pdf', 'svg'):
        fig.savefig(stem.with_suffix('.' + ext), dpi=300)


def old_c(ax, frame):
    for kind, color, marker, offset, name in [('D', PURPLE, 'o', -.065, 'Directional'),
                                              ('S', GREEN, 's', .065, 'Shared toward correct side')]:
        interval(ax, np.arange(len(frame))+offset, frame[kind], frame[kind+'_boot_lo'],
                 frame[kind+'_boot_hi'], color=color, marker=marker, lw=1.1, label=name)
        for j, row in frame.iterrows():
            if row[kind+'_holm_boot'] < .05:
                ax.text(j+offset, row[kind+'_boot_hi']+.045, '*', ha='center', color=color, fontsize=10)
    time_axis(ax, frame)
    ax.set_ylabel('Pulse coefficient (log-odds)')
    ax.set_ylim(-.65, .92)
    ax.legend(loc='lower left')


def main():
    parser = argparse.ArgumentParser(__doc__)
    parser.add_argument('--previous', type=Path, required=True)
    parser.add_argument('--timing', type=Path, required=True)
    parser.add_argument('--interaction', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--persistence-sequence', action='store_true', help='D: directional persistence; E: dilution; assignment moved to supplement')
    parser.add_argument('--omit-dilution', action='store_true', help='A–D only; retain removed dilution table as historical support')
    parser.add_argument('--dilution-only', action='store_true', help='Keep compensated influence as D; omit separate directional panel')
    parser.add_argument('--model-free', action='store_true', help='Add saved model-free accuracy differences as E')
    parser.add_argument('--exponential-overlay', type=Path, help='Saved standalone pulse exponential preview directory')
    parser.add_argument('--compact-connected', action='store_true', help='Narrow compensated panel and connect observed points')
    args = parser.parse_args()
    if args.exponential_overlay and (not args.dilution_only or args.model_free):
        parser.error('--exponential-overlay requires --dilution-only without --model-free')
    if args.model_free and not args.dilution_only:
        parser.error('--model-free requires --dilution-only')
    if args.dilution_only and (not args.persistence_sequence or args.omit_dilution):
        parser.error('--dilution-only requires --persistence-sequence and excludes --omit-dilution')
    if args.omit_dilution and not args.persistence_sequence:
        parser.error('--omit-dilution requires --persistence-sequence')
    out = args.output
    out.mkdir(parents=True, exist_ok=False)
    shutil.copytree(args.previous/'source_data', out/'source_data')
    sd = out/'source_data'
    # Former C remains archived in a separate supplementary draft.
    archive = out/'supplementary_drafts'
    archive.mkdir()
    shutil.move(sd/'fig4_C_directional_shared.csv', archive/'former_C_directional_shared.csv')
    for source, name in [('influence_curves.csv', 'fig4_C_timing_curves.csv'),
                         ('slope_tests.csv', 'fig4_C_timing_slope_tests.csv'),
                         ('coefficients.csv', 'fig4_C_timing_coefficients.csv')]:
        shutil.copy2(args.timing/source, sd/name)
    backup = out/'backup_direction_interaction'
    backup.mkdir()
    for source in args.interaction.iterdir():
        if source.is_file():
            shutil.copy2(source, backup/source.name)
    (backup/'STATUS.md').write_text('Backup figure retained by author request. Not included in main Figure 4.\nSame joint ordinal model and interaction test as Figure 4C; not independent evidence.\n')
    table = lambda name: pd.read_csv(sd/(name+'.csv'))
    with plt.rc_context(STYLE):
        fig = plt.figure(figsize=(250/25.4, 165/25.4))
        a, c, d, e = [fig.add_axes(pos) for pos in [(.075,.59,.24,.27), (.075,.16,.24,.27),
                                                       (.405,.16,.24,.27), (.735,.16,.24,.27)]]
        points = table('fig4_A_displayed_pulse_points')
        curves = table('fig4_A_psychometric_curves')
        for direction, color, marker, name in [(-1, BLUE, 'v', 'Left pulse'), (1, ORANGE, '^', 'Right pulse')]:
            z = points[points.pulse == direction].sort_values('coherence_pct')
            a.errorbar(z.coherence_pct, z['mean'], yerr=z['sem'], fmt=marker, ls='none', color=color,
                       capsize=2, label=name, ms=3.7)
            z = curves[curves.pulse == direction].sort_values('coherence_pct')
            a.plot(z.coherence_pct, z.p_right, '-', c=color, lw=1.2)
        a.axhline(.5, color='.8', lw=.5)
        a.set(xlim=(-110,110), xticks=[-100,-36,0,36,100], ylim=(0,1), xlabel='Signed baseline coherence (%)', ylabel='P(right response)')
        a.legend(loc='upper left')
        label(a, 'A', 'Pulse direction shifts choices')
        aa = fig.add_axes([.435,.59,.18,.27]); bb = fig.add_axes([.755,.59,.18,.27])
        draw_paired([aa, bb], table('fig4_B_paired_parameters'), table('fig4_B_paired_tests'))
        aa.text(-.15,1.17,'B',transform=aa.transAxes,fontsize=10,fontweight='bold')
        fig.text(.435,.94,'Paired pulse psychometric parameters',fontsize=8.5)
        fig.text(.435,.49,'Each line: one mouse. Exploratory; weakly constrained fits retained.',fontsize=6,color='.3')
        timing = table('fig4_C_timing_curves')
        z = timing[(timing.comparison == 'all_available_10') & (timing.objective == 'wls')]
        c.fill_between(z.stage_index, z.ci_lo, z.ci_hi, color=PURPLE, alpha=.18, linewidth=0)
        c.plot(z.stage_index, z.influence, color=PURPLE, lw=1.5)
        stages = z[z.stage_index.isin([1., 2., 3.])]
        c.plot(stages.stage_index, stages.influence, 'o', color=PURPLE)
        c.axhline(0, color='.7', lw=.7)
        c.set(xlim=(.85,3.15), ylim=(-10,22), xticks=[1,2,3], xticklabels=['Early','Middle','Late'],
              xlabel='Pulse onset stage (coded 1, 2, 3)', ylabel='Directional pulse influence w\n(% coherence)')
        c.text(.04,.96,'Slope = −5.40 per stage\np = 0.023; 95% CI shaded', transform=c.transAxes, va='top', fontsize=6.3)
        c.text(.04,.04,'10 mice; late pulses in 6',transform=c.transAxes,fontsize=6.3,color='.3')
        label(c,'C','Pulse influence versus pulse timing')
        gamma = table('fig4_D_dilution_adjustment')
        z = gamma[gamma.lo_s >= .3].reset_index(drop=True)
        interval(d,np.arange(len(z)),z.gammaT,z.lo,z.hi,color='black',marker='o',lw=1.3,label='Observed; mouse-bootstrap 95% CI')
        d.hlines(float(z.K.iloc[0]),-.2,2.2,color='.5',ls=':',lw=1,label='Early-bin mean')
        time_axis(d,z)
        d.set_ylabel('Coherence-equivalent influence × RT\n(% coherence · s)')
        d.legend(loc='lower left')
        label(d,'D','Dilution-adjusted pulse influence')
        ss = table('fig4_E_assignment_effects').set_index('mouse').loc[MICE]
        for i, (_, row) in enumerate(ss.iterrows()):
            e.scatter(row.by_5s_pp,i,c=ORANGE if row.rig=='ucla' else BLUE,marker='o' if row.rig=='ucla' else 's',s=22)
        mean = ss.by_5s_pp.mean()
        half = student_t.ppf(.975,len(ss)-1)*ss.by_5s_pp.sem()
        e.errorbar(mean,len(ss)+.4,xerr=half,fmt='D',c='black',capsize=3,ms=4.5)
        e.axvline(0,color='.6',lw=.7)
        e.set(yticks=list(np.arange(len(ss)))+[len(ss)+.4],yticklabels=MICE+['Mean, 95% CI'],ylim=(len(ss)+1.2,-.7),xlabel='Right-pulse minus left-pulse\ndirectional response contrast (pp)')
        label(e,'E','Pulse effect across mice')
        if args.persistence_sequence:
            # Preserve the assignment analysis as an independently usable vector panel.
            e.set_title('Pulse effect across mice', loc='left', pad=7)
            for text in e.texts:
                if text.get_text() == 'E':
                    text.set_visible(False)
            fig.canvas.draw()
            bounds = e.get_tightbbox(fig.canvas.get_renderer()).transformed(fig.dpi_scale_trans.inverted()).expanded(1.04, 1.06)
            for ext in ('png', 'pdf', 'svg'):
                fig.savefig(archive/f'assignment_effects.{ext}', bbox_inches=bounds, dpi=300)
            d.clear(); e.clear()
            dec = pd.read_csv(archive/'former_C_directional_shared.csv')
            interval(d, np.arange(len(dec)), dec.D, dec.D_boot_lo, dec.D_boot_hi,
                     color=PURPLE, marker='o', lw=1.3, label='Mouse-bootstrap 95% CI')
            for j, row in dec.iterrows():
                if row.D_holm_boot < .05:
                    d.text(j, row.D_boot_hi+.045, '*', ha='center', color=PURPLE, fontsize=10)
            time_axis(d, dec)
            d.set_xlabel('Time from pulse to response (s)')
            d.set(ylim=(-.3,.92), ylabel='Directional pulse influence\n(log-odds)')
            d.legend(loc='lower left')
            label(d, 'D', 'Pulse influence after the pulse')
            interval(e, np.arange(len(z)), z.gammaT, z.lo, z.hi, color='black', marker='o', lw=1.3,
                     label='Mouse-bootstrap 95% CI')
            e.hlines(float(z.K.iloc[0]), -.2, 2.2, color='.5', ls=':', lw=1, label='Early-bin mean')
            time_axis(e, z)
            e.set_xlabel('Time from pulse to response (s)')
            e.set_ylabel('Coherence-equivalent influence × RT\n(% coherence · s)')
            e.legend(loc='lower left')
            label(e, 'E', 'Dilution-adjusted pulse influence')
        if args.omit_dilution:
            fig.delaxes(e)
            c.set_position([.09,.16,.34,.27])
            d.set_position([.57,.16,.34,.27])
        if args.dilution_only:
            fig.delaxes(d)
            e.set_position([.47,.16,.46,.27])
            for text in e.texts:
                if text.get_text() == 'E':
                    text.set_text('D')
                    text.set_position((-.10,1.10))
        if args.model_free:
            e.set_position([.405,.16,.24,.27])
            for text in e.texts:
                if text.get_text() == 'D': text.set_position((-.12,1.10))
            mf = fig.add_axes([.735,.16,.24,.27])
            source = Path('dissemination/paper_accumulation/tables')
            pm = pd.read_csv(source/'congruency_choice_effect_2026-10-30_per_mouse.csv')
            summary = pd.read_csv(source/'congruency_choice_effect_2026-10-30_summary.csv')
            grid = np.sort(summary.mid_ms.unique())
            for cat, color, marker, name in [('cong',BLUE,'o','Congruent'),('incong',ORANGE,'s','Incongruent')]:
                for _, group in pm[pm.cat==cat].groupby('mouse'):
                    values = group.set_index('mid_ms').d_pp.reindex(grid)
                    mf.plot(grid/1000,values,color=color,alpha=.22,lw=.65)
                group = summary[summary.cat==cat].sort_values('mid_ms')
                mf.errorbar(group.mid_ms/1000,group.mean_pp,yerr=group.sem_pp,fmt=marker+'-',color=color,ms=3,lw=1.4,capsize=2,label=name)
            mf.axhline(0,color='.7',lw=.7)
            mf.set(xlim=(0,2.1),xlabel='Time from pulse to response (s)',ylabel='Change in P(correct)\n(pulse − matched control; pp)')
            mf.legend(loc='upper right')
            label(mf,'E','Model-free accuracy change')
            for suffix in ['per_mouse','summary']:
                shutil.copy2(source/f'congruency_choice_effect_2026-10-30_{suffix}.csv',sd/f'fig4_E_model_free_{suffix}.csv')
        if args.exponential_overlay:
            exp_obs = pd.read_csv(args.exponential_overlay/'observations.csv')
            exp_curve = pd.read_csv(args.exponential_overlay/'curve.csv')
            exp_meta = json.loads((args.exponential_overlay/'manifest.json').read_text())
            np.testing.assert_allclose(exp_obs.gammaT, z.gammaT)
            e.clear()
            if args.compact_connected: e.set_position([.47,.16,.32,.27])
            e.vlines(exp_obs.mean_delay_s,exp_obs.ci_lo,exp_obs.ci_hi,color='black',lw=1.1)
            e.plot(exp_obs.mean_delay_s,exp_obs.gammaT,'o-' if args.compact_connected else 'o',color='black',lw=1.1,label='Observed; 95% CI' if args.compact_connected else 'Observed; mouse-bootstrap 95% CI')
            e.fill_between(exp_curve.delay_s,exp_curve.ci_lo,exp_curve.ci_hi,color=BLUE,alpha=.17,linewidth=0)
            e.plot(exp_curve.delay_s,exp_curve['fit'],color=BLUE,lw=1.5,label=(f'Exponential (τ = {exp_meta["fit"]["tau_s"]:.2f} s)' if args.compact_connected else f'Descriptive exponential (τ = {exp_meta["fit"]["tau_s"]:.2f} s)'))
            e.hlines(float(z.K.iloc[0]),exp_obs.mean_delay_s.iloc[0],exp_obs.mean_delay_s.iloc[2],color='.5',ls=':',lw=1,label='Early-bin mean')
            e.axhline(0,color='.7',lw=.7)
            e.set(xlabel='Mean time from pulse to response (s)',ylabel='Coherence-equivalent influence × RT\n(% coherence · s)')
            e.legend(loc='upper right',fontsize=6)
            label(e,'D','Dilution-adjusted pulse influence')
            for source,name in [('observations.csv','fig4_D_exponential_observations.csv'),('curve.csv','fig4_D_exponential_curve.csv'),('manifest.json','exponential_fit_manifest.json')]:
                shutil.copy2(args.exponential_overlay/source,sd/name)
        fig.suptitle('Figure 4 | Brief motion pulses influence subsequent choices',fontsize=10,x=.06,ha='left')
        save(fig,out/'figure4')
        plt.close(fig)
        detail, ax = plt.subplots(figsize=(95/25.4,85/25.4))
        detail.subplots_adjust(left=.20,right=.97,bottom=.25,top=.87)
        old_c(ax,pd.read_csv(archive/'former_C_directional_shared.csv'))
        ax.set_title('Directional and shared influence',loc='left',pad=7)
        save(detail,archive/'former_C_directional_shared')
        plt.close(detail)
    old_caption = (args.previous/'caption.md').read_text()
    former_caption = old_caption.split('**(C)**')[1].split('**(D)**')[0]
    (archive/'caption.md').write_text('# Supplementary draft: former Figure 4C\n\n'+former_caption.strip()+'\n\nUnassigned supplementary number; retained unchanged estimates.\n')
    new_c = ('**(C)** Directional pulse influence across early, middle and late pulse stages, coded 1, 2 and 3. '
             'A joint nonlinear psychometric model was fitted to 21,725 restricted responses, with categorical baseline offsets for 10 mice and shared pulse, coherence-sensitivity and asymptote parameters. '
             'Influence w is half the right-minus-left additive coherence-offset separation; points and line show fitted estimates, not raw observations. '
             'Shading shows pointwise 95% mouse-cluster CR1/t9 intervals using the full observed Hessian. '
             'The fitted linear slope was −5.40 coherence-percentage units per stage (95% CI −9.85 to −0.95; two-sided cluster p=0.0226; cluster-jackknife sensitivity p=0.0440). '
             'Only six mice contributed late pulses. The matched-six-mouse sensitivity analysis was inconclusive (slope −1.72, 95% CI −7.25 to 3.82, p=0.4615), so the all-available estimate depends on the shared-effect assumption. '
             'Ordinal stage is not elapsed physical time and does not estimate an intrinsic integration time constant.\n\n')
    caption = old_caption.split('**(C)**')[0] + new_c + '**(D)**' + old_caption.split('**(D)**')[1]
    caption = caption.replace('The x axes in C–D use discrete bins;', 'The x axis in D uses discrete bins;')
    caption = caption.split('Provisional artwork exported')[0] + 'Provisional v6 artwork: C replaced by the author-selected ordinal timing curve. A/B/D/E use unchanged saved estimates. Direction-interaction view retained as backup; former C retained as supplementary draft.\n'
    if args.persistence_sequence:
        assignment_caption = old_caption.split('**(E)**')[1].split('Provisional artwork')[0].strip()
        (archive/'assignment_caption.md').write_text('# Supplementary draft: assignment-based pulse influence\n\n'+assignment_caption+'\n')
        persistence_caption = ('**(D)** Directional pulse influence as a function of response latency from pulse onset. '
            'The pooled logistic decomposition includes categorical coherence-by-latency-bin baselines, categorical mouse intercepts, '
            'a directional pulse term and a shared term toward the baseline-correct side. Only the directional coefficient is displayed here; the full decomposition is retained in the supplement draft. '
            'Points show coefficients and vertical lines show percentile 95% intervals from 300 mouse-bootstrap refits. '
            'Asterisks mark Holm-adjusted bootstrap p<0.05 across seven directional bins; the three bins spanning 0.3–1.2 s each have adjusted p=0.0233. '
            'The early/middle-onset analysis includes 19,313 eligible responses from 10 mice (8,529 pulse responses), with symmetric pulse schedules, null pulses excluded, responses after actual or virtual pulse offset, and at least 0.1 s after onset. '
            'Controls use matched virtual onsets. Zero-coherence responses contribute to the directional term but not the signed shared term. '
            'Late-onset pulse and matched-control strata are excluded here, unlike the all-available onset-stage model in C. '
            'The curve shows sustained directional influence through responses made 0.9–1.2 s after pulse onset; it does not estimate an intrinsic integration time constant.\n\n')
        dilution_caption = old_caption.split('**(D)**')[1].split('**(E)**')[0]
        dilution_caption = dilution_caption.replace('The x axes in C–D use discrete bins;', 'The x axes in D–E use discrete bins;')
        caption = caption.split('**(D)**')[0] + persistence_caption + '**(E)**' + dilution_caption
        caption += ('Current v7 sequence: A pulse psychometrics; B paired parameters; C pulse-onset stage; D post-pulse persistence; E dilution-adjusted influence. '
                    'The D/E analyses reuse the same response-selected population and are complementary summaries, not independent replications. '
                    'The assignment contrast, full directional/shared decomposition and direction-interaction backup are retained separately. No refits or new tests.\n')
        shutil.move(sd/'fig4_D_dilution_adjustment.csv', sd/'fig4_E_dilution_adjustment.csv')
        shutil.move(sd/'fig4_E_assignment_effects.csv', archive/'assignment_effects.csv')
        shutil.copy2(archive/'former_C_directional_shared.csv', sd/'fig4_D_persistence.csv')
    if args.omit_dilution:
        caption = caption.split('**(E)**')[0] + 'Current figure contains A–D. Dilution-adjusted panel omitted at author request; historical results are preserved separately. Congruency ROC is not selected for inclusion. No refits or new tests.\n'
        shutil.move(sd/'fig4_E_dilution_adjustment.csv', archive/'historical_dilution_adjustment.csv')
    if args.dilution_only:
        removed = caption.split('**(D)**')[1].split('**(E)**')[0]
        (archive/'directional_persistence_caption.md').write_text(removed.strip()+'\n')
        retained = caption.split('**(E)**')[1].split('Current v7 sequence:')[0]
        retained = retained.replace('The x axes in D–E use discrete bins;', 'The x axis in D uses discrete bins;')
        retained += ('The analysis uses 19,313 eligible early/middle responses from 10 mice, with matched virtual control onsets, responses after pulse offset and at least 0.1 s after onset. '
                     'Late-onset strata are excluded here, whereas C includes late pulses from six mice.\n\n')
        caption = caption.split('**(D)**')[0]+'**(D)**'+retained+'Current figure: A–C preserved; dilution-adjusted influence retained as D. Separate directional panel removed; congruency ROC excluded from planned supplement. No refits or new tests.\n'
        shutil.move(sd/'fig4_D_persistence.csv', archive/'directional_persistence.csv')
        shutil.move(sd/'fig4_E_dilution_adjustment.csv', sd/'fig4_D_dilution_adjustment.csv')
    if args.model_free:
        caption = caption.split('Current figure:')[0]
        caption += ('**(E)** Model-free change in accuracy relative to matched control responses. '
            'For each pulse response, its correctness was compared with control accuracy in the same mouse, signed baseline coherence and pulse-to-response latency bin. '
            'Congruent pulses agree with the nonzero baseline/task-correct direction; incongruent pulses oppose it. '
            'Only absolute coherences 9–36%, early/middle pulse schedules and responses at least 0.1 s after pulse onset were included, using the existing eligibility selection. '
            'Thin traces show individual mice; bold points and lines show unweighted mouse means, with SEM error bars. '
            'Mouse-by-condition bins require at least 10 pulse responses; 5–9 mice contribute per point. '
            'Missing individual bins are left as gaps. Existing two-sided mouse-level Wilcoxon tests used Holm correction over 12 condition-by-bin contrasts; none passed correction. '
            'These descriptive response-conditioned differences are supporting views of the same experiment, not independent replication or estimates of an unconditional assignment effect.\n\n'
            'Current figure: A–C preserved; compensated D retained and model-free E added. Congruency ROC remains excluded. No refits or new tests.\n')
    if args.exponential_overlay:
        caption = caption.replace('The x axis in D uses discrete bins; spacing does not represent equal physical durations.',
            'Points in D are positioned at the observed mean pulse-to-response latency of each bin; the x axis is physical time.')
        caption += ('\nThe blue overlay in D is the saved descriptive exponential y=A exp[−(t−t_ref)/τ], '
            'with fixed zero asymptote, nonnegative amplitude and unweighted least squares across all six displayed bins. '
            'The negative late estimate is retained. τ=1.11 s (percentile 95% interval 0.45–3.73 s from 600 saved whole-mouse bootstrap curves; seven fits reach the slow-decay search boundary). '
            'Blue shading is the pointwise bootstrap fit band, conditional on observed mean time coordinates. '
            'This is an approximate description of the time course, not an intrinsic forgetting-time estimate. No new fit was performed for the overlay.\n')
    if args.compact_connected:
        caption += '\nObserved points in D are connected as a visual guide; the black segments are not an additional fitted model. Panel width is reduced for author review.\n'
    (out/'caption.md').write_text(caption)
    preserved_paths = {p.name: sd/p.name for p in (args.previous/'source_data').glob('*.csv')
                       if not p.name.startswith('fig4_C_')}
    if args.persistence_sequence:
        preserved_paths['fig4_D_dilution_adjustment.csv'] = (archive/'historical_dilution_adjustment.csv' if args.omit_dilution else sd/'fig4_E_dilution_adjustment.csv')
        preserved_paths['fig4_E_assignment_effects.csv'] = archive/'assignment_effects.csv'
    if args.dilution_only:
        preserved_paths['fig4_D_dilution_adjustment.csv'] = sd/'fig4_D_dilution_adjustment.csv'
    unchanged = {name: (args.previous/'source_data'/name).read_bytes() == target.read_bytes()
                 for name, target in preserved_paths.items()}
    verification = {'unchanged_ABDE_source_tables':unchanged, 'no_refitting':True,
                    'timing_source_copied_exactly':(args.timing/'influence_curves.csv').read_bytes()==(sd/'fig4_C_timing_curves.csv').read_bytes(),
                    'primary_curve_rows':len(timing[(timing.comparison=='all_available_10')&(timing.objective=='wls')]),
                    'late_mice':6, 'total_mice':10}
    assert all(unchanged.values()) and verification['timing_source_copied_exactly']
    (out/'verification.json').write_text(json.dumps(verification,indent=2)+'\n')
    sources = [*sd.glob('fig4_D_exponential*'), *sd.glob('exponential_fit_manifest.json'), *sd.glob('fig4_E_model_free*.csv'), *args.previous.glob('source_data/*.csv'), *args.timing.glob('*.csv'), Path(__file__)]
    (out/'figure_manifest.json').write_text(json.dumps({'base_commit':subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),
        'previous':str(args.previous),'timing':str(args.timing),'backup':str(args.interaction),
        'persistence_sequence':args.persistence_sequence,'omit_dilution':args.omit_dilution,
        'dilution_only':args.dilution_only,'model_free':args.model_free,'compact_connected':args.compact_connected,
        'exponential_overlay':str(args.exponential_overlay) if args.exponential_overlay else None,
        'source_sha256':{str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in sources},
        'scope':'Saved-estimate assembly only; no refitting, new tests or trial exclusions.'},indent=2)+'\n')


if __name__ == '__main__':
    main()
