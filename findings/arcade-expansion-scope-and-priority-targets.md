# Arcade expansion scope and first targets

Date: 2026-09-07
Branch: `research-game-list-arcade-expansion`

Status: **active research branch**

## Protected baseline

This branch starts from merged main commit:

`a1bf54e96fc28b721a38d6920f0d4557dbd99730`

That commit includes the golden Test08 full console scanner milestone. The six-console FC/SFC/MD/GB/GBC/GBA Refresh path is protected and must not regress.

Golden artifact:

```text
game-list-test08-full-console-scanner
xgo-game-list-test08-all-console-scanner.zip
ZIP SHA-256      9c66fd727a2f894ad692b4868ba8bcee3daf2ff81b4d7eced539f80f2fd2e61e
firmware SHA-256 45831b0ea3c9ae336d82b240e6afe27167e5e83b88037152af237ab758ca1444
```

## Primary objective

Extend on-device Refresh and game launching to Arcade.

Two related but distinct goals:

1. discover and stable-merge additional games into the existing curated Arcade pages;
2. add playable arcade families/titles that are not represented by the current CPS1/CPS2/NeoGeo/IGS organization.

## Existing XGO Arcade groups already confirmed

The current stock resource-map identities are:

```text
list 7   CPS1     mswb7.tax  msdtc.nec  mfpmp.bvs
list 8   CPS2     kjbyr.tax  djoin.nec  ke89a.bvs
list 9   NeoGeo   rmapi.tax  pcadm.nec  ntdll.bvs
list 10  IGS      subst.tax  aepic.nec  sensc.bvs
```

The physical card uses a shared `/ARCADE` directory, so blindly appending every discovered `.zfb`/archive to every page is unsafe. The first archaeology target is exact wrapper/content-family classification.

## User-priority classic arcade targets

Treat the following games as concrete compatibility milestones:

```text
Asteroids
Pac-Man
Ms. Pac-Man
Donkey Kong
Mario Bros.
Frogger
Galaga
```

These titles are intentionally important because they exercise arcade hardware families outside the current CPS1/CPS2/NeoGeo/IGS organization.

Likely family diversity means a single existing CPS/NeoGeo path should not be assumed sufficient.

## Research sequence

1. Fully map `/ARCADE` inventory versus the four existing filename catalogs.
2. Recover the exact stock `.zfb` / archive launch classifier and any embedded system/driver identifiers.
3. Determine how existing CPS1/CPS2/NeoGeo/IGS files are distinguished at launch.
4. Build a safe table-driven Arcade Refresh path for the existing four pages using stable append and preserved indices.
5. Audit stock FBA/MAME-era core code and sibling firmware for driver coverage of classic non-CPS/NeoGeo games.
6. Specifically test whether the shipped arcade emulator contains drivers for the seven priority titles even though the frontend does not expose them.
7. If stock coverage exists, expose those games through a new or repurposed arcade list/page without disturbing existing list IDs.
8. If stock coverage does not exist, evaluate a lightweight external arcade core, with MAME2000/FBA-family lineage as the first candidate surface because the project already has native arcade-core integration experience.
9. Preserve existing controller mapping, pause/quit behavior, audio timing, and Test08 Refresh behavior.

## UI/list strategy constraint

Do not force unrelated classics into CPS1/CPS2/NeoGeo/IGS pages merely to avoid frontend work.

If the games require a fifth/general Arcade page, investigate the inherited fifth `ARCADE` entry/list-ID-11 path already identified in the firmware before creating a completely new frontend screen. The stranded/inherited fifth arcade slot may provide the least-invasive native presentation path.

## Deferred work

Box-art generation/association for newly discovered games is explicitly lower priority than Arcade expansion.

Transaction-safe catalog recovery remains important, but Arcade archaeology and compatibility classification are the immediate branch focus requested by the user.
