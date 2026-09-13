# Stock SFC metadata/artwork enrichment — first proof contract

Date: 2026-09-13
Branch: `research-stock-catalog-enrichment`
Status: **ARCHAEOLOGY/DESIGN GATE CLOSED — NO FIRMWARE CANDIDATE YET**

## Protected parent

All implementation work must start from the cumulative hardware-proven Test72-era baseline documented by `HANDOFF-CURRENT.md`.

Do not substitute stock firmware, Test52, Test53, or another older candidate merely because its binary is easier to obtain.

Protected cumulative behavior includes Mapper v19, CPS1 pacing repair, Audio OSD v8, six-console generalized Refresh, normalized CLASSIC/MAME2000, CLASSIC Save/Load, CLASSIC logo/reconciliation fixes, external `/CLASSIC/refresh.xgc`, JPEG conversion/scaling, and stable unchanged `No New Games` semantics.

## Why SFC is the first stock proof

SFC has the strongest XGO-local evidence:

- stock outer extension `.zsf`;
- synchronized catalog triplet `urefs.tax / adsnt.nec / xvb6c.bvs`;
- 144 x 208 little-endian RGB565 preview contract, 59,904 bytes;
- WQW payload begins at `0xEA00`;
- launcher decompresses archive item 0;
- Test03 hardware-proved an externally generated method-0/STORE WQW `.zsf` created from scratch;
- the generalized stock scanner already discovers `.zsf` and raw SFC-family files.

No other stock console should be modified until this SFC proof passes the regression gate.

## Source namespace

Raw source material must not live directly in `/SFC` because the protected generalized scanner deliberately accepts native SFC-family extensions there. Leaving `foo.sfc` beside a newly generated `Friendly Foo.zsf` would create two independent scan identities and can produce duplicate catalog entries.

Use a non-scanned subdirectory for editable ROM sources:

```text
/SFC/import/<basename>.sfc
/SFC/art/<basename>.jpg
/SFC/meta/<basename>.txt
```

Only the generated stock-style wrapper enters the normal top-level runtime namespace:

```text
/SFC/<Friendly Title>.zsf
```

The existing scanner skips directories, so the source ROM remains retained and non-destructive without becoming a second catalog candidate.

## Metadata contract

For the first proof:

- metadata is optional;
- when `/SFC/meta/<basename>.txt` exists, its first non-empty line supplies the friendly outer wrapper title;
- otherwise the raw ROM basename is the fallback title;
- the wrapper extension is always `.zsf`;
- characters invalid in FAT-style filenames are sanitized/rejected consistently before output creation;
- trailing spaces/dots are removed;
- an empty result is invalid and must fail that item rather than create an anonymous wrapper;
- no existing top-level wrapper is renamed.

The English XGO UI derives the visible title from the outer wrapper filename with the extension stripped, so no renderer hook is required.

## Runtime identity contract

The generated `.zsf` contains exactly one archive member: the source ROM bytes from `/SFC/import/<basename>.sfc`.

The XGO console launcher consumes WQW archive item 0. The inner member filename is not used to select the emulator. The active SFC list/folder plus outer `.zsf` route selects the SFC runtime.

First proof packaging should retain the already hardware-proven Test03 format:

```text
[59,904-byte 144x208 LE RGB565 preview]
[method-0/STORE WQW archive]
```

WQW rules:

- local header `WQW\x03`;
- central directory `WQW\x02`;
- EOCD `WQW\x01`;
- stored member filename bytes XOR `0xE5`;
- CRC32 and ordinary ZIP record fields remain standard.

Do not introduce an ordinary-PK-ZIP shortcut in the first proof because WQW STORE is already hardware-confirmed on this exact XGO.

## Artwork contract

Artwork is optional.

Preferred source:

```text
/SFC/art/<basename>.jpg
```

Reuse the protected Test64 concepts:

```text
baseline/non-progressive JPEG
 -> decode on XGO
 -> aspect-fit
 -> black letterbox
 -> 144 x 208
 -> little-endian RGB565
 -> 59,904-byte wrapper prefix
```

