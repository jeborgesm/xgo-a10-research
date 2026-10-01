# XGO SNES producer cadence versus 576-frame frontend quantum

Date: 2026-10-01  
Branch: `research-audio-fidelity-latency`  
Status: **SRC/UP + XGO BIN CROSSWALK — SNES CALLBACK CADENCE CLOSED FOR PINNED FAMILY CORE**

## Pinned source

The XGO SNES work already pins the SF2000-family Snes9x2005 fork:

```text
madcock/snes9x2005
fa69dd6a3caf279cc1f457e65e360f8b9a3683ed
```

That exact revision was inspected for this latency pass.

## Rate [SRC/UP]

The SF2000 build selects:

```c
#if !defined(SF2000)
#define AUDIO_SAMPLE_RATE 32040
#else
#define AUDIO_SAMPLE_RATE 11025
#endif
```

This independently matches the XGO stock family-0x08 fixed 11025-Hz setup already closed from XGO firmware [BIN].

## Producer callback cadence [SRC/UP]

The non-Blargg path calculates:

```c
samples_per_frame = AUDIO_SAMPLE_RATE / refresh_rate;
```

and retains the fractional remainder in `audio_samples_accumulator`.

Each `retro_run()` executes:

```text
S9xMainLoop()
video callback
audio_upload_samples()
```

and `audio_upload_samples()` performs one:

```c
audio_batch_cb(audio_out_buffer, available_frames);
```

where `available_frames` is the integer per-video-frame sample count, occasionally incremented by one when the fractional accumulator crosses 1.

Therefore this family Snes9x2005 path emits **one audio batch per emulated video frame**, with batch length determined by `11025 / refresh_rate`, not a 576-frame callback.

For NTSC (~60.1 Hz), that is approximately:

```text
183.45 source frames/video frame
```

so callbacks alternate over time between 183 and 184 frames according to the accumulator.

For PAL (~50 Hz), the corresponding cadence is approximately 220/221 frames.

## XGO frontend interaction [BIN + SRC/UP]

XGO's stock frontend consumer still requires:

```text
576 source frames
```

before forwarding a block.

Thus NTSC SNES normally requires PCM accumulated across roughly three to four Snes9x2005 frame callbacks before one frontend consumer transfer can occur.

The earlier mental model:

```text
one SNES callback = 576 frames = 52.245 ms
```

is wrong for the pinned family core.

Correct model:

```text
one SNES callback ~= 183/184 frames ~= one video frame
XGO consumer quantum = 576 frames ~= 3.14 NTSC callback batches
```

## Important latency consequence

The 52.245-ms duration represented by a 576-frame consumer block is **not a fixed frontend residence time**.

Samples enter the ring once per emulated video frame. Depending on residual occupancy:

- some samples cross the 576 threshold immediately on their callback;
- others survive one or more later frame callbacks before becoming part of a consumer transfer.

This is directly analogous to the FBA 367/576 phase relationship, but SNES has a fractional 183/184 producer cadence rather than a fixed integer 367.

## Frame phase [SRC/UP]

For the pinned core:

```text
input poll
 -> S9xMainLoop()
 -> video callback
 -> audio_upload_samples()
 -> audio_batch_cb()
```

Therefore generated audio reaches the XGO frontend after the current emulated SNES frame has run.

This is useful for eventual input-to-audio latency modeling: the frontend cannot receive that frame's completed PCM before `S9xMainLoop()` finishes.

## Lower path remains unchanged [XGO BIN]

Once XGO's frontend has 576 SNES source frames:

```text
576 @ 11025
 -> x4 whole-frame repetition
 -> 2304 @ 44100
 -> 576 lower cursor units
```

The lower transfer is admitted only while queued lower-SND backlog is below 482 units.

Thus the stock SNES pipeline contains two large, independent quantizations:

1. frame-paced producer callbacks of ~183/184 source frames;
2. frontend consumer blocks of 576 source frames, expanded to a 576-unit lower block.

## Evidence boundary

This source result proves the behavior of the exact pinned maintained family Snes9x2005 revision used in the XGO external-core archaeology.

The XGO stock built-in SNES core itself is not source-identical by assumption. XGO BIN proves its frontend family-0x08 rate is 11025 and proves the common frontend ring consumer. A direct stock-core callback-size trace would be needed to promote the 183/184 cadence to XGO built-in BIN.

## Next work

1. Model the 183/184 fractional callback sequence against the 576-frame consumer threshold.
2. Derive sample residence distribution for NTSC and PAL.
3. Search XGO built-in SNES binary/core evidence for callback frame counts to determine whether it matches this family cadence.
4. Combine the resulting frontend residence with the lower 576-unit/482-unit queue sawtooth without adding incompatible maxima as a typical value.

## Hardware gate

Not reached.
