# Hardware Test 03 candidate — CPS1 Core #3 on top of hardware-passed Test 02

Status: **READY FOR PHYSICAL XGO TEST**

## Baseline discipline

This candidate is composed from the exact hardware-passed Test 02 package, not from stock firmware and not from mapper v19 alone.

Preserved baseline:

```text
Test02 ZIP SHA-256
6c8fec790fb8a3d2f93e3d405912aca46d4b1b6db6609775faea74ffdde95869

Test02 bisrv.asd SHA-256
8db8d091f7896e0847d63455ec325bdc9889a2caeebd3d37525c0005006a226a

Mapper-v19 gpapi.bvs SHA-256
759cc078816e6b865ac177ca39a37bb542ae5f64bbfbf0c0cb10f230532950c8

Snes9x2005 core.xgc SHA-256
ee694b5989e1d056f73de99a47588f124caa2df9b5e8c751862c92adb7a543bf
```

## Selected CPS1 core

```text
madcock/fbalpha2012_cps1
commit 5714c8dc311f4dda6e54533bc8dd901a29700635
FB Alpha 2012 CPS-1 v0.2.97.28
```

Why this core:

- CPS1-specialized rather than full-system FBNeo;
- maintained HC15xx/SF2000 build target already exists;
- MIPS32 little-endian soft-float Codescape build matches XGO;
- built-in libretro optimizations and speedhacks;
- RGB565 frontend support;
- 11025-Hz SF2000 audio profile;
- standard libretro serialization;
- exact six-button Street Fighter layout already mapped.

## Successful Core #3 build

Workflow run:

```text
33840206615
artifact 9924662630
artifact digest sha256:1dde42e1426aa1280c0561c98475a8dfff6ee17dfc1d4bf0fb298a72832df29d
```

Core:

```text
core-fbalpha2012-cps1.xgc
SHA-256 b11ae69186fdef1e10bbd21e9a7dcee51782a41ad3de0b7ec2018fea18138c5e

payload   2,202,432 bytes
runtime   3,086,056 bytes
headroom 10,393,368 bytes
undefined symbols 0
```

The C++ core required one freestanding CRT anchor, `__dso_handle`, because XGOC links with `-nostartfiles`. Static constructors continue to run through the already-proven `__libc_init_array()` entry path.

## CPS1-local environment compatibility

FBA2012 CPS1 contains an unsafe frontend assumption: after obtaining save/system directories it calls `log_cb()` without checking for NULL.

The proven NES/SNES environment shim deliberately returns false for `GET_LOG_INTERFACE`.

Rather than modify that hardware-passed common behavior, Core #3 adds a CPS1-only wrapper that returns a no-op external logger and delegates every other command to the existing minimal shim.

This preserves the regression boundary around NES/SNES.

## Content contract

Unlike FCEUmm/Snes9x2005 memory-load mode, FBA2012 CPS1 requires the original ZIP path:

```text
need_fullpath = true
valid_extensions = zip
```

It derives the arcade driver from the ZIP basename and reopens the archive through filesystem calls to locate its constituent ROMs.

Therefore Core #3 keeps the stock XGO filename and uses the already-proven external newlib -> stock filesystem bridge.

A failure to load a particular ZIP may be a FBA 0.2.97.28 ROM-set/basename mismatch rather than an external-runtime failure.

## Independent loader cave

Test 02 already contains:

- mapper-v19 injected code in the early firmware cave;
- relocated SNES loader beginning at `0x80002230`.

The exact Test 02 image leaves another zero-filled cave:

```text
0x80002780 .. 0x80002fff
2,176 bytes
```

Core #3 uses only that new cave.

CPS1 loader:

```text
address    0x80002780
size       1,365 / 2,176 bytes
SHA-256    06bc1a0efbd7d6f04f4f2d5544cfcb50068d0e866ebb5c7785f77e2b94b0d739
GP refs    0
fallback   stock run_fba @ 0x8035e4b4
core path  /mnt/sda1/cores/fbalpha2012_cps1/core.xgc
```

Stock Arcade/FBA dispatch site:

```text
runtime 0x80360e00
ASD     0x00360e00
stock   jal 0x8035e4b4
new     jal 0x80002780
```

## Test 03 combined image

```text
bisrv.asd SHA-256
dfa9898368b697e91b2aff8cf83f819660c3e29fa9a4d3b2bd12f8614faf9b55

LCFG CRC-32/MPEG-2
0x497b390f

Test03 ZIP SHA-256
3755cd56e04a33ae9a817ccd8dc4dd3a199db0a228258e3f400ebee3613fbb73
```

## Regression invariant

Byte-level comparison against exact Test 02:

```text
unexpected changed bytes = 0
```

Explicitly preserved unchanged:

- mapper-v19 injection bytes;
- mapper-v19 resource;
- relocated Snes9x2005 loader;
- SNES dispatch JAL;
- Snes9x2005 XGOC;
- all unrelated firmware code/data.

Permitted Test03 changes are only:

1. CPS1 loader bytes at `0x2780...`;
2. CPS1/FBA dispatch JAL at `0x00360e00`;
3. LCFG CRC field;
4. new `/cores/fbalpha2012_cps1/core.xgc` file.

No `Firmware.upk` or SPI-NOR updater material is included.

## Street Fighter II input contract

The core maps CPS1 six-button fighting controls as:

```text
Y = Weak Punch
X = Medium Punch
L = Strong Punch

B = Weak Kick
A = Medium Kick
R = Strong Kick
```

Coin and Start map through Select and Start.

This is also compatible with mapper-v19's six remappable physical controls.

## Hardware gate

Primary experiment: launch the same Street Fighter II CPS1 ZIP that exhibits severe stock frame dropping.

Observe:

1. does it load;
2. frame pacing and animation visibility versus stock;
3. input latency/responsiveness;
4. six-button correctness;
5. audio speed/stability;
6. Start+Select -> pause menu;
7. Mapper still present and functional;
8. SNES still launches externally afterward;
9. NES remains normal afterward.

The goal is not merely "CPS1 boots." The success criterion is a materially better SFII experience **without regression of the Test 02 baseline**.
