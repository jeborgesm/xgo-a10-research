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
gp = 0x80c34774
lw t0,-23952(gp)
=> 0x80c2e9e4
```

Therefore the stock firmware retains a runtime/backend selector with the same key values as the old handheld FBA lineage:

```text
0 -> C68K
1 -> Musashi path (strong inference from the three-way dispatcher and matching family numbering)
2 -> A68K
```

This does **not yet prove** which value XGO selects for CPS1 at launch. It gives us the exact next static-analysis target: trace writes to `0x80c2e9e4` and determine the selected core for CPS1/NeoGeo/other 68K families.


## XGO CPS1 backend: strong evidence for C68K

The corrected selector address is `0x80c2e9e4`.

The preserved ASD file ends at file offset `0x00c2d4c4`, while the selector corresponds to runtime-relative offset `0x00c2e9e4`. Therefore the selector is not file-initialized data; it resides in the runtime/BSS region and naturally starts at zero after normal firmware zero-initialization.

A direct scan of GP-relative references to the selector found one direct store in the `SekInit` path. The surrounding XGO MIPS is:

```asm
80373f84  lui   a1,0x0006
80373f88  ori   a0,a1,0x8000          ; 0x00068000
80373f8c  xor   v1,s3,a0              ; nCPUType != 0x68000?
80373f90  sltu  v0,zero,v1
80373f94  sltiu ra,t1,1               ; nCount == 0?
80373f98  and   t9,ra,v0
80373f9c  beq   t9,zero,0x80373fb8
...
80373fa4  lw    a3,-23952(gp)         ; nSekCpuCore
80373fa8  addiu v0,zero,1
80373fac  bnel  a3,v0,0x80373fb8
80373fb0  sw    v0,-23952(gp)         ; force core 1
```

This matches the family-source logic from `fba-a320`:

```cpp
// only m68k supports 68010 and 68EC020
if (nCount == 0 && nCPUType != 0x68000 &&
    nSekCpuCore != SEK_CORE_M68K)
    nSekCpuCore = SEK_CORE_M68K;
