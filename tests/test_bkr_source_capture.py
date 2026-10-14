"""Source-identity and transport refusal controls; no network requests."""
import copy
import json
from pathlib import Path
import tempfile
import unittest

from research_bkr_source.capture import NoRedirect, capture, iso_day, validate_discovery


def fixture():
    # Deliberately small metadata fixture, using the observed original identities.
    return {'cik': '0001701605', 'name': 'Baker Hughes Co', 'tickers': ['BKR'],
            'filings': {'recent': {
                'accessionNumber': ['0001701605-26-000029', '0001193125-26-305477', '0001701605-26-000023'],
                'form': ['8-K/A', '8-K', '10-Q'],
                'reportDate': ['2026-07-16', '2026-07-16', '2026-06-30'],
                'filingDate': ['2026-10-01', '2026-07-16', '2026-07-27'],
                'primaryDocument': ['bkr-20260716.htm', 'd105425d8k.htm', 'bkr-20260630.htm'],
            }}}


def check(p): return validate_discovery(json.dumps(p).encode())


class SourceIdentityTests(unittest.TestCase):
    def test_observed_alias_and_registered_filings(self):
        r=check(fixture())
        self.assertEqual(len(r['selected_filings']),2)
        self.assertEqual(r['latest_10q_within_recent_asof_cutoff']['reportDate'],'2026-06-30')

    def test_legal_company_name_alias(self):
        p=fixture();p['name']='Baker Hughes Company'
        self.assertEqual(check(p)['cik'],'0001701605')

    def test_wrong_cik_and_boolean_refused(self):
        for v in ('0001701606',True):
            with self.subTest(v=v):
                p=fixture();p['cik']=v
                with self.assertRaises(ValueError):check(p)

    def test_wrong_name_refused(self):
        p=fixture();p['name']='A different issuer'
        with self.assertRaises(ValueError):check(p)

    def test_wrong_or_untyped_ticker_refused(self):
        for v in (['BKRB'],'BKR',[]):
            with self.subTest(v=v):
                p=fixture();p['tickers']=v
                with self.assertRaises(ValueError):check(p)

    def test_parallel_array_mismatch(self):
        p=fixture();p['filings']['recent']['form'].pop()
        with self.assertRaises(ValueError):check(p)

    def test_duplicate_registered_accession(self):
        p=fixture();r=p['filings']['recent']
        for key in r:r[key].append(r[key][0])
        with self.assertRaises(ValueError):check(p)

    def test_missing_registered_accession(self):
        p=fixture();p['filings']['recent']['accessionNumber'][0]='0001701605-26-000028'
        with self.assertRaises(ValueError):check(p)

    def test_wrong_form_report_and_document(self):
        for key,value in [('form','8-K'),('reportDate','2026-07-15'),('primaryDocument','other.htm')]:
            with self.subTest(key=key):
                p=fixture();p['filings']['recent'][key][0]=value
                with self.assertRaises(ValueError):check(p)

    def test_future_filing_and_wrong_amendment_date(self):
        for d in ('2026-10-15','2026-10-02'):
            with self.subTest(d=d):
                p=fixture();p['filings']['recent']['filingDate'][0]=d
                with self.assertRaises(ValueError):check(p)

    def test_event_must_not_postdate_filing(self):
        p=fixture();p['filings']['recent']['filingDate'][1]='2026-07-15'
        with self.assertRaises(ValueError):check(p)

    def test_future_quarter_is_not_available_at_cutoff(self):
        p=fixture();p['filings']['recent']['filingDate'][2]='2026-10-27'
        with self.assertRaises(ValueError):check(p)

    def test_no_input_mutation(self):
        p=fixture();old=copy.deepcopy(p);check(p)
        self.assertEqual(p,old)

    def test_iso_dates_are_canonical(self):
        for v in ('2026-7-16','2026-07-16T00:00:00','not-a-date'):
            with self.subTest(v=v):
                with self.assertRaises(ValueError):iso_day(v)

    def test_redirect_refused(self):
        with self.assertRaises(ValueError):NoRedirect().redirect_request(None,None,302,'redirect',{},'https://other.test')

    def test_undeclared_agent_refused_before_network(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'fresh'
            with self.assertRaises(ValueError):capture(p,'anonymous')
            self.assertFalse(p.exists())

    def test_existing_output_refused_before_network(self):
        with tempfile.TemporaryDirectory() as d:
            with self.assertRaises(ValueError):capture(Path(d),'Prasanna academic contact example@example.org')


if __name__=='__main__':unittest.main()
