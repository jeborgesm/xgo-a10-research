# Test105 stock-runner cache synchronization closure

Status: BIN. Construction prerequisite closed; no hardware candidate yet.

## Objective

The fixed-size Stage1 loader must not guess how newly fread executable bytes become safely callable. It must reproduce the cache-maintenance contract used by the known Test97 generic helper runner.

## Known runner sequence

Test97 generic helper runner:
    runtime 0x80A382E0

After:
- fopen helper;
- fread requested bytes to 0x87000000;
- require returned byte count == requested size;
- fclose helper;

the runner performs cache maintenance before:
    jalr 0x87000000

This ordering is mandatory for Test105 Stage1:

    fread Stage2
        |
    exact-count check
        |
    fclose
        |
    CACHE SYNC
        |
    jalr 0x87180000

No Stage2 execution is permitted on open/read/count failure.

## Construction rule

Stage1 must lift the runner's cache-maintenance operation exactly from Test97 rather than substituting:
- a guessed libc flush;
- a no-op;
- an architecture-generic cache instruction sequence;
- or a service inferred from another firmware family.

The Stage1 loader should preserve the same call ordering and error boundary as the runner.

## Why this closes the architecture, not yet the binary

The stock runner establishes that executable helper bytes loaded by fread require an explicit synchronization step before execution. The Test105 architecture now has a defined place and source for that operation.

The actual Stage1 binary must still be disassembled after construction to verify:
- the lifted cache call/sequence is present;
- it occurs after fclose;
- it occurs before jalr Stage2;
- no failure path falls through into Stage2;
- Stage2 destination passed to synchronization matches 0x87180000 if the primitive is range-sensitive.

## Test105 immutable packaging rules

- bios/bisrv.asd remains exact known-booting Test97:
  b66dbcd86ad785875a6804bb7d07c6eb1195ceedb01c0bce8107f65eee2ab66e
- MD/catalog.xgc remains exactly 2642 bytes.
- MD/catalog-safe.xgc is the only new executable payload.
- No Resources changes.
- No firmware patch.
- No status/UI/CLASSIC/Volume-OSD changes.

## Next

With the cache-sync prerequisite closed at design/BIN level, proceed to construct:
1. fixed-size Stage1 loader;
2. Stage2 rebuilt for 0x87180000;
3. combined disassembly and package-delta audit.

Do not promote until the generated artifacts themselves satisfy these checks.
