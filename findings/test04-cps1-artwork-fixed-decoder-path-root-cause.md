# Test04 CPS1 artwork root cause — inherited fixed decoder pathname geometry

Date: 2026-09-26
Branch: `research-arcade-refresh-four-family`
Status: **BIN ROOT CAUSE CLOSED; repair design pending offline audit**

## New HW/filesystem observation

The physical Test04 SD card was inspected after the failed 1941 artwork import.

`/ARCADE/CPS1/art/` contains:
- `1941.jpg` — original source retained;
- `.xgo.jpg` — temporary prepared JPEG retained;
- no `.xgo.rgb565`.

The exact source image is an ordinary baseline JFIF JPEG and is not progressive.

This proves artwork discovery and preparation advanced far enough to create the temporary JPEG. The failure is after source discovery and before successful RGB565 scratch output.

## Exact materializer identity

User supplied the physical Test04 `/ARCADE/CPS1/refresh.xgc`:
- size `0x101F08`
- SHA-256 `301df6494c89928cf615a918b76f81d4c0774d864cd45c77cacc2e145fed3f28`.

The decoder tail is byte-identical to the golden worker and the call at `+0x0730 -> 0x87100000` is intact.

## Root cause

The inherited JPEG worker contains fixed private pathname storage in its tail. The golden low materializer populates those private fields using copy loops whose destination/end geometry is hard-coded for the shorter ancestral scratch paths.

Test04 correctly retargeted the **source literals** to:
- `/mnt/sda1/ARCADE/CPS1/art/.xgo.jpg`
- `/mnt/sda1/ARCADE/CPS1/art/.xgo.rgb565`

but preserved the ancestral fixed copy-bound constants around the decoder preparation sequence, including the bounds formed around runtime `0x87101E64` and `0x87101E6F`.

Path lengths demonstrate the incompatibility:

| scratch path | chars |
|---|---:|
| `/mnt/sda1/FC/art/.xgo.jpg` | 25 |
| `/mnt/sda1/FC/art/.xgo.rgb565` | 28 |
| `/mnt/sda1/ARCADE/CPS1/art/.xgo.jpg` | 34 |
| `/mnt/sda1/ARCADE/CPS1/art/.xgo.rgb565` | 37 |

The Arcade specialization therefore lengthened the low-helper source strings without correspondingly changing the decoder-private pathname geometry.

This is consistent with the exact physical residue:
- source `1941.jpg` exists;
- prepared `.xgo.jpg` exists;
- decoder output `.xgo.rgb565` does not;
- materializer subsequently takes its established black-preview fallback.

## Evidence classification

**HW/filesystem:** source and `.xgo.jpg` present, `.xgo.rgb565` absent, generated ZFB preview black.

**BIN:** exact Test04 materializer retains golden decoder and decoder call; CPS1 source literals are live; decoder-preparation copy loops retain fixed ancestral end-address geometry.

**Conclusion:** Test04 artwork failure is caused by incomplete path retargeting at the decoder-private pathname boundary, not by source stem lookup, JPEG format, decoder replacement, preview-copy loop, ZFB finalizer, or launcher.

## Repair rule

Do not modify the JPEG decoder algorithm or Arcade finalizer.

The repair must preserve the golden decoder code and provide decoder pathname strings within proven-safe storage geometry. Candidate approaches must be compared offline before selection. Prefer the smallest mechanism that avoids lengthening the decoder-private path fields at all—for example, a short scratch namespace—over expanding/relocating opaque decoder-private storage without proof.

No hardware candidate is authorized by this finding alone.
