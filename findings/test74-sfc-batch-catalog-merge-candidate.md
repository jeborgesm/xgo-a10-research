# Test74 — SFC batch materialization + explicit catalog merge candidate

Date: 2026-09-13
Branch: `research-stock-catalog-enrichment`

Status: **offline-audited hardware candidate; pending device test**

## Why Test74 exists

Test73 produced a valid stock-shaped SFC wrapper on hardware, including friendly filename and artwork, but the new game did not appear in the SFC UI list. A second Refresh returned `No New Games`.

The generated test wrapper was:

`Super Mario All-Stars + SMW.zsf`

Its filename is 31 bytes. The captured stock SFC catalog contains slot-0 filenames up to 66 bytes, so filename length is not the cause.

## Design correction

Test74 makes the SFC path explicitly batch-oriented instead of relying on the existing six-console scanner to discover files materialized earlier in the same Refresh.

Refresh order becomes:

1. unchanged Test73 SFC materializer (`/SFC/refresh.xgc`)
2. new explicit SFC catalog merge (`/SFC/catalog.xgc`)
3. unchanged Test08-era six-console scanner
4. unchanged Test72 CLASSIC helper

The explicit SFC catalog merge scans top-level `/SFC/*.zsf` after materialization, compares exact filenames against slot 0 of the stock SFC triplet, collects every missing wrapper, and performs one synchronized append pass.

Stock SFC triplet:

- `/Resources/urefs.tax` — exact physical wrapper filename
- `/Resources/adsnt.nec` — basename fallback
- `/Resources/xvb6c.bvs` — basename/search fallback

The first candidate supports up to 256 missing `.zsf` wrappers in one pass. Existing order and indexes are preserved. Entries are appended; none are deleted or resorted.

## Batch semantics

The intended behavior is now explicit:

- materialize all pending source ROMs first;
- merge all missing generated wrappers in one catalog pass;
- never overwrite an existing wrapper automatically;
- retain ROM/JPG/TXT source sidecars;
- one game and a 50-game batch use the same code path;
- `Games Updated` if either materialization or catalog merge changes anything;
- `No New Games` only when both stages make no change.

## Recovery behavior

The Test73-generated wrapper does not need to be deleted. On a card where `Super Mario All-Stars + SMW.zsf` already exists but is not visible in the SFC catalog, Test74 should append that existing wrapper on the first Refresh.

## Implementation

New helper:

`/SFC/catalog.xgc`

- linked for `0x87000000`;
- size: 2,642 bytes;
- SHA-256: `7c45d63c4f15a23661a6f47873bd5c664d68a0a0806155a422f123952bc28a01`;
- no `$gp` references;
- uses the same stock file/directory ABI already proven by the project;
- invalidates the stock SFC count cache at `0x80D28954` after a successful merge.

The pre-scan firmware loader at `0x80A38240` was replaced with a two-helper sequential loader. It first runs the unchanged Test73 `/SFC/refresh.xgc`, then `/SFC/catalog.xgc`, ORs their changed/no-change result, initializes the six-console loop state exactly as Test73 did, and returns to the existing scanner.

The new loader is 591 bytes and remains inside the verified cave ending at `0x80A391F8`.

## Protection boundary

Unchanged from Test73/Test72:

- `/SFC/refresh.xgc` remains byte-for-byte the Test73 materializer;
- `/CLASSIC/refresh.xgc` remains byte-for-byte Test72;
- protected MAME2000 core remains byte-for-byte unchanged;
- existing six-console scanner hook/function is unchanged;
- stock Arcade is unchanged;
- Test72 CLASSIC bootstrap at `0x80A38000..0x80A3823F` is unchanged.

Firmware changes relative to Test73 are confined to:

- CRC word at `0x18C`;
- pre-scan loader cave `0x80A38240..0x80A391F7`.

The hook at `0x807DB67C` is unchanged from Test73.

## Candidate hashes

- Test74 ZIP SHA-256: `219c61525bb8b8ba1cb0db8c3d59b70a44e068242d51e12f5f6942ea2ccbc8fc`
- Test74 firmware SHA-256: `160e2bb9cb5ac04d2cba6df2802ead39b46e42208a5b6a5a0a8d6467e259632d`
- SFC materializer SHA-256: `1c1706dc1974f48eb6ab8b4598f866ac74992342e2e0885c5509c5edb8fe2dde`
- SFC catalog helper SHA-256: `7c45d63c4f15a23661a6f47873bd5c664d68a0a0806155a422f123952bc28a01`
- Test72 CLASSIC helper SHA-256: `9f932f35b1627bb8a4a7427831454e3c5dd854972231c1062316a814ada8723f`
- protected MAME2000 core SHA-256: `60a62e463fd6faf92744a7be666602dd1621b9fd706f90d20e3b55ee3382bb1e`

## Offline validation

The stock captured SFC triplet was parsed and rebuilt with the Mario wrapper appended:

- original count: 929
- synthetic new count: 930
- `urefs.tax` final value: `Super Mario All-Stars + SMW.zsf`
- `adsnt.nec` final value: `Super Mario All-Stars + SMW`
- `xvb6c.bvs` final value: `Super Mario All-Stars + SMW`

All three rebuilt triplets parsed successfully with matching count and index alignment.

## First hardware test

Keep the Test73-created Mario wrapper and source sidecars on the card.

1. Install Test74.
2. Run Refresh once — expected `Games Updated`.
3. Enter SFC — expected exactly one `Super Mario All-Stars + SMW` entry.
4. Verify artwork and launch.
5. Run Refresh again unchanged — expected `No New Games`.
6. After the single recovery proof passes, add several source sets together and test the real batch path.

Do not propagate to FC/MD/GB/GBC/GBA until this SFC path passes both single recovery and batch testing.
