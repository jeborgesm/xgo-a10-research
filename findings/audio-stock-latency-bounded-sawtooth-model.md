# XGO stock audio latency model — corrected bounded queue sawtooth

Date: 2026-10-02
Branch: `research-audio-fidelity-latency`
Status: **BIN-DERIVED MODEL — TWO-FRAME CURSOR CORRECTION APPLIED**

## Corrected lower unit

Authoritative lower packing:

```text
1 cursor unit = 2 stereo S16 output frames
queued = (+0x38 - +0x3A) mod 8208
admit next transfer iff queued < 482 units
```

Thus:

```text
482 units = 964 frames = 21.859 ms @44100
```

The earlier 43.719-ms threshold value was based on the superseded four-frame/unit interpretation.

## Source-dependent blocks

### FBA 22050 -> 44100

```text
576 source frames
x2 -> 1152 output frames
= 576 lower units
represented duration = 26.122 ms
```

Near-threshold arithmetic bound:

```text
481 + 576 = 1057 units
= 2114 frames
= 47.937 ms @44100
```

### SNES 11025 -> 44100

```text
576 source
x4 -> 2304 output
= 1152 lower units
represented duration = 52.245 ms
```

Bound:

```text
481 + 1152 = 1633 units
= 3266 frames
= 74.059 ms
```

### Native 44100

```text
576 frames = 288 units
bound = 769 units = 1538 frames = 34.875 ms
```

### Native 48000

```text
576 frames = 288 units
threshold = 20.083 ms
bound = 1538 frames = 32.042 ms
```

## Backing capacity is not normal latency

```text
8208 units * 2 frames = 16416 frames
```

Capacity:

```text
372.245 ms @44100
342.000 ms @48000
```

The admission controller prevents normal producer backlog from simply filling that entire allocation.

## Frontend batching remains unchanged

The upper 576-source-frame batching duration is still:

```text
11025 -> 52.245 ms
22050 -> 26.122 ms
44100 -> 13.061 ms
48000 -> 12.000 ms
```

A sample's actual batching residence depends on phase.

Exact FBA phase analysis gives about 13.07-ms mean callback-to-consumer residence at the stock fixed-367 cadence.

## Corrected conservative combined envelopes

Using the earliest-sample upper-batch maximum plus the largest arithmetic lower post-submit bound:

```text
FBA:
26.122 + 47.937 <= 74.059 ms

SNES:
52.245 + 74.059 <= 126.304 ms

native 44100:
13.061 + 34.875 <= 47.936 ms

native 48000:
12.000 + 32.042 <= 44.042 ms
```

These are deliberately conservative software-queue envelopes, not measured latency and not expected typical values.

They exclude core generation phase, task wakeup jitter, SND/DAC internals and analog propagation.

## CPS1 practical interpretation

The corrected lower threshold is smaller than previously believed.

For FBA, the fixed 576-source-frame frontend batching and once-per-video-frame core delivery are therefore proportionally more important latency contributors than the old four-frame cursor model suggested.

That strengthens the case for:

1. first cleaning the rate/conversion path;
2. then testing a moderate frontend quantum reduction if needed.

## Hardware gate

The minimal native-22050 FBA proof remains the first isolated hardware experiment; this correction does not require adding queue changes to it.
