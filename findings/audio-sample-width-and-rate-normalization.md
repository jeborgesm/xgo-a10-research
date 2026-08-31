# Audio sample width, DAC format, channel count, and rate normalization

## Summary

The XGO sound path is now sufficiently characterized for alternative-firmware board work. The board configuration carries separate DAC precision and DAC-format bytes, while the runtime SND state explicitly configures a two-channel transport even though the handheld has only one physical speaker.

The practical stock baseline is:

- internal HC15xx SND/I2SO transport: **2 channels**
- sample precision: **16-bit**
- normal hardware rates: **44.1 kHz and 48 kHz**
- normal working block: **960 samples**
- board DAC-format selector: **1**
- speaker/amp output gate: **GPIO L23**
- built-in acoustic output: **one physical speaker / mono**
- user volume states: **0 / 33 / 66 / 99 = mute / low / medium / high**

The remaining serial-framing and analog summing details are interesting implementation details, but they no longer block a conservative XGO board profile: a port should preserve two-channel 16-bit PCM transport and the XGO-specific L23 output gate rather than assuming a mono hardware PCM device.

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

This ordering is independently consistent with older public ALi SDK definitions of `struct snd_output_cfg`, whose first fields include `dac_precision` followed by `dac_format`. That older family exposes I2S, left-justified, and right-justified serial-format choices and separately configures precision.

**CONFIRMED:** XGO stock audio uses 16-bit SND precision.

**CONFIRMED:** XGO board configuration selects DAC-format value `1`.

**STRONG EVIDENCE:** the value `1` is an HC15xx descendant of the ALi-family serial framing selector. The exact HC15xx symbolic name for raw value `1` has not been recovered, so it should not be labeled I2S, left-justified, or right-justified without further evidence.

## Two-channel transport confirmed

The normal setup path writes the constant `2` to two related runtime fields before configuring SND/I2SO:

```text
80306e30: addiu $2, $zero, 2
80306e34: sw    $2, 0x1c($19)
80306e38: sb    $2, 0x110($17)
```

The channel field is validated elsewhere in the SND subsystem against the supported set `1`, `2`, `4`, and `8`; unsupported values enter the driver's error/assertion path. Normal XGO initialization selects **2**.

**CONFIRMED:** stock XGO uses a **two-channel internal SND transport**.

This resolves the apparent contradiction with the physical unit: the handheld has only one built-in speaker, but its digital PCM path is not a one-channel device. The collapse from two digital channels to one acoustic output can happen by mixing, channel selection/duplication, or analog summing downstream; the exact stage is not required to reproduce the known-working digital transport.

## Hardware programming

The lower-level helper at `0x8030a268` accepts:

- 8
- 16
- 24
- 32

and maps those values to a compact SND hardware field. The XGO path reaches it with `16`; another runtime condition also explicitly forces `16`, reinforcing that 16-bit precision is intentional.

A separate helper at `0x8030a528` accepts values `0..3` and writes a two-bit SND field. The XGO board's DAC-format global is `1`, so stock selects field value `1` here.

Another helper at `0x8030a5ac` configures a related frame/clock field using the `0x20`/`0x30`/`0x40` family. Its exact symbolic meaning has not been recovered.

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

## Physical observations and volume behavior

Direct observation establishes that the XGO contains **one physical speaker**. The physical volume button cycles through:

1. none / mute
2. low
3. medium
4. high
5. back to none / mute

This exactly matches the firmware L29 volume-button path:

`0 -> 33 -> 66 -> 99 -> 0`

| Firmware value | Observed setting |
| ---: | --- |
| 0 | none / mute |
| 33 | low |
| 66 | medium |
| 99 | high |

The built-in speaker quality is observed to be poor at all levels. Alternative firmware may improve resampling, clipping, gain handling, latency, or emulator behavior, but the small mono speaker/amplifier/enclosure is likely a substantial fidelity limit.

## Output gate

Separate executable tracing identifies GPIO **L23** as the XGO-specific speaker/amp gate. Volume-zero and transition paths drive this line to mute/disable the analog output; nonzero-volume paths enable it before applying software volume.

This is board-specific and differs from known related devices: an XGO port must not blindly inherit the SF2000 or GB300 speaker-gate GPIO.

## Current XGO audio contract

```text
emulator / frontend PCM
        |
        +-- two-channel transport         CONFIRMED
        +-- 16-bit precision              CONFIRMED
        +-- DAC serial-format value 1     CONFIRMED raw value
        +-- 44.1 / 48 kHz normally        CONFIRMED
        +-- 11.025 / 22.05 via 44.1 kHz   CONFIRMED behavior
        +-- 960-sample working blocks     CONFIRMED
        |
        +-- HC15xx SND / I2SO hardware
        |
        +-- XGO-specific L23 output gate  STRONG executable evidence
               |
               -> one physical speaker / mono acoustic output

Volume button (L29):
0 (mute) -> 33 (low) -> 66 (medium) -> 99 (high) -> 0
```

## Investigation status

For board-port purposes, the **sound investigation is considered complete enough to proceed**. The unresolved items below are non-blocking refinements rather than architectural unknowns:

- exact HC15xx symbolic name for DAC-format raw value `1`;
- whether left/right samples remain distinct all the way to the DAC or are mixed/duplicated earlier;
- exact downstream stage that converts the two-channel digital path to the one-speaker analog output;
- symbolic name of the secondary `0x20`/`0x30`/`0x40` frame/clock selector.

If future runtime testing exposes an audio-routing problem, these are the first details to revisit. Until then, the conservative compatibility baseline is **2-channel, 16-bit, 44.1/48-kHz HC15xx SND/I2SO with the XGO L23 output gate**.