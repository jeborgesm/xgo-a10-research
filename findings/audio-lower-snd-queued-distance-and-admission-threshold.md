# XGO lower-SND queued-audio distance and 482-unit admission threshold

Date: 2026-10-02
Branch: `research-audio-fidelity-latency`
Status: **BIN CLOSURE — CORRECTED TWO-FRAME CURSOR UNIT**

## Queue arithmetic [BIN]

`0x802FD720` computes:

```text
queued = (commit38 - playback3A) mod 8208
```

where:

- SND +0x38 is the software-committed lower boundary;
- SND +0x3A is hardware playback/consumption progress;
- private +0x44 caches the observed +0x3A;
- private +0x48 is the 8208-unit modulus.

## Admission predicate [BIN]

`0x802FD5A4` permits another lower submission iff:

```text
queued < private+0xFA
```

Normal setup derives:

```text
sample_num = 960
threshold = (960 >> 1) + 2 = 482 units
```

Therefore 482 is a queued-backlog admission ceiling, not a startup-prebuffer requirement.

## Corrected cursor unit

Direct packing plus ALi HLD command correspondence proves:

```text
1 cursor unit = 2 stereo S16 PCM time frames
```

not four.

Therefore:

```text
482 units = 964 output frames
```

Time depth:

```text
44100 Hz -> 21.8594 ms
48000 Hz -> 20.0833 ms
22050 Hz -> 43.7188 ms
11025 Hz -> 87.4376 ms
```

These are threshold depths only.

## Corrected post-submit arithmetic bounds

The readiness check occurs before a whole block is committed.

### FBA 22050 -> 44100

```text
576 source frames
x2 -> 1152 output frames
= 576 cursor units

max pre-submit = 481 units
post-submit arithmetic bound = 1057 units
= 2114 output frames
= 47.9365 ms @44100
```

### SNES 11025 -> 44100

```text
576 source frames
x4 -> 2304 output frames
= 1152 cursor units

481 + 1152 = 1633 units
= 3266 output frames
= 74.0590 ms @44100
```

### Native 44100

```text
576 output frames
= 288 units

481 + 288 = 769 units
= 1538 frames
= 34.8753 ms
```

### Native 48000

```text
769 units
= 1538 frames
= 32.0417 ms
```

These remain conservative queue-only bounds; maxima need not coincide with actual submission phase.

## Important consequence

Both converted low-rate blocks exceed the 482-unit admission threshold:

```text
FBA block  = 576 units
SNES block = 1152 units
threshold  = 482 units
```

So after either low-rate block is accepted, the next submission must wait until hardware playback drains backlog below the threshold.

This makes the lower queue a source-dependent burst controller.

## 960 semantics narrowed

Because each cursor unit represents two PCM frames:

```text
(sample_num >> 1)+2
= 482 units
= 964 PCM frames
```

The legacy `sample_num=960` is now strongly tied to PCM sample-frame/count geometry rather than being an unrelated opaque number.

Exact vendor register naming remains open.

## Hardware gate

No candidate is produced by this arithmetic correction.
