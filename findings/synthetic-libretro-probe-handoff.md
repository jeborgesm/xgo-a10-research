# XGO synthetic libretro probe handoff

Status: **host build successful and stock run-loop indirections independently verified; no hardware execution yet**.

## Purpose

After proving that arbitrary code can be built for the `0x87000000` external-core window, the next bring-up step is to validate the XGO's real libretro handoff before attempting a production emulator core.

The synthetic probe core is intentionally not an emulator. It implements only the standard callback surface needed to let the stock XGO frontend call it repeatedly.

## Synthetic core behavior

The core reports:

```text
base/max geometry: 320 x 240
pixel format used by callback payload: RGB565
fps: 60
sample rate declaration: 22050 Hz
```

Its frame function calls the stock input callback for both controller ports and fills a fixed framebuffer at:

```text
0x87100000
```

with one of four colors:

```text
blue  = neither P1 nor P2 A
red   = Player 1 A
 green = Player 2 A
white = both Player 1 and Player 2 A
```

It then submits the frame through the stock XGO video callback.

This makes the same diagnostic useful for validating external-core execution, stock video transport, stock input polling, and eventually Player 2.

## Why no XGO board-driver imports are needed

The probe does not call ST7789V, OSD, VPO, GPIO, ADC, audio-driver, or other board-specific functions directly.

Instead the loader provides the already-running XGO callbacks:

```text
retro_video_refresh_cb       = 0x8035e70c
retro_audio_sample_batch_cb  = 0x8035e7d8
retro_input_poll_cb          = 0x8035ea30
retro_input_state_cb         = 0x8035eb20
retro_environment_cb         = 0x8035eb64
```

Therefore the external core remains behind the stock XGO hardware abstraction.

## Stock run_emulator() indirections verified

XGO `run_emulator` begins at:

```text
0x8035ed48
```

The executable itself confirms the function-pointer globals used by the proposed loader.

### Load game

At approximately `0x8035edf0`:

```text
lw   $s0,-0xca8($gp)
...
jalr $s0
```

With `$gp = 0x80c34774`:

```text
0x80c34774 - 0x0ca8 = 0x80c33acc
```

which is the mapped `gfn_retro_load_game` slot.

The function passes:

```text
0x80c2e914
```

as the game-info structure, confirming the mapped `g_retro_game_info` address.

### AV-info callback

At approximately `0x8035ee14`:

```text
lw $v0,-0xcc8($gp)
jalr $v0
```

which resolves to:

```text
0x80c33aac = gfn_get_system_av_info
```

### Region callback

At approximately `0x8035ee5c`:

```text
lw $s0,-0xcd8($gp)
jalr $s0
```

which resolves to:

```text
0x80c33a9c = gfn_retro_get_region
```

### Frame callback

Inside the run loop, XGO loads:

```text
gp - 0x0c90 = 0x80c33ae4
```

and calls it each frame, confirming:

```text
0x80c33ae4 = gfn_retro_run
```

The adjacent optional pointer at:

```text
0x80c33ae0
```

is checked as an optional frameskip callback, matching the existing Multicore model.

These executable checks are independent confirmation that the synthetic loader is populating the correct XGO globals.

## Loader behavior

Only:

```text
/mnt/sda1/ROMS/XGO_LIBRETRO_PROBE.gba
```

enters the probe path. All other GBA launches pass through to stock `run_gba`.

For the probe path the loader:

1. verifies live heap break `< 0x87000000`;
2. loads `/mnt/sda1/XGO_LIBRETRO_PROBE.BIN` at `0x87000000`;
3. flushes caches;
4. calls the external core entry;
5. stops the previous sound task using the stock flag convention;
6. supplies stock XGO video/audio/input/environment callbacks;
7. populates the verified stock core-function globals;
8. calls XGO `run_emulator(load_state)`;
9. deinitializes the probe core and restores the original heap ceiling when the stock run loop returns.

## Host-build results

Using Clang 17's MIPS target:

```text
synthetic loader binary = 944 bytes
synthetic core binary   = 1508 bytes
loader relocations      = none
core relocations        = none
loader entry            = 0x80001500
core entry              = 0x87000000
```

The loader therefore fits comfortably in the confirmed 3200-byte stock injection hole.

## Why this is a major feasibility milestone

If the earlier SD-write and raw-execution probes succeed physically, this synthetic core becomes a much more informative test than immediately trying a complex emulator.

A successful run would prove:

```text
external MIPS module
   -> stock XGO libretro callback wiring
   -> XGO run_emulator()
   -> stock display path
   -> stock controller polling
   -> P1 + P2 port access
```

while still avoiding production-core/newlib complexity.

The remaining step after this probe is no longer "figure out whether Multicore architecture can work." It is primarily to map/build the additional runtime imports needed by selected real libretro cores and any advanced Multicore features we choose to retain.

## Source

- `tools/multicore/xgo_libretro_probe_loader.c`
- `tools/multicore/xgo_libretro_probe_core.c`
- `tools/multicore/xgo_libretro_probe_core.ld`
