# XGO stock SNES special runtime contract — exact closure

Status: **CONFIRMED from the preserved stock XGO `bios/bisrv.asd` and matched against the pinned HC15xx Snes9x2005 fork.**

Firmware SHA-256:

```text
869e056d000337e1b10c834f0a93244c0abd99457c1c8374367f7dff20e43daf
```

## Headline

The apparently awkward XGO SNES `0x08` special case is no longer an unknown.

It is a deliberate **11,025-Hz SNES audio profile**, and it matches the maintained SF2000/HC15xx Snes9x2005 port exactly.

This changes the Core #2 design decision materially: the first external SNES candidate should use XGO's native SNES family `0x08`, not masquerade as a generic/NES-family core and not be resampled to 44.1 kHz before we have evidence that such a rewrite is necessary.

## Exact machine-code branch

Inside stock:

```text
run_emulator = 0x8035ed48
```

the active family selector is read at:

```text
8035ee00  lhu   t0,-0xca4(gp)    ; 0x80c33ad0
8035ee04  li    a2,8
8035ee08  beq   t0,a2,0x8035f1f8
```

All ordinary families fall into the generic AV-info path:

```text
8035ee14  load active retro_get_system_av_info
8035ee1c  jalr  active callback
...
8035ee54  call stock sound initialization
8035ee5c  call active retro_get_region
```

SNES family `0x08` branches around the AV-info callback to:

```text
8035f1f8  li    ra,80
8035f1fc  li    t9,11025
8035f200  move  a0,zero
8035f204  li    a1,11025
8035f208  li    a2,2
8035f20c  sw    ra,-29540(gp)   ; 0x80c2d410 = 80
8035f210  b     0x8035ee54
8035f214  sw    t9,-29548(gp)   ; 0x80c2d408 = 11025
```

Execution then reaches:

```text
8035ee54  jal   0x8035c998     ; stock sound initialization
8035ee5c  ... active retro_get_region ...
```

Therefore the SNES special branch supplies:

```text
sound init a0 = 0
sound init a1 = 11025 Hz
sound init a2 = 2 channels

0x80c2d408 = 11025
0x80c2d410 = 80
```

and **does not call `retro_get_system_av_info()` before sound setup**.

The exact semantic name of the fixed value `80` remains to be closed, but its downstream audio-configuration use is confirmed. It is copied into the stock sound configuration structure together with the 11,025-Hz value.

## Direct match with the pinned replacement core

SF2000 Multicore currently pins:

```text
madcock/snes9x2005
fa69dd6a3caf279cc1f457e65e360f8b9a3683ed
```

That fork's `platform=sf2000` source contains:

```c
#if !defined(SF2000)
#define AUDIO_SAMPLE_RATE 32040
#else
#define AUDIO_SAMPLE_RATE 11025
#endif
```

and reports the same constant from `retro_get_system_av_info()`.

The source also calculates its per-frame mixed sample count from that same `AUDIO_SAMPLE_RATE`.

So we now have an unusually strong cross-check:

```text
XGO stock SNES frontend fixed rate = 11025 Hz
HC15xx Snes9x2005 SF2000 rate      = 11025 Hz
```

This is not merely "both run on MIPS." Their SNES audio operating point agrees exactly.

## Memory-load compatibility is clean

The pinned Snes9x2005 core has:

```c
#ifdef LOAD_FROM_MEMORY
   info->need_fullpath = false;
...
#ifdef LOAD_FROM_MEMORY
   if (!LoadROM(game))
#else
   if (!LoadROM(game->path))
#endif
```

The audit successfully builds:

```text
platform=sf2000 LOAD_FROM_MEMORY=1
```

under the exact Codescape HC15xx toolchain.

That makes the core compatible in principle with the already-proven XGO content handoff:

```text
stock run_game()
 -> preload selected .sfc/.smc into gp_buf_64m
 -> external core receives retro_game_info.data/size
 -> no second ROM read required
```

It also removes the normal SF2000 VFS/full-path dependency from the first XGO SNES candidate.

## Video contract

