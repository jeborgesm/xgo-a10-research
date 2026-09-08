# Arcade Test13 — dual-mono audio diagnostic

Date: 2026-09-07
Branch: `research-game-list-arcade-expansion`

Status: **hardware candidate; NOT golden**

## Hypothesis

XGO has one physical speaker, while the stock libretro/FBA transport is confirmed to use:

```text
interleaved stereo signed 16-bit PCM
L16, R16
4 bytes per audio frame
```

The stock frontend copies those stereo frames directly to its PCM ring buffer and does not downmix them first.

Pac-Man is playable but silent through both list ID 11 and list ID 7. One plausible explanation is that its generated audio is present only or primarily on a channel that the XGO's mono output path does not reproduce.

## Patch

Test13 intercepts the call from stock `retro_audio_sample_batch_cb` to `run_sound_advance`.

Only when active list ID is 7 through 11 (Arcade), every stereo frame is rewritten in place:

```text
mono = (left + right) / 2
left  = mono
right = mono
```

Using the average avoids 16-bit overflow/clipping from a raw sum.

All console-system audio paths remain untouched.

## Patch points

```text
retro_audio_sample_batch_cb   0x8035e7d8
original run_sound_advance    0x8035cba0
patched JAL site              0x8035e800
dual-mono shim                0x807db9c0
shim length                   156 bytes
shim SHA-256                  eb8e1b089c06bfd903b84c1b14885cd4aae0fc9b0a0affecb4f2a5cefc3a6184
```

## Exact candidate

```text
xgo-arcade-test13-arcade-dual-mono-pacman.zip
size                          4,922,677 bytes
ZIP SHA-256                   e4fee0238dbce719738a8f49c08c00c658fd7763b46076dc601caddf3dd1b5e6
firmware SHA-256              877bc29ebcab2621d2fafc45026c1c1de340d4609f4ef6fc5c2f7f5c9fe74a7c
LCFG CRC-32/MPEG-2            c97cb138
```

The package preserves Test10's activated fifth Arcade page and Pac-Man entry.
No ROM image is included.

## Hardware test

Use the same compatible `ARCADE/bin/pacman.zip` already proven to launch.

1. Launch Pac-Man from the fifth Arcade page.
2. Check whether any game audio is now audible.
3. Briefly launch one known working CPS1/CPS2/NeoGeo title and confirm its sound remains present.

Interpretation:

```text
Pac-Man gains audio
 -> mono/stereo channel routing was the cause.

Pac-Man remains silent; other Arcade sound remains good
 -> return to Pac-Man/Namco sound-generation initialization.

All Arcade sound fails
 -> dual-mono shim integration is wrong; restore Test10 and inspect callback ABI.
```
