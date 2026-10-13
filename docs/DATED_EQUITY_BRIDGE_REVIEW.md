# Dated equity scenario bridge — execution review

A price measured in late 2028 is not a value measured in September 2026. The original extension also deducted a debt proxy based on 2027 EBITDA from enterprise value based on 2028 EBITDA. This separate repair keeps the original September CSV intact and makes both dates and assumptions explicit.

The method was registered at `3d91f319fe818307ed7135a842a6b49e7d614983` before the new scenario calculation. An inaccessible secondary method link was removed at `50641c72fb290a4ca6cb36e86bb58a592d86d8e6`; dates, scenarios, rates and criteria were unchanged. The independently read NYU terminal-value note distinguishes multiple-based terminal pricing from intrinsic valuation. Our result is a conditional pricing scenario, not certified fair value.

## Convention and complete evidence

- As-of: fixed 11 September 2026 market-price snapshot, $59.06; no market refresh.
- Terminal date: 31 December 2028; 842 days / 365 = 2.3068493151 years.
- Enterprise value and target-net-debt proxy both use 2028 EBITDA. Debt is EBITDA times the existing leverage assumption, not a sourced debt/cash roll-forward.
- Shares: constant 0.992327 billion ClassA June2026 proxy; future buybacks/dilution are not modeled.
- Required return on equity: explicit 8%,10%,12% sensitivity assumptions, not calibrated rates and not WACC.
- Distributions: explicitly zero in this registered run. Terminal equity alone is discounted; intermediate dividends are absent. The engine separately supports explicitly dated supplied distributions, checked with a closed-form fixture.
- Complete machine-readable run: [`summary.json`](../reference/equity_bridge/summary.json). Original scenario CSV, assumption CSV, source facts, projections and original transaction-model source are hashed before/after and remain byte-identical.

## Results, including the adverse comparison

| Case | Preserved mixed-year quote | Common-date terminal quote | Terminal-only PV at10% | PV versus frozen spot | Price-only annualized change |
|---|---:|---:|---:|---:|---:|
| Bear | $44.82 | $43.89 | $35.23 | −40.36% | −12.08% |
| Base | $62.65 | $61.44 | $49.32 | −16.50% | 1.73% |
| Bull | $74.73 | $73.56 | $59.04 | −0.03% | 9.99% |
| Probability-weighted | $61.22 | $60.08 | $48.23 | −18.35% | 0.75% from weighted terminal price |

Weighted terminal-only PV is $50.31 / $48.23 / $46.26 at8% /10% /12%. The 0.75% annualized change obtained from the weighted terminal price differs from the probability-weighted mean case annualized change of0.34%; the transformation is nonlinear. Both appear in the full result with distinct labels. These are price-only conditional summaries, not expected total returns. A weighted mean price alone is not evidence of a risk-adjusted recommendation.

No positive conclusion is forced: incorporating the explicit horizon and common-date debt proxy reduces the legacy comparison materially. The old HOLD/NEUTRAL stance stays historical; this partial zero-distribution calculation does not establish a fresh buy/sell decision or complete intrinsic value. Debt financing, dividends, dilution, cost-of-equity calibration, scenario probabilities and multiple appropriateness require a larger sourced financial model before such a claim.

## Reproduction and checks

```bash
python -m unittest discover -s tests -v
python research_equity_bridge/run.py --output /tmp/bkr-dated-equity-new
```

Use a new nonexistent output directory outside the repository. Python3.12, standard library only. Historical CSV identities are independently reproduced within the preregistered1e-7 absolute/relative tolerance. New full reference replay uses1e-10 for finite floats and exact type/schema/text/count/file-hash identities. Six original transaction-model tests plus16 new substantive checks passed locally; they cover closed-form same-date debt, dated distributions, leap-date/time/scale invariance, discount monotonicity, invalid inputs/weights/dates, negative-equity refusal, nonlinear weighted summaries, typed-reference corruption and refusal to overwrite evidence. The source workflow repeats these checks and the registered result replay.

The existing baseline release had a stale equity README size/hash in `MANIFEST.json`; matching-head main run38285902741 failed at that integrity step before any model test. The manifest is now updated for the intentionally changed current docs and extended with source/result identities; original binary and frozen-input hashes are retained. That old failure remains in CI history.
