"""Build the accumulation paper's first figure set from existing audited results.

No decision-model fitting, simulations, package changes or previous-output writes.
Author-requested descriptive psychometric fits and control mean RTs are included. New output
folder is mandatory. Run as a module so project imports resolve.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import subprocess

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
from matplotlib.lines import Line2D
from matplotlib.patches import FancyBboxPatch
import numpy as np
import pandas as pd
from scipy.stats import t as student_t
from src.utils.pmf_utils import fit_psychometric_function

from config import dir_config
from scripts.paper.fig1_task_behaviour import (
    panel_task, panel_schedule, make_schedule, psychometric_table, rt_table,
)
from scripts.behavior.huk_shadlen_replication import load as load_huk
from scripts.behavior.pulse_decomposition import design

ROOT = Path(__file__).resolve().parents[2]
TABLES = 'dissemination/paper_accumulation/tables/'
DYN = 'dissemination/pulse_dynamics_2026-11-13/'
TRADE = 'dissemination/pulse_rt_tradeoff_2026-11-13/'
CTRL = 'dissemination/paper_control/tables/'
MICE = ['DBM12', 'DBM13', 'DBM14', 'DBM15', 'DBM5', 'DBM6', 'PSUIM10', 'PSUIM5', 'PSUIM6', 'PSUIM7']
BLUE, ORANGE, GREEN, PURPLE = '#0072B2', '#D55E00', '#007F5F', '#8D4B8D'
COLORS = {'control_primary': BLUE, 'power_leak_urgency': ORANGE,
          'pw_per_time_no_sv': GREEN, 'no_sv': PURPLE}
NAMES = {'control_primary': 'Control-trained accumulator',
         'power_leak_urgency': 'Joint power + leak + urgency',
         'pw_per_time_no_sv': 'Joint onset weights; no drift variability',
         'no_sv': 'Joint no-leak accumulator; no drift variability'}
STYLE = {
    'font.family': 'DejaVu Sans', 'font.size': 7.3,
    'axes.labelsize': 7.3, 'axes.titlesize': 8.1, 'axes.titleweight': 'normal',
    'xtick.labelsize': 6.7, 'ytick.labelsize': 6.7, 'legend.fontsize': 6.3,
    'legend.frameon': False, 'axes.spines.top': False, 'axes.spines.right': False,
    'axes.linewidth': .6, 'xtick.major.width': .6, 'ytick.major.width': .6,
    'lines.linewidth': 1.1, 'lines.markersize': 3.7,
    'pdf.fonttype': 42, 'svg.fonttype': 'none', 'figure.facecolor': 'white',
    'savefig.facecolor': 'white', 'axes.unicode_minus': True,
}

class Builder:
    def __init__(self, output: Path):
        self.output = output
        self.output.mkdir(parents=True, exist_ok=False)
        (self.output / 'source_data').mkdir()
        self.sources = {}
        self.panels = []
        self.figures = []
        self.summary = {}

    def record(self, path: Path):
        self.sources[str(path)] = hashlib.sha256(path.read_bytes()).hexdigest()
        return path

    def read(self, relative: str):
        return pd.read_csv(self.record(ROOT / relative))

    def export(self, frame: pd.DataFrame, name: str, detail: str):
        path = self.output / 'source_data' / f'{name}.csv'
        frame.to_csv(path, index=False)
        self.panels.append({'panel': name, 'table': str(path.relative_to(self.output)),
                            'definition': detail, 'rows': len(frame)})

    def save(self, fig, name, title, book):
        fig.suptitle(title, fontsize=10, x=.06, ha='left')
        fig.canvas.draw()
        renderer=fig.canvas.get_renderer()
        import matplotlib.text as mtext
        clipping=[]
        displayed=list(fig.texts)
        for axis in fig.axes:
            displayed.extend(axis.texts)
            displayed.extend([axis.title,axis._left_title,axis._right_title])
            if axis.axison:
                for coordinate in [axis.xaxis,axis.yaxis]:
                    if not coordinate.get_visible():
                        continue
                    displayed.append(coordinate.label)
                    lower,upper=sorted(coordinate.get_view_interval())
                    for tick in coordinate.get_major_ticks()+coordinate.get_minor_ticks():
                        if lower-1e-9<=tick.get_loc()<=upper+1e-9:
                            displayed.extend([tick.label1,tick.label2])
            legend=axis.get_legend()
            if legend is not None:
                displayed.extend(legend.get_texts())
        for item in displayed:
            if not item.get_visible() or not item.get_text().strip():
                continue
            bounds=item.get_window_extent(renderer)
            if bounds.x0 < -1 or bounds.y0 < -1 or bounds.x1 > fig.bbox.x1+1 or bounds.y1 > fig.bbox.y1+1:
                clipping.append({'text':item.get_text(),'bbox_px':[bounds.x0,bounds.y0,bounds.x1,bounds.y1]})
        self.summary.setdefault('layout_checks',{})[name]={'text_outside_canvas':clipping}
        for ext in ['pdf', 'svg', 'png']:
            fig.savefig(self.output / f'{name}.{ext}', dpi=300 if ext == 'png' else None)
        book.savefig(fig)
        self.figures.append({'figure': name, 'title': title,
                             'width_mm': fig.get_figwidth() * 25.4,
                             'height_mm': fig.get_figheight() * 25.4})
        plt.close(fig)


def label(ax, letter, title):
    ax.set_title(title, loc='left', pad=7)
    ax.text(-.12, 1.10, letter, transform=ax.transAxes, ha='left', va='bottom',
            fontweight='bold', fontsize=10)


def time_axis(ax, frame):
    labels = [f'{a:g}–{b:g}' for a, b in zip(frame.lo_s, frame.hi_s)]
    ax.set_xticks(np.arange(len(frame)), labels, rotation=35, ha='right')
    ax.set_xlabel('Pulse-to-response interval (s; discrete bins)')
    ax.axhline(0, color='.7', lw=.7, zorder=0)


def interval(ax, x, estimate, low, high, **kwargs):
    # Plot endpoints directly: asymmetric bootstrap intervals need not contain
    # a point estimate. Do not clip an interval to make errorbar() accept it.
    ax.vlines(x, low, high, **{k:v for k,v in kwargs.items() if k in {'color','alpha','lw','zorder'}})
    ax.plot(x, estimate, **{k:v for k,v in kwargs.items() if k not in {'alpha','lw','zorder'}},
            alpha=kwargs.get('alpha',1), lw=kwargs.get('lw',1), zorder=kwargs.get('zorder',3))


def control_rt_means(b, psychometric_mouse):
    """Summarize retained control RTs, matching the accepted choice population."""
    data = pd.read_csv(b.record(Path(dir_config.data.processed) / 'valid_data.csv'))
    # Equivalent to scheduled_pulse == 0 for this dataset; verify the complete
    # mouse/coherence population against the archived control summary below.
    control = data[(~data.is_pulse_trial) | data.pulse_coherence.eq(data.signed_coherence)].copy()
    assert control.reaction_time.between(.3, 5).all()
    assert control.choice.isin([0, 1]).all()
    observed = control.groupby(['subject_id', 'signed_coherence']).agg(
        n_trials=('choice', 'size'), p_right=('choice', 'mean')).sort_index()
    expected = psychometric_mouse.set_index(['subject_id', 'signed_coherence'])[['n_trials', 'p_right']].sort_index()
    pd.testing.assert_frame_equal(observed, expected, check_dtype=False)
    control['response_class'] = np.where(control.choice.eq(1), 'right choice', 'left choice')
    mouse = control.groupby(['subject_id', 'signed_coherence', 'response_class'], as_index=False).agg(
        n_trials=('reaction_time', 'size'), mean_rt_s=('reaction_time', 'mean'))
    mouse['eligible'] = mouse.n_trials >= 10
    shown = mouse[mouse.eligible]
    group = shown.groupby(['signed_coherence', 'response_class'], as_index=False).agg(
        mean=('mean_rt_s', 'mean'), sem=('mean_rt_s', 'sem'), n_mice=('subject_id', 'nunique'),
        n_trials_in_eligible_cells=('n_trials', 'sum'))
    return mouse, group


def figure1(b, book):
    prefix='dissemination/paper/figures/fig1_task_behaviour_2026-10-26_v2_source_'
    pm=b.read(prefix+'psychometric_mouse.csv')
    pg=b.read(prefix+'psychometric_group.csv')
    rm, rg = control_rt_means(b, pm)
    schedule=b.read(prefix+'schedule.csv')
    overview=b.read(prefix+'overview.csv').set_index('rig').loc['all']
    b.export(schedule, 'fig1_B_schedule', 'Scheduled signed-pulse timing in accepted sessions, independent of observed response timing. Onset spans are observed ranges.')
    b.export(pm, 'fig1_C_psychometric_mouse', 'Scheduled controls, responses by 5 s; each row is a mouse × signed coherence.')
    b.export(pg, 'fig1_C_psychometric_group', 'Unweighted mouse means and SEM; number of contributing mice can vary by coherence.')
    b.export(rm, 'fig1_D_rt_mouse', 'Scheduled controls; arithmetic mean RT per mouse, signed coherence and physical choice direction, including zero coherence. Display requires at least 10 trials per cell; excluded cells retained here.')
    b.export(rg, 'fig1_D_rt_group', 'Unweighted mean and SEM across eligible mouse arithmetic means by choice direction. n_mice is given for every point.')
    prep = ROOT / DYN / 'preparation_checks.json'
    n_model = json.loads(b.record(prep).read_text())['n_input_trials']
    counts = {'n_mice':int(overview.n_mice), 'n_sessions':int(overview.n_mouse_sessions),
              'n_responded':int(overview.n_responded), 'n_no_response_by_5s':int(overview.n_no_response),
              'n_accepted_eligible':int(overview.n_trials), 'n_model':n_model,
              'n_control_responded':int(pm.n_trials.sum()),
              'n_control_psychometric_mice':int(pm.subject_id.nunique())}
    # The count of sessions is independently audited, not inferred from a guessed
    # CSV identifier. Read the chronology audit for the manuscript denominator.
    audit = ROOT / 'dissemination/history_dynamics_2026-11-14/selection_audit.json'
    counts['n_sessions'] = json.loads(b.record(audit).read_text())['n_accepted_sessions']
    assert counts['n_responded'] == 25508 and n_model == 25493
    b.summary['population'] = counts
    b.export(pd.DataFrame([counts]), 'fig1_population', 'Accepted-session analysis flow; no response by 5 s includes late recorded choices and no-choice trials. Corrections are not in this eligible trial table.')
    fig = plt.figure(figsize=(180/25.4, 132/25.4), layout='constrained')
    grid = fig.add_gridspec(2,2,height_ratios=[1,1.05],hspace=.12,wspace=.08)
    aa, ab, ac, ad = [fig.add_subplot(grid[i,j]) for i,j in [(0,0),(0,1),(1,0),(1,1)]]
    panel_task(aa)
    panel_schedule(ab, schedule)
    for ax in [aa,ab]:
        for t in ax.texts:
            t.set_fontsize(max(6.1,t.get_fontsize()))
    label(aa,'A','Motion discrimination')
    label(ab,'B','Brief signed motion perturbations')
    # Source tables were extracted with sched_pulse_type == 0, then responded-only.
    # Match the author's four-parameter logistic and its fitting implementation.
    fit_rows, fit_curves = [], []
    x_fit = np.linspace(-100, 100, 401)
    for mouse, g in pm.groupby('subject_id'):
        model = fit_psychometric_function(g.signed_coherence.to_numpy(), g.p_right.to_numpy(),
                                         g.n_trials.to_numpy(), 'logit_4')
        pred = model.predict(x_fit)
        ac.plot(x_fit,pred,c='.72',lw=.55,alpha=.7)
        ac.plot(g.signed_coherence,g.p_right,ls='none',marker='o',ms=1.5,c='.72',alpha=.6)
        fit_rows.append({'subject_id':mouse,'weighting':'trial-count weighted least squares',**model.coefs_})
        fit_curves.extend({'subject_id':mouse,'signed_coherence':x,'p_right':y} for x,y in zip(x_fit,pred))
    # Fit the unweighted mouse means: do not let trial-rich mice set the group curve.
    model = fit_psychometric_function(pg.signed_coherence.to_numpy(), pg['mean'].to_numpy(), None, 'logit_4')
    fit_rows.append({'subject_id':'group','weighting':'unweighted least squares on mouse means',**model.coefs_})
    pred = model.predict(x_fit)
    fit_curves.extend({'subject_id':'group','signed_coherence':x,'p_right':y} for x,y in zip(x_fit,pred))
    b.export(pd.DataFrame(fit_rows),'fig1_C_psychometric_parameters','Author logit_4 implementation; existing helper default bounds. Group fit uses equal-mouse means; individual fits use trial counts.')
    b.export(pd.DataFrame(fit_curves),'fig1_C_psychometric_curves','Smooth four-parameter logistic predictions on a fixed coherence grid; descriptive fits only.')
    ac.errorbar(pg.signed_coherence,pg['mean'],yerr=pg['sem'],fmt='o',ls='none',c='black',capsize=2,label='Control data ± SEM')
    ac.plot(x_fit,pred,c='black',lw=1.3,label='4-parameter fit')
    ac.axhline(.5,c='.8',lw=.6,ls=':')
    ac.set(xlim=(-105,105),ylim=(0,1),xticks=[-100,-36,0,36,100],xlabel='Signed coherence (%)',ylabel='P(right response)')
    ac.legend(loc='upper left')
    label(ac,'C','Control-trial psychometric function')
    for cls,col,marker,ls in [('right choice',ORANGE,'o','-'),('left choice',BLUE,'s','-')]:
        g=rg[rg.response_class==cls]
        ad.plot(g.signed_coherence,g['mean'],marker=marker,c=col,ls='none',label=cls.capitalize())
        # Reindex to preserve visible gaps if any coherence has no eligible mice.
        connected = g.set_index('signed_coherence').reindex(pg.signed_coherence)
        ad.fill_between(connected.index.to_numpy(),
                        (connected['mean']-connected['sem']).to_numpy(),
                        (connected['mean']+connected['sem']).to_numpy(),
                        color=col,alpha=.18,linewidth=0,zorder=1)
        ad.plot(connected.index,connected['mean'],c=col,ls=ls,lw=1.1)
    ad.axvline(0,c='.8',lw=.6,ls=':')
    ad.set(xlabel='Signed coherence (%)',ylabel='Mean RT (s)',xticks=[-100,-36,0,36,100],xlim=(-105,105))
    ad.margins(y=.25)
    ad.legend(loc='upper right')
    label(ad,'D','Control-trial response times')
    b.save(fig,'figure1','Figure 1 | Task and control-trial performance',book)


def figure2(b, book):
    d=b.read(CTRL+'heldout_diff_per_mouse_2026-10-29.csv')
    g=b.read(CTRL+'heldout_group_2026-10-29.csv')
    conf=b.read(CTRL+'recovery_confusion_2026-10-30_v3.csv')
    cohorts=b.read(CTRL+'recovery_cohort_rates_2026-10-30_v3.csv')
    d=d[d.model.isin(['E','ES'])].copy()
    b.export(d,'fig2_AB_control_differences','Alternative NLL minus accumulator NLL, per 1,000 held-out control trials; positive favors accumulation. Existing five-fold scores.')
    b.export(g[g.model.isin(['E','ES'])],'fig2_AB_group_statistics','Existing mouse-level group statistics; Holm correction follows the original four-alternative comparison family, separately by score component.')
    order=['C','E','ES','DDMx','ESx']
    conf=conf.set_index('generator').loc[order,order]
    assert (conf.sum(axis=1)==20).all()
    b.export(conf.reset_index(),'fig2_C_recovery','Winner counts across all five fitted candidates; 20 fixed dataset pairs per generator. Each candidate fit uses the same generated train/test data.')
    cohort=cohorts[cohorts.generator.isin(['C','E','ES'])]
    b.export(cohort,'fig2_D_recombined_cohorts','Existing fraction of 1,024 recombinations of two replicates per mouse that reproduce an accumulation preference; not 1,024 independent simulations.')
    fig,axes=plt.subplots(2,2,figsize=(180/25.4,156/25.4),layout='constrained',gridspec_kw={'hspace':.16,'wspace':.09})
    ax=axes[0,0]
    dt=d[d.part=='total']
    for j,(model,col) in enumerate([('E',BLUE),('ES',ORANGE)]):
        z=dt[dt.model==model].set_index('mouse').loc[MICE]
        offsets=np.linspace(-.12,.12,len(z))
        ax.scatter(j+offsets,z.per_1000,c=col,marker='o' if j==0 else 's',s=19,zorder=3)
        mean=z.per_1000.mean(); sem=z.per_1000.sem()
        ax.errorbar(j+.23,mean,yerr=sem,fmt='D',c='black',capsize=3,ms=4)
    for mouse in MICE:
        z=dt[dt.mouse==mouse].set_index('model')
        offset=np.linspace(-.12,.12,len(MICE))[MICE.index(mouse)]
        ax.plot([offset,1+offset],[z.loc['E','per_1000'],z.loc['ES','per_1000']],c='.75',lw=.5,zorder=0)
    ax.axhline(0,c='.5',lw=.8)
    ax.set(xticks=[0,1],xticklabels=['Rapid forgetting\n(E)','Sample extrema\n(ES)'],ylabel='Alternative − accumulation NLL\n(per 1,000 control trials)',xlim=(-.35,1.48))
    ax.text(.02,.98,'Points: mice; diamonds: mean ± SEM',transform=ax.transAxes,va='top',fontsize=6.1)
    label(ax,'A','Control prediction favors accumulation')
    ax=axes[0,1]
    for j,model in enumerate(['E','ES']):
        vals=g[(g.model==model)&g.part.isin(['choice','rt'])].set_index('part')['mean']
        ax.bar(j,vals['choice'],color=BLUE,label='Choice' if j==0 else None,width=.56)
        ax.bar(j,vals['rt'],bottom=vals['choice'],color=ORANGE,label='RT' if j==0 else None,width=.56,hatch='//',lw=.25,edgecolor='white')
        ax.text(j,vals.sum()+.7,f'{vals.sum():.2f}',ha='center',fontsize=7)
    ax.axhline(0,c='.5',lw=.7)
    ax.set(xticks=[0,1],xticklabels=['E','ES'],ylabel='Mean NLL advantage for accumulation\n(per 1,000 control trials)',ylim=(0,24))
    ax.legend(loc='upper left')
    label(ax,'B','Most discrimination comes from RTs')
    ax=axes[1,0]
    im=ax.imshow(conf.to_numpy()/20,vmin=0,vmax=1,cmap='Blues',aspect='equal')
    for i in range(5):
        for j in range(5):
            n=int(conf.iloc[i,j]); ax.text(j,i,str(n),ha='center',va='center',color='white' if n>=12 else 'black',fontsize=7.7)
    ax.set(xticks=range(5),xticklabels=order,yticks=range(5),yticklabels=order,xlabel='Best-scoring candidate',ylabel='Generating model')
    cb=fig.colorbar(im,ax=ax,shrink=.75,pad=.025); cb.set_label('Fraction of 20 dataset pairs')
    label(ax,'C','Fixed-data strategy recovery')
    ax=axes[1,1]
    cc=cohort.set_index('generator').loc[['C','E','ES']]
    yy=np.arange(3)
    for col,offset,color,marker,lab in [('rep_E',-.12,BLUE,'o','C better than E'),('rep_ES',.12,ORANGE,'s','C better than ES')]:
        ax.scatter(cc[col],yy+offset,c=color,marker=marker,s=32,label=lab)
    ax.set(xlim=(-.08,1.08),ylim=(2.6,-.6),xticks=[0,.5,1],yticks=yy,yticklabels=['C-generated','E-generated','ES-generated'],xlabel='Fraction of recombined cohorts\nreproducing accumulation preference')
    ax.legend(loc='center',bbox_to_anchor=(.55,.36))
    ax.text(.5,.03,'1,024 recombinations of the same replicates',transform=ax.transAxes,ha='center',fontsize=6.0)
    label(ax,'D','Cohort-level discrimination')
    b.summary['control_scores']=g[(g.part=='total')&g.model.isin(['E','ES'])].to_dict('records')
    b.save(fig,'figure2','Figure 2 | Control behavior discriminates tested strategies',book)


def figure3(b, book):
    # Loader and design only; their fit functions are never called.
    from scripts.behavior.huk_shadlen_replication import TRIAL_TABLE
    b.record(TRIAL_TABLE)
    u,_,_=design(load_huk())
    pm=(u.groupby(['mouse','coherence_pct','pulse']).right.agg(['mean','size']).reset_index())
    pg=pm.groupby(['coherence_pct','pulse'])['mean'].agg(mean='mean',sem='sem',n_mice='size').reset_index()
    b.export(pm,'fig3_A_psychometric_mouse','Huk-style eligible early/middle schedules, symmetric cells, responses after pulse offset and at least 0.1 s after onset; per-mouse P(right).')
    b.export(pg,'fig3_A_psychometric_group','Unweighted means/SEM over available mice, separately by coherence and physical pulse direction. Descriptive curves, not fitted shifts.')
    dec=b.read(TABLES+'pulse_decomposition_2026-10-30_bins.csv')
    obs=b.read(DYN+'data_readouts.csv')
    boot=b.read(DYN+'data_bootstrap_readouts.csv')
    obs=obs[obs.scope=='all_coherences'].sort_values('bin')
    bb=boot[boot.scope=='all_coherences'].groupby('bin').gammaT.quantile([.025,.975]).unstack().rename(columns={.025:'lo',.975:'hi'})
    gamma=obs.merge(bb,on='bin')
    signed=b.read('dissemination/reviewer_2026-11-12/independent_signed_effects.csv')
    b.export(dec,'fig3_B_directional_shared','Saved joint logistic directional D and shared S coefficients; percentile mouse-bootstrap intervals; Holm over seven bins separately per term.')
    b.export(gamma,'fig3_C_dilution_adjustment','Point estimates and 600-mouse-bootstrap percentile intervals for gamma × mean RT; bins are a descriptive response-conditioned readout.')
    b.export(signed,'fig3_D_assignment_effects','Signed directional response contrast by 5 s; all eligible assignments in symmetric matched cells, not the response-conditioned temporal estimator.')
    fig,axes=plt.subplots(2,2,figsize=(180/25.4,160/25.4),layout='constrained',gridspec_kw={'hspace':.14,'wspace':.08})
    ax=axes[0,0]
    for pulse,col,marker,ls,lab in [(-1,BLUE,'v','--','Left pulse'),(0,'.2','o','-','Control'),(1,ORANGE,'^',':','Right pulse')]:
        z=pg[pg.pulse==pulse].sort_values('coherence_pct')
        ax.errorbar(z.coherence_pct,z['mean'],yerr=z['sem'],color=col,marker=marker,ls=ls,capsize=2,lw=1.1,label=lab)
    ax.axhline(.5,color='.8',lw=.5)
    ax.set(xticks=[-100,-36,0,36,100],ylim=(0,1),xlabel='Signed baseline coherence (%)',ylabel='P(right response)')
    ax.legend(loc='upper left')
    label(ax,'A','Pulse direction shifts choices')
    ax=axes[0,1]
    for kind,col,marker,offset,lab in [('D',PURPLE,'o',-.065,'Directional'),('S',GREEN,'s',.065,'Shared toward correct side')]:
        x=np.arange(len(dec))+offset
        interval(ax,x,dec[kind],dec[kind+'_boot_lo'],dec[kind+'_boot_hi'],color=col,marker=marker,lw=1.1,label=lab)
        for j,row in dec.iterrows():
            if row[kind+'_holm_boot']<.05:
                ax.text(j+offset,row[kind+'_boot_hi']+.045,'*',ha='center',color=col,fontsize=10)
    time_axis(ax,dec); ax.set_ylabel('Pulse coefficient (log-odds)');ax.set_ylim(-.65,.92)
    ax.legend(loc='lower left')
    label(ax,'B','Directional influence persists after the pulse')
    ax=axes[1,0]
    z=gamma[gamma.lo_s>=.3].reset_index(drop=True)
    interval(ax,np.arange(len(z)),z.gammaT,z.lo,z.hi,color='black',marker='o',lw=1.3,label='Observed; mouse-bootstrap 95% CI')
    ax.hlines(float(z.K.iloc[0]),-.2,2.2,color='.5',ls=':',lw=1,label='Early-bin mean')
    time_axis(ax,z); ax.set_ylabel('Coherence-equivalent influence × RT\n(% coherence · s)');ax.legend(loc='lower left')
    label(ax,'C','A later decline remains after dilution adjustment')
    ax=axes[1,1]
    ss=signed.set_index('mouse').loc[MICE]
    y=np.arange(len(ss))
    for i,(mouse,row) in enumerate(ss.iterrows()):
        ax.scatter(row.by_5s_pp,i,c=ORANGE if row.rig=='ucla' else BLUE,marker='o' if row.rig=='ucla' else 's',s=22)
    mean=ss.by_5s_pp.mean(); half=student_t.ppf(.975,len(ss)-1)*ss.by_5s_pp.sem()
    ax.errorbar(mean,len(ss)+.4,xerr=half,fmt='D',c='black',capsize=3,ms=4.5)
    ax.axvline(0,color='.6',lw=.7)
    ax.set(yticks=list(y)+[len(ss)+.4],yticklabels=MICE+['Mean, 95% CI'],ylim=(len(ss)+1.2,-.7),xlabel='Right-pulse minus left-pulse\ndirectional response contrast (pp)')
    label(ax,'D','Assignment effect across mice')
    b.summary['pulse']={'n_temporal_trials':len(u),'n_temporal_mice':u.mouse.nunique(),
       'n_temporal_pulse':int((u.pulse!=0).sum()),'signed_mean_pp':mean,'signed_ci_low':mean-half,'signed_ci_high':mean+half,
       'temporal_bin_counts':dec[['lo_s','hi_s','n_trials','n_pulse']].to_dict('records')}
    b.save(fig,'figure3','Figure 3 | Transient motion has a sustained directional influence',book)


def figure4(b, book):
    reads=b.read(DYN+'all_readouts.csv')
    dec=b.read(TABLES+'pulse_decomposition_2026-10-30_bins.csv')
    obs=reads[(reads.family=='data')&(reads.scope=='all_coherences')].sort_values('bin')
    families=['control_primary','power_leak_urgency','pw_per_time_no_sv']
    curves=reads[(reads.scope=='all_coherences')&reads.family.isin(families+['no_sv'])]
    boot=b.read(DYN+'data_bootstrap_readouts.csv')
    bb=boot[boot.scope=='all_coherences'].groupby('bin').gammaT.quantile([.025,.975]).unstack()
    dif=b.read(TRADE+'difference_by_mouse_seed12345.csv')
    dif=dif[dif.pair=='pw_per_time_no_sv_minus_pw_per_time'].set_index('mouse').loc[MICE]
    q=b.read(TRADE+'difference_by_quantile_seed12345.csv')
    q=q[q.pair=='pw_per_time_no_sv_minus_pw_per_time']
    hist=b.read(TRADE+'rt_histograms_seed12345.csv')
    hist=hist[(hist.mouse=='PSUIM7')&(hist.coherence==-100)&(hist.scheduled_pulse==0)&(hist.correctness=='correct')]
    win=b.read('dissemination/figures/qc/pulse_joint_signatures_2026-11-12_pw_windows.csv')
    data=b.read('dissemination/figures/qc/pulse_effect_bootstrap_2026-11-12_pw_data.csv')
    cohort_data=data[(data.window=='0.3-1.2')&(data.mouse=='mean over mice')].iloc[0]
    data=data[(data.window=='0.3-1.2')&data.mouse.isin(MICE)].set_index('mouse').loc[MICE]
    b.export(curves,'fig4_AB_model_readouts','Pooled model readouts from fixed fitted parameters; each seed pools 30 simulations per input. Individual seeds retained, not parameter uncertainty.')
    b.export(obs,'fig4_AB_observed_readouts','Observed directional and dilution-adjusted readouts; identical estimators are applied to simulated decisions.')
    b.export(win,'fig4_C_individual_predictions','Previously computed individual pulse-minus-control response-conditioned effect, pp; model predictions are fixed-parameter simulations.')
    b.export(data.reset_index(),'fig4_C_individual_intervals','Within-mouse observed trial/bootstrap and block intervals from existing analysis; displayed interval is within-mouse block bootstrap, not animal-population uncertainty.')
    b.export(pd.DataFrame([cohort_data]),'fig4_C_cohort_interval','Observed cohort mean with the existing mouse-plus-trial hierarchical bootstrap interval; distinct from the within-mouse block intervals.')
    b.export(dif.reset_index(),'fig4_D_matched_scores','Matched onset-weight models, without minus with persistent drift variability; positive NLL difference favors variability. Includes controls and pulses.')
    b.export(q,'fig4_E_rt_quantiles','Held-out conditional RT-bin contributions; bins are within coherence × pulse × choice quantiles, not shared physical RT intervals.')
    b.export(hist,'fig4_F_example_rt','Largest matched RT-loss cell selected descriptively: PSUIM7, correct -100% controls. Saved fold histogram counts summed for display.')
    fig,axes=plt.subplots(3,2,figsize=(180/25.4,205/25.4),layout='constrained',gridspec_kw={'hspace':.14,'wspace':.1})
    ax=axes[0,0]
    interval(ax,np.arange(7),dec.D,dec.D_boot_lo,dec.D_boot_hi,color='black',marker='o',lw=1.3,label='Observed')
    ls=['--',':','-.']
    for fam,style in zip(families,ls):
        z=curves[curves.family==fam].groupby('bin').D_joint.mean()
        ax.plot(z.index,z.values,color=COLORS[fam],ls=style,label={'control_primary':'Control-trained','power_leak_urgency':'Power + leak + urgency','pw_per_time_no_sv':'Onset weights, no $s_v$'}[fam],lw=1.2)
    time_axis(ax,obs);ax.set_ylabel('Directional pulse coefficient\n(log-odds)')
    ax.legend(loc='upper right',fontsize=6.0)
    label(ax,'A','Pulse sensitivity tests fitted accounts')
    ax=axes[0,1]
    z=obs[obs.lo_s>=.3].reset_index(drop=True)
    interval(ax,np.arange(len(z)),z.gammaT,bb.loc[z.bin,.025].to_numpy(),bb.loc[z.bin,.975].to_numpy(),color='black',marker='o',lw=1.3,label='Observed')
    for fam,style in [('no_sv','--'),('power_leak_urgency',':'),('pw_per_time_no_sv','-.')]:
        v=curves[(curves.family==fam)&(curves.lo_s>=.3)].groupby('bin').gammaT.mean()
        ax.plot(np.arange(len(v)),v.values,color=COLORS[fam],ls=style,label={'no_sv':'No leak; no drift variability','power_leak_urgency':'Joint power + leak + urgency','pw_per_time_no_sv':'Joint onset weights; no variability'}[fam],lw=1.1)
    time_axis(ax,z);ax.set_ylabel('Coherence-equivalent influence × RT\n(% coherence · s)')
    ax.legend(loc='lower left',fontsize=5.8)
    label(ax,'B','Full trajectories constrain the interpretation')
    ax=axes[1,0]
    y=np.arange(len(MICE))
    ax.hlines(y,data.lo_block,data.hi_block,color='black',lw=.7,alpha=.65)
    ax.scatter(data.effect,y,c='black',s=17,label='Observed; block 95% CI',zorder=4)
    for fam,col,marker,offset,lab in [('pw_per_time',BLUE,'s',-.14,'Onset weights; drift variability'),('pw_per_time_no_sv',GREEN,'^',.14,'Onset weights; no drift variability')]:
        v=win[win.model==fam].set_index('mouse').loc[MICE]
        ax.scatter(v['0.3-1.2'],y+offset,c=col,marker=marker,s=20,label=lab)
        ax.scatter(v['0.3-1.2'].mean(),10.55+offset,c=col,marker=marker,s=23)
    ax.axvline(0,color='.6',lw=.7)
    ax.hlines(10.55,cohort_data.lo_hier,cohort_data.hi_hier,color='black',lw=1.0)
    ax.scatter(cohort_data.effect,10.55,c='black',marker='D',s=22,zorder=4)
    ax.axhline(9.95,color='.85',lw=.6)
    ax.set(yticks=list(y)+[10.55],yticklabels=MICE+['Mean'],ylim=(11.15,-.7),xlabel='Pulse-minus-control effect, 0.3–1.2 s (pp)')
    ax.legend(loc='upper left',bbox_to_anchor=(0,-.24),fontsize=5.8,borderaxespad=0)
    label(ax,'C','Individual pulse effects remain informative')
    ax=axes[1,1]
    ax.barh(y-.16,dif.delta_choice_nll,height=.28,color=BLUE,label='Choice')
    ax.barh(y+.16,dif.delta_rt_nll,height=.28,color=ORANGE,hatch='//',edgecolor='white',lw=.2,label='RT')
    ax.scatter(dif.delta_total,y,c='black',s=12,label='Total',zorder=4)
    ax.axvline(0,c='.6',lw=.7)
    ax.set(yticks=y,yticklabels=MICE,ylim=(9.65,-.7),xlabel='Held-out NLL: no variability − variability')
    ax.legend(loc='upper right',fontsize=6)
    label(ax,'D','The matched score tradeoff varies by mouse')
    ax=axes[2,0]
    ax.bar(q.quantile_bin+1,q.delta_rt_nll,color=np.where(q.delta_rt_nll>=0,ORANGE,BLUE),width=.72)
    ax.axhline(0,c='.6',lw=.7)
    ax.set(xticks=range(1,10),xlabel='Conditional RT quantile bin (fast → slow)',ylabel='RT NLL: no variability − variability')
    label(ax,'E','Central RT bins carry the main cost')
    ax=axes[2,1]
    hc={'pw_per_time':BLUE,'pw_per_time_no_sv':GREEN}
    for fam,col in hc.items():
        v=hist[hist.family==fam].groupby('lo_s')[['data_n','model_n']].sum()
        ax.plot(v.index+.05,v.model_n/v.model_n.sum()/.1,c=col,ls='--' if fam=='pw_per_time' else '-.',label='With variability' if fam=='pw_per_time' else 'Without variability')
    v=hist[hist.family=='pw_per_time'].groupby('lo_s').data_n.sum()
    ax.plot(v.index+.05,v/v.sum()/.1,'o-',c='black',ms=2.7,label='Observed')
    ax.set(xlim=(.3,2.6),xlabel='Response time (s)',ylabel='Conditional density (s⁻¹)')
    ax.legend(loc='upper right',fontsize=6)
    label(ax,'F','Illustrative RT constraint: PSUIM7')
    b.summary['matched_tradeoff']={k:float(dif[k].sum()) for k in ['delta_choice_nll','delta_rt_nll','delta_total']}
    b.summary['matched_tradeoff']['PSUIM7_share']=float(dif.loc['PSUIM7','delta_total']/dif.delta_total.sum())
    b.save(fig,'figure4','Figure 4 | Pulse and response-time predictions impose joint constraints',book)


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args()
    with plt.rc_context(STYLE):
        b=Builder(args.output)
        with PdfPages(b.output/'main_figures.pdf') as book:
            for build in [figure1,figure2,figure3,figure4]:
                build(b,book)
                print(f'Completed {build.__name__}',flush=True)
    b.record(Path(__file__).resolve())
    b.summary['base_commit']=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()
    b.summary['source_hashes']=b.sources
    b.summary['panels']=b.panels
    b.summary['figures']=b.figures
    b.summary['scope']='Figure assembly from existing results, descriptive psychometric fits and control mean RT aggregation; no decision-model fits or new simulations.'
    b.summary['format']='Provisional research-article layout; exact current Neuron requirements remain unverified (official page inaccessible).'
    (b.output/'figure_manifest.json').write_text(json.dumps(b.summary,indent=2)+'\n')
    print(json.dumps({'output':str(b.output),'figures':len(b.figures),'source_tables':len(b.panels),'population':b.summary['population']},indent=2))

if __name__=='__main__':
    main()
