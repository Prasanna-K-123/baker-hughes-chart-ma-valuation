# Original BKR source reconciliation — 14 October 2026

The existing rendered-source arithmetic now has an executed original-response
reproduction. Four genuine SEC bodies are preserved, hashed and checked; a
dependency-free HTML parser binds the actual statement heading, date, columns
and four row labels, then independently compares all20 financial cells with the
earlier frozen transcription. All20 match. This is supporting research within
the existing portfolio, with no new flagship or investment recommendation.

## What the sources establish

All amounts below are displayed USD millions; equality is at that display
precision, not a claim to underlying dollar-level accuracy.

| March31,2026 AS-IF row | BKR historic | Chart adjusted | Transaction | Financing | Combined |
|---|---:|---:|---:|---:|---:|
| Cash |14764|268|-14548|2000|2484|
| Short-term debt |753|0|0|0|753|
| Long-term debt |15411|3808|-3808|2000|17411|
| Total assets |50896|9692|-6374|2000|56214|

Displayed gross debt18164 and simple net debt15680 follow from those AS-IF rows.
The parser treats a displayed dash as zero under this statement convention and
refuses a missing cell. It excludes adjacent footnote columns; it does not infer
an absent legal/security category as zero.

The purchase consideration table totals14806: cash for shares10054, Chart debt
payoff4451, a258 termination fee and43 for stock-based awards. The source says
the258 fee was already paid in2025. New cash uses therefore total14548, which
matches the cash adjustment. Do not double-count that prepayment. July's4451
debt payoff also differs from the March3808 historic Chart debt removed in the
AS-IF balance-sheet column.

The original8-K confirms2000 actually borrowed, rather than merely committed.
The pro forma note explicitly identifies **15July2026** term-loan drawdown;
**16July** is the acquisition closing and original report date. **1October** is
the amendment filing date. Earlier shorthand identifying a July16 loan draw
must be read with this correction; the historic numerical models are preserved.

## Acquisition and validation history

The source-extension protocol was registered at
`83d8ed63e69bfcb7aafb422fd5e00ed9bb975e54` before acquisition. The first capture
failed a literal Company-versus-Co issuer-name assumption. A second explicit
failed diagnostic preserved the authentic submissions body. The recorded
[identity amendment](../research_bkr_source/AMENDMENT_SOURCE_IDENTITY.md) permits
exactly the observed alias and the filing's legal name, retains the CIK and
registered accession/date/document checks and adds tickerBKR. Neither failed
capture is relabelled as success; no transport/security bypass or financial
expected-value amendment occurred.

The full successful capture is run38532791635 at
`91ac63f1dfa0f5aa2e04147eb47ea26674969dc3`, artifact11878213996. Its ZIP digest,
CRC and all four original-body digests were independently verified locally.

There are40 new consequential source/metadata/corruption/refusal controls plus
the22 unchanged original tests: **62 local tests pass with warnings as errors**.
An initial negative test incorrectly tried to remove a literal dash when the
source stored an HTML entity; that fixture was corrected without changing the
financial data or acceptance contract. Typed full-reference replay passes.
Remote release/matching-main status must be read from the actual workflow runs,
not inferred from these local checks.

## Reproduce without network access

Python3.12 and its standard library suffice; no live SEC request or third-party
Python package is needed for the pinned replay.

```bash
python -W error -m unittest discover -s tests -v
python -W error -m research_bkr_source.run --output /tmp/bkr-original-source --verify-reference
```

The output path must be new and outside the source repository. The exact pinned
archive and reference are checked, and source/default model files are not
rewritten. A future new acquisition requires the declared request identity and
the documented bounded capture workflow; do not silently replace this snapshot.

## What remains open

The14October submissions capture's latest10-Q is the30June2026 pre-close report,
filed27July. The issuer currently schedules Q3 results for27October. This source
snapshot therefore does not supply a post-close actual Q3 balance sheet. The
AS-IF figures cannot replace actual July/September data or a2028 debt/cash input.
Unsupported basis/date/fair-value requests are explicitly refused.

No new debt/cash/share/dividend forecast, calibrated cost of equity, current
market valuation, legal/accounting certification, analyst endorsement or client
result follows. Original workbook, source models, dated equity bridge and
scenario inputs/outputs are preserved. Applications/outreach/reviewer sharing
remain HOLD; no scientific or whole-stage completion percentage is asserted.
