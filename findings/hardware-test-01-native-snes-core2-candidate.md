# Hardware Test 01 candidate — native Snes9x2005 Core #2

Status: **READY FOR PHYSICAL XGO TEST**

## Package identity

Local staged overlay:

```text
xgo-native-snes-core2-test01.zip
SHA-256 046a6c07ba4bb1684a2810b151167db47f8fef492f874ddfe7e749143daf9bae
```

Contents that affect runtime:

```text
bios/bisrv.asd
SHA-256 d26951d932dc4788b5a5e95ed162c9d89d73dfe5e0b9cb757192aff755e1654f

cores/snes9x2005/core.xgc
SHA-256 ee694b5989e1d056f73de99a47588f124caa2df9b5e8c751862c92adb7a543bf
```

The package also contains a manifest and hardware-test instructions.

It contains **no `Firmware.upk`**, no updater directory and no SPI-NOR programming material.

## Exact candidate architecture

```text
normal stock SNES browser
  -> stock run_game() file discovery/preload
  -> stock SNES dispatch site 0x80360e40
  -> injected GP-free loader @ 0x80001500
  -> /cores/snes9x2005/core.xgc
  -> external Snes9x2005 @ 0x87000000
  -> family 0x08 / stock 11025-Hz SNES profile
  -> stock GP-safe video/audio/input
  -> stock run_emulator()
  -> generic libretro state bridge
  -> stock Select+Start/save UI
```

## Offline gates completed

- exact stock firmware fingerprint verified;
- exact stock SNES dispatch bytes verified;
- family-0x08 11025-Hz branch verified;
- stock loader cave verified zero;
- injected loader builds to 1,359 bytes / 3,200 available;
- injected loader emits no `$gp` references;
- canonical Snes9x2005 XGOC links with zero undefined symbols;
- XGOC payload/runtime/bounds/CRCs validated;
- patched LCFG CRC independently recomputed and verified;
- patched ASD byte-diff contains no changes outside loader/JAL/LCFG CRC regions;
- package contains no updater material.

## Hardware observations requested

Use a disposable clone of the known-good SD card and launch an ordinary known-good SNES ROM from the stock browser.

Record:

1. launch result: gameplay, return-to-menu, freeze or crash;
2. video geometry and color/black level;
3. audio speed/quality;
4. A/B/X/Y/L/R, D-pad, Select/Start behavior;
5. frame pacing/performance versus the embedded stock SNES core;
6. Select+Start exit to stock UI;
7. save and load behavior if gameplay is stable.

A title that visibly performs poorly on the stock embedded core is ideal because Core #2 exists partly to test whether the newer HC15xx Snes9x2005 fork materially improves the XGO's SNES experience.

## Failure interpretation

The guarded loader falls back to untouched stock `run_snes()` for pre-entry failures such as missing/bad XGOC, invalid CRC/bounds, short read or unsafe upper-heap state.

Therefore:

- normal stock SNES gameplay after applying the overlay may indicate guarded fallback;
- a hang/crash/new visual behavior after the loading transition implies execution progressed beyond the pre-entry fallback boundary;
- successful external gameplay would prove the generic runtime with a second real core.

## Provenance

Core/link workflow:

```text
run       33836747646
artifact  9923539928
digest    sha256:318a3ff58285cf82d44db05470710c7a62cb9a3e1f6c889adae20dd91089e2c9
```

Canonical core commit:

```text
madcock/snes9x2005
fa69dd6a3caf279cc1f457e65e360f8b9a3683ed
```
