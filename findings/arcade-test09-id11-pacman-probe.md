# Arcade Test09 — list-ID 11 / Pac-Man stock-driver probe

Date: 2026-09-07
Branch: `research-game-list-arcade-expansion`

Status: **hardware candidate; NOT golden**

## Goal

Test the least-invasive native Classic Arcade path before patching frontend state tables.

The fifth repeated `ARCADE` menu entry is list ID 11. Its three normal metadata pointers are all the literal filename:

```text
11 -> None / None / None
```

The browser uses the ordinary fixed-list random-access path for these table entries and no dedicated list-ID-11 rejection branch has been identified.

Therefore the first probe supplies a valid `Resources/None` instead of modifying the resource table.

## Why Pac-Man

Direct inspection of the shipped XGO firmware proves that the stock FBA binary contains the Pac-Man driver family.

Representative embedded driver/set identifiers:

```text
pacman
pacmanf
pacplus
puckman
mspacman
mspacmnf
mspacmat
mspacmab
mspacmbe
mspacpls
pacgal
```

Representative embedded ROM descriptors:

```text
pacman.6e
pacman.6f
pacman.6h
pacman.6j
82s123.7f
82s126.4a
82s126.1m
82s126.3m
mspacatk.2
mspacatk.5
mspacatk.6
```

This is executable-driver evidence, not merely a frontend title string.

Canonical identifiers for Galaga, Frogger, Donkey Kong, Mario Bros., and Asteroids were not found in the shipped binary during the same scan. Their upstream FBA support should not be confused with actual inclusion in this XGO build.

## Package

```text
xgo-arcade-test09-id11-pacman-probe.zip
size       4,922,444 bytes
SHA-256    f2b6b2c127effc554f882190648f84ab7cba4a1f026a74a1ccbaf042d0768ba6
```

Golden Test08 firmware is carried forward unchanged.

Added files only:

```text
Resources/None
  size 20
  SHA-256 27387fdfb31fc2d3d14070578782484e85ded64b0f85c49dff9f5dab2d932159
  contents = one stock list entry: Pac-Man.zfb

ARCADE/Pac-Man.zfb
  size 59,920
  SHA-256 5fd31a661e852c07e526d0b762a1154400184fd31723af6ebc279156e1db1aa1
  layout:
      59,904 zero RGB565 thumbnail bytes
      4 zero bytes
      "pacman.zip"
      2 zero bytes
```

No ROM image is included.

## User-supplied requirement

For hardware testing place a compatible legally obtained FBA 0.2.97.42-era ROM set at:

`ARCADE/bin/pacman.zip`

The ZIP basename must remain `pacman.zip`.

## Expected interpretations

### Fifth page appears and Pac-Man launches

This proves:
- list ID 11 can serve as a native general/classic Arcade page;
- `Resources/None` is sufficient to activate it;
- the stock XGO FBA Pac-Man driver is executable;
- future classic-arcade additions can use the existing stock page without frontend restructuring.

### Fifth page appears but launch returns/fails

This still proves list ID 11 is usable. Next isolate:
- exact ROM-set revision/CRC compatibility;
- stock FBA driver selection from archive basename;
- any launch-path assumptions unique to lists 7..10.

### Fifth page remains empty or cannot enter

This proves an additional dormant list-ID-11 gate exists despite the resource table. Then patch the frontend state/table path explicitly.

## Protected behavior

Test09 does not alter:
- golden Test08 firmware;
- FC/SFC/MD/GB/GBC/GBA Refresh;
- CPS1/CPS2/NeoGeo/IGS catalogs;
- audio OSD;
- mapper;
- native SNES/CPS1 scheduler work.

Artwork is intentionally a blank thumbnail and is outside this probe.
