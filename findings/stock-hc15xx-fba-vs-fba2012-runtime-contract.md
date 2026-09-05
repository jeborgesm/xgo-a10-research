# Stock HC15xx FBA vs upstream FBA2012: runtime-contract delta

Date: 2026-09-05
Branch: `research-post-mapper-runtime`

## Scope

This note follows the family-wide stock-FBA comparative archaeology direction in `HANDOFF-CURRENT.md`.

It does **not** resume A68K ROM bisection.

The goal is to identify why upstream FBA2012 is not behaviorally equivalent to the stock SF2000/GB300/XGO arcade runtime even when both can be described loosely as "old FinalBurn Alpha".

## Stock family is a vendor hybrid, not plain FBA2012

Three stock firmwares now show the same arcade architecture:

```text
SF2000 08/03
GB300 v2
XGO
```

All carry the identity:

```text
FB Alpha
v0.2.97.42 621e371
```

but their 68000 integration does **not** match upstream `Aftnet/fbalpha` at commit `621e371`.

Upstream `621e371` supports the ordinary historical pair:

```text
Musashi
A68K
```

The stock HC15xx binaries instead contain the older handheld-style three-way selector:

```text
0 = C68K / Cyclone
1 = Musashi
2 = A68K
```

with the same non-68000 fallback logic seen in the FBA-a320 lineage.

This indicates a vendor hybrid:

```text
later FBA engine/wrapper generation
        +
older handheld C68K-enabled Sek integration
        +
HC15xx-specific frontend/runtime patches
```

## Upstream FBA2012 differs even more

The upstream `libretro/fbalpha2012` CPS1 core at commit:

```text
0ce31536bef3162fe7e69ff5f555334ec4913cef
```

identifies itself as:

```text
FB Alpha 2012
v0.2.97.29
```

and has no C68K backend in its `m68000_intf.cpp`.

Its CPU selection model is:

```cpp
if (BUILD_A68K && bBurnUseASMCPUEmulation && nCPUType == 0x68000)
    use A68K;
else
    use Musashi;
```

Therefore FBA2012 cannot reproduce the stock family's ordinary CPS1 CPU path merely through a runtime option. The stock path's default backend—C68K—is absent.

## Audio workload differs

Upstream FBA2012 hardcodes:

```cpp
#define AUDIO_SAMPLERATE      32000
#define AUDIO_SEGMENT_LENGTH  534
```

Stock HC15xx FBA uses:

```text
22050 Hz
367 samples/frame
```

and advertises `22050.0` through its stock `retro_get_system_av_info()`.

The XGO frontend then initializes the hardware sound-driver path from that advertised sample rate.

Thus stock arcade generates substantially less audio work than upstream FBA2012.

## FBA2012 lacks the stock private frameskip contract

Upstream FBA2012's ordinary `retro_run()` does:

```cpp
pBurnDraw = (uint8_t*)g_fba_frame;

InputMake();
ForceFrameStep();

video_cb(g_fba_frame, width, height, nBurnPitch);
audio_batch_cb(g_audio_buf, nBurnSoundLen);
```

Every call:

- enables drawing;
- executes the frame;
- submits video;
- submits audio.

There is no stock-family `gfn_frameskip(bool)` entry point.

## Stock HC15xx FBA has render-only adaptive frameskip

The stock frontend detects when execution is more than one frame period late and calls the active private frameskip hook.

For stock FBA:

```text
frameskip(1):
    pBurnDraw source buffer = NULL

frameskip(0):
    toggle between two render buffers
    pBurnDraw source buffer = selected buffer
```

The subsequent `retro_run()` still executes the emulated frame and audio.

When the draw pointer is NULL:

- CPU/game emulation continues;
- audio continues;
- expensive FBA drawing is suppressed;
- video callback is omitted.

This exact private hook is conserved at:

```text
SF2000 08/03  0x803659cc
GB300 v2      0x80369f2c
XGO           0x8036bdc0
```

## Scheduler policy is conserved despite frontend evolution

SF2000 and GB300 v2 `run_emulator()` are not byte-identical functions; GB300 v2 contains substantial later frontend/menu/state additions.

However their performance-critical timing blocks remain aligned:

- same 50/60-Hz cadence setup;
- same elapsed-time accumulator model;
- same late-state boolean generation;
- same per-frame private frameskip callback contract.

XGO independently implements the same behavior.

Therefore there is no evidence that XGO is missing a later GB300-specific "magic scheduler".

## Delta matrix

