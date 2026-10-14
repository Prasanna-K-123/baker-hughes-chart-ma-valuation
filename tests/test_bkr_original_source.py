"""Genuine-source reconciliation and consequential corruption/refusal checks."""
import copy
import csv
import io
import re
import tempfile
from pathlib import Path
import unittest

from research_bkr_source.reconcile import (
    ROOT,Document,EvidenceError,compare_transcription,number,parse_statement,
    parse_transaction,reconcile,requested_balance,verify_archive,
)
from research_bkr_source.run import verify_reference


class OriginalSourceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.bodies,cls.manifest=verify_archive(ROOT/'input/original_sec_capture_20261014.zip')
        cls.raw=cls.bodies['exhibit_993.html']
        cls.text=cls.raw.decode('utf-8')
        cls.result=reconcile()

    def changed(self,needle,replacement):
        self.assertIn(needle,self.text)
        return self.text.replace(needle,replacement,1).encode()

    def row(self,label):
        pattern=r'<tr\b[^>]*>(?:(?!</tr>).)*?'+re.escape(label)+r'(?:(?!</tr>).)*?</tr>'
        matches=re.findall(pattern,self.text,re.S|re.I)
        self.assertTrue(matches,label)
        return matches[0]

    def test_all_twenty_original_cells_match_previous_transcription(self):
        rows,context,doc=parse_statement(self.raw)
        self.assertEqual(compare_transcription(rows,ROOT/'historical_transcribed_rows.csv'),20)
        self.assertEqual(context[0],'As of March 31, 2026')
        self.assertEqual(self.result['as_if_balance_usd_millions'],
                         {'cash':2484,'short_debt':753,'long_debt':17411,'gross_debt':18164,'simple_net_debt':15680,'total_assets':56214})

    def test_prepaid_fee_is_distinct_from_new_cash_use(self):
        tx=self.result['transaction'];c=tx['consideration_components_usd_millions']
        self.assertEqual(c['preliminary_consideration'],14806)
        self.assertEqual(c['termination_fee'],258)
        self.assertEqual(tx['termination_fee_prepaid_year'],2025)
        self.assertEqual(tx['new_cash_uses_usd_millions'],10054+4451+43)
        self.assertEqual(tx['new_cash_uses_usd_millions'],14806-258)

    def test_draw_closing_and_filing_dates_are_distinct(self):
        tx=self.result['transaction']
        self.assertEqual(tx['source_loan_draw_date'],'2026-07-15')
        self.assertEqual(tx['transaction_completion_date'],'2026-07-16')
        self.assertEqual(tx['original_report_filed_on'],'2026-07-16')
        self.assertEqual(tx['amendment_filed_on'],'2026-10-01')
        self.assertEqual(tx['actual_borrowing_usd_millions'],2000)

    def test_actual_and_future_balance_requests_refused(self):
        for d in ('2026-07-16','2026-09-30','2028-12-31'):
            with self.subTest(date=d):
                with self.assertRaises(EvidenceError):requested_balance(self.result,'simple_net_debt',d,'illustrative_unaudited_pro_forma')
        with self.assertRaises(EvidenceError):requested_balance(self.result,'cash','2026-03-31','actual')

    def test_unknown_fair_value_is_refused_even_if_injected(self):
        r=copy.deepcopy(self.result);r['as_if_balance_usd_millions']['fair_value']=1
        with self.assertRaises(EvidenceError):requested_balance(r,'fair_value','2026-03-31','illustrative_unaudited_pro_forma')

    def test_only_supported_dated_metric_is_returned(self):
        old=copy.deepcopy(self.result)
        self.assertEqual(requested_balance(self.result,'cash','2026-03-31','illustrative_unaudited_pro_forma'),2484)
        self.assertEqual(self.result,old)

    def test_unverified_source_result_refused(self):
        r=copy.deepcopy(self.result);r['status']='FAILED'
        with self.assertRaises(EvidenceError):requested_balance(r,'cash','2026-03-31','illustrative_unaudited_pro_forma')

    def test_archive_tampering_refused(self):
        b=bytearray((ROOT/'input/original_sec_capture_20261014.zip').read_bytes());b[100]^=1
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'changed.zip';p.write_bytes(b)
            with self.assertRaises(EvidenceError):verify_archive(p)

    def test_wrong_statement_period_refused_even_with_old_intro(self):
        with self.assertRaises(EvidenceError):parse_statement(self.changed('As of March 31, 2026','As of June 30, 2026'))

    def test_wrong_units_refused(self):
        with self.assertRaises(EvidenceError):parse_statement(self.changed('(In millions)','(In thousands)'))

    def test_missing_metric_refused(self):
        with self.assertRaises(EvidenceError):parse_statement(self.changed('Short-term debt','Unrelated liabilities'))

    def test_duplicate_metric_refused(self):
        r=self.row('Short-term debt')
        with self.assertRaises(EvidenceError):parse_statement(self.text.replace(r,r+r,1).encode())

    def test_duplicate_statement_refused(self):
        table=re.search(r'<table\b.*?</table>',self.text,re.S|re.I).group()
        with self.assertRaises(EvidenceError):parse_statement((self.text+table).encode())

    def test_selected_metric_column_span_refused(self):
        r=self.row('Short-term debt');new=r.replace('colspan="3"','colspan="4"',1)
        self.assertNotEqual(new,r)
        with self.assertRaises(EvidenceError):parse_statement(self.text.replace(r,new,1).encode())

    def test_empty_cell_is_not_inferred_zero(self):
        r=self.row('Short-term debt');new=r.replace('&#8212;','',1)
        self.assertNotEqual(new,r)
        with self.assertRaises(EvidenceError):parse_statement(self.text.replace(r,new,1).encode())

    def test_missing_dollar_marker_refused(self):
        r=self.row('Cash and cash equivalents');new=r.replace('$','EUR')
        self.assertNotEqual(new,r)
        with self.assertRaises(EvidenceError):parse_statement(self.text.replace(r,new,1).encode())

    def test_changed_row_arithmetic_refused(self):
        with self.assertRaises(EvidenceError):parse_statement(self.changed('14,764','14,765'))

    def test_balanced_tampering_still_fails_independent_transcription(self):
        raw=self.changed('14,764','14,765').replace(b'2,484',b'2,485',1)
        rows,_,_=parse_statement(raw)
        with self.assertRaises(EvidenceError):compare_transcription(rows,ROOT/'historical_transcribed_rows.csv')

    def test_historical_transcription_missing_duplicate_or_wrong_unit(self):
        with (ROOT/'historical_transcribed_rows.csv').open(newline='') as f:rows=list(csv.DictReader(f))
        parsed,_,_=parse_statement(self.raw)
        cases=[rows[:-1],rows[:-1]+[rows[0]],copy.deepcopy(rows)]
        cases[2][0]['unit']='USD_thousands'
        with tempfile.TemporaryDirectory() as d:
            for i,case in enumerate(cases):
                p=Path(d)/f'case{i}.csv'
                with p.open('w',newline='') as f:
                    w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(case)
                with self.subTest(case=i):
                    with self.assertRaises(EvidenceError):compare_transcription(parsed,p)

    def test_prepaid_fee_source_year_cannot_be_changed(self):
        raw=self.changed('termination fee paid in 2025','termination fee paid in 2024')
        _,_,doc=parse_statement(raw)
        with self.assertRaises(EvidenceError):parse_transaction(doc,self.bodies['original_8k.html'])

    def test_borrowing_must_be_stated_as_borrowed(self):
        raw=self.bodies['original_8k.html'];self.assertIn(b'borrowed',raw)
        _,_,doc=parse_statement(self.raw)
        with self.assertRaises(EvidenceError):parse_transaction(doc,raw.replace(b'borrowed',b'committed'))

    def test_integer_sign_and_nonfinite_controls(self):
        self.assertEqual(number('$ (14,548)'),-14548)
        self.assertEqual(number('—'),0)
        for x in ('','NaN','inf','1.5','True','2(a)','(1','1)'):
            with self.subTest(value=x):
                with self.assertRaises(EvidenceError):number(x)

    def test_typed_reference_rejects_bool_float_missing_and_extra(self):
        for mutation in ('bool','float','missing','extra'):
            r=copy.deepcopy(self.result)
            if mutation=='bool':r['as_if_balance_usd_millions']['cash']=True
            elif mutation=='float':r['as_if_balance_usd_millions']['cash']=2484.0
            elif mutation=='missing':r.pop('transaction')
            else:r['new_claim']=True
            with self.subTest(mutation=mutation):
                with self.assertRaises(EvidenceError):verify_reference(r,self.result)


if __name__=='__main__':unittest.main()
