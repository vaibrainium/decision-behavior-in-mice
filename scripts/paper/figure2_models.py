"""Draw Figure 2 model schematics and implementation table; no fitted predictions.

Uses the C/E/ES update rules on one deliberately constructed increment sequence.
The illustrative thresholds and time constants are exported, not fit to behavior.
"""
import argparse
import hashlib
import json
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scripts.paper.style import RC, RIGHT_COLOR, LEFT_COLOR


def main():
    parser = argparse.ArgumentParser(__doc__)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=False)
    dt, leak, n = .001, 50., 500
    k = np.arange(n)
    # Constructed samples, not recorded evidence, diffusion draws or model fits.
    mean_increment = np.where((k < 140) | (k >= 260), .005, 0.)
    samples = mean_increment + np.random.default_rng(7).normal(0., .012, n)
    samples[400] = .105
    time = (k+1)*dt
    accumulation = np.cumsum(samples)
    recent = np.zeros(n)
    for i in range(n):
        recent[i] = (1-leak*dt)*(recent[i-1] if i else 0) + samples[i]
    # Independent convolution check of the rapid-forgetting recurrence.
    np.testing.assert_allclose(recent, np.convolve(samples,(1-leak*dt)**k)[:n], atol=1e-12)
    models = [
        ('C', 'Accumulation', accumulation, .85, 'Sum successive samples'),
        ('E', 'Rapid forgetting', recent, .15, 'Retain recent evidence;\nolder evidence decays'),
        ('ES', 'Extrema detection', samples, .08, 'Test each sample;\nno sum across samples'),
    ]
    implementations = {
        'C': ('C / DDMx', 'C: motion-energy input\nDrift variability + fast guesses\nDDMx: nominal-coherence input\nNo drift variability or fast guesses'),
        'E': ('E', 'E: C with rapid leakage\nSame sensory and response components'),
        'ES': ('ES / ESx', 'ES: motion-energy input\nDrift variability + fast guesses\nESx: nominal-coherence input\nNo drift variability or fast guesses'),
    }
    coordinates = pd.DataFrame({'time_s':time,'illustrative_increment':samples,'constructed_mean_increment':mean_increment})
    settings = {'scope':'Illustrative decision-stage dynamics only; not data or fitted predictions.',
                'construction':{'seed':7,'noise_sd':.012,'mean_increment':.005,'zero_mean_indices':[140,260],'deliberate_extreme_index':400,'deliberate_extreme_value':.105},
                'dt_s':dt,'leak_per_s':leak,'tau_s':1/leak,
                'starting_state_centered':0,'thresholds':{},'first_crossing_indices':{},
                'inspiration':{'doi':'10.7554/eLife.55365','figure':'1',
                               'url':'https://elifesciences.org/articles/55365/figures'},
                'differences_from_reference':'C, E and ES are the locally tested matched candidates; no snapshot candidate is depicted.',
                'normalization':'Each decision signal is divided by its own illustrative threshold. Thresholds are not equated across models.',
                'omitted_shared_components':'Sensory representation, across-trial drift variation, fast guesses, nondecision time and minimum-RT floor are not drawn.',
                'checks':{'rapid_forgetting_matches_convolution':True,'C_matches_cumulative_sum':True,'ES_tests_single_samples':True}}
    settings['implementation_labels'] = {key: {'models': pair[0], 'description': pair[1]} for key, pair in implementations.items()}
    settings['scope'] += ' Three decision rules introduce five tested implementations; shared example increments do not imply identical fitted sensory inputs.'
    comparison = pd.DataFrame([
        ['C','Accumulation','Motion energy','Yes','Yes'],
        ['E','Rapid forgetting','Motion energy','Yes','Yes'],
        ['ES','Extrema detection','Motion energy','Yes','Yes'],
        ['DDMx','Accumulation','Nominal coherence','No','No'],
        ['ESx','Extrema detection','Nominal coherence','No','No'],
    ], columns=['Model','Decision rule','Input','Drift variability','Fast guesses'])
    with plt.rc_context({**RC, 'font.family':'DejaVu Sans'}):
        fig = plt.figure(figsize=(180/25.4,138/25.4))
        grid = fig.add_gridspec(2,3,left=.10,right=.985,bottom=.44,top=.80,
                               height_ratios=[.7,2.1],hspace=.35,wspace=.38)
        fig.text(.025,.98,'Figure 2 | Candidate decision models',fontsize=10,va='top')
        fig.text(.025,.90,'A',fontsize=12,fontweight='bold',va='top')
        for j,(key,title,signal,threshold,description) in enumerate(models):
            hit = int(np.flatnonzero(np.abs(signal)>=threshold)[0])
            assert np.all(np.abs(signal[:hit]) < threshold)
            settings['thresholds'][key] = threshold
            settings['first_crossing_indices'][key] = hit
            coordinates[key+'_signal'] = signal
            coordinates[key+'_displayed'] = k <= hit
            top = fig.add_subplot(grid[0,j])
            top.plot(time,samples,c='.55',lw=.55)
            top.axhline(0,c='.8',lw=.45)
            top.set(xlim=(0,.5),ylim=(-.045,.17),xticks=[],yticks=[])
            top.spines[['top','right','left','bottom']].set_visible(False)
            top.set_title(f'{title}\n{implementations[key][0]}',fontsize=8.2,pad=15)
            if j == 0:
                top.set_ylabel('Momentary\nevidence',fontsize=7,labelpad=5)
            ax = fig.add_subplot(grid[1,j])
            ax.axhline(1,c=RIGHT_COLOR,lw=.8,ls='--',alpha=.8)
            ax.axhline(-1,c=LEFT_COLOR,lw=.8,ls='--',alpha=.8)
            ax.axhline(0,c='.8',lw=.5)
            if key == 'ES':
                # Discrete marks only: no line connecting successive samples.
                ax.vlines(time[:hit+1],0,signal[:hit+1]/threshold,color='.65',lw=.35)
                ax.scatter(time[:hit+1],signal[:hit+1]/threshold,c='.25',s=1.3,linewidths=0)
            else:
                ax.plot(np.r_[0,time[:hit+1]],np.r_[0,signal[:hit+1]/threshold],c='.15',lw=1)
            ax.plot(time[hit],signal[hit]/threshold,'o',c=RIGHT_COLOR,ms=4)
            ax.set(xlim=(0,.5),ylim=(-1.4,1.4),xticks=[],yticks=[-1,0,1],yticklabels=['−1','0','+1'],xlabel='Time')
            ax.tick_params(axis='y',length=2)
            ax.text(.02,.96,'Right bound',transform=ax.transAxes,fontsize=6,color=RIGHT_COLOR,va='top')
            ax.text(.02,.04,'Left bound',transform=ax.transAxes,fontsize=6,color=LEFT_COLOR,va='bottom')
            if j == 0:
                ax.set_ylabel('Decision signal\n(relative to bound)',fontsize=7)
            center = (ax.get_position().x0+ax.get_position().x1)/2
            fig.text(center,.375,description,
                     fontsize=7,ha='center',va='center')
        fig.text(.025,.305,'B',fontsize=12,fontweight='bold',va='top')
        fig.text(.10,.305,'Model implementations',fontsize=8.2,va='top')
        table_ax = fig.add_axes([.10,.075,.885,.205])
        table_ax.set_axis_off()
        table = table_ax.table(cellText=comparison.values,
                              colLabels=['Model','Decision rule','Input','Across-trial\ndrift variability','Fast guesses'],
                              colWidths=[.09,.24,.27,.24,.16],
                              cellLoc='left',colLoc='left',bbox=[0,0,1,1])
        table.auto_set_font_size(False)
        table.set_fontsize(6.8)
        for (row,col),cell in table.get_celld().items():
            cell.visible_edges = 'B'
            cell.set_edgecolor('.8')
            cell.set_linewidth(.4)
            if row == 0:
                cell.set_text_props(weight='medium')
        fig.text(.10,.025,'Illustrative trajectories; scales normalized separately. Orange dots mark the first bound crossing.',fontsize=6.2,c='.35')
        for suffix in ['pdf','svg','png']:
            fig.savefig(args.output/f'figure2.{suffix}',dpi=300,facecolor='white')
        plt.close(fig)
    coordinates.to_csv(args.output/'schematic_coordinates.csv',index=False)
    comparison.to_csv(args.output/'model_comparison.csv',index=False)
    for source in [Path(__file__),Path('src/ddm/simulator.py'),Path('scripts/ddm/primacy.py')]:
        settings.setdefault('source_hashes',{})[str(source)] = hashlib.sha256(source.read_bytes()).hexdigest()
    (args.output/'schematic_manifest.json').write_text(json.dumps(settings,indent=2)+'\n')
    print(args.output/'figure2.png')


if __name__ == '__main__':
    main()
