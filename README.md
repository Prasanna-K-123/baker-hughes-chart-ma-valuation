# Baker Hughes / Chart Industries — M&A Valuation & Fairness Reconstruction

**Status:** Public release. Not affiliated with Baker Hughes, Chart Industries, Bank of America, Wells Fargo, Goldman Sachs, Centerview, Morgan Stanley, or any transaction party/advisor.

## Question

How does Baker Hughes' **$210/share all-cash acquisition of Chart Industries** compare with valuation reference ranges disclosed in Chart's merger proxy, and what do the announced financing and synergy terms imply for merger consequences?

## What this project demonstrates

This is an investment-banking-style public-information case designed around the exact work signals in Bank of America's 2027 Mumbai Global Investment Banking Summer Analyst role:

- transaction overview and purchase-price bridge;
- selected-company valuation reconstruction;
- precedent-transaction analysis;
- independent DCF reconstruction and sensitivity;
- financing / synergy / EPS-accretion sensitivity;
- source mapping and release QA;
- explicit separation of reported facts, derived values and analyst-created assumptions.

## Key transaction facts

- **$210/share** all-cash consideration.
- Approximately **$10.1bn equity value** and **$13.6bn enterprise value**.
- Approximately **30% premium** to Chart's unaffected price before the earlier Flowserve transaction announcement.
- **$325m** expected annualized cost synergies by the end of Year 3.
- Baker Hughes described the transaction as approximately **9x 2025E EBITDA on a fully synergized basis**.
- The acquisition closed on **July 16, 2026**.

## Independent valuation reconstruction

The workbook triangulates:

1. **Selected companies**  
   The Chart proxy identifies the peer set used by Wells Fargo and discloses applied EV/EBITDA ranges of **10x–12x 2025E** and **9x–11x 2026E**. Using the public Chart projections plus an approximate EV-to-equity bridge derived from rounded transaction values, the workbook reconstructs a range of roughly **$166–$221/share**, close to Wells Fargo's disclosed **$168–$223/share** range.

2. **Selected transactions**  
   The proxy identifies ten precedent transactions and discloses an applied **11x–13x LTM EBITDA** range, which produced a Wells Fargo reference range of **$163–$206/share**. The workbook retains the exact disclosed transaction set and derives the approximate LTM EBITDA consistent with those endpoints.

3. **Independent DCF**  
   Chart's proxy discloses management projections through 2030, plus Wells Fargo's **12%–14% discount-rate** and **9x–11x terminal EBITDA multiple** ranges. The exact proprietary banker UFCF build is not public, so this workbook builds a transparent independent UFCF bridge using:
   - 2024 reported D&A / sales;
   - 2024 operating NWC / sales;
   - a normalized 2024 tax rate;
   - disclosed management sales / EBITDA / CapEx projections;
   - 2030 CapEx extended using the 2029 CapEx / sales ratio.

   The resulting sensitivity range is approximately **$165–$224/share**, versus Wells Fargo's disclosed **$171–$230/share** range. The purpose is directional reconstruction, not exact replication.

## Merger consequences

The workbook separately shows:

- announced notes / term-loan funding structure;
- transaction EV / equity / implied net-debt bridge;
- $325m cost-synergy contribution;
- an explicitly illustrative debt-cost / accretion sensitivity.

The accretion analysis is intentionally labeled **simplified / pre-purchase-accounting**. It excludes detailed purchase accounting, one-time transaction costs, commercial synergies and undisclosed tranche-level financing economics.

## Reproducibility

The repository contains a small independent Python reference model and unit tests that recompute the key transaction bridge, selected-company range and DCF reference outputs from structured source facts. The Excel model remains the primary banking work product; the Python layer is a validation aid, not a replacement.

```bash
python -m unittest discover -s tests -v
python -m src.model_logic
```

## Files

- `Baker_Hughes_Chart_MA_Valuation_Model.xlsx` — full model
- `outputs/deal_summary.png` — rendered model summary
- `outputs/dcf_preview.png` — DCF sheet preview
- `outputs/qa_checks.png` — formula-driven release checks
- `reference/` — structured source facts and source register
- `src/model_logic.py` — independent reference calculations
- `tests/` — automated validation tests

## Source discipline

Primary public sources:

1. Bank of America — Mumbai GIB 2027 role  
   https://careers.bankofamerica.com/en-us/students/job-detail/14534/global-investment-banking-summer-analyst-2027-mumbai-mumbai-india

2. Baker Hughes transaction announcement  
   https://investors.bakerhughes.com/news/press-releases/news-details/2025/Baker-Hughes-to-Acquire-Chart-Industries-Accelerating-Energy-Industrial-Technology-Strategy-07-29-2025/default.aspx

3. Chart Industries merger proxy / Wells Fargo fairness analysis  
   https://www.sec.gov/Archives/edgar/data/892553/000119312525191284/d52397dprem14a.htm

4. Chart Industries 2024 Form 10-K  
   https://www.sec.gov/Archives/edgar/data/892553/000089255325000039/gtls-20241231.htm

5. Baker Hughes 2025 Form 10-K  
   https://www.sec.gov/Archives/edgar/data/1701605/000170160526000007/bkr-20251231.htm

6. Baker Hughes Q2 2026 Form 10-Q  
   https://www.sec.gov/Archives/edgar/data/1701605/000170160526000023/bkr-20260630.htm

7. Baker Hughes acquisition completion release  
   https://investors.bakerhughes.com/news/press-releases/news-details/2026/Baker-Hughes-Completes-Acquisition-of-Chart-Industries/default.aspx

## Evidence boundary

- This is **independent public-information research**.
- It is **not** a fairness opinion, investment recommendation, company guidance, or representation of work performed for any transaction party.
- Rounded disclosed transaction values are used to derive approximate net debt and diluted shares.
- Undisclosed banker model inputs are not invented; where an assumption is required, it is visibly labeled as an analyst assumption.
- The project preserves differences between reported facts, derived metrics and illustrative sensitivities.

## QA

The workbook includes a dedicated `QA Checks` sheet. Current release-candidate checks pass for:

- equity value + derived net debt = enterprise value;
- offer price × derived shares = equity value;
- 2024 EBITDA reconstruction from reported components;
- selected-company reconstruction proximity to disclosed fairness range;
- independent DCF overlap with the disclosed DCF range;
- analytical conclusion consistency.

No formula errors were found in the final workbook scan.
