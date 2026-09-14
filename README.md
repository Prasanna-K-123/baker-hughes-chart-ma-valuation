# Baker Hughes / Chart Industries — M&A Valuation & Post-Close Equity Research

**Status:** Public release. Independent public-information research; not affiliated with Baker Hughes, Chart Industries, or any transaction party/advisor.

## Research questions

1. How does Baker Hughes' **$210/share all-cash acquisition of Chart Industries** compare with valuation reference ranges disclosed in Chart's merger proxy, and what do the announced financing and synergy terms imply for merger consequences?
2. After the acquisition closed, what do current public disclosures imply for Baker Hughes' integration, earnings, leverage, catalysts, risks and equity valuation under explicit bear/base/bull assumptions?

## What this project demonstrates

This is a public-information finance research case spanning transaction analysis and a dated post-close equity-research extension:

- transaction overview and purchase-price bridge;
- selected-company valuation reconstruction;
- precedent-transaction analysis;
- independent DCF reconstruction and sensitivity;
- financing / synergy / merger-consequence sensitivity;
- company / industry research and current-public-source synthesis;
- bear/base/bull scenario valuation, catalysts and risks;
- source mapping and release QA;
- explicit separation of reported facts, management targets, derived values and analyst assumptions.

## Key transaction facts

- **$210/share** all-cash consideration.
- Approximately **$10.1bn equity value** and **$13.6bn enterprise value**.
- Approximately **30% premium** to Chart's unaffected price before the earlier Flowserve transaction announcement.
- **$325m** expected annualized cost synergies by the end of Year 3.
- Baker Hughes described the transaction as approximately **9x 2025E EBITDA on a fully synergized basis**.
- The acquisition closed on **July 16, 2026**.

## Post-close equity research extension

After the acquisition closed, the project was extended into a separate **Baker Hughes (NASDAQ: BKR) post-close equity-research layer** using current public filings, management targets and a fixed market-price snapshot.

At the **11 September 2026 close of $59.06/share**, the independent scenario analysis produced:

- **Bear:** $44.82/share;
- **Base:** $62.65/share;
- **Bull:** $74.73/share;
- **Probability-weighted fair value:** $61.22/share.

The resulting recommendation is **HOLD / NEUTRAL**. The neutral conclusion is retained rather than forcing a bullish thesis: modeled base-case upside is modest and the probability-weighted value is close to the fixed market-price snapshot.

The extension separates core Baker Hughes from Chart and tests integration/margin execution, deleveraging, FCF conversion, catalysts, risks and valuation-multiple sensitivity. The **$325m** cost-synergy target is **not** added on top of management-aligned 2028 margin assumptions, avoiding a double count.

GitHub-native evidence:

- [`equity_research/README.md`](equity_research/README.md) — thesis, scenario valuation, catalysts, risks and evidence boundaries;
- [`equity_research/model_snapshot.csv`](equity_research/model_snapshot.csv) — dated scenario outputs and valuation cross-checks;
- [`equity_research/assumptions.csv`](equity_research/assumptions.csv) — bear/base/bull analyst assumptions;
- [`equity_research/sources.md`](equity_research/sources.md) — primary-source register and fixed market-price source.

## Independent valuation reconstruction

The original transaction workbook triangulates:

1. **Selected companies**  
   The Chart proxy identifies the peer set used by Wells Fargo and discloses applied EV/EBITDA ranges of **10x–12x 2025E** and **9x–11x 2026E**. Using the public Chart projections plus an approximate EV-to-equity bridge derived from rounded transaction values, the workbook reconstructs a range of roughly **$166–$221/share**, close to Wells Fargo's disclosed **$168–$223/share** range.

2. **Selected transactions**  
   The proxy identifies ten precedent transactions and discloses an applied **11x–13x LTM EBITDA** range, which produced a Wells Fargo reference range of **$163–$206/share**. The workbook retains the exact disclosed transaction set and derives the approximate LTM EBITDA consistent with those endpoints.

3. **Independent DCF**  
   Chart's proxy discloses management projections through 2030, plus Wells Fargo's **12%–14% discount-rate** and **9x–11x terminal EBITDA multiple** ranges. The exact proprietary banker UFCF build is not public, so the workbook builds a transparent independent UFCF bridge using:
   - 2024 reported D&A / sales;
   - 2024 operating NWC / sales;
   - a normalized 2024 tax rate;
   - disclosed management sales / EBITDA / CapEx projections;
   - 2030 CapEx extended using the 2029 CapEx / sales ratio.

   The resulting sensitivity range is approximately **$165–$224/share**, versus Wells Fargo's disclosed **$171–$230/share** range. The purpose is directional reconstruction, not exact replication.

