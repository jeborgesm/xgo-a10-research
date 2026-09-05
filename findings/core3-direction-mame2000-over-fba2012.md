# Core #3 direction change — MAME2000 preferred over FBA2012 for CPS1

Status: **ARCHITECTURAL DECISION BASED ON CROSS-CODEBASE EVIDENCE**

## Hardware evidence against FBA2012

Tests 08 and 09 established:

- the corrected CPS1-only list gate works;
- CPS2/IGS/Neo Geo remain on stock;
- the real XGO arcade content path can be resolved;
- FBA2012 initializes CPS1 far enough for SFII to display its board self-test;
- disabling `poll_input()` does not change the freeze;
- the remaining stall is inside the first `BurnDrvFrame()` path, likely at or below 68000/Z80/device execution.

Other CPS1 games remain black at the same effective first-frame boundary.

## Comparative SF2000 evidence

The original `madcock/sf2000_multicore` project classifies its cores explicitly.

For FBA2012:

```text
#working but major issues, not to release
# ... fbalpha2012 ...
```

For MAME2000:

```text
#fully working
make CONSOLE=m2k CORE=cores/libretro-mame2000
```

This is a much stronger signal than simple build compatibility.

The current SF2000/GB300 core catalog still pins the same dedicated FBA2012 CPS1 commit used by XGO tests:

```text
madcock/fbalpha2012_cps1
5714c8dc311f4dda6e54533bc8dd901a29700635
```

There is no newer hidden CPS1-specific fork in that catalog that supersedes it.

## MAME2000 properties relevant to XGO

Pinned SF2000-family core:

```text
madcock/libretro-mame2000
231929ab69e7538bc1d98f59634b8d7fee2ddde7
```

It provides:

- explicit `platform=sf2000` Codescape MIPS32 soft-float build;
- RGB565 output;
- six-button joypad descriptors;
- configurable audio rates including 11025 Hz;
- frameskip controls;
- CPS1/SFII support through the classic MAME 0.37b5 driver;
- full-path ZIP loading.

The major compatibility risk is ROM-set age: MAME2000 expects MAME 0.37b5-era filenames/CRCs, while the XGO's existing `ARCADE/bin/*.zip` sets were built for its embedded FBA lineage.

## Decision

Do not keep modifying the shared XGO runtime to rescue FBA2012.

Preserve FBA2012 tests as evidence and switch the next CPS1 candidate to MAME2000.

Reuse the already-closed XGO architecture:

```text
active list ID 7
 -> CPS1-only external loader
 -> stock-resolved <ARCADE>/bin/<game>.zip path
 -> MAME2000 external core

list IDs 8/9/10
 -> untouched stock arcade wrapper
```

Mapper v19, NES, SNES, stock CPS2/IGS/Neo Geo and stock arcade cleanup remain immutable baseline requirements.

## First MAME2000 gates

1. build exact pinned MAME2000 SF2000 archive;
2. audit undefined symbols and XGOC footprint;
3. force/advertise XGO-compatible 11025-Hz audio through the environment shim;
4. verify RGB565 and input callbacks;
5. inspect SFII expected 0.37b5 ROM filenames/CRCs;
6. determine whether the XGO `sf2.zip` is directly compatible or requires a separate MAME2000 ROM-set directory;
7. only then generate a hardware package.
