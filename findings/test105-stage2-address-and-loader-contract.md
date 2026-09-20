# Test105 staged-loader address and cache contract closure

Status: BIN / DESIGN. No hardware candidate.

This note continues the fixed-2642-byte Stage-1 architecture. bisrv.asd remains byte-for-byte the known-booting Test97 image.

## What the stock runner proves

The stock generic runner at 0x80A382E0 loads executable helper bytes to 0x87000000, verifies exact fread byte count, performs cache maintenance, and calls 0x87000000.

The same runner has already loaded the 1,056,520-byte refresh helper, ending at 0x87101F08.

Catalog working buffers begin at 0x87200000.

Therefore a second-stage loader does not need to invent a new execution model; it needs to reproduce the stock runner's load/verify/cache/call contract at a non-overlapping destination.

## Stage-2 placement decision

Use a conservative candidate:

    STAGE2 = 0x87180000

For the current 7000-byte hardened engine:

    start 0x87180000
    end   0x87181B58

Distance from proven largest Stage-1-style helper end:
    0x87180000 - 0x87101F08 = 0x0007E0F8

Distance to first catalog buffer:
    0x87200000 - 0x87181B58 = 0x0007E4A8

So the 7KB Stage2 sits approximately centered in the previously unused gap and does not overlap the known helper image or catalog buffers.

This is address-space evidence, not yet HW proof.

## Critical relocation requirement

The Test104 7000-byte helper was linked for 0x87000000 and cannot simply be copied to 0x87180000.

All appended absolute pointers/jump targets must be rebuilt for STAGE2=0x87180000.

The original catalog logic embedded in Stage2 must likewise execute correctly at the new base; any absolute self-references must be relocated.

Therefore Test105 Stage2 is a rebuild, not a rename of Test104 catalog.xgc.

## Stage1 responsibilities

Stage1 remains exactly 0x0A52 bytes because the unchanged firmware requests exactly that many bytes.

It should:
1. preserve the stock helper ABI;
2. fopen /mnt/sda1/MD/catalog-safe.xgc in rb;
3. fread exactly the Stage2 byte size to 0x87180000;
4. require exact byte count;
5. fclose;
6. perform the same cache synchronization required before executing newly loaded code;
7. jalr 0x87180000;
8. return Stage2 v0 unchanged.

On any load/open/count failure, return -1 using the existing catalog-helper status convention.

## Why recursive generic-runner reuse is rejected

Calling 0x80A382E0 from Stage1 would cause the generic runner to load Stage2 to 0x87000000, overwriting Stage1 while Stage1 is still part of the return chain.

A tail-transfer variant is theoretically possible but adds unnecessary stack/global restoration uncertainty.

Use a separate destination and explicit loader.

## Cache contract

The Stage1 loader must copy the exact cache-maintenance semantics used by the stock runner before jalr.

Do not omit cache synchronization merely because fread completed. The CPU may otherwise execute stale instructions from the Stage2 address.

Exact helper calls/instruction sequence must be lifted from the runner during implementation rather than guessed.

## Firmware invariant

Test105 packaging rule:

    bios/bisrv.asd SHA-256
    b66dbcd86ad785875a6804bb7d07c6eb1195ceedb01c0bce8107f65eee2ab66e

Any package whose bisrv.asd differs is automatically rejected before hardware.

## Remaining construction gate

Next offline step is now implementation-specific:
- extract exact runner cache sequence;
- rebuild hardened engine for 0x87180000;
- build fixed-size 2642-byte Stage1;
- disassemble both;
- prove Stage1 contains no path that writes firmware/catalog state itself;
- prove package delta is only MD/catalog.xgc + new MD/catalog-safe.xgc, with bisrv.asd unchanged.

No hardware test until those checks pass.
