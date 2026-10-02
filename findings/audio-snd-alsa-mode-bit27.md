# SND +0x34 bit 27 is legacy I2S ALSA mode

Date: 2026-10-02
Branch: `research-audio-fidelity-latency`
Status: **BIN SYMBOL/BEHAVIOR CLOSED; INTERNAL HARDWARE SEMANTICS PARTLY OPEN**

## Closure

The hardware feature enabled by runtime-reinit command `0x59(1)` is no longer unnamed.

The stock firmware retains the diagnostic/function-name string:

```text
snd_i2s_alsa_mode_enable
```

at firmware address `0x808D6D08`.

The low-level helper reached by command 0x59 is:

```text
0x8030AB64
```

Its invalid-argument diagnostic path constructs a pointer to that exact string at `0x8030ABC4`.

Therefore:

> `0x8030AB64` = legacy `snd_i2s_alsa_mode_enable` behavior. [BIN]

## Exact register behavior [BIN]

The helper masks its boolean argument to 8 bits.

For argument 0:

```text
SND[+0x34] &= 0xF7FFFFFF
```

For argument 1:

```text
SND[+0x34] |= 0x08000000
```

Any other value takes the diagnostic/error path that references `snd_i2s_alsa_mode_enable`.

Thus SND register `+0x34`, bit 27 is the legacy I2S **ALSA mode enable** bit.

## Runtime-reinit consequence

The recovered runtime initializer executes command:

```text
0x59(1)
```

through the concrete sound-object dispatcher.

That path resolves to:

```text
0x80309BEC
 -> 0x802FD8C8
 -> 0x8030AB64
```

Therefore runtime sound initialization explicitly enables legacy I2S ALSA mode.

This replaces the previous OPEN description of command 0x59 as merely an unknown hardware feature bit.

## Adjacent legacy mode control [BIN]

Immediately before this helper, the firmware contains another low-level mode function whose error path references:

```text
snd_i2s_proc_normal_play_en
```

at `0x808D6CEC`.

That adjacent helper manipulates bit 28 (`0x10000000`) of the same SND `+0x34` register.

So the legacy hardware exposes at least two neighboring software-controlled playback modes:

```text
SND +0x34 bit 28 -> proc_normal_play enable
SND +0x34 bit 27 -> ALSA mode enable
```

The exact interaction between the two modes still requires recovery.

## Important limitation

“ALSA mode” is the firmware's own retained symbol terminology.

It does **not by itself** prove the exact empty-buffer behavior. In particular it does not yet establish whether ALSA mode:

- stops DMA at empty;
- emits zero;
- holds a sample;
- generates a completion/underrun event;
- changes cursor semantics;
- automatically restarts when new PCM is committed.

Those details remain the next binary target.

## Family-source context [UP]

Modern HC15xx HCRTOS exposes ALSA-style PCM concepts including:

- START/DROP;
- DELAY;
- DRAIN;
- PAUSE/RESUME;
- XFER;
- AVAIL_MIN;
- explicit `SND_EVENT_UNDERRUN`.

This is architectural family context only. Numeric ioctl/event mappings from modern HCRTOS must not be projected onto the older XGO binary.

## Reinit/noise significance

The runtime reinit sequence now includes a proven playback-mode operation while L23 may remain open:

```text
speaker gate open
 -> sound object reconfiguration
 -> ALSA mode explicitly enabled
 -> frontend FIFO reset/rebuild
```

That strengthens the reinit path as a noise/discontinuity lead, but does not prove an audible artifact.

## Next target

Trace how ALSA mode changes the lower transfer/interrupt path, especially:

```text
playback cursor +0x3A catches commit +0x38
 -> event/interrupt
 -> lower service task
 -> ALSA-mode empty behavior
 -> later XFER/restart
```

## Hardware gate

Not reached.
