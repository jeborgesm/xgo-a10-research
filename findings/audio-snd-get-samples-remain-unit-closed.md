# SND_GET_SAMPLES_REMAIN exactly converts both queued stages to PCM-frame counts

Date: 2026-10-02
Branch: `research-audio-fidelity-latency`
Status: **BIN + ALi API CORRESPONDENCE — DIAGNOSTIC UNIT CLOSED**

## Public command identity

The validated ALi HLD command map identifies:

```text
0x31 = SND_GET_SAMPLES_REMAIN
```

The XGO 0x31 handler calls `0x80309100` and returns that helper's value through the caller-provided output pointer.

The remaining question was the exact unit of the returned value.

That unit is now closed.

## Exact XGO helper

`0x80309100` obtains two queue-depth terms.

First:

```text
jal 0x802FD68C
```

Second:

```text
jal 0x802FD814
```

It adds the two returned values and returns the sum.

Both wrappers have the same form:

```text
call queue-distance helper
if result != 0:
    result <<= 1
return result
```

### First queued stage

`0x802FD68C` calls `0x802FD624`.

`0x802FD624` computes a modulo distance from private 16-bit cursor fields:

```text
+0x62
+0x64
+0x66
```

and returns that distance in internal cursor units.

`0x802FD68C` doubles it.

### Lower committed/playback stage

`0x802FD814` calls `0x802FD720`.

`0x802FD720` is the already-proven lower queue-distance helper:

```text
queued = (+0x38 commit - +0x3A playback) mod 8208
```

represented by the private +0x44/+0x48 cursor state.

`0x802FD814` doubles that distance too.

## Exact returned unit

Therefore:

```text
SND_GET_SAMPLES_REMAIN
= 2 * stage_A_cursor_distance
+ 2 * lower_committed_cursor_distance
```

The public ALi API names the result “samples remain”.

Combined with the direct XGO writer, this closes:

> **one internal cursor unit represents two PCM sample time frames.**

And:

> **XGO command 0x31 returns remaining PCM time-frame count across both queued driver stages.**

For the normal stereo-S16 emulator path, the returned number is a count of stereo PCM time positions, not bytes.

## Why this matters

A future diagnostic build does not need to infer queue depth from raw register geometry.

The stock driver already exposes:

```text
0x15 IS_PCM_EMPTY
0x31 SND_GET_SAMPLES_REMAIN
```

These can answer, during actual CPS1 gameplay:

- did the sound path reach empty?
- how many PCM frames remained near a glitch?
- does Cadillacs and Dinosaurs choppiness correlate with true buffer starvation?
- does exact FBA rate correction eliminate empty events?

## Important two-stage nuance

Command 0x31 includes **two** queued stages.

It is therefore more complete than reading only the lower +0x38/+0x3A committed/playback distance.

This also explains why a raw lower-queue model should not automatically be equated with total device latency.

## Hardware diagnostic conversion

If the selected hardware rate is known:

```text
remaining_ms = SND_GET_SAMPLES_REMAIN * 1000 / hardware_rate
```

Examples:

```text
964 frames @44100 = 21.859 ms
964 frames @22050 = 43.719 ms
```

The API result can therefore be logged directly in time units without relying on the internal 16-byte DMA packing.

## Evidence boundary

- 0x31 public command identity: **SRC/UP + validated BIN correspondence**
- two queue-distance helpers and x2 conversion: **BIN**
- lower helper identity: **BIN**
- returned unit as PCM sample time frames: **BIN+SRC closed**
- physical DAC pipeline after the reported queues: **OPEN/HW**

## Candidate policy

Do not add this instrumentation to the first native-22050 fidelity proof.

Use it only in a separate diagnostic candidate if Test A/B listening reveals a repeatable gameplay artifact that needs correlation with real queue starvation.
