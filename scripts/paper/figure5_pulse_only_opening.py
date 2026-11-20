"""Opening Figure 5 preview from existing pulse-only fitted candidates; no refits."""
import argparse,hashlib,json,subprocess
from pathlib import Path
import numpy as np
import pandas as pd
from matplotlib.patches import FancyBboxPatch
from matplotlib.ticker import StrMethodFormatter,MaxNLocator
from scripts.paper.build_paper_2026_11_15 import plt,STYLE,BLUE,ORANGE

SOURCE=Path('dissemination/figures/qc/model_ic_summary_2026-11-12_rescored.csv')


def readable(family):
    _,mapping,variant=family.split('_',2)
    no_sv=variant.endswith('_no_sv') or variant=='no_sv'
    variant=variant.removesuffix('_no_sv')
    names={'primary':'Integrator','no_sv':'Integrator','leak':'Leak','urgency':'Urgency','leak_urgency':'Leak + urgency','ugm':'UGM region'}
    return {'linear':'Linear','power':'Power','norm':'Normalized'}[mapping]+' · '+names[variant]+(' · no sᵥ' if no_sv else ' · sᵥ')


def schematic(ax):
    ax.set_axis_off();ax.set(xlim=(0,1),ylim=(0,1))
    boxes=[(.02,.18,'Pulse-trial input','Motion evidence\nover time'),(.265,.21,'Input mapping','Linear\nPower law\nNormalization'),(.54,.23,'Accumulation dynamics','Integrator / leak\nUrgency / leak + urgency\nUrgency-gating region'),(.825,.15,'Predictions','Choice\nand RT')]
    for x,width,title,body in boxes:
        ax.add_patch(FancyBboxPatch((x,.35),width,.48,boxstyle='round,pad=.01',fc='#f3f5f7',ec='.55',lw=.7))
        ax.text(x+width/2,.73,title,ha='center',va='center',fontsize=7.3,fontweight='bold')
        ax.text(x+width/2,.52,body,ha='center',va='center',fontsize=6.8,linespacing=1.5)
    for x1,x2 in [(.20,.265),(.475,.54),(.77,.825)]:
        ax.annotate('',xy=(x2-.015,.59),xytext=(x1+.01,.59),arrowprops={'arrowstyle':'->','lw':.8,'color':'.4'})
    ax.text(.655,.17,'Across-trial drift variability sᵥ: fitted or fixed to zero',ha='center',fontsize=7)
    ax.text(.02,.03,'22 fitted combinations; model coverage differs across input mappings.',fontsize=6.5,color='.3')
    ax.text(.0,1.03,'A',fontsize=11,fontweight='bold',transform=ax.transAxes)
    ax.set_title('Accumulation models fitted to pulse trials',loc='left',fontsize=9,pad=12)


def scores(fig,frame,positions):
    y=np.arange(len(frame));axes=[]
    for metric,title,pos in zip(['heldout','bic'],['Held-out NLL','BIC'],positions):
        ax=fig.add_axes(pos);axes.append(ax)
        ax.scatter(frame[metric],y,c='.55',s=14,zorder=3)
        idx=int(np.argmin(frame[metric].to_numpy()));color=BLUE if metric=='heldout' else ORANGE
        ax.scatter(frame[metric].iloc[idx],idx,c=color,s=35,zorder=4)
        ax.set(ylim=(len(frame)-.5,-.5),yticks=y,xlabel=title+' (lower is better)')
        ax.set_yticklabels(frame.display_label if metric=='heldout' else ['']*len(frame),fontsize=6.4)
        ax.tick_params(axis='y',length=0,pad=7);ax.xaxis.set_major_formatter(StrMethodFormatter('{x:,.0f}'))
        ax.xaxis.set_major_locator(MaxNLocator(3));ax.tick_params(axis='x',labelsize=6.3);ax.set_title(title,loc='left',fontsize=8,pad=8)
        ax.margins(x=.15)
        for k in y:ax.axhline(k,color='.94',lw=.4,zorder=0)
    axes[0].text(-1.38,1.06,'B',transform=axes[0].transAxes,fontweight='bold',fontsize=11)
    return axes