```

The same source defines the backend numbering used by the frontend:

```text
0 = C68K
1 = Musashi/M68K
2 = A68K
```

Consequences for CPS1:

- CPS1 uses a normal `SekInit(0, 0x68000)` path.
- The non-68000 fallback above is therefore not taken.
- The selector's zero/BSS default is C68K.
- No other direct GP-relative store to this selector was found in the preserved XGO firmware.

This is **strong static evidence that stock XGO CPS1 uses C68K**, not A68K. An indirect write cannot yet be ruled out absolutely, so hardware instrumentation is not justified yet; family/binary comparison should continue first.

This materially changes the optimization hypothesis: the successful stock path should be compared first against the family C68K build/runtime rather than treating native-MIPS A68K as the presumed vendor fast path.

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


## XGO vendor FBA lowers the libretro wrapper audio load

The exact upstream `621e371` libretro wrapper hardcodes:

```cpp
AUDIO_SAMPLERATE      = 48000
AUDIO_SEGMENT_LENGTH  = 801
```

The preserved XGO stock binary does something materially different in the FBA game-load initialization path:

```asm
8036d7e0  lui   a0,0x809a
8036d7e4  addiu t3,a0,0x50b8
8036d7e8  lw    a0,0(t3)              ; stock FBA audio buffer pointer
8036d7ec  lui   v1,0x80d3
8036d7f0  addiu t2,v1,-13520
8036d7f4  addiu t1,zero,22050
8036d7f8  addiu t0,zero,367
...
8036d804  sw    t2,-24108(gp)         ; pBurnSoundOut-like global
8036d808  sw    t1,-24100(gp)         ; 22050 Hz
8036d80c  sw    t0,-24104(gp)         ; 367 samples/frame buffer length
```

Using the authoritative XGO GP `0x80c34774`, these globals are:

```text
0x80c2e948
0x80c2e94c
0x80c2e950
```

The code shape corresponds directly to the upstream wrapper's `retro_load_game()` assignments to `pBurnSoundOut`, `nBurnSoundRate`, and `nBurnSoundLen`, but XGO has replaced the upstream 48 kHz / 801-sample values with 22.05 kHz / 367.

This aligns with the older handheld `fba-a320` lineage, whose default frontend sample rate is also 22050 Hz.

This is a concrete vendor optimization: XGO's embedded arcade build generates substantially less audio data per emulated frame than the untouched 2017 libretro wrapper.

## XGO frontend does not expose the FBA CPU-overclock option

The embedded FBA wrapper contains the upstream option string:

```text
fba-cpu-speed-adjust
```

but XGO's stock `retro_environment_cb` at `0x8035eb64` handles `RETRO_ENVIRONMENT_GET_VARIABLE` (command 15) only for these keys:

```text
fceumm_region
picodrive_region_fps
catsfc_VideoMode
```

The handler compares the requested key against those three strings and returns false for other keys.

Therefore the embedded FBA wrapper cannot receive a stock-frontend value for `fba-cpu-speed-adjust`. Its upstream `check_variables()` logic leaves `nBurnCPUSpeedAdjust` at the core default when GET_VARIABLE fails.

This rules out a previously plausible explanation for stock CPS1 speed: XGO is not secretly driving the old FBA wrapper through its 110-200% CPU-overclock option. The more promising optimizations are now the C68K backend, reduced audio workload, and stock scheduler/frame-pacing integration.

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


## Exact stock-family binary comparison

A dedicated archaeology workflow on this branch analyzed the preserved stock binaries from historical `Trademarked69/sf2000_multicore` commit `d973e5dd0bfe5a77ea7a11f42391e7f39294e8b0`.

Artifacts:

```text
SF2000 08/03:
  assets/os/bisrv_08_03.asd
  size   12,624,436 bytes
  sha256 c0afbfd09069773076934d2f4970226d1a8d188d067f60e04afcbb17be26515b

GB300 v2:
  assets/os/bisrv_GB300_V2.asd
  size   12,949,540 bytes
  sha256 253942ed35c9d874d7fc08d44af4213499cf891582fc176a9c066f935887bf11
```

Both binaries contain the exact same FBA/libretro identity as XGO:

```text
FB Alpha
v0.2.97.42 621e371
fba-cpu-speed-adjust
SekInit SEK_CORE_C68K
SekInit SEK_CORE_A68K
SekReset SEK_CORE_C68K
SekReset SEK_CORE_A68K
```

### Conserved vendor audio tuple

The characteristic adjacent constants are present in all three firmwares:

| Firmware | 22050 site | 367 site |
| --- | --- | --- |
| SF2000 08/03 | `0x80367400` | `0x80367404` |
| GB300 v2 | `0x8036b960` | `0x8036b964` |
| XGO | `0x8036d7f4` | `0x8036d7f8` |

This establishes that the 22.05-kHz / 367-sample FBA configuration is a **conserved HC15xx-family vendor modification**, not an XGO-specific optimization.

### Conserved SekInit backend logic

The family-source `SekInit` 68000 comparison pattern is likewise present in all three:

```text
SF2000 08/03  0x8036db90
GB300 v2      0x803720f0
XGO           0x80373f84
```

The C68K/A68K diagnostic xrefs move consistently with those functions:

```text
SF2000 C68K SekInit log: 0x8036e064 / 0x8036e06c
SF2000 A68K SekInit log: 0x8036e118 / 0x8036e120

GB300v2 C68K SekInit log: 0x803725c4 / 0x803725cc
GB300v2 A68K SekInit log: 0x80372678 / 0x80372680

XGO C68K SekInit log: 0x80374458 / 0x80374460
XGO A68K SekInit log: 0x8037450c / 0x80374514
```

The address deltas are consistent with inherited code blocks rather than independent implementations.

### Family-level conclusion

The stock arcade architecture now has a much firmer shape:

```text
old FBA-a320 engine ancestry
        |
        +-- three-way Sek backend support (C68K / Musashi / A68K)
        +-- C68K default for ordinary 68000 CPUs
        +-- Musashi fallback for non-68000 Sek CPU types
        |
