import copy
from datetime import date
import math
from pathlib import Path
import tempfile
import unittest

from src.equity_bridge import Scenario, Distribution, dated_equity_bridge, weighted_scenarios
from research_equity_bridge.run import compare_reference, historical_hashes, run, ROOT


class EquityBridgeTests(unittest.TestCase):
    def fixture(self, **updates):
        inputs = dict(scenario=Scenario("Fixture", 1.0, 10, 5, 1), shares_bn=2.0,
                      as_of="2025-01-01", terminal_date="2026-01-01",
                      required_equity_return=0.10, distributions=(), spot_price=20.0)
        inputs.update(updates)
        return dated_equity_bridge(**inputs)

    def test_closed_form_equity_after_same_date_debt(self):
        row = self.fixture()
        self.assertEqual(row["terminal_ev_usd_bn"], 50)
        self.assertEqual(row["terminal_net_debt_usd_bn"], 10)
        self.assertEqual(row["terminal_usd_per_share"], 20)
        self.assertAlmostEqual(row["pv_terminal_usd_per_share"], 20 / 1.1)

    def test_zero_debt_fixture(self):
        self.assertEqual(self.fixture(scenario=Scenario("No debt", 1, 10, 5, 0))["terminal_equity_usd_bn"], 50)

    def test_discount_dividends_at_own_dates(self):
        row = self.fixture(terminal_date="2027-01-01", distributions=(Distribution("2026-01-01", 2.0),))
        self.assertAlmostEqual(row["pv_equity_cashflows_usd_per_share"], 20 / 1.1**2 + 2 / 1.1)
        self.assertEqual(row["distributions"][0]["date"], "2026-01-01")

    def test_zero_rate_and_same_day(self):
        self.assertEqual(self.fixture(required_equity_return=0)["pv_terminal_usd_per_share"], 20)
        row = self.fixture(terminal_date="2025-01-01", distributions=(Distribution("2025-01-01", 1),))
        self.assertEqual(row["pv_equity_cashflows_usd_per_share"], 21)
        self.assertIsNone(row["price_only_annualized_change"])

    def test_day_count_includes_leap_day(self):
        row = self.fixture(as_of="2024-01-01", terminal_date="2025-01-01")
        self.assertEqual(row["elapsed_days"], 366)
        self.assertAlmostEqual(row["pv_terminal_usd_per_share"], 20 / 1.1**(366 / 365))

    def test_time_translation_invariance(self):
        self.assertEqual(self.fixture()["pv_terminal_usd_per_share"],
                         self.fixture(as_of="2026-01-01", terminal_date="2027-01-01")["pv_terminal_usd_per_share"])

    def test_currency_scale_invariance(self):
        self.assertEqual(self.fixture(scenario=Scenario("Scaled", 1, 100, 5, 1), shares_bn=20)["terminal_usd_per_share"], 20)

    def test_discount_monotonicity(self):
        values = [self.fixture(required_equity_return=rate)["pv_terminal_usd_per_share"] for rate in (0, .08, .10, .12)]
        self.assertEqual(values, sorted(values, reverse=True))

    def test_negative_rate_within_domain(self):
        self.assertAlmostEqual(self.fixture(required_equity_return=-.1)["pv_terminal_usd_per_share"], 20 / .9)

    def test_bad_numbers_domains_and_negative_equity_refused(self):
        for field in ("shares_bn", "spot_price", "required_equity_return"):
            for value in (float("nan"), float("inf"), True, "1"):
                with self.subTest(field=field, value=value), self.assertRaises(ValueError):
                    self.fixture(**{field: value})
        for field in ("shares_bn", "spot_price"):
            for value in (0, -1):
                with self.assertRaises(ValueError): self.fixture(**{field: value})
        for rate in (-1, -2):
            with self.assertRaises(ValueError): self.fixture(required_equity_return=rate)
        for values in [("Bad", 1, 0, 5, 1), ("Bad", 1, 1, 1, 2), ("Bad", 1.1, 1, 2, 1)]:
            with self.assertRaises(ValueError): Scenario(*values)

    def test_invalid_dates_and_distribution_schedule_refused(self):
        for date_value in ("2026-02-30", "20260101", "bad", 123):
            with self.assertRaises(ValueError): self.fixture(terminal_date=date_value)
        with self.assertRaises(ValueError): self.fixture(terminal_date="2024-12-31")
        for schedule in ((Distribution("2024-12-31", 1),), (Distribution("2026-01-02", 1),),
                         (Distribution("2025-06-01", 1), Distribution("2025-06-01", 2))):
            with self.assertRaises(ValueError): self.fixture(distributions=schedule)
        with self.assertRaises(ValueError): Distribution("2026-01-01", -1)
        with self.assertRaises(ValueError): self.fixture(distributions=[])

    def test_weighted_prices_and_nonlinear_annualized_summaries(self):
        rows = [self.fixture(scenario=Scenario("Low", .5, 10, 4, 1), terminal_date="2027-01-01"),
                self.fixture(scenario=Scenario("High", .5, 10, 8, 1), terminal_date="2027-01-01")]
        result = weighted_scenarios(rows)
        self.assertEqual(result["terminal_usd_per_share"], 25)
        self.assertAlmostEqual(result["annualized_change_from_weighted_terminal_price"], math.sqrt(25 / 20) - 1)
        self.assertNotEqual(result["annualized_change_from_weighted_terminal_price"], result["weighted_mean_case_annualized_change"])

    def test_bad_weights_duplicates_and_horizons_refused(self):
        with self.assertRaises(ValueError): weighted_scenarios([])
        with self.assertRaises(ValueError): weighted_scenarios([self.fixture(), self.fixture()])
        rows = [self.fixture(scenario=Scenario("A", .4, 10, 5, 1)), self.fixture(scenario=Scenario("B", .4, 10, 5, 1))]
        with self.assertRaises(ValueError): weighted_scenarios(rows)
        rows[0]["probability"] = rows[1]["probability"] = .5
        rows[1]["terminal_date"] = "2027-01-01"
        with self.assertRaises(ValueError): weighted_scenarios(rows)

    def test_input_records_not_mutated(self):
        rows = [self.fixture()]
        before = copy.deepcopy(rows)
        weighted_scenarios(rows)
        self.assertEqual(rows, before)

    def test_reference_type_and_numeric_corruption_refused(self):
        compare_reference({"version": 1, "value": 2.0}, {"version": 1, "value": 2.0})
        for wrong in ({"version": True, "value": 2.0}, {"version": 1, "value": float("nan")}, {"version": 1, "value": 2.1}):
            with self.assertRaises(ValueError): compare_reference(wrong, {"version": 1, "value": 2.0})

    def test_existing_or_repository_outputs_refused_before_calculation(self):
        before = historical_hashes()
        with tempfile.TemporaryDirectory() as temporary:
            with self.assertRaises(ValueError): run(Path(temporary))
        for path in (ROOT, ROOT / "reference/new-output", ROOT / "equity_research/new-output"):
            with self.assertRaises(ValueError): run(path)
        self.assertEqual(historical_hashes(), before)


if __name__ == "__main__": unittest.main()
