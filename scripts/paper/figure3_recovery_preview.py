"""Show existing Figure 3 recovery panels C/D without the superseded A/B."""
import argparse
import hashlib
import json
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scripts.paper.style import RC


def main():
    p=argparse.ArgumentParser(__doc__);p.add_argument('--input',type=Path,required=True);p.add_argument('--output',type=Path,required=True)
    p.add_argument('--only-c',action='store_true')
    a=p.parse_args();a.output.mkdir(parents=True,exist_ok=False)
    cpath=a.input/'source_data/fig3_C_recovery.csv';dpath=a.input/'source_data/fig3_D_recombined_cohorts.csv'
    order=['C','E','ES','DDMx','ESx'];c=pd.read_csv(cpath).set_index('generator').loc[order,order]
    np.testing.assert_array_equal(c.sum(axis=1),np.full(5,20))
    d=pd.read_csv(dpath).set_index('generator').loc[['C','E','ES']]
    with plt.rc_context({**RC,'font.family':'DejaVu Sans'}):
        fig,axes=plt.subplots(1,2,figsize=(180/25.4,90/25.4))
        fig.subplots_adjust(left=.10,right=.98,bottom=.23,top=.77,wspace=.65)
        ax=axes[0];im=ax.imshow(c.to_numpy()/20,vmin=0,vmax=1,cmap='Blues',aspect='equal')
        for i in range(5):
            for j in range(5):
                n=int(c.iloc[i,j]);ax.text(j,i,str(n),ha='center',va='center',color='white' if n>=12 else 'black',fontsize=8)
        ax.set(xticks=range(5),xticklabels=order,yticks=range(5),yticklabels=order,xlabel='Best-scoring candidate',ylabel='Generating model')
        fig.colorbar(im,ax=ax,shrink=.8,pad=.03).set_label('Fraction of 20 dataset pairs',fontsize=6.5)
        ax.set_title('C   Model recovery',fontsize=9,pad=14,loc='left')
        ax=axes[1];yy=np.arange(3)
        for key,offset,color,marker,label in [('rep_E',-.12,'#0072B2','o','C better than E'),('rep_ES',.12,'#D55E00','s','C better than ES')]:
            ax.scatter(d[key],yy+offset,c=color,marker=marker,s=26,label=label)
        ax.set(xlim=(-.08,1.08),ylim=(2.6,-.6),xticks=[0,.5,1],yticks=yy,yticklabels=['C-generated','E-generated','ES-generated'],xlabel='Fraction of recombined cohorts\nreproducing accumulation preference')
        ax.legend(frameon=False,fontsize=6,loc='center',bbox_to_anchor=(.52,.40))
        ax.set_title('D   Cohort-level recovery',fontsize=9,pad=14,loc='left')
        ax.text(.5,-.36,'1,024 recombinations of the same replicates',transform=ax.transAxes,ha='center',fontsize=5.7,color='.3')
        fig.text(.10,.94,'Existing recovery results; panels awaiting author review',fontsize=8,color='.3')
        if a.only_c:
            # Export the approved matrix alone without changing its values or labeling.
            axes[1].remove()
            fig.set_size_inches(95/25.4,90/25.4)
            axes[0].set_position([.19,.23,.59,.58])
            fig.axes[-1].set_position([.80,.27,.03,.48])
            fig.texts[0].set_text('Approved Figure 3C — model recovery')
            fig.texts[0].set_position((.10,.94))
        for ext in ['png','pdf','svg']:fig.savefig(a.output/f'figure3_CD.{ext}',dpi=300,facecolor='white')
        plt.close(fig)
    for path in [cpath,dpath]:(a.output/path.name).write_bytes(path.read_bytes())
    (a.output/'manifest.json').write_text(json.dumps({'scope':'Existing recovery results rendered without superseded A/B; no new analysis',
        'source_hashes':{str(path.resolve()):hashlib.sha256(path.read_bytes()).hexdigest() for path in [cpath,dpath]},
        'script_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'status':('C approved; D result text only' if a.only_c else 'Historical C/D preview'), 'only_c':a.only_c},indent=2)+'\n')


if __name__=='__main__':main()