| Runtime property | Stock HC15xx FBA | Upstream FBA2012 CPS1 |
| --- | --- | --- |
| Engine identity | 0.2.97.42 / 621e371 vendor hybrid | 0.2.97.29 |
| Ordinary 68000 backend | C68K | Musashi or A68K only |
| Backend selector | 0=C68K, 1=Musashi, 2=A68K | boolean A68K-vs-Musashi |
| Audio rate | 22050 Hz | 32000 Hz |
| Audio segment | 367 | 534 |
| Frontend adaptive lateness check | yes | external frontend dependent |
| Private render-skip hook | yes | no |
| Skip behavior | pBurnDraw=NULL, emulation/audio continue | no equivalent |
| Render buffering | alternating two stock buffers | one g_fba_frame |
| Video callback on skipped frame | omitted | always called |
| CPU-speed-adjust override from XGO frontend | no | core option exists but irrelevant to stock contract |

## Consequence for the failed external-core direction

The prior external FBA2012+A68K work attempted to improve performance by changing the CPU backend while retaining a core whose runtime contract differs from stock in several independent ways.

The stock archaeology now says that premise was inverted:

```text
stock performance contract
    = C68K
    + 22.05-kHz audio
    + adaptive render-only frameskip
    + double-buffered draw path
    + HC15xx stock scheduler/transport
```

whereas the tested FBA2012 path was fundamentally closer to:

```text
A68K or Musashi
    + 32-kHz audio
    + draw every retro_run
    + submit video every retro_run
```

A faster 68000 backend alone therefore could not make the external core behave like stock.

## Public-source ancestry status

No inspected public fork currently reproduces the exact complete HC15xx hybrid.

The closest public source pieces are:

### FBA-a320 family

Provides:

- C68K/Cyclone backend;
- three-way `nSekCpuCore` selector;
- default C68K;
- 22050-Hz handheld-era configuration ancestry.

### Aftnet/fbalpha 621e371

Provides:

- the later 0.2.97.42 identity and libretro wrapper generation present in stock;
- but not the stock C68K Sek integration.

### HC15xx stock binaries

Provide the remaining vendor-specific evidence:

- merged C68K-enabled Sek model;
- 22050/367 wrapper constants;
- private `SetFrameSkip`-style hook;
- alternating frame buffers;
- stock frontend pacing integration.




## Exact XGO arcade callback install contract

Direct XGO disassembly of the arcade wrapper install block at `0x80360870..0x80360964` now bounds the vendor frontend extension precisely.

Using the authoritative XGO GP and stock global map, the wrapper installs:

```text
stock slot                    XGO arcade function

gfn_state_save   0x80c33a70  <- 0x80360718
gfn_state_load   0x80c33ac0  <- 0x803605fc

gfn_retro_get_region
                 0x80c33a9c  <- 0x8036c220

gfn_get_system_av_info
                 0x80c33aac  <- 0x8036c028

gfn_retro_load_game
                 0x80c33acc  <- 0x8036d658

gfn_retro_unload_game
                 0x80c33ad4  <- 0x8036b890

gfn_frameskip    0x80c33ae0  <- 0x8036bdc0  (_SetFrameSkip)

gfn_retro_run    0x80c33ae4  <- 0x8036c228
```

The key materialization is:

```asm
80360908  lui   t7,0x8037
80360924  addiu t6,t7,-16960       ; 0x8036bdc0
...
80360954  sw    t6,-3220(gp)       ; gfn_frameskip
```

The same block installs the ordinary libretro-facing callbacks around it.

This is significant because it shows that the arcade performance integration is not a large private API surface. At the stock frontend boundary, the relevant extension is essentially:

```c
void SetFrameSkip(int skip);
```

in addition to the normal core callbacks already expected by `run_emulator()`.

No second adjacent arcade-private performance hook is installed in this callback table.

Therefore the minimal wrapper contract for reproducing stock behavior is now bounded as:

1. ordinary libretro callbacks;
2. one private `SetFrameSkip(bool)` entry point;
3. stock `run_emulator()` calls that private hook before each `retro_run()`.

## Vendor framebuffer patch is exactly a doubled upstream allocation

Upstream `Aftnet/fbalpha@621e371` allocates one libretro framebuffer after `BurnDrvGetFullSize()`:

```cpp
g_fba_frame = (uint32_t*)malloc(width * height * sizeof(uint32_t));
```

The XGO stock load path performs the corresponding calculation as:

```asm
8036dfb4  ... get full width/height
8036dfbc  lw    v1,width
8036dfc0  lw    t9,height
8036dfc4  mult  v1,t9
8036dfc8  mflo  t8
8036dfcc  jal   allocator
8036dfd0  sll   a0,t8,3       ; width * height * 8 bytes
```

