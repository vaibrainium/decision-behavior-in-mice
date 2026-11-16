"""Render manually assessed evidence with API-derived bibliographic metadata.

This script performs no automated scientific interpretation. Findings/caveats
below are the reviewer's source-assessed extraction; metadata comes from saved
Europe PMC/Crossref records. Never use JATS contributor lists as author lists:
some eLife XML includes editors/reviewers in additional contributor groups.
"""
import csv
import difflib
import hashlib
import json
from pathlib import Path
import re
import sys

OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[1]
sys.path.insert(0, str(ROOT / '.claude/skills/citation-management/scripts'))
from extract_metadata import MetadataExtractor

# PMID: theme; assessment depth; design; finding; limitation; next implication.
EXTRACT = {
'42504837': ('sensory encoding', 'selected full text: XML', 'Macaque RDK, MT recordings and pupillometry',
    'Temporal context changes sensory adaptation and behavior; MT and pupil measures provide partly separate explanatory contributions.',
    'Observational links do not identify an accumulator algorithm; adapter/test design differs from brief pulses.',
    'Test context-dependent encoding before interpreting behavioral weighting as memory leak.'),
'40610349': ('background', 'abstract/metadata; discovery only', 'Review',
    'Reviews temporal structure in perceptual decision variability.', 'Not primary evidence for this dataset or a new mechanism.', 'Use for citation chaining; do not count as an independent experiment.'),
'40114010': ('background', 'abstract/metadata; discovery only', 'Review',
    'Reviews the problem of assigning decision variability to specific processes.', 'Review synthesis is not a direct test of the proposed models.', 'Maintain separate sensory, policy and response hypotheses.'),
'40800290': ('history and bias', 'abstract', 'Human choice/RT modeling constrained by EEG',
    'Neural constraints shift the inferred source of prior-probability bias toward accumulation rate.',
    'Independent neural constraints are unavailable in the reviewed mouse trial table.', 'Do not assign all history effects to starting point by default.'),
'38816552': ('attention onset', 'selected full text: XML', 'Human spatial cueing, motion discrimination and EEG',
    'Valid cues affect sensory sensitivity and decision-related timing; CPP begins earlier.',
    'Controlled spatial attention differs from uncued mouse motion; some modeling pooled participants.',
    'The postdecision-delay null does not test variable sensory encoding or accumulation onset.'),
'38280196': ('behavioral states', 'selected full text: XML', 'Mouse visual/auditory discrimination, choices, omissions, pupil and movement',
    'Persistent performance states covary with arousal and movement; prestimulus measures predict state occupancy.',
    'State labels and physiological associations do not prove attention is the causal variable.',
    'Assess serial structure and validate inferred states with outcomes excluded from state fitting.'),
'38188903': ('gain variability', 'selected full text: XML', 'Theoretical fluctuating-stimulus DDM/confidence model',
    'Defines trial-to-trial drift-rate scaling multiplicatively for time-varying sensory evidence.',
    'A confidence derivation does not demonstrate that positive gain explains mouse pulse/RT data.',
    'Multiplicative sensitivity is an established computational alternative, not a novel attention discovery.'),
'32338595': ('identification', 'earlier review: full text', 'Perceptual strategy discrimination and modeling',
    'Specified nonintegration strategies can mimic conventional accumulation signatures.',
    'Conclusions depend on task and tested candidate families.', 'Retain fair response-process assumptions and recovery for new comparisons.'),
'33427198': ('lapses and values', 'selected full text: XML', 'Rat multisensory decisions, reward manipulations and neural disruption',
    'Reward-dependent lapse patterns support uncertainty-guided exploration over a generic inattention explanation.',
    'Reward manipulations and modalities differ from this mouse motion task.', 'Do not identify high-coherence errors or a fitted guess fraction as attention lapses.'),
'31264959': ('history and bias', 'selected full text: XML', 'Human perceptual decisions across task protocols',
    'Choice repetition relates strongly to history-dependent accumulation bias, rather than only starting point.',
    'Task-specific conditional RT predictions need simulation with this rig and stimulus.', 'Compare drift-bias and starting-point history mechanisms using conditional bias versus RT.'),
'30322902': ('mouse accumulation', 'abstract; earlier review', 'Unrestrained mouse visual evidence task',
    'Visual accumulation in freely moving mice predates the present dataset.',
    'Discrete visual pulses and response demands differ.', 'Frame novelty around constraints on variability, not the existence of mouse accumulation.'),
'30406190': ('temporal weighting', 'abstract and publisher methods excerpt', 'Human/macaque time-varying motion statistics',
    'Temporal evidence weights adapt to the time course of stimulus information.',
    'Experimentally manipulated statistics differ from the present fixed pulse schedule.', 'Treat temporal weighting as potentially strategic rather than a direct memory filter.'),
'30154467': ('identification', 'selected full text: XML', 'Computational analysis of psychophysical kernels',
    'Bounds, integration mechanisms and variable delays distort recovered sensory weights.',
    'A kernel alone cannot distinguish those sources.', 'Forward-simulate the exact response-conditioned pulse estimator for every candidate.'),
'27882927': ('urgency', 'selected full text: XML', 'Human deadline task, EEG, pupillometry and modeling',
    'Speed pressure induces urgency-related motor preparation; pupil-linked gain is a candidate implementation.',
    'Global neural gain is not equivalent to multiplying only the signed sensory input.', 'Keep sensory gain, evidence-independent urgency and bound changes distinct.'),
'26853360': ('attention onset', 'abstract', 'Human uncertain target time/location with EEG',
    'Target-selection signals modulate evidence accumulation onset and rate.',
    'Human target selection is not directly measured in the mouse task.', 'Consider onset gating only if its pulse-time and RT signatures are supported.'),
'25232732': ('arousal', 'selected full text: XML', 'Human motion discrimination, pupil and hierarchical DDM',
    'Baseline pupil state relates to variability in evidence accumulation rate.',
    'Correlational modeling does not uniquely separate between- and within-trial noise mechanisms.', 'Attention/arousal literature does not uniformly favor replacing additive drift variability.'),
'23559254': ('accumulation noise', 'abstract; earlier review', 'Rat/human controlled evidence accumulation',
    'Controlled evidence permits quantitative modeling of accumulation and noise components.',
    'Independent discrete samples offer identification advantages over correlated motion energy.', 'Separate sensory sample uncertainty from accumulation noise and latent sensitivity.'),
'18946528': ('recurrent dynamics', 'selected full text: XML', 'Recurrent circuit model of macaque motion pulses',
    'Recurrent dynamics reproduce persistent pulse effects and timing dependence.',
    'Computational agreement is not unique circuit identification.', 'Attractors remain an alternative, but a larger circuit model needs an additional discriminating signature.'),
'25716848': ('divided attention', 'abstract', 'Human dual-stream categorization with EEG',
    'Divided attention can impair downstream integration while leaving encoded decision information available.',
    'Two simultaneous streams differ substantially from the mouse single-stream task.', 'Attention can affect integration itself; do not reduce the entire literature to sensory gain.'),
'37352857': ('termination', 'earlier review: full text', 'Macaque recordings and SC intervention',
    'Independent neural and causal measurements distinguish accumulation from decision termination.',
    'Behavior-only data cannot support an equivalent circuit-level claim.', 'Use as a benchmark for specificity and calibrate the publication claim.'),
'37140191': ('identification', 'earlier review: full text', 'Cross-task/species behavioral tests of integration',
    'Designed evidence manipulations constrain integration versus nonintegration accounts.',
    'Identification depends on input correlations and task structure.', 'Existing-data mechanism claims require recoverability within the actual design.'),
'28435173': ('attention and encoding', 'selected full text: PMC web', 'Human noise/signal task, EEG-informed hierarchical DDM',
    'Attention-related EEG measures predict drift and preprocessing time and modestly improve held-out prediction.',
    'Error-RT prediction remains poor; neural features provide constraints absent here.', 'Test full choice/RT adequacy, not just a better correct-RT or choice fit.'),
'35132235': ('behavioral states', 'selected full text: author manuscript PDF', 'Mouse/human choice GLM-HMM with held-out comparisons',
    'Persistent biased and stimulus-guided strategies explain serial choice structure; RT and omissions provide external checks.',
    'State-conditioned RT checks are not a fitted joint choice/RT generative mechanism.', 'Compare static history, continuous change and a small HMM; validate pulse/RT consequences separately.'),
'33412101': ('continuous strategies', 'selected full text: author PDF and PMC web', 'Dynamic psychophysical models across species',
    'Continuous changes in sensitivity, bias and history weights can be inferred across trials and sessions.',
    'Smoothed trajectories use future data and are not prestimulus causal states.', 'Compare continuous dynamics; use filtering or properly masked prediction for pulse tests.'),
'24777419': ('gain variability', 'selected full text: author PDF', 'Macaque visual neuronal responses and modulated-Poisson modeling',
    'Multiplicative excitability fluctuations explain neuronal variability and can have slow temporal correlations.',
    'Includes anesthesia effects and is not a behavioral demonstration of attention.', 'Assess gain persistence rather than assuming an iid scalar gain is an attention model.'),
'24656259': ('adaptive gain', 'selected full text: PMC web', 'Human sequential evidence task with pupil/fMRI',
    'Context-dependent gain favors evidence consistent with recent samples and predicts serial weighting.',
    'This is not arbitrary amplification of surprising or strong pulses.', 'Require a signed context/congruency prediction before adding adaptive gain.'),
'24336710': ('attention and accumulation', 'selected full text: PMC web', 'Human RDK/EEG',
    'Decision-signal buildup varies with coherence and endogenous attentional indices.',
    'Neural covariation does not specify a unique gain distribution.', 'Sensory sensitivity is plausible, but computational parameters alone do not identify attention.'),
'23177968': ('within-trial attention', 'selected full text: PMC web', 'Human multisample categorization and EEG',
    'Evidence weighting fluctuates with slow oscillatory phase rather than remaining constant within trials.',
    'The present pulse schedule lacks a direct phase measure or broad phase-sampling design.', 'Do not fit an oscillatory attention account from a few response-conditioned pulse bins.'),
'19915566': ('sensory noise', 'abstract and available PMC text', 'Macaque attention/population recordings',
    'Attention-related performance changes include altered interneuronal correlations.',
    'Neural population noise is not identifiable from a scalar behavioral gain parameter.', 'Distinguish sensory noise, gain and decision noise.'),
'19348543': ('encoding and memory', 'abstract', 'Integrated computational attention/visual memory theory',
    'Attention changes formation or onset of durable stimulus representations driving decisions.',
    'A theoretical account is not direct validation in these mice.', 'Pure postdecision delay and evidence-encoding delay are different model tests.'),
'19186161': ('normalization background', 'selected full text: author PDF', 'Theoretical review introducing an attention normalization model',
    'Normalization can produce distinct gain effects depending on stimulus and attention-field configuration.',
    'Not new empirical evidence and not equivalent to the already fitted scalar normalization family.', 'Use for mechanisms and predictions, not as proof that another normalization fit will solve the mismatch.'),
}


