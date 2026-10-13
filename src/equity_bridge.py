"""Explicit-date scenario pricing, with equity cash-flow discounting.

This is a conditional analyst scenario, not calibrated intrinsic valuation.
The original transaction model and mixed-year evidence remain separate.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import date
import math
from numbers import Real


def finite_number(value: Real, name: str) -> float:
    if isinstance(value, bool) or not isinstance(value, Real):
        raise ValueError(f"{name} must be a finite number")
    result = float(value)
    if not math.isfinite(result):
        raise ValueError(f"{name} must be finite")
    return result


def iso_date(value: str, name: str) -> date:
    if not isinstance(value, str):
        raise ValueError(f"{name} must be an ISO date YYYY-MM-DD")
    try:
        result = date.fromisoformat(value)
    except ValueError as error:
        raise ValueError(f"{name} must be an ISO date YYYY-MM-DD") from error
    if result.isoformat() != value:
        raise ValueError(f"{name} must be an ISO date YYYY-MM-DD")
    return result


@dataclass(frozen=True)
class Scenario:
    name: str
    probability: float
    ebitda_bn: float
    exit_multiple: float
    net_leverage: float

    def __post_init__(self):
        if not isinstance(self.name, str) or not self.name.strip():
            raise ValueError("Scenario name is required")
        values = {key: finite_number(getattr(self, key), key) for key in
                  ("probability", "ebitda_bn", "exit_multiple", "net_leverage")}
        if not 0 <= values["probability"] <= 1:
            raise ValueError("probability must be in [0,1]")
        if values["ebitda_bn"] <= 0 or values["exit_multiple"] < 0 or values["net_leverage"] < 0:
            raise ValueError("EBITDA must be positive; multiple and net leverage nonnegative")
        if values["exit_multiple"] < values["net_leverage"]:
            raise ValueError("Negative residual equity: this pricing model does not floor or price insolvent equity")


@dataclass(frozen=True)
class Distribution:
    date: str
    usd_per_share: float

    def __post_init__(self):
        iso_date(self.date, "distribution date")
        if finite_number(self.usd_per_share, "distribution") < 0:
            raise ValueError("Distributions must be nonnegative; capital calls are outside this model")


def dated_equity_bridge(scenario: Scenario, *, shares_bn: float,
                        as_of: str, terminal_date: str, required_equity_return: float,
                        distributions: tuple[Distribution, ...], spot_price: float) -> dict:
    """Price one terminal equity scenario and explicitly dated cash distributions.

    EBITDA/debt/EV units are USD billion; shares are billion, so prices are USD/share.
    The equity required return is annual effective and ACT/365 is used throughout.
    An empty distribution schedule is an explicit zero-distribution assumption.
    """
    if not isinstance(scenario, Scenario):
        raise ValueError("scenario must be a validated Scenario")
    shares = finite_number(shares_bn, "shares_bn")
    spot = finite_number(spot_price, "spot_price")
    rate = finite_number(required_equity_return, "required_equity_return")
    if shares <= 0 or spot <= 0:
        raise ValueError("Shares and spot price must be positive")
    if rate <= -1:
        raise ValueError("Annual effective required equity return must exceed -1")
    start = iso_date(as_of, "as_of")
    end = iso_date(terminal_date, "terminal_date")
    if end < start:
        raise ValueError("Terminal date precedes as-of date")
    if not isinstance(distributions, tuple) or any(not isinstance(x, Distribution) for x in distributions):
        raise ValueError("distributions must be an explicit tuple of Distribution records")
    payout_dates = [x.date for x in distributions]
    if len(set(payout_dates)) != len(payout_dates):
        raise ValueError("Combine same-day distributions explicitly; duplicate dates refused")
    days = (end - start).days
    years = days / 365.0
    terminal_ev = float(scenario.ebitda_bn) * float(scenario.exit_multiple)
    terminal_net_debt = float(scenario.ebitda_bn) * float(scenario.net_leverage)
    terminal_equity = terminal_ev - terminal_net_debt
    terminal_price = terminal_equity / shares
    try:
        terminal_discount = math.exp(-years * math.log1p(rate))
        pv_terminal = terminal_price * terminal_discount
        pv_distributions = 0.0
        payout_records = []
        for payout in sorted(distributions, key=lambda x: x.date):
            payout_date = iso_date(payout.date, "distribution date")
            if not start <= payout_date <= end:
                raise ValueError("Distribution date lies outside the valuation horizon")
            payout_years = (payout_date - start).days / 365.0
            pv = float(payout.usd_per_share) * math.exp(-payout_years * math.log1p(rate))
            pv_distributions += pv
            payout_records.append({"date": payout.date, "usd_per_share": float(payout.usd_per_share), "pv_usd_per_share": pv})
        price_only_annualized_change = ((terminal_price / spot) ** (1.0 / years) - 1.0) if years > 0 else None
    except (OverflowError, ZeroDivisionError) as error:
        raise ValueError("Inputs produce a nonfinite discount or price calculation") from error
    numeric_outputs = [terminal_ev, terminal_net_debt, terminal_equity, terminal_price,
                       terminal_discount, pv_terminal, pv_distributions]
    if price_only_annualized_change is not None:
        numeric_outputs.append(price_only_annualized_change)
    if not all(math.isfinite(x) for x in numeric_outputs):
        raise ValueError("Inputs produce a nonfinite price calculation")
    pv = pv_terminal + pv_distributions
    if not math.isfinite(pv):
        raise ValueError("Present value is not finite")
    return {
        "scenario": scenario.name, "probability": float(scenario.probability),
        "as_of": as_of, "terminal_date": terminal_date, "elapsed_days": days,
        "year_fraction_act365": years, "required_equity_return": rate,
        "shares_bn_constant_proxy": shares,
        "terminal_ev_usd_bn": terminal_ev, "terminal_net_debt_usd_bn": terminal_net_debt,
        "terminal_equity_usd_bn": terminal_equity, "terminal_usd_per_share": terminal_price,
        "pv_terminal_usd_per_share": pv_terminal, "pv_distributions_usd_per_share": pv_distributions,
        "pv_equity_cashflows_usd_per_share": pv, "spot_comparison_usd_per_share": spot,
        "pv_minus_spot_fraction": pv / spot - 1.0,
        "price_only_annualized_change": price_only_annualized_change,
        "distributions": payout_records,
        "scope": "Conditional terminal-multiple equity pricing; explicit target debt/share/return assumptions; not calibrated intrinsic fair value or a total return forecast",
    }


def weighted_scenarios(rows: list[dict]) -> dict:
    if not rows:
        raise ValueError("No scenarios to aggregate")
    names = [row["scenario"] for row in rows]
    if len(set(names)) != len(names):
        raise ValueError("Duplicate scenario names")
    probabilities = [finite_number(row["probability"], "probability") for row in rows]
    if any(not 0 <= p <= 1 for p in probabilities) or not math.isclose(sum(probabilities), 1.0, abs_tol=1e-12, rel_tol=0):
        raise ValueError("Scenario probabilities must be in [0,1] and sum to one")
    for key in ("as_of", "terminal_date", "required_equity_return", "shares_bn_constant_proxy",
                "spot_comparison_usd_per_share", "distributions"):
        if any(row[key] != rows[0][key] for row in rows):
            raise ValueError(f"Scenarios have different {key}")
    def average(key):
        return math.fsum(p * finite_number(row[key], key) for p, row in zip(probabilities, rows))
    terminal_price = average("terminal_usd_per_share")
    years = finite_number(rows[0]["year_fraction_act365"], "year_fraction_act365")
    spot = finite_number(rows[0]["spot_comparison_usd_per_share"], "spot_comparison_usd_per_share")
    # Transforming the weighted price is not averaging the individual nonlinear CAGRs.
    annualized_weighted_price = (terminal_price / spot) ** (1.0 / years) - 1.0 if years > 0 else None
    mean_case_annualized = average("price_only_annualized_change") if years > 0 else None
    return {"scenario": "Probability-weighted", "probability": 1.0,
            "terminal_usd_per_share": terminal_price,
            "pv_equity_cashflows_usd_per_share": average("pv_equity_cashflows_usd_per_share"),
            "pv_minus_spot_fraction": average("pv_equity_cashflows_usd_per_share") / spot - 1.0,
            "annualized_change_from_weighted_terminal_price": annualized_weighted_price,
            "weighted_mean_case_annualized_change": mean_case_annualized}