later v0.2.97.42 / 621e371 libretro wrapper
        |
vendor HC15xx modifications
        +-- 22050-Hz FBA audio
        +-- 367-sample frame audio buffer
        +-- stock run_emulator pacing/audio transport
        |
        +-- SF2000 08/03
        +-- GB300 v2
        +-- XGO
```

This substantially weakens the premise that A68K is the key to reproducing stock CPS1 performance. The conserved family solution instead points first to **C68K plus lower audio workload plus vendor frontend pacing**.


## Audio-transport comparison correction: function boundary was truncated

A first normalized SF2000/GB300 v2 diff appeared to show a GB300-only ring-buffer recovery tail. That interpretation was incorrect and was caught before any hardware candidate was proposed.

The comparison windows were asymmetric:

```text
SF2000 sound window stopped at 0x80356380
GB300 v2 sound window continued to 0x8035b000
```

The apparent added GB300 code occurs in the **next audio function**, beginning at:

```text
SF2000    0x803562e0
GB300 v2  0x8035af2c
```

The SF2000 disassembly was simply cut off before the corresponding tail could be seen.

The GB300 sequence that had looked like a recovery helper is actually:

```asm
sw   next_position,<producer/consumer state>
li   a0,1
jal  dly_tsk
sw   zero,<state>
```

so the called helper is just the stock 1-ms task yield, not a newly identified GB300-specific recovery routine.

Accordingly:

- **withdrawn:** claim that GB300 v2 contains an audio-ring recovery fix absent from XGO;
- **still valid:** the family audio/runtime path remains a high-value comparison target;
- **next requirement:** identify exact corresponding function boundaries through the libretro audio-batch callback in each firmware before making any behavioral diff claim.

This correction preserves the research rule that family evidence must produce a concrete mechanism before hardware testing.


## Exact audio callback/ring-writer comparison: conserved across the family

The libretro audio callbacks are structurally identical in SF2000 08/03, GB300 v2, and XGO.

They all:

1. read the stock millisecond tick;
2. call the actual PCM ring writer;
3. read the tick again;
4. measure callback duration;
5. if the call took at least 21 ms, store the current tick in a frontend timing global;
6. return zero rather than the conventional consumed-frame count.

Exact ring-writer targets:

```text
SF2000 08/03  retro_audio_sample_batch_cb 0x80358430
                -> ring writer 0x80356864

GB300 v2      retro_audio_sample_batch_cb 0x8035c25c
                -> ring writer 0x8035b4b0

XGO           retro_audio_sample_batch_cb 0x8035e7d8
                -> ring writer 0x8035cba0
```

The callback body in all three includes the same threshold:

```asm
tick_before = os_get_tick_count()
ring_writer(data, frames)
tick_after  = os_get_tick_count()
elapsed = tick_after - tick_before
if (elapsed >= 21)
    timing_global = tick_after
