# Audio OSD archaeology — framebuffer hook and storage surface

Date: 2026-09-05
Branch: `research-audio-osd`

## New result

The first OSD candidate does **not** need to patch `retro_video_refresh_cb` itself.

The already hardware-exercised mapper work identified the stock menu renderer framebuffer globals:

```text
gp-0x1410 -> framebuffer pointer
gp-0xe18  -> framebuffer width/pitch
```

With XGO stock GP `0x80c34774`, these resolve to:

```text
0x80c33364 -> current renderer framebuffer pointer
0x80c3395c -> current renderer width/pitch
```

The mapper v1 marker routine already proved that writing RGB565 pixels through these renderer globals can produce visible overlay markers on real hardware.

That gives us a lower-risk volume-OSD route than intercepting the libretro callback or issuing an extra OSD/DMA write.

## Important distinction

There are two framebuffer contexts in play:

1. libretro cores submit their source frame to `retro_video_refresh_cb @ 0x8035e70c`;
2. the stock frontend/menu renderer has a writable framebuffer pointer exposed through GP-relative state.

The mapper marker proof establishes the second context as a safe native drawing surface for frontend UI.

For the volume OSD, the ideal hook is therefore **after the stock frame has been rendered into the frontend framebuffer but before/within the ordinary frontend presentation cadence**, using the existing renderer state rather than creating a second display transaction.

## Existing low-memory cave is no longer available

Protected baseline composition matters.

The current golden chain contains:

```text
mapper v19 injection      ~0x800014a0...
SNES Test02 loader         0x80002230...
historical Core #3 cave    0x80002780..0x80002fff
CPS1 scheduler transplant  in-place at 0x8035ee..
```

Therefore the original mapper-era zero cave cannot be treated as free OSD storage.

The OSD experiment must first scan the **exact protected scheduler baseline** for a new verified zero/code cave, or reuse demonstrably dead space only after byte-level proof.

## State requirements are tiny

A bar-only OSD needs only:

```text
last_volume      1 byte/word
visible_count    1 word
optional dirty   1 word
```

No heap allocation is justified.

The stock live value remains:

```text
g_volume = 0x80c33a54
```

A first implementation can detect a volume change by comparing `g_volume` to `last_volume`, eliminating the need to patch the physical GPIO/button handler.

That is safer than modifying the volume-button control path.

Pseudo-contract:

```text
on ordinary frontend presentation:
    v = g_volume
    if v != last_volume:
        last_volume = v
        visible_count = N

    if visible_count != 0:
        draw tiny RGB565 bar using renderer framebuffer globals
        visible_count--
```

## Why change detection is preferable

Hooking the volume button would require another patch in controller-task logic.

Polling one already-live frontend word during an existing presentation hook gives the same observable behavior while preserving:

- GPIO L29 handling;
- 0/33/66/99 stock policy;
- Archive.sys persistence;
- `set_audio_volume`;
- GPIO L23 hardware mute behavior.

This makes the OSD experiment orthogonal to audio behavior.

## Expiry policy

For the first hardware proof, frame-count expiry is preferable to introducing another timing dependency.

At roughly 60 Hz:

```text
N = 90 frames -> about 1.5 seconds
N = 120       -> about 2 seconds
```

Exact duration is not important for the first proof. The scheduler must not be consulted or modified.

## First visual form

Use a small solid RGB565 bar, not text.

Suggested geometry:

```text
outer width  ~80 px
height       ~8-12 px
filled width = volume * inner_width / 99
```

The bar should be clipped against the renderer width/pitch and should use only a few hundred 16-bit stores per visible frame.

## Remaining static gate before build

Before emitting a hardware candidate:

1. obtain/scan the exact protected baseline bytes;
2. identify a verified unused code/data island;
3. identify the least invasive frontend presentation hook whose displaced instructions can be reproduced exactly;
4. prove the hook is not shared with timing-sensitive scheduler state;
5. build a patcher that refuses any input except firmware SHA-256
   `9136479687e921fc478ad89ccce3af94296366768a83600312b3bed5ee294607`;
6. byte-audit that only CRC, hook, and new island change.

No candidate should be produced until those six conditions are satisfied.
