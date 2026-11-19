"""Per-mouse paired pulse psychometric coefficients with fit-quality audit."""
import itertools
import warnings
import numpy as np
import pandas as pd
from scipy.optimize import least_squares
from scipy.special import expit
from scipy import stats
from src.utils.pmf_utils import fit_psychometric_function


def paired_parameters(mouse_table,multistart=False):
    rows=[];shared=[];curves=[]
    for mouse,g in mouse_table.groupby('mouse'):
        c=g[g.pulse==0]
        control=fit_psychometric_function(c.coherence_pct.to_numpy(),c['mean'].to_numpy(),c['size'].to_numpy(),'logit_4')
        gamma=control.coefs_['lapse_rate'];lam=control.coefs_['guess_rate']
        for pulse in [-1,1]:
            z=g[g.pulse==pulse].sort_values('coherence_pct')
            with warnings.catch_warnings(record=True) as caught:
                warnings.simplefilter('always')
                fit=fit_psychometric_function(z.coherence_pct.to_numpy(),z['mean'].to_numpy(),z['size'].to_numpy(),'logit_4')
            co=dict(fit.coefs_);native_co=dict(co)
            xx=z.coherence_pct.to_numpy();yy=z['mean'].to_numpy();weight=np.sqrt(z['size'].to_numpy())
            native_sse=float(np.sum(weight**2*(fit.predict(xx)-yy)**2))
            best_condition=float(np.linalg.cond(fit.covar_));n_starts=1
            if multistart:
                def residual4(q):return weight*(q[2]+(1-q[2]-q[3])*expit(q[1]*(xx-q[0]))-yy)
                bounds=([-100,1e-5,1e-5,1e-5],[100,30,.4,.4])
                starts=[[co['mean'],co['var'],co['lapse_rate'],co['guess_rate']]]+[[m,b,l,u] for m,b,(l,u) in itertools.product([-40,0,40],[.015,.05,.15],[(.05,.05),(.25,.15)])]
                solved=[least_squares(residual4,np.clip(seed,*bounds),bounds=bounds,max_nfev=3000,ftol=1e-10,xtol=1e-10,gtol=1e-10) for seed in starts]
                best=min(solved,key=lambda r:np.sum(r.fun**2));assert np.sum(best.fun**2)<=native_sse+1e-8
                co=dict(zip(['mean','var','lapse_rate','guess_rate'],map(float,best.x)))
                best_condition=float(np.linalg.cond(best.jac.T@best.jac));n_starts=len(starts)
            pred=co['lapse_rate']+(1-co['guess_rate']-co['lapse_rate'])*expit(co['var']*(xx-co['mean']))
            rows.append({'mouse':mouse,'pulse':pulse,'alpha':co['mean'],'beta':co['var'],
                'lower_asymptote':co['lapse_rate'],'upper_asymptote':1-co['guess_rate'],
                'n_trials':int(z['size'].sum()),'n_coherence_levels':len(z),
                'weighted_sse':float(np.sum(z['size']*(pred-z['mean'])**2)),
                'initial_helper_covariance_condition_number':float(np.linalg.cond(fit.covar_)),
                'selected_fit_condition_number':best_condition,'n_starts':n_starts,
                'initial_helper_alpha':native_co['mean'],'initial_helper_beta':native_co['var'],'initial_helper_sse':native_sse,
                'beta_at_lower_bound':bool(np.isclose(co['var'],1e-5,rtol=1e-3,atol=1e-9)),
                'any_asymptote_parameter_at_bound':bool(any(np.isclose(co[k],bound,atol=1e-6) for k in ['lapse_rate','guess_rate'] for bound in [1e-5,.4])),
                'fit_warning':'; '.join(str(w.message) for w in caught)})
            grid=np.linspace(-100,100,401)
            curves.extend({'mouse':mouse,'pulse':pulse,'coherence_pct':float(x),'p_right':float(y)} for x,y in zip(grid,co['lapse_rate']+(1-co['guess_rate']-co['lapse_rate'])*expit(co['var']*(grid-co['mean']))))
            # Sensitivity only: common control-derived asymptotes, all mice retained.
            xx=z.coherence_pct.to_numpy();yy=z['mean'].to_numpy();weight=np.sqrt(z['size'].to_numpy())
            def residual(q):return weight*(gamma+(1-gamma-lam)*expit(q[1]*(xx-q[0]))-yy)
            runs=[least_squares(residual,[m,b],bounds=([-100,1e-5],[100,30]),max_nfev=2000)
                  for m,b in itertools.product([-25,0,25],[.02,.05,.1])]
            best=min(runs,key=lambda q:np.sum(q.fun**2))
            shared.append({'mouse':mouse,'pulse':pulse,'alpha':float(best.x[0]),'beta':float(best.x[1]),
                'lower_asymptote':gamma,'upper_asymptote':1-lam,'weighted_sse':float(np.sum(best.fun**2)),
                'alpha_at_bound':bool(np.isclose(abs(best.x[0]),100)),'beta_at_lower_bound':bool(np.isclose(best.x[1],1e-5,atol=1e-9))})
    frame=pd.DataFrame(rows);sensitivity=pd.DataFrame(shared)
    differences=[];tests=[]
    for name in ['alpha','beta']:
        wide=frame.pivot(index='mouse',columns='pulse',values=name).sort_index()
        assert len(wide)==10 and wide.notna().all().all()
        d=(wide[1]-wide[-1]).to_numpy();n=len(d)
        permutations=np.array(list(itertools.product([-1,1],repeat=n)))
        null=(permutations*d).mean(axis=1)
        p=float(np.mean(np.abs(null)>=abs(d.mean())-1e-12))
        se=stats.sem(d);half=stats.t.ppf(.975,n-1)*se
        tests.append({'parameter':name,'n_mice':n,'direction':'right pulse minus left pulse',
                      'mean_difference':float(d.mean()),'median_difference':float(np.median(d)),
                      'ci95_t_low':float(d.mean()-half),'ci95_t_high':float(d.mean()+half),
                      'signed_dz':float(d.mean()/d.std(ddof=1)),
                      'n_negative':int((d<0).sum()),'n_positive':int((d>0).sum()),
                      'p_exact_signflip':p,'p_paired_t_sensitivity':float(stats.ttest_rel(wide[1],wide[-1]).pvalue)})
        for mouse,left,right,delta in zip(wide.index,wide[-1],wide[1],d):
            differences.append({'mouse':mouse,'parameter':name,'left_pulse':left,'right_pulse':right,'right_minus_left':delta})
    tests=pd.DataFrame(tests)
    for pcol,target in [('p_exact_signflip','p_holm'),('p_paired_t_sensitivity','p_t_holm_sensitivity')]:
        values=tests[pcol].to_numpy();order=np.argsort(values);adjust=np.empty(len(values));run=0.
        for j,i in enumerate(order):run=max(run,(len(values)-j)*values[i]);adjust[i]=min(run,1.)
        tests[target]=adjust
    return frame,pd.DataFrame(differences),tests,sensitivity,pd.DataFrame(curves)


def draw_paired(axes,parameters,tests):
    blue='#0072B2';orange='#D55E00'
    for ax,key,title,ylabel in zip(axes,['alpha','beta'],['Midpoint α','Slope coefficient β'],
                                  ['α (% coherence)','β (per % coherence; log scale)']):
        wide=parameters.pivot(index='mouse',columns='pulse',values=key).sort_index()
        for mouse,row in wide.iterrows():
            ax.plot([0,1],[row[-1],row[1]],c='.7',lw=.7,zorder=1)
            ax.plot(0,row[-1],'v',c=blue,ms=4,zorder=2);ax.plot(1,row[1],'^',c=orange,ms=4,zorder=2)
        if key=='beta':ax.set_yscale('log')
        else:ax.axhline(0,c='.85',ls=':',lw=.5,zorder=0)
        ax.set(xlim=(-.28,1.28),xticks=[0,1],xticklabels=['Left pulse','Right pulse'],ylabel=ylabel)
        p=tests.loc[tests.parameter==key,'p_holm'].item()
        ax.set_title(f'{title}\nHolm p = {p:.3f}',fontsize=7.5,loc='left',pad=7)
        ax.tick_params(axis='x',labelsize=6.5)
