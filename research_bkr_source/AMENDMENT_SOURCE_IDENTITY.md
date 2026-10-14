# Source-identity amendment — 14 October 2026

The initial capture atbe4b71c1ddff25b47857a43d4dd70d6aef2caf4e failed in
run38529270305 at the literal issuer-name check. Original source integrity and
the existing financial-reference workflow remained separate; the latter passed.

Diagnostic commit902965908852c10415c3b88a3262e74b740268d3 retained the exact
HTTP200 submissions response before semantic validation, without relaxing any
identity or transport control. Its run38532083119 explicitly failed the same
name check. The original diagnostic ZIP/artifact11878069192, all CRCs and the
submissions-body digest were checked independently.

That original SEC body reports CIK0001701605, name **Baker Hughes Co**, tickerBKR,
and both registered accessions/forms/report dates/primary filenames. The filing
text's legal name is Baker Hughes Company. The API alias difference is a parser
assumption error, not a source disagreement or access-control failure.

The revised check permits exactly those two normalized names, retains the exact
CIK and accession/date/document checks, and adds a requiredBKR ticker check.
Body/URL/status/cutoff/rate/redirect controls remain unchanged. Failed captures
remain failed; only a separately successful complete four-body capture can support
downstream source reconciliation. No financial expected value or scenario changes.
