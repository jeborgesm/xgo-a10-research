# XGO Resource Tables, Search Indexes, and Hidden ROM Inventory

Status: **file formats confirmed; several frontend behaviors reconstructed from SD resources and firmware tables**.

## Scope

This pass analyzed the XGO `Resources` directory together with the central filename-pointer table embedded in `bios/bisrv.asd`. No hardware modification or runtime probing was required.

## Setup UI confirms the three persisted `Archive.sys` settings

Decoded 640x480 RGB565 setup screens explicitly show three setup items:

```text
User Games
Language
TV System
```

The six language-selection screens identify the language ordering as:

```text
0 English
1 Chinese
2 Arabic
3 Hebrew
4 Spanish
5 Russian
```

This resolves the first two words of the 12-byte `Archive.sys` file more strongly than the earlier behavioral inference:

```text
uint32 language       // 0..5
uint32 tv_system      // 0/1
uint32 volume         // 0,33,66,99
```

The firmware already confirmed that the second word is a persisted binary toggle followed by display reconfiguration; the decoded setup artwork now identifies its user-facing role as **TV System**.

## Resource pointer table

A large direct-pointer table around `0x80a3c298` maps opaque resource filenames to frontend roles. Examples include:

```text
0x80a3c298 -> fhshl.skb   English UI strings
0x80a3c29c -> t2act.sgf   Chinese UI strings
0x80a3c2a0 -> vdaz5.bjk   Arabic UI strings
0x80a3c2a4 -> xjebd.clq   Hebrew UI strings
0x80a3c2a8 -> eknjo.ofd   Spanish UI strings
0x80a3c2ac -> tvctu.uby   Russian UI strings
...
0x80a3c318 -> dism.cef    in-game menu page 0
0x80a3c31c -> d2d1.hgp    in-game menu page 1
0x80a3c320 -> bisrv.nec    in-game menu page 2
0x80a3c324 -> pwsso.occ    in-game menu page 3
0x80a3c328 -> gpapi.bvs   stranded remapping artwork
```

The meaningless extensions are therefore deliberate obfuscation/noise rather than useful type information.

## UI string bundles reveal frontend features

The six localized text bundles contain the same functional messages. The English bundle `fhshl.skb` contains:

```text
Loading......
Folder is empty。
Resume Quit Load Save
Archive already exists,
overwrite this archive?
Archive save failed .
Please check TF card
after power off .
LOW BATTERY!
Please charge it in time.
Save the progress, Power off and charge.
Search
No games match the keyword.
Favorites are full !
Remove from favorites?
```

This confirms the shipped frontend has active concepts for:

- four save-state slots / pause-menu actions;
- overwrite confirmation and TF-card save errors;
- low-battery warnings;
- text search;
- favorites with a capacity limit and remove confirmation.

These are not emulator-core strings; they are XGO frontend localization resources.

## Missing inherited resource files

Comparing all resource filenames referenced by the XGO firmware's main resource table to the actual SD-card file listing finds only three referenced names missing from the card:

```text
seltMap.key
dectMap.key
dsreg.bvs
```

`seltMap.key` and `dectMap.key` are known SF2000-family controller-test/remapping-era resources. Their names remain in the XGO firmware table but the files are absent. Together with the present-but-unreachable `gpapi.bvs`, this is additional evidence that the XGO fork retained portions of an older controller/remapping resource layout after removing/disconnecting parts of the visible feature.

## Built-in ROM-list format

Most system list resources use a common format:

```text
uint32 count
uint32 offsets[count]      // relative to start of string-data area
char   strings[]           // NUL-terminated UTF-8 / ASCII
```

The XGO stores three parallel lists for each built-in console section:

1. packaged ROM filenames;
2. Chinese display titles;
3. short romanized search keys.

Confirmed groups:

```text
NES / FC
  rdbui.tax   744 filenames
  fhcfg.nec   744 Chinese titles
  nethn.bvs   744 search keys

SNES / SFC
  urefs.tax   929 filenames
  adsnt.nec   929 Chinese titles
  xvb6c.bvs   929 search keys

Mega Drive
  scksp.tax   788 filenames
  setxa.nec   788 Chinese titles
  wmiui.bvs   788 search keys

Game Boy
  vdsdc.tax   885 filenames
  umboa.nec   885 Chinese titles
  qdvd6.bvs   885 search keys

Game Boy Color
  pnpui.tax   958 filenames
  wjere.nec   958 Chinese titles
  mgdel.bvs   958 search keys

Game Boy Advance
  vfnet.tax   626 filenames
  htuiw.nec   626 Chinese titles
  sppnp.bvs   626 search keys
```

### The `.bvs` strings are pinyin-style search keys

The short strings are not arbitrary internal IDs. They correspond to romanized initials of the Chinese titles. Examples:

```text
魂斗罗 1             -> HDL1
火焰纹章...           -> HYWZ...
忍者三人组            -> RZSRZ
```

This strongly indicates that the XGO's search system supports compact romanized/pinyin-style matching for the Chinese built-in lists.

## Arcade is split into multiple logical menu sections

Four packaged arcade metadata groups are confirmed:

```text
CPS1
  mswb7.tax   26 filenames
  msdtc.nec   26 Chinese titles
  mfpmp.bvs   26 search keys

CPS2
  kjbyr.tax   28 filenames
  djoin.nec   28 Chinese titles
  ke89a.bvs   28 search keys

PGM / IGS-style curated group
  subst.tax    6 filenames
  aepic.nec    6 Chinese titles
  sensc.bvs    6 search keys

Neo Geo
  rmapi.tax   117 filenames
  pcadm.nec   117 Chinese titles
  ntdll.bvs   117 search keys
```

