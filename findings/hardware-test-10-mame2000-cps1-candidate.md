# Hardware Test 10 candidate — MAME2000 CPS1, core-only swap

Status: **READY FOR PHYSICAL TEST**

## Why Test 10 exists

FBA2012 hardware Tests 08/09 established that:

- the corrected CPS1-only list gate works;
- the stock-derived arcade ZIP path works far enough for CPS1 initialization;
- input polling is not the first-frame blocker;
- FBA2012 stalls inside/under `BurnDrvFrame()`.

Cross-codebase evidence then showed that the sibling HC15xx project classifies FBA2012 as "working but major issues, not to release" while MAME2000 is in its "fully working" set.

## Regression strategy

Test 10 deliberately does **not** modify firmware or the CPS1 loader.

It starts from the existing Test 08 package and replaces only:

```text
/cores/fbalpha2012_cps1/core.xgc
```

with a MAME2000 XGOC.

The directory name is temporarily misleading. This is intentional: the first MAME2000 test should not introduce another loader/firmware variable.

Unchanged:

- mapper v19 firmware/resource;
- NES path;
- external Snes9x2005;
- CPS1-only list-ID gate;
- CPS2/IGS/Neo Geo stock fallback;
- corrected arcade runtime hook;
- stock arcade cleanup.

## MAME2000 image

```text
madcock/libretro-mame2000
231929ab69e7538bc1d98f59634b8d7fee2ddde7

libco support:
madcock/libretro-common
9362316bf1da38160b324a1515bfb83e44ebd7af
```

Linked result:

```text
undefined symbols  0
payload            9,127,984
runtime           10,510,824
headroom           2,968,600

XGOC SHA-256
353a749f677b68edf67dba52bea571b10de54e7c781cf675be6dfb69dd576761
```

## Package identity

```text
xgo-core3-cps1-test10-mame2000-v19-snes.zip
SHA-256
645820284ee52e345b10f69ffded9ba18825a9ee73765dc46c0eb554da2a7f4c
```

Firmware in package:

```text
16233cbb0d7b7e5a90d72a0eed04b873a3754bcdbaaedcea64fc1b3b972e3f1f
```

Mapper resource:

```text
759cc078816e6b865ac177ca39a37bb542ae5f64bbfbf0c0cb10f230532950c8
```

SNES core:

```text
ee694b5989e1d056f73de99a47588f124caa2df9b5e8c751862c92adb7a543bf
```

## ROM compatibility note

MAME2000 uses MAME 0.37b5-era CPS1 filenames, but its ROM loader has an explicit CRC fallback.

If opening the expected filename fails, `readroms()` retries with the expected CRC rendered as eight hexadecimal characters. `load_zipped_file()` accepts either a filename match or an archive-member CRC match.

Therefore the XGO/FBA-style archive can still work despite renamed members if the underlying ROM data matches the expected CPS1 set.

## Hardware acceptance

1. CPS2 remains stock and quits normally.
2. SFII starts under MAME2000.
3. SFII reaches gameplay rather than first-frame freeze.
4. Measure perceived smoothness/input response versus stock.
5. Pause-menu QUIT returns cleanly.
6. Second CPS1 launch works.
7. Mapper remains available.
8. Snes9x2005 remains functional.

MAME2000 reports zero-size libretro serialization; save-state support is explicitly deferred for this first candidate.
