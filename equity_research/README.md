# Baker Hughes Post-Close Equity Research

**Research snapshot:** 13 September 2026  
**Market-price snapshot:** $59.06/share at the 11 September 2026 close  
**Recommendation:** **HOLD / NEUTRAL**

This folder extends the repository's original Baker Hughes / Chart transaction analysis into a post-close Baker Hughes (NASDAQ: BKR) equity-research case. The work is independent public-information research and is **not investment advice**.

## Investment view

Baker Hughes has a credible path to a higher-quality earnings mix through Chart integration, a **22%-23% Chart EBITDA-margin target by 2H28**, **$325m** of annualized cost synergies, and leverage reduction toward **1.0-1.5x**. The central issue is valuation rather than strategic logic: the base case offers only modest upside from the fixed market-price snapshot, while the probability-weighted undiscounted scenario quote remains close to the fixed spot snapshot under the illustrative conventions.

The neutral label is the project's dated illustrative research stance, **not** a valuation-certified investment recommendation. The unadjusted forward quote comparison cannot establish a return forecast. The neutral conclusion is deliberate. The analysis does not force a positive recommendation when the modeled expected return is limited.

## Scenario valuation

| Case | Probability | 2028E EBITDA | Target net leverage | Exit EV/EBITDA | Target price | Upside/(Downside) |
|---|---:|---:|---:|---:|---:|---:|
| Bear | 25% | $6.22bn | 2.00x | 9.0x | $44.82 | (24.1%) |
| Base | 50% | $6.97bn | 1.75x | 10.5x | $62.65 | 6.1% |
| Bull | 25% | $7.34bn | 1.55x | 11.5x | $74.73 | 26.5% |
| **Probability-weighted** | **100%** |  |  |  | **$61.22** | **3.7%** |

The share-count proxy is **992.327m Class A shares outstanding at 30 June 2026**, taken from Baker Hughes' Q2 2026 Form 10-Q.

**Valuation-basis clarification (audited 12 October 2026):** Each displayed scenario is an **undiscounted, mixed-year forward scenario proxy**, not a present fair-value estimate. Reproduced directly from the frozen `model_snapshot.csv` values, the identity is:

`implied_equity_value_bn = 2028E_EBITDA_bn × exit_EV_EBITDA − 2027E_EBITDA_bn × target_net_leverage`; `scenario_value_per_share = implied_equity_value_bn / 0.992327bn shares`.

The Base calculation is `6.9682243920 × 10.5 − 6.2821731065 × 1.75 = 62.1725531796` **USD bn**, or **$62.6533/share**. This mixes a **2028 enterprise-value numerator** with a **2027 EBITDA proxy for net debt**. The original record does not establish a common explicit valuation target date, debt roll-forward to that date, discounting of the exit price to 11 September 2026, share-count roll-forward, or dividends. The stated $61.22 probability-weighted value is only a probability-weighted **scenario quote under these conventions**; comparing it to the September 2026 spot price does not produce a validated investment horizon return, annualized upside or contemporaneous intrinsic value. No historical result has been recomputed, retuned or relabelled as a newly executed valuation. Scenario growth, margins, target-date leverage, FCF conversion and valuation multiples are analyst assumptions rather than company guidance.

## Variant perception

- Chart improves Baker Hughes' industrial exposure, aftermarket opportunity and earnings mix, but the valuation only becomes compelling if integration execution is better or faster than the base case.
- The base case deliberately **does not add the $325m synergy target on top of management-aligned 2028 margin assumptions**, avoiding a double count.
- The 10-11 September sell-off reduced valuation risk versus the pre-sell-off level, but it did not by itself create a large expected return under the stated assumptions.
- The **HOLD / NEUTRAL** recommendation is retained rather than manufacturing a bullish thesis; the $44.82 bear case remains material.

## Forecast framework

The analysis separates Baker Hughes ex-Chart from Chart to keep the integration bridge visible. FY2026 midpoint guidance is split by subtracting management's partial-year Chart contribution from total guidance; Chart's 16 July-31 December contribution is annualized only as a run-rate anchor and is not presented as company guidance.

