# Stock FBA CPU-backend and frontend-timing comparative archaeology

Date: 2026-09-05
Branch: `research-post-mapper-runtime`

## Scope

This checkpoint follows the authoritative `HANDOFF-CURRENT.md` direction:

- family-wide stock-FBA comparative archaeology;
- no new hardware package yet;
- no resumption of A68K ROM bisection.

The purpose is to identify the actual stock arcade lineage and runtime choices before proposing another XGO experiment.

## XGO stock FBA contains both C68K and A68K

Preserved XGO firmware:

`bios/bisrv.asd`

SHA-256 already documented in the repository:

`869e056d000337e1b10c834f0a93244c0abd99457c1c8374367f7dff20e43daf`

The stock binary contains the diagnostic strings:

```text
SekReset SEK_CORE_C68K
SekReset SEK_CORE_A68K
SekInit SEK_CORE_C68K
SekInit SEK_CORE_A68K
```

The two `SekInit` strings are at:

```text
file 0x009a5108 -> VA 0x809a5108 : SekInit SEK_CORE_C68K
file 0x009a5120 -> VA 0x809a5120 : SekInit SEK_CORE_A68K
```

Direct MIPS xrefs land inside the stock `SekInit` dispatcher:

```asm
80374298  beq   t0,t6,0x803744c0      ; t6 = 2
...
803742a0  addiu a3,zero,2
803742a4  beq   t0,a3,0x8037450c      ; selector 2 -> A68K path
803742ac  bne   t0,zero,0x80374468    ; selector 0 falls into C68K path
...
80374458  lui   t9,0x809a
8037445c  jal   0x802947c0
80374460  addiu a0,t9,0x5108         ; "SekInit SEK_CORE_C68K"
...
8037450c  lui   t2,0x809a
80374510  jal   0x802947c0
80374514  addiu a0,t2,0x5120         ; "SekInit SEK_CORE_A68K"
```

The active selector is loaded from stock global:

```text
gp = 0x80c114f4
lw t0,-23952(gp)
=> 0x80c0b764
```

Therefore the stock firmware retains a runtime/backend selector with the same key values as the old handheld FBA lineage:

```text
0 -> C68K
2 -> A68K
```

This does **not yet prove** which value XGO selects for CPS1 at launch. It gives us the exact next static-analysis target: trace writes to `0x80c0b764` and determine the selected core for CPS1/NeoGeo/other 68K families.

## Family ancestor: FBA-a320 defaults to C68K, not A68K

The documented SF2000 engine lineage is close to Dmitry Smagin's `fba-a320` / FBA 0.2.96.86.

Its stock configuration defaults are:

```cpp
options.samplerate = 2;   // 22050 Hz
options.frameskip = -1;   // auto frameskip
options.m68kcore = 0;     // 0 = C68K, 1 = Musashi, 2 = A68K
options.z80core = 0;
```

This is important because the external XGO FBA+A68K experiment assumed the native-MIPS A68K backend was the likely performance path. The family ancestor instead treated C68K as the default and exposed A68K as an alternate backend.

## XGO wrapper lineage remains FB Alpha v0.2.97.42 / 621e371

Existing repository finding:

`findings/embedded-arcade-fba-lineage.md`

already establishes that XGO embeds the old FB Alpha libretro-facing identity:

```text
FB Alpha
v0.2.97.42 621e371
```

The exact upstream `621e371` libretro wrapper contains:

```cpp
#define AUDIO_SAMPLERATE 48000
#define AUDIO_SEGMENT_LENGTH 801
```

and in `retro_run()`:

```cpp
InputMake();
ForceFrameStep();
video_cb(...);
audio_batch_cb(g_audio_buf, nBurnSoundLen);
```

For CPS builds its AV timing is hardcoded around CPS frequency:

```cpp
struct retro_system_timing timing = {
    59.629403,
    59.629403 * AUDIO_SEGMENT_LENGTH
};
```

The wrapper's `fba-cpu-speed-adjust` option maps 100-200 to `nBurnCPUSpeedAdjust`, defaulting to 100%.

The preserved XGO binary contains the same option namespace, including:

```text
fba-cpu-speed-adjust
fba-aspect
fba-sh2-mode
fba-hiscores
fba-controls-p1
fba-controls-p2
```

## HC15xx frontend integration is part of the performance model

The SF2000 multicore loader demonstrates that replacement cores do not own the whole runtime. They are inserted under stock firmware services:

- stock `run_emulator()`;
- stock video callback;
- stock audio batch callback;
- stock input callbacks;
- stock sound task lifecycle;
- stock scheduler/tick functions.

Notably, the multicore wrapper documents:

```cpp
// NOTE: stock frontend audio_batch_cb always return 0!
retro_audio_sample_batch_cb(data, frames);
// return frames as if all data was consumed
return frames;
```

and supports core-provided auto-frameskip through the stock frontend callback:

```cpp
RETRO_ENVIRONMENT_SET_AUDIO_BUFFER_STATUS_CALLBACK
...
gfn_frameskip = frameskip_cb;
```

The loader also explicitly waits for the stock sound task to terminate before replacing a core.

This means stock arcade performance cannot be explained by the 68000 backend alone. The vendor combination is:

```text
FBA engine/backend
    + libretro wrapper
    + HC15xx stock run_emulator scheduler
    + stock audio task / callback semantics
    + stock video transport
```

## Working hypothesis

The highest-value next question is no longer "can A68K load SFII?"

It is:

> What backend and timing configuration does stock XGO actually select for CPS1, and does that selection differ from SF2000/GB300 v2?

Priority static-analysis targets:

1. Trace all writes/readers of XGO global `0x80c0b764` to identify the stock 68K selector policy.
2. Identify the XGO environment callback behavior for `fba-cpu-speed-adjust` and whether CPS1 receives a non-100% value.
3. Recover the effective XGO FBA audio rate / segment length and compare it with upstream `621e371` and SF2000.
4. Locate stock frameskip/frame-pacing logic around `run_emulator()`, not inside the external core.
5. Acquire/compare GB300 v2 stock binary values at the equivalent selector/timing sites.

No hardware candidate should be built until these static comparisons produce a concrete transplant or patch hypothesis.
