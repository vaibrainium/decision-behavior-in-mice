"""Check direction/congruency coding independently of fitted models."""
import numpy as np
from scipy import special
from scripts.behavior.make_nhp_pulse_inputs import pulse_features


def run():
    schedule=np.tile(np.arange(-3,4),2)
    baseline=np.repeat([-18.,18.],7)
    d,dnames,_=pulse_features(schedule,baseline,'direction')
    np.testing.assert_array_equal(d[:7],d[7:])
    np.testing.assert_array_equal(d.sum(1),schedule!=0)
    c,names,_=pulse_features(schedule,baseline,'congruency')
    np.testing.assert_array_equal(np.abs(c).sum(1),schedule!=0)
    for i,(s,b)in enumerate(zip(schedule,baseline)):
        active=np.flatnonzero(c[i])
        if not s:assert len(active)==0;continue
        assert len(active)==1
        label=names[active[0]]
        assert f'stage{abs(s)}'in label
        expected='congruent'if s*b>0 else'incongruent'
        assert label==f'pulse_{expected}_stage{abs(s)}_baseline_signed'
        assert c[i,active[0]]==np.sign(b)
    # A congruent pulse shifts right-choice log odds in opposite directions
    # for left/right baselines, but shifts correctness in the same direction.
    beta=np.array([.3,-.8,.4,-.7,.6,-.5])
    eta=c@beta+np.linspace(-1,1,len(schedule))
    right=(np.arange(len(schedule))%2).astype(float);side=np.sign(baseline)
    correct=np.where(side>0,right,1-right)
    nll_right=np.logaddexp(0,eta)-right*eta
    nll_correct=np.logaddexp(0,side*eta)-correct*side*eta
    np.testing.assert_allclose(nll_right,nll_correct,atol=1e-14)
    try:pulse_features([1],[0.],'congruency')
    except ValueError:pass
    else:raise AssertionError('Undefined zero-coherence congruency silently coded')
    # Task-side coding keeps 0% trials and agrees with baseline coding whenever
    # baseline sign and assigned side agree. Physical pulse sign is retained.
    target=np.where(baseline>0,1.,-1.)
    t,tnames,_=pulse_features(schedule,np.zeros(len(schedule)),'target_congruency',target)
    np.testing.assert_array_equal(t,c)
    assert all('_target_signed'in n for n in tnames)
    np.testing.assert_array_equal(np.abs(t).sum(1),schedule!=0)
    for i,s in enumerate(schedule):
        if s:
            active=np.flatnonzero(t[i])[0]
            expected='congruent'if s*target[i]>0 else'incongruent'
            assert tnames[active]==f'pulse_{expected}_stage{abs(s)}_target_signed'
            assert t[i,active]==target[i]
    try:pulse_features([1],[0.],'target_congruency',[np.nan])
    except ValueError:pass
    else:raise AssertionError('Missing assigned target silently filled')
    print('PASS: six distinct types; control zero; congruency/physical direction mapping; right-choice/correctness likelihood equivalence')


if __name__=='__main__':run()