If no JPG exists, the first proof may use a known-good SFC fallback preview prefix. It must not borrow a CLASSIC/Arcade launcher payload; only the 59,904-byte image prefix may be reused as image data.

JPG/JPEG remains the supported ordinary source. Do not resurrect PNG Tests65-70.

## Collision and reprocessing rules

The first proof is intentionally conservative:

1. If the intended `/SFC/<Friendly Title>.zsf` does not exist, generate it.
2. If it already exists, do not overwrite it automatically.
3. A pre-existing wrapper is treated as already materialized; Refresh proceeds to normal catalog discovery/indexing.
4. Metadata edits that would imply renaming an already-generated wrapper are deferred; no automatic rename/delete migration in the first proof.
5. Two source ROMs resolving to the same friendly wrapper title are a collision; do not overwrite either existing output.
6. Source ROM/JPG/TXT files are retained after success.

This makes repeated Refresh idempotent and protects existing save/mapper identity keyed by outer wrapper filename.

## Refresh ordering

To achieve one-button/one-pass behavior, SFC materialization must run before the existing generalized stock scanner in the same user Refresh action:

```text
SFC source reconciliation/materialization
 -> generated top-level .zsf exists
 -> existing six-console scanner
 -> stable-append new .zsf into SFC triplet
 -> existing CLASSIC Refresh path remains intact
```

On a second unchanged pass:

- SFC helper sees the wrapper already exists and makes no change;
- generalized scanner sees the wrapper already indexed;
- CLASSIC helper sees no CLASSIC change;
- final UI result must be `No New Games`.

## First hardware dataset

Use one expendable, known-good SFC ROM not already represented by the intended friendly wrapper name.

Stage:

```text
/SFC/import/<basename>.sfc
/SFC/art/<basename>.jpg
/SFC/meta/<basename>.txt
```

The TXT should deliberately differ from the ROM basename so display/runtime separation is proven.

## Required hardware pass

The first candidate passes only if all of these are true:

1. One Refresh reports `Games Updated`.
2. Exactly one friendly SFC entry is added for the staged source.
3. Its supplied JPG artwork is displayed correctly.
4. Selecting it launches the source ROM normally.
5. The raw ROM remains under `/SFC/import` and is not separately indexed.
6. A second unchanged Refresh reports `No New Games`.
7. An existing untouched stock SFC title still launches.
8. Mapper v19 still opens, remaps, and persists on a representative title.
9. Audio OSD v8 remains button-event-only and times out normally.
10. A known CLASSIC game still launches.
11. CLASSIC Save/Load still restores a known hardware-proven title.
12. Existing CLASSIC metadata/artwork is unchanged.
13. Stock Arcade is unchanged.

Do not propagate to FC/MD/GB/GBC/GBA until this gate passes.

## Binary provenance gate before build

The current repository documents the final hardware artifact:

```text
xgo-classic-test72-one-shot-batch-import.zip
SHA-256 af14ce8eb2e111386873ad697e1c4654ea2dcde663be5410bfd5a71f36fa4a16
```

However, during this continuation the actual Test72 ZIP and its final `/CLASSIC/refresh.xgc` were not found in:

- the checked-out/current tree of `jeborgesm/xgo-a10-research`;
- the current committed tree of private `jeborgesm/xgo-a10-artifacts`;
- the supplied `/mnt/data/XGoAnalisis.zip` (which contains stock firmware SHA-256 `869e056d000337e1b10c834f0a93244c0abd99457c1c8374367f7dff20e43daf`, not the cumulative Test72 firmware).

The public research history records Test64 firmware SHA-256 `0fb8dda0f03b3a8068b23a02d03354475538be0c8e7ed83d8f2ee5d69ab57fef` and Test64 `refresh.xgc` SHA-256 `6d416c71af871445023de96522d78bfa62b6277cfb7e5e37945bc12ea76dc98d`, but those hashes are not a license to reconstruct Test72 from an older package.

Therefore no hardware candidate should be labeled cumulative/Test72-based until the exact final Test72 package (or byte-equivalent final firmware + `/CLASSIC/refresh.xgc` + protected runtime files) is recovered and hash-audited.

This is a provenance/safety gate, not an architecture uncertainty.
