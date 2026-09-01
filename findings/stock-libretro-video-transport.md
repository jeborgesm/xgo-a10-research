# XGO stock libretro video transport contract

Status: **confirmed by disassembly of `retro_video_refresh_cb` and `run_screen_write`**.

## Headline

The stock XGO video callback is substantially reusable for external libretro cores as long as frames are RGB565.

Confirmed behavior:

```text
RGB565 frame transport      yes
libretro pitch in bytes     yes
NULL-frame duping           yes
runtime width changes       yes
runtime height changes      yes
stock XGO scaler retained   yes
```

The main incompatibility remains pixel-format negotiation: stock `SET_PIXEL_FORMAT` falsely accepts unsupported formats, so an external environment shim must constrain or convert formats.

## Callback chain

```text
retro_video_refresh_cb  0x8035e70c
          |
          v
run_screen_write        0x8035c398
          |
          v
run_osd_region_write    0x8035c31c
          |
          v
XGO ALi OSD/scaler/display stack
          |
          v
ST7789V 320x240 panel
```

## NULL frame / frame duping

`retro_video_refresh_cb` tests the frame-data pointer and returns cleanly when it is NULL.

This matches libretro's frame-duping convention, so a compatibility environment wrapper may truthfully answer:

```text
RETRO_ENVIRONMENT_GET_CAN_DUPE = true
```

## Pitch is standard libretro byte pitch

`retro_video_refresh_cb(data, width, height, pitch)` forwards the original arguments to `run_screen_write`.

`run_screen_write` then performs:

```text
pixel_pitch = pitch >> 1
```

before passing the value into the RGB565 OSD region writer.

For a 320-pixel-wide tightly packed RGB565 frame:

```text
libretro pitch = 320 * 2 = 640 bytes
XGO OSD pitch  = 640 >> 1 = 320 pixels
```

Therefore XGO follows the normal libretro convention: callback pitch is expressed in bytes.

## Dynamic framebuffer dimensions

`run_screen_write` maintains cached width and height values in the display runtime state.

On every submitted frame it compares the incoming width/height against the cached geometry. When either changes, it:

1. closes/reinitializes the active OSD path as needed;
2. delays while the display path settles;
3. recreates the OSD region for the new source geometry;
4. stores the new width and height;
5. resumes writing through the stock scaler.

Thus the underlying stock XGO transport is not restricted to one emulator's native framebuffer size.

This is valuable for Multicore because NES, GB, GBA, SNES, Genesis and other cores can present different source geometries while leaving board-specific panel/scaler handling in stock firmware.

## Pixel-format limitation

Stock `retro_environment_cb(RETRO_ENVIRONMENT_SET_PIXEL_FORMAT, ...)` returns success without checking the requested enum.

The video path itself, however, converts byte pitch to 16-bit pixel pitch and feeds the RGB565 OSD pipeline. Therefore raw XRGB8888 output must not be passed directly simply because stock firmware returned `true` to format negotiation.

Initial XGO external-core policy should be:

```text
RGB565 request   -> accept and use stock callback
XRGB8888 request -> reject until converter exists
0RGB1555 request -> reject or explicitly convert
```

A later compatibility layer may add XRGB8888 conversion, as newer SF2000 Multicore implementations do.

## Practical consequence

The first real XGO Multicore port does not need its own LCD driver or framebuffer scaler. A small compatibility wrapper can preserve:

- XGO board-specific LCD initialization;
- XGO OSD setup;
- XGO 640x480 logical/frontend conventions;
- physical 320x240 panel scaling;
- TV/display routing already present in stock firmware.

This materially reduces the amount of board-specific code that must be reproduced before external emulator cores can run.
