# Arcade Test11 — Pac-Man audio A/B path diagnostic

Date: 2026-09-07
Branch: `research-game-list-arcade-expansion`

Status: **hardware candidate; NOT golden**

## Purpose

Test10 proved Pac-Man gameplay works from newly activated list ID 11 but is silent.

Static comparison now shows the Pac-Man frame routine reaches the same shared stock FBA sound-output helper used by other compiled arcade drivers. Therefore the next question is whether:

1. list ID 11 is missing some frontend/audio initialization that the vendor only configured for IDs 7..10; or
2. the compiled Pac-Man/Namco sound path itself is incomplete/broken in the XGO FBA payload.

Test11 performs a direct A/B comparison with the exact same `pacman.zip`.

## Package behavior

Test11 preserves Test10's fifth Arcade page and Pac-Man entry.

It additionally stable-appends the same `Pac-Man.zfb` to the existing CPS1 catalog triplet (list ID 7), producing a temporary 27th CPS1 entry.

Both list entries resolve to:

`ARCADE/Pac-Man.zfb -> ARCADE/bin/pacman.zip`

No ROM is included.

## Hardware procedure

1. Launch Pac-Man from the fifth Arcade page and reconfirm silent gameplay.
2. Quit through the normal pause menu.
3. Open the first/CPS1 Arcade page.
4. Launch the appended Pac-Man entry there.
5. Compare sound.

Interpretation:

```text
CPS1 page has sound; fifth page silent
 -> list ID 11 is missing/incorrect frontend audio initialization.

Both pages silent
 -> Pac-Man/Namco sound implementation itself is absent/incomplete/broken
    in this stock XGO FBA build.

CPS1-page launch fails before gameplay
 -> list ID influences more than presentation/audio; trace stock subtype setup.
```

## Exact candidate

```text
xgo-arcade-test11-pacman-audio-ab.zip
size       4,923,915 bytes
SHA-256    a1a77ae81427b4623023419d0d55b74a08ff13224528ba736a02a23d6de42976
```

Temporary CPS1 triplet:

```text
Resources/mswb7.tax   27 entries  SHA-256 f08b5e1e794f888d675157ba18cab5c8873fab4cc8aa3b42281d53f9305e7c22
Resources/msdtc.nec   27 entries  SHA-256 bd67aa0aee35847e659f6dd9164defd75617c290fb6e24cd0c8ff4f48f448570
Resources/mfpmp.bvs   27 entries  SHA-256 dff3a96d079efe4630c9690cf26d092fee862909e5571e08b10206fc95e85264
```

This CPS1 insertion is diagnostic only and must not be treated as the eventual Classic Arcade organization.
