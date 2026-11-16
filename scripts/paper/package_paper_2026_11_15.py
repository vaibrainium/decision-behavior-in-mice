"""Package the figures-first paper draft, references and local evidence records.

Does not fit models, change source data, or assert human source verification.
Refuses to overwrite the named deliverables; use a new dated workspace to rerun.
"""
from __future__ import annotations
import csv
import hashlib
import importlib.util
import json
from pathlib import Path
import re
import subprocess

from docx import Document
from docx.shared import Inches, Pt
from docx.oxml import OxmlElement
from docx.oxml.ns import qn

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'dissemination/paper_accumulation/draft_2026-11-15'
DATE='2026-11-16'


def write_new(path, text):
    if path.exists():
        raise FileExistsError(path)
    path.write_text(text,encoding='utf-8')


def json_new(path,value):
    write_new(path,json.dumps(value,indent=2,ensure_ascii=False)+'\n')


def metadata_references():
    module_path=ROOT/'.claude/skills/citation-management/scripts/_common.py'
    spec=importlib.util.spec_from_file_location('citation_common',module_path)
    helper=importlib.util.module_from_spec(spec);spec.loader.exec_module(helper)
    records=json.loads((OUT/'evidence/reference_metadata.json').read_text())
    keys={'10.1523/jneurosci.4684-04.2005':'Huk2005',
          '10.1364/josaa.2.000284':'Adelson1985',
          '10.3758/bf03196302':'Ratcliff2002',
          '10.7554/elife.55365':'Stine2020'}
    texts=[]; bib=[]; sources=[]; enrich=[]
    ids={'Huk2005':'E020','Stine2020':'E021','Adelson1985':'E022','Ratcliff2002':'E023'}
    pmids={'Huk2005':'16280581','Stine2020':'32338595','Adelson1985':'3973762','Ratcliff2002':'12412886'}
    locators={'Huk2005':'Eq. 8 / Fig. 4 for behavioral persistence; Figs. 8–9 and Discussion for bounded-model/time-constant interpretation.',
              'Stine2020':'Results model definitions and simulated discrimination; model methods.',
              'Adelson1985':'Abstract / original model architecture: oriented spatiotemporal quadrature energy and opponency.',
              'Ratcliff2002':'Model fitting and explicit contaminant-response/parameter-variability treatment; not a claim that our exact objective is identical.'}
    for record in records:
        assert record['status']=='retrieved',record['requested_doi']
        d=record['record']; doi=d['DOI']; key=keys[doi.lower()]
        year=d['published']['date-parts'][0][0]
        authors=[f"{a.get('family','')}, {a.get('given','')}".strip(', ') for a in d['author']]
        page=d.get('page') or d.get('article-number','')
        if key=='Adelson1985':
            enrich.append({'key':key,'field':'pages','crossref_value':page,'selected_value':'284–299',
                           'source':'https://pubmed.ncbi.nlm.nih.gov/3973762/','reason':'Crossref lists first page only; complete range verified from the primary PubMed record.'})
            page='284–299'
        fields={'author':' and '.join(authors),'title':d['title'][0],'journal':d['container-title'][0],
                'year':str(year),'volume':d.get('volume',''),'number':d.get('issue',''),
                'pages':helper.format_pages(page),'doi':doi,'url':f'https://doi.org/{doi}'}
        bib.append(helper.render_entry('article',key,fields))
        volume=d.get('volume',''); issue=f"({d['issue']})" if d.get('issue') else ''
        texts.append(f"{'; '.join(authors)} ({year}). {d['title'][0]}. {d['container-title'][0]} {volume}{issue}, {page}. https://doi.org/{doi}")
        sources.append({'evidence_id':ids[key],'source_type':'journal_article','title':d['title'][0],
            'authors':authors,'year':year,'identifiers':{'doi':doi,'pmid':pmids[key],'pmcid':'','isbn':'','url':f'https://doi.org/{doi}'},
            'locator':locators[key],'confidentiality':'public','verification':{'source_opened':False,'status':'unverified','verified_by':'','verified_on':''}})
    write_new(OUT/'references.bib','\n\n'.join(bib)+'\n')
    write_new(OUT/'references.md','# References\n\n'+'\n\n'.join(texts)+'\n')
    json_new(OUT/'evidence/bibliography_enrichment.json',enrich)
    return sources


