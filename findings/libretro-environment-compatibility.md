# Stock XGO libretro environment callback compatibility

Status: **confirmed by disassembly of `retro_environment_cb` at `0x8035eb64`**.

## Headline

The stock XGO frontend implements only four libretro environment commands:

```text
1   RETRO_ENVIRONMENT_SET_ROTATION
10  RETRO_ENVIRONMENT_SET_PIXEL_FORMAT
15  RETRO_ENVIRONMENT_GET_VARIABLE
27  RETRO_ENVIRONMENT_GET_LOG_INTERFACE
```

Other commands fall through and return false.

This is a major constraint for loading newer libretro cores directly, and explains why a Multicore-style compatibility wrapper is valuable even though XGO's stock video/audio/input callbacks are reusable.

## Command 1: SET_ROTATION

The callback logs:

```text
Environ SET_ROTATION: %u
```

and stores the selected rotation state.

It also rewrites the directional entries in the joypad mask table. The default directional masks are:

```text
UP    0x0010
DOWN  0x0040
LEFT  0x0080
RIGHT 0x0020
```

For rotation states 1 and 3, firmware permutes those masks so directional input follows the rotated display.

Therefore rotation support is active behavior, not a dead libretro compatibility stub.

## Command 10: SET_PIXEL_FORMAT

The implementation simply returns success.

It does **not** inspect or validate the requested pixel-format enum.

This is an important compatibility trap: a core requesting XRGB8888 can receive `true` even though the stock XGO video path is fundamentally built around RGB565 buffers. Passing 32-bit frames directly afterward can therefore produce corrupt output or worse.

A custom XGO Multicore environment wrapper should intercept pixel-format negotiation and either:

- advertise RGB565 only; or
- provide an explicit XRGB8888-to-RGB565 conversion path before invoking stock XGO video transport.

## Command 15: GET_VARIABLE

The stock callback recognizes exactly three variable keys:

```text
fceumm_region
picodrive_region_fps
catsfc_VideoMode
```

For those keys it returns one of:

```text
NTSC
PAL
AUTO
```

selected by the stock region-mode state at `0x80c2e878`.

Unknown variable names return false.

This is sufficient for the three embedded stock emulator families that ask these questions, but not for the larger option sets used by many modern cores.

## Command 27: GET_LOG_INTERFACE

The callback returns a stock firmware logging function at approximately:

```text
0x8035e5c8
```

This makes XGO's existing logging facility reusable by an external compatibility layer/core.

## Commands not implemented

No stock handling was found for common modern requests such as:

```text
GET_SYSTEM_DIRECTORY
SET_INPUT_DESCRIPTORS
SET_VARIABLES
GET_VARIABLE_UPDATE
SET_SUPPORT_NO_GAME
GET_LIBRETRO_PATH
GET_RUMBLE_INTERFACE
GET_INPUT_DEVICE_CAPABILITIES
GET_SAVE_DIRECTORY
SET_GEOMETRY
GET_CORE_OPTIONS_VERSION
SET_CORE_OPTIONS / V2
GET_MESSAGE_INTERFACE_VERSION
SET_AUDIO_BUFFER_STATUS_CALLBACK
```

The exact set needed varies by core, and well-behaved cores may tolerate false for many of these. Others require wrapper support.

## Multicore consequence

The best XGO architecture is now clearer:

```text
external libretro core
        |
XGO compatibility environment wrapper
        |-- emulate/answer modern environment commands
        |-- convert XRGB8888 when needed
        |-- expose directories/options
        |
stock XGO callbacks
        |-- video transport
        |-- audio transport
        |-- P1/P2 input
        |
stock XGO board drivers
```

This preserves the XGO-specific LCD, scaler, audio, SD, battery, and Player-2 implementation while replacing only the compatibility layer and emulator core.

## Confidence

### CONFIRMED

- callback address `0x8035eb64`;
- supported command IDs 1, 10, 15, and 27;
- all other commands return false in the stock callback;
- hard-coded variable keys and NTSC/PAL/AUTO values;
- rotation modifies the directional input mask table;
- SET_PIXEL_FORMAT returns success without validating the requested format.

### Engineering implication

A raw modern libretro core should not be assumed compatible merely because the stock XGO exposes libretro callbacks. A thin environment shim is the correct porting boundary.
