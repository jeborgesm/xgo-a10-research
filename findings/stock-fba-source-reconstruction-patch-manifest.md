# Stock HC15xx FBA source-reconstruction patch manifest

Date: 2026-09-05  
Branch: `research-post-mapper-runtime`

## Purpose

This is a **static reconstruction manifest**, not a hardware-test package.

It translates the family-wide stock-FBA archaeology into a source-level model that can be reviewed and compared before another device experiment.

The target is the conserved arcade behavior observed across:

- SF2000 08/03;
- GB300 v2;
- XGO.

It explicitly does **not** resume the failed FBA2012+A68K ROM-bisection direction.

---

## Reconstructed source ancestry

The best current model is:

```text
Aftnet/fbalpha @ 621e371
    provides:
      - FB Alpha v0.2.97.42 engine generation
      - libretro wrapper generation
      - archive/CRC/name ROM loader
      - CPS driver generation
      - input/DIP/state wrapper structure

Dmitry Smagin fba-a320 / Miyoo descendants
    provide:
      - portable C68K core
      - three-way Sek selector
      - C68K default for normal 68000
      - Musashi fallback for non-68000 types
      - A68K optional third backend
      - 22050-Hz handheld tuning ancestry
      - render-suppression catch-up model

HC15xx vendor patch
    provides:
      - 22050 / 367 libretro audio constants
      - doubled framebuffer allocation
      - alternating two-buffer render surface
      - private SetFrameSkip(bool) callback
      - pBurnDraw=NULL on late/skipped render frames
      - conditional video callback
      - stock run_emulator() timing contract
```

No inspected public repository contains this exact combination already assembled.

---

# A. Family-faithful reconstruction

## Base tree

Use:

```text
Aftnet/fbalpha
commit 621e371e553eb7814f12504b23f78de4715b7d11
```

Reason:

The preserved HC15xx binaries identify themselves as:

```text
FB Alpha
v0.2.97.42 621e371
```

and retain the later libretro archive-loader diagnostics found in this source generation.

Do **not** use FBA2012 v0.2.97.29 as the reconstruction base.

---

## Patch 1 — restore the three-way Sek backend model

### Donor

Preferred lineage donor:

```text
dmitrysmagin/fba-a320
or the directly preserved
littlehui/miyoo-emu/fba-a320-miyoo
```

Relevant donor files:

```text
src/burn/sek.cpp
src/burn/sek.h

src/cpu/c68k/c68k.c
src/cpu/c68k/c68k.h
src/cpu/c68k/c68k_ini.c
src/cpu/c68k/c68k_op.c
src/cpu/c68k/c68kmacro.h
```

### Required selector contract

Restore:

```cpp
#define SEK_CORE_C68K 0
#define SEK_CORE_M68K 1
#define SEK_CORE_A68K 2

int nSekCpuCore = SEK_CORE_C68K;
```

### Required SekInit policy

Equivalent to:

```cpp
if (nCount == 0 &&
    nCPUType != 0x68000 &&
    nSekCpuCore != SEK_CORE_M68K)
{
    nSekCpuCore = SEK_CORE_M68K;
}
```

Then dispatch:

```text
0 -> portable C68K
1 -> Musashi
2 -> A68K
```

For ordinary CPS1:

```cpp
SekInit(0, 0x68000)
```

therefore remains on C68K.

### Compatibility surface with 621e371

The old and newer Sek interfaces are already very close.

The 621e371 interface adds only a small number of later helpers beyond the older donor, notably:

```text
SekShouldInterrupt()
SekBurnUntilInt()
SekSetTASCallback()
```

plus typedef/name modernization such as:

```text
int          -> INT32
unsigned int -> UINT32
unsigned char -> UINT8
```

The ordinary CPS1 path uses the long-established Sek API:

```text
SekInit
SekOpen / SekClose
SekReset
SekRun
SekIdle
SekTotalCycles
SekSetIRQLine
SekSetCyclesScanline
SekMapMemory / SekMapHandler
read/write handlers
```

Therefore the donor should be adapted to the 621e371 header/API rather than replacing later driver code.

---

## Patch 2 — use the portable C68K implementation

Important distinction:

The target donor is **not Cyclone ARM assembly**.

FBA-a320 contains the portable C implementation:

```text
src/cpu/c68k/c68k.c
src/cpu/c68k/c68k_ini.c
src/cpu/c68k/c68k_op.c
src/cpu/c68k/c68kmacro.h
```

