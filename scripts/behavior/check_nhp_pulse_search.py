"""Independent training-only shape starts for selected outer HMMs.

Priors stay frozen. Test outcomes never choose an optimizer solution. Original
results remain intact; save a v2 selected-model/prediction set for assessment.
"""
import json
import numpy as np
import pandas as pd
from scripts.behavior.fit_nhp_pulse_pilot import (
    ROOT,OUT,INPUT,prepare,split,fit_start,predict,dump,sha,
)


def run():
    collection=pd.read_pickle(INPUT);old=pd.read_pickle(OUT/'cache/selected_models.pkl')
    revised={};predictions=[];records=[]
    signature=json.loads((OUT/'pilot_manifest.json').read_text())
    signature=signature|dict(search_source_sha256=sha(__file__),
        purpose='Two training-only coherence-sensitivity starts; priors frozen; no test selection')
    for mouse in ['PSUIM6','PSUIM7']:
        pack=prepare(mouse,collection)
        for fold in [2,3,4]:
            train=split(pack,fold);static=old[(mouse,fold,'static')]['result']
            revised[(mouse,fold,'static')]=old[(mouse,fold,'static')]
            for family in ['tied','free']:
                original=old[(mouse,fold,family)];best=original['result']
                for j,(contrast,stay)in enumerate([(.7,.95),(1.2,.985)]):
                    W=np.repeat(static['state']['weights'],2,axis=0)
                    for i,name in enumerate(pack['names']):
                        if name.startswith('coherence_'):
                            coh=int(name.split('_')[1])
                            W[:,0,i]+=np.array([-contrast,contrast])*np.sign(coh)
                    W[:,0,0]+=np.array([-.1,.1])
                    start=dict(weights=W,transition=np.array([[stay,1-stay],[1-stay,stay]]),initial=np.array([.5,.5]))
                    fit=fit_start(pack,train,family,best['prior_sigma'],0,static['state'],
                        f'outer{fold}_shape{j}',signature,tied=start)
                    records.append({k:v for k,v in fit.items()if k not in ['state','signature','progress']})
                    if fit['actual_log_probability']>best['actual_log_probability']:best=fit
                revised[(mouse,fold,family)]=dict(original,result=best)
                records.append(dict(mouse=mouse,family=family,fold=fold,stage='selection_summary',
                    objective_improvement=best['actual_log_probability']-original['result']['actual_log_probability'],
                    changed=best['stage']!=original['result']['stage']))
                print('SEARCH',mouse,fold,family,'training improvement',
                    best['actual_log_probability']-original['result']['actual_log_probability'],flush=True)
            for family in ['static','tied','free']:
                predictions.append(predict(pack,revised[(mouse,fold,family)]['result'],fold))
    dump(OUT/'cache/selected_models_v2.pkl',revised)
    pd.concat(predictions,ignore_index=True).to_csv(OUT/'heldout_predictions_v2.csv',index=False)
    pd.DataFrame(records).to_csv(OUT/'search_check.csv',index=False)
    (OUT/'search_manifest.json').write_text(json.dumps(signature,indent=2)+'\n')


if __name__=='__main__':run()