| Metric | 2026E run-rate | Bear 2028E | Base 2028E | Bull 2028E |
|---|---:|---:|---:|---:|
| Core BKR revenue | $27.35bn | $27.90bn | $29.30bn | $30.15bn |
| Core EBITDA margin | 17.6% | 19.0% | 20.0% | 20.5% |
| Chart revenue | $4.43bn | $4.61bn | $4.93bn | $5.02bn |
| Chart EBITDA margin | 17.1% | 20.0% | 22.5% | 23.0% |
| Combined EBITDA | $5.58bn | $6.22bn | $6.97bn | $7.34bn |

## Catalysts

- Chart EBITDA-margin progression toward the published **22%-23% by 2H28** target with visible integration and cost-synergy milestones.
- IET/LNG/data-center order conversion from a large RPO base and continued services growth.
- Deleveraging toward **1.0-1.5x**, restoring greater capital-allocation flexibility.
- Portfolio optimization, asset-sale proceeds and cross-selling across the Baker Hughes and Chart installed bases.

## Risks

- Integration or synergy delay; Chart margins fail to approach the published 2H28 target.
- LNG project timing, soft hydrogen demand or first-of-a-kind project pressure persists into 2027.
- OFSE activity weakens and margin resilience deteriorates.
- Higher leverage, interest expense or integration cash costs delay FCF conversion and debt reduction.
- Multiple compression offsets operating progress even if execution meets expectations.

## What would change the view

**Upgrade toward BUY:** evidence that Chart margins and synergies are tracking ahead of schedule, leverage declines faster than the base case, and IET conversion supports above-base growth without sacrificing margins.

**Downgrade toward SELL:** integration slippage, a persistent sub-20% core margin path, material FCF shortfall, or a leverage trajectory inconsistent with the published target.

## GitHub-native evidence

- [`model_snapshot.csv`](model_snapshot.csv) - dated scenario outputs and valuation cross-checks.
- [`assumptions.csv`](assumptions.csv) - bear/base/bull analyst assumptions.
- [`sources.md`](sources.md) - primary-source register and the fixed market-price source.

The public layer is intentionally text-native so the thesis, assumptions, adverse case and source trail are inspectable directly in GitHub.

## Evidence boundary

- Independent public-information research; not investment advice.
- No live portfolio, realized P&L, client mandate, proprietary information or investment authority is claimed.
- Reported facts, management targets, derived values and analyst assumptions are separated.
- The recommendation is a **dated scenario-model output** and can be wrong.
- The **$59.06** market price is fixed to the 11 September 2026 close; later market moves require an explicit refresh.
- The analysis preserves adverse cases and does not treat management targets as guaranteed outcomes.

## Separately registered common-date repair — 13 October 2026

The dated original table is preserved above. The new [review and full result](../docs/DATED_EQUITY_BRIDGE_REVIEW.md) explicitly uses 31 December2028 terminal EV and a same-date target-net-debt assumption. It discounts equity cash flows to the frozen 11 September2026 price date with ACT/365 and explicit illustrative equity rates. No original numeric CSV or original M&A DCF is changed.

Common-date Bear/Base/Bull terminal quotes are $43.89/$61.44/$73.56. Their weighted $60.08 terminal quote is **not** a current fair value. At10% with an explicitly empty distribution schedule, weighted terminal-only PV is $48.23 (18.35% below the frozen spot). At8%/12% it is $50.31/$46.26. The adverse effect of the date/debt correction is retained. Company dividends, sourced debt/cash roll-forward, share dilution and calibrated discount rates are not supplied by this partial scenario model; the original HOLD/NEUTRAL stance remains historical rather than silently becoming a new recommendation.

Reproduce with `python research_equity_bridge/run.py --output /tmp/bkr-dated-equity-new` after the unit checks, using a new output directory outside the repository. The runner reproduces all old price/equity/FCF identities, preserves historical hashes and compares the full newly registered reference with exact schema/type identities plus1e-10 float tolerance.