The pinned core explicitly requests:

```text
RETRO_PIXEL_FORMAT_RGB565
```

which is the exact format accepted by the hardware-proven XGO stock video transport.

Its advertised geometry is:

```text
base 256x224
max  512x512
aspect 4:3
```

The XGO stock video path has already been proven to accept changing RGB565 source dimensions and route them through the board scaler.

No new LCD/video driver is required for Core #2.

## Input contract

The core's ordinary SNES descriptors use:

```text
D-pad
B A X Y
L R
SELECT START
```

for ports 0 and 1, exactly within the hardware-proven XGO two-port libretro mapping.

No hidden L2/R2/L3/R3 support is required for ordinary SNES gameplay.

## Save-state contract

The pinned core exports standard:

```text
retro_serialize_size
retro_serialize
retro_unserialize
```

and the first SNES audit build confirms all three exports are present.

The generic XGO save-state bridge is already hardware-proven with FCEUmm. There is therefore no architectural reason to create a SNES-specific persistence mechanism; Core #2 should reuse the generic state adapter unchanged unless hardware proves otherwise.

## Important environment-shim work still required

The modern Snes9x2005 libretro layer asks for more environment commands than the minimal FCEUmm path, including:

```text
GET_LOG_INTERFACE
GET_PERF_INTERFACE
SET_SUPPORT_ACHIEVEMENTS
SET_PIXEL_FORMAT
GET_INPUT_BITMASKS
SET_INPUT_DESCRIPTORS
GET_VARIABLE / GET_VARIABLE_UPDATE
GET_AUDIO_VIDEO_ENABLE
SET_AUDIO_BUFFER_STATUS_CALLBACK
SET_MINIMUM_AUDIO_LATENCY
```

Not all are mandatory for correct basic emulation.

The first XGO SNES frontend should explicitly classify each request as:

```text
supported truthfully
safe no-op / false
required before hardware test
optional feature deferred
```

rather than forwarding stock environment behavior blindly.

## Core #2 strategy after this closure

The evidence now favors:

```text
XGO native SNES launch
 -> family selector = 0x08
 -> stock-preloaded ROM buffer
 -> external Snes9x2005 built with platform=sf2000 LOAD_FROM_MEMORY=1
 -> existing GP-safe video/audio/input/state runtime
 -> stock run_emulator() SNES 11025-Hz profile
```

This is cleaner than forcing SNES through family `0x01` and adding a 44.1-kHz resampler solely to satisfy the generic-family scheduler.

The `0x08` branch is not an obstacle anymore. It is now a **compatibility asset**.

## Reproduction

A verifier is preserved at:

```text
tools/multicore/audit_stock_snes_runtime.py
```

It requires the exact stock firmware SHA-256 and checks the branch and fixed constants without modifying the image.

## Next engineering gate

Before generating a hardware package:

1. close the exact minimum Snes9x2005 environment-command subset;
2. link the memory-load Snes9x2005 archive against the existing generic XGO runtime;
3. measure linked payload/runtime/BSS headroom;
4. implement SNES-native dispatch interception at the already-known stock call site `0x80360e40`;
5. audit wrapper/session mutations against stock `run_snes @ 0x8035f9d8`;
6. build a guarded Core #2 candidate;
7. hardware-test using a known title that performs poorly under the embedded stock core.

## Confidence

**CONFIRMED:** stock family `0x08` skips the generic AV-info setup.

**CONFIRMED:** stock family `0x08` initializes stereo audio at exactly 11,025 Hz.

**CONFIRMED:** the maintained HC15xx/SF2000 Snes9x2005 fork uses exactly 11,025 Hz under `platform=sf2000`.

**CONFIRMED:** the pinned core can be built with `LOAD_FROM_MEMORY=1`.

**CONFIRMED:** RGB565, standard SNES joypad input, and libretro serialization align with already-proven XGO runtime services.

**OPEN:** semantic meaning of the fixed companion value `80`.

**OPEN:** exact minimum environment shim and final linked image footprint.

**OPEN:** physical XGO execution of external Snes9x2005.
