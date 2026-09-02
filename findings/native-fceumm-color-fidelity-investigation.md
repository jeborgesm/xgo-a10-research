# Native FCEUmm color-fidelity investigation

## Trigger

The first successful full-path external FCEUmm hardware test loaded and played Contra normally, with working controls/audio/timing, but the user observed that colors looked somewhat muted versus the stock XGO NES emulator.

## Current interpretation

This is a post-bring-up fidelity issue, not a core execution failure. Geometry and framebuffer transport are functional enough for normal gameplay, which makes a gross pixel-format mismatch less likely.

The investigation should distinguish among:

1. FCEUmm's selected NES palette versus the stock XGO emulator's palette.
2. RGB565 packing/channel order or bit expansion differences.
3. Any stock NES-specific color conversion, saturation, brightness, or palette lookup performed before the common display callback.
4. LCD/OSD configuration differences caused by the stock emulator path versus the external path.

## Known external-core path

Pinned FCEUmm is built with `FRONTEND_SUPPORTS_RGB565`. Its libretro driver generates a 16-bit palette and sends 256-pixel-wide frames with 512-byte pitch to the XGO stock video callback. Earlier firmware analysis established that the stock callback consumes the libretro pitch as 16-bit pixels (`pitch >> 1`), so the successful rendered image is consistent with a 16-bit RGB path.

## Important caution

Do not infer that muted color means RGB/BGR channel reversal. A full R/B swap usually produces conspicuously wrong hues, whereas a generally muted appearance can result simply from a different NES palette or intensity curve. The stock emulator may not use the same palette as upstream FCEUmm.

## Next evidence targets

- recover/identify the stock NES palette table or palette-generation routine in `bisrv.asd`
- compare it numerically with pinned FCEUmm's default palette
- confirm the exact pixel format requested/accepted by the stock XGO NES libretro path
- inspect whether the stock video callback itself is system-family-sensitive
- only after those comparisons, consider a small palette/color correction in the external frontend/core build

Status: **open investigation; hardware symptom confirmed**.
