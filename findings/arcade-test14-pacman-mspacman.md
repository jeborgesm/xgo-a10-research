# Arcade Test14 — Pac-Man + Ms. Pac-Man final-night probe

Date: 2026-09-07
Branch: `research-game-list-arcade-expansion`

Status: **hardware candidate; NOT golden**

## Audio-routing decision

The stock XGO audio transport is confirmed as 2-channel, 16-bit PCM. The internal speaker amplifier is separately gated through GPIO L23.

However, the exact branch that distinguishes internal-speaker output from external/AV audio remains unproven. Therefore no global stereo-to-mono patch is included in Test14. This avoids risking loss of external stereo while routing is still unresolved.

## Purpose

Test whether Ms. Pac-Man, from the same compiled Pac-Man driver family already proven executable on XGO, launches from the fifth Arcade section and whether its sound behavior matches Pac-Man.

## Fifth Arcade contents

```text
Pac-Man      -> ARCADE/bin/pacman.zip
Ms Pac-Man   -> ARCADE/bin/mspacman.zip
```

No ROM images are included.

## Exact candidate

```text
xgo-arcade-test14-pacman-mspacman.zip
size       4,922,777 bytes
SHA-256    c5e95c38bc1a9c6d16092c06c2b579b2f077053f58ae25168e93de3ca3e78603
```

Golden Test08 firmware remains unchanged. Test10 fifth-page activation remains via `Foldername.ini = 12 7 0`. No Test13 dual-mono patch is present.

## Hardware procedure

1. Keep the already working `ARCADE/bin/pacman.zip`.
2. Place a compatible legally obtained FBA 0.2.97.42-era `mspacman.zip` at `ARCADE/bin/mspacman.zip`.
3. Open the fifth Arcade section.
4. Launch Ms. Pac-Man.
5. Record:
   - launches/gameplay;
   - controls;
   - sound yes/no;
   - pause/quit behavior.

Interpretation:
- Ms. Pac-Man runs silently too -> strongly reinforces Pac-Man-family/Namco sound-path defect.
- Ms. Pac-Man has audio -> isolate differences in driver init/set selection between Pac-Man and Ms. Pac-Man.
- Ms. Pac-Man fails to launch -> isolate ROM-set compatibility before drawing sound conclusions.
