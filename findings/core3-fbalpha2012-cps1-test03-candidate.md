# Core #3 candidate — FB Alpha 2012 CPS-1 layered on hardware-passed Test 02

Status: **OFFLINE BUILD/REGRESSION AUDIT PASS; HARDWARE TEST PENDING**

## Baseline is immutable

Core #3 is built on the exact hardware-passed Test 02 package:

```text
Test02 ZIP
6c8fec790fb8a3d2f93e3d405912aca46d4b1b6db6609775faea74ffdde95869

Test02 combined bisrv.asd
8db8d091f7896e0847d63455ec325bdc9889a2caeebd3d37525c0005006a226a

Mapper v19 gpapi.bvs
759cc078816e6b865ac177ca39a37bb542ae5f64bbfbf0c0cb10f230532950c8

Snes9x2005 core.xgc
ee694b5989e1d056f73de99a47588f124caa2df9b5e8c751862c92adb7a543bf
```

The CPS1 experiment does not rebuild mapper v19 or SNES.

## Chosen CPS1 core

```text
madcock/fbalpha2012_cps1
commit 5714c8dc311f4dda6e54533bc8dd901a29700635
library FB Alpha 2012 CPS-1 v0.2.97.28
```

This is the CPS1-specific core used by the maintained SF2000 Multicore ecosystem.

The SF2000 build profile already matches the HC15xx/XGO execution model:

```text
Codescape mips32-mti-elf 2019.09-03-2
MIPS32 little-endian
soft-float
-G0
-mno-abicalls
-fno-pic
static archive
SF2000 define
RGB565 enabled
```

Its SF2000 libretro frontend uses:

```text
audio sample rate 11025 Hz
video refresh      59.629403 Hz
RGB565             requested/supported
content            CPS1 .zip sets
```

The core has explicit six-button Street Fighter mappings:

```text
Weak Punch    -> Y
Medium Punch  -> X
Strong Punch  -> L
Weak Kick     -> B
Medium Kick   -> A
Strong Kick   -> R
```

which fits the XGO's six remappable physical controls unusually well.

## XGO arcade contract

Static XGO analysis closes the native arcade dispatch used by CPS1:

```text
stock run_game dispatch site   0x80360e00
stock target                   run_fba @ 0x8035e4b4
XGO system family              0x40
```

The external frontend deliberately retains family `0x40` so the stock arcade/FBA run-loop policy remains in effect rather than impersonating NES or SNES.

## Linked Core #3

```text
core-fbalpha2012-cps1.xgc
SHA-256 b11ae69186fdef1e10bbd21e9a7dcee51782a41ad3de0b7ec2018fea18138c5e

payload bytes  2,202,432
runtime bytes  3,086,056
window bytes  13,479,424
headroom       10,393,368
undefined      0
```

## Independent CPS1 loader

To avoid both existing injected regions:

```text
mapper v19 / legacy injected code  ~0x800014a0...
SNES loader                         0x80002230...
```

Core #3 gets another independent verified cave:

```text
CPS1 loader address   0x80002780
loader bytes          1,365
available             2,176
SHA-256
06bc1a0efbd7d6f04f4f2d5544cfcb50068d0e866ebb5c7785f77e2b94b0d739
```

It retains the same guarded XGOC validation / RAMSIZE / IRQ-GP / cache-flush safety model and falls back to untouched stock `run_fba()` on pre-entry failure.

## Combined Test 03 firmware

```text
bisrv.asd
dfa9898368b697e91b2aff8cf83f819660c3e29fa9a4d3b2bd12f8614faf9b55

LCFG CRC-32/MPEG-2
0x497b390f
```

Byte-level regression audit against Test 02:

```text
unexpected changed bytes = 0
```

Permitted new mutations are only:

1. CPS1 loader bytes at `0x2780..`;
2. CPS1 dispatch JAL at ASD `0x00360e00`;
3. LCFG CRC.

Verified unchanged:

```text
mapper-v19 resource     identical
Snes9x2005 XGOC         identical
SNES dispatch/loader    identical
all pre-existing mapper firmware bytes preserved
```

## Test package

```text
xgo-core3-cps1-test03-v19-snes.zip
SHA-256
3755cd56e04a33ae9a817ccd8dc4dd3a199db0a228258e3f400ebee3613fbb73
```

No `Firmware.upk` or SPI-NOR updater material is present.

## Hardware target

The primary performance comparison is **Street Fighter II**.

Acceptance criteria:

1. SFII launches from the ordinary CPS1/arcade path;
2. controls work, especially all six attack buttons;
3. frame pacing/input latency is compared directly with stock;
4. audio remains stable;
5. Start+Select still reaches the mapper/save UI;
6. mapper v19 remains functional and persistent;
7. external Snes9x2005 still launches normally;
8. NES still behaves normally.

A CPS1 performance win is only accepted if Test 02 functionality remains intact.
