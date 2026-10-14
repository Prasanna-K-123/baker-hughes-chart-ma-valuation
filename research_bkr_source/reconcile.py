"""Source-bound, dependency-free reconciliation of the registered BKR filings."""
from __future__ import annotations

import csv
from datetime import date
from decimal import Decimal
import hashlib
from html.parser import HTMLParser
import io
import json
from pathlib import Path
import re
import zipfile

from research_bkr_source.capture import CIK, CUTOFF, REGISTRATION, SOURCES, validate_discovery

ROOT = Path(__file__).resolve().parent
ARCHIVE_SHA = 'c0c64f1e594a149e0686bbf7c7170a2939e043d9c519ff87111980f1ad22a775'
CAPTURE_COMMIT = '91ac63f1dfa0f5aa2e04147eb47ea26674969dc3'
COLUMNS = ('bkr_historical','chart_adjusted','transaction_adjustment','financing_adjustment','published_pro_forma')
LABELS = {'cash_and_cash_equivalents':'Cash and cash equivalents','short_term_debt':'Short-term debt',
          'long_term_debt':'Long-term debt','total_assets':'Total assets'}
HEADERS = ('Baker Hughes, As Reported','Chart, As Adjusted(Note 2)',
           'Transaction Adjustments(Note 4)','Financing Adjustments(Note 6)','Pro Forma Combined')
VALUE_STARTS = (3,9,15,21,27)


class EvidenceError(ValueError): pass


class Node:
    def __init__(self, tag, attrs=None, parent=None):
        self.tag, self.attrs, self.parent = tag, dict(attrs or []), parent
        self.children=[]

    def descendants(self, tag):
        for c in self.children:
            if isinstance(c,Node):
                if c.tag==tag:yield c
                yield from c.descendants(tag)

    def text(self):
        if self.tag in {'script','style'}:return ''
        return ' '.join(c.text() if isinstance(c,Node) else c for c in self.children)


class Document(HTMLParser):
    VOID={'area','base','br','col','embed','hr','img','input','link','meta','param','source','track','wbr'}
    def __init__(self, raw):
        super().__init__(convert_charrefs=True)
        self.root=Node('root');self.stack=[self.root]
        self.feed(raw.decode('utf-8'));self.close()
    def handle_starttag(self, tag, attrs):
        n=Node(tag,attrs,self.stack[-1]);self.stack[-1].children.append(n)
        if tag not in self.VOID:self.stack.append(n)
    def handle_startendtag(self, tag, attrs):
        self.stack[-1].children.append(Node(tag,attrs,self.stack[-1]))
    def handle_endtag(self, tag):
        for i in range(len(self.stack)-1,0,-1):
            if self.stack[i].tag==tag:self.stack=self.stack[:i];break
    def handle_data(self, data):self.stack[-1].children.append(data)


def norm(s): return ' '.join(s.replace('\u00a0',' ').replace('’',"'").split())
def key(s): return re.sub(r'\s+','',norm(s)).casefold()


def spans(tr):
    result=[];start=0
    for c in tr.children:
        if not isinstance(c,Node) or c.tag not in {'td','th'}:continue
        if c.attrs.get('rowspan') not in (None,'1'):
            raise EvidenceError('Unsupported row-span schema')
        try:width=int(c.attrs.get('colspan','1'))
        except (ValueError,TypeError) as e:raise EvidenceError('Invalid column span') from e
        if not 1<=width<=30:raise EvidenceError('Excessive/nonpositive column span')
        result.append((start,start+width,norm(c.text())));start+=width
    return result,start


def group(cells,start,width=3):
    result=[]
    for a,b,text in cells:
        if b<=start or a>=start+width:continue
        if a<start or b>start+width:raise EvidenceError('A cell crosses semantic columns')
        if text:result.append(text)
    return ' '.join(result)


def rows(table):
    for tr in table.descendants('tr'):
        p=tr.parent
        while p is not None and p.tag!='table':p=p.parent
        if p is table:yield tr


