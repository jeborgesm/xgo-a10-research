# FCEUmm as the first real XGO external emulator target

Status: **recommended first-core target based on source-level compatibility audit; hardware execution not yet performed**.

## Why FCEUmm is the best first proof

Current FCEUmm aligns unusually well with the behavior preserved in the XGO stock frontend:

- supports software RGB565 output;
- standard libretro joypad input;
- can generate 44.1-kHz audio;
- region option key is exactly `fceumm_region`, which XGO stock firmware already knows;
- core-options negotiation has backward-compatible fallbacks;
- NES can use XGO system family `0x01`, avoiding the stock SNES special path;
- upstream SF2000 Multicore work already demonstrates this emulator family is practical on HC15xx-class hardware.

This makes it a cleaner validation target than beginning with a more demanding SNES core.

## RGB565 compatibility

Current FCEUmm contains an explicit RGB565 frontend path. When built with frontend RGB565 support, it requests:

```text
RETRO_ENVIRONMENT_SET_PIXEL_FORMAT = RETRO_PIXEL_FORMAT_RGB565
```

and uses RGB565 when the frontend returns success.

The XGO compatibility shim intentionally accepts RGB565 and rejects XRGB8888/0RGB1555 until converters exist.

This matches the proven XGO stock video transport exactly.

## Audio compatibility and the modern Auto-rate trap

FCEUmm supports:

```text
32000
44100
48000
96000 Hz
```

Its current `fceumm_sndrate_hint` default is `Auto`.

Modern FCEUmm resolves Auto by querying:

```text
RETRO_ENVIRONMENT_GET_TARGET_SAMPLE_RATE
```

and selecting the nearest supported rate.

If the frontend does not implement that environment command, FCEUmm currently falls back to 48000 Hz on ordinary platforms.

That would conflict with XGO's stock run-loop audio byte budgets, which are hard-wired around 44100 Hz.

The XGO minimal environment shim therefore answers the target-sample-rate query with:

```text
44100
```

so unmodified current FCEUmm Auto mode naturally selects the XGO-compatible rate.

## Core-options fallback is usable for bring-up

FCEUmm first asks for the modern Core Options API version.

If unsupported, it falls back through older option interfaces and ultimately to the legacy `SET_VARIABLES` mechanism. Failure to expose a full frontend options UI does not prevent the core from retaining its compiled defaults.

This means the first XGO experiment does not need a complete configuration frontend before the emulator can initialize.

## `fceumm_region` OEM spelling mismatch

XGO's stock environment callback contains an OEM-era FCEUmm integration and recognizes:

```text
fceumm_region
```

Its region table is physically present at `0x80a3d4c4`:

```text
state 0 -> "NTSC"
state 1 -> "PAL"
state 2 -> "AUTO"
```

with region state at:

```text
0x80c2e878
```

Current FCEUmm expects the automatic option value as the case-sensitive string:

```text
"Auto"
```

not uppercase `"AUTO"`.

The XGO compatibility shim therefore handles `fceumm_region` itself:

```text
0 -> NTSC
1 -> PAL
2/other -> Auto
```

while preserving the same stock region state.

This is a concrete example of why a thin compatibility layer is required even though XGO already embeds a libretro-style frontend.

## XGO family identity while running

The external launch should temporarily change the active XGO system selector at:

```text
0x80c33ad0
```

from the GBA-hook value `0x10` to NES `0x01` before invoking stock `run_emulator()`, then restore it on exit.

That ensures the stock frontend supplies NES-family fallback keymaps and ordinary generic run-loop behavior.

## Initial FCEUmm compatibility profile

```text
XGO family             0x01 / NES
video format           RGB565
video transport        stock XGO callback
frame duping           supported
input                   stock XGO libretro P1/P2 callback
audio transport        stock stereo int16 batch callback
target sample rate     forced/advised 44100 by environment shim
region                  XGO state normalized to NTSC/PAL/Auto
system directory        /mnt/sda1/bios
save directory          /mnt/sda1/saves
modern core options     optional for first boot
hardware rendering      not required
```

## Remaining work before hardware FCEUmm test

1. produce a MIPS32 little-endian soft-float static FCEUmm core image linked for the `0x87000000` external-core ABI;
2. inventory unresolved libc/newlib symbols from that exact build;
3. extend the XGO linker symbol map only for symbols actually required;
4. connect the minimal environment shim into the external-core bridge;
5. save/restore `0x80c33ad0` around the external run and select family `0x01`;
6. perform the same byte/disassembly audit already used for the raw probe image;
7. first execution remains SD-only and must not contain `UpdateFirmware/Firmware.upk`.

## Conclusion

FCEUmm is currently the lowest-risk real emulator with which to prove XGO Multicore operation. It exercises the actual goals—replacement emulator code, NES main-family controls, P1/P2 libretro input, video scaling, and audio—without simultaneously requiring XRGB8888 conversion, unusual devices, or a bespoke board driver.
