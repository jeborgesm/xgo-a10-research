# Test79 — MD dispatcher-only no-op bisect

## Status

**OFFLINE AUDITED / AWAITING HARDWARE**

A Test75 control rerun was performed before this candidate with the staged MD directories, native .md files, sidecars, and ignore_file.xyz still present. Test75 returned **No New Games** and remained responsive. This establishes that the staged MD filesystem contents themselves do not regress the hardware-passed Test75 Refresh path.

## Construction

Test79 starts from the exact hardware-passed Test75 package.

Only the pre-scan dispatcher cave is replaced with the expanded Test76 dispatcher form. At the point where that expanded form would begin the MD helper stage, Test79 performs an unconditional jump directly to the proven stock-scanner continuation.

Therefore Test79:

- does not load /MD/refresh.xgc;
- does not call an MD helper;
- does not load /MD/catalog.xgc;
- does not inspect any MD files or directories;
- leaves FC and SFC helper binaries byte-for-byte unchanged;
- preserves the staged MD test files as an inert control fixture.

The MD-stage bypass is at firmware file offset 0xA38540 and jumps to runtime 0x80A38598, the existing continuation into the stock Refresh scanner path.

## Candidate identity

- ZIP: xgo-stock-test79-md-dispatcher-noop-bisect.zip
- ZIP SHA-256: 6cfddac68e8905ab87a6c2f9f6662e7bbbf9ae1141b93d8d83728079fa62d5d5
- firmware SHA-256: dba187197180b175d1af9978e115fce3f4da8b9f0222aa0485bb9b05f1c4c0f4
- firmware CRC-32/MPEG-2: 0xCCB1C958
- FC refresh SHA-256: 8b9607e51e4ad24cf19b92cd356f065d57081eaf93d722ccd9c65c00156fbd4e
- SFC refresh SHA-256: 1c1706dc1974f48eb6ab8b4598f866ac74992342e2e0885c5509c5edb8fe2dde
- ZIP integrity test passed.

## Hardware interpretation

With the current unchanged SD-card fixture, expected result is **No New Games** and a responsive frontend.

- If Test79 freezes, the regression is in the expanded dispatcher/control-flow patch itself, before MD helper loading.
- If Test79 returns normally, the expanded dispatcher is viable and Test78 localizes the failure specifically to the MD helper load/call/return integration boundary.

Diagnostic artifact only; do not promote to golden.
