# XGO stock libretro rotation support is incomplete

Status: **confirmed from `retro_environment_cb()` and firmware-wide cross-reference search of the rotation state**.

## Headline

XGO returns success for `RETRO_ENVIRONMENT_SET_ROTATION`, stores the requested value, and remaps D-pad masks for rotation values 1 and 3.

However, the stored rotation state is never consumed by the stock video path. No framebuffer/display routine reads it.

Therefore the stock frontend does **not** implement actual libretro video rotation through this environment command.

## Rotation state

`retro_environment_cb` stores the requested rotation value at:

```text
$gp - 0x5f08 = 0x80c2e86c
```

A firmware-wide disassembly cross-reference search finds this global only inside `retro_environment_cb()`:

```text
0x8035ebdc  read current rotation
0x8035ecfc  store SET_ROTATION value
0x8035ed04  read current rotation
```

No stock display, scaler, OSD, emulator wrapper, or frame callback reads `0x80c2e86c`.

## What the callback actually does

On entry the callback resets the four direction masks to their default mapping:

```text
UP    0x0010
DOWN  0x0040
LEFT  0x0080
RIGHT 0x0020
```

Then:

- rotation `1` applies one 90-degree directional permutation;
- rotation `3` applies the opposite 90-degree permutation;
- rotation `2` receives no special permutation and leaves the default D-pad mapping.

The callback still returns success for `SET_ROTATION`.

## Consequences

### 90 / 270 degree requests

The controls are rotated, but the stock firmware has no corresponding video-rotation state consumer. Unless the core itself rotates its output despite requesting frontend rotation, video and controls can disagree.

### 180 degree request

Neither video nor directional input is rotated. The command is accepted but effectively does not implement the requested orientation.

## Multicore compatibility rule

The XGO environment compatibility shim should not blindly delegate `SET_ROTATION` to stock firmware and treat the returned success as proof of frontend capability.

Safer initial behavior is:

```text
rotation 0 -> accept
rotation 1/2/3 -> reject until wrapper-side frame rotation exists
```

A fuller XGO Multicore frontend can implement rotation in its RGB565 video wrapper and then apply matching input-direction permutations itself.

## Why this matters

This is the second confirmed case where XGO's stock libretro environment callback reports success without providing the full required behavior:

1. `SET_PIXEL_FORMAT` accepts any format while the stock transport is RGB565-oriented;
2. `SET_ROTATION` accepts rotations while no stock video path consumes the rotation state.

External modern cores therefore require capability validation/interposition rather than direct trust in stock environment return values.
