# Audio OSD archaeology — volume state and first render strategy

Status: **static path substantially recovered; first hardware OSD candidate not yet built**.

## Frontend volume state is directly accessible

The stock GP is:

```text
XGO_STOCK_GP = 0x80c34774
```

The persisted volume word is referenced as `gp-0xd20`, therefore its live runtime address is:

```text
g_volume = 0x80c33a54
```

This is the same value stored as word 2 of `Resources/Archive.sys`.

The physical volume button is GPIO L29. Its frontend path still implements:

```text
0 -> 33 -> 66 -> 99 -> 0
```

then calls the stock audio helper and persists `Archive.sys`.

Importantly, `g_volume` is adjacent to the already-mapped controller globals:

```text
0x80c33a54  g_volume
0x80c33a5c  g_joy_task_state
...
0x80c33ac4  g_joy_state
```

So a transient OSD can observe volume state from ordinary frontend memory without touching the libretro audio callback or sound task.

## Stock volume helper accepts an arbitrary 8-bit value

The stock helper at `0x801b3b40` disassembles as:

```text
801b3b40  addiu sp,sp,-24
801b3b44  sw    ra,16(sp)
801b3b48  andi  a2,a0,0xff
801b3b4c  lw    a0,-29200(gp)
801b3b50  jal   0x80279d20
801b3b54  addiu a1,zero,4
...
```

Therefore it does not quantize to 0/33/66/99. It masks the requested value to 8 bits and forwards:

```text
sound_device, subblock/command 4, uint8 volume
```

The next wrapper at `0x80279d20` again performs only:

```text
andi a2,a2,0xff
```

then dispatches through the active sound-device vtable.

No four-step quantization occurs in either layer.

### Consequence

The current four levels are definitely imposed by the XGO frontend button policy, not by these first two stock audio API layers.

This does **not** yet prove that every value 0..99 is perceptually distinct at the analog output. The final sound driver/DAC may still clamp, quantize, or map the values nonlinearly. Hardware testing is required.

However, intermediate values such as 16, 25, 50, 75, etc. can be sent to the same stock driver path without replacing the audio transport.

## Hardware mute remains separate

Volume zero is accompanied by:

```text
GPIO L23 = 1
```

while nonzero volume uses:

```text
GPIO L23 = 0
```

The software volume helper and the board-level mute/amplifier gate are therefore separate mechanisms.

Any finer-volume experiment must preserve the existing L23 behavior:

```text
volume == 0 -> hardware mute asserted
volume > 0  -> hardware mute released
```

## Existing OSD transport is usable, but direct one-shot writes are too transient

The stock display chain is already mapped:

```text
retro_video_refresh_cb  0x8035e70c
    -> run_screen_write 0x8035c398
    -> run_osd_region_write 0x8035c31c
    -> osddrv_3x_region_write 0x80279114
```

`run_osd_region_write` writes an RGB565 rectangle at the top-left of active OSD region 0.

Previous external-core diagnostics proved that small direct region writes can become visible on hardware. They also proved that such writes are transient because normal frontend/game redraws overwrite them.

Therefore a one-shot call from the volume-button handler is not a satisfactory gameplay OSD.

## Lowest-risk first gameplay OSD strategy

Do **not** hook the sound callback and do **not** alter the successful CPS1 scheduler.

The preferred first candidate is:

```text
volume button changes g_volume
    -> set a small OSD-expiry state

ordinary retro_video_refresh_cb
    -> while expiry active:
         composite a tiny RGB565 volume bar into the outgoing frame
    -> call the existing run_screen_write exactly once
```

Advantages:

1. no second OSD/DMA write per frame;
2. no audio-path instrumentation;
3. no scheduler replacement or timing-policy change;
4. no display geometry changes;
5. the overlay naturally disappears when the expiry state ends;
6. only a very small number of RGB565 stores are added while visible.

The first hardware candidate should deliberately avoid text/font rendering. A simple bar provides a binary proof of safe transient overlay behavior before adding numbers or labels.

## First-candidate constraints

The initial OSD should:

- use `g_volume @ 0x80c33a54`;
- leave the 0/33/66/99 control policy unchanged;
- leave `set_audio_volume @ 0x801b3b40` unchanged;
- preserve GPIO L23 mute behavior;
- draw only when a volume press has occurred recently;
- draw a small bar in a low-risk corner;
- respect incoming width, height and byte pitch;
- do nothing for NULL/dupe frames;
- add no extra `run_screen_write` or `run_osd_region_write` call;
- expire automatically after a short interval.

After that is hardware-confirmed, the next independent experiment can change the volume step policy and test whether intermediate values are actually audible.

## New mapped symbols

`tools/multicore/xgo_stockfw_symbols.ld` now records:

```text
g_volume        = 0x80c33a54
set_audio_volume = 0x801b3b40
```

## Current conclusion

Two previously open questions are now separated cleanly:

```text
OSD problem
  -> frontend/video concern
  -> can be implemented without touching sound transport

volume granularity problem
  -> frontend currently quantizes by +33
  -> stock audio API accepts arbitrary uint8 values at least through its first two layers
  -> final perceptual granularity still requires hardware validation
```

The next concrete step is a protected-baseline **bar-only transient volume OSD** candidate.