def source_manifest(public_sources):
    catalog=[
      ('E001','Figure 1 source tables and population flow','dataset','figures_v5/figure_manifest.json; source_data/fig1_*','restricted'),
      ('E002','Matched control score and fixed-data recovery tables','dataset','figures_v5/source_data/fig2_*; dissemination/reviewer_2026-11-13/COMPLETED_RESULTS.md','restricted'),
      ('E003','Pulse directional/persistence data and intervals','dataset','figures_v5/source_data/fig3_*; dissemination/pulse_dynamics_2026-11-13/','restricted'),
      ('E004','Matched pulse predictions and choice/RT score decomposition','dataset','figures_v5/source_data/fig4_*; dissemination/pulse_rt_tradeoff_2026-11-13/','restricted'),
      ('E005','Recorded chronology, selection and original-row audit','report','dissemination/history_dynamics_2026-11-14/selection_audit.json; dissemination/reviewer_2026-11-12/independent_audit.json','restricted'),
      ('E006','Performed preprocessing and psychometric session filter','software','notebooks/0.0-data-compilation.ipynb; notebooks/0.1-preprocessing-data.ipynb cell 12; config/main.yaml; src/utils/pmf_utils.py','restricted'),
      ('E007','Decision model, parameterization and saved fitting settings','software','scripts/ddm/fit_mouse_ddm.py; src/ddm/ddm.py; src/ddm/simulator.py; evidence/control_fit_settings.json','restricted'),
      ('E008','Responded-only conditional choice and RT-quantile objective','software','src/ddm/likelihood_calculator_censored.py; scripts/ddm/fit_mouse_ddm.py select()/heldout_nll()','restricted'),
      ('E009','Fixed-input recovery and cohort recombination implementation','software','scripts/ddm/model_recovery.py; scripts/ddm/recovery_cohorts.py; dissemination/reviewer_2026-11-13/recovery_fit_inventory.csv','restricted'),
      ('E010','Huk-style trial selection, directional decomposition and dilution estimator','software','scripts/behavior/huk_shadlen_replication.py; pulse_decomposition.py; pulse_dilution.py; scripts/ddm/pulse_dynamics_bridge.py; pulse_dynamics_sensitivity.py','restricted'),
      ('E011','Motion-energy reconstruction and pulse-channel inputs','software','scripts/motion_energy.py MOUSE_ME_PARAMS; scripts/ddm/build_ddm_inputs.py; scripts/ddm/fit_mouse_ddm.py select(); .agents/reports/2026-10-29-ucla-pulse-me-nofreeze.md','restricted'),
      ('E012','Independent scheduled-pulse contrast reproduction and original corrected group comparison','software','dissemination/reviewer_2026-11-12/audit_existing_data.py signed_effect()/summary(); dissemination/reviewer_2026-11-13/COMPLETED_RESULTS.md','restricted'),
      ('E013','Individual pulse-effect bootstrap, estimands and uncertainty','software','scripts/ddm/pulse_effect_bootstrap.py; scripts/ddm/pulse_joint_signatures.py; figures_v5/source_data/fig4_C_*','restricted'),
      ('E014','Exact held-out score reconstruction and numerical-seed sensitivity','software','scripts/ddm/diagnose_pulse_rt_tradeoff.py; dissemination/pulse_rt_tradeoff_2026-11-13/RESULTS_AND_NEXT_MODEL.md','restricted'),
      ('E015','Drafting scope and author-authorized sequence','report','.agents/plans/2026-10-26-paper-accumulation-variant.md; current conversation; draft README','restricted'),
    ]
    sources=[{'evidence_id':eid,'source_type':typ,'title':title,'authors':[], 'year':2026,
       'identifiers':{'doi':'','pmid':'','pmcid':'','isbn':'','url':''},'locator':loc,'confidentiality':conf,
       'verification':{'source_opened':False,'status':'unverified','verified_by':'','verified_on':''}} for eid,title,typ,loc,conf in catalog]
    sources+=public_sources
    manifest={'schema_version':'1.0','sources':sources}
    json_new(OUT/'source_manifest.json',manifest)
    inspections=[{'evidence_id':s['evidence_id'],'agent':'Codex','inspected_on':DATE,
       'status':'agent_inspected; human verification pending',
       'note':'Sources/locators checked by the assistant. Human verifier fields intentionally remain unset; source_opened in verification refers to the required human check.'} for s in sources]
    json_new(OUT/'evidence/agent_inspection.json',inspections)
    return manifest


