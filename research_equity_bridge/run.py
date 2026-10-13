"""Isolated registered dated-equity repair, retaining all historical data."""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from src.equity_bridge import Scenario, dated_equity_bridge, weighted_scenarios

SHARES_BN = 0.992327
AS_OF = "2026-09-11"
TERMINAL_DATE = "2028-12-31"
SPOT = 59.06
RATES = (0.08, 0.10, 0.12)
HISTORICAL = (
    "src/model_logic.py", "reference/source_facts.csv", "reference/management_projections.csv",
    "equity_research/model_snapshot.csv", "equity_research/assumptions.csv",
)


def historical_hashes() -> dict:
    return {rel: hashlib.sha256((ROOT / rel).read_bytes()).hexdigest() for rel in HISTORICAL}


def assert_close(actual, expected, name, tolerance=1e-7):
    if not math.isfinite(actual) or not math.isfinite(expected) or not math.isclose(actual, expected, abs_tol=tolerance, rel_tol=tolerance):
        raise ValueError(f"Historical identity mismatch: {name}")


def load_snapshot() -> tuple[list[dict], dict]:
    with (ROOT / "equity_research/model_snapshot.csv").open(newline="") as stream:
        rows = list(csv.DictReader(stream))
    if len(rows) != 4 or [r["scenario"] for r in rows] != ["Bear", "Base", "Bull", "Probability-weighted"]:
        raise ValueError("Frozen snapshot scenario schema changed")
    for row in rows:
        if row["research_snapshot"] != "2026-09-13" or row["market_price_date"] != AS_OF:
            raise ValueError("Frozen snapshot dates changed")
        assert_close(float(row["market_price"]), SPOT, "market price", tolerance=0)
    scenarios = rows[:3]
    for row in scenarios:
        e27, e28 = float(row["2027E_EBITDA_bn"]), float(row["2028E_EBITDA_bn"])
        debt = e27 * float(row["target_net_leverage"])
        equity = e28 * float(row["exit_EV_EBITDA"]) - debt
        price = equity / SHARES_BN
        fcf = e28 * float(row["FCF_conversion_2028"])
        assert_close(equity, float(row["implied_equity_value_bn"]), row["scenario"] + " equity")
        assert_close(price, float(row["target_price"]), row["scenario"] + " price")
        assert_close(price / SPOT - 1, float(row["upside_downside"]), row["scenario"] + " unadjusted price comparison")
        assert_close(fcf, float(row["FCF_bn_2028"]), row["scenario"] + " FCF")
        assert_close(fcf / equity, float(row["FCF_yield"]), row["scenario"] + " FCF yield")
    weighted = math.fsum(float(r["probability"]) * float(r["target_price"]) for r in scenarios)
    assert_close(weighted, float(rows[-1]["target_price"]), "old weighted price")
    assert_close(weighted / SPOT - 1, float(rows[-1]["upside_downside"]), "old weighted comparison")
    assert_close(float(rows[-1]["probability"]), 1.0, "weighted probability", tolerance=0)
    return scenarios, {"status": "PASS", "legacy_price_usd_per_share": weighted,
                       "absolute_plus_relative_tolerance": 1e-7, "original_dates_and_numeric_rows_unchanged": True}


def calculate_summary() -> dict:
    original, historical_check = load_snapshot()
    rate_results = []
    for rate in RATES:
        cases = []
        for row in original:
            scenario = Scenario(row["scenario"], float(row["probability"]), float(row["2028E_EBITDA_bn"]),
                                float(row["exit_EV_EBITDA"]), float(row["target_net_leverage"]))
            case = dated_equity_bridge(scenario, shares_bn=SHARES_BN, as_of=AS_OF, terminal_date=TERMINAL_DATE,
                                       required_equity_return=rate, distributions=(), spot_price=SPOT)
            case["historical_mixed_year_price_usd_per_share"] = float(row["target_price"])
            case["historical_2027_proxy_net_debt_usd_bn"] = float(row["2027E_EBITDA_bn"]) * scenario.net_leverage
            case["terminal_net_debt_increase_vs_old_proxy_usd_bn"] = case["terminal_net_debt_usd_bn"] - case["historical_2027_proxy_net_debt_usd_bn"]
            cases.append(case)
        rate_results.append({"required_equity_return": rate, "cases": cases, "probability_weighted": weighted_scenarios(cases)})
    return {"schema_version": 1, "method_registration": "docs/DATED_EQUITY_BRIDGE_PROTOCOL.md",
            "input": "equity_research/model_snapshot.csv", "historical_identity_replay": historical_check,
            "historical_sha256": historical_hashes(), "as_of": AS_OF, "terminal_date": TERMINAL_DATE,
            "day_count": "ACT/365", "analyst_sensitivity_rates_not_calibrated": list(RATES),
            "distribution_assumption": "Explicitly zero intermediate cash distributions; terminal-only PV, not complete fair value",
            "net_debt_assumption": "Terminal EBITDA times analyst leverage on the same terminal date, not reported/projected cash/debt roll-forward",
            "share_count_assumption": "Fixed June2026 ClassA share proxy, not forecast dilution/buyback",
            "rate_results": rate_results,
            "scope": "Existing frozen scenarios; corrected dated pricing mechanics only. Multiples/rates/debt/shares/probabilities are assumptions. No fresh price, investment recommendation, realized/total return or external validation."}


def compare_reference(actual, reference, path="summary"):
    if type(actual) is not type(reference):
        raise ValueError(f"Reference type changed at {path}")
    if isinstance(actual, float):
        if not math.isfinite(actual) or not math.isclose(actual, reference, abs_tol=1e-10, rel_tol=1e-10):
            raise ValueError(f"Reference numeric mismatch at {path}")
    elif isinstance(actual, dict):
        if actual.keys() != reference.keys():
            raise ValueError(f"Reference keys changed at {path}")
        for key in actual:
            compare_reference(actual[key], reference[key], path + "." + key)
    elif isinstance(actual, list):
        if len(actual) != len(reference):
            raise ValueError(f"Reference length changed at {path}")
        for i, (value, expected) in enumerate(zip(actual, reference)):
            compare_reference(value, expected, path + f"[{i}]")
    elif actual != reference:
        raise ValueError(f"Reference identity changed at {path}")


def run(output: Path) -> dict:
    output = output.resolve()
    if output.exists() or output == ROOT or ROOT in output.parents:
        raise ValueError("Output must be a new nonexistent directory outside the repository")
    before = historical_hashes()
    summary = calculate_summary()
    reference = ROOT / "reference/equity_bridge/summary.json"
    if reference.exists():
        compare_reference(summary, json.loads(reference.read_text()))
    if before != historical_hashes():
        raise ValueError("Historical inputs were mutated")
    output.mkdir(parents=True, exist_ok=False)
    (output / "summary.json").write_text(json.dumps(summary, indent=2, allow_nan=False) + "\n")
    if before != historical_hashes():
        raise ValueError("Historical inputs were mutated")
    return summary


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    arguments = parser.parse_args()
    print("DATED_EQUITY_RESULT_JSON=" + json.dumps(run(arguments.output), allow_nan=False))