with APIs such as:

```text
C68k_Init
C68k_Reset
C68k_Exec
```

This is compatible in principle with the MIPS HC15xx target.

Do not substitute the later libretro-lite Cyclone backend merely because it also calls the selector "C68K".

---

## Patch 3 — restore stock arcade audio constants

In the 621e371 libretro wrapper, replace:

```cpp
#define AUDIO_SAMPLERATE      48000
#define AUDIO_SEGMENT_LENGTH  801
```

with the stock-family values:

```cpp
#define AUDIO_SAMPLERATE      22050
#define AUDIO_SEGMENT_LENGTH  367
```

The resulting stock behavior must advertise:

```text
sample_rate = 22050.0
```

through `retro_get_system_av_info()`.

The XGO stock frontend initializes its sound driver from that advertised rate.

---

## Patch 4 — replace single framebuffer with two surfaces

Upstream 621e371:

```cpp
static uint32_t *g_fba_frame;

g_fba_frame =
    (uint32_t*)malloc(width * height * sizeof(uint32_t));
```

Stock-equivalent wrapper state:

```cpp
static uint32_t *g_fba_frames;
static uint32_t *g_fba_frame[2];
static uint32_t *g_fba_active_frame;
static unsigned  g_fba_frame_index;
```

Equivalent allocation:

```cpp
size_t pixels = width * height;

g_fba_frames =
    (uint32_t*)malloc(pixels * sizeof(uint32_t) * 2);

g_fba_frame[0] = g_fba_frames;
g_fba_frame[1] = g_fba_frames + pixels;

g_fba_frame_index = 0;
g_fba_active_frame = g_fba_frame[0];
```

This matches XGO binary behavior:

```text
allocation = width * height * 8 bytes

buffer0 = base
buffer1 = base + width*height*4
active  = base
index   = 0
```

---

## Patch 5 — add the HC15xx private SetFrameSkip contract

Add one non-standard callback entry point:

```cpp
void SetFrameSkip(int skip)
{
    if (skip) {
        g_fba_active_frame = NULL;
        return;
    }

    g_fba_frame_index ^= 1;
    g_fba_active_frame = g_fba_frame[g_fba_frame_index];
}
```

This reconstructs XGO `0x8036bdc0` and the equivalent stock-family hooks:

```text
SF2000 08/03  0x803659cc
GB300 v2      0x80369f2c
XGO           0x8036bdc0
```

GB300's public linker map already labels this callback:

```text
_SetFrameSkip
```

---

## Patch 6 — make retro_run render-conditionally

Upstream 621e371 currently begins each frame with:

```cpp
pBurnDraw = (uint8_t*)g_fba_frame;
```

and always calls:

```cpp
video_cb(g_fba_frame, width, height, nBurnPitch);
```

Stock-equivalent behavior:

```cpp
void retro_run()
{
    ...

    pBurnDraw = (uint8_t*)g_fba_active_frame;

    InputMake();
    ForceFrameStep();

    ...

    if (g_fba_active_frame)
        video_cb(g_fba_active_frame,
                 width,
                 height,
                 nBurnPitch);

    audio_batch_cb(g_audio_buf, nBurnSoundLen);

    ...
}
```

This preserves:

```text
late frame:
    CPU/game emulation = yes
    audio generation    = yes
    drawing             = no
    video callback      = no
```

---

## Patch 7 — retain the 621e371 archive loader

Do **not** replace `open_archive()`, `archive_load_rom()`, or the later libretro ROM-selection logic with the old SDL frontend's loader.

The XGO stock binary contains the later loader diagnostics:

```text
[FBA] Archive: %s
[FBA] Failed to find archive: %s, let's continue with other archives...
[FBA] Parsing archive %s.
[FBA] Searching ROM at index ...
[FBA] Using ROM at index ... with wrong CRC ...
[FBA] Cannot find driver.
[FBA] Game %s is not marked as working
```

Those strings and their control flow belong to the later libretro archive-loader family.

Therefore:

```text
621e371 loader stays
FBA-a320 CPU/render ancestry is grafted into it
```

not the reverse.

---

## Patch 8 — expose SetFrameSkip to the HC15xx wrapper installer

The XGO stock arcade wrapper installs:

