"""Compose joint-test-bits and delta-BIC previews from exported metric tables."""
import argparse
import json
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator
import numpy as np
import pandas as pd
from scripts.paper.style import RC


def main():
    p=argparse.ArgumentParser(__doc__)
    p.add_argument('--input',type=Path,required=True)
    p.add_argument('--output',type=Path,required=True)
    a=p.parse_args();a.output.mkdir(parents=True,exist_ok=False)
    models=['C','E','ES','DDMx','ESx']
    g=pd.read_csv(a.input/'group_metrics.csv',index_col='model').loc[models]
    specs=[('B','Joint test likelihood', 'joint_test_logscore_bits_per_trial','Test choice + RT log score\n(bits/trial)','Higher is better'),
           ('C','Complexity-adjusted fit','delta_bic_vs_C','Mean ΔBIC relative to C','Lower is better')]
    with plt.rc_context({**RC,'font.family':'DejaVu Sans'}):
        fig,axs=plt.subplots(1,2,figsize=(180/25.4,85/25.4))
        fig.subplots_adjust(left=.10,right=.98,bottom=.18,top=.74,wspace=.50)
        for ax,(letter,title,key,ylabel,direction) in zip(axs,specs):
            y=g[key].to_numpy();pad=max(float(np.ptp(y))*.30,.001)
            ax.plot(range(5),y,'o-',color='.2',lw=1,ms=5.5)
            for j,v in enumerate(y):
                label=f'{v:.3f}' if 'bits' in ylabel else f'{v:.1f}'
                ax.text(j,v+pad*.2,label,ha='center',fontsize=6.2)
            ax.set(xticks=range(5),xticklabels=models,xlabel='Model',ylabel=ylabel,
                   xlim=(-.45,4.45),ylim=(y.min()-pad,y.max()+pad))
            ax.yaxis.set_major_locator(MaxNLocator(nbins=4));ax.ticklabel_format(axis='y',useOffset=False,style='plain')
            if 'BIC' in key.lower() or key=='delta_bic_vs_C': ax.axhline(0,c='.75',lw=.6,ls=':')
            box=ax.get_position();fig.text(box.x0-.07,.97,letter,fontsize=12,fontweight='bold',va='top')
            fig.text(box.x0,.97,title,fontsize=8.2,va='top')
            fig.text(box.x0,.85,'Mean across 10 mice; '+direction.lower(),fontsize=6.4,c='.3')
        for ext in ['pdf','svg','png']: fig.savefig(a.output/f'bits_and_delta_bic.{ext}',dpi=300,facecolor='white')
        plt.close(fig)
    (a.output/'source_group_metrics.csv').write_text((a.input/'group_metrics.csv').read_text())
    (a.output/'composition.json').write_text(json.dumps({'source':str(a.input),'panels':['joint_test_logscore_bits_per_trial','delta_bic_vs_C'],'scope':'Rendering only; no new analysis.'},indent=2)+'\n')
    print(a.output/'bits_and_delta_bic.png')


if __name__=='__main__': main()
