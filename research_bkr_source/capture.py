"""One registered, bounded, original SEC capture; no retries or redirects."""
from __future__ import annotations

import argparse
from datetime import date, datetime, timezone
import hashlib
import html
import json
import os
from pathlib import Path
import re
import time
import urllib.error
import urllib.request

CIK = '0001701605'
CUTOFF = '2026-10-14'
REGISTRATION = '83d8ed63e69bfcb7aafb422fd5e00ed9bb975e54'
MAX_BYTES = 8_000_000
SOURCES = (
    ('submissions.json', 'https://data.sec.gov/submissions/CIK0001701605.json'),
    ('amended_8k.html', 'https://www.sec.gov/Archives/edgar/data/1701605/000170160526000029/bkr-20260716.htm'),
    ('exhibit_993.html', 'https://www.sec.gov/Archives/edgar/data/1701605/000170160526000029/bkr20260110exhibit993.htm'),
    ('original_8k.html', 'https://www.sec.gov/Archives/edgar/data/1701605/000119312526305477/d105425d8k.htm'),
)
TARGETS = (
    ('0001701605-26-000029', '8-K/A', '2026-07-16', 'bkr-20260716.htm'),
    ('0001193125-26-305477', '8-K', '2026-07-16', 'd105425d8k.htm'),
)


def iso_day(value):
    if not isinstance(value, str) or date.fromisoformat(value).isoformat() != value:
        raise ValueError('Canonical ISO date required')
    return value


def validate_discovery(raw):
    p = json.loads(raw)
    if isinstance(p.get('cik'), bool) or str(p.get('cik')).zfill(10) != CIK:
        raise ValueError('Wrong SEC issuer')
    if re.sub(r'\W', '', p.get('name', '')).lower() != 'bakerhughescompany':
        raise ValueError('Wrong issuer name')
    recent = p['filings']['recent']
    names = ('accessionNumber', 'form', 'reportDate', 'filingDate', 'primaryDocument')
    if any(not isinstance(recent.get(k), list) for k in names):
        raise ValueError('Incomplete submissions arrays')
    if len({len(recent[k]) for k in names}) != 1:
        raise ValueError('Mismatched submissions arrays')
    selected = []
    for accession, form, report, document in TARGETS:
        indices = [i for i, a in enumerate(recent['accessionNumber']) if a == accession]
        if len(indices) != 1:
            raise ValueError('Registered accession is not unique')
        i = indices[0]
        item = {k: recent[k][i] for k in names}
        if (item['form'], item['reportDate'], item['primaryDocument']) != (form, report, document):
            raise ValueError('Registered form/report/primary document differs')
        if not iso_day(report) <= iso_day(item['filingDate']) <= CUTOFF:
            raise ValueError('Registered event/cutoff violation')
        if form == '8-K/A' and item['filingDate'] != '2026-10-01':
            raise ValueError('Amendment filing date differs')
        selected.append(item)
    quarters = []
    for i, form in enumerate(recent['form']):
        if form == '10-Q' and recent['filingDate'][i] <= CUTOFF:
            report, filed = recent['reportDate'][i], recent['filingDate'][i]
            if not iso_day(report) <= iso_day(filed) <= CUTOFF:
                raise ValueError('Quarter period/cutoff differs')
            quarters.append({k: recent[k][i] for k in names})
    if not quarters:
        raise ValueError('No current quarterly source discovery')
    return {'cik': CIK, 'issuer': p['name'], 'selected_filings': selected,
            'latest_10q_within_recent_asof_cutoff': max(quarters, key=lambda q: q['reportDate']),
            'snapshot_scope': 'Current capture filtered by cutoff; not original-vintage submissions history'}


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        raise ValueError('Source redirect refused')


def capture(output: Path, user_agent: str):
    if output.exists() or not output.parent.is_dir():
        raise ValueError('Fresh output directory with existing parent required')
    if (not isinstance(user_agent, str) or '\n' in user_agent or '\r' in user_agent
            or not re.search(r'[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}', user_agent)
            or len(user_agent) < 20):
        raise ValueError('Genuine declared contact identity required')
    output.mkdir()
    status = {'schema_version': 1, 'status': 'FAILED', 'cik': CIK, 'cutoff': CUTOFF,
              'registration_commit': REGISTRATION,
              'capture_source_commit': os.environ.get('GITHUB_SHA'),
              'started_at_utc': datetime.now(timezone.utc).isoformat(), 'files': []}
    opener = urllib.request.build_opener(NoRedirect())
    last_start = None
    try:
        for name, url in SOURCES:
            now = time.monotonic()
            if last_start is not None and now - last_start < 0.25:
                time.sleep(0.25 - (now - last_start))
            last_start = time.monotonic()
            request = urllib.request.Request(url, headers={'User-Agent': user_agent, 'Accept-Encoding': 'identity'})
            with opener.open(request, timeout=60) as response:
                if response.status != 200 or response.geturl() != url:
                    raise ValueError('Non-200 or changed source URL')
                content_type = response.headers.get('Content-Type', '')
                raw = response.read(MAX_BYTES + 1)
            if not raw or len(raw) > MAX_BYTES:
                raise ValueError('Empty/excessive source response')
            # Preserve the exact original body even when semantic identity fails.
            # A recorded response is not a verified filing; overall status stays FAILED.
            (output / name).write_bytes(raw)
            status['files'].append({'path': name, 'url': url, 'bytes': len(raw),
                                    'sha256': hashlib.sha256(raw).hexdigest(),
                                    'content_type': content_type, 'status_code': 200,
                                    'captured_at_utc': datetime.now(timezone.utc).isoformat()})
            if name.endswith('.json'):
                if 'json' not in content_type.lower():
                    raise ValueError('Unexpected JSON source content type')
                original = json.loads(raw)
                status['observed_discovery_identity'] = {
                    k: original.get(k) for k in ('cik', 'name', 'tickers')}
                status['discovery'] = validate_discovery(raw)
            else:
                lower = raw.lower()
                if ('html' not in content_type.lower() or b'<html' not in lower
                        or any(marker in lower for marker in (
                            b'your request originates from an undeclared',
                            b'request rate threshold exceeded', b'please enable javascript and cookies'))):
                    raise ValueError('Unexpected source HTML or access block')
                text = re.sub(r'\s+', ' ', html.unescape(re.sub(r'<[^>]*>', ' ', raw.decode('utf-8')))).lower()
                if 'baker hughes' not in text:
                    raise ValueError('Issuer absent from original filing')
        status['status'] = 'PASS_ORIGINAL_BYTE_CAPTURE_ONLY'
        status['scope'] = 'Four original response bodies captured; downstream table reconciliation is separate'
    except Exception as error:
        status['error_type'] = type(error).__name__
        status['error'] = str(error)[:300]
        raise
    finally:
        status['completed_at_utc'] = datetime.now(timezone.utc).isoformat()
        (output / 'CAPTURE.json').write_text(json.dumps(status, indent=2, sort_keys=True) + '\n')
    return status


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--output', required=True, type=Path)
    a = p.parse_args()
    result = capture(a.output, os.environ.get('SEC_USER_AGENT', ''))
    print(json.dumps({'status': result['status'], 'files': len(result['files'])}))


if __name__ == '__main__':
    main()
