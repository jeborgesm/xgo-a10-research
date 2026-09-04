# XGO stock arcade emulator exact source lineage closed

Status: **CONFIRMED TO EXACT PUBLIC GIT COMMIT**

## Firmware identity

Direct string extraction from the preserved stock XGO `bios/bisrv.asd` yields:

```text
FB Alpha
v0.2.97.42 621e371
```

The abbreviated Git revision is not decorative.

The public repository:

```text
madcock/sf2000-fbalpha
```

contains the exact commit:

```text
621e371e553eb7814f12504b23f78de4715b7d11
```

and at that revision:

```text
src/burn/version.h

VER_MAJOR 0
VER_MINOR 2
VER_BETA  97
VER_ALPHA 42
```

The libretro source at the same revision also defines:

```c
#define FBA_VERSION "v0.2.97.42"
```

Therefore the XGO embedded arcade emulator is directly traceable to this public FB Alpha source revision.

## Why this matters for Core #3

The first external candidate used:

```text
madcock/fbalpha2012_cps1
v0.2.97.28
```

Test 08 proved that candidate can locate the real XGO SFII ZIP and initialize far enough to display the CPS1 self-test, but it stalls before gameplay.

The XGO card's arcade ROM collection was prepared for the embedded `0.2.97.42` lineage. Using a `0.2.97.28` CPS1 ROM database introduces a 14-revision compatibility gap.

The exact-source discovery therefore changes the preferred direction:

**Do not keep bending the frontend around the older 2012 core.**

Instead:

1. build from exact stock source commit `621e371`;
2. preserve the 0.2.97.42 driver/ROM database;
3. specialize the build to CPS1 where practical;
4. retain RGB565;
5. reduce frontend/audio overhead for HC15xx;
6. compare performance with the embedded stock build.

## Performance opportunities visible in exact source

At `621e371`, the libretro frontend uses:

```c
#define AUDIO_SAMPLERATE 48000
#define AUDIO_SEGMENT_LENGTH 801
static uint32_t *g_fba_frame;
```

and `retro_run()` performs a full frame then sends video plus 801 stereo audio frames every emulated frame.

The build already enables:

```text
LIBRETRO_OPTIMIZATIONS = 1
USE_SPEEDHACKS = 1
-O3
RGB565 frontend support
```

So a useful XGO-specific optimization must go beyond merely recompiling with `-O3`.

High-value candidates include:

- CPS1-only driver/source reduction where link topology permits;
- HC15xx-specific 16-bit framebuffer allocation;
- lower audio sample rate / segment size compatible with XGO hardware;
- removal of irrelevant full-FBA frontend features from the CPS1 image;
- potentially controlled CPS1 CPU-cycle reduction only after baseline compatibility is proven.

## Cross-check with current public fork

Current `madcock/sf2000-fbalpha` is 0.2.97.43, only one revision newer than XGO stock.

This repository is therefore far more relevant to XGO arcade archaeology than the older `fbalpha2012_cps1` fork.

## Confidence

**CONFIRMED:** exact stock FBA version = 0.2.97.42.

**CONFIRMED:** embedded abbreviated Git hash = 621e371.

**CONFIRMED:** public commit 621e371 exists in madcock/sf2000-fbalpha.

**CONFIRMED:** that commit's version.h/libretro frontend are 0.2.97.42.

**STRONG CONCLUSION:** XGO's bundled arcade ROM inventory should be treated as a 0.2.97.42-family ROM set.

**NEXT:** build/link audit exact 621e371 against the existing XGO external runtime before any further hardware test.