The XGO `Foldername.ini` contains five repeated `ARCADE` sections. Favorites/history record IDs resolve the first four cleanly:

```text
menu/list ID 7  -> CPS1   (observed history indices fit 0..25)
menu/list ID 8  -> CPS2   (observed history indices fit 0..27)
menu/list ID 9  -> PGM/IGS curated group (observed indices fit 0..5)
menu/list ID 10 -> Neo Geo (observed indices fit the 117-entry list)
```

List ID 11 remains the unexplained fifth arcade section and is a useful future target. The card also contains a large set of raw `.zip` arcade files, making a dynamically scanned/raw-arcade section a plausible hypothesis, but this is not yet confirmed.

## Favorites and history record IDs map directly to menu sections

Both persistence files use 4-byte records after a leading count:

```text
uint32 count
repeat count times:
    uint16 list_id
    uint16 game_index
```

`Falas.clk` contains 9 records and `Hisas.boa` contains 200 records on the preserved card.

The observed IDs support this menu numbering:

```text
0  User ROMS        // notably absent from History
1  FC / NES
2  SFC / SNES
3  MD
4  GB
5  GBC
6  GBA
7  Arcade CPS1
8  Arcade CPS2
9  Arcade PGM/IGS
10 Arcade Neo Geo
11 fifth Arcade section, unresolved
```

The lack of list ID 0 in the 200-entry history is consistent with the SF2000-family behavior that user-folder ROMs are not stored in the built-in history database.

## User-ROM index `tsmfk.tax`

`tsmfk.tax` is structurally different from the fixed built-in lists and corresponds to the `ROMS` user folder.

On the preserved card:

```text
uint32 count = 61
uint32 sorted_offsets[61]
char filename_strings[]
```

The 61 offsets are relative to the string-data area. Unlike the built-in lists, they are intentionally **not monotonic**: resolving them produces the user ROM filenames in alphabetical display/search order even though the underlying string blob is stored in another order.

This confirms that the XGO frontend builds/uses a dedicated sorted index for the freely scanned `ROMS` directory rather than treating it like one of the fixed built-in packaged lists.

## A large number of ROM files are physically present but not in built-in lists

Comparing the original card file listing against the filename metadata resources reveals many ROM files that physically exist in the built-in system directories but are absent from the corresponding menu index.

```text
System   physical candidate ROMs   indexed   physical-but-unindexed
FC                764                744              20
SFC              1078                929             149
MD                833                788              45
GB                973                885              88
GBC               973                958              15
GBA               656                626              30
```

Every indexed filename was found physically on the card; the mismatch goes only in the other direction. Thus at least **347 console ROM files are stored on the card but omitted from their built-in menu lists**.

Examples of physically present but unindexed files include titles such as `Shantae.zgb`, `Actraiser 2.zsf`, `Batman Returns.zsf`, and multiple native `.nes` files in the FC directory.

For packaged arcade `.zfb` files:

```text
physical .zfb files  = 184
indexed in four known arcade groups = 177
unindexed = 7
```

The seven unindexed packaged arcade files are:

```text
Metal Slug 6.zfb
Pop 'n Bounce.zfb
Power Instinct.zfb
Pretty Soldier Sailor Moon.zfb
Puzzle Star.zfb
Shock Troopers -2nd Squad.zfb
Street Fighter Zero.zfb
```

This is a software/content-layout finding only; it does not imply those omitted titles are compatible or intentionally supported. They may have been excluded because of duplication, performance, quality-control, or list-generation decisions. But they are objectively present on the card and not referenced by the visible built-in indexes.

## Four save-state slots confirmed from card inventory

The firmware path format is:

```text
%s/save/%s.sa%d
```

and the original file listing contains `.sa0`, `.sa1`, `.sa2`, and `.sa3` across multiple systems, matching the four visual Load/Save slots in the pause interface.

State sizes vary substantially by emulator/game, consistent with serialized emulator state rather than a fixed raw-memory dump. No separate per-slot thumbnail files are present in the save directories, so the displayed slot preview must either be embedded/derived from the state file or generated from another runtime source; the exact state container layout remains unresolved.

## Confidence summary

### CONFIRMED

- six-language localized frontend text bundles and their order;
- setup UI includes User Games, Language, and TV System;
- `Archive.sys` second persisted setting is the TV-system control;
- fixed built-in ROM list file format;
- per-system filename/title/search-key triplets and exact entry counts;
- pinyin-style purpose of the compact search-key lists;
- `tsmfk.tax` is a 61-entry sorted user-ROM filename index on this card;
- favorites/history 4-byte record format and menu/list-ID mapping through ID 10;
- four save-state slot suffixes `.sa0` through `.sa3`;
- hundreds of physically present but unindexed console ROM files;
- seven physically present but unindexed packaged arcade `.zfb` files;
- `seltMap.key`, `dectMap.key`, and `dsreg.bvs` are referenced by firmware but absent from the preserved card.

### STRONG EVIDENCE

- list ID 11 is the fifth repeated Arcade section from `Foldername.ini`;
- the fifth Arcade section may relate to the card's raw `.zip` arcade inventory;
- `gpapi.bvs` plus absent controller-era resources are remnants of a partially removed older remapping/test UI.

### OPEN

- exact role and backing data for arcade list ID 11;
- exact save-state compression/container format;
- why the vendor shipped hundreds of unindexed ROM files;
- whether editing built-in list resources is sufficient to expose every omitted file safely;
- exact generated-index update rules for `tsmfk.tax`.