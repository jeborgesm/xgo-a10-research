# GB first materialization — HW result and stem defect closure

Date: 2026-09-23
Branch: `research-refresh-gb-gbc-gba`
Status: HW PARTIAL PASS / next defect statically closed

## Hardware result

Exact Test132 helper plus the one-byte suffix-gate repair at +0x009C:
- Refresh Games -> Game Boy: Games Updated
- wrapper was physically created
- generated filename lost one character immediately before the extension
- generated wrapper was not added to the visible GB list

This is a major boundary advance: directory discovery, .gb acceptance, and wrapper materialization are now hardware-proven to execute.

## Root cause of clipped filename

The exact Test132 helper contains the inherited FC/SFC stem helper at +0x0DCC.

At +0x0DF8 it still contains:
`2441 FFFB` = adjustment -5

That contract removes the four-byte `.xxx` suffix plus the helper's length convention. It is correct for .nes/.sfc, not two-character .gb.

The historical Test102 MD audit already isolated this exact inherited defect and established the two-character correction:
`-5 -> -4`
implemented as one byte at +0x0DF8:
`FB -> FC`.

The GB hardware symptom now independently confirms the same defect: the wrapper is generated, but the basename loses its final character before `.zgb`.

## Combined minimal GB repair

Starting from exact Test132 GB helper SHA:
`00addd59c2b3305e936021bb6cb7c66e03cac334816cd2a61e5c216315e19810`

Change exactly two bytes:
- +0x009C: 05 -> 06 — two-character extension dot geometry
- +0x0DF8: FB -> FC — two-character stem length

Combined candidate SHA:
`34f4714ecbe5affc97b7a0b87726944c253286c3baa3531e437e982174bda238`

No firmware/bisrv.asd change.
No catalog helper change.
No gameplay-path change.

## Catalog observation

The missing visible-list entry is not yet attributed solely to catalog failure because the malformed generated filename/stem is sufficient to invalidate the expected materializer/catalog contract. Retest with the corrected wrapper name first. If the correctly named wrapper is still absent from the list, isolate catalog invocation/merge next.

## Next controlled test

Remove the malformed generated wrapper from this run so it cannot mask the result. Keep the same raw import input and replace only GB/refresh.xgc with the combined two-byte candidate. Invoke GB Refresh once.

Expected materializer artifact: the full original basename followed by `.zgb`, with no clipped final character.