def preceding_context(table):
    result=[];node=table
    for _ in range(5):
        parent=node.parent
        if parent is None:break
        siblings=[c for c in parent.children if isinstance(c,Node)]
        i=siblings.index(node)
        for s in reversed(siblings[:i]):
            if s.tag=='table' or list(s.descendants('table')):break
            t=norm(s.text())
            if t:result.append(t)
            if len(result)==3:return result
        node=parent
    return result


def number(value):
    if not isinstance(value,str):raise EvidenceError('Displayed financial text required')
    s=norm(value).replace(' ','')
    if s.startswith('$'):s=s[1:]
    if s in {'—','–','-'}:return 0
    integer=r'(?:0|[1-9][0-9]*|[1-9][0-9]{0,2}(?:,[0-9]{3})+)'
    if not re.fullmatch(integer+r'|\('+integer+r'\)',s):
        raise EvidenceError('Displayed integer or explicit dash required')
    s=s.replace(',','')
    return -int(s[1:-1]) if s.startswith('(') else int(s)


def parse_statement(raw):
    doc=Document(raw).root; candidates=[]
    for table in doc.descendants('table'):
        for tr in rows(table):
            texts={key(c.text()) for c in tr.children if isinstance(c,Node) and c.tag in {'td','th'}}
            if not {key(h) for h in HEADERS}.issubset(texts):continue
            cells,width=spans(tr)
            if width!=30 or not all(key(group(cells,s))==key(h) for s,h in zip(VALUE_STARTS,HEADERS)):
                raise EvidenceError('Statement header column positions differ')
            if key(group(cells,0))!=key('(In millions)'):
                raise EvidenceError('Statement unit differs')
            candidates.append(table)
    if len(candidates)!=1:raise EvidenceError('Ambiguous/missing registered statement schema')
    table=candidates[0]
    expected=('As of March 31, 2026','Pro Forma Combined Balance Sheet (Unaudited)','Baker Hughes Company')
    context=preceding_context(table)
    if len(context)!=3 or any(key(a)!=key(b) for a,b in zip(context,expected)):
        raise EvidenceError('Statement issuer/date/as-if heading differs')
    result=[]
    for metric,label in LABELS.items():
        matched=[]
        for tr in rows(table):
            first=next((c for c in tr.children if isinstance(c,Node) and c.tag in {'td','th'}),None)
            if first is None or key(first.text())!=key(label):continue
            cells,width=spans(tr)
            if width!=30 or key(group(cells,0))!=key(label):raise EvidenceError('Selected metric row schema differs')
            matched.append(cells)
        if len(matched)!=1:raise EvidenceError('Duplicate/missing statement metric')
        cells=matched[0];display=[group(cells,s) for s in VALUE_STARTS]
        if metric in {'cash_and_cash_equivalents','total_assets'} and any('$' not in x for x in display):
            raise EvidenceError('Dollar currency marker absent')
        values={c:number(v) for c,v in zip(COLUMNS,display)}
        if sum(values[c] for c in COLUMNS[:-1])!=values['published_pro_forma']:
            raise EvidenceError('Statement row does not reconcile')
        result.append({'metric':metric,'source_label':label,'period':'2026-03-31',
                       'basis':'illustrative_unaudited_pro_forma','unit':'USD_millions',
                       'column_values':values,'displayed_cells':display})
    return result,context,doc


