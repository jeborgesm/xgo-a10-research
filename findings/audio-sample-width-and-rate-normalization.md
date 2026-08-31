# Audio sample width and rate normalization

## Summary

The XGO audio initialization path exposes a clearer HC15xx PCM contract than was previously documented.

The active setup routine at `0x80306cdc` receives:

- requested sample rate in `$a1`
- sample count in `$a2`
- an 8-bit audio-format/config value in `$a3`

Known callers pass either `48000` (`0xBB80`) or `44100` (`0xAC44`) as the sample rate and `960` (`0x3C0`) as the working sample count.

A debug string embedded in the firmware matches this call exactly:

`i2so sample_rate=%d->%d sample_num=%d snd_dac_format=%d`

This strongly confirms that the fourth argument is the vendor's `snd_dac_format` configuration value.

## Accepted sample-width values

A lower-level SND register helper at `0x8030a268` accepts exactly four width-like values:

- `8`
- `16`
- `24`
- `32`

and converts them to a two-bit register field in the SND block.

The main setup path calls this helper with the incoming format-derived width, except under one board/runtime condition where it explicitly forces `16`.

**Confirmed:** the HC15xx SND driver embedded in the XGO firmware has explicit hardware support for 8-, 16-, 24-, and 32-bit audio word-width selections.

**Not yet confirmed:** which of these widths the normal XGO frontend/emulator path uses at runtime. The active `snd_dac_format` byte originates in board/runtime configuration loaded earlier, so it should not be guessed from the speaker count or from generic SDK defaults.

## Related DAC/frame-format field

Another SND helper at `0x8030a5ac` accepts the values:

- `0x20`
- `0x30`
- `0x40`

and translates them to another compact register field.

The main setup routine chooses `0x40` when one incoming format value equals `0x20`; otherwise it chooses `0x30`.

This is clearly part of the DAC/frame transport configuration, but the exact semantic names of `0x20`, `0x30`, and `0x40` have not yet been established from XGO-local evidence. They should not be labeled mono/stereo or I2S/LJ/RJ without additional proof.

## Sample-rate normalization

The same initialization routine contains an important special case for low sample rates.

If the requested rate is:

- `11025` (`0x2B11`), or
- `22050` (`0x5622`)

then the hardware-facing rate stored in the primary SND state is rewritten to:

- `44100` (`0xAC44`)

while the original requested rate is retained separately.

For ordinary `44100` and `48000` requests, no such rewrite is performed.

This is strong evidence that the vendor SND layer uses a 44.1 kHz hardware clock path plus internal ratio/interpolation handling for 11.025 and 22.05 kHz sources rather than programming the hardware directly to those lower rates.

## 960-sample period

All currently traced normal callers of `0x80306cdc` pass `960` samples.

At 48 kHz:

`960 / 48000 = 0.020 s`

so this corresponds exactly to a 20 ms audio block.

At 44.1 kHz the same 960-sample block is about 21.77 ms.

**Strong evidence:** `960` is the vendor's normal working transfer/period count for this path, not a bit-depth or channel-count value.

## Current XGO audio model

The evidence now supports this model:

```text
emulator / frontend PCM
        |
        +-- requested sample rate
        |      44.1 kHz / 48 kHz normally
        |      11.025 / 22.05 kHz normalized through 44.1 kHz path
        |
        +-- 960-sample working blocks
        |
        +-- HC15xx SND/I2SO configuration
        |      explicit 8/16/24/32-bit width selector support
        |      additional DAC/frame-format selector
        |
        +-- XGO board-specific L23 output gate
               |
               -> analog speaker/amplifier path
```

## What remains unresolved

For an XGO-specific alternative-firmware audio profile, the remaining high-value unknowns are:

1. the normal runtime value of `snd_dac_format` on the XGO board;
2. the effective transport channel count (mono vs stereo slots);
3. the exact meaning of the second DAC/frame-format selector (`0x20`/`0x30`/`0x40` family);
4. whether PCM is duplicated to two hardware slots even if the physical output is mono, as happens on some related HC15xx boards.

Until these are traced, do not infer the transport format from the number of physical speakers.