return 0
```

The exact SF2000 and GB300 v2 ring writers are also instruction-for-instruction equivalent modulo relocated GP globals and libc addresses. XGO's preserved ring writer has the same control-flow and operation sequence:

- `byte_count = frames << 2`;
- compute producer end position;
- if the write would collide with the consumer region, repeatedly `dly_tsk(1)`;
- contiguous `memcpy` when no wrap is required;
- split `memcpy` when crossing the ring end;
- update the producer pointer;
- return.

Therefore the stock PCM producer path and its blocking semantics are a **conserved family mechanism**, not a later GB300 improvement.

This also clarifies the earlier misleading diff: the apparent GB300-only recovery code belonged to the next sound-driver function and was exposed only because the SF2000 disassembly window had been truncated.

### Consequence

The remaining high-value runtime comparison is now one layer higher:

> the `run_emulator()` timing/frameskip state machine that decides when to run frames, when to invoke the optional `gfn_frameskip` callback, and how the 21-ms audio timing global affects pacing.

On XGO, `run_emulator()` reads `gfn_frameskip = 0x80c33ae0` at:

```text
0x8035ef54
0x8035ef70
```

and, when non-null, calls it at:

```asm
8035f0d4  lw    a0,<frameskip_flag>
8035f0d8  jalr  v0              ; gfn_frameskip(flag)
```

The flag is maintained by the surrounding timing accumulator rather than by the FBA core itself. This is the next family-diff target.


## XGO vendor FBA restores real draw skipping through a private frontend hook

The upstream `621e371` libretro wrapper contains no `RETRO_ENVIRONMENT_SET_AUDIO_BUFFER_STATUS_CALLBACK` request and no frameskip callback. Its `retro_run()` always sets `pBurnDraw` to the FBA framebuffer before `BurnDrvFrame()`.

The XGO vendor build adds a private mechanism outside that upstream API.

The stock arcade launcher installs:

```text
gfn_retro_run  = 0x8036c228
gfn_frameskip  = 0x8036bdc0
```

at the end of the arcade wrapper immediately before jumping into stock `run_emulator()`.

With XGO stock GP `0x80c34774`:

```text
gfn_frameskip = 0x80c33ae0  -> GP - 3220
gfn_retro_run = 0x80c33ae4  -> GP - 3216
```

The private FBA frameskip hook is:

```asm
8036bdc0  beq   a0,zero,0x8036bdd0
8036bdc4  lw    a3,-24260(gp)

; a0 != 0: skip drawing this emulated frame
8036bdc8  jr    ra
8036bdcc  sw    zero,-24248(gp)

; a0 == 0: select the next real framebuffer
8036bdd0  addiu v0,gp,-24268
8036bdd4  xori  a0,a3,1
8036bdd8  sll   a2,a0,2
8036bddc  addu  v1,a2,v0
8036bde0  lw    a1,0(v1)
8036bde4  sw    a0,-24260(gp)
8036bde8  jr    ra
8036bdec  sw    a1,-24248(gp)
```

The involved XGO globals are:

```text
0x80c2e8a8  two-entry framebuffer pointer table
0x80c2e8b0  current framebuffer selector
0x80c2e8bc  active FBA draw pointer
```

The FBA `retro_run()` entry at `0x8036c228` then loads this vendor-selected draw pointer:

```asm
8036c24c  lw    v0,-24248(gp)
...
8036c258  sw    v0,-24088(gp)
```

The destination global is the FBA-side draw target used for the frame.

Therefore the stock HC15xx integration has recreated the old handheld FBA optimization in a private frontend/core ABI:

```text
stock run_emulator timing
        |
        +-- behind schedule?
        |      |
        |      +-- gfn_frameskip(1)
        |              -> active FBA draw pointer = NULL
        |              -> BurnDrvFrame still emulates
        |              -> expensive FBA video rendering is suppressed
        |
        +-- normal frame
               |
               +-- gfn_frameskip(0)
                       -> alternate real framebuffer
                       -> normal draw/render
```

This is directly analogous to the old `fba-a320` SDL loop:

```cpp
pBurnDraw = NULL;
if (bDraw) {
    pBurnDraw = BurnVideoBuffer;
}
BurnDrvFrame();
```

where catch-up frames are emulated without drawing and only the final frame is rendered.

This private hook is a major stock-performance mechanism that generic libretro integration does not reproduce automatically. It explains why simply dropping in a nominally newer FBA/MAME core under the stock frontend can perform worse even when CPU emulation itself is comparable.

### Important correction to upstream-only inference

It is not sufficient to inspect `621e371` and conclude that stock FBA has no frameskip support. The vendor binary extends the wrapper with this private `gfn_frameskip` ABI even though upstream `621e371` does not expose it through standard libretro.

The family comparison must therefore treat the **vendor wrapper patches**, not just the identified upstream commit, as first-class optimization code.


## Private FBA draw-skip hook is conserved in SF2000, GB300 v2, and XGO

The predicted sibling hook addresses were verified directly against the preserved stock binaries.

```text
SF2000 08/03  gfn_frameskip target 0x803659cc
GB300 v2      gfn_frameskip target 0x80369f2c
XGO           gfn_frameskip target 0x8036bdc0
```

All three implement the same logic:

```c
if (frameskip_flag != 0) {
    active_fba_draw_pointer = NULL;
    return;
}