## Merger consequences

The original workbook separately shows:

- announced notes / term-loan funding structure;
- transaction EV / equity / implied net-debt bridge;
- $325m cost-synergy contribution;
- an explicitly illustrative debt-cost / accretion sensitivity.

The accretion analysis is intentionally labeled **simplified / pre-purchase-accounting**. It excludes detailed purchase accounting, one-time transaction costs, commercial synergies and undisclosed tranche-level financing economics.

## Reproducibility

The repository contains an independent Python reference model and unit tests that recompute the key original transaction bridge, selected-company range and DCF reference outputs from structured source facts. The Excel model remains the primary M&A work product; the Python layer is a validation aid, not a replacement.

```bash
python -m unittest discover -s tests -v
python -m src.model_logic
```

For the post-close equity-research extension, the public layer is deliberately GitHub-native: scenario outputs, assumption registers and source trails are exposed directly as Markdown/CSV so a recruiter can inspect the thesis without opening a binary model.

## Files

- `Baker_Hughes_Chart_MA_Valuation_Model.xlsx` — original M&A valuation model
- `outputs/deal_summary.png` — rendered transaction-model summary
- `outputs/dcf_preview.png` — DCF sheet preview
- `outputs/qa_checks.png` — formula-driven release checks
- `reference/` — original structured source facts and source register
- `src/model_logic.py` — independent reference calculations for the M&A case
- `tests/` — automated validation tests
- `equity_research/` — post-close BKR equity-research thesis, scenario outputs, assumptions and source register

## Source discipline

Primary public sources:

1. Baker Hughes transaction announcement  
   https://investors.bakerhughes.com/news/press-releases/news-details/2025/Baker-Hughes-to-Acquire-Chart-Industries-Accelerating-Energy--Industrial-Technology-Strategy-07-29-2025/default.aspx

2. Chart Industries merger proxy / Wells Fargo fairness analysis  
   https://www.sec.gov/Archives/edgar/data/892553/000119312525191284/d52397dprem14a.htm

3. Chart Industries 2024 Form 10-K  
   https://www.sec.gov/Archives/edgar/data/892553/000089255325000039/gtls-20241231.htm

4. Baker Hughes 2025 Form 10-K  
   https://www.sec.gov/Archives/edgar/data/1701605/000170160526000007/bkr-20251231.htm

5. Baker Hughes Q2 2026 Form 10-Q  
   https://www.sec.gov/Archives/edgar/data/1701605/000170160526000023/bkr-20260630.htm

6. Baker Hughes acquisition completion release  
   https://investors.bakerhughes.com/news/press-releases/news-details/2026/Baker-Hughes-Completes-Acquisition-of-Chart-Industries/default.aspx

7. Baker Hughes September 2026 investor presentation / SEC Exhibit 99.1  
   https://www.sec.gov/Archives/edgar/data/1701605/000119312526385823/d539011dex991.htm

8. Baker Hughes Q2 2026 results / SEC Exhibit 99.1  
   https://www.sec.gov/Archives/edgar/data/1701605/000170160526000021/earningsreleaseex991063020.htm

9. BKR historical market-price snapshot used by the equity-research extension  
   https://ca.investing.com/equities/baker-hughes-historical-data

## Evidence boundary

- This is **independent public-information research**.
- It is **not** a fairness opinion, investment advice, company guidance, client work or representation of work performed for any transaction party.
- Rounded disclosed transaction values are used to derive approximate net debt and diluted shares in the original M&A reconstruction.
- Undisclosed banker model inputs are not invented; where an assumption is required, it is visibly labeled.
- The post-close recommendation is a **dated analyst scenario output**, not a statement of future return.
- The **$59.06** market price is fixed to the 11 September 2026 close and must be refreshed for later valuation work.
- Post-close growth, target-date leverage, FCF conversion and exit multiples are analyst assumptions; management targets are labeled separately.
- No live portfolio, realized P&L, client mandate or investment authority is claimed.
- The project preserves adverse findings, including the neutral recommendation and bear case.

## QA

The original M&A workbook includes a dedicated `QA Checks` sheet. Current release checks pass for:

- equity value + derived net debt = enterprise value;
- offer price × derived shares = equity value;
- 2024 EBITDA reconstruction from reported components;
- selected-company reconstruction proximity to disclosed fairness range;
- independent DCF overlap with the disclosed DCF range;
- analytical conclusion consistency.

No formula errors were found in the final original M&A workbook scan.

For the post-close extension, the public release preserves the exact dated scenario outputs and assumptions from the independently QA'd research model; the public Markdown/CSV values are checked against that model before release.
