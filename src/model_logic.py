"""Independent public-information validation logic for the Baker Hughes / Chart M&A case.

This module intentionally reproduces only the transparent mechanics disclosed in the
repository. It does not represent Wells Fargo's proprietary fairness-opinion model.
"""
from __future__ import annotations
import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def load_facts():
    out = {}
    with (ROOT / "reference" / "source_facts.csv").open(newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            out[row["key"]] = float(row["value"])
    return out

def load_projections():
    out = {}
    with (ROOT / "reference" / "management_projections.csv").open(newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            out[int(row["year"])] = {
                "sales": float(row["sales_mm"]),
                "ebitda": float(row["ebitda_mm"]),
                "capex": float(row["capex_mm"]) if row["capex_mm"] else None,
            }
    return out

def derived_inputs():
    f = load_facts()
    d_and_a = f["chart_2024_depreciation_mm"] + f["chart_2024_amortization_mm"]
    tax_rate = f["chart_2024_tax_expense_mm"] / f["chart_2024_pretax_income_mm"]
    nwc = (
        f["chart_2024_ar_mm"] + f["chart_2024_inventory_mm"] + f["chart_2024_unbilled_mm"]
        - f["chart_2024_ap_mm"] - f["chart_2024_customer_advances_mm"]
    )
    return {
        "d_and_a_sales": d_and_a / f["chart_2024_sales_mm"],
        "tax_rate": tax_rate,
        "nwc_sales": nwc / f["chart_2024_sales_mm"],
        "net_debt_mm": f["enterprise_value_mm"] - f["equity_value_mm"],
        "diluted_shares_mm": f["equity_value_mm"] / f["offer_price_per_share"],
        "chart_2024_ebitda_mm": f["chart_2024_operating_income_mm"] + d_and_a,
    }

def dcf_value_per_share(wacc=0.13, exit_multiple=10.0):
    f = load_facts()
    p = load_projections()
    di = derived_inputs()
    prev_nwc = (
        f["chart_2024_ar_mm"] + f["chart_2024_inventory_mm"] + f["chart_2024_unbilled_mm"]
        - f["chart_2024_ap_mm"] - f["chart_2024_customer_advances_mm"]
    )
    capex_2030 = p[2030]["sales"] * (p[2029]["capex"] / p[2029]["sales"])
    pv = 0.0
    periods = {2025: 0.5, 2026: 1.5, 2027: 2.5, 2028: 3.5, 2029: 4.5}
    for y in range(2025, 2031):
        sales = p[y]["sales"]
        ebitda = p[y]["ebitda"]
        da = sales * di["d_and_a_sales"]
        ebit = ebitda - da
        nopat = ebit * (1.0 - di["tax_rate"])
        capex = capex_2030 if y == 2030 else p[y]["capex"]
        nwc = sales * di["nwc_sales"]
        delta_nwc = nwc - prev_nwc
        ufcf = nopat + da - capex - delta_nwc
        prev_nwc = nwc
        if y == 2025:
            ufcf *= 0.5
        if y <= 2029:
            pv += ufcf / ((1.0 + wacc) ** periods[y])
    terminal_ev = p[2030]["ebitda"] * exit_multiple
    pv += terminal_ev / ((1.0 + wacc) ** 4.5)
    equity = pv - di["net_debt_mm"]
    return equity / di["diluted_shares_mm"]

def selected_company_range():
    p = load_projections()
    di = derived_inputs()
    lows = []
    highs = []
    for year, low_mult, high_mult in [(2025,10.0,12.0),(2026,9.0,11.0)]:
        lows.append((p[year]["ebitda"] * low_mult - di["net_debt_mm"]) / di["diluted_shares_mm"])
        highs.append((p[year]["ebitda"] * high_mult - di["net_debt_mm"]) / di["diluted_shares_mm"])
    return min(lows), max(highs)

def headline_ev_to_2025e_ebitda():
    f = load_facts()
    p = load_projections()
    return f["enterprise_value_mm"] / p[2025]["ebitda"]

if __name__ == "__main__":
    lo, hi = selected_company_range()
    print(f"Selected-company range: ${lo:.2f} - ${hi:.2f}/share")
    print(f"DCF base: ${dcf_value_per_share():.2f}/share")
    print(f"DCF sensitivity low/high: ${dcf_value_per_share(0.14,9.0):.2f} - ${dcf_value_per_share(0.12,11.0):.2f}/share")