def bindings(filename,section):
    if filename=='figure_captions.md':
        return {'Figure 1':['E001','E005'],'Figure 2':['E002','E009'],
                'Figure 3':['E003','E010','E012'],'Figure 4':['E004','E013','E014']}.get(section[:8],['E015'])
    if filename=='results.md':
        if 'Mice used' in section:return ['E001','E005']
        if 'Control choices' in section:return ['E002','E007','E009','E021']
        if 'Brief motion' in section:return ['E003','E010','E012','E020']
        if 'Pulse responses' in section:return ['E003','E004','E013','E014']
        return ['E015']
    if section in ['Lead contact','Materials availability','Data and code availability']:
        return ['E015']
    if section in ['Experimental model and subject details','Session selection, trial selection and analysis populations']:
        return ['E005','E006','E001']
    if section=='Motion-discrimination task and behavioral timing':return ['E001','E006','E011']
    if section=='Descriptive choice and response-time summaries':return ['E001']
    if section=='Stimulus reconstruction and motion-energy representation':return ['E011','E022']
    if section in ['Accumulation and matched nonintegration models','Joint pulse models and matched variability comparisons']:
        return ['E007','E011','E021']
    if section=='Simulation-based objective and cross-validation':return ['E007','E008','E023']
    if section=='Fixed-input strategy recovery':return ['E002','E009']
    if section=='Scheduled-pulse directional response contrast':return ['E012']
    if section in ['Pulse-to-response time course','Coherence-equivalent influence and dilution adjustment']:
        return ['E003','E010','E020']
    if section=='Matched forward predictions and individual pulse-effect checks':return ['E004','E010','E013','E014']
    if section=='Quantification and statistical analysis':return ['E002','E003','E008','E010','E012','E013','E014']
    return ['E015']


def annotate(suffix=""):
    claims=[]; joined=[]; locations=[]; n=0
    for name in ['figure_captions.md','methods.md','results.md']:
        section=name; out=[]
        for lineno,line in enumerate((OUT/name).read_text().splitlines(),1):
            if line.startswith('#'):
                section=line.lstrip('# ').strip(); out.append(line);continue
            if not line.strip() or line.startswith('[AUTHOR DETAIL:') :
                out.append(line);continue
            n+=1; claim=f'C{n:03d}'; ids=bindings(name,section)
            digest=hashlib.sha256(' '.join(line.split()).encode()).hexdigest()
            kind='method' if name=='methods.md' else 'result' if name=='results.md' else 'factual'
            claims.append({'claim_id':claim,'section':f'{name}: {section}','claim_kind':kind,
                'claim_text_sha256':digest,'evidence_ids':';'.join(ids),'verification_status':'unverified',
                'uncertainty':'moderate','analysis_intent':'exploratory' if name!='methods.md' else 'descriptive'})
            out.append(line+f' [claim:{claim}] [evidence:{",".join(ids)}]')
            locations.append({'claim_id':claim,'file':name,'line':lineno,'evidence_ids':ids})
        write_new(OUT/'evidence'/name.replace('.md',f'.annotated{suffix}.md'),'\n'.join(out)+'\n')
        joined+=['',*out]
    with (OUT/f'claims{suffix}.csv').open('x',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(claims[0]));w.writeheader();w.writerows(claims)
    write_new(OUT/f'evidence/annotated_draft{suffix}.md','\n'.join(joined)+'\n')
    json_new(OUT/f'evidence/claim_locations{suffix}.json',locations)
    return claims


