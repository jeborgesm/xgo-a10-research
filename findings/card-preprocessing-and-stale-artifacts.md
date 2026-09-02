# XGO Card Preprocessing and Stale Build Artifacts

Status: **OEM/card-preparation workflow strongly evidenced by timestamp clustering, emulator-specific sidecars, stale arcade states, and duplicate BIOS content.**

## Scope

This note treats the original `xgo_filelist.csv` as an archaeological artifact rather than merely a file inventory. The preserved analysis archive does not contain the multi-gigabyte ROM payload itself, but the inventory records exact filenames, sizes, timestamps and attributes from the original card.

The result is a clear picture of a card image that was assembled in multiple preprocessing passes and was not fully cleaned between revisions.

## Arcade quick-start `.skp` population

The original card contains:

```text
185 ARCADE/bin/*.zip ROM archives
167 ARCADE/skp/*.skp files total
```

Of the 167 `.skp` files:

```text
166 use the normal <rom>.zip.skp naming form
1 is malformed: gaia.zipip.skp
```

The XGO firmware contains the path template:

```text
%s/skp/%s.skp
```

at runtime string address `0x809a3a30`.

The active game-launch path around `0x8035f0ec` builds this filename with `sprintf`, tests the resulting path for existence, and only when the state file exists enters the subsequent state-loading path before normal game execution continues.

This matches independent SF2000-family reverse engineering: `.skp` files are emulator save states loaded automatically for prepackaged arcade games to skip the normal board boot/attract sequence and enter a prepared state quickly.

Thus `.skp` is not arbitrary cache data; it is **pre-generated emulator state used as part of the packaged arcade launch experience**.

## Twenty stale `.skp` files preserve removed arcade inventory

Comparing normal `<name>.zip.skp` sidecars against the 185 current `ARCADE/bin/<name>.zip` archives gives:

```text
146 .skp files with a matching current ROM archive
20  normal .skp files with no matching current ROM archive
```

The 20 stale names are:

```text
2020bb
bakatono
bstars2
cyberlip
galaxyfg
janshin
joyjoy
minasan
panicbom
pbobbl2n
pbobblen
pnyaa
pzlbowl
sgemf
snowbro3
snowbros
sonicwi2
spf2ta
tpgolf
turfmast
```

These files are strong archaeological evidence that the card-build source tree once contained or expected additional arcade ROM archives that were later removed without deleting their associated quick-start states.

They therefore preserve part of an **earlier arcade content manifest** even though the corresponding ROM payload is no longer on the card.

## Malformed `gaia.zipip.skp`

One additional state file is named:

```text
gaia.zipip.skp
```

rather than the expected:

```text
gaia.zip.skp
```

`gaia.zip` is present in the current arcade ROM inventory, but there is no correctly named `gaia.zip.skp`.

Because the firmware constructs the state path mechanically from the ROM filename plus `.skp`, this malformed sidecar is very unlikely to be selected by the normal launcher path.

This is a small but direct example of imperfect OEM preprocessing/content assembly surviving in the shipped card image.

## `.skp` timestamps show batch generation

The normal arcade `.skp` files are heavily clustered into a handful of timestamps, especially:

```text
2022-07-13 22:45:26  -> 106 files
2022-07-13 22:44:48  -> 23 files
2023-02-07 16:25:02  -> 15 files
```

This is consistent with automated or semi-automated state generation during ROM-set preparation rather than organic user gameplay.

Together with the separately documented 490 preprovisioned GBA `.sav` files, the SD image clearly underwent emulator-specific compatibility/content preprocessing.

## Duplicate Neo Geo BIOS archive

The preserved `bios` directory contains:

```text
neogeo.zip   2,727,539 bytes
neogeo1.zip  2,727,539 bytes
```

The two files are **byte-for-byte identical**:

```text
SHA-256:
ca3ce0fb17ff882cefb1a9f2e9165c4e9c6717148ed8d7313e12964cbea37129
```

for both files.

The XGO FBA core contains explicit BIOS archive strings:

```text
neogeo.zip
pgm.zip
/mnt/sda1/bios/%s
```

around `0x809a4dec`, and diagnostics such as:

```text
[FBA] Archive: %s
[FBA] Parsing archive %s.
[FBA] NeoGeo BIOS missing ...
```

No `neogeo1.zip` string occurs anywhere in `bisrv.asd`.

### Current conclusion

**CONFIRMED:** `neogeo.zip` and `neogeo1.zip` contain identical bytes.

**CONFIRMED:** the embedded FBA code explicitly names `neogeo.zip` and contains no literal `neogeo1.zip` reference.

**STRONG EVIDENCE:** `neogeo1.zip` is redundant compatibility/build debris rather than a distinct BIOS set required by the normal XGO firmware path.

Do not yet claim that deleting it is universally safe: an indirect/generated filename path has not been exhaustively ruled out. But there is no evidence of such a path, and the normal FBA BIOS selection explicitly points to `neogeo.zip`.

## Multi-stage card assembly chronology

The file timestamps provide a rough preparation sequence rather than a single monolithic image-build date. Examples include:

```text
2022-07-13  arcade quick-start states and many packaged assets
2023-02     large portions of GB/GBC/GBA/arcade packaged content
2023-05-29  many frontend RGB/resource assets
2023-06-29  mass GBA .sav provisioning and directory updates
2023-07     additional resource/content changes
2023-08-12  bisrv.asd timestamp
```

The exact meaning of each filesystem timestamp is not guaranteed—copies can preserve or alter timestamps—but the clustering and subsystem-specific batches strongly support **incremental assembly from multiple source packs/tools**.

This helps explain several otherwise odd properties already documented:

- hundreds of physically present but unindexed ROMs;
- stale remapping resources referenced by firmware but absent from the card;
- one present-but-unreachable remapping screen;
- stale arcade quick-start states for removed ROMs;
- duplicate BIOS archives;
- separate later GBA save-sidecar provisioning.

The shipped card is therefore best understood as an evolved OEM content tree with historical residue, not a clean build produced from one canonical manifest.

## Confidence

### CONFIRMED

- 185 current `ARCADE/bin/*.zip` archives are listed;
- 167 `.skp` files are listed;
- 166 have normal `.zip.skp` form and one is `gaia.zipip.skp`;
- 20 normal `.skp` basenames have no corresponding current `ARCADE/bin` archive;
- XGO firmware actively constructs `%s/skp/%s.skp` in the game-launch path;
- `neogeo.zip` and `neogeo1.zip` are byte-identical and share the same SHA-256;
- XGO FBA strings explicitly reference `neogeo.zip` and `pgm.zip`;
- no literal `neogeo1.zip` string exists in `bisrv.asd`.

### STRONG EVIDENCE

- the stale `.skp` files preserve names from an earlier arcade payload;
- `.skp` files were batch-generated as launch/quick-start states;
- `gaia.zipip.skp` is an unusable preprocessing typo under the normal launcher naming rule;
- `neogeo1.zip` is redundant card-build debris;
- the card was assembled incrementally from multiple content/preprocessing passes.

### OPEN

- exact earlier ROM set that produced the 20 stale `.skp` names;
- whether any indirect code path can ever request `neogeo1.zip`;
- exact byte contents/state format of the `.skp` files, since the uploaded analysis archive preserves their metadata but not the arcade payload/state files themselves;
- precise OEM tooling that generated the packaged ROMs, thumbnails, `.skp` states and GBA `.sav` sidecars.