def parse_transaction(doc,loan_raw):
    candidates=[]
    for table in doc.descendants('table'):
        for tr in rows(table):
            texts={key(c.text()) for c in tr.children if isinstance(c,Node) and c.tag in {'td','th'}}
            if not {key('(In millions)'),key('Purchase Price Consideration')}.issubset(texts):continue
            cs,w=spans(tr)
            if w!=6 or key(group(cs,0))!=key('(In millions)') or key(group(cs,3))!=key('Purchase Price Consideration'):
                raise EvidenceError('Consideration column positions differ')
            candidates.append(table)
    if len(candidates)!=1:raise EvidenceError('Ambiguous/missing consideration source table')
    names={'cash_consideration':'Cash consideration',
           'chart_debt_paid':'Plus: Cash paid to settle Chart\'s third-party debt',
           'termination_fee':'Plus: Chart-Flowserve termination fee',
           'stock_awards':'Plus: Other consideration for stock-based awards',
           'preliminary_consideration':'Preliminary consideration'}
    amounts={}
    for metric,label in names.items():
        values=[]
        for tr in rows(candidates[0]):
            first=next((c for c in tr.children if isinstance(c,Node) and c.tag in {'td','th'}),None)
            if first is None or key(first.text())!=key(label):continue
            cs,w=spans(tr)
            if w!=6 or key(group(cs,0))!=key(label):raise EvidenceError('Consideration row schema differs')
            values.append(number(group(cs,3)))
        if len(values)!=1:raise EvidenceError('Duplicate/missing consideration component')
        amounts[metric]=values[0]
    if any(v<0 for v in amounts.values()) or sum(amounts[k] for k in names if k!='preliminary_consideration')!=amounts['preliminary_consideration']:
        raise EvidenceError('Purchase consideration does not reconcile')
    text=norm(doc.text())
    prepaid=re.findall(r'\$([0-9,]+) million termination fee paid in (2025) by Baker Hughes',text)
    if len(prepaid)!=1 or number(prepaid[0][0])!=amounts['termination_fee']:
        raise EvidenceError('Previously paid fee is not source-confirmed')
    draws=re.findall(r'July (\d{1,2}), (2026) term loan drawdown',text)
    if len(draws)!=1:raise EvidenceError('Loan draw date is not unique in source')
    draw_date=date(int(draws[0][1]),7,int(draws[0][0])).isoformat()
    if not '2026-03-31'<draw_date<='2026-07-16':raise EvidenceError('Loan/closing chronology differs')
    loan=norm(Document(loan_raw).root.text())
    matches=re.findall(r'borrowed\s*\$([0-9]+(?:\.[0-9]+)?)\s*billion collectively',loan)
    if len(matches)!=1:raise EvidenceError('Actual loan borrowing amount is not unique')
    borrowed=Decimal(matches[0])*1000
    if borrowed<=0 or borrowed!=borrowed.to_integral_value():raise EvidenceError('Unsupported borrowing units')
    if not re.search(r'two separate \$1 billion term loans',text):raise EvidenceError('Two source financing facilities absent')
    return {'consideration_components_usd_millions':amounts,'termination_fee_prepaid_year':2025,
            'new_cash_uses_usd_millions':amounts['preliminary_consideration']-amounts['termination_fee'],
            'actual_borrowing_usd_millions':int(borrowed),'source_loan_draw_date':draw_date,
            'transaction_completion_date':'2026-07-16','original_report_filed_on':'2026-07-16',
            'amendment_filed_on':'2026-10-01'}


def verify_archive(path):
    if Path(path).stat().st_size!=60155:raise EvidenceError('Original archive size differs')
    raw=Path(path).read_bytes()
    if hashlib.sha256(raw).hexdigest()!=ARCHIVE_SHA:raise EvidenceError('Original archive digest differs')
    with zipfile.ZipFile(io.BytesIO(raw)) as z:
        expected={'CAPTURE.json'}|{name for name,url in SOURCES}
        if len(z.namelist())!=len(expected) or set(z.namelist())!=expected or z.testzip() is not None:
            raise EvidenceError('Archive members or CRC differ')
        m=json.loads(z.read('CAPTURE.json'))
        if (m.get('status'),m.get('cik'),m.get('cutoff'),m.get('registration_commit'),m.get('capture_source_commit')) != ('PASS_ORIGINAL_BYTE_CAPTURE_ONLY',CIK,CUTOFF,REGISTRATION,CAPTURE_COMMIT):
            raise EvidenceError('Capture identity/registration/cutoff differs')
        if len(m.get('files',[]))!=4 or len({f.get('path') for f in m['files']})!=4:raise EvidenceError('Repeated/incomplete source capture')
        files={f['path']:f for f in m['files']};bodies={}
        for name,url in SOURCES:
            f=files.get(name);b=z.read(name)
            if f is None or f.get('url')!=url or f.get('status_code')!=200 or len(b)!=f.get('bytes') or hashlib.sha256(b).hexdigest()!=f.get('sha256'):
                raise EvidenceError('Original source body/hash/URL differs')
            bodies[name]=b
        if validate_discovery(bodies['submissions.json'])!=m['discovery']:
            raise EvidenceError('Source discovery differs from original metadata')
    return bodies,m


