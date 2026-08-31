# Audio sample width, DAC format, and rate normalization

## Summary

A deeper trace resolves an ambiguity in the earlier audio analysis. The XGO board configuration carries separate DAC precision and DAC-format bytes, matching the long-lived ALi sound-driver architecture.

The relevant XGO configuration bytes are:

- `dac_precision = 0x10` = **16 bits**
- `dac_format = 0x01`

The active audio setup routine at `0x80306cdc` receives requested sample rate, sample count, and the precision value. Normal callers use 44.1 or 48 kHz, 960 samples, and the board-configured 16-bit precision.

## Correction to the earlier interpretation

The embedded debug string says:

`i2so sample_rate=%d->%d sample_num=%d snd_dac_format=%d`

Taken alone, that label suggested the fourth argument was the serial DAC format. Following the value into `0x80306514` shows that it is passed to the hardware precision helper `0x8030a268`, which accepts exactly `8`, `16`, `24`, or `32`.

Therefore the debug label is misleading or uses `snd_dac_format` loosely. In the active XGO path the fourth argument is the **sample precision / word width**, and the normal board value is **16**.

## Direct board-configuration evidence

During platform initialization around `0x80309fc0`, the firmware copies adjacent board-configuration bytes into globals:

- source byte `+0x02` -> precision global
- source byte `+0x03` -> DAC-format global

The corresponding bytes in the XGO LCFG configuration are `10 01`.

This ordering is independently consistent with older public ALi SDK definitions of `struct snd_output_cfg`, whose first fields include `dac_precision` followed by `dac_format`. The older SDK explicitly describes precision as 24- or 16-bit and DAC format as the serial codec framing selection.

**CONFIRMED:** XGO stock audio uses 16-bit SND precision.

**CONFIRMED:** XGO board configuration selects DAC-format value `1`.

**STRONG EVIDENCE:** the value `1` belongs to the ALi-family I2S/left/right serial framing selector. The exact HC15xx enum name for raw value `1` remains to be proven before calling it I2S, left-justified, or right-justified.

## Hardware programming

The lower-level helper at `0x8030a268` accepts:

- 8
- 16
- 24
- 32

and maps those values to a compact SND hardware field. The XGO path reaches it with `16`; under another runtime condition the code also explicitly forces `16`, reinforcing that 16-bit precision is intentional rather than accidental.

A separate helper at `0x8030a528` accepts values `0..3` and writes a two-bit SND field. The XGO board's DAC-format global is `1`, so the stock board selects field value `1` here.

Another helper at `0x8030a5ac` configures a related frame/clock field using the `0x20`/`0x30`/`0x40` family. Its exact semantic name remains unresolved.

## Sample-rate normalization

The vendor layer normalizes low source rates through the 44.1-kHz hardware path:

- 11025 -> 44100 hardware-facing rate
- 22050 -> 44100 hardware-facing rate
- 44100 -> 44100
- 48000 -> 48000

The original low rate is retained separately, consistent with ratio/interpolation handling.

## Working block size

Normal callers pass `960` samples.

At 48 kHz:

`960 / 48000 = 0.020 s`

so the working block is exactly 20 ms. At 44.1 kHz it is about 21.77 ms.

## Current XGO audio contract

```text
emulator / frontend PCM
        |
        +-- 16-bit precision             CONFIRMED
        +-- DAC serial-format value 1    CONFIRMED
        +-- 44.1 / 48 kHz normally
        +-- 11.025 / 22.05 normalized through 44.1 kHz
        +-- 960-sample working blocks
        |
        +-- HC15xx SND / I2SO hardware
        |
        +-- XGO-specific L23 output gate
               |
               -> speaker / amplifier
```

## What remains unresolved

The main remaining audio-format questions are now narrower:

1. the exact HC15xx name/meaning of DAC-format value `1`;
2. effective transport channel count and slot layout;
3. whether mono content is duplicated into stereo hardware slots;
4. exact semantics of the secondary `0x20`/`0x30`/`0x40` frame/clock selector.

Do not infer transport channel count merely from the physical speaker count.