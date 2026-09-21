# Test105 architecture correction: fixed 2642-byte catalog shim, no firmware modification

Status: DESIGN / implementation direction. Supersedes the Test104 firmware-size patch approach.

## Core correction

There is no architectural requirement to modify bios/bisrv.asd merely because the hardened catalog implementation is larger than 2642 bytes.

The known-booting Test97 firmware already establishes a fixed external-helper contract:

    /MD/catalog.xgc
    exact requested size = 2642 bytes
    load address = 0x87000000

Preserve that contract exactly.

The Test104 failure demonstrated that changing the firmware-side size immediate is unnecessary risk. Test105 must use the exact known-booting Test97 bisrv.asd byte-for-byte.

## Two-stage architecture

Stage 1:

    /MD/catalog.xgc
    EXACTLY 2642 bytes

Responsibilities:
- run under the unchanged Test97 helper contract;
- load Stage 2 from SD;
- transfer control to Stage 2;
- return Stage 2 result to the stock caller.

Stage 2:

    /MD/catalog-safe.xgc

Responsibilities:
- recovery preflight;
- existing live-catalog validation;
- backup OLD generation;
- byte-verify backup;
- construct NEW generation;
- commit TAX/NEC/BVS;
- byte-verify NEW LIVE;
- rollback on failure;
- recovery cleanup;
- cache invalidation;
- return existing status convention.

bios/bisrv.asd remains byte-for-byte Test97.

## Important implementation constraint

Stage 1 cannot load Stage 2 over itself at 0x87000000 and then continue executing.

Therefore Stage 2 needs a separate execution address.

The existing catalog buffers begin at 0x87200000. The already proven refresh helper extends to 0x87101F08.

A conservative Stage-2 execution address must lie above the Stage-1 image and below known catalog buffers, without colliding with any runner/runtime workspace.

Candidate region for offline analysis:

    0x87180000

This is DESIGN only until all Test97 helpers are searched for accesses in that region.

Do not choose an address merely because it appears numerically free.

## Better reuse opportunity

The original 2642-byte catalog helper already knows the stock firmware-service ABI for:
- fopen
- fread
- fwrite
- fclose
- directory operations
- cache behavior through its established call convention

Stage 1 therefore does not need a second generic firmware runner. It can be a tiny explicit loader:

    fopen("/mnt/sda1/MD/catalog-safe.xgc","rb")
        |
        v
    fread(STAGE2_ADDR, 1, EXACT_STAGE2_SIZE)
        |
        v
    require exact byte count
        |
        v
    fclose
        |
        v
    instruction/data cache maintenance
        |
        v
    jalr STAGE2_ADDR
        |
        v
    return Stage2 v0

The cache-maintenance requirement is mandatory. Loading executable bytes and jumping without reproducing the runner's cache synchronization would be unsafe.

## Alternative with even less new loader code

Before implementing the explicit loader, investigate whether the 2642-byte Stage 1 can invoke the existing generic runner at 0x80A382E0 recursively:

    Stage1 @ 0x87000000
        |
        v
    generic runner(path=Stage2, size=Stage2Size)

This is attractive but potentially unsafe because the generic runner itself loads its target to 0x87000000, which would overwrite the currently executing Stage1 before the runner returns through Stage1.

Unless control can be tail-transferred so Stage1 is never resumed, this path must be rejected.

Current default: separate Stage2 address + explicit load/cache/jump.

## Packaging goal

Test105 should eventually have:

CHANGED/ADDED:
- MD/catalog.xgc          fixed 2642-byte Stage1 shim
- MD/catalog-safe.xgc     Stage2 hardened implementation

UNCHANGED:
- bios/bisrv.asd          exact Test97 SHA
- MD/refresh.xgc
- FC/SFC helpers
- Resources
- CLASSIC
- Volume OSD
- stock status paths

## Hardware gate

No Test105 hardware package until:
1. a Stage2 address is proven unused by all relevant Test97 helper code;
2. exact cache-maintenance calls are reconstructed from the generic runner;
3. Stage1 fits exactly inside 2642 bytes;
4. Stage1 error paths preserve stock return convention;
5. Stage2 is relocated for its chosen execution address;
6. the combined Stage1/Stage2 pair is statically disassembled;
7. package comparison proves bisrv.asd is byte-identical to the user's uploaded known-booting file.

This architecture removes the Test104 boot-sensitive firmware delta entirely.
