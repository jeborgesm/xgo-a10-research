# Test125 hardware FAIL — cross-family catalog corruption

Date: 2026-09-22
Branch: `research-refresh-gb-gbc-gba`
Candidate ZIP SHA-256:
`f3e4498237bb7c191b02581f7e0db2aa6bc1d03ed76ada1ed32ba5f22f0b1d12`

Status: **HW FAIL — DO NOT PROMOTE / DO NOT REUSE AS HANDHELD BASELINE**

## Hardware observations

Test sequence and observed result:

1. Refresh -> Game Boy:
   - returned **Games Updated** unexpectedly;
   - GB list subsequently showed no new visible entries;
   - previously added GB games remained present and playable.

2. Refresh -> Game Boy Color:
   - returned **No New Games**;
   - no pending GBC game appeared.

3. Refresh -> Game Boy Advance:
   - returned **No New Games**;
   - GBA list was nevertheless populated with games originating from the GB
     catalog;
   - those cross-listed GB games did not launch from GBA.

4. Refresh -> Classic:
   - returned **No New Games** rather than the expected independent CLASSIC
     behavior/status.

## What this disproves

Test125 does **not** prove selective Test08 semantics.  The helper/descriptor
reconstruction is writing or resolving the wrong per-system catalog state.
The status return is also not trustworthy as an indication of the visible list
that was mutated.

No Test125 output may be promoted.

## Immediate root-cause direction

The failure pattern is stronger than a simple extension-classifier miss:

- GB reported a change with no corresponding new visible GB entry.
- GBC reported no change despite the pending GBC input.
- GBA visibly acquired GB entries while reporting no change.
- CLASSIC status behavior was also wrong.

This points first at the reconstructed per-system resource/count/dispatch
contracts, not at raw filename matching.

The Test125 source hard-coded resource-table pointers:
- GB 0x80A3C374
- GBC 0x80A3C38C
- GBA 0x80A3C3A4

Those values were derived by applying a presumed 24-byte stride to a table
base. Hardware has now contradicted the resulting system isolation. They must
be treated as **unproven/incorrect until recovered directly from the exact
HW-proven Test08 scanner or exact firmware data**.

Likewise, do not assume the one-based 8-byte count-cache extrapolation is
correct merely because FC/SFC/MD fit the pattern. Revalidate the handheld
addresses from direct Test08 binary evidence before another candidate.

## Mandatory next gate

Before Test126:

1. decode the exact HW-passed Test08 3601-byte scanner blob;
2. recover the actual six per-system descriptor records/control flow from that
   blob, especially GB/GBC/GBA resource pointers, directory identity,
   classifier bounds, and count invalidation;
3. compare those exact values against Test125;
4. audit Test125 command routing and CLASSIC path against the emitted firmware;
5. patch source only from direct BIN/SRC evidence;
6. perform an offline synthetic isolation test using distinct sentinel
   filenames for GB/GBC/GBA and verify each worker touches only its selected
   triplet;
7. only then emit another hardware candidate.

Do not proceed to handheld art/meta materialization until selective catalog
isolation is repaired. The Test74/Test75 enrichment architecture remains the
final target and is unaffected by this negative result.