def consistency():
    figs=json.loads((OUT/'figures_v5/figure_manifest.json').read_text())
    facts=[]
    concepts=[('n_mice',10,'mice','retained sessions','E001'),('n_sessions',50,'sessions','retained sessions','E001'),
      ('n_responded',25508,'trials','descriptive responses','E001'),('n_model',25493,'trials','model responses','E001'),
      ('n_control_model',14014,'trials','control-model CV','E002'),('n_control_descriptive',14015,'trials','descriptive controls','E001'),
      ('n_temporal',19313,'trials','response-conditioned pulse readout','E003'),('n_temporal_pulse',8529,'trials','response-conditioned pulse readout','E003'),
      ('recovery_pairs',100,'pairs','synthetic strategy recovery','E002'),('recovery_fits',500,'fits','synthetic strategy recovery','E002'),
      ('recovery_recombinations',1024,'recombinations','dependent recovery exercise','E002'),
      ('signed_effect',5.84,'percentage_points','assignment-based response by 5 s','E003'),
      ('choice_delta',-49.29,'NLL','matched joint CV','E004'),('rt_delta',360.22,'NLL','matched joint CV','E004'),
      ('total_delta',310.93,'NLL','matched joint CV','E004')]
    for concept,value,unit,analysis,eid in concepts:
        for section in ['figure_captions','methods' if concept.startswith('n_') or concept.startswith('recovery') else 'results','results']:
            if any(f['concept']==concept and f['section']==section for f in facts):continue
            facts.append({'fact_id':f'N{len(facts)+1:03d}','concept':concept,'section':section,'value':value,'unit':unit,
              'numerator':None,'denominator':None,'sample_size':None,'analysis_set':analysis,'evidence_ids':[eid]})
    methods=[]; results=[]
    for i,(name,eid) in enumerate([('Control model comparison and recovery','E002'),('Pulse influence and temporal persistence','E003'),('Matched pulse/RT predictions','E004')],1):
        methods.append({'method_id':f'M{i:03d}','name':name,'analysis_intent':'exploratory','protocol_status':'post_hoc','outcome_ids':[f'O{i:03d}']})
        results.append({'result_id':f'R{i:03d}','method_id':f'M{i:03d}','outcome_id':f'O{i:03d}','analysis_intent':'exploratory','sample_size':10,'evidence_ids':[eid],'reported_sections':['figure_captions','results']})
    json_new(OUT/'consistency_manifest.json',{'schema_version':'1.0','numeric_facts':facts,'methods':methods,'results':results})
    return figs


def manuscript_manifest():
    template=json.loads((ROOT/'.claude/skills/scientific-writing/assets/manuscript_manifest_template.json').read_text())
    template['document_id']='mouse-motion-figures-first-20261115'
    template['study_design']='Existing-data behavioral animal experiment with within-session scheduled stimulus perturbations and computational model comparison'
    template['registries']['reporting_coverage']='reporting_coverage.json'
    template['reporting_guidelines']=['arrive-2.0-2020']
    json_new(OUT/'manuscript_manifest.json',template)
    authorship=json.loads((ROOT/'.claude/skills/scientific-writing/assets/authorship_template.json').read_text())
    json_new(OUT/'authorship.json',authorship)
    coverage={'guideline':'ARRIVE 2.0','official_source':'https://arriveguidelines.org/arrive-guidelines','checked':DATE,
      'status':'working coverage; not a completed official checklist',
      'addressed':['Analysis sets and experimental unit','Recorded inclusion/exclusion criteria','Outcome estimands and statistical procedures','Group/within-mouse uncertainty distinctions'],
      'partial':['Study design and task procedures','Sample-size provenance','Reporting of all supporting analyses'],
      'missing_author_facts':['Animal characteristics','Ethics approvals/protocol IDs','Randomization implementation','Blinding','Housing/welfare and training details']}
    json_new(OUT/'reporting_coverage.json',coverage)