def save(fig,stem):
    for ext in ['png','pdf','svg']:fig.savefig(stem.with_suffix('.'+ext),dpi=300)
    plt.close(fig)


def main():
    p=argparse.ArgumentParser(__doc__);p.add_argument('--output',type=Path,required=True);a=p.parse_args();out=a.output;out.mkdir(parents=True,exist_ok=False)
    all_rows=pd.read_csv(SOURCE);frame=all_rows[all_rows.kind=='pulse_only'].sort_values('heldout').reset_index(drop=True).copy()
    assert len(frame)==22 and frame.n.nunique()==1 and frame.heldout.notna().all() and frame.bic.notna().all()
    frame['display_label']=frame.family.map(readable);assert frame.display_label.nunique()==22
    ll=frame.loc[frame.heldout.idxmin()];bic=frame.loc[frame.bic.idxmin()]
    assert ll.family=='pulse_norm_ugm_no_sv' and bic.family=='pulse_linear_leak'
    frame.to_csv(out/'pulse_only_candidates.csv',index=False)
    with plt.rc_context(STYLE):
        fig=plt.figure(figsize=(220/25.4,205/25.4));ax=fig.add_axes([.035,.72,.93,.20]);schematic(ax)
        scores(fig,frame,[[.405,.14,.235,.50],[.735,.14,.235,.50]])
        fig.text(.035,.975,'Figure 5 opening | Pulse-only accumulation fits',fontsize=10,va='top')
        fig.text(.035,.66,'Pulse-only candidate comparison',fontsize=8.5)
        fig.text(.035,.075,'Best predictive score: normalized UGM region, no sᵥ',color=BLUE,fontsize=7)
        fig.text(.035,.045,'Lowest BIC: linear leaky accumulator, with sᵥ',color=ORANGE,fontsize=7)
        fig.text(.035,.018,'All 22 pulse-only candidates shown; scores summed across 10 mice. No new fits.',fontsize=6.5,color='.3')
        save(fig,out/'figure5_opening')
        detail=plt.figure(figsize=(220/25.4,60/25.4));ax=detail.add_axes([.035,.13,.93,.70]);schematic(ax);save(detail,out/'figure5A_models')
    (out/'caption.md').write_text('''Figure 5 opening preview. (A) Components varied across the existing pulse-only accumulation fits: input mapping (linear, power law or normalization), accumulator dynamics (integration, leak, urgency, leak plus urgency, or a restricted urgency-gating region), and presence or absence of persistent across-trial drift variability. This diagram is a conceptual summary, not a fully crossed design or simulated trajectory. All candidates were fitted to pulse trials; control-only and joint-fit candidates are excluded. (B) Existing held-out NLL and independently rescored full-fit BIC for all 22 pulse-only candidates, ranked by held-out NLL in both columns. Scores are summed over 10 individually fitted mice; the common modeled population contains 11,479 pulse trials. Held-out scores sum five test folds per mouse; BIC is a distinct full-fit criterion using the original free-parameter counts and independent training rescoring. Blue marks the lowest held-out score; orange marks the lowest BIC. Other candidates are gray. Points are descriptive cohort totals, without inferential error bars or a new group significance test. The predictive winner is normalized input in the urgency-gating region without drift variability; BIC instead favors the linear-input leaky accumulator with drift variability. Unequal candidate coverage limits attribution of the difference to any one component. No new fitting or scoring was performed.\n''')
    (out/'manifest.json').write_text(json.dumps({'base_commit':subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),'source':str(SOURCE),'sha256':hashlib.sha256(SOURCE.read_bytes()).hexdigest(),'code_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'n_candidates':len(frame),'n_trials':int(frame.n.iloc[0]),'predictive_winner':ll.family,'bic_winner':bic.family,'scope':'Author-review opening preview; pulse-only models; no refits.'},indent=2)+'\n')
    print('22 pulse-only candidates exported; distinct predictive/BIC winners verified.')

if __name__=='__main__':main()