framebuffer_index ^= 1;
active_fba_draw_pointer = framebuffer_table[framebuffer_index];
```

The exact sibling disassembly confirms the same control-flow and operation sequence.

SF2000:

```asm
803659cc  beqz  a0,0x803659dc
803659d0  lw    a3,-24288(gp)
803659d4  jr    ra
803659d8  sw    zero,-24276(gp)
803659dc  addiu v0,gp,-24296
803659e0  xori  a0,a3,1
803659e4  sll   a2,a0,2
803659e8  addu  v1,a2,v0
803659ec  lw    a1,0(v1)
803659f0  sw    a0,-24288(gp)
803659f4  jr    ra
803659f8  sw    a1,-24276(gp)
```

GB300 v2:

```asm
80369f2c  beqz  a0,0x80369f3c
80369f30  lw    a3,-24144(gp)
80369f34  jr    ra
80369f38  sw    zero,-24132(gp)
80369f3c  addiu v0,gp,-24152
80369f40  xori  a0,a3,1
80369f44  sll   a2,a0,2
80369f48  addu  v1,a2,v0
80369f4c  lw    a1,0(v1)
80369f50  sw    a0,-24144(gp)
80369f54  jr    ra
80369f58  sw    a1,-24132(gp)
```

XGO:

```asm
8036bdc0  beq   a0,zero,0x8036bdd0
8036bdc4  lw    a3,-24260(gp)
8036bdc8  jr    ra
8036bdcc  sw    zero,-24248(gp)
8036bdd0  addiu v0,gp,-24268
8036bdd4  xori  a0,a3,1
8036bdd8  sll   a2,a0,2
8036bddc  addu  v1,a2,v0
8036bde0  lw    a1,0(v1)
8036bde4  sw    a0,-24260(gp)
8036bde8  jr    ra
8036bdec  sw    a1,-24248(gp)
```

The corresponding FBA run entries are also conserved:

```text
SF2000    0x80365e34
GB300 v2  0x8036a394
XGO       0x8036c228
```

Each immediately reads the vendor-selected active draw pointer and copies it into the FBA draw target before frame execution.

This establishes a family-wide stock optimization:

> the HC15xx vendor deliberately restored old FBA-style render suppression through a nonstandard private frontend/core ABI after adopting the later libretro wrapper.

A generic libretro replacement that only implements the public API will not automatically inherit this optimization.

## Working hypothesis

The highest-value next question is no longer "can A68K load SFII?"

It is:

> What backend and timing configuration does stock XGO actually select for CPS1, and does that selection differ from SF2000/GB300 v2?

Priority static-analysis targets:

1. Treat C68K as the leading stock-CPS1 backend hypothesis and confirm it against SF2000/GB300 v2 binaries.
2. Compare the XGO 22.05 kHz / 367-sample FBA audio path against SF2000 and GB300 v2.
3. Recover the effective XGO FBA audio rate / segment length and compare it with upstream `621e371` and SF2000.
4. Locate stock frameskip/frame-pacing logic around `run_emulator()`, not inside the external core.
5. Treat private FBA draw suppression as confirmed family baseline; compare the SF2000/GB300 wall-time scheduler against XGO's different incremental drift scheduler to identify whether XGO's pacing policy is the remaining source of stock lag.

No hardware candidate should be built until these static comparisons produce a concrete transplant or patch hypothesis.