```text
gfn_retro_get_region      <- stock FBA retro_get_region
gfn_get_system_av_info    <- stock FBA retro_get_system_av_info
gfn_retro_load_game       <- stock FBA retro_load_game
gfn_retro_unload_game     <- stock FBA retro_unload_game
gfn_retro_run             <- stock FBA retro_run
gfn_frameskip             <- stock FBA SetFrameSkip
```

The private extension is only:

```c
void SetFrameSkip(int skip);
```

No second adjacent arcade-private performance hook was found.

An eventual XGO external wrapper therefore needs to install this function into the existing stock:

```text
gfn_frameskip = 0x80c33ae0
```

slot along with the normal core callbacks.

---

# B. Minimal CPS1-only reconstruction

For a first **source proof**, not a family-complete core, the scope can be smaller.

Required:

```text
621e371 CPS1 driver/archive code
portable C68K backend
22050 / 367
double framebuffer
SetFrameSkip
conditional video callback
stock XGO run_emulator transport
```

Potentially unnecessary for the first CPS1 proof:

```text
A68K backend
non-CPS drivers
68010 / 68EC020 support beyond a Musashi fallback stub
NeoGeo-specific wrapper options
SH2 options
general arcade breadth
```

The key rule is that **C68K must be the actual ordinary CPS1 backend**.

This minimal candidate is conceptually much closer to stock than FBA2012+A68K was.

---

# C. Why this is different from the failed external FBA2012 direction

The failed experimental path was roughly:

```text
FBA2012 v0.2.97.29
    + 32-kHz audio
    + A68K/Musashi-only Sek layer
    + one framebuffer
    + always render
    + always submit video
```

The reconstructed stock contract is:

```text
FBA v0.2.97.42 / 621e371 loader + drivers
    + portable C68K default
    + 22.05-kHz audio
    + double framebuffer
    + adaptive pBurnDraw=NULL catch-up
    + stock HC15xx run_emulator pacing
```

These are not minor tuning differences.

They are different runtime architectures.

---

# D. Static gates before any hardware package

Before producing another device-test archive, the reconstruction should satisfy all of these source/build checks:

1. **C68K execution path**
   - CPS1 `SekInit(0, 0x68000)` selects C68K.
   - generated binary contains no accidental forced-A68K CPS1 path.

2. **Loader provenance**
   - archive loader remains the 621e371-style CRC/name loader.
   - no FBA2012-specific v0.2.97.29 ROM-definition assumptions are silently introduced.

3. **Audio**
   - `nBurnSoundRate = 22050`.
   - `nBurnSoundLen = 367`.
   - AV info advertises 22050.

4. **Frameskip callback**
   - exported `SetFrameSkip(1)` makes draw buffer NULL.
   - `SetFrameSkip(0)` selects alternating surfaces.

5. **retro_run**
   - always executes `BurnDrvFrame()`.
   - always submits audio.
   - submits video only when active frame pointer is non-null.

6. **Framebuffer**
   - exactly two full render surfaces are allocated.
   - no third full-size copy is introduced by the wrapper.

7. **HC15xx integration**
   - normal XGO stock callbacks remain responsible for display/audio/input.
   - `gfn_frameskip` is populated with the reconstructed private hook.

8. **No A68K-bisection dependency**
   - loading/debug strategy does not depend on the abandoned A68K ROM-phase probes.

Only after these gates pass should a hardware candidate be considered.

---

## Current confidence

### Confirmed from stock binaries

- 621e371 identity;
- later libretro archive loader;
- C68K/Musashi/A68K three-way selector;
- C68K ordinary CPS1 path;
- 22050 / 367 audio;
- doubled framebuffer allocation;
- two render surfaces;
- SetFrameSkip private callback;
- NULL draw buffer on skipped render;
- conditional video callback;
- audio continues on skipped render;
- family-wide preservation across SF2000, GB300 v2 and XGO.

### Confirmed from public ancestry

- FBA-a320 defaults C68K/22050/auto frameskip;
- FBA-a320 suppresses drawing by setting `pBurnDraw=NULL` on catch-up frames;
- its C68K donor is portable C, not ARM assembly;
- 621e371 supplies the later archive/libretro wrapper lineage found in stock.

### Still to prove before building

- exact compile-time glue required to adapt the old three-way Sek implementation to all 621e371 typedef/API additions;
- whether any non-CPS driver in the desired build requires the newer Sek helper functions;
- exact binary-size/runtime-memory footprint of the reconstructed CPS1-only source tree on the XGO toolchain.
