"""Export existing pulse-influence results as provisional Figure 4 for review."""
import argparse
import json
import logging
import numpy as np
import pandas as pd
from src.utils.pmf_utils import fit_psychometric_function
from pathlib import Path
from matplotlib.backends.backend_pdf import PdfPages
from scripts.paper.build_paper_2026_11_15 import Builder,STYLE,figure3,plt


class PulseBuilder(Builder):
    def export(self,frame,name,detail):
        if getattr(self,'paired_psychometric',False):
            for old,new in [('fig3_B_','fig4_C_'),('fig3_C_','fig4_D_'),('fig3_D_','fig4_E_')]:
                if name.startswith(old):name=name.replace(old,new,1);break
        return super().export(frame,name.replace('fig3_','fig4_',1),detail)

    def save(self,fig,name,title,book):
        if getattr(self,'fit_pulse_psychometric',False):
            self.revise_psychometric(fig.axes[0])
        if getattr(self,'paired_psychometric',False):
            self.add_paired_psychometric(fig)
        return super().save(fig,'figure4','Figure 4 | Brief motion pulses influence subsequent choices',book)


    def revise_psychometric(self,ax):
        # All original B–D artists and source tables remain untouched.
        group=pd.read_csv(self.output/'source_data/fig4_A_psychometric_group.csv')
        ax.clear();coefficients=[];curves=[]
        for direction,color,marker,label in [(-1,'#0072B2','v','Left pulse'),(1,'#D55E00','^','Right pulse')]:
            z=group[group.pulse==direction].sort_values('coherence_pct')
            fit=fit_psychometric_function(z.coherence_pct.to_numpy(),z['mean'].to_numpy(),None,'logit_4')
            grid=(np.linspace(-100,100,401) if getattr(self,'extend_pulse_curves',False) else np.linspace(z.coherence_pct.min(),z.coherence_pct.max(),401))
            pred=fit.predict(grid)
            assert np.isfinite(pred).all() and ((pred>=0)&(pred<=1)).all()
            ax.errorbar(z.coherence_pct,z['mean'],yerr=z['sem'],fmt=marker,ls='none',color=color,
                        capsize=2,label=label,ms=3.7)
            ax.plot(grid,pred,'-',c=color,lw=1.2)
            coefficients.append({'pulse':direction,'weighting':'unweighted least squares on equal-mouse means',
                                 'coherence_min':float(grid.min()),'coherence_max':float(grid.max()),**fit.coefs_})
            curves.extend({'pulse':direction,'coherence_pct':float(x),'p_right':float(y)} for x,y in zip(grid,pred))
        self.export(group[group.pulse.isin([-1,1])].copy(),'fig4_A_displayed_pulse_points',
                    'Only physical left/right pulse groups displayed; group data and SEM unchanged. Control retained in original source table, excluded from panel A.')
        self.export(pd.DataFrame(coefficients),'fig4_A_psychometric_parameters',
                    'Author logit_4 helper/default bounds, unweighted fit across equal-mouse group proportions, separately by pulse direction.')
        self.export(pd.DataFrame(curves),'fig4_A_psychometric_curves',
                    ('Smooth descriptive four-parameter logistic over −100 to100% at author request, including extrapolation beyond each direction’s observed range.' if getattr(self,'extend_pulse_curves',False) else 'Smooth descriptive four-parameter logistic restricted to each direction’s observed range.'))
        ax.axhline(.5,color='.8',lw=.5)
        ax.set(xlim=(-110,110),xticks=[-100,-36,0,36,100],ylim=(0,1),xlabel='Signed baseline coherence (%)',ylabel='P(right response)')
        ax.legend(loc='upper left')
        from scripts.paper.build_paper_2026_11_15 import label
        label(ax,'A','Pulse direction shifts choices')


    def add_paired_psychometric(self,fig):
        from scripts.paper.pulse_paired_psychometrics import paired_parameters,draw_paired
        table=pd.read_csv(self.output/'source_data/fig4_A_psychometric_mouse.csv')
        params,differences,tests,sensitivity,curves=paired_parameters(table,multistart=getattr(self,'multistart_paired',False))
        for name,frame,description in [
            ('parameters',params,'Individual author logit_4 fits, trial-count WLS, all20 fits retained; native mean=alpha, var=beta. Fit quality/bound flags exported.'),
            ('differences',differences,'Right-minus-left paired mouse coefficients,10 mice.'),
            ('tests',tests,'Exploratory exact two-sided sign-flip tests of mean fitted parameter differences; Holm over alpha and beta. Paired-t sensitivity corrected separately; t CIs conditional on fitted coefficients.'),
            ('shared_asymptote_sensitivity',sensitivity,'Sensitivity only: asymptotes from each mouse control curve fixed for pulse pair; alpha/beta fitted. Not used to choose significance or replace primary fits.'),
            ('individual_curves',curves,'Per-mouse descriptive four-parameter fitted pulse curves for fit audit.')]:
            self.export(frame,'fig4_B_paired_'+name,description)
        original=list(fig.axes)
        fig.set_layout_engine(None);fig.set_size_inches(250/25.4,165/25.4)
        positions=[(.075,.59,.24,.27),(.075,.16,.24,.27),(.405,.16,.24,.27),(.735,.16,.24,.27)]
        for ax,position in zip(original,positions):ax.set_position(position)
        for ax,old,new,title in zip(original[1:],['B','C','D'],['C','D','E'],
                                  ['Directional and shared influence','Dilution-adjusted pulse influence','Pulse effect across mice']):
            for text in ax.texts:
                if text.get_text()==old:text.set_text(new)
            ax.set_title(title,loc='left',pad=7)
        aa=fig.add_axes([.435,.59,.18,.27]);bb=fig.add_axes([.755,.59,.18,.27])
        draw_paired([aa,bb],params,tests)
        aa.text(-.15,1.17,'B',transform=aa.transAxes,fontsize=10,fontweight='bold')
        fig.text(.435,.94,'Paired pulse psychometric parameters',fontsize=8.5)
        fig.text(.435,.49,'Each line: one mouse. Exploratory; weakly constrained fits retained.',fontsize=6,color='.3')
        # A focused preview of the added panel; no additional estimation.
        with plt.rc_context(STYLE):
            detail,axes=plt.subplots(1,2,figsize=(125/25.4,88/25.4))
            detail.subplots_adjust(left=.14,right=.97,bottom=.20,top=.72,wspace=.50)
            draw_paired(axes,params,tests)
            detail.text(.04,.97,'B  Paired pulse psychometric parameters',fontsize=9,va='top')
            detail.text(.14,.86,'10 mice; lines connect the same mouse',fontsize=7,color='.3')
            detail.text(.14,.04,'Unrestricted fits; some parameters are weakly constrained.',fontsize=6,color='.3')
            for ext in ['png','pdf','svg']:detail.savefig(self.output/f'paired_psychometric_panel.{ext}',dpi=300,facecolor='white')
            plt.close(detail)


