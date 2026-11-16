"""Public scholarly retrieval for a focused narrative review; no project data sent.

Retrieves selected OA JATS, uses the pinned skill's metadata-only-safe parser,
and obtains one bounded metadata query. All requests and failures are recorded.
"""
import argparse
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import time
import urllib.parse
import urllib.request

OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[1]
BASE = 'https://www.ebi.ac.uk/europepmc/webservices/rest'
PARSER = ROOT / '.claude/skills/paper-lookup/scripts/jats_to_text.py'
PAPERS = {
    'ashwood2022': 'PMC8890994', 'hulsey2024': 'PMC11016285',
    'roy2021': 'PMC7897255', 'urai2019': 'PMC6606080',
    'murphy2014': 'PMC4168983', 'nunez2017': 'PMC5397902',
    'kelly2013': 'PMC6618757', 'cheadle2014': 'PMC4411568',
    'wyart2012': 'PMC3975574', 'reynolds2009': 'PMC2752446',
    'pisupati2021': 'PMC7846276', 'okazawa2018': 'PMC6113286',
    'attention_onset2024': 'PMC11208218', 'mcgaughey2026': 'PMC13405624',
    'gain_confidence2024': 'PMC7615478', 'wong2007': 'PMC2525934',
    'murphy2016urgency': 'PMC5123079', 'wyart2015divided': 'PMC4402727',
}
EXTRA_PMIDS = ['26853360', '30406190', '23559254', '30322902', '40800290']
EXTRA_DOIS = ['10.7554/eLife.55365', '10.7554/eLife.105116',
              '10.1038/s41583-025-00916-3', '10.1016/j.tics.2025.06.003']


def request(url, target):
    if target.exists():
        return {'url': url, 'file': str(target.relative_to(OUT)), 'cached': True, 'ok': True}
    record = {'url': url, 'file': str(target.relative_to(OUT)),
              'accessed_utc': datetime.now(timezone.utc).isoformat(), 'ok': False}
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'scientific-literature-review/1.0 (public scholarly lookup)'})
        with urllib.request.urlopen(req, timeout=25) as response:
            data = response.read()
            record['http_status'] = response.status
        target.write_bytes(data)
        record.update(ok=True, sha256=hashlib.sha256(data).hexdigest(), bytes=len(data))
    except Exception as exc:
        record['error'] = str(exc)
    return record


def get_text(item):
    key, pmc = item
    path = OUT / 'sources' / f'{key}_{pmc}.xml'
    record = request(f'{BASE}/{pmc}/fullTextXML', path)
    if record['ok']:
        result = subprocess.run([sys.executable, str(PARSER), str(path)], capture_output=True, text=True)
        record['parser_exit'] = result.returncode
        if result.returncode == 0:
            parsed = json.loads(result.stdout)
            (OUT / 'sources' / f'{key}.json').write_text(json.dumps(parsed, indent=2))
            record['parsed_file'] = f'sources/{key}.json'
        else:
            record['parser_error'] = result.stderr[:500]
    print(key, record.get('http_status'), 'parser', record.get('parser_exit'), flush=True)
    return key, record


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--fetch', action='store_true')
    parser.add_argument('--crossref', action='store_true')
    a = parser.parse_args()
    (OUT / 'sources').mkdir(parents=True, exist_ok=True)
    logs = {}
    lp = OUT / 'retrieval_log.json'
    if lp.exists():
        logs = json.loads(lp.read_text())
    if a.fetch:
        with ThreadPoolExecutor(max_workers=2) as pool:
            logs.update(dict(pool.map(get_text, PAPERS.items())))
        pmids = list(EXTRA_PMIDS)
        dois = list(EXTRA_DOIS)
        for key in PAPERS:
            p = OUT / 'sources' / f'{key}.json'
            if p.exists():
                d = json.loads(p.read_text())
                m = d.get('metadata', d)
                if m.get('pmid'):
                    pmids.append(m['pmid'])
                elif m.get('doi'):
                    dois.append(m['doi'])
        query = '(' + ' OR '.join([f'EXT_ID:{v}' for v in pmids] + [f'DOI:"{v}"' for v in dois]) + ') AND SRC:MED'
        params = {'query': query, 'format': 'json', 'pageSize': 100, 'resultType': 'core'}
        target = OUT / 'sources/selected_metadata.json'
        logs['selected_metadata'] = request(BASE + '/search?' + urllib.parse.urlencode(params), target)
        if target.exists():
            body = json.loads(target.read_text())
            assert 'resultList' in body and 'errCode' not in body, body
            records = body['resultList']['result']
            (OUT / 'metadata.json').write_text(json.dumps(records, indent=2))
            logs['selected_metadata'].update(total=body['hitCount'], retrieved=len(records), bounded=True)
            print('METADATA', len(records), 'of', body['hitCount'], flush=True)
    if a.crossref:
        metadata_file = OUT / 'metadata_enriched.json'
        records = json.loads((metadata_file if metadata_file.exists() else OUT / 'metadata.json').read_text())
        # Earlier control-review sources already have verified records. Focus
        # fresh Crossref calls on the new attention/state/encoding synthesis.
        skip = {'40610349', '40114010', '32338595', '37140191', '23559254', '30322902'}
        for d in records:
            if d['id'] in skip:
                continue
            doi = d.get('doi')
            if not doi:
                continue
            key = d.get('pmid') or d['id']
            target = OUT / 'sources' / f'crossref_{key}.json'
            logs[f'crossref_{key}'] = request('https://api.crossref.org/works/' + urllib.parse.quote(doi, safe=''), target)
            print('CROSSREF', key, doi, logs[f'crossref_{key}']['ok'], flush=True)
            time.sleep(.3)
    lp.write_text(json.dumps(logs, indent=2))


if __name__ == '__main__':
    main()
