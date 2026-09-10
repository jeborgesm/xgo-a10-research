# Arcade Test15 — Classic Arcade routed to external MAME2000

Date: 2026-09-08
Branch: `research-game-list-arcade-expansion`

Status: **offline/CI audit PASS; hardware test pending**

## Architecture

Test15 keeps the existing four stock Arcade pages unchanged:

```text
list 7  CPS1    -> stock XGO FBA
list 8  CPS2    -> stock XGO FBA
list 9  IGS/PGM -> stock XGO FBA
list 10 NeoGeo  -> stock XGO FBA
```

The newly activated fifth page is routed separately:

```text
list 11 Classic Arcade
  -> XGO external-core loader
  -> /cores/mame2000/core.xgc
  -> previously hardware-proven MAME2000 Test12 core
```

This deliberately reuses the already-debugged XGO MAME2000 frontend/input/state integration while avoiding the prior mistake of replacing CPS1.

## Why old MAME2000 performance results do not reject this design

MAME2000 was previously made playable on XGO with Street Fighter II, but CPS1/SFII remained slower than the optimized stock FBA core.

That result applies to comparatively expensive CPS1 emulation.

Test15 instead targets early classic hardware such as Pac-Man/Ms. Pac-Man and eventually Galaga/Frogger/Donkey Kong/Mario Bros./Asteroids. Performance must be measured directly on those much lighter drivers.

## Current-golden baseline

Firmware is composed from golden Test08:

```text
xgo-game-list-test08-all-console-scanner.zip
ZIP SHA-256
9c66fd727a2f894ad692b4868ba8bcee3daf2ff81b4d7eced539f80f2fd2e61e
```

The Test08 console Refresh implementation is retained.

## Loader

A new list-ID-11-only external-core loader is placed in a verified zero cave:

```text
loader address  0x80001900
cave end        0x80002180
loader size     1,325 bytes
loader SHA-256
74046302713cd575a3b3db8abebb00e656c9dd7fb7c33a6bc1b66094c71ebd0e
```

The loader intercepts the stock arcade runtime JAL at `0x80360df8`.

Behavior:

```text
active_list_id == 11
    -> validate/load /cores/mame2000/core.xgc
    -> run external MAME2000

active_list_id != 11
    -> untouched stock arcade runtime 0x80360848
```

Therefore lists 7-10 retain the stock path.

## External core

The core is the previously hardware-proven Test12 MAME2000 XGOC extracted from the private artifact vault:

```text
core bytes      9,127,952
core SHA-256
abf8e4ec6eb7c6d4c2162076e8faa868954a3663b8210c820e1267857b345461
```

This build already contains the repaired XGO joypad filtering and isolated MAME state namespace used during the prior CPS1 experiments.

## Fifth page

`Foldername.ini` uses the hardware-proven:

```text
12 7 0
```

List ID 11 is backed by `Resources/None` with two entries:

```text
Pac-Man.zfb     -> ARCADE/bin/pacman.zip
Ms Pac-Man.zfb  -> ARCADE/bin/mspacman.zip
```

No ROM images are included.

## Exact candidate

```text
xgo-arcade-test15-mame2000-classic.zip
size       7,400,598 bytes
SHA-256
20cba65613463f68fb6d9ee7bf4ef2b7dc1ac2f86423dda4a50620e339fd0097

firmware SHA-256
7ade9be3609ce74add4ffd217e4f48ff077e3ce50420670854315941dc7bff50
```

Private CI:
- workflow run `34188223200`
- workflow artifact ID `10041265802`
- candidate also archived at the private vault root.

## Hardware test

Use MAME2000/MAME 0.37b5-compatible ROM sets where possible.

First test:
1. verify CPS1/CPS2/NeoGeo/IGS still launch through stock paths;
2. enter fifth Arcade;
3. launch Pac-Man;
4. observe video, speed, controls, audio, pause/quit;
5. launch Ms. Pac-Man;
6. record the same.

The most important acceptance signals are:
- full-speed or near-full-speed classic gameplay;
- working sound, unlike stock hidden Pac-Man FBA;
- working controls;
- clean pause/quit return;
- no regression to the four stock Arcade pages.

If successful, next candidate expands list ID 11 to Galaga, Frogger, Donkey Kong, Mario Bros., and Asteroids using MAME2000-compatible sets.
