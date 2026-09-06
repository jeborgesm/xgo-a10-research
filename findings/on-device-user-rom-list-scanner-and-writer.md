# XGO on-device User-ROM scanner and list writer

Date: 2026-09-05
Branch: `research-game-list-scanning`

Status: **native scanner/writer confirmed; caller scope still being narrowed**

## Provenance

Architecture was recovered from the preserved stock-analysis image:

```text
bios/bisrv.asd
size 12,768,452
SHA-256 869e056d000337e1b10c834f0a93244c0abd99457c1c8374367f7dff20e43daf
```

This is not a patch base. The protected Audio OSD v8 golden baseline remains:

```text
artifact audio-osd-v8-button-event-only
ZIP SHA-256 ba3dad99471c6144fd8f6e9f5891bc88d44b955c5de8a21df905d0d396cdb83a
firmware SHA-256 4b8f7af994d16371a2664a3d46c983e52ffd1aefbebc5b5a4a9ae63dc6cbe954
```

## Major finding

XGO contains a complete device-side directory scanner, alphabetical sorter, and stock-list writer at runtime address:

```text
0x80353ae0
```

The routine uses the active list ID to select both a content folder and an output resource. It enumerates files through the stock filesystem layer, skips directories, normalizes and validates filename extensions, collects accepted filenames, sorts them with stock `strcmp`, converts entries to offsets, and writes the existing XGO list format:

```text
uint32_le count
uint32_le offsets[count]
char strings[]
```

The output is opened using the normal Resources path and `wb`, then closed and filesystem-synced.

## Filesystem anchors

```text
directory open wrapper   0x807d40c4
directory read wrapper   0x807d4124
directory close wrapper  0x807d41f4

fs_opendir   0x802abe28
fs_readdir   0x802ac438
fs_closedir  0x802ac4f0
```

## Folder/list relationship

The shipped `Resources/Foldername.ini` orders folders as:

```text
0 ROMS
1 FC
2 SFC
3 MD
4 GB
5 GBC
6 GBA
7-11 ARCADE
```

The independently recovered resource table maps list ID 0 to:

```text
tsmfk.tax / tsmfk.tax / tsmfk.tax
```

while built-in IDs use synchronized filename/title/search-key triplets.

The preserved `tsmfk.tax` is already known to contain 61 alphabetically indexed User-ROM filenames and carries the XGO runtime-write timestamp fingerprint.

Independent SF2000 and GB300 family documentation reports the same behavior: `tsmfk.tax` is generated from the User-ROM folder at runtime/boot.

Combined with the direct XGO implementation, this is strong evidence that `0x80353ae0` is XGO's native User-ROM index generator.

## Extension table

The scanner uppercases extensions and validates them against the stock table at approximately `0x80a3c4c8`.

Recovered accepted formats include:

```text
BKP ZIP
ZFC ZSF ZMD ZGB ZFB
SMC FIG SFC GD3 GD7 DX2 BSX SWC
NES NFC FDS UNF
GBA AGB GBZ
GBC GB SGB
BIN MD SMD GEN SMS
```

This directly supports mixed ordinary ROM formats in `ROMS`.

## Important built-in-list constraint

The scanner writes only the first resource selected for the active list ID.

That is internally consistent for ID 0 because all three resource slots are `tsmfk.tax`.

It is not yet safe to invoke the same routine blindly for FC/SFC/MD/GB/GBC/GBA or curated Arcade pages. Those pages have position-coupled filename, display-title, and search-key catalogs. Rebuilding only the filename list would misalign metadata unless the parallel resources are regenerated or normalized too.

Therefore:

```text
on-device ROM discovery and list serialization: CONFIRMED
safe stock built-in catalog regeneration: NOT YET PROVEN
```

## Runtime behavior

The only direct caller found so far is:

```text
0x80359404 -> 0x80353ae0
```

A frontend flag at `gp-0x5f64` is checked before this path, and the scanner sets it after generation. This proves the stock frontend deliberately suppresses redundant regeneration within the same runtime session.

## Confidence

### CONFIRMED

- native directory scan exists on XGO;
- file entries are filtered by a stock extension table;
- accepted filenames are alphabetically sorted;
- the exact stock list format is serialized by the device itself;
- the output resource is selected through the same menu/list resource table;
- list ID 0 maps `ROMS` to `tsmfk.tax`;
- a once-per-session style regeneration flag exists;
- built-in pages have parallel position-coupled metadata resources.

### STRONG EVIDENCE

- the routine is the normal XGO `ROMS -> Resources/tsmfk.tax` generator;
- the mechanism is inherited from the same SF2000/GB300 firmware family.

### OPEN

- exact frontend state gate proving normal invocation is restricted to list ID 0;
- whether XGO performs the rebuild at boot, first User Games entry, or another once-per-session transition;
- special behavior, if any, for fifth Arcade list ID 11;
- safe on-device strategy for rebuilding built-in metadata triplets;
- atomic/recoverable update design for an explicit user-triggered rebuild.

No firmware was modified and no hardware-test ZIP was produced in this pass.
