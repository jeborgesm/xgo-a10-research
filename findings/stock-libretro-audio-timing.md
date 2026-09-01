# XGO stock libretro audio transport and timing assumptions

Status: **confirmed by disassembly of `retro_audio_sample_batch_cb`, `run_sound_advance`, `run_emulator`, and sound-driver initialization**.

## Headline

The XGO stock libretro audio boundary is standard interleaved stereo 16-bit PCM, but the stock run loop's per-frame audio scheduling is hard-wired around **44.1 kHz at 50/60 Hz**.

This creates an important external-core compatibility rule:

> Cores that advertise/output 44.1 kHz fit the stock timing model naturally. Cores using other sample rates may require an XGO Multicore audio shim/resampler even though the low-level batch callback accepts their stereo buffers.

## Batch callback ABI

`retro_audio_sample_batch_cb` at `0x8035e7d8` forwards:

```text
a0 = sample buffer
a1 = frame count
```

to `run_sound_advance` at `0x8035cba0`.

`run_sound_advance` computes:

```text
byte_count = frame_count << 2
           = frame_count * 4
```

and copies exactly that many bytes into the XGO circular audio buffer.

Four bytes per libretro audio frame means:

```text
left  = int16_t
right = int16_t
```

so the stock boundary is standard interleaved stereo signed 16-bit PCM.

## Core-advertised sample rate is read

After invoking the active core's `retro_get_system_av_info`, `run_emulator()` reads the `sample_rate` double from the timing structure and converts it to an integer.

That integer is passed into the sound-driver initialization path at `0x8035c998`.

The sound setup structure also selects:

```text
channels = 2
sample width = 16 bits
```

So XGO does not simply ignore a core's advertised sample rate at hardware initialization time.

## But frame scheduling assumes 44.1 kHz

The stock run loop chooses PAL/NTSC pacing from the core's region callback.

For the two ordinary modes it installs:

```text
PAL:
  target FPS / cadence = 50 Hz
  frame period         = 20000 us
  audio bytes/frame    = 3528

NTSC:
  target FPS / cadence = 60 Hz
  frame period         ~= 16667 us
  audio bytes/frame    = 2940
```

Those byte budgets correspond exactly to stereo 16-bit 44.1-kHz PCM:

```text
44100 samples/s / 50 * 4 bytes = 3528
44100 samples/s / 60 * 4 bytes = 2940
```

Therefore the per-frame buffering/pacing constants are not derived from the arbitrary sample rate returned by the external core.

## Compatibility consequence

For an external core advertising 44100 Hz:

```text
sound-driver rate       = 44100
stock frame byte budget = matches 44100
```

For a core advertising another rate, e.g. 22050 Hz:

```text
sound-driver rate       = 22050
stock frame byte budget = still based on 44100
```

That mismatch can plausibly cause buffer pressure, timing drift, underrun/overrun behavior, or unstable audio pacing.

## First-core selection rule

Until the XGO compatibility layer owns audio pacing or performs resampling, the safest first real libretro emulator core should:

- output RGB565;
- tolerate the minimal environment shim;
- use standard joypad input;
- advertise **44100 Hz** audio;
- operate naturally at 50/60 Hz region timing.

This dramatically narrows the first-core search and avoids confusing an audio-timing mismatch with a bad Multicore port.

## Future shim options

A fuller XGO frontend can address non-44.1-kHz cores by one of:

1. resampling core audio to 44.1 kHz before calling stock audio transport;
2. replacing the stock per-frame audio-byte scheduling with rate-derived values;
3. buffering asynchronously and feeding the XGO sound ring according to actual consumption.

The first option is the least invasive because it leaves the existing XGO sound driver untouched.