It then initializes the private double-buffer state:

```asm
8036e00c  sw    v0,active_buffer
8036e010  sw    v0,buffer0
8036e018  sw    zero,buffer_index

8036dfe4  mult  width,height
8036e020  mflo  t6
8036e024  sll   t5,t6,2       ; width * height * 4
8036e028  addu  t4,t5,v0
8036e034  sw    t4,buffer1
```

Therefore:

```text
allocation = width * height * 8

buffer0 = base
buffer1 = base + width * height * 4
active  = buffer0
index   = 0
```

This is exactly two upstream-sized `uint32_t` frame surfaces in one allocation.

Combined with the private frameskip hook:

```text
draw enabled:
    toggle buffer0/buffer1

draw skipped:
    active_buffer = NULL
```

the vendor framebuffer modification can be reconstructed at source level as a small wrapper patch rather than an unknown graphics subsystem.

## FBA-a320 contains the direct source ancestor of HC15xx render skipping

The strongest source-level lineage match now comes from `dmitrysmagin/fba-a320`.

Its default configuration is already the same cluster of choices seen in stock HC15xx:

```cpp
options.samplerate = 2;   // 22050 Hz
options.frameskip  = -1;  // automatic frameskip
options.m68kcore   = 0;   // C68K
```

More importantly, its frame runner implements the same render-only suppression strategy.

`src/sdl-dingux/run.cpp`:

```cpp
int RunOneFrame(bool bDraw, int fps)
{
    ...
    pBurnDraw = NULL;

    if (bDraw) {
        nFramesRendered++;
        pBurnDraw = (unsigned char *)BurnVideoBuffer;
    }

    BurnDrvFrame();

    if (bDraw) {
        VideoTrans();
        ...
        VideoFlip();
    }
}
```

Thus an overdue frame is still fully emulated, including CPU and sound generation, but graphics rendering/output is disabled by setting `pBurnDraw = NULL`.

Its main timing loop in `src/sdl-dingux/sdl_run.cpp` performs catch-up as:

```cpp
timer = GetTicks() / frametime;
now   = timer;
ticks = now - done;

if (ticks < 1)
    continue;

if (ticks > 10)
    ticks = 10;

for (i = 0; i < ticks - 1; i++) {
    RunOneFrame(false, fps);
    SndPlay();
}

RunOneFrame(true, fps);
SndPlay();

done = now;
```

This is conceptually the same policy now recovered from HC15xx stock:

```text
if behind:
    emulate overdue frames without drawing
    keep audio/game state progressing

when caught up enough:
    render a frame
```

The HC15xx vendor adaptation changes the API boundary:

```text
FBA-a320 SDL frontend:
    RunOneFrame(false)
        -> pBurnDraw = NULL
        -> BurnDrvFrame()

HC15xx libretro frontend:
    gfn_frameskip(1)
        -> active FBA draw buffer = NULL
    retro_run()
        -> BurnDrvFrame()
```

The core optimization is the same.

This substantially strengthens the ancestry model:

```text
FBA-a320 handheld runtime
    ├─ default C68K
    ├─ default 22050 Hz
    ├─ automatic catch-up frameskip
    └─ pBurnDraw=NULL on skipped frames
             |
             | vendor adaptation into libretro/HC15xx
             v
HC15xx stock FBA
    ├─ C68K default
    ├─ 22050 Hz / 367 samples
    ├─ stock frontend lateness detector
    └─ gfn_frameskip -> pBurnDraw=NULL
```

The stock family's private frameskip callback is therefore best understood as a libretro-facing refactoring of an existing FBA-a320 handheld optimization, not an independent HC15xx invention.

## Research direction

The next useful question is **not** how to make the failed A68K ROM loader proceed.

It is:

> Can we reconstruct the smallest source-level "stock arcade contract" from public ancestry, or identify an already-existing handheld FBA port close enough that only the HC15xx frontend adapter is missing?

Priority comparisons:

1. FBA-a320 / Miyoo descendants that preserve C68K.
2. Their CPS1 ROM loader versus the stock binary's CPS1 loader.
3. Their draw-path behavior when `pBurnDraw == NULL`.
4. Their audio setup at 22050 Hz.
5. Whether a source base exists where the vendor private frameskip hook can be added without transplanting the newer FBA2012 archive loader.

No new hardware package should be built until that source-lineage comparison produces a coherent stock-contract candidate.
