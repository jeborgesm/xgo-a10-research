# Arcade Test12 — classic-driver/audio matrix

Date: 2026-09-07
Branch: `research-game-list-arcade-expansion`

Status: **hardware candidate; NOT golden**

## Purpose

Test11 proved Pac-Man remains silent even when launched from known-good list ID 7, so the fifth Arcade page is not the primary audio problem.

Test12 broadens the probe to multiple classic drivers that are compiled into the shipped XGO FBA payload.

The fifth Arcade page contains:

```text
Pac-Man       -> ARCADE/bin/pacman.zip
Ms Pac-Man    -> ARCADE/bin/mspacman.zip
1942          -> ARCADE/bin/1942.zip
Arkanoid      -> ARCADE/bin/arkanoid.zip
Pooyan        -> ARCADE/bin/pooyan.zip
Mr Do         -> ARCADE/bin/mrdo.zip
Route 16      -> ARCADE/bin/route16.zip
```

No ROM images are included.

## Why these games

Pac-Man / Ms Pac-Man exercise the now-proven but silent Pac-Man-family path.

1942, Arkanoid, Pooyan, Mr Do and Route 16 are independent classic-era drivers with different board/sound architectures. If any of them produce sound, the silence is likely specific to the Pac-Man/Namco path rather than a general hidden-driver problem.

## Exact candidate

```text
xgo-arcade-test12-classic-driver-matrix.zip
size       4,923,909 bytes
SHA-256    885d04cfdbb4697997f8b1130231bcc24ae62d063a066712e1794fe8607721ca
```

Golden Test08 firmware remains unchanged. The Test10 fifth-section activation remains in place.

Artwork is intentionally blank.

## Hardware matrix

For each compatible user-supplied ROM set, record:

```text
title | launches | gameplay | audio | controls | pause/quit
```

Interpretation:

- Pac-Man/Ms Pac-Man silent but another classic driver audible -> Namco/Pac-Man sound path defect.
- all hidden classic drivers silent -> broader vendor wrapper/core audio integration defect for dormant drivers.
- some hidden drivers fail to launch -> classify compiled-but-incomplete/unsupported families separately from working hidden drivers.