def authors_crossref(authors):
    out = []
    for a in authors:
        if a.get('name'):
            out.append('{' + a['name'] + '}')
        elif a.get('family'):
            out.append(a['family'] + (', ' + a['given'] if a.get('given') else ''))
    return ' and '.join(out)


def main():
    records = json.loads((OUT / 'metadata_enriched.json').read_text())
    converter = MetadataExtractor()
    rows, bib, verification = [], [], []
    for r in records:
        pid = r['id']
        assert pid in EXTRACT, pid
        topic, access, design, finding, caveat, implication = EXTRACT[pid]
        path = OUT / 'sources' / f'crossref_{pid}.json'
        cr = json.loads(path.read_text()).get('message') if path.exists() else None
        if cr:
            title = (cr.get('title') or [''])[0]
            ratio = difflib.SequenceMatcher(None, re.sub(r'\W','',title.lower()), re.sub(r'\W','',r['title'].lower())).ratio()
            assert ratio > .85, (pid, title, r['title'])
            assert cr['DOI'].lower() == r['doi'].lower()
            year = converter._extract_year_crossref(cr)
            meta = {'entry_type': 'article', 'title': title,
                'authors': authors_crossref(cr.get('author', [])), 'year': year,
                'journal': (cr.get('container-title') or [''])[0], 'volume': cr.get('volume',''),
                'issue': cr.get('issue',''), 'pages': cr.get('page') or cr.get('article-number',''),
                'doi': r['doi'], 'pmid': pid}
            updates = cr.get('update-to', [])
        else:
            ji = r.get('journalInfo', {})
            names = []
            for a in r.get('authorList', {}).get('author', []):
                if a.get('collectiveName'):
                    names.append('{' + a['collectiveName'] + '}')
                elif a.get('lastName'):
                    names.append(a['lastName'] + (', ' + a['firstName'] if a.get('firstName') else ''))
            meta = {'entry_type': 'article','title': r['title'].rstrip('.'), 'authors':' and '.join(names),
                'year':r['pubYear'],'journal':ji.get('journal',{}).get('title',''),
                'volume':ji.get('volume',''),'issue':ji.get('issue',''),'pages':r.get('pageInfo',''),
                'doi':r.get('doi',''),'pmid':pid}
            ratio, updates = None, []
        bib.append(converter.metadata_to_bibtex(meta, citation_key=f'ref{pid}'))
        rows.append({'pmid':pid,'year':meta['year'],'authors':r['authorString'],
            'title':r['title'],'doi':r.get('doi',''),'url':'https://doi.org/'+r['doi'],
            'journal':meta['journal'],'topic':topic,'assessment':access,'design':design,
            'verified_finding':finding,'limitation':caveat,'proposed_next_test':implication,
            'crossref_identity_verified':bool(cr)})
        verification.append({'pmid':pid,'doi':r.get('doi'),'crossref_checked':bool(cr),
            'title_similarity':ratio,'update_to_metadata':updates,
            'note':'No update-to notice in checked Crossref record is not a guarantee of no correction/retraction.'})
    extra = OUT / 'sources/crossref_chakravarty2025.json'
    if extra.exists():
        m = json.loads(extra.read_text())['message']
        meta = {'entry_type':'article','title':m['title'][0], 'authors':authors_crossref(m.get('author',[])),
            'year':converter._extract_year_crossref(m),'journal':(m.get('container-title')or['eLife'])[0],
            'volume':m.get('volume',''),'pages':m.get('page')or m.get('article-number',''),'doi':m['DOI']}
        bib.append(converter.metadata_to_bibtex(meta,citation_key='Chakravarty2025'))
        rows.append({'pmid':'','year':meta['year'],'authors':meta['authors'],'title':meta['title'],
            'doi':meta['doi'],'url':'https://elifesciences.org/reviewed-preprints/105116',
            'journal':meta['journal'],'topic':'close comparator','assessment':'abstract and reviewed-preprint record',
            'design':'Cross-species behavioral accumulation framework',
            'verified_finding':'Reports mouse behavior better described using multiple strategies in a cross-species evidence task.',
            'limitation':'Reviewed preprint; task and validation differ from these RDK pulses.',
            'proposed_next_test':'Constrain novelty to the joint RT/pulse variability problem.',
            'crossref_identity_verified':True})
    with (OUT/'evidence_matrix.csv').open('w') as f:
        writer=csv.DictWriter(f,fieldnames=list(rows[0]));writer.writeheader();writer.writerows(rows)
    (OUT/'references.bib').write_text('\n\n'.join(bib)+'\n')
    (OUT/'citation_identity_checks.json').write_text(json.dumps(verification,indent=2)+'\n')
    md=['# Source-assessed evidence matrix','',
        'Assessment depth distinguishes current full-text sections, abstracts, and earlier verified reviews. Implications are proposals, not findings in this dataset.','',
        '| Reference | Design / assessment | Source finding | Limit and implication |','|---|---|---|---|']
    for r in sorted(rows,key=lambda r:(r['topic'],r['year'])):
        name=r['authors'].split(',')[0]+' ('+r['year']+')'
        md.append(f"| [{name}]({r['url']}) | {r['design']}; {r['assessment']} | {r['verified_finding']} | {r['limitation']} **Next:** {r['proposed_next_test']} |")
    (OUT/'EVIDENCE_MATRIX.md').write_text('\n'.join(md)+'\n')
    summary={'reference_records':len(rows),'fresh_crossref_identity_checks':sum(r['crossref_identity_verified'] for r in rows),
        'new_xml_bodies':10,'selection':'Purposive narrative review, not PRISMA or meta-analysis',
        'metadata_author_source':'Europe PMC/Crossref; not unfiltered JATS contributor lists',
        'files_sha256':{n:hashlib.sha256((OUT/n).read_bytes()).hexdigest() for n in ['evidence_matrix.csv','references.bib','EVIDENCE_MATRIX.md']}}
    (OUT/'bibliography_audit.json').write_text(json.dumps(summary,indent=2)+'\n')
    print(json.dumps(summary,indent=2))


if __name__=='__main__':
    main()
