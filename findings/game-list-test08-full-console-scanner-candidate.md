# Game-List Test08 — full six-console discovery + stable-merge candidate

Date: 2026-09-07
Branch: `research-game-list-general-scanner`

Status: **offline-audited hardware candidate; NOT golden pending hardware test**

## Supersedes Test07 before hardware test

Test07's SFC-only candidate is superseded. No Test07 hardware test is required.

Test08 is the first candidate intended to exercise the actual target behavior:

```text
one Refresh command
  -> FC
  -> SFC
  -> MD
  -> GB
  -> GBC
  -> GBA
```

There are no hardcoded ROM filenames, no expected old/new catalog counts, and no staged replacement catalogs.

## Protected parent

The candidate starts from the exact hardware-confirmed Test06b firmware/UI milestone:

```text
xgo-game-list-test06b-timed-status.zip
ZIP SHA-256      2d859b3ca3f0644a461c197fcfe0b58f2650c26bc6a7c8d28a189da196aa1042
firmware SHA-256 5d15cbe1cef380b3517cbd64727526e1b837df5160ba5275ccde6fec01324f4e
```

The Test06b Refresh menu and timed stock-font status behavior remain the protected UI baseline.

## Runtime system table

The engine iterates list IDs 1 through 6. It resolves each synchronized filename/title/search triplet directly from the stock firmware table at `0x80a3c32c`.

Confirmed mapping:

```text
ID 1  FC   rdbui.tax  fhcfg.nec  nethn.bvs
ID 2  SFC  urefs.tax  adsnt.nec  xvb6c.bvs
ID 3  MD   scksp.tax  setxa.nec  wmiui.bvs
ID 4  GB   vdsdc.tax  umboa.nec  qdvd6.bvs
ID 5  GBC  pnpui.tax  wjere.nec  mgdel.bvs
ID 6  GBA  vfnet.tax  htuiw.nec  sppnp.bvs
```

The per-list count array at `0x80d2894c` is invalidated only for systems actually changed.

## Extension classification

The stock classifier at `0x80360a08` returns one-based indices into the recovered extension table.

Test08 accepts the system's wrapper return plus the native-family return range:

```text
FC   ZFC=3   or NES/NFC/FDS/UNF = 16..19
SFC  ZSF=4   or SMC/FIG/SFC/GD3/GD7/DX2/BSX/SWC = 8..15
MD   ZMD=5   or BIN/MD/SMD/GEN/SMS = 26..30
GB   ZGB=6   or GBC/GB/SGB = 23..25
GBC  ZGB=6   or GBC/GB/SGB = 23..25
GBA  ZGB=6   or GBA/AGB/GBZ = 20..22
```

Folder identity therefore separates GB/GBC/GBA wrapped `.zgb` files while native extensions remain family-filtered.

The classifier's global system-mask side effect is saved and restored around every system pass.

## Stable merge

For each system:

1. read the current synchronized triplet;
2. verify all three counts agree;
3. scan the real physical directory through stock `DIR_OPEN/DIR_NEXT/DIR_CLOSE`;
4. skip directories;
5. classify the extension;
6. compare each physical filename against slot 0;
7. collect every filename absent from slot 0;
8. preserve every existing entry/index/order;
9. append the exact filename to slot 0;
10. append basename-without-extension fallback strings to slots 1 and 2;
11. construct all three complete output catalogs in RAM;
12. rewrite the triplet;
13. `fs_sync`;
14. invalidate only `count[list_id]`;
15. continue to the next console.

Missing physical files are never deleted from catalogs and existing catalogs are never globally re-sorted.

Candidate capacity is 512 newly discovered files per system. Only confirmed additions consume candidate records; rejected and already-indexed files use a fixed temporary filename buffer.

## Captured-card scale audit

The preserved XGO filesystem inventory and captured catalogs were run through the same discovery rules offline.

Expected physical-but-unindexed workload in that capture:

```text
FC    20   744 -> 764
SFC  149   929 -> 1078
MD    45   788 -> 833
GB    88   885 -> 973
GBC   15   958 -> 973
GBA   30   626 -> 656
-----------------------
total 347 additions
```

Projected final triplet sizes all remain below the 65,536-byte per-slot guard:

```text
FC   17,071 / 13,760 /  7,453
SFC  31,537 / 25,030 / 14,238
MD   23,301 / 16,949 /  9,125
GB   27,509 / 21,745 / 11,525
GBC  30,915 / 22,969 / 11,130
GBA  23,588 / 18,930 /  8,870
```

These values are evidence/audit expectations only. They are not embedded in runtime code.

## Clean install package

Unlike Test06b/Test07 proof packaging, Test08 deliberately contains:

- patched `bios/bisrv.asd`;
- the six already-proven Test06b User Menu UI resources;
- hardware-test README.

It deliberately contains **none** of:

- `Resources/refresh.bin`;
- any game-list catalog;
- `SFC/XGO Import Test.zsf`;
- any other test ROM.

Installing Test08 therefore does not itself reset or pre-populate a catalog. Catalog mutation begins only when the device-side Refresh scanner is invoked.

## Exact candidate

```text
xgo-game-list-test08-all-console-scanner.zip
size              4,921,057 bytes
ZIP SHA-256        9c66fd727a2f894ad692b4868ba8bcee3daf2ff81b4d7eced539f80f2fd2e61e
firmware SHA-256   45831b0ea3c9ae336d82b240e6afe27167e5e83b88037152af237ab758ca1444
scanner/status     3,601 bytes
scanner SHA-256    a3f965d0ccabc2238da240a4b05b5f8027c968e40ede1831b51c42cff374c01d
firmware cave      0x807dab98..0x807dbba0
remaining cave     495 bytes
```

The candidate was independently rebuilt by the compact exact-candidate reproducer and the resulting ZIP was byte-identical.

Repository reproducer:

`tools/game_lists/build_test08_all_console_scanner_candidate.py`

Commit:

`95f91ae374dd26134c83284c3b15e4882bb49469`

## Hardware gate

**Disposable clone only. Do not interrupt power during Refresh.**

Before Refresh, record visible FC/SFC/MD/GB/GBC/GBA counts.

First Refresh:

- should scan all six directories;
- should report `Games Updated` when at least one system has discoveries;
- every previously unindexed accepted physical ROM should appear at the end of its corresponding list;
- existing games must stay in their previous order and at their previous indices.

Second Refresh:

- should report `No New Games`;
- counts should remain unchanged.

Regression checks:

- representative existing Favorites/History/save references;
- Search;
- Chinese-mode list/search alignment;
- several newly discovered games from multiple systems launch through the correct emulator page;
- User Games / Language / TV System;
- three-second status expiry;
- Audio OSD;
- protected SNES and CPS1 behavior.

## Remaining safety boundary

Test08 still performs in-place canonical triplet writes. It builds each system's complete new triplet in RAM first, but a power interruption during the three-file write remains capable of leaving that system inconsistent.

Transaction marker + backup/recovery remains the next safety layer after Test08 hardware confirmation.

Arcade is intentionally excluded from Test08. Arcade requires a separate wrapper-to-CPS1/CPS2/NeoGeo/IGS classification rule before a shared `ARCADE` directory can be safely stable-merged into the four curated pages.
