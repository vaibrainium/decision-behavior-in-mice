"""Apply source-verified locator/type corrections without changing the raw export."""
import json
from pathlib import Path
import re
import sys
import xml.etree.ElementTree as ET

OUT=Path(__file__).resolve().parent
ROOT=OUT.parents[1]
sys.path.insert(0,str(ROOT/'.claude/skills/citation-management/scripts'))
from _common import parse_bibtex,render_entry

entries=parse_bibtex((OUT/'references.bib').read_text())
changes=[]
for e in entries:
    f=e['fields']
    old=f.get('pages','')
    new=re.sub(r'^(\d+)-(\d+(?:\.e\d+)?)$',r'\1--\2',old)
    if new!=old:
        f['pages']=new
        changes.append({'key':e['key'],'field':'pages','before':old,'after':new,
                        'reason':'Format an actual page range; preserve electronic-page suffix.'})
    if e['key']=='ref18946528' and not f.get('pages'):
        article=ET.parse(OUT/'sources/wong2007_PMC2525934.xml').getroot()
        locator=article.findtext('front/article-meta/fpage')
        assert locator=='6'
        f['pages']=locator
        changes.append({'key':e['key'],'field':'pages','after':locator,
                        'source':'sources/wong2007_PMC2525934.xml: front/article-meta/fpage'})
    if e['key']=='Chakravarty2025':
        m=json.loads((OUT/'sources/crossref_chakravarty2025.json').read_text())['message']
        assert m['type']=='posted-content'
        e['type']='misc'
        f.pop('journal',None)
        f['howpublished']='eLife reviewed preprint'
        f['note']='Reviewed preprint; version 1 published 11 April 2025'
        changes.append({'key':e['key'],'field':'type','after':'misc',
                        'source':'Crossref posted-content and eLife reviewed-preprint record'})
(OUT/'references_verified.bib').write_text('\n\n'.join(render_entry(e['type'],e['key'],e['fields'])for e in entries)+'\n')
(OUT/'bibliography_normalizations.json').write_text(json.dumps({'changes':changes,
    'preserved_article_identifiers':['imag-2-00338','ENEURO.0169-18.2018'],
    'note':'Identifier hyphens are not page ranges. Missing preprint volume/pages are not invented.'},indent=2)+'\n')
print('Wrote source-verified bibliography:',len(entries),'entries;',len(changes),'normalizations')