def compare_transcription(parsed,path):
    with Path(path).open(newline='',encoding='utf-8') as f:old=list(csv.DictReader(f))
    if len(old)!=4 or len({r['metric'] for r in old})!=4 or {r['metric'] for r in old}!=set(LABELS):
        raise EvidenceError('Historical transcription shape differs')
    by_metric={r['metric']:r for r in old}
    for r in parsed:
        old=by_metric[r['metric']]
        if any(old.get(k)!=r[k] for k in ('period','basis','unit')) or old.get('sec_exhibit_url')!=SOURCES[2][1]:
            raise EvidenceError('Historical observation/source metadata differs')
        for col in COLUMNS:
            if not re.fullmatch(r'-?(?:0|[1-9][0-9]*)',old.get(col,'')) or int(old[col])!=r['column_values'][col]:
                raise EvidenceError('Original source disagrees with frozen transcription')
    return 20


def reconcile(archive=ROOT/'input/original_sec_capture_20261014.zip',transcription=ROOT/'historical_transcribed_rows.csv'):
    bodies,m=verify_archive(archive)
    parsed,context,doc=parse_statement(bodies['exhibit_993.html'])
    matches=compare_transcription(parsed,transcription)
    tx=parse_transaction(doc,bodies['original_8k.html'])
    values={r['metric']:r['column_values'] for r in parsed}
    cash=values['cash_and_cash_equivalents']['published_pro_forma']
    short=values['short_term_debt']['published_pro_forma'];long=values['long_term_debt']['published_pro_forma']
    if tx['new_cash_uses_usd_millions']!=-values['cash_and_cash_equivalents']['transaction_adjustment']:
        raise EvidenceError('Cash consideration and statement disagree')
    if any(values[k]['financing_adjustment']!=tx['actual_borrowing_usd_millions'] for k in ('cash_and_cash_equivalents','long_term_debt')):
        raise EvidenceError('Original borrowing and as-if financing disagree')
    if values['long_term_debt']['chart_adjusted']!=-values['long_term_debt']['transaction_adjustment']:
        raise EvidenceError('March historic Chart debt removal differs')
    return {'status':'PASS_ORIGINAL_SOURCE_RECONCILIATION','source_registration_commit':REGISTRATION,
            'original_capture_archive_sha256':ARCHIVE_SHA,'source_capture_commit':CAPTURE_COMMIT,
            'source_body_identities':m['files'],'filing_discovery':m['discovery'],
            'statement_context':context,'parsed_statement_rows':parsed,
            'original_source_vs_frozen_transcription_cells':matches,'transaction':tx,
            'as_if_balance_usd_millions':{'cash':cash,'short_debt':short,'long_debt':long,'gross_debt':short+long,'simple_net_debt':short+long-cash,'total_assets':values['total_assets']['published_pro_forma']},
            'actual_postclose_balance':None,'terminal_2028_calibration':None,
            'date_correction':'Exhibit identifies July15 loan drawdown; July16 is the closing/report date. Earlier historical shorthand must not collapse these dates.',
            'claim_boundary':'Original HTML response/column integrity and displayed arithmetic only; AS-IF March2026, not actual postclose balances, a forecast, financial/legal certification, fair value or investment recommendation.'}


def requested_balance(result,metric,observation_date,basis):
    allowed={'cash','short_debt','long_debt','gross_debt','simple_net_debt','total_assets'}
    if (result.get('status')!='PASS_ORIGINAL_SOURCE_RECONCILIATION'
            or result.get('original_capture_archive_sha256')!=ARCHIVE_SHA
            or observation_date!='2026-03-31' or basis!='illustrative_unaudited_pro_forma'
            or metric not in allowed):
        raise EvidenceError('Unsupported actual/future/basis/metric request')
    return result['as_if_balance_usd_millions'][metric]
