# Test59 — External CLASSIC Refresh helper candidate

Date: 2026-09-10
Branch: `research-game-metadata-enrichment`

## Goal

Move the hardware-proven Test58 CLASSIC Refresh/reconciliation logic out of the nearly-full firmware cave so normal-image conversion can be added without destabilizing the importer.

## Test58 pressure

Test58 importer size: 4,584 bytes.
Established importer cave: 4,600 bytes (`0x80A38000..0x80A391F8`).
Remaining space: 16 bytes.

Therefore PNG/JPEG decoding, scaling, and RGB565 conversion must not be forced into the existing firmware cave.

## Test59 architecture

Test59 replaces the Test58 firmware-resident importer with a 485-byte bootstrap in the same proven cave.

The bootstrap:

1. checks that the live stock heap break is below `0x87000000`;
2. opens `/mnt/sda1/CLASSIC/refresh.xgc`;
3. temporarily lowers `RAMSIZE` to `0x87000000`;
4. reads the exact helper image to `0x87000000`;
5. performs the same cache-maintenance strategy used by the XGO external-core loader;
6. calls the helper at `0x87000000`;
7. restores `RAMSIZE` after return;
8. maps helper result into the existing `Games Updated / No New Games / Refresh Failed` path.

`0x87000000` is the already established external-core execution address in the XGO multicore work. Test35's failed worker used `0x86FE0000`; Test59 deliberately uses the canonical proven external-code address and allocator ceiling contract instead.

The external helper contains the same Test58 reconciliation/import behavior and is 4,760 bytes.

## Candidate identity

- ZIP: `xgo-classic-test59-external-refresh-helper.zip`
- ZIP SHA-256: `79680c311858c858c30d7b575646d68aaea11c4dfba030d19d5e345065de336f`
- firmware SHA-256: `af2713c5581ee6d9b9217952e945515a1501d7118d8610c26c538916a8857da5`
- bootstrap size: 485 bytes / 4,600-byte cave
- external helper size: 4,760 bytes
- external helper SHA-256: `858856796179d7b13b99b6b2116d96d26bf056062083141827ad982267af61a2`
- protected MAME2000 core SHA-256 remains `60a62e463fd6faf92744a7be666602dd1621b9fd706f90d20e3b55ee3382bb1e`

## Hardware gate

1. Boot and verify the Test57 CLASSIC UI remains correct.
2. Refresh with no changes; expect stable no-change behavior.
3. Delete one expendable `/CLASSIC/bin/*.zip`, Refresh, and verify its entry disappears.
4. Restore that ZIP, Refresh, and verify it reappears.
5. Launch CLASSIC and verify Save/Load remains functional.

If this passes, future helper revisions can add PNG/JPEG decode and resize/conversion logic without consuming firmware-cave space.