def style_notes():
    notes=[
      {'paper':'Huk & Shadlen (2005)','url':'https://www.gatsby.ucl.ac.uk/~pel/course_wuhan/2021/papers/huk_shadlen2005.pdf',
       'inspected':'Original PDF: behavioral Results, Fig. 4 and bounded-model sections.',
       'pattern':'Establish behavior, test persistence, then compare the observed trajectory with a model. Give the positive persistence finding a clear conclusion before discussing the origin of the decline.',
       'applied':'Results section on persistent pulse influence followed by a separate model-comparison section.'},
      {'paper':'Stine et al. (2020)','url':'https://pmc.ncbi.nlm.nih.gov/articles/PMC7217695/',
       'inspected':'Primary PMC text and full XML; strategy definitions, experimental Results and recovery reasoning.',
       'pattern':'Define competing decision rules operationally, explain the comparison that distinguishes them, validate discrimination on simulations, then interpret subjects. Scope conclusions to tested models.',
       'applied':'Matched C/E/ES explanation and recovery stay in the main Results; RT evidence is reported directly.'},
      {'paper':'Odoemene et al. (2018)','url':'https://pmc.ncbi.nlm.nih.gov/articles/PMC6246883/',
       'inspected':'Primary PMC Results: task performance and temporal-weighting sections.',
       'pattern':'Open with the animal task and observable behavior. Use finding-based headings and connect the next analysis to a specific question raised by the previous result.',
       'applied':'Task behavior precedes model inference; headings identify the findings. No unsupported learning or neural-manipulation claim is borrowed.'},
      {'paper':'Stine et al. (2023), Neuron','url':'https://pmc.ncbi.nlm.nih.gov/articles/PMC10565788/',
       'inspected':'Primary PMC Results opening, behavioral/pulse reasoning and correlation-to-intervention transition.',
       'pattern':'Keep task setup concise; link observations to a stated hypothesis; introduce the test needed to go beyond the current inference. The strength of the language follows the experimental support.',
       'applied':'Short task introduction, figure-linked evidence and a specific interpretation at each section end; no causal neural language transferred to this behavioral study.'},
      {'paper':'Roy et al. (2021), Neuron','url':'https://pmc.ncbi.nlm.nih.gov/articles/PMC7897255/',
       'inspected':'Primary full-text search extraction: Introduction, initial model/task Results and Discussion. Direct PMC open challenged; XML unavailable.',
       'pattern':'Introduce a model through the behavioral problem it addresses, define its variables only as needed, and separate predictive description from mechanism.',
       'applied':'Model terms explained by what they change in behavior. The paper remains an accumulation/pulse study, not a PsyTrack methods paper.'},
    ]
    json_new(OUT/'evidence/writing_models.json',notes)
    text='''# Writing notes

The author-selected production order was figures → captions → Methods → Results. Introduction, Discussion, Summary and the final title are deferred to the next phase. This is a writing packet, not a submission-ready manuscript.

Comparable primary papers and the specific passages inspected are recorded in `evidence/writing_models.json`. The adopted pattern is a focused question, the comparison needed to answer it, a figure-linked finding, and a short inference. The draft uses original prose and no copied passages. Headings name findings. Model terminology follows decision-making usage: motion strength/coherence, choice bias, reaction time, accumulation, decision bound, drift variability and temporal integration. Technical bookkeeping remains in Methods, captions or evidence files.

The current main set contains four figures because they carry this argument; this is not a claimed journal figure-count requirement. The official Neuron author page returned 403 during the current check, so exact limits and final format remain unverified. The draft uses a provisional STAR Methods structure and working author-year references. Final citation and section ordering can be converted after the narrative is settled.

Source checks were performed by Codex. The skill's named-human verification fields are intentionally pending; none are represented as completed. Drafting is authorized, while publication approval remains separate. No unpublished text or data were included in public search or metadata queries.

The optional citation helper requires `requests`, which is absent from the project environment. Public Crossref metadata were retrieved with the standard library instead, and bibliography formatting uses the skill's dependency-free local renderer. No packages were installed. Complete Adelson–Bergen pagination was checked against the primary PubMed record because Crossref provided only the first page.

Scientific-writing, citation-management, scientific-visualization and venue-template repository skills informed this work. Workflow attribution: Kassis, T., Agarwal, V., He, Y., Patel, D., and Brueckner, A. M. (2026). Scientific Agent Skills: A Library of Procedural Knowledge for Research Agents. arXiv preprint. https://doi.org/10.48550/arXiv.2609.00065 . The current record was checked during this drafting session. This is workflow attribution, not evidence about decision making.

Open author facts are explicitly marked in Methods: animals, oversight, training/task hardware, randomization/blinding, resource access, authorship and declarations. Historical exploratory analyses, including the state/delay/gain pilots, remain preserved; they are candidates for supporting material rather than added main-paper claims in this first packet.
'''
    write_new(OUT/'WRITING_NOTES.md',text)


def append_markdown(doc,text):
    equation=False
    for line in text.splitlines():
        if not line.strip():continue
        if line.startswith('#'):
            level=min(len(line)-len(line.lstrip('#')),3)
            doc.add_heading(line.lstrip('# ').strip(),level=level)
        elif line.startswith('\\['):
            equation=True
        elif line.startswith('\\]'):
            equation=False
        else:
            p=doc.add_paragraph()
            if equation:
                p.style='No Spacing'
                value=line
                if line.startswith('dX_i'):
                    value='dXᵢ(t) = [g f(Mᵢ(t)) + b + sᵥ Zᵢ − λ{Xᵢ(t) − za}] dt + dWᵢ(t)'
                elif line.startswith('\\mathrm{NLL}'):
                    value='NLL = −∑(c,k) nₖc log P̂(k | c, R) − ∑(c,k,b) n_bkc log P̂(b | k, c, R)'
                para=OxmlElement('m:oMathPara');math=OxmlElement('m:oMath');run=OxmlElement('m:r');text=OxmlElement('m:t')
                text.text=value;run.append(text);math.append(run);para.append(math);p._p.append(para)
            else:
                for i,part in enumerate(re.split(r'(\*\*[^*]+\*\*)',line)):
                    r=p.add_run(part[2:-2] if part.startswith('**') else part)
                    r.bold=part.startswith('**')
                if line.startswith('[AUTHOR DETAIL:'):
                    for r in p.runs:r.font.color.rgb=__import__('docx').shared.RGBColor.from_string('9C3600')


