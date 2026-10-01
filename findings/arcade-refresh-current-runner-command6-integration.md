# Arcade Refresh - current golden runner and command-6 integration closure

Date: 2026-09-24
Branch: research-arcade-refresh-four-family
Status: DIRECT BIN AUDIT OF FINAL GBC/GBA GOLDEN FIRMWARE

Source firmware:
SHA-256 ea442b74bdc07cd5e05ec2de8da5c997848a76ed3125681c1955fbcb29b66152

## Generic runner is still intact

The current golden firmware contains the generic external-helper runner at
0x80A382E0..0x80A38454.

ABI:
- a0 = helper pathname
- a1 = exact byte count
- return v0 = helper return value, or -1 on runner failure.

Directly recovered behavior:
1. reject when heap break 0x80C237B0 is above 0x86FFFFFF;
2. fopen(path, "rb") through stock wrapper 0x802B3524;
3. save current execution-region global 0x80C2CE6C;
4. set that global to 0x87000000;
5. fread exactly a1 bytes to 0x87000000 through 0x802B3698;
6. fclose through 0x802B2F40;
7. require exact byte count;
8. execute cache-op-1 loop, sync, cache-op-0 loop;
9. jalr 0x87000000;
10. restore 0x80C2CE6C;
11. return helper v0.

The cache sequence is exactly the one later copied into the HW-proven
Test105/Test106 staged loader lineage.

## Current command-6 slot

The final GBC/GBA decoder continuation at 0x80A397E0 distinguishes:
- 4 -> GBC
- 5 -> GBA
- 7 -> CLASSIC
- default, including command 6 -> existing native No New Games path.

Therefore command 6 remains a clean additive integration point.

Commands 0..5 and 7 do not need to be rewritten.

## Loader choice

A single common /ARCADE/refresh.xgc remains the preferred materializer shape:
- exact size can remain 0x101F08, same as Test74/Test75;
- generic runner already HW-proves loading that size to 0x87000000;
- decoder tail remains at +0x100000 / runtime 0x87100000;
- one helper can iterate CPS1,CPS2,IGS,NEOGEO descriptors;
- no duplicated 1MB decoder tails.

Catalog transaction logic should NOT be appended beyond 0x101F08 because that
would collide with the fixed decoder layout and would abandon the proven
materializer geometry.

Use a separate Arcade catalog stage after materialization.

## Catalog-stage shape

The safe precedent is Test105/Test106:
- small first-stage helper loaded by the generic runner at 0x87000000;
- Stage1 explicitly loads larger transaction engine to 0x87180000;
- exact-count check;
- byte-identical stock cache-maintenance sequence;
- jalr 0x87180000;
- return Stage2 v0.

For Arcade this gives a clean sequence:

command 6
 -> run /ARCADE/refresh.xgc size 0x101F08
 -> if negative: Refresh Failed
 -> run /ARCADE/catalog.xgc fixed Stage1 size
 -> Stage1 loads /ARCADE/catalog-safe.xgc to 0x87180000
 -> four-family transaction engine
 -> aggregate return
 -> existing common Refresh status/epilogue

The materializer has returned before catalog Stage1 is loaded, so overwriting
0x87000000 is safe. The Stage2 address 0x87180000 does not overlap the
materializer's proven end 0x87101F08 or catalog work buffers beginning at
0x87200000.

## Result aggregation

Materializer and catalog stage use the established status convention:
- negative -> overall failure
- zero -> no change
- positive -> OR into aggregate changed flag

Within catalog Stage2:
CPS1 -> CPS2 -> IGS -> NEOGEO
- each family has its own marker/recovery triplet;
- a later family failure does not roll back an earlier committed family;
- overall return remains negative on any family failure.

## Firmware delta target

First candidate should modify only:
- LCFG CRC field;
- the existing command-6/default branch in the 0x80A397E0 decoder continuation;
- previously-zero cave bytes needed for a compact Arcade command-6 body and
  path literals.

Commands 0..5 and 7, generic runner, GB/GBC/GBA bodies, CLASSIC bootstrap and
all protected historical mechanisms should compare byte-identical.

No speculative Arcade count-cache write is part of this design.
