# Stock SNES lower-queue offered-load recurrence

Date: 2026-10-01  
Branch: `research-audio-fidelity-latency`  
Status: **BIN + EXACT ARITHMETIC; PHYSICAL UNDERRUN RESPONSE OPEN**

## Purpose

Combine the now-closed stock SNES producer cadence with the frontend 576-frame consumer and the 44.1-kHz lower-SND drain.

This distinguishes a proven offered-load deficit from assumptions about what the hardware does when that deficit reaches zero.

## Closed inputs

```text
SNES producer increment      183 source frames / emulated frame
stock NTSC scheduler         60 frames/s (17,17,16 ms)
frontend consumer quantum    576 source frames
11025 -> 44100 conversion    exact x4 frame repetition
lower cursor unit            4 stereo output frames
hardware-facing rate         44100 output frames/s
```

One 576-source-frame frontend transfer becomes:

```text
2304 output frames = 576 lower cursor units
```

Hardware drain at nominal 44.1 kHz is:

```text
44100 / 4 = 11025 lower cursor units/s
```

## Exact frontend transfer recurrence

For:

```text
P = 183
C = 576
gcd(P,C) = 3
```

the source phase repeats after 192 producer callbacks.

Across one 192-frame / 3.2-second cycle:

```text
183 * 192 = 35136 source frames
35136 / 576 = 61 exact frontend transfers
```

Transfer callback numbers begin:

```text
4, 7, 10, 13, 16, 19, 23, 26, ...
```

Among the 60 inter-transfer gaps in one complete phase cycle:

```text
52 gaps are 3 emulated frames
 8 gaps are 4 emulated frames
```

So the lower SND input is not a smooth 10.98-kHz source stream. It receives 576-unit bursts separated mostly by three game frames, with eight four-frame holes per 3.2-second phase cycle.

## Long-term balance

Input offered to lower SND during the complete cycle:

```text
61 * 576 = 35136 cursor units
```

Nominal drain during 3.2 s:

```text
11025 * 3.2 = 35280 cursor units
```

Net deficit:

```text
35280 - 35136 = 144 cursor units per phase cycle
144 / 3.2 = 45 cursor units/s
```

Equivalent output-frame deficit:

```text
45 * 4 = 180 frames/s
```

This independently reproduces the previously closed 43,920-vs-44,100 output-rate mismatch.

## Why the four-frame gaps matter

At the nominal drain rate, one 576-unit burst represents:

```text
576 / 11025 = 52.2449 ms
```

A four-frame scheduler gap spans either 66 or 67 ms depending on its alignment with the 17/17/16-ms cadence.

Thus one isolated 576-unit burst cannot by itself span a four-frame gap:

```text
66 ms drain = 727.65 units
67 ms drain = 738.675 units
```

versus only 576 units added by one transfer.

Whether starvation actually occurs at a particular gap depends on carried queue depth from preceding bursts and the lower-driver start/restart state.

## Continuously-running illustrative model [INF]

If the lower consumer is already draining continuously and begins this recurrence with only the first 576-unit transfer queued, exact simulation of the recovered burst schedule produces depletion at each of the eight four-frame gaps in the 192-frame cycle.

Depending on 17/17/16 phase alignment, the uncovered portions are on the order of fractions of a millisecond to a few milliseconds.

This is **not promoted to a hardware fact**, because the lower SND engine may:

- establish additional startup depth before starting DMA;
- stop/restart on underrun;
- apply the proven underrun-fade feature;
- alter the effective cursor behavior at empty;
- preserve backlog from an earlier phase.

The important binary/arithmetic result is stronger and safer:

> Once the hardware is draining at nominal 44.1 kHz, stock SNES supplies less PCM than that drain consumes, and the deficit is deterministic rather than random.

No finite initial backlog can eliminate a persistent 45-unit/s deficit forever. It can only postpone the point at which the lower driver's empty/underrun policy becomes relevant.

## Interaction with the 482-unit admission threshold

The 482-unit predicate limits admission when the lower queue is already deep. It cannot repair a source-rate deficit because it only delays writes; it never creates PCM.

Likewise, the frontend ring can accumulate whole 183-frame producer callbacks but cannot increase the long-term average above 10,980 source frames/s.

Therefore neither queue policy can provide rate compensation.

## Noise/fidelity connection

The stock SND underrun-fade bit is enabled.

That now has a potentially important relationship to SNES:

```text
fixed-183 source deficit
        ↓
deterministic lower-queue depletion pressure
        ↓
lower empty/underrun state
        ↓
SND underrun-fade behavior
        ↓
possible audible smoothing / discontinuity / repeated low-level artifact
```

Only the first three arrows through depletion pressure are currently established. The exact hardware empty-state transition and fade waveform remain OPEN.

## Next archaeology target

Recover the lower driver's empty/underrun state machine:

1. determine what +0x3A does when it catches +0x38;
2. determine whether DMA stops, loops, holds last sample, emits zero, or enters fade;
3. determine how a later XFER restarts/continues output;
4. connect the already-proven underrun-fade enable bit to that transition.

This is now higher-value than further abstract latency arithmetic because it may explain a stock SNES audio artifact and the runtime-reinit noise path with the same lower-driver mechanism.

## Hardware gate

Not reached.
