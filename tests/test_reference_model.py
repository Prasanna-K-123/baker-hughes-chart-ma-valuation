import unittest
from src.model_logic import derived_inputs, dcf_value_per_share, selected_company_range, headline_ev_to_2025e_ebitda

class TestReferenceModel(unittest.TestCase):
    def test_2024_ebitda_reconstruction(self):
        self.assertAlmostEqual(derived_inputs()["chart_2024_ebitda_mm"], 917.4, places=6)

    def test_transaction_bridge(self):
        di = derived_inputs()
        self.assertAlmostEqual(di["net_debt_mm"], 3500.0, places=6)
        self.assertAlmostEqual(di["diluted_shares_mm"], 10100.0 / 210.0, places=6)

    def test_selected_companies_close_to_disclosed_endpoints(self):
        lo, hi = selected_company_range()
        self.assertLessEqual(abs(lo - 167.63), 3.0)
        self.assertLessEqual(abs(hi - 223.06), 3.0)

    def test_dcf_base(self):
        self.assertAlmostEqual(dcf_value_per_share(0.13, 10.0), 193.74, delta=0.10)

    def test_dcf_sensitivity_overlaps_disclosed_range(self):
        lo = dcf_value_per_share(0.14, 9.0)
        hi = dcf_value_per_share(0.12, 11.0)
        self.assertLess(lo, 229.77)
        self.assertGreater(hi, 171.32)

    def test_headline_multiple(self):
        self.assertAlmostEqual(headline_ev_to_2025e_ebitda(), 13600.0 / 1146.0, places=6)

if __name__ == "__main__":
    unittest.main()
