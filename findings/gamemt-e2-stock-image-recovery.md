# GameMT E2 stock-image recovery lead

Date: 2026-09-07
Status: **live public share index located; payload not yet acquired**

## Major new result

The previously identified `Gamemt-e2.img` is not merely an old filename preserved in a dead search index.

The current Xuebapan resource page states:

```text
Gamemt-e2.img 28.5GB
```

and, critically, reports:

```text
File set size: 276.4GB
Time: 2026-02-27
Extraction code: 9CD6
Network-disk link valid, can access
Go to Baidu Netdisk download
```

Source:
https://www.xuebapan.com/info/52157fb9f60fb68dccd4c4f4bafce7cb.html

The page describes itself as an index/crawler of publicly shared network-disk links rather than the file host.

## Why this matters

This materially upgrades the E2 firmware target:

Previous status:
- evidence that a 28.5GB E2 image once circulated.

Current status:
- a **recently indexed, reportedly live Baidu Netdisk share** containing that exact image exists as of the 2026-02-27 resource set;
- the extraction code is publicly exposed as `9CD6`;
- the image sits alongside other stock/handheld images rather than being a textual reference.

The full 28.5GB image is unnecessary for our immediate goal. The high-value target is the E2 application/resource layer, especially any equivalent of:

```text
bios/bisrv.asd
Resources/
Foldername.ini
```

## Recovery plan

If the Baidu share can be accessed:

1. inspect archive/image contents before copying ROM payloads;
2. extract only filesystem metadata and firmware/resource files needed for comparative archaeology;
3. hash all recovered files;
4. identify partition/FAT layout;
5. compare application image against:
   - XGO A10;
   - DY19;
   - SF2000 1.71;
   - GB300 v1/v2;
   - X60;
6. search for XGO scanner signatures, mapper state machine, emulator-core strings and game-list code.

## Exact comparison targets

### Application identity
- LCFG header
- application length
- entry/load geometry
- build timestamp
- Libcore/SDK/compiler strings
- H1512 identification strings

### UI / game database
- Foldername.ini
- .tax/.nec/.bvs equivalents
- Zxx packaged-ROM formats
- resource filenames and sizes
- pause-menu option count
- mapper/keymap resource structures

### Emulator layer
- FCEUmm
- Snes9x 2005
- gpSP
- PicoDrive
- FBA
- arcade ROM-loading path
- scheduler/audio/frame pacing

### Hardware adaptation
- display initialization
- GPIO controller scanner
- RF driver
- battery ADC
- power-bank behavior
- external-controller paths

## Evidence discipline

The Xuebapan page says the Baidu link is valid, but the actual 28.5GB payload has **not** been downloaded or hash-verified by this project. Until that happens, do not claim possession of the E2 firmware.

This is nevertheless the strongest recoverable sibling-firmware lead found so far.