def packet(suffix=""):
    title='Mouse motion decisions: figures-first working draft'
    assembled=['# '+title,'','Draft started 2026-11-15; assembled 2026-11-16. Production order: figures, captions, Methods, Results. Introduction, Discussion and Summary are deferred.','']
    doc=Document()
    sec=doc.sections[0];sec.top_margin=Inches(.65);sec.bottom_margin=Inches(.65);sec.left_margin=Inches(.7);sec.right_margin=Inches(.7)
    normal=doc.styles['Normal'];normal.font.name='Arial';normal.font.size=Pt(10.5);normal.paragraph_format.space_after=Pt(7)
    doc.add_heading(title,0)
    doc.add_paragraph('Internal working draft · 16 November 2026. Human source verification and author-specific details are pending.')
    doc.add_paragraph('Figures and captions → Methods → Results. The separate main_figures.pdf retains native-size artwork.')
    page=doc.sections[0].footer.paragraphs[0]
    page.alignment=2
    fld=OxmlElement('w:fldSimple');fld.set(qn('w:instr'),'PAGE');page._p.append(fld)
    caps=(OUT/'figure_captions.md').read_text()
    sections=re.split(r'(?m)^## ',caps)[1:]
    for i,caption in enumerate(sections,1):
        doc.add_page_break()
        heading,body=caption.split('\n',1)
        doc.add_heading(heading,1)
        # Preserve legibility in the editable packet; tall Figure 4 is on its own
        # page and its caption follows naturally instead of shrinking text.
        width=6.2 if i!=4 else 5.7
        doc.add_picture(str(OUT/'figures_v5'/f'figure{i}.png'),width=Inches(width))
        append_markdown(doc,body)
        assembled += ['## '+heading,'',f'![Figure {i}](figures_v5/figure{i}.png)','',body]
    for filename in ['methods.md','results.md','references.md']:
        doc.add_page_break(); text=(OUT/filename).read_text()
        append_markdown(doc,text)
        assembled+=['',text]
    target=OUT/f'working_draft{suffix}.docx'
    if target.exists():raise FileExistsError(target)
    doc.save(target)
    write_new(OUT/f'working_draft{suffix}.md','\n'.join(assembled)+'\n')
    return {'paragraphs':len(doc.paragraphs),'images':len(doc.inline_shapes)}


def main():
    public=metadata_references(); source_manifest(public);claims=annotate();figs=consistency();manuscript_manifest();style_notes();doc=packet()
    summary={'date':DATE,'base_commit':figs['base_commit'],'new_work_uncommitted':True,
      'selected_artwork':'figures_v5','n_figures':len(figs['figures']),'n_panel_source_tables':len(figs['panels']),
      'claim_count':len(claims),'references':len(public),'docx':doc,
      'human_verification_completed':False,'submission_ready':False,
      'scope':'Existing-results figure assembly, captions, Methods and Results; no new fitting/simulation; Intro/Discussion/Summary deferred.'}
    json_new(OUT/'draft_manifest.json',summary)
    print(json.dumps(summary,indent=2))

def revision(version='v2'):
    suffix='_'+version
    claims=annotate(suffix)
    doc=packet(suffix)
    manifest=json.loads((OUT/'manuscript_manifest.json').read_text())
    manifest['registries']['claim_evidence']='claims'+suffix+'.csv'
    manifest['reporting_guidelines']=['arrive-2.0-2020']
    manifest['registries']['consistency_manifest']='consistency_manifest_v2.json'
    json_new(OUT/('manuscript_manifest'+suffix+'.json'),manifest)
    summary=json.loads((OUT/'draft_manifest.json').read_text())
    summary['claim_count']=len(claims);summary['docx']=doc
    summary['revision']=version;summary['selected_reading_copy']='working_draft'+suffix+'.docx'
    summary['selected_evidence_copy']='evidence/annotated_draft'+suffix+'.md'
    json_new(OUT/('draft_manifest'+suffix+'.json'),summary)
    print(json.dumps(summary,indent=2))

if __name__=='__main__':
    import sys
    if '--revision' in sys.argv:revision(sys.argv[sys.argv.index('--revision')+1])
    else:main()
