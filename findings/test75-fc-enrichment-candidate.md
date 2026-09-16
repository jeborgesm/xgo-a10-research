# Test75 — FC stock enrichment hardware candidate

Date: 2026-09-13
Branch: `research-stock-catalog-enrichment`
Status: **OFFLINE AUDITED — awaiting hardware test**

## Parent

Test75 is additive to the hardware-passed Test74 SFC batch checkpoint.

Parent artifact:
`xgo-stock-test74-sfc-batch-catalog-merge.zip`

Parent ZIP SHA-256:
`219c61525bb8b8ba1cb0db8c3d59b70a44e068242d51e12f5f6942ea2ccbc8fc`

Test74 SFC behavior remains protected byte-for-byte.

## FC archaeology before build

The captured XGO file inventory confirms the shipped FC system uses:

- top-level `.zfc` packaged games;
- native `.nes` games in the same FC directory;
- stock catalog triplet `rdbui.tax / fhcfg.nec / nethn.bvs`.

The common XGO packaged-console launcher contract already maps `ZFC` through the same 144x208 RGB565 preview/package path used by `ZSF/ZMD/ZGB`. A direct FC wrapper byte capture is still unavailable, so Test75 is deliberately a one-game proof rather than a broad promotion.

## Candidate

`xgo-stock-test75-fc-enrichment-proof.zip`

ZIP size: `7,318,604` bytes

ZIP SHA-256:
`2a550aded4f37ce0b05488f54f30ad5de9295287f446a2f2a593737d615fc686`

Firmware SHA-256:
`67461ff030aadd5bf2f7fa62315a5cd176f97dfb105488ce57f1d4c938343801`

LCFG CRC-32/MPEG-2:
`0x9337ea6c`

## FC helper derivation

Rather than creating a new implementation, Test75 clones the hardware-passed Test74 SFC helpers and changes only the system-specific contract.

### `/FC/refresh.xgc`

Size: `1,056,520` (`0x101F08`)

SHA-256:
`8b9607e51e4ad24cf19b92dc356f065d57081eaf93d722ccd9c65c00156fbd4e`

Changes from the exact Test74 `/SFC/refresh.xgc`:

- source directory `/SFC/import` -> `/FC/import`;
- art/meta/scratch paths `/SFC/...` -> `/FC/...`;
- accepted proof source extension `.sfc` -> `.nes`;
- generated wrapper extension `.zsf` -> `.zfc`.

The JPEG decoder/scaler tail at helper offset `0x100000` is byte-for-byte unchanged from Test74/Test72.

First proof input contract:

```text
/FC/import/<stem>.nes
/FC/art/<stem>.jpg       optional; .jpeg also accepted
/FC/meta/<stem>.txt      optional friendly title
```

Generated runtime output:

```text
/FC/<friendly-or-basename>.zfc
```

Test75 intentionally accepts `.nes` only for the initial hardware proof. NFC/FDS/UNF can be generalized after the basic wrapper/route is proven.

### `/FC/catalog.xgc`

Size: `2,642` bytes

SHA-256:
`b12541d5daede8c6e35c0f6f3a53c35c705a7d7ea7bbb508a6ae7e1b8d956067`

Changes from the exact Test74 SFC catalog helper:

- wrapper filter `.zsf` -> `.zfc`;
- catalog triplet -> `rdbui.tax / fhcfg.nec / nethn.bvs`;
- scan root `/SFC` -> `/FC`;
- count-cache invalidation target -> FC list-0 cache at `0x80D2894C` (the documented count-table base; SFC list 1 is `0x80D28954`).

Stable merge semantics remain the proven Test74 behavior: collect missing top-level wrappers, preserve existing order/indexes, append exact physical wrapper filename to slot 0 and basename fallback to slots 1/2, rewrite each canonical catalog once, and return no-change on an unchanged second pass.

## Extended pre-scan dispatcher

The proven Test74 generic external-helper runner at `0x80A382E0..0x80A38457` is unchanged.

The Test74 pre-scan entry at `0x80A38240` now jumps to additive dispatcher code in previously empty cave space beginning at `0x80A38490`.

Execution order:

```text
FC refresh.xgc
-> FC catalog.xgc
-> unchanged SFC refresh.xgc
-> unchanged SFC catalog.xgc
-> existing six-console generalized scanner
-> unchanged Test72 CLASSIC bootstrap/helper
```

The dispatcher ORs change results from all four stock-enrichment helpers. Any helper failure routes directly to existing `Refresh Failed`. It initializes the scanner loop state exactly as Test73/Test74 did.

## Protected identities

Test75 carries these exact Test74 files unchanged:

- `/SFC/refresh.xgc` SHA-256 `1c1706dc1974f48eb6ab8b4598f866ac74992342e2e0885c5509c5edb8fe2dde`
- `/SFC/catalog.xgc` SHA-256 `7c45d63c4f15a23661a6f47873bd5c664d68a0a0806155a422f123952bc28a01`
- `/CLASSIC/refresh.xgc` remains the protected Test72 helper
- `/cores/classic-mame2000/core.xgc` remains the protected normalized MAME2000 core
- Test72 CLASSIC bootstrap `0x80A38000..0x80A3823F` is byte-for-byte unchanged
- existing six-console scanner hook/path remains in place.

## Offline audit

- candidate ZIP integrity test passes;
- FC helper sizes fit the already-proven external helper loader contract;
- new dispatcher occupies only previously unused cave space;
- generic helper runner is unchanged;
- SFC helpers are unchanged;
- CLASSIC bootstrap is unchanged;
- FC materializer changes only path/extension constants from the SFC implementation;
- FC catalog helper changes only wrapper extension, catalog paths, root, and list-cache target;
- no direct FC byte-wrapper capture is being falsely promoted as proof.

## Hardware gate

Use one known-good NES game first.

Expected:

1. Refresh -> `Games Updated`.
2. exactly one friendly FC entry appears;
3. matching JPG appears as artwork;
4. game launches through the FC emulator and normal pause/save behavior remains intact;
5. existing FC games still launch;
6. existing SFC enriched games still launch;
7. second unchanged Refresh -> `No New Games` with no duplicate.

Only after this passes should FC receive a small multi-game batch or the implementation move to MD.
