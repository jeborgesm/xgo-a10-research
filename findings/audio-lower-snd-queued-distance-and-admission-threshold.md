# XGO lower-SND queued-audio distance and 482-unit admission threshold

Date: 2026-10-01  
Branch: `research-audio-fidelity-latency`  
Status: **BIN CLOSURE — LOWER QUEUE SEMANTICS RESOLVED**

## Major closure

The previously OPEN modular distance between SND `+0x38` and `+0x3A` is now instruction-level closed.

Function `0x802FD720`:

1. reads SND `+0x38` through `0x8030A174`;
2. reads SND `+0x3A` through `0x8030A198`;
3. stores the observed `+0x3A` value at private `+0x44`;
4. computes the modular difference using private `+0x48 = 8208`.

The arithmetic is:

```text
if commit38 >= cursor3A:
    queued = commit38 - cursor3A
else:
    queued = modulus - cursor3A + commit38
```

or:

```text
queued = (commit38 - cursor3A) mod 8208
```

Previous work proved that SND `+0x38` is written from the software submission cursor after a lower transfer.

Therefore SND `+0x3A` is the paired consumption/playback-progress cursor for this calculation, and the modular distance is **queued lower-SND audio**. [BIN]

This supersedes the earlier OPEN labels "free space vs queued data" for this helper.

## Exact 482 predicate [BIN]

The upper readiness callback `0x802FD5A4`:

```text
threshold = private +0xFA
queued = 0x802FD720(object)
q = queued / threshold
return (q < 1)
```

For the normal XGO setup:

```text
sample_num = 960
threshold = (960 >> 1) + 2 = 482
```

Since unsigned integer `queued / 482 < 1` exactly when `queued < 482`:

```text
0x802FD5A4 returns true iff queued lower-SND audio < 482 cursor units
```

The caller waits/retries when this predicate does not permit submission.

Therefore **482 is a lower-SND backlog/admission threshold**, not a startup prebuffer threshold. [BIN]

## Cursor unit conversion [BIN]

Earlier transfer archaeology proved:

```text
1 lower cursor unit = 16 copied PCM bytes
                    = 4 stereo S16 output frames
```

Therefore:

```text
482 units = 7,712 bytes
          = 1,928 stereo output frames
```

At 44.1 kHz this threshold represents:

```text
1,928 / 44,100 = 43.719 ms
```

At 48 kHz:

```text
1,928 / 48,000 = 40.167 ms
```

These are **admission-threshold queue depths**, not complete emulator-to-speaker latency measurements.

## Post-submit queue bounds by source path [BIN + arithmetic]

The predicate is checked before the next converted block is submitted. Therefore one accepted block can carry queue occupancy above 482 units.

### SNES special path: 11025 -> 44100

Consumer source quantum:

```text
576 source frames
x4 repetition
= 2,304 output frames
= 576 cursor units
```

If admission occurs at the largest allowed pre-submit occupancy (481 units), the strict arithmetic post-submit upper bound is:

```text
481 + 576 = 1,057 units
4,228 output frames
95.87 ms at 44.1 kHz
```

(The exact instantaneous maximum depends on hardware cursor movement during the copy/commit interval, so this is a conservative arithmetic bound.)

### FBA: 22050 -> 44100

```text
576 source frames
x2 repetition
= 1,152 output frames
= 288 cursor units
```

Pre-submit maximum 481 units plus one block:

```text
769 units
3,076 output frames
69.75 ms at 44.1 kHz
```

### Native 44100

```text
576 output frames
= 144 cursor units
```

Bound:

```text
625 units
2,500 frames
56.69 ms at 44.1 kHz
```

### Native 48000

Same 576-frame block / 144 cursor units:

```text
625 units
2,500 frames
52.08 ms at 48 kHz
```

These are lower-SND queue bounds only. They exclude frontend-ring waiting, callback timing, DAC/filter/analog delay, and any scheduling interval.

## Important SNES consequence

The SNES converted block itself is:

```text
2,304 output frames = 52.245 ms
```

which is larger than the 1,928-frame admission threshold.

Thus a single accepted SNES block can take the lower queue from below the threshold to above it. The next consumer submission must wait for the hardware cursor to drain the backlog below 482 units again.

This explains why the same 482-unit policy produces materially different queue excursions for 11.025-kHz, 22.05-kHz and native-rate sources.

## Relationship to family API [UP/INF]

The recovered HC15xx HCRTOS API exposes `get_avail()`, `AVAIL_MIN`, and `DELAY`.

XGO's old driver implements the relevant admission policy using the inverse quantity:

```text
queued backlog < threshold
```

rather than exposing free frames directly at this callback.

This is conceptually compatible with a bounded-backlog transfer policy, but no source-name identity is asserted.

## What this closes

CONFIRMED [BIN]:

- SND `+0x38` is the software-committed lower submission boundary.
- SND `+0x3A` is the paired consumption/progress cursor used to determine outstanding audio.
- `0x802FD720` computes queued lower-SND distance.
- private `+0x44` caches the observed `+0x3A` cursor.
- `+0x48 = 8208` is the cursor modulus.
- `+0xFA = 482` is the backlog threshold.
- submission is permitted only while queued distance is below 482 units.

## Still OPEN

- normal steady-state occupancy distribution within the allowed sawtooth;
- exact timing between readiness test, PCM copy and `+0x38` commit;
- whether `+0x3A` advances continuously or at a lower hardware granularity;
- frontend-ring contribution to normal end-to-end latency;
- DAC/analog propagation delay.

## Next target

Trace `+0x3A` at the interrupt/status boundary and recover its advancement granularity. Then combine:

```text
frontend 576-frame threshold
+
lower-SND queued-distance policy
+
per-core converted block size
```

into a bounded stock latency model.

## Hardware gate

Not reached.