def main():
    p=argparse.ArgumentParser(__doc__);p.add_argument('--output',type=Path,required=True);p.add_argument('--fit-pulse-psychometric',action='store_true');p.add_argument('--extend-pulse-curves',action='store_true');p.add_argument('--paired-psychometric',action='store_true');p.add_argument('--multistart-paired',action='store_true');a=p.parse_args()
    logging.getLogger('fontTools').setLevel(logging.WARNING)
    with plt.rc_context(STYLE):
        builder=PulseBuilder(a.output)
        builder.fit_pulse_psychometric=a.fit_pulse_psychometric
        builder.extend_pulse_curves=a.extend_pulse_curves
        builder.paired_psychometric=a.paired_psychometric
        builder.multistart_paired=a.multistart_paired
        with PdfPages(a.output/'figure4_review.pdf') as book:figure3(builder,book)
    for source in [Path(__file__),Path('scripts/paper/build_paper_2026_11_15.py'),Path('src/utils/pmf_utils.py'),Path('scripts/paper/pulse_paired_psychometrics.py')]:builder.record(source.resolve())
    builder.summary.update(source_hashes=builder.sources,panels=builder.panels,figures=builder.figures,
        paired_psychometric=a.paired_psychometric,multistart_paired=a.multistart_paired,scope=('Panel A shows left/right pulse points and descriptive author logit_4 fits; control hidden. B–D unchanged; no decision-model fits or simulations.' if a.fit_pulse_psychometric else 'Existing pulse influence results exported for Figure 4 panel review; no new fits/simulations/analysis; global old manuscript numbering retained pending assembly.'))
    (a.output/'figure_manifest.json').write_text(json.dumps(builder.summary,indent=2)+'\n')


if __name__=='__main__':main()
