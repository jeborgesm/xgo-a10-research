# Audio lower-SND ring capacity and cursor-unit closure

Date: 2026-10-02
Branch: `research-audio-fidelity-latency`
Status: **BIN + ALi SRC CROSS-CLOSURE — CORRECTED**

## Correction notice

Earlier versions correctly proved a 16-byte cursor stride but incorrectly divided those bytes by packed stereo-S16 width and concluded one cursor unit represented four stereo frames.

Direct XGO packing code plus the identified ALi `pcm_output` structure now proves:

> **1 lower cursor unit = 16 internal bytes = 2 stereo S16 time frames.**

See `audio-correction-lower-cursor-two-frame-unit.md`.

## Geometry [BIN]

The lower initialization sets:

```text
G = 8
```

Public ALi command correspondence independently identifies this value as the legacy PCM DMA buffer depth.

Allocation:

```text
G * 513 * 32 = 131,328 bytes
```

Wrap modulus:

```text
G * 513 * 2 = 8,208 cursor units
```

Software commit cursor starts at zero and is eventually published to SND +0x38.

## Cursor packing [BIN]

The lower writer addresses:

```text
lower_base + (cursor << 4)
```

so one cursor slot is 16 internal bytes.

For the two-channel frontend path, the source offset advances by 8 packed source bytes for each cursor slot.

Packed stereo S16 is 4 bytes per time frame, therefore:

```text
8 source bytes = 2 stereo frames
```

The writer expands/reformats those two source frames into the 16-byte internal slot.

The XGO `SND_GET_SAMPLES_REMAIN` lineage independently doubles queued cursor units when converting them to remaining PCM sample frames, confirming the same 2:1 relationship.

## Correct lower capacity

```text
8208 cursor units
* 2 stereo frames/unit
= 16416 stereo frames
```

Time capacity:

```text
44100 Hz -> 372.245 ms
48000 Hz -> 342.000 ms
```

This remains backing capacity, not normal latency.

## Correct admission threshold

Normal setup:

```text
sample_num = 960
threshold = (960 >> 1) + 2 = 482 cursor units
```

With the corrected cursor unit:

```text
482 units = 964 stereo frames
```

Time represented:

```text
44100 Hz -> 21.859 ms
48000 Hz -> 20.083 ms
22050 Hz -> 43.719 ms
11025 Hz -> 87.438 ms
```

The threshold is an admission ceiling, not a forced preload.

The relation is now especially revealing:

```text
482 units * 2 frames/unit = 964 frames
sample_num                         = 960 frames/count
```

so the threshold is approximately one `sample_num` plus four PCM frames.

## Correct block sizes

```text
FBA:
576 source @22050
 -> 1152 output @44100
 -> 576 cursor units

SNES:
576 source @11025
 -> 2304 output @44100
 -> 1152 cursor units

native 44100/48000:
576 output
 -> 288 cursor units

native FBA 22050:
576 output
 -> 288 cursor units
```

The represented PCM durations themselves are unchanged.

## Queue topology

```text
frontend stereo-S16 ring
  576-source-frame dequeue
       |
       v
optional x2/x4 low-rate repetition
       |
       v
ALi-lineage pcm_output
       |
       v
lower packed DMA ring
  131,328 internal bytes
  8,208 cursor units
  16 internal bytes/unit
  2 stereo time frames/unit
  admission ceiling 482 units
       |
       v
SND/I2SO
```

## Hardware gate

No new hardware candidate is created by this correction.